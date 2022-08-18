import asyncio
import logging
import os
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, DefaultDict, Dict, List, Set, Tuple

import html2text
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.util import undefined
from framework.nats.client import Client as NatsClient
from pytz import timezone

from application import resources
from application.domain.asset import Asset, AssetId, Assets
from application.domain.email import Email, EmailStatus
from application.domain.repair_email_output import (
    CreateTicketsOutput,
    PotentialTicketsOutput,
    RepairEmailOutput,
    TicketOutput,
)
from application.domain.ticket import Category, Ticket, TicketStatus
from application.exceptions import ResponseException
from application.repositories.bruin_repository import BruinRepository
from application.repositories.new_tagged_emails_repository import NewTaggedEmailsRepository
from application.repositories.repair_ticket_kre_repository import RepairTicketKreRepository
from application.rpc import RpcError
from application.rpc.append_note_to_ticket_rpc import AppendNoteToTicketRpc
from application.rpc.get_asset_topics_rpc import GetAssetTopicsRpc
from application.rpc.send_email_reply_rpc import SendEmailReplyRpc
from application.rpc.set_email_status_rpc import SetEmailStatusRpc
from application.rpc.subscribe_user_rpc import SubscribeUserRpc
from application.rpc.upsert_outage_ticket_rpc import UpsertedStatus, UpsertedTicket, UpsertOutageTicketRpc

log = logging.getLogger(__name__)


def get_feedback_not_created_due_cancellations(map_with_cancellations: Dict[str, str]) -> List[TicketOutput]:
    feedback_not_created_due_cancellations = []
    service_numbers_by_site_id_map = defaultdict(list)
    for service_number, site_id in map_with_cancellations.items():
        service_numbers_by_site_id_map[site_id].append(service_number)

    for site_id, service_numbers in service_numbers_by_site_id_map.items():
        site_id_feedback = TicketOutput(
            site_id=site_id,
            service_numbers=service_numbers,
            reason="A previous ticket on that site was recently cancelled",
        )
        feedback_not_created_due_cancellations.append(site_id_feedback)
    return feedback_not_created_due_cancellations


