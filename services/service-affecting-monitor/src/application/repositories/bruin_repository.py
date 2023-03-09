import asyncio
import itertools
import json
import logging
import os
import re
from collections import defaultdict
from datetime import datetime
from typing import Any
from copy import deepcopy

from application import AffectingTroubles, ForwardQueues
from application.repositories import nats_error_response
from dateutil.parser import parse
from pytz import timezone
from shortuuid import uuid
from tenacity import retry, stop_after_attempt, wait_fixed

INTERFACE_NOTE_REGEX = re.compile(r"Interface: (?P<interface_name>[a-zA-Z0-9]+)")
logger = logging.getLogger(__name__)


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


def get_data_from_response_message(message):
    return json.loads(message.data)


class BruinRepository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
        self._config = config
        self._notifications_repository = notifications_repository
        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_REPORT_CONFIG["semaphore"])

    async def get_tickets(
        self, client_id: int, ticket_topic: str, ticket_statuses: list, *, service_number: str = None
    ):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "client_id": client_id,
                "ticket_statuses": ticket_statuses,
                "ticket_topic": ticket_topic,
                "product_category": self._config.PRODUCT_CATEGORY,
            },
        }

        if service_number:
            request["body"]["service_number"] = service_number

        try:
            if not service_number:
                logger.info(
                    f"Getting all tickets with any status of {ticket_statuses}, with ticket topic "
                    f"{ticket_topic} and belonging to client {client_id} from Bruin..."
                )
            else:
                logger.info(
                    f"Getting all tickets with any status of {ticket_statuses}, with ticket topic "
                    f"{ticket_topic}, service number {service_number} and belonging to client {client_id} from Bruin..."
                )

            response = get_data_from_response_message(
                await self._nats_client.request("bruin.ticket.basic.request", to_json_bytes(request), timeout=150)
            )
        except Exception as e:
            err_msg = (
                f"An error occurred when requesting tickets from Bruin API with any status of {ticket_statuses}, "
                f"with ticket topic {ticket_topic} and belonging to client {client_id} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                if not service_number:
                    logger.info(
                        f"Got all tickets with any status of {ticket_statuses}, with ticket topic "
                        f"{ticket_topic} and belonging to client {client_id} from Bruin!"
                    )
                else:
                    logger.info(
                        f"Got all tickets with any status of {ticket_statuses}, with ticket topic "
                        f"{ticket_topic}, service number {service_number} and belonging to client "
                        f"{client_id} from Bruin!"
                    )
            else:
                if not service_number:
                    err_msg = (
                        f"Error while retrieving tickets with any status of {ticket_statuses}, with ticket topic "
                        f"{ticket_topic} and belonging to client {client_id} in "
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )
                else:
                    err_msg = (
                        f"Error while retrieving tickets with any status of {ticket_statuses}, with ticket topic "
                        f"{ticket_topic}, service number {service_number} and belonging to client {client_id} in "
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_ticket_details(self, ticket_id: int):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {"ticket_id": ticket_id},
        }

        try:
            logger.info(f"Getting details of ticket {ticket_id} from Bruin...")
            response = get_data_from_response_message(
                await self._nats_client.request("bruin.ticket.details.request", to_json_bytes(request), timeout=75)
            )
        except Exception as e:
            err_msg = f"An error occurred when requesting ticket details from Bruin API for ticket {ticket_id} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while retrieving details of ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )
            else:
                logger.info(f"Got details of ticket {ticket_id} from Bruin!")

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)
        return response

    async def append_note_to_ticket(self, ticket_id: int, note: str, *, service_numbers: list = None):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "ticket_id": ticket_id,
                "note": note,
            },
        }

        if service_numbers:
            request["body"]["service_numbers"] = service_numbers

        try:
            logger.info(f"Appending note to ticket {ticket_id}... Note contents: {note}")
            response = get_data_from_response_message(
                await self._nats_client.request("bruin.ticket.note.append.request", to_json_bytes(request), timeout=75)
            )
            logger.info(f"Note appended to ticket {ticket_id}!")
        except Exception as e:
            err_msg = (
                f"An error occurred when appending a ticket note to ticket {ticket_id}. "
                f"Ticket note: {note}. Error: {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while appending note to ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. Note was {note}. Error: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def unpause_ticket_detail(self, ticket_id: int, service_number: str):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "ticket_id": ticket_id,
                "service_number": service_number,
            },
        }

        try:
            logger.info(f"Unpausing detail of ticket {ticket_id} related to serial number {service_number}...")
            response = get_data_from_response_message(
                await self._nats_client.request("bruin.ticket.unpause", to_json_bytes(request), timeout=90)
            )
        except Exception as e:
            err_msg = (
                f"An error occurred when unpausing detail of ticket {ticket_id} related to serial number "
                f"{service_number}. Error: {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(f"Detail of ticket {ticket_id} related to serial number {service_number}) was unpaused!")
            else:
                err_msg = (
                    f"Error while unpausing detail of ticket {ticket_id} related to serial number {service_number}) in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. "
                    f"Error: Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def create_affecting_ticket(self, client_id: int, service_number: str, contact_info: list):
        err_msg = None
        ticket_details = {
            "request_id": uuid(),
            "body": {
                "clientId": client_id,
                "category": "VAS",
                "services": [{"serviceNumber": service_number}],
                "contacts": contact_info,
            },
        }

        try:
            logger.info(f"Creating affecting ticket for serial {service_number} belonging to client {client_id}...")

            response = get_data_from_response_message(
                await self._nats_client.request(
                    "bruin.ticket.creation.request", to_json_bytes(ticket_details), timeout=150
                )
            )

        except Exception as e:
            err_msg = (
                f"An error occurred while creating affecting ticket for client id {client_id} and serial "
                f"{service_number} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(
                    f"Affecting ticket for client {client_id} and serial {service_number} created successfully!"
                )
            else:
                err_msg = (
                    f"Error while opening affecting ticket for client {client_id} and serial {service_number} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def subscribe_user_to_ticket(self, ticket_id, subscriber):
        err_msg = None
        request_details = {
            "request_id": uuid(),
            "body": {
                "subscriptionType": "2",
                "user": {
                    "email": subscriber
                }
            },
        }

        try:
            logger.info(f"Subscribing user {subscriber} to ticket {ticket_id}...")

            response = get_data_from_response_message(
                await self._nats_client.request(
                    "bruin.subscribe.user", to_json_bytes(request_details), timeout=150
                )
            )

        except Exception as e:
            err_msg = f"An error occurred while subscribing user {subscriber} to ticket {ticket_id} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(
                    f"Subscriber {subscriber} subscribed successfully to ticket {ticket_id}!"
                )
            else:
                err_msg = (
                    f"Error while subscribing user {subscriber} to ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def open_ticket(self, ticket_id: int, detail_id: int):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }

        try:
            logger.info(f"Opening ticket {ticket_id} (affected detail ID: {detail_id})...")
            response = get_data_from_response_message(
                await self._nats_client.request("bruin.ticket.status.open", to_json_bytes(request), timeout=75)
            )
            logger.info(f"Ticket {ticket_id} opened!")
        except Exception as e:
            err_msg = f"An error occurred when opening outage ticket {ticket_id} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while opening outage ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def change_detail_work_queue(
        self, ticket_id: int, task_result: str, *, service_number: str = None, detail_id: int = None
    ):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {"ticket_id": ticket_id, "queue_name": task_result},
        }

        if service_number:
            request["body"]["service_number"] = service_number

        if detail_id:
            request["body"]["detail_id"] = detail_id

        try:
            logger.info(
                f"Changing task result of detail {detail_id} / serial {service_number} in ticket {ticket_id} "
                f"to {task_result}..."
            )
            response = get_data_from_response_message(
                await self._nats_client.request("bruin.ticket.change.work", to_json_bytes(request), timeout=150)
            )
        except Exception as e:
            err_msg = (
                f"An error occurred when changing task result of detail {detail_id} / serial {service_number} "
                f"in ticket {ticket_id} to {task_result} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(
                    f"Task result of detail {detail_id} / serial {service_number} in ticket {ticket_id} "
                    f"changed to {task_result} successfully!"
                )
            else:
                err_msg = (
                    f"Error while changing task result of detail {detail_id} / serial {service_number} in ticket "
                    f"{ticket_id} to {task_result} in {self._config.ENVIRONMENT_NAME.upper()} "
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def resolve_ticket(self, ticket_id: int, detail_id: int):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }

        try:
            logger.info(f"Resolving detail {detail_id} of ticket {ticket_id}...")
            response = get_data_from_response_message(
                await self._nats_client.request("bruin.ticket.status.resolve", to_json_bytes(request), timeout=75)
            )
        except Exception as e:
            err_msg = f"An error occurred while resolving detail {detail_id} of ticket {ticket_id} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(f"Detail {detail_id} of ticket {ticket_id} resolved successfully!")
            else:
                err_msg = (
                    f"Error while resolving detail {detail_id} of ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def send_initial_email_milestone_notification(self, ticket_id: int, service_number: str) -> dict:
        notification_type = "TicketBYOBAffectingRepairAcknowledgement-E-Mail"
        return await self.post_notification_email_milestone(ticket_id, service_number, notification_type)

    async def send_reminder_email_milestone_notification(self, ticket_id: int, service_number: str) -> dict:
        notification_type = "TicketBYOBAffectingRepairReminder-E-Mail"
        return await self.post_notification_email_milestone(ticket_id, service_number, notification_type)

    async def post_notification_email_milestone(self, ticket_id: int, service_number: str, notification_type: str):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "notification_type": notification_type,
                "ticket_id": ticket_id,
                "service_number": service_number,
            },
        }

        try:
            logger.info(
                f"Sending email for ticket id {ticket_id}, "
                f"service_number {service_number} "
                f"and notification type {notification_type}..."
            )
            response = get_data_from_response_message(
                await self._nats_client.request(
                    "bruin.notification.email.milestone", to_json_bytes(request), timeout=150
                )
            )
        except Exception as e:
            err_msg = (
                f"An error occurred when sending email for ticket id {ticket_id}, "
                f"service_number {service_number} "
                f"and notification type {notification_type}...-> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(
                    f"Email sent for ticket {ticket_id}, service number {service_number} "
                    f"and notification type {notification_type}!"
                )
            else:
                err_msg = (
                    f"Error while sending email for ticket {ticket_id}, "
                    f"service_number {service_number} and notification type {notification_type} in "
                    f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    @staticmethod
    def get_contact_info_for_site(site_details):
        site_detail_name = site_details["primaryContactName"]
        site_detail_phone = site_details["primaryContactPhone"]
        site_detail_email = site_details["primaryContactEmail"]

        if site_detail_name is None or site_detail_email is None:
            return None

        contact_info = [
            {
                "email": site_detail_email,
                "name": site_detail_name,
                "type": "ticket",
            },
            {
                "email": site_detail_email,
                "name": site_detail_name,
                "type": "site",
            },
        ]

        if site_detail_phone is not None:
            contact_info[0]["phone"] = site_detail_phone
            contact_info[1]["phone"] = site_detail_phone

        return contact_info

    @staticmethod
    def get_contact_info_for_ticket(ticket_contact_details):
        ticket_contact_detail_first_name = ticket_contact_details["firstName"]
        ticket_contact_detail_last_name = ticket_contact_details["lastName"]
        ticket_contact_detail_email = ticket_contact_details["email"]

        if (ticket_contact_detail_first_name is None
            or ticket_contact_detail_last_name is None
                or ticket_contact_detail_email is None):
            return None

        full_name = ticket_contact_detail_first_name + " " + ticket_contact_detail_last_name

        contact_info = [
            {
                "email": ticket_contact_detail_email,
                "name": full_name,
                "type": "ticket",
            },
            {
                "email": ticket_contact_detail_email,
                "name": full_name,
                "type": "site",
            },
        ]

        if "phone" in ticket_contact_details and ticket_contact_details["phone"] is not None:
            contact_info[0]["phone"] = ticket_contact_details["phone"]
            contact_info[1]["phone"] = ticket_contact_details["phone"]

        return contact_info

    @staticmethod
    def _get_ticket_contact_from_ticket_contact_details(ticket_contact_details):
        ticket_contact_detail_first_name = ticket_contact_details["firstName"]
        ticket_contact_detail_last_name = ticket_contact_details["lastName"]
        ticket_contact_detail_email = ticket_contact_details["email"]

        if (ticket_contact_detail_first_name is None
            or ticket_contact_detail_last_name is None
                or ticket_contact_detail_email is None):
            return None

        full_name = ticket_contact_detail_first_name + " " + ticket_contact_detail_last_name

        ticket_contact = {
            "email": ticket_contact_detail_email,
            "name": full_name,
            "type": "ticket",
        }

        if "phone" in ticket_contact_details and ticket_contact_details["phone"] is not None:
            ticket_contact["phone"] = ticket_contact_details["phone"]

        return ticket_contact

    @staticmethod
    def _get_site_contact_from_site_details(site_details):
        site_detail_name = site_details["primaryContactName"]
        site_detail_phone = site_details["primaryContactPhone"]
        site_detail_email = site_details["primaryContactEmail"]

        if site_detail_name is None or site_detail_email is None:
            return None

        site_contact = {
            "email": site_detail_email,
            "name": site_detail_name,
            "type": "site",
        }

        if site_detail_phone:
            site_contact["phone"] = site_detail_phone

        return site_contact

    @staticmethod
    def get_contact_info_from_site_and_ticket_contact_details(site_details, ticket_contact_details):
        site_contact = BruinRepository._get_site_contact_from_site_details(site_details)
        ticket_contact = BruinRepository._get_ticket_contact_from_ticket_contact_details(ticket_contact_details)

        if site_contact is None and ticket_contact is None:
            return None

        if site_contact is None:
            site_contact = deepcopy(ticket_contact)
            site_contact["type"] = "site"

        if ticket_contact is None:
            ticket_contact = deepcopy(site_contact)
            ticket_contact["type"] = "ticket"

        return [site_contact, ticket_contact]

    @staticmethod
    def get_ticket_contact_additional_subscribers(ticket_contact_additional_subscribers):
        subscribers = []

        for subscriber in ticket_contact_additional_subscribers:
            if subscriber["email"]:
                subscribers.append(subscriber["email"])

        return subscribers

    async def get_affecting_tickets(self, client_id: int, ticket_statuses: list, *, service_number: str = None):
        ticket_topic = "VAS"

        return await self.get_tickets(client_id, ticket_topic, ticket_statuses, service_number=service_number)

    async def get_open_affecting_tickets(self, client_id: int, *, service_number: str = None):
        ticket_statuses = ["New", "InProgress", "Draft"]

        return await self.get_affecting_tickets(client_id, ticket_statuses, service_number=service_number)

    async def get_resolved_affecting_tickets(self, client_id: int, *, service_number: str = None):
        ticket_statuses = ["Resolved"]

        return await self.get_affecting_tickets(client_id, ticket_statuses, service_number=service_number)

    async def append_autoresolve_note_to_ticket(self, ticket_id: int, serial_number: str):
        all_troubles = list(AffectingTroubles)
        troubles_joint = f"{', '.join(trouble.value for trouble in all_troubles[:-1])} and {all_troubles[-1].value}"

        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))
        autoresolve_note = os.linesep.join(
            [
                "#*MetTel's IPA*#",
                f"All Service Affecting conditions ({troubles_joint}) have stabilized.",
                f"Auto-resolving task for serial: {serial_number}",
                f"TimeStamp: {current_datetime_tz_aware}",
            ]
        )

        return await self.append_note_to_ticket(ticket_id, autoresolve_note, service_numbers=[serial_number])

    # ------------------------ Legacy methods for SA reports ------------------------
    async def _get_ticket_details(self, ticket):
        @retry(
            wait=wait_fixed(self._config.MONITOR_REPORT_CONFIG["wait_fixed"]),
            stop=stop_after_attempt(self._config.MONITOR_REPORT_CONFIG["stop_after_attempt"]),
            reraise=True,
        )
        async def _get_ticket_details():
            async with self._semaphore:
                ticket_id = ticket["ticketID"]
                ticket_details = await self.get_ticket_details(ticket_id)
                if ticket_details["status"] in [401, 403]:
                    logger.exception(f"Error: Retry after few seconds. Status: {ticket_details['status']}")
                    raise Exception(f"Error: Retry after few seconds. Status: {ticket_details['status']}")

                if ticket_details["status"] not in range(200, 300):
                    logger.error(f"Error: an error occurred retrieving ticket details for ticket: {ticket_id}")
                    return None

                ticket_details_body = ticket_details["body"]
                logger.info(f"Returning ticket details of ticket: {ticket_id}")
                return {"ticket": ticket, "ticket_details": ticket_details_body}

        try:
            return await _get_ticket_details()
        except Exception as e:
            msg = (
                f"[service-affecting-monitor-reports]"
                f"Max retries reached getting ticket details {ticket['ticketID']}"
            )
            logger.error(msg)
            await self._notifications_repository.send_slack_message(msg)
            return None

    async def get_all_affecting_tickets(
        self, client_id=None, serial=None, start_date=None, end_date=None, ticket_statuses=None
    ):
        @retry(
            wait=wait_fixed(self._config.MONITOR_REPORT_CONFIG["wait_fixed"]),
            stop=stop_after_attempt(self._config.MONITOR_REPORT_CONFIG["stop_after_attempt"]),
            reraise=True,
        )
        async def _get_all_affecting_tickets():
            ticket_request_msg = {
                "request_id": uuid(),
                "body": {
                    "client_id": client_id,
                    "category": self._config.PRODUCT_CATEGORY,
                    "ticket_topic": "VAS",
                    "ticket_status": ticket_statuses,
                },
            }
            if start_date:
                ticket_request_msg["body"]["start_date"] = start_date
            if end_date:
                ticket_request_msg["body"]["end_date"] = end_date
            if serial:
                ticket_request_msg["body"]["service_number"] = serial

            response_all_tickets = get_data_from_response_message(
                await self._nats_client.request("bruin.ticket.request", to_json_bytes(ticket_request_msg), timeout=150)
            )

            if response_all_tickets["status"] in [401, 403]:
                logger.exception(
                    f"Error: Retry after few seconds all tickets. Status: {response_all_tickets['status']}"
                )
                raise Exception(f"Error: Retry after few seconds all tickets. Status: {response_all_tickets['status']}")

            if response_all_tickets["status"] not in range(200, 300):
                logger.error(f"Error: an error occurred retrieving affecting tickets: {response_all_tickets}")
                return None
            return response_all_tickets

        try:
            return await _get_all_affecting_tickets()
        except Exception as e:
            msg = f"Max retries reached getting all tickets for the service affecting monitor process."
            logger.error(f"{msg} - exception: {e}")
            await self._notifications_repository.send_slack_message(msg)
            return None

    async def get_affecting_ticket_for_report(self, client_id, start_date, end_date):
        @retry(
            wait=wait_fixed(self._config.MONITOR_REPORT_CONFIG["wait_fixed"]),
            stop=stop_after_attempt(self._config.MONITOR_REPORT_CONFIG["stop_after_attempt"]),
            reraise=True,
        )
        async def get_affecting_ticket_for_report():

            logger.info(f"Retrieving affecting tickets between start date: {start_date} and end date: {end_date}")

            response = await self.get_all_affecting_tickets(
                client_id=client_id,
                start_date=start_date,
                end_date=end_date,
                ticket_statuses=["New", "InProgress", "Draft", "Resolved", "Closed"],
            )

            if not response:
                logger.error("An error occurred while fetching Service Affecting tickets for reports")
                return None

            logger.info(f"Getting ticket details for {len(response['body'])} tickets")
            all_tickets_sorted = sorted(response["body"], key=lambda item: parse(item["createDate"]), reverse=True)
            tasks = [self._get_ticket_details(ticket) for ticket in all_tickets_sorted]
            tickets = await asyncio.gather(*tasks, return_exceptions=True)
            tickets = {ticket["ticket"]["ticketID"]: ticket for ticket in tickets if ticket}

            return tickets

        try:
            return await get_affecting_ticket_for_report()
        except Exception as e:
            msg = f"[service-affecting-monitor-reports] Max retries reached getting all tickets for the report."
            logger.error(f"{msg} - exception: {e}")
            await self._notifications_repository.send_slack_message(msg)
            return None

    def group_ticket_details_by_serial(self, tickets):
        all_serials = defaultdict(list)

        for detail_object in tickets:
            serial = detail_object["ticket_detail"]["detailValue"].upper()
            all_serials[serial].append(detail_object)

        return all_serials

    @staticmethod
    def group_ticket_details_by_serial_and_interface(ticket_details):
        grouped_tickets = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        for detail in ticket_details:
            serial = detail["ticket_detail"]["detailValue"]

            for note in detail["ticket_notes"]:
                match = INTERFACE_NOTE_REGEX.search(note["noteValue"])

                if match:
                    interface = match["interface_name"]
                    if "Transfer" in note["noteValue"]:
                        grouped_tickets[serial][interface]["bandwidth_up_exceeded"].append(detail)
                    elif "Receive" in note["noteValue"]:
                        grouped_tickets[serial][interface]["bandwidth_down_exceeded"].append(detail)

        return grouped_tickets

    @staticmethod
    def search_interfaces_and_count_in_details(ticket_details):
        interfaces_by_trouble = dict()
        for detail_object in ticket_details:
            for note in detail_object["ticket_notes"]:
                interface = INTERFACE_NOTE_REGEX.search(note["noteValue"])
                if interface:
                    trouble = detail_object["trouble_value"]
                    interface_name = interface["interface_name"]
                    interfaces_by_trouble.setdefault(trouble, {})
                    interfaces_by_trouble[trouble].setdefault(interface_name, set())
                    interfaces_by_trouble[trouble][interface_name].add(detail_object["ticket_id"])
        return interfaces_by_trouble

    @staticmethod
    def transform_tickets_into_ticket_details(tickets: dict) -> list:
        result = []
        for ticket_id, ticket_details in tickets.items():
            details = ticket_details["ticket_details"]["ticketDetails"]
            notes = ticket_details["ticket_details"]["ticketNotes"]
            ticket = ticket_details["ticket"]
            for detail in details:
                serial_number = detail["detailValue"]
                notes_related_to_serial = [
                    note
                    for note in notes
                    if note["serviceNumber"] is not None
                    if serial_number in note["serviceNumber"]
                ]
                result.append(
                    {
                        "ticket_id": ticket_id,
                        "ticket": ticket,
                        "ticket_detail": detail,
                        "ticket_notes": notes_related_to_serial,
                    }
                )
        return result

    def prepare_items_for_monitor_report(self, ticket_details_by_serial, cached_names_by_serial):
        items_for_report = []
        for serial, ticket_details in ticket_details_by_serial.items():
            interfaces_by_trouble = self.search_interfaces_and_count_in_details(ticket_details)
            for trouble in interfaces_by_trouble.keys():
                for interface, ticket_ids in interfaces_by_trouble[trouble].items():
                    logger.info(f"--> {serial} : {len(ticket_details)} tickets")
                    item_report = self.build_monitor_report_item(
                        ticket_details=ticket_details,
                        serial_number=serial,
                        edge_name=cached_names_by_serial[serial],
                        number_of_tickets=len(ticket_ids),
                        interface=interface,
                        trouble=trouble,
                    )
                    items_for_report.append(item_report)

        return items_for_report

    @staticmethod
    def build_monitor_report_item(ticket_details, edge_name, serial_number, number_of_tickets, interface, trouble):
        return {
            "customer": {
                "client_id": ticket_details[0]["ticket"]["clientID"],
                "client_name": ticket_details[0]["ticket"]["clientName"],
            },
            "location": ticket_details[0]["ticket"]["address"],
            "edge_name": edge_name,
            "serial_number": serial_number,
            "number_of_tickets": number_of_tickets,
            "bruin_tickets_id": set(detail_object["ticket_id"] for detail_object in ticket_details),
            "interfaces": interface,
            "trouble": trouble,
        }

    def prepare_items_for_bandwidth_report(self, links_metrics, grouped_ticket_details,
                                           enterprise_id_edge_id_relation, serial_numbers):
        logger.info(f"[bandwidth-reports] Preparing items for bandwidth report")
        report_items = []
        for link_metrics in links_metrics:
            serial_number = link_metrics["serial_number"]
            if serial_number not in serial_numbers:
                continue

            interface = link_metrics["interface"]
            enterprise_info = [
                {
                    "id" : edge["enterprise_id"],
                    "name": edge["enterprise_name"]
                }
                for edge in enterprise_id_edge_id_relation
                if edge["serial_number"] == serial_number][0]
            report_item = self.build_bandwidth_report_item(
                enterprise_id=enterprise_info["id"],
                enterprise_name=enterprise_info["name"],
                serial_number=serial_number,
                edge_name=link_metrics["edge_name"],
                interface=interface,
                ticket_details_up=grouped_ticket_details[serial_number][interface]["bandwidth_up_exceeded"],
                ticket_details_down=grouped_ticket_details[serial_number][interface]["bandwidth_down_exceeded"],
                down_Mbps_total_min=link_metrics["down_Mbps_total_min"],
                down_Mbps_total_max=link_metrics["down_Mbps_total_max"],
                up_Mbps_total_min=link_metrics["up_Mbps_total_min"],
                up_Mbps_total_max=link_metrics["up_Mbps_total_max"],
                peak_Mbps_down=link_metrics["peak_Mbps_down"],
                peak_Mbps_up=link_metrics["peak_Mbps_up"],
                peak_percent_down=link_metrics["peak_percent_down"],
                peak_percent_up=link_metrics["peak_percent_up"],
                peak_time_down=link_metrics["peak_time_down"],
                peak_time_up=link_metrics["peak_time_up"],
                link_name=link_metrics["link_name"],
            )
            report_items.append(report_item)

        return report_items

    @staticmethod
    def build_bandwidth_report_item(
        enterprise_id,
        enterprise_name,
        serial_number,
        edge_name,
        interface,
        ticket_details_up,
        ticket_details_down,
        down_Mbps_total_min,
        down_Mbps_total_max,
        up_Mbps_total_min,
        up_Mbps_total_max,
        peak_Mbps_down,
        peak_Mbps_up,
        peak_percent_down,
        peak_percent_up,
        peak_time_down,
        peak_time_up,
        link_name,
    ):
        logger.info(f"[bandwidth-reports] Building bandwidth report item for edge {serial_number} and \
                      interface {interface}")
        return {
            "enterprise_id": enterprise_id,
            "enterprise_name": enterprise_name,
            "serial_number": serial_number,
            "edge_name": edge_name,
            "interface": interface,
            "link_name": link_name,
            "down_Mbps_total_min": down_Mbps_total_min,
            "down_Mbps_total_max": down_Mbps_total_max,
            "up_Mbps_total_min": up_Mbps_total_min,
            "up_Mbps_total_max": up_Mbps_total_max,
            "peak_Mbps_down": peak_Mbps_down,
            "peak_Mbps_up": peak_Mbps_up,
            "peak_percent_down": peak_percent_down,
            "peak_percent_up": peak_percent_up,
            "peak_time_down": peak_time_down,
            "peak_time_up": peak_time_up,
            "threshold_exceeded_up": len(ticket_details_up) if len(ticket_details_up) <= 288 else 288,
            "threshold_exceeded_down": len(ticket_details_down) if len(ticket_details_down) <= 288 else 288,
            "ticket_ids_up": set(itertools.islice(set(detail["ticket_id"] for detail in ticket_details_up), 288)),
            "ticket_ids_down": set(itertools.islice(set(detail["ticket_id"] for detail in ticket_details_down), 288)),
        }

    @staticmethod
    def filter_ticket_details_by_serials(ticket_details, cached_names_by_serial):
        return [
            detail_object
            for detail_object in ticket_details
            if detail_object["ticket_detail"]["detailValue"] in cached_names_by_serial
        ]

    @staticmethod
    def filter_trouble_notes_in_ticket_details(tickets_details, troubles):
        ret = []
        for detail_object in tickets_details:
            for trouble in troubles:
                trouble_notes = [
                    ticket_note
                    for ticket_note in detail_object["ticket_notes"]
                    if ticket_note["noteValue"]
                    if (
                        "#*Automation Engine*#" in ticket_note["noteValue"]
                        or "#*MetTel's IPA*#" in ticket_note["noteValue"]
                    )
                    if f"Trouble: {trouble}" in ticket_note["noteValue"]
                ]

                if trouble_notes:
                    ret.append(
                        {
                            "ticket_id": detail_object["ticket_id"],
                            "ticket": detail_object["ticket"],
                            "ticket_detail": detail_object["ticket_detail"],
                            "ticket_notes": trouble_notes,
                            "trouble_value": trouble,
                        }
                    )
        return ret

    @staticmethod
    def filter_trouble_reports(report_list, active_reports, threshold):
        filter_reports = []
        for report in report_list:
            if report["trouble"] in active_reports and report["number_of_tickets"] >= threshold:
                filter_reports.append(report)
        return filter_reports

    async def append_asr_forwarding_note(self, ticket_id, link, serial_number):
        target_queue = ForwardQueues.ASR.value
        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))

        note_lines = [
            f"#*MetTel's IPA*#",
            f'Status of Wired Link {link["interface"]} ({link["displayName"]}) is {link["linkState"]}.',
            f"Moving task to: {target_queue}",
            f"TimeStamp: {current_datetime_tz_aware}",
        ]

        task_result_note = os.linesep.join(note_lines)
        return await self.append_note_to_ticket(ticket_id, task_result_note, service_numbers=[serial_number])
