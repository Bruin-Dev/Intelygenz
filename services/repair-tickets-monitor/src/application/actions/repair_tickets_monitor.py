import os
from collections import defaultdict
from datetime import datetime
from typing import Any, DefaultDict, Dict, List, Set, Tuple

import asyncio
import html2text
import time
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone

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
        if any(output):
            self._logger.error("Unexpected output in repair monitor coroutines: %s", output)

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
        email_id = email_data["email_id"]
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
        if prediction_response["status"] != 200:
            self._logger.info(
                "email_id=%s Error prediction response status code %s %s",
                email_id,
                prediction_response["status"],
                prediction_response["body"],
            )
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
        validated_ticket_numbers: List[Dict[str, Any]] = None,
        bruin_ticket_status_map: Dict[str, Any] = None,
        bruin_ticket_call_type_map: Dict[str, Any] = None,
        bruin_ticket_category_map: Dict[str, Any] = None,
    ):
        """Save the output from the ticket creation / inference verification"""
        service_number_sites_map = service_number_sites_map or {}
        tickets_created = tickets_created or []
        tickets_updated = tickets_updated or []
        tickets_could_be_created = tickets_could_be_created or []
        tickets_could_be_updated = tickets_could_be_updated or []
        tickets_cannot_be_created = tickets_cannot_be_created or []
        validated_ticket_numbers = validated_ticket_numbers or []
        bruin_ticket_status_map = bruin_ticket_status_map or {}
        bruin_ticket_call_type_map = bruin_ticket_call_type_map or {}
        bruin_ticket_category_map = bruin_ticket_category_map or {}

        output_response = await self._repair_tickets_kre_repository.save_outputs(
            str(email_id),
            service_number_sites_map,
            tickets_created,
            tickets_updated,
            tickets_could_be_created,
            tickets_could_be_updated,
            tickets_cannot_be_created,
            validated_ticket_numbers,
            bruin_ticket_status_map,
            bruin_ticket_call_type_map,
            bruin_ticket_category_map,
        )
        if output_response["status"] != 200:
            self._logger.error("email_id=%s Error while saving output %s", email_id, output_response)
            return
        return output_response["body"]

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

    async def _get_validated_ticket_numbers(self, tickets_id: List[int]) -> Dict[str, dict]:
        """
        Return the tickets that already exist in Bruin
        """
        validated_tickets = defaultdict(dict)
        validated_tickets['validated_ticket_numbers'] = []

        for ticket_id in tickets_id:
            bruin_bridge_response = await self._bruin_repository.get_single_ticket_basic_info(ticket_id)
            if bruin_bridge_response["status"] == 200:
                ticket_id = bruin_bridge_response["body"]['ticket_id']

                validated_tickets["validated_ticket_numbers"].append(ticket_id)
                validated_tickets["bruin_ticket_status_map"][ticket_id] = bruin_bridge_response["body"]["ticket_status"]
                validated_tickets["bruin_ticket_call_type_map"][ticket_id] = bruin_bridge_response["body"]["call_type"]
                validated_tickets["bruin_ticket_category_map"][ticket_id] = bruin_bridge_response["body"]["category"]

        return validated_tickets

    async def _process_repair_email(self, email_tag_info: Dict[str, Any]):
        """
        Process repair emails, verify it's service numbers, created/update tickets,
        and save the result of this operations into KRE.
        """
        email_id = email_tag_info["email_id"]
        self._logger.info("email_id=%s Running Repair Email Process", email_id)
        email_data = self._new_tagged_emails_repository.get_email_details(email_id).get("email")
        email_data["tag"] = email_tag_info
        client_id = email_data["client_id"]

        tickets_created = []
        tickets_updated = []
        tickets_could_be_created = []
        tickets_could_be_updated = []
        tickets_cannot_be_created = []

        async with self._semaphore:
            # Ask for potential services numbers to KRE
            inference_data = await self._get_inference(email_data, email_tag_info)
            if not inference_data:
                self._logger.error("email_id=%s No inference data. Marking email as complete in Redis", email_id)
                self._new_tagged_emails_repository.mark_complete(email_id)
                return

            potential_service_numbers = inference_data.get("potential_service_numbers")
            if potential_service_numbers is None:
                potential_service_numbers = []

            potential_ticket_numbers = inference_data.get("potential_ticket_numbers")
            if potential_ticket_numbers is None:
                potential_ticket_numbers = []

            self._logger.info(
                "email_id=%s inference: potential services numbers=%s potential_tickets_numbers=%s",
                email_id,
                potential_service_numbers,
                potential_ticket_numbers,
            )

            try:
                # Check if the service number is valid against Bruin API
                service_number_site_map = await self._get_valid_service_numbers_site_map(
                    client_id, potential_service_numbers
                )
                self._logger.info("email_id=%s service_numbers_site_map=%s", email_id, service_number_site_map)
                existing_tickets = await self._get_existing_tickets(client_id, service_number_site_map)
                self._logger.info("email_id=%s existing_tickets=%s", email_id, existing_tickets)
            except ResponseException as e:
                self._logger.error("email_id=%s Error in bruin %s, could not process email", email_id, e)
                tickets_cannot_be_created.append(
                    self._create_output_ticket_dict(service_numbers=[], site_id="", reason=e)
                )

                await self._save_output(email_id, tickets_cannot_be_created=tickets_cannot_be_created)
                self._new_tagged_emails_repository.mark_complete(email_id)
                return

            # Remove site id with previous cancellations
            site_ids_with_previous_cancellations = self.get_site_ids_with_previous_cancellations(existing_tickets)
            self._logger.info(
                "email_id=%s Found %s sites with previous cancellations",
                email_id,
                len(site_ids_with_previous_cancellations),
            )
            (
                map_with_cancellations,
                map_without_cancellations,
            ) = self.get_service_number_site_id_map_with_and_without_cancellations(
                service_number_site_map, site_ids_with_previous_cancellations
            )
            self._logger.info(
                "email_id=%s map_with_cancellations=%s map_without_cancellations=%s",
                email_id,
                map_with_cancellations,
                map_without_cancellations,
            )

            is_actionable = self._is_inference_actionable(inference_data)
            self._logger.info(
                "email_id=%s is_actionable=%s predicted_class=%s",
                email_id,
                is_actionable,
                inference_data.get("predicted_class"),
            )
            if is_actionable:
                tickets_created, tickets_updated, tickets_cannot_be_created = await self._create_tickets(
                    email_data,
                    map_without_cancellations,
                )
            elif not is_actionable and inference_data["predicted_class"] != "Other":
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

            validated_tickets = (
                await self._get_validated_ticket_numbers(potential_ticket_numbers)
                if potential_ticket_numbers
                else defaultdict(list)
            )

            output_send_to_save = {
                "service_number_sites_map": service_number_site_map,
                "tickets_created": tickets_created,
                "tickets_updated": tickets_updated,
                "tickets_could_be_created": tickets_could_be_created,
                "tickets_could_be_updated": tickets_could_be_updated,
                "tickets_cannot_be_created": tickets_cannot_be_created,
                "validated_ticket_numbers": validated_tickets["validated_ticket_numbers"],
                "bruin_ticket_status_map": validated_tickets["bruin_ticket_status_map"],
                "bruin_ticket_call_type_map": validated_tickets["bruin_ticket_call_type_map"],
                "bruin_ticket_category_map": validated_tickets["bruin_ticket_category_map"],
            }
            self._logger.info("email_id=%s output_send_to_save=%s", email_id, output_send_to_save)
            await self._save_output(email_id, **output_send_to_save)

            # we only mark the email as done in bruin when at least one ticket has been created or updated,
            # and there is no cancellations in any site
            if (tickets_created or tickets_updated) and not feedback_not_created_due_cancellations:
                self._logger.info("email_id=%s Calling bruin to mark email as done", email_id)
                await self._bruin_repository.mark_email_as_done(email_id)

            self._logger.info("email_id=%s Removing email from Redis", email_id)
            self._new_tagged_emails_repository.mark_complete(email_id)
            return

    async def _get_valid_service_numbers_site_map(
        self, client_id: str, potential_service_numbers: List[str]
    ) -> Dict[str, str]:
        """Give a dictionary with keys as service numbers with their site ids"""
        service_number_site_map = {}
        for potential_service_number in potential_service_numbers:
            result = await self._bruin_repository.verify_service_number_information(client_id, potential_service_number)
            if result["status"] == 200:
                service_number_site_map[potential_service_number] = str(result["body"]["site_id"])
            elif result["status"] == 404:
                continue
            else:
                raise ResponseException(f"Exception while verifying service_number: {potential_service_number}")

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

    def _compose_bec_note_to_ticket(
        self,
        ticket_id: int,
        service_numbers: List[str],
        subject: str,
        from_address: str,
        body: str,
        date: datetime,
        is_update_note: bool = False,
    ) -> List[Dict]:
        new_ticket_message = "This ticket was opened via MetTel Email Center AI Engine."
        update_ticket_message = "This note is new commentary from the client and posted via BEC AI engine."
        operator_message = update_ticket_message if is_update_note else new_ticket_message
        body_cleaned = html2text.html2text(body)

        note_text = os.linesep.join(
            [
                "#*MetTel's IPA*#",
                "BEC AI RTA",
                "",
                operator_message,
                "Please review the full narrative provided in the email attached:\n" f"From: {from_address}",
                f"Date Stamp: {date}",
                f"Subject: {subject}",
                f"Body: \n {body_cleaned}",
            ]
        )
        notes = [{"text": note_text, "service_number": service_number} for service_number in service_numbers]
        self._logger.info("ticket_id=%s Sending note: %s", ticket_id, notes)

        return notes

    async def _create_tickets(
        self,
        email_data: Dict[str, Any],
        service_number_site_map: Dict[str, str],
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Try to create tickets for valid service_number
        """
        email_id = email_data["email_id"]
        client_id = email_data["client_id"]
        email_body = email_data["body"]
        email_subject = email_data["subject"]
        email_from_address = email_data["from_address"]
        email_date = email_data["date"]

        bruin_updated_reasons_dict = {
            409: "In progress ticket present. Added line to it.",
            471: "Resolved ticket. Unresolving 'manually'.",
            472: "Resolved ticket. Unresolved automatically.",
            473: "Same site ticket. Unresolved and added line.",
        }

        # Return data
        tickets_created = []
        tickets_updated = []
        tickets_cannot_be_created = []

        site_id_sn_buckets = defaultdict(list)
        for service_number, site_id in service_number_site_map.items():
            site_id_sn_buckets[site_id].append(service_number)

        for site_id, service_numbers in site_id_sn_buckets.items():
            ticket_creation_response = await self._bruin_repository.create_outage_ticket(
                client_id, service_numbers, email_from_address
            )
            ticket_creation_response_body = ticket_creation_response["body"]
            ticket_creation_response_status = ticket_creation_response["status"]
            self._logger.info(
                "email_id=%s Got response %s, with items: %s",
                email_id,
                ticket_creation_response_status,
                ticket_creation_response_body,
            )

            error_response = False
            ticket_updated_flag = False

            if ticket_creation_response_status == 200:
                ticket_id = ticket_creation_response_body
                self._logger.info("email_id=%s Successfully created outage ticket %s", email_id, ticket_id)
                created_ticket = self._create_output_ticket_dict(
                    ticket_id=str(ticket_id), site_id=str(site_id), service_numbers=service_numbers
                )
                tickets_created.append(created_ticket)
            elif ticket_creation_response_status in bruin_updated_reasons_dict.keys():
                ticket_id = ticket_creation_response_body
                update_reason = bruin_updated_reasons_dict[ticket_creation_response_status]
                self._logger.info(
                    "email_id=%s Ticket already present bruin response %s reason: %s",
                    email_id,
                    ticket_creation_response_status,
                    update_reason,
                )
                updated_ticket = self._create_output_ticket_dict(
                    ticket_id=str(ticket_id), site_id=str(site_id), service_numbers=service_numbers
                )
                tickets_updated.append(updated_ticket)
                ticket_updated_flag = True
            else:
                self._logger.error(
                    "email_id=%s Got error %s, %s while creating ticket for %s and client %s",
                    email_id,
                    ticket_creation_response_status,
                    ticket_creation_response_body,
                    service_numbers,
                    client_id,
                )
                error_response = True
                ticket_cannot_be_created = self._create_output_ticket_dict(
                    site_id=str(site_id), service_numbers=service_numbers, reason="Error while creating bruin ticket"
                )
                tickets_cannot_be_created.append(ticket_cannot_be_created)

            if not error_response:
                ticket_id = ticket_creation_response_body
                notes_to_append = self._compose_bec_note_to_ticket(
                    ticket_id=ticket_id,
                    service_numbers=service_numbers,
                    subject=email_subject,
                    from_address=email_from_address,
                    body=email_body,
                    date=email_date,
                    is_update_note=ticket_updated_flag,
                )

                await self._bruin_repository.append_notes_to_ticket(ticket_id, notes_to_append)
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

        return not any(
            [
                filtered,
                validation_set,
                tagger_below_threshold,
                is_other,
                rta_model1_is_below_threshold,
            ]
        )
