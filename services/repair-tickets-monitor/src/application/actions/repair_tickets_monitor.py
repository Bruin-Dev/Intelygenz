import asyncio
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, DefaultDict, Dict, List, Set, Tuple

from application.exceptions import ResponseException
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone


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
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz)
            self._logger.info("RepairTicketsMonitor job is going to be executed immediately")

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
            self._logger.info(f"Skipping start of repair tickets monitor job. Reason: {conflict}")

    async def _run_repair_tickets_polling(self):
        """Poll the storage for new tagged emails create tasks to process those"""
        self._logger.info("Starting RepairTicketsMonitor process...")

        start_time = time.time()

        self._logger.info("Getting all tagged emails...")
        tagged_emails_by_stored_key: List[
            Dict[str, dict]
        ] = self._new_tagged_emails_repository.get_tagged_pending_emails()
        self._logger.info(tagged_emails_by_stored_key)
        repair_emails, other_tags_emails = self._triage_emails_by_tag(tagged_emails_by_stored_key)
        self._logger.info(f"Got {len(tagged_emails_by_stored_key)} tagged emails.")
        self._logger.info(f"Got {len(repair_emails)} Repair emails: {repair_emails}")
        self._logger.info(f"Got {len(other_tags_emails)} emails with meaningless tags: {other_tags_emails}")

        other_tags_tasks = [self._process_other_tags_email(email_data) for email_data in other_tags_emails]
        repair_tasks = [self._process_repair_email(email_data) for email_data in repair_emails]
        tasks = repair_tasks + other_tags_tasks

        output = await asyncio.gather(*tasks, return_exceptions=True)
        self._logger.info("RepairTicketsMonitor process finished! Took {:.3f}s".format(time.time() - start_time))
        self._logger.info(f"Output: {output}")

    def _triage_emails_by_tag(self, tagged_emails) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Separate between repair emails and non repair emails"""
        repair_tag_id = self._config.MONITOR_CONFIG["tag_ids"]["Repair"]
        repair_emails = [e for e in tagged_emails if str(e["tag_id"]) == str(repair_tag_id)]
        other_tags_emails = [e for e in tagged_emails if str(e["tag_id"]) != str(repair_tag_id)]

        return repair_emails, other_tags_emails

    async def _process_other_tags_email(self, email: Dict[str, Any]):
        """Process email that are not repair tickets"""
        tag_id = str(email["tag_id"])
        tag_name = [tag for tag, id_ in self._config.MONITOR_CONFIG["tag_ids"].items() if str(id_) == str(tag_id)][0]

        self._logger.info(f"Marking email {email['email_id']} as complete because it's tagged as '{tag_name}'")
        self._new_tagged_emails_repository.mark_complete(email["email_id"])

    async def _get_inference(self, email_data, tag_info):
        """Get the models inference for given email data"""
        cc_addresses = ", ".join(email_data.get("send_cc")) if email_data.get("send_cc") else ""

        prediction_response = await self._repair_tickets_kre_repository.get_email_inference(
            {
                "email_id": email_data["email_id"],
                "client_id": email_data["client_id"],
                "subject": email_data["subject"],
                "body": email_data["body"],
                "date": email_data["date"],
                "from_address": email_data["from_address"],
                "to": email_data["to_address"],
                "cc": cc_addresses,
            },
            tag_info,
        )
        if prediction_response["status"] not in range(200, 300):
            self._logger.info(f"Error prediction response status code {prediction_response['status']}")
            return
        return prediction_response.get("body")

    async def _save_output(
        self,
        email_id: str,
        service_number_sites_map: Dict[str, str] = None,
        tickets_created: List[Dict[str, Any]] = None,
        tickets_updated: List[Dict[str, Any]] = None,
        tickets_could_be_created: List[Dict[str, Any]] = None,
        tickets_could_be_updated: List[Dict[str, Any]] = None,
        tickets_cannot_be_created: List[Dict[str, Any]] = None,
    ):
        """Save the output from the ticket creation / inference verification"""
        service_number_sites_map = service_number_sites_map or {}
        tickets_created = tickets_created or []
        tickets_updated = tickets_updated or []
        tickets_could_be_created = tickets_could_be_created or []
        tickets_could_be_updated = tickets_could_be_updated or []
        tickets_cannot_be_created = tickets_cannot_be_created or []
        output_response = await self._repair_tickets_kre_repository.save_outputs(
            str(email_id),
            service_number_sites_map,
            tickets_created,
            tickets_updated,
            tickets_could_be_created,
            tickets_could_be_updated,
            tickets_cannot_be_created,
        )
        if output_response["status"] not in range(200, 300):
            self._logger.info(f"Error while saving output response status code {output_response['status']}")
            return
        return output_response.get("body")

    def get_site_ids_with_previous_cancellations(self, tickets: List[Dict[str, Any]]) -> List[str]:
        site_ids = set()
        for ticket in tickets:
            ticket_notes = ticket.get("ticket_notes")
            if ticket.get("ticket_status") == "Resolved" and ticket_notes:
                status, _ = self._bruin_repository._get_status_and_cancellation_reasons_from_notes(ticket_notes)
                if status == "cancelled":
                    site_ids.add(ticket["site_id"])
        return list(site_ids)

    def get_service_number_site_id_map_with_and_without_cancellations(
        self, service_number_site_map: Dict[str, str], site_ids_with_cancellations: Tuple[str]
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        service_number_site_id_map_with_cancellations = DefaultDict()
        service_number_site_id_map_without_cancellations = DefaultDict()

        for service_number, site_id in service_number_site_map.items():
            if site_id in site_ids_with_cancellations:
                service_number_site_id_map_with_cancellations[service_number] = site_id
            else:
                service_number_site_id_map_without_cancellations[service_number] = site_id

        return service_number_site_id_map_with_cancellations, service_number_site_id_map_without_cancellations

    def get_feedback_not_created_due_cancellations(
        self, map_with_cancellations: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        feedback_not_created_due_cancellations = []
        service_numbers_by_site_id_map = DefaultDict(list)
        for service_number, site_id in map_with_cancellations.items():
            service_numbers_by_site_id_map[site_id].append(service_number)

        for site_id, service_numbers in service_numbers_by_site_id_map.items():
            site_id_feedback = self._create_output_ticket_dict(
                site_id=site_id,
                service_numbers=service_numbers,
                reason="A previous ticket on that site was recently cancelled",
            )
            feedback_not_created_due_cancellations.append(site_id_feedback)
        return feedback_not_created_due_cancellations

    async def _process_repair_email(self, email_tag_info: Dict[str, Any]):
        """
        Process repair emails, verify it's service numbers, created/update tickets,
        and save the result of this operations into KRE.
        """
        email_id = email_tag_info["email_id"]
        email_data = self._new_tagged_emails_repository.get_email_details(email_id).get("email")
        email_data["tag"] = email_tag_info
        client_id = email_data["client_id"]
        self._logger.info(f"Running Repair Email Process for email_id: {email_id}")

        tickets_created = []
        tickets_updated = []
        tickets_could_be_created = []
        tickets_could_be_updated = []
        tickets_cannot_be_created = []

        async with self._semaphore:
            # Ask for potencial services numbers to KRE
            inference_data = await self._get_inference(email_data, email_tag_info)
            if not inference_data:
                self._logger.error(f"Could not process email {email_id}, marking it as complete")
                self._new_tagged_emails_repository.mark_complete(email_id)
                return

            potential_service_numbers = inference_data["potential_service_numbers"]
            try:
                # Check if the service number is valid against Bruin API
                service_number_site_map = await self._get_valid_service_numbers_site_map(
                    client_id, potential_service_numbers
                )
                existing_tickets = await self._get_existing_tickets(client_id, service_number_site_map)
            except ResponseException as e:
                self._logger.error(f"Error in bruin {e} could not process email: {email_id}")
                tickets_cannot_be_created.append(
                    self._create_output_ticket_dict(service_numbers=[], site_id="", reason=e)
                )

                await self._save_output(email_id, tickets_cannot_be_created=tickets_cannot_be_created)
                self._new_tagged_emails_repository.mark_complete(email_id)
                return

            # Remove site id with previous cancellations
            site_ids_with_previous_cancellations = self.get_site_ids_with_previous_cancellations(existing_tickets)
            self._logger.info("Found %s sites with previous cancellations", len(site_ids_with_previous_cancellations))
            (
                map_with_cancellations,
                map_without_cancellations,
            ) = self.get_service_number_site_id_map_with_and_without_cancellations(
                service_number_site_map, site_ids_with_previous_cancellations
            )
            self._logger.info("Evaluate services number without previous cancellations: %s ", map_without_cancellations)

            is_actionable = self._is_inference_actionable(inference_data)
            if is_actionable:
                tickets_created, tickets_updated, tickets_cannot_be_created = await self._create_tickets(
                    email_data,
                    map_without_cancellations,
                )
            elif not is_actionable and inference_data["predicted_class"] != "Other":
                if inference_data["predicted_class"] != "Other":
                    tickets_could_be_created, tickets_could_be_updated = self._get_potential_tickets(
                        inference_data,
                        service_number_site_map,
                        existing_tickets,
                    )
            else:
                tickets_cannot_be_created = self._get_class_other_tickets(service_number_site_map)

            feedback_not_created_due_cancellations = self.get_feedback_not_created_due_cancellations(
                map_with_cancellations
            )

            tickets_cannot_be_created += feedback_not_created_due_cancellations

            save_output_response = await self._save_output(
                email_id,
                service_number_site_map,
                tickets_created,
                tickets_updated,
                tickets_could_be_created,
                tickets_could_be_updated,
                tickets_cannot_be_created,
            )
            if not save_output_response:
                self._logger.error(f"Error while saving output for email: {email_id}")
                return

            # we only mark the email as done in bruin when at least one ticket has been created or updated,
            # and there is no cancellations in any site
            if (tickets_created or tickets_updated) and not feedback_not_created_due_cancellations:
                await self._bruin_repository.mark_email_as_done(email_id)

            self._new_tagged_emails_repository.mark_complete(email_id)
            return

    async def _get_valid_service_numbers_site_map(
        self, client_id: str, potential_service_numbers: List[str]
    ) -> Dict[str, str]:
        """Give a dictionary with keys as service numbers with their site ids"""
        service_number_site_map = {}
        for potential_service_number in potential_service_numbers:
            result = await self._bruin_repository.verify_service_number_information(client_id, potential_service_number)
            if result["status"] in range(200, 300):
                service_number_site_map[potential_service_number] = str(result["body"]["site_id"])
            elif result["status"] == 404:
                continue
            else:
                raise ResponseException(f"Exception while verifying service_number: {potential_service_number}")

        if not service_number_site_map:
            raise ResponseException("No validated service numbers")

        return service_number_site_map

    async def _get_existing_tickets(
        self, client_id: str, service_number_site_map: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Return a list of preexisting tickets that has not previous cancellations in bruin with the given sites.
        """
        service_numbers = list(service_number_site_map.keys())
        site_ids = list(set(service_number_site_map.values()))

        existing_tickets = await self._bruin_repository.get_existing_tickets_with_service_numbers(client_id, site_ids)

        # Manage status
        if existing_tickets["status"] == 404:
            return []
        elif existing_tickets["status"] != 200:
            raise ResponseException("Exception while getting bruin response for existing tickets")

        # Try to add site_id to tickets with services numbers
        tickets_with_site_id = []
        for ticket in existing_tickets["body"]:
            for service_number in service_numbers:
                if service_number in ticket["service_numbers"]:
                    ticket["site_id"] = service_number_site_map[service_number]
                    tickets_with_site_id.append(ticket)
                    break

        return tickets_with_site_id

    async def _create_tickets(
        self,
        email_data: Dict[str, Any],
        service_number_site_map: Dict[str, str],
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Try to create tickets for valid service_number
        """
        site_id_sn_buckets = defaultdict(list)

        for service_number, site_id in service_number_site_map.items():
            site_id_sn_buckets[site_id].append(service_number)

        email_id = email_data["email_id"]
        client_id = email_data["client_id"]
        email_body = email_data["body"]
        email_subject = email_data["subject"]
        email_from_address = email_data["from_address"]
        email_date = email_data["date"]

        tickets_created = []
        tickets_updated = []
        tickets_cannot_be_created = []

        for site_id, service_numbers in site_id_sn_buckets.items():
            ticket_creation_response = await self._bruin_repository.create_outage_ticket(
                client_id, service_numbers, email_from_address
            )
            ticket_creation_response_body = ticket_creation_response["body"]
            ticket_creation_response_status = ticket_creation_response["status"]
            self._logger.info(
                f"Got response {ticket_creation_response_status}," f" with items: {ticket_creation_response_body}"
            )

            error_response = False
            ticket_updated_flag = False

            bruin_updated_reasons_dict = {
                409: "In progress ticket present. Added line to it.",
                471: "Resolved ticket. Unresolving 'manually'.",
                472: "Resolved ticket. Unresolved automatically.",
                473: "Same site ticket. Unresolved and added line.",
            }
            bruin_custom_status_codes = [409, 471, 472, 473]

            if ticket_creation_response_status in range(200, 300):
                ticket_id = ticket_creation_response_body
                self._logger.info(f"Successfully created outage ticket {ticket_id} for email_id {email_id}.")
                created_ticket = self._create_output_ticket_dict(
                    ticket_id=str(ticket_id), site_id=str(site_id), service_numbers=service_numbers
                )
                tickets_created.append(created_ticket)

            elif ticket_creation_response_status in bruin_custom_status_codes:
                ticket_id = ticket_creation_response_body
                update_reason = bruin_updated_reasons_dict[ticket_creation_response_status]
                self._logger.info(
                    f"Ticket already present bruin response {ticket_creation_response_status},"
                    f"reason: {update_reason}"
                )
                updated_ticket = self._create_output_ticket_dict(
                    ticket_id=str(ticket_id), site_id=str(site_id), service_numbers=service_numbers
                )
                tickets_updated.append(updated_ticket)
                ticket_updated_flag = True

            else:
                self._logger.error(
                    f"Got error {ticket_creation_response_status}, {ticket_creation_response_body}"
                    f"while creating ticket for {service_numbers} and client {client_id}"
                )
                error_response = True
                ticket_cannot_be_created = self._create_output_ticket_dict(
                    site_id=str(site_id), service_numbers=service_numbers, reason="Error while creating bruin ticket"
                )
                tickets_cannot_be_created.append(ticket_cannot_be_created)

            if not error_response:
                ticket_id = ticket_creation_response_body
                await self._bruin_repository.append_bec_note_to_ticket(
                    ticket_id=ticket_id,
                    service_numbers=service_numbers,
                    subject=email_subject,
                    from_address=email_from_address,
                    body=email_body,
                    date=email_date,
                    is_update_note=ticket_updated_flag,
                )
                await self._bruin_repository.link_email_to_ticket(ticket_id, email_id)

        return tickets_created, tickets_updated, tickets_cannot_be_created

    def _get_potential_tickets(
        self,
        inference_data: Dict[str, Any],
        service_number_site_map: Dict[str, str],
        existing_tickets: List[Dict[str, Any]],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Get potential updated/created tickets"""
        potential_created_tickets = []
        potential_updated_tickets = []

        predicted_class = inference_data["predicted_class"]
        site_ids = set(service_number_site_map.values())

        for ticket in existing_tickets:
            if self._should_update_ticket(ticket, site_ids, predicted_class):
                potential_updated_tickets.append(
                    self._create_output_ticket_dict(
                        site_id=ticket["site_id"],
                        service_numbers=ticket["service_numbers"],
                        ticket_id=str(ticket["ticket_id"]),
                    )
                )
                site_ids.remove(ticket["site_id"])

        for site_id in site_ids:
            service_numbers_filtered_by_site_id = [
                service_number
                for service_number, service_site_id in service_number_site_map.items()
                if service_site_id == site_id
            ]
            potential_created_tickets.append(
                self._create_output_ticket_dict(
                    site_id=site_id,
                    service_numbers=service_numbers_filtered_by_site_id,
                )
            )

        return potential_created_tickets, potential_updated_tickets

    def _get_class_other_tickets(
        self,
        service_number_site_map: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        not_created_tickets = []
        site_ids = set(service_number_site_map.values())

        for site_id in site_ids:
            service_numbers_filtered_by_site_id = [
                service_number
                for service_number, service_site_id in service_number_site_map.items()
                if service_site_id == site_id
            ]
            not_created_tickets.append(
                self._create_output_ticket_dict(
                    site_id=site_id,
                    service_numbers=service_numbers_filtered_by_site_id,
                    reason="predicted class is Other",
                )
            )

        return not_created_tickets

    @staticmethod
    def _create_output_ticket_dict(
        site_id: str,
        service_numbers: List[str],
        ticket_id: str = "",
        reason: str = "",
    ) -> Dict[str, Any]:
        """Create a dict for output purposes"""
        return {
            "site_id": site_id,
            "service_numbers": service_numbers,
            "ticket_id": ticket_id,
            "not_creation_reason": reason,
        }

    @staticmethod
    def _should_update_ticket(ticket: Dict[str, Any], site_ids: Set[str], predicted_class: str) -> bool:
        """Check if existing ticket should be updated"""
        ticket_category = ticket["category"]
        if ticket["site_id"] not in site_ids:
            return False

        if ticket_category not in ["VOO", "VAS"]:
            return False

        if predicted_class == ticket_category:
            return True
        elif predicted_class == "VOO" and ticket_category == "VAS":
            return False
        elif predicted_class == "VAS" and ticket_category == "VOO":
            return True

    @staticmethod
    def _is_inference_actionable(inference_data: Dict[str, Any]) -> bool:
        """Check if the inference can be used to create/update a ticket"""
        is_other = inference_data["predicted_class"] == "Other"
        filtered = inference_data["filter_flags"]["is_filtered"]
        validation_set = inference_data["filter_flags"]["in_validation_set"]
        tagger_below_threshold = inference_data["filter_flags"]["tagger_is_below_threshold"]
        rta_model1_is_below_threshold = inference_data["filter_flags"]["rta_model1_is_below_threshold"]
        rta_model2_is_below_threshold = inference_data["filter_flags"]["rta_model2_is_below_threshold"]

        return not any(
            [
                filtered,
                validation_set,
                tagger_below_threshold,
                is_other,
                rta_model1_is_below_threshold,
                rta_model2_is_below_threshold,
            ]
        )
