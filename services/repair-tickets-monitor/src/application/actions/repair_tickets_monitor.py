import asyncio
from collections import defaultdict
import time
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from datetime import datetime
from pytz import timezone
from typing import Any, Dict, List, Tuple, Iterator


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
        repair_tag_id = self._config.MONITOR_CONFIG["tag_ids"]["Repair"]
        repair_emails = filter(lambda x: x['tag_id'] == repair_tag_id, tagged_emails)
        other_tags_emails = filter(lambda x: x['tag_id'] != repair_tag_id, tagged_emails)

        return repair_emails, other_tags_emails

    async def _get_inference(self, email_data):
        prediction_response = await self._repair_tickets_kre_repository.get_email_inference(
            email_data
        )
        if prediction_response["status"] not in range(200, 300):
            self._logger.info(
                f"Error predicion response status code {prediction_response['status']}"
            )
            return
        return prediction_response.get("body")

    async def _process_other_tags_email(self, email: Dict[str, Any]):
        self._new_tagged_emails_repository.mark_complete(email['email_id'])

    async def _process_repair_email(self, email: Dict[str, Any]):
        email_id = email['email_id']
        email_data = self._new_tagged_emails_repository.get_email_details(email_id)
        client_id = email_data['email']['client_id']
        self._logger.info(f'Running Repair Email Process for email_id: {email_id}')

        async with self._semaphore:
            inference_data = await self._get_inference(email_data)
            potential_service_numbers = inference_data['potential_service_numbers']
            service_numbers_by_site = await self._get_valid_service_numbers_by_site(potential_service_numbers)
            existing_tickets_ids = await self._get_existing_tickets(client_id, service_numbers_by_site)
            if self._is_inference_actionable(inference_data):
                created_ticket_ids = self._create_tickets(inference_data, service_numbers_by_site, existing_tickets_ids)

            response = await self._repair_tickets_kre_repository.save_outputs(
                service_numbers_by_site,
                existing_tickets_ids,
                created_ticket_ids,
            )
            if response["status"] not in range(200, 300):
                # TODO add proper logging
                return

            self._new_tagged_emails_repository.mark_complete(email['email_id'])

    async def _get_valid_service_numbers_by_site(self, potential_service_numbers: List[str]) -> Dict[str, List]:
        service_number_by_site = defaultdict[list]
        for pontential_service_number in potential_service_numbers:
            result = await self._bruin_repository.verify_service_number_information(pontential_service_number)
            if result['site_id']:
                service_number_by_site[result['site_id']] = result['service_number']

        return service_number_by_site

    async def _get_existing_tickets(self, client_id: str, service_numbers_by_site: Dict[str, List]) -> List[str]:
        # TODO add site id filtering
        service_numbers = [service_number for _, service_number_list in service_numbers_by_site
                           for service_number in service_number_list]
        open_tickets = await self._bruin_repository.get_open_tickets_with_serial_numbers(client_id)

        existing_tickets = list()
        for ticket in open_tickets:
            for service_number in service_numbers:
                if service_number in ticket['service_numbers']:
                    existing_tickets.append(ticket['ticketId'])

        return existing_tickets

    def _create_tickets(
            self,
            inference_data: Dict[str, Any],
            service_number_by_site: Dict[str, List],
            existing_tickets: List[str]
    ) -> List[str]:
        # TODO: Add content
        # Separate VOO/VAS
        # Update/Reopen/Open logic
        # Return created ticket_id
        # here be dragons
        pass

    @staticmethod
    def _is_inference_actionable(inference_data: Dict[str, Any]) -> bool:
        filtered = inference_data['filter_flags']['is_filtered']
        validation_set = inference_data['filter_flags']['is_validation_set']
        tagger_below_threshold = inference_data['filter_flags']['tagger_is_below_threshold']
        return not any([filtered, validation_set, tagger_below_threshold])