@dataclass
class RepairTicketsMonitor:
    _event_bus: NatsClient
    _scheduler: AsyncIOScheduler
    _config: Any
    _bruin_repository: BruinRepository
    _new_tagged_emails_repository: NewTaggedEmailsRepository
    _repair_tickets_kre_repository: RepairTicketKreRepository
    _append_note_to_ticket_rpc: AppendNoteToTicketRpc
    _get_asset_topics_rpc: GetAssetTopicsRpc
    _upsert_outage_ticket_rpc: UpsertOutageTicketRpc
    _subscribe_user_rpc: SubscribeUserRpc
    _set_email_status_rpc: SetEmailStatusRpc
    _send_email_reply_rpc: SendEmailReplyRpc

    def __post_init__(self):
        self._semaphore = asyncio.BoundedSemaphore(
            self._config.MONITOR_CONFIG["semaphores"]["repair_tickets_concurrent"]
        )

    async def start_repair_tickets_monitor(self, exec_on_start: bool = False):
        """Start the monitor scheduled checks, to process input emails."""
        log.info("Scheduling RepairTicketsMonitor job...")
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz)
            log.info("RepairTicketsMonitor job is going to be executed immediately")

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
            log.info(f"Skipping start of repair tickets monitor job. Reason: {conflict}")

    async def _run_repair_tickets_polling(self):
        """Poll the storage for new tagged emails create tasks to process those"""
        log.info("Starting RepairTicketsMonitor process...")

        start_time = time.time()

        log.info("Getting all tagged emails...")
        pending_emails: List[Email] = self._new_tagged_emails_repository.get_tagged_pending_emails()
        log.info(pending_emails)
        repair_emails, other_tags_emails = self._triage_emails_by_tag(pending_emails)
        log.info(f"Got {len(pending_emails)} tagged emails.")
        log.info(f"Got {len(repair_emails)} Repair emails: {repair_emails}")
        log.info(f"Got {len(other_tags_emails)} emails with meaningless tags: {other_tags_emails}")

        other_tags_tasks = [self._process_other_tags_email(email_data) for email_data in other_tags_emails]
        repair_tasks = [self._process_repair_email(email_data) for email_data in repair_emails]
        tasks = repair_tasks + other_tags_tasks

        output = await asyncio.gather(*tasks, return_exceptions=True)
        log.info("RepairTicketsMonitor process finished! Took {:.3f}s".format(time.time() - start_time))
        if any(output):
            log.error("Unexpected output in repair monitor coroutines: %s", output)

    def _triage_emails_by_tag(self, tagged_emails: List[Email]) -> Tuple[List[Email], List[Email]]:
        """Separate between repair emails and non repair emails"""
        repair_tag_id = self._config.MONITOR_CONFIG["tag_ids"]["Repair"]
        repair_emails = [e for e in tagged_emails if str(e.tag.type) == str(repair_tag_id)]
        other_tags_emails = [e for e in tagged_emails if str(e.tag.type) != str(repair_tag_id)]

        return repair_emails, other_tags_emails

    async def _process_other_tags_email(self, email: Email):
        """Process email that are not repair tickets"""
        tag_name = [
            tag for tag, id_ in self._config.MONITOR_CONFIG["tag_ids"].items() if str(id_) == str(email.tag.type)
        ][0]

        log.info(f"Marking email {email.id} as complete because it's tagged as '{tag_name}'")
        self._new_tagged_emails_repository.mark_complete(email.id)

    async def _get_inference(self, email: Email):
        """Get the models inference for given email data"""
        prediction_response = await self._repair_tickets_kre_repository.get_email_inference(
            {
                "email_id": email.id,
                "client_id": email.client_id,
                "subject": email.subject,
                "body": email.body,
                "date": email.date.isoformat(),
                "from_address": email.sender_address,
                "to": email.recipient_addresses,
                "cc": email.comma_separated_cc_addresses(),
                "is_auto_reply_answer": email.is_reply_email,
                "auto_reply_answer_delay": email.reply_interval,
            },
            {
                "tag_probability": email.tag.probability,
            },
        )

        if prediction_response["status"] != 200:
            log.info(
                "email_id=%s Error prediction response status code %s %s",
                email.id,
                prediction_response["status"],
                prediction_response["body"],
            )
            return
        return prediction_response.get("body")

    async def _save_output(self, output: RepairEmailOutput):
        """Save the output from the ticket creation / inference verification"""
        output_response = await self._repair_tickets_kre_repository.save_outputs(output)

        if output_response["status"] != 200:
            log.error("email_id=%s Error while saving output %s", output.email_id, output_response)
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

    @staticmethod
    def get_service_number_site_id_map_with_and_without_cancellations(
        service_number_site_map: Dict[str, str], site_ids_with_cancellations: List[str]
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        service_number_site_id_map_with_cancellations = DefaultDict[str, str]()
        service_number_site_id_map_without_cancellations = DefaultDict[str, str]()

        for service_number, site_id in service_number_site_map.items():
            if site_id in site_ids_with_cancellations:
                service_number_site_id_map_with_cancellations[service_number] = site_id
            else:
                service_number_site_id_map_without_cancellations[service_number] = site_id

        return service_number_site_id_map_with_cancellations, service_number_site_id_map_without_cancellations

    # To be refactored in an RPC
    async def _get_tickets(self, email_id: str, tickets_id: List[str]) -> List[Ticket]:
        """
        Return the tickets that already exist in Bruin
        """
        validated_tickets = []

        for ticket_id in tickets_id:
            bruin_bridge_response = await self._bruin_repository.get_single_ticket_basic_info(ticket_id)
            if bruin_bridge_response["status"] == 200:
                try:
                    ticket_status_raw = str(bruin_bridge_response["body"]["ticket_status"])
                    # Remove the dash for In-Progress and In-Review status
                    ticket_status_raw = ticket_status_raw.replace("-", "")
                    ticket_status = TicketStatus(ticket_status_raw)
                except ValueError as e:
                    ticket_status = TicketStatus.UNKNOWN
                    log.warning(
                        "email_id=%s Unknown ticket status, response=%s, error=%s", email_id, bruin_bridge_response, e
                    )

                ticket = Ticket(
                    id=str(bruin_bridge_response["body"]["ticket_id"]),
                    status=ticket_status,
                    call_type=bruin_bridge_response["body"]["call_type"],
                    category=bruin_bridge_response["body"]["category"],
                )

                validated_tickets.append(ticket)

        return validated_tickets

    async def _process_repair_email(self, email: Email):
        """
        Process repair emails, verify it's service numbers, created/update tickets,
        and save the result of this operations into KRE.
        """
        log.info("email_id=%s Running Repair Email Process", email.id)

        output = RepairEmailOutput(email_id=email.id)
        async with self._semaphore:
            # Ask for potential services numbers to KRE
            inference_data = await self._get_inference(email)
            if not inference_data:
                log.error("email_id=%s No inference data. Marking email as complete in Redis", email.id)
                self._new_tagged_emails_repository.mark_complete(email.id)
                return

            auto_reply_whitelist = self._config.MONITOR_CONFIG["auto_reply_whitelist"]
            auto_reply_allowed = False
            if len(auto_reply_whitelist) > 0:
                auto_reply_allowed = any(
                    recipient_email.lower() in auto_reply_whitelist for recipient_email in email.recipient_addresses
                )

            is_actionable = self._is_inference_actionable(inference_data)
            is_ticket_actionable = self._is_ticket_actionable(inference_data)

            potential_service_numbers = inference_data.get("potential_service_numbers")
            if potential_service_numbers is None:
                potential_service_numbers = []

            potential_ticket_numbers = inference_data.get("potential_ticket_numbers")
            if potential_ticket_numbers is None:
                potential_ticket_numbers = []

            log.info(
                "email_id=%s inference: potential services numbers=%s potential_tickets_numbers=%s",
                email.id,
                potential_service_numbers,
                potential_ticket_numbers,
            )

            output.validated_tickets = await self._get_tickets(email.id, potential_ticket_numbers)

            try:
                # Check if the service number is valid against Bruin API
                service_number_site_map = await self._get_valid_service_numbers_site_map(
                    email.client_id, potential_service_numbers
                )
                output.service_numbers_sites_map = service_number_site_map
                log.info("email_id=%s service_numbers_site_map=%s", email.id, service_number_site_map)

                # Build the assets list
                # This logic will be refactored into a new email_service.extract_entities() method

                assets = Assets()
                for service_number, site_id in service_number_site_map.items():
                    asset_id = AssetId(client_id=email.client_id, site_id=site_id, service_number=service_number)

                    try:
                        allowed_asset_topics = await self._get_asset_topics_rpc(asset_id)
                    except RpcError as e:
                        # TODO: sent slack notification
                        allowed_asset_topics = []
                        log.warning(
                            f"[email_id={email.id}] _process_repair_email():" f"get_topics_device_rpc({asset_id}): {e}"
                        )

                    asset = Asset(id=asset_id, allowed_topics=allowed_asset_topics)
                    assets.append(asset)

                assets_without_topics = assets.with_no_topics()
                assets_with_topics = Assets(asset for asset in assets if asset not in assets_without_topics)

                allowed_assets = assets_with_topics.with_allowed_category(Category.SERVICE_OUTAGE.value)
                not_allowed_assets = Assets(asset for asset in assets_with_topics if asset not in allowed_assets)

                wireless_assets = not_allowed_assets.with_allowed_category(Category.WIRELESS_SERVICE_NOT_WORKING.value)
                other_category_assets = Assets(asset for asset in not_allowed_assets if asset not in wireless_assets)

                allowed_service_number_site_map = {
                    asset.id.service_number: asset.id.site_id for asset in allowed_assets
                }
                log.info("email_id=%s allowed_service_numbers_site_map=%s", email.id, allowed_service_number_site_map)

                if wireless_assets:
                    output.tickets_cannot_be_created.append(TicketOutput(reason="contains_wireless_assets"))
                elif other_category_assets:
                    output.tickets_cannot_be_created.append(TicketOutput(reason="contains_other_assets"))
                elif assets_without_topics:
                    output.tickets_cannot_be_created.append(TicketOutput(reason="no_topics_detected"))

                # Gather any existing tickets for the extracted assets
                existing_tickets = await self._get_existing_tickets(email.client_id, allowed_service_number_site_map)
                log.info("email_id=%s existing_tickets=%s", email.id, existing_tickets)
            except ResponseException as e:
                log.error("email_id=%s Error in bruin %s, could not process email", email.id, e)
                output.tickets_cannot_be_created.append(TicketOutput(reason=str(e)))
                await self._save_output(output)

                self._new_tagged_emails_repository.mark_complete(email.id)
                return

            # Remove site id with previous cancellations
            site_ids_with_previous_cancellations = self.get_site_ids_with_previous_cancellations(existing_tickets)
            log.info(
                "email_id=%s Found %s sites with previous cancellations",
                email.id,
                len(site_ids_with_previous_cancellations),
            )
            (
                map_with_cancellations,
                map_without_cancellations,
            ) = self.get_service_number_site_id_map_with_and_without_cancellations(
                allowed_service_number_site_map, site_ids_with_previous_cancellations
            )
            log.info(
                "email_id=%s map_with_cancellations=%s map_without_cancellations=%s",
                email.id,
                map_with_cancellations,
                map_without_cancellations,
            )

            log.info(
                "email_id=%s is_actionable=%s predicted_class=%s",
                email.id,
                is_actionable,
                inference_data.get("predicted_class"),
            )

            if is_actionable:
                create_tickets_output = await self._create_tickets(
                    email,
                    map_without_cancellations,
                )
                output.extend(create_tickets_output)

            elif not is_actionable and inference_data["predicted_class"] != "Other":
                potential_tickets_output = self._get_potential_tickets(
                    inference_data,
                    allowed_service_number_site_map,
                    existing_tickets,
                )
                output.extend(potential_tickets_output)

            else:
                output.tickets_cannot_be_created = self._get_class_other_tickets(allowed_service_number_site_map)

            feedback_not_created_due_cancellations = get_feedback_not_created_due_cancellations(map_with_cancellations)

            output.tickets_cannot_be_created.extend(feedback_not_created_due_cancellations)

            # Tickets processing
            operable_tickets = [
                ticket for ticket in output.validated_tickets if ticket.is_active() and ticket.is_repair()
            ]

            if not allowed_service_number_site_map:
                if is_ticket_actionable:
                    for ticket in operable_tickets:
                        ticket_updated = await self._update_ticket(ticket, email)
                        if ticket_updated:
                            output.tickets_updated.append(
                                TicketOutput(ticket_id=ticket.id, reason="update_with_ticket_found")
                            )
                else:
                    for ticket in operable_tickets:
                        output.tickets_could_be_updated.append(TicketOutput(ticket_id=ticket.id))

            if not service_number_site_map and not output.tickets_updated and not output.tickets_could_be_updated:
                log.info(f"email_id={email.id} No service number nor ticket actions triggered")
                auto_reply_reason = "No validated service numbers"

                auto_reply_enabled = self._config.MONITOR_CONFIG["auto_reply_enabled"]
                log.info(f"email_id={email.id} auto_reply_enabled={auto_reply_enabled}")
                log.info(f"email_id={email.id} auto_reply_allowed={auto_reply_allowed}")

                send_auto_reply = auto_reply_enabled and auto_reply_allowed
                if email.is_parent_email and is_actionable and not output.validated_tickets and send_auto_reply:
                    log.info(f"email_id={email.id} Sending auto-reply")
                    auto_reply_reason = "No validated service numbers. Sent auto-reply"
                    await self._set_email_status_rpc(email.id, EmailStatus.AIQ)
                    await self._send_email_reply_rpc(email.id, resources.AUTO_REPLY_BODY)
                    self._new_tagged_emails_repository.save_parent_email(email)
                elif email.is_reply_email:
                    log.info(f"email_id={email.id} Restoring parent_email {email.parent.id}")
                    await self._set_email_status_rpc(email.parent.id, EmailStatus.NEW)

                output.tickets_cannot_be_created.append(TicketOutput(reason=auto_reply_reason))

            log.info("email_id=%s output_send_to_save=%s", email.id, output)
            await self._save_output(output)

            # we only mark the email as done in bruin when at least one ticket has been created or updated,
            # and there is no cancellations in any site
            tickets_automated = output.tickets_created or output.tickets_updated
            no_tickets_failed = not output.tickets_cannot_be_created
            if tickets_automated and no_tickets_failed and not feedback_not_created_due_cancellations:
                log.info("email_id=%s Calling bruin to mark email as done", email.id)
                await self._bruin_repository.mark_email_as_done(email.id)
                if email.is_reply_email:
                    await self._bruin_repository.mark_email_as_done(email.parent.id)

            log.info("email_id=%s Removing email from Redis", email.id)
            self._new_tagged_emails_repository.mark_complete(email.id)
            if email.is_reply_email:
                self._new_tagged_emails_repository.remove_parent_email(email.parent)
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

    @staticmethod
    def _compose_bec_note_text(email: Email, is_update_note: bool = False) -> str:
        new_ticket_message = "This ticket was opened via MetTel Email Center AI Engine."
        update_ticket_message = "This note is new commentary from the client and posted via BEC AI engine."
        operator_message = update_ticket_message if is_update_note else new_ticket_message
        body_cleaned = html2text.html2text(email.body)

        return os.linesep.join(
            [
                "#*MetTel's IPA*#",
                "BEC AI RTA",
                "",
                operator_message,
                "Please review the full narrative provided in the email attached:\n" f"From: {email.sender_address}",
                f"Date Stamp: {email.date}",
                f"Subject: {email.subject}",
                f"Body: \n {body_cleaned}",
            ]
        )

    def _compose_bec_note_to_ticket(
        self,
        ticket_id: str,
        service_numbers: List[str],
        email: Email,
        is_update_note: bool = False,
    ) -> List[Dict]:
        note_text = self._compose_bec_note_text(email=email, is_update_note=is_update_note)
        notes = [{"text": note_text, "service_number": service_number} for service_number in service_numbers]
        log.info("ticket_id=%s Sending note: %s", ticket_id, notes)

        return notes

    async def _create_tickets(
        self,
        email: Email,
        service_number_site_map: Dict[str, str],
    ) -> CreateTicketsOutput:
        """
        Try to create tickets for valid service_number
        """
        # Return data
        create_tickets_output = CreateTicketsOutput()

        site_id_sn_buckets = defaultdict(list)
        for service_number, site_id in service_number_site_map.items():
            site_id_sn_buckets[site_id].append(service_number)

        for site_id, service_numbers in site_id_sn_buckets.items():
            asset_ids = [
                AssetId(client_id=email.client_id, site_id=site_id, service_number=service_number)
                for service_number in service_numbers
            ]

            try:
                result = await self._upsert_outage_ticket_rpc(asset_ids=asset_ids, contact_email=email.sender_address)
            except RpcError:
                log.exception(
                    "email_id=%s Error while creating ticket for %s and client %s",
                    email.id,
                    service_numbers,
                    email.client_id,
                )
                create_tickets_output.tickets_cannot_be_created.append(
                    TicketOutput(
                        site_id=str(site_id),
                        service_numbers=service_numbers,
                        reason="Error while creating bruin ticket",
                    )
                )
                continue

            if result.status == UpsertedStatus.created:
                log.info("email_id=%s Successfully created outage ticket %s", email.id, result.ticket_id)
                create_tickets_output.tickets_created.append(
                    TicketOutput(ticket_id=result.ticket_id, site_id=site_id, service_numbers=service_numbers)
                )

            elif result.status == UpsertedStatus.updated:
                log.info("email_id=%s Ticket already present", email.id)
                create_tickets_output.tickets_updated.append(
                    TicketOutput(
                        ticket_id=result.ticket_id,
                        site_id=str(site_id),
                        service_numbers=service_numbers,
                        reason="update_with_asset_found",
                    )
                )

            await self._post_process_upsert(email, result, service_numbers)
            if email.is_reply_email:
                await self._post_process_upsert(email.parent, result, service_numbers)

            try:
                await self._subscribe_user_rpc(ticket_id=result.ticket_id, user_email=email.sender_address)
            except RpcError:
                log.exception(f"email_id={email.id} Error while subscribing user to ticket {result.ticket_id}")

        return create_tickets_output

    async def _post_process_upsert(self, email: Email, ticket: UpsertedTicket, service_numbers: List[str]):
        notes_to_append = self._compose_bec_note_to_ticket(
            ticket_id=ticket.ticket_id,
            service_numbers=service_numbers,
            email=email,
            is_update_note=ticket.status == UpsertedStatus.updated,
        )

        await self._bruin_repository.append_notes_to_ticket(ticket.ticket_id, notes_to_append)
        await self._bruin_repository.link_email_to_ticket(ticket.ticket_id, email.id)

    def _get_potential_tickets(
        self,
        inference_data: Dict[str, Any],
        service_number_site_map: Dict[str, str],
        existing_tickets: List[Dict[str, Any]],
    ) -> PotentialTicketsOutput:
        """Get potential updated/created tickets"""
        output = PotentialTicketsOutput()
        predicted_class = inference_data["predicted_class"]
        site_ids = set(service_number_site_map.values())

        for ticket in existing_tickets:
            if self._should_update_ticket(ticket, site_ids, predicted_class):
                output.tickets_could_be_updated.append(
                    TicketOutput(
                        site_id=ticket["site_id"],
                        service_numbers=ticket["service_numbers"],
                        ticket_id=ticket["ticket_id"],
                    )
                )
                site_ids.remove(ticket["site_id"])

        for site_id in site_ids:
            service_numbers_filtered_by_site_id = [
                service_number
                for service_number, service_site_id in service_number_site_map.items()
                if service_site_id == site_id
            ]
            output.tickets_could_be_created.append(
                TicketOutput(
                    site_id=site_id,
                    service_numbers=service_numbers_filtered_by_site_id,
                )
            )

        return output

    @staticmethod
    def _get_class_other_tickets(service_number_site_map: Dict[str, str]) -> List[TicketOutput]:
        not_created_tickets = []
        site_ids = set(service_number_site_map.values())

        for site_id in site_ids:
            service_numbers_filtered_by_site_id = [
                service_number
                for service_number, service_site_id in service_number_site_map.items()
                if service_site_id == site_id
            ]
            not_created_tickets.append(
                TicketOutput(
                    site_id=site_id,
                    service_numbers=service_numbers_filtered_by_site_id,
                    reason="predicted class is Other",
                )
            )

        return not_created_tickets

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

    @staticmethod
    def _is_ticket_actionable(inference_data: Dict[str, Any]) -> bool:
        """Check if the inference can be used to create/update a ticket reference"""
        filtered = inference_data["filter_flags"]["is_filtered"]
        tagger_below_threshold = inference_data["filter_flags"]["tagger_is_below_threshold"]

        return not any(
            [
                filtered,
                tagger_below_threshold,
            ]
        )

    async def _update_ticket(self, ticket: Ticket, email: Email) -> bool:
        note = self._compose_bec_note_text(email=email, is_update_note=True)

        try:
            note_appended = await self._append_note_to_ticket_rpc(ticket.id, note)
            if not note_appended:
                return False
        except RpcError as e:
            # TODO: send notification to slack
            log.error("email_id=%s append_note_to_ticket_rpc(%s, %s) => %s", email.id, ticket.id, note, e)
            return False

        response = await self._bruin_repository.link_email_to_ticket(ticket.id, email.id)
        if response.get("status") != 200:
            return False
        else:
            return True
