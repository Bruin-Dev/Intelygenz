import logging
import re
import time
from datetime import datetime
from typing import List, Optional

from application import ForwardQueues
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone

logger = logging.getLogger(__name__)

EMAIL_REGEXES = [
    {
        "type": "Possible Fraud",
        "subject": re.compile(r"Possible Fraud on .*"),
        "body": re.compile(r"(?P<email_body>Possible Fraud Warning.*)\n\nThanks,\nFraud Detection System", re.DOTALL),
        "did": re.compile(r"DID: (?P<did>.*)"),
    },
    {
        "type": "Request Rate Monitor Violation",
        "subject": re.compile(r"Request Rate Monitor Violation\(High\)"),
        "body": re.compile(r"Subject: (?P<email_body>.*)\n\nConfidentiality Notice", re.DOTALL),
        "did": re.compile(r"Destination Phone : (?P<did>.*)"),
    },
]


class FraudMonitor:
    def __init__(
        self,
        nats_client,
        scheduler,
        config,
        metrics_repository,
        notifications_repository,
        email_repository,
        bruin_repository,
        ticket_repository,
        utils_repository,
    ):
        self._nats_client = nats_client
        self._scheduler = scheduler
        self._config = config
        self._metrics_repository = metrics_repository
        self._notifications_repository = notifications_repository
        self._email_repository = email_repository
        self._bruin_repository = bruin_repository
        self._ticket_repository = ticket_repository
        self._utils_repository = utils_repository

    async def start_fraud_monitoring(self, exec_on_start=False):
        logger.info("Scheduling Fraud Monitor job...")
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz)
            logger.info("Fraud Monitor job is going to be executed immediately")

        try:
            self._scheduler.add_job(
                self._fraud_monitoring_process,
                "interval",
                minutes=self._config.FRAUD_CONFIG["monitoring_interval"],
                next_run_time=next_run_time,
                replace_existing=False,
                id="_fraud_monitor_process",
            )
        except ConflictingIdError as conflict:
            logger.info(f"Skipping start of Fraud Monitoring job. Reason: {conflict}")

    async def _fraud_monitoring_process(self):
        logger.info(f'Processing all unread email from {self._config.FRAUD_CONFIG["inbox_email"]}')
        start = time.time()
        unread_emails_response = await self._email_repository.get_unread_emails()
        unread_emails_body = unread_emails_response["body"]
        unread_emails_status = unread_emails_response["status"]

        if unread_emails_status not in range(200, 300):
            logger.warning(f"Bad status calling to get unread emails. Skipping fraud monitor process")
            return

        for email in unread_emails_body:
            message = email["message"]
            body = email["body"]
            msg_uid = email["msg_uid"]
            subject = email["subject"]

            email_regex = self._utils_repository.get_first_element_matching(
                EMAIL_REGEXES, lambda regex: regex["subject"].search(subject)
            )

            if message is None or msg_uid == -1:
                logger.error(f"Invalid message: {email}")
                continue

            if not email_regex:
                logger.info(f"Email with msg_uid {msg_uid} is not a fraud warning. Skipping...")
                continue

            if not email_regex["body"].search(body):
                logger.error(f"Email with msg_uid {msg_uid} has an unexpected body")
                continue

            logger.info(f"Processing email with msg_uid {msg_uid}")
            processed = await self._process_fraud(email_regex, body, msg_uid)

            if processed and self._config.CURRENT_ENVIRONMENT == "production":
                mark_email_as_read_response = await self._email_repository.mark_email_as_read(msg_uid)
                mark_email_as_read_status = mark_email_as_read_response["status"]

                if mark_email_as_read_status not in range(200, 300):
                    logger.error(f"Could not mark email with msg_uid {msg_uid} as read")

            if processed:
                logger.info(f"Processed email with msg_uid {msg_uid}")
            else:
                logger.info(f"Failed to process email with msg_uid {msg_uid}")

        stop = time.time()
        logger.info(
            f'Finished processing all unread email from {self._config.FRAUD_CONFIG["inbox_email"]}. '
            f"Elapsed time: {round((stop - start) / 60, 2)} minutes"
        )

    async def _process_fraud(self, email_regex: dict, email_body: str, msg_uid: str) -> bool:
        did = email_regex["did"].search(email_body).group("did")
        email_body = email_regex["body"].search(email_body).group("email_body")

        client_info_by_did_response = await self._bruin_repository.get_client_info_by_did(did)
        if client_info_by_did_response["status"] in range(200, 300):
            client_id = client_info_by_did_response["body"]["clientId"]
            service_number = client_info_by_did_response["body"]["btn"]
        else:
            logger.warning(f"Failed to get client info by DID {did}, using default client info")
            default_client_info = self._config.FRAUD_CONFIG["default_client_info"]
            client_id = default_client_info["client_id"]
            service_number = default_client_info["service_number"]

        open_fraud_tickets_response = await self._bruin_repository.get_open_fraud_tickets(client_id, service_number)
        if open_fraud_tickets_response["status"] not in range(200, 300):
            logger.warning(
                f"Bad status calling to get open fraud tickets for client id: {client_id} and "
                f"service number: {service_number}. Process fraud FALSE ..."
            )
            return False

        # Get oldest open ticket related to Fraud Monitor
        open_fraud_tickets = open_fraud_tickets_response["body"]
        open_fraud_ticket = await self._get_oldest_fraud_ticket(open_fraud_tickets, service_number)

        if open_fraud_ticket:
            ticket_id = open_fraud_ticket["ticket_overview"]["ticketID"]
            logger.info(f"An open Fraud ticket was found for {service_number}. Ticket ID: {ticket_id}")

            # The task can be in Resolved state, even if the ticket is reported as Open by Bruin.
            # If that's the case, the task should be re-opened instead.
            if self._ticket_repository.is_task_resolved(open_fraud_ticket["ticket_task"]):
                logger.info(
                    f"Fraud ticket with ID {ticket_id} is open, but the task related to {service_number} is resolved. "
                    f"Therefore, the ticket will be considered as Resolved."
                )
                resolved_fraud_ticket = {**open_fraud_ticket}
            else:
                return await self._append_note_to_ticket(open_fraud_ticket, service_number, email_body, msg_uid)
        else:
            # If we didn't find an Open ticket, we need look for a Resolved ticket
            logger.info(f"No open Fraud ticket was found for {service_number}")
            resolved_fraud_tickets_response = await self._bruin_repository.get_resolved_fraud_tickets(
                client_id, service_number
            )
            if resolved_fraud_tickets_response["status"] not in range(200, 300):
                logger.warning(
                    f"bad status calling to get resolved fraud tickets for client id: {client_id} "
                    f"and service number: {service_number}. Skipping process fraud ..."
                )
                return False

            resolved_fraud_tickets = resolved_fraud_tickets_response["body"]
            resolved_fraud_ticket = await self._get_oldest_fraud_ticket(resolved_fraud_tickets, service_number)

        # If the Open ticket flow or the Resolved ticket flow returned a Resolved ticket task, we need to unresolve it
        if resolved_fraud_ticket:
            ticket_id = resolved_fraud_ticket["ticket_overview"]["ticketID"]
            logger.info(f"A resolved Fraud ticket was found for {service_number}. Ticket ID: {ticket_id}")
            return await self._unresolve_task_for_ticket(
                resolved_fraud_ticket, service_number, email_regex, email_body, msg_uid
            )

        # If not a single ticket was found, create a new one
        logger.info(f"No open or resolved Fraud ticket was found for {service_number}")
        return await self._create_fraud_ticket(client_id, service_number, email_regex, email_body, msg_uid)

    async def _get_oldest_fraud_ticket(self, tickets: List[dict], service_number: str) -> Optional[dict]:
        tickets = sorted(tickets, key=lambda item: parse(item["createDate"]))

        for ticket in tickets:
            ticket_id = ticket["ticketID"]
            ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)

            if ticket_details_response["status"] not in range(200, 300):
                logger.warning(
                    f"Bad status calling to get ticket details for ticket id: {ticket_id}."
                    f"Skipping get oldest fraud ticket ..."
                )
                return

            ticket_notes = ticket_details_response["body"]["ticketNotes"]
            relevant_notes = [
                note
                for note in ticket_notes
                if note["serviceNumber"] is not None
                if service_number in note["serviceNumber"]
                if note["noteValue"] is not None
            ]

            if not self._ticket_repository.is_fraud_ticket(relevant_notes):
                continue

            ticket_tasks = ticket_details_response["body"]["ticketDetails"]
            relevant_task = self._ticket_repository.find_task(ticket_tasks, service_number)

            return {
                "ticket_overview": ticket,
                "ticket_task": relevant_task,
                "ticket_notes": relevant_notes,
            }

    async def _append_note_to_ticket(
        self, ticket_info: dict, service_number: str, email_body: str, msg_uid: str
    ) -> bool:
        ticket_id = ticket_info["ticket_overview"]["ticketID"]
        logger.info(f"Appending Fraud note to ticket {ticket_id}")

        # Get notes since latest re-open or ticket creation
        latest_notes = self._ticket_repository.get_latest_notes(ticket_info["ticket_notes"])

        # If there is a Fraud note for the current email since the latest re-open note, skip
        # Otherwise, append Fraud note to ticket using the callback passed as parameter
        if self._ticket_repository.note_already_exists(latest_notes, msg_uid):
            logger.info(
                f"No Fraud trouble note will be appended to ticket {ticket_id}. "
                f"A note for this email was already appended to the ticket after the latest re-open or ticket creation."
            )
            return True

        if self._config.CURRENT_ENVIRONMENT != "production":
            logger.info(
                f"No Fraud note will be appended to ticket {ticket_id} since the current environment is not production"
            )
            return True

        append_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, service_number, email_body, msg_uid
        )
        if append_note_response["status"] not in range(200, 300):
            logger.warning(f"Bad status calling to append note to ticket id: {ticket_id}. Skipping append note ...")
            return False

        logger.info(f"Fraud note was successfully appended to ticket {ticket_id}!")
        await self._notifications_repository.notify_successful_note_append(ticket_id, service_number)

        return True

    async def _unresolve_task_for_ticket(
        self, ticket_info: dict, service_number: str, email_regex: dict, email_body: str, msg_uid: str
    ) -> bool:
        ticket_id = ticket_info["ticket_overview"]["ticketID"]
        task_id = ticket_info["ticket_task"]["detailID"]
        logger.info(f"Unresolving task related to {service_number} of Fraud ticket {ticket_id}...")

        if self._config.CURRENT_ENVIRONMENT != "production":
            logger.info(
                f"Task related to {service_number} of Fraud ticket {ticket_id} will not be unresolved "
                f"since the current environment is not production"
            )
            return True

        unresolve_task_response = await self._bruin_repository.open_ticket(ticket_id, task_id)
        if unresolve_task_response["status"] not in range(200, 300):
            logger.warning(
                f"Bad status calling to open ticket with ticket id: {ticket_id}. "
                f"Unresolve task for ticket return FALSE"
            )
            return False

        logger.info(f"Task related to {service_number} of Fraud ticket {ticket_id} was successfully unresolved!")
        self._metrics_repository.increment_tasks_reopened(trouble=email_regex["type"])
        await self._notifications_repository.notify_successful_reopen(ticket_id, service_number)

        append_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, service_number, email_body, msg_uid, reopening=True
        )
        if append_note_response["status"] not in range(200, 300):
            logger.warning(
                f"Bad status calling to append note to ticket id: {ticket_id} and service number:"
                f"{service_number}. Unresolve task for ticket return FALSE"
            )
            return False

        logger.info(f"Fraud note was successfully appended to ticket {ticket_id}!")
        await self._notifications_repository.notify_successful_note_append(ticket_id, service_number)

        return True

    async def _create_fraud_ticket(
        self, client_id: int, service_number: str, email_regex: dict, email_body: str, msg_uid: str
    ) -> bool:
        logger.info(f"Creating Fraud ticket for client {client_id} and service number {service_number}")
        contacts = await self._get_contacts(client_id, service_number)

        if not contacts:
            logger.warning(f"Not found contacts to create the fraud ticket")
            return False

        if self._config.CURRENT_ENVIRONMENT != "production":
            logger.info(f"No Fraud ticket will be created since the current environment is not production")
            return True

        create_fraud_ticket_response = await self._bruin_repository.create_fraud_ticket(
            client_id, service_number, contacts
        )
        if create_fraud_ticket_response["status"] not in range(200, 300):
            logger.warning(
                f"Bad status calling to create fraud ticket with client id: {client_id} and"
                f"service number: {service_number}. Create fraud ticket return FALSE ..."
            )
            return False

        ticket_id = create_fraud_ticket_response["body"]["ticketIds"][0]
        logger.info(f"Fraud ticket was successfully created! Ticket ID is {ticket_id}")
        self._metrics_repository.increment_tasks_created(trouble=email_regex["type"])
        await self._notifications_repository.notify_successful_ticket_creation(ticket_id, service_number)

        append_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, service_number, email_body, msg_uid
        )
        if append_note_response["status"] not in range(200, 300):
            logger.warning(
                f"Bad status calling to append note to ticket id: {ticket_id} and service number:"
                f"{service_number}. Create fraud ticket return FALSE ..."
            )
            return False

        logger.info(f"Fraud note was successfully appended to ticket {ticket_id}!")
        await self._notifications_repository.notify_successful_note_append(ticket_id, service_number)

        logger.info(f"Forwarding ticket {ticket_id} to HNOC")
        change_work_queue_response = await self._bruin_repository.change_detail_work_queue_to_hnoc(
            ticket_id=ticket_id, service_number=service_number
        )

        if change_work_queue_response["status"] in range(200, 300):
            self._metrics_repository.increment_tasks_forwarded(
                trouble=email_regex["type"], target_queue=ForwardQueues.HNOC.value
            )
            await self._notifications_repository.notify_successful_ticket_forward(ticket_id, service_number)

        return True

    async def _get_contacts(self, client_id: int, service_number: str):
        default_contacts = self._bruin_repository.get_contacts(self._config.FRAUD_CONFIG["default_contact"])

        client_info_response = await self._bruin_repository.get_client_info(service_number)
        if client_info_response["status"] not in range(200, 300) or not client_info_response["body"]:
            logger.warning(f"Failed to get client info for service number {service_number}, using default contacts")
            return default_contacts

        site_id = client_info_response["body"][0]["site_id"]
        site_details_response = await self._bruin_repository.get_site_details(client_id, site_id)
        if site_details_response["status"] not in range(200, 300):
            logger.warning(
                f"Failed to get site details for client {client_id} and site {site_id}, using default contacts"
            )
            return default_contacts

        site_details = site_details_response["body"]
        contact_info = self._bruin_repository.get_contact_info(site_details)
        contacts = self._bruin_repository.get_contacts(contact_info)

        return contacts or default_contacts
