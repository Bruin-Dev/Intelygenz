import asyncio
from collections import defaultdict
import time
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from datetime import datetime
from pytz import timezone
from typing import Any, Dict, Set, List, Tuple, Iterator
from application.exceptions import ResponseException


class RepairTicketsMonitor:
    def __init__(
            self,
            event_bus,
            logger,
            scheduler,
            config,
            bruin_repository,
            new_tagged_emails_repository,
            repair_tickets_kre_repository,
    ):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._bruin_repository = bruin_repository
        self._new_tagged_emails_repository = new_tagged_emails_repository
        self._repair_tickets_kre_repository = repair_tickets_kre_repository

        self._semaphore = asyncio.BoundedSemaphore(
            self._config.MONITOR_CONFIG["semaphores"]["repair_tickets_concurrent"]
        )

    async def start_repair_tickets_monitor(self, exec_on_start: bool = False):
        """Start the monitor scheduled checks, to process input emails."""
        self._logger.info("Scheduling RepairTicketsMonitor job...")
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG["timezone"])
            next_run_time = datetime.now(tz)
            self._logger.info(
                "RepairTicketsMonitor job is going to be executed immediately"
            )

        try:
            scheduler_seconds = self._config.MONITOR_CONFIG["scheduler_config"]["repair_ticket_monitor"]
            self._scheduler.add_job(
                self._run_repair_tickets_polling,
                "interval",
                seconds=scheduler_seconds,
                next_run_time=next_run_time,
                replace_existing=False,
                id="_run_repair_tickets_polling",
            )
        except ConflictingIdError as conflict:
            self._logger.info(
                f"Skipping start of repair tickets monitor job. Reason: {conflict}"
            )

    async def _run_repair_tickets_polling(self):
        """Poll the storage for new tagged emails create tasks to process those"""
        self._logger.info("Starting RepairTicketsMonitor process...")

        start_time = time.time()

        self._logger.info("Getting all tagged emails...")
        tagged_emails = self._new_tagged_emails_repository.get_tagged_pending_emails()
        repair_emails, other_tags_emails = self._triage_emails_by_tag(tagged_emails)
        self._logger.info(f"Got {len(tagged_emails)} tagged emails of those where {repair_emails} repair emails.")

        other_tags_tasks = [self._process_other_tags_email(email_data) for email_data in repair_emails]
        repair_tasks = [self._process_repair_email(email_data) for email_data in repair_emails]
        tasks = repair_tasks + other_tags_tasks

        output = await asyncio.gather(*tasks, return_exceptions=True)
        self._logger.info(
            "RepairTicketsMonitor process finished! Took {:.3f}s".format(
                time.time() - start_time
            )
        )
        self._logger.info(f"Output: {output}")

    def _triage_emails_by_tag(self, tagged_emails) -> Tuple[Iterator, Iterator]:
        """Separate between repair emails and non repair emails"""
        repair_tag_id = self._config.MONITOR_CONFIG["tag_ids"]["Repair"]
        repair_emails = filter(lambda x: x['tag_id'] == repair_tag_id, tagged_emails)
        other_tags_emails = filter(lambda x: x['tag_id'] != repair_tag_id, tagged_emails)

        return repair_emails, other_tags_emails

    async def _process_other_tags_email(self, email: Dict[str, Any]):
        """Process email that are not repair tickets"""
        self._new_tagged_emails_repository.mark_complete(email['email_id'])

    async def _get_inference(self, email_data):
        """Get the models inference for given email data"""
        prediction_response = await self._repair_tickets_kre_repository.get_email_inference(
            email_data
        )
        if prediction_response["status"] not in range(200, 300):
            self._logger.info(
                f"Error prediction response status code {prediction_response['status']}"
            )
            return
        return prediction_response.get("body")

    async def _save_output(
            self,
            email_id: str,
            service_number_site_map: Dict[str, str],
            tickets_created: List[Dict[str, Any]],
            ticket_updated: List[Dict[str, Any]],
            tickets_could_be_created: List[Dict[str, Any]],
            tickets_could_be_updated: List[Dict[str, Any]],
            tickets_cannot_be_created: List[Dict[str, Any]],
    ):
        """Save the output from the ticket creation / inference verification"""
        output_response = await self._repair_tickets_kre_repository.save_outputs(
            email_id,
            service_number_site_map,
            tickets_created,
            ticket_updated,
            tickets_could_be_created,
            tickets_could_be_updated,
            tickets_cannot_be_created,
        )
        if output_response["status"] not in range(200, 300):
            self._logger.info(
                f"Error while saving output response status code {output_response['status']}"
            )
            return
        return output_response.get("body")

    async def _process_repair_email(self, email_tag_info: Dict[str, Any]):
        """
        Process repair emails, verify it's service numbers, created/update tickets,
        and save the result of this operations into KRE.
        """
        # TODO add update email status
        email_id = email_tag_info['email_id']
        email_data = self._new_tagged_emails_repository.get_email_details(email_id)
        email_data['tag'] = email_tag_info
        client_id = email_data['email']['client_id']
        self._logger.info(f'Running Repair Email Process for email_id: {email_id}')

        tickets_created = []
        tickets_updated = []
        tickets_could_be_created = []
        tickets_could_be_updated = []
        ticket_cannot_be_created = []

        async with self._semaphore:
            inference_data = await self._get_inference(email_data)
            if not inference_data:
                return

            potential_service_numbers = inference_data['potential_service_numbers']
            try:
                service_number_site_map = await self._get_valid_service_numbers_site_map(potential_service_numbers)
                existing_tickets = await self._get_existing_tickets(client_id, service_number_site_map)
            except ResponseException as e:
                self._logger.error(f'Error in bruin {e} could not process email: {email_id}')
                return
            if self._is_inference_actionable(inference_data):
                tickets_created, tickets_updated, ticket_cannot_be_created = await self._create_tickets(
                    inference_data,
                    service_number_site_map,
                    existing_tickets
                )
            else:
                tickets_could_be_created, tickets_could_be_updated = self._get_potential_tickets(
                    inference_data,
                    service_number_site_map,
                    existing_tickets,
                )

            save_output_response = await self._save_output(
                email_id,
                service_number_site_map,
                tickets_created,
                tickets_updated,
                tickets_could_be_created,
                tickets_could_be_updated,
                ticket_cannot_be_created,
            )
            if not save_output_response:
                return

            self._new_tagged_emails_repository.mark_complete(email_id)

    async def _get_valid_service_numbers_site_map(self, potential_service_numbers: List[str]) -> Dict[str, str]:
        """Give a dictionary with keys as service numbers with their site ids"""
        service_number_site_map = {}
        for potential_service_number in potential_service_numbers:
            result = await self._bruin_repository.verify_service_number_information(potential_service_number)
            if result['status'] not in range(200, 300):
                ResponseException(f'Exception while verifying service_number: {potential_service_number}')
            if result['site_id']:
                service_number_site_map[potential_service_number] = result['site_id']

        return service_number_site_map

    async def _get_existing_tickets(
            self,
            client_id: str,
            service_number_site_map: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Return a list of preexisting tickets in bruin with the given sites"""
        service_numbers = list(service_number_site_map.keys())
        existing_tickets = []
        open_tickets = await self._bruin_repository.get_open_tickets_with_service_numbers(client_id)
        if open_tickets['status'] == 404:
            return existing_tickets
        if open_tickets['status'] not in range(200, 300):
            raise ResponseException('Exception while getting bruin response for existing tickets')

        for ticket in open_tickets['body']:
            if not ticket['service_numbers']:
                continue
            for service_number in service_numbers:
                if service_number in ticket['service_numbers']:
                    ticket['site_id'] = service_number_site_map.get(service_number)
                    existing_tickets.append(ticket)
                    break

        return existing_tickets

    async def _create_tickets(
            self,
            inference_data: Dict[str, Any],
            service_number_site_map: Dict[str, str],
            existing_tickets: List[Dict[str, Any]],
    ) -> (List[str], List[str], List[str]):
        # TODO: Add content
        # Separate VOO/VAS
        # Update/Reopen/Open logic
        # Return created ticket_id
        # here be dragons
        return [], [], []

    def _get_potential_tickets(
            self,
            inference_data: Dict[str, Any],
            service_number_site_map: Dict[str, str],
            existing_tickets: List[Dict[str, Any]],
    ) -> (List[Dict[str, Any]], List[Dict[str, Any]]):
        """Get potential updated/created tickets"""
        potential_created_tickets = []
        potential_updated_tickets = []
        predicted_class = inference_data['predicted_class']
        site_ids = set(service_number_site_map.values())

        for ticket in existing_tickets:
            if self._should_update_ticket(ticket, site_ids, predicted_class):
                potential_updated_tickets.append(
                    self._create_output_ticket_dict(
                        site_id=ticket['site_id'],
                        service_numbers=ticket['service_numbers'],
                        ticket_id=ticket['ticketId'],
                    )
                )
                site_ids.remove(ticket['site_id'])

        for site_id in site_ids:
            service_numbers_filtered_by_site_id = [
                service_number
                for service_number, service_site_id in
                service_number_site_map.items()
                if service_site_id == site_id
            ]
            potential_created_tickets.append(
                self._create_output_ticket_dict(
                    site_id=site_id,
                    service_numbers=service_numbers_filtered_by_site_id,
                )
            )

        return potential_created_tickets, potential_updated_tickets

    def _update_email_status(self):
        # TODO: add content
        pass

    @staticmethod
    def _create_output_ticket_dict(
            site_id: str,
            service_numbers: List[str],
            ticket_id: str = "",
            reason: str = "",
    ) -> Dict[str, Any]:
        """Create a dict for output purposes"""
        return {
            'site_id': site_id,
            'service_numbers': service_numbers,
            'ticket_id': ticket_id,
            'not_created_reason': reason,
        }

    @staticmethod
    def _should_update_ticket(ticket: Dict[str, Any], site_ids: Set[str], predicted_class: str) -> bool:
        """Check if exiting ticket should be updated"""
        ticket_category = ticket['category']
        if ticket['site_id'] not in site_ids:
            return False

        if ticket_category not in ['VOO', 'VAS']:
            return False

        if predicted_class == ticket_category:
            return True
        elif predicted_class == 'VOO' and ticket_category == 'VAS':
            return False
        elif predicted_class == 'VAS' and ticket_category == 'VOO':
            return True

    @staticmethod
    def _is_inference_actionable(inference_data: Dict[str, Any]) -> bool:
        """Check if the inference can be used to create/update a ticket"""
        is_other = inference_data['predicted_class'] == 'Other'
        filtered = inference_data['filter_flags']['is_filtered']
        validation_set = inference_data['filter_flags']['is_validation_set']
        tagger_below_threshold = inference_data['filter_flags']['tagger_is_below_threshold']
        return not any([filtered, validation_set, tagger_below_threshold, is_other])
