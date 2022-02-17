import os
from shortuuid import uuid
from datetime import datetime

import humps
import html2text
from tenacity import retry, wait_exponential, stop_after_delay

from application.repositories import nats_error_response
from typing import Any, Dict, List, Tuple


class BruinRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._timeout = self._config.MONITOR_CONFIG["nats_request_timeout"][
            "bruin_request_seconds"
        ]

    async def get_single_ticket_basic_info(self, ticket_id: str):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"],
                min=self._config.NATS_CONFIG["min"],
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def get_single_ticket_basic_info():
            err_msg = None
            self._logger.info(f'Getting ticket "{ticket_id}" basic info')
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "ticket_id": ticket_id,
                },
            }
            try:
                response = await self._event_bus.rpc_request(
                    "bruin.single_ticket.basic.request",
                    request_msg,
                    timeout=self._timeout,
                )

            except Exception as err:
                err_msg = (
                    f"An error occurred when getting basic info from Bruin, "
                    f'for ticket_id "{ticket_id}" -> {err}'
                )
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status not in range(200, 300):
                    err_msg = (
                        f"Error getting basic info for ticket {ticket_id} in "
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )
                else:
                    response["body"] = {
                        "ticket_id": ticket_id,
                        "ticket_status": response["body"]["ticketStatus"],
                        "call_type": response["body"]["callType"],
                        "category": response["body"]["category"],
                        "creation_date": response["body"]["createDate"],
                    }

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(
                    f"Basic info for ticket {ticket_id} retrieved from Bruin"
                )

            return response

        try:
            return await get_single_ticket_basic_info()
        except Exception as e:
            self._logger.error(f"Error getting ticket {ticket_id} from Bruin: {e}")

    async def get_single_ticket_info_with_service_numbers(self, ticket_id: str):
        basic_info_response = await self.get_single_ticket_basic_info(ticket_id)
        if basic_info_response["status"] not in range(200, 300):
            return {
                "status": basic_info_response["status"],
                "body": "Error while retrieving basic ticket info",
            }
        if not basic_info_response["body"]:
            return {"status": 404, "body": "Ticket not found"}

        ticket = basic_info_response["body"]
        details = await self.get_ticket_details(ticket["ticket_id"])
        if details["status"] not in range(200, 300):
            err_msg = f"Error while retrieving details from ticket {ticket_id}"
            self._logger(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)
            return {
                "status": 500,
                "body": "Error while retrieving ticket service_numbers",
            }
        service_numbers = self._get_details_service_numbers(details["body"])
        ticket["service_numbers"] = service_numbers

        return {"status": 200, "body": ticket}

    async def verify_service_number_information(
        self, client_id: str, service_number: str
    ):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"],
                min=self._config.NATS_CONFIG["min"],
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def verify_service_number_information():
            err_msg = None
            self._logger.info(
                f'Getting inventory "{client_id}" and service number {service_number}'
            )
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "client_id": client_id,
                    "service_number": service_number,
                    "status": "A",
                },
            }
            try:
                response = await self._event_bus.rpc_request(
                    "bruin.customer.get.info", request_msg, timeout=self._timeout
                )
            except Exception as err:
                err_msg = (
                    f"An error occurred when getting service number info from Bruin, "
                    f'for ticket_id "{client_id}" -> {err}'
                )
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status not in range(200, 300):
                    err_msg = (
                        f"Error getting service number info for {service_number} in "
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )
                elif not response_body:
                    self._logger.info(f"Service number not validated {service_number}")
                    response["status"] = 404
                    response["body"] = "Service number not validated"
                else:
                    response["status"] = response_status
                    response["body"] = {
                        "client_id": client_id,
                        "site_id": response_body[0].get("site_id"),
                        "service_number": service_number,
                    }

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(
                    f"Service number info {service_number} retrieved from Bruin"
                )

            return response

        try:
            return await verify_service_number_information()
        except Exception as e:
            self._logger.error(
                f"Error getting service number info {service_number} from Bruin: {e}"
            )

    async def get_ticket_details(self, ticket_id: int):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"],
                min=self._config.NATS_CONFIG["min"],
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def get_ticket_details():
            err_msg = None

            request = {
                "request_id": uuid(),
                "body": {"ticket_id": ticket_id},
            }

            try:
                self._logger.info(
                    f"Getting details of ticket {ticket_id} from Bruin..."
                )
                response = await self._event_bus.rpc_request(
                    "bruin.ticket.details.request",
                    request,
                    self._timeout,
                )
            except Exception as e:
                err_msg = (
                    f"An error occurred when requesting ticket details "
                    f"from Bruin API for ticket {ticket_id} -> {e}"
                )
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
                    self._logger.info(f"Got details of ticket {ticket_id} from Bruin!")

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            return response

        try:
            return await get_ticket_details()
        except Exception as e:
            self._logger.error(
                f"Error getting ticket details for {ticket_id} from Bruin: {e}"
            )

    async def get_site(self, client_id: str, site_id: str):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "client_id": client_id,
                "site_id": site_id,
            },
        }

        try:
            self._logger.info(
                f"Getting site for site_id {site_id} of client {client_id}..."
            )

            response = await self._event_bus.rpc_request(
                "bruin.get.site", request, timeout=15
            )
        except Exception as e:
            err_msg = (
                f"An error occurred while getting site for site_id {site_id} "
                f"Error: {e} "
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(
                    f"Got site details of site {site_id} and client {client_id} successfully!"
                )
            else:
                err_msg = (
                    f"An error response from bruin while getting site information for site_id {site_id} "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment."
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def link_email_to_ticket(self, ticket_id: int, email_id: int):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "ticket_id": ticket_id,
                "email_id": email_id,
            },
        }

        try:
            self._logger.info(f"Linking email {email_id} with ticket {ticket_id}...")

            response = await self._event_bus.rpc_request(
                "bruin.link.ticket.email", request, timeout=15
            )
        except Exception as e:
            err_msg = (
                f"An error occurred when linking ticket {ticket_id} and email {email_id}. "
                f"Error: {e} "
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(
                    f"Linked email {email_id} to ticket {ticket_id} successfully!"
                )
            else:
                err_msg = (
                    f"An error occurred when linking ticket {ticket_id} to email {email_id} "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment."
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def mark_email_as_done(self, email_id: int):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "email_id": email_id,
            },
        }

        try:
            self._logger.info(f"Marking email {email_id} as done...")

            response = await self._event_bus.rpc_request(
                "bruin.mark.email.done", request, timeout=15
            )
        except Exception as e:
            err_msg = f"An error occurred while marking email {email_id} as done. {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(f"Marked email {email_id} as done successfully!")
            else:
                err_msg = (
                    f"An error occurred while marking {email_id} as done in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def create_outage_ticket(
        self, client_id: int, service_numbers: List[str], contact_address: str
    ):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "client_id": client_id,
                "service_number": service_numbers,
                "ticket_contact": {"email": contact_address},
            },
        }

        try:
            self._logger.info(
                f"Creating outage ticket for device {service_numbers} that belongs to client {client_id}..."
            )
            response = await self._event_bus.rpc_request(
                "bruin.ticket.creation.outage.request", request, timeout=30
            )
        except Exception as e:
            err_msg = (
                f"An error occurred when creating outage ticket for device {service_numbers} belong to client"
                f"{client_id} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            is_bruin_custom_status = response_status in (409, 471, 472, 473)
            if response_status in range(200, 300) or is_bruin_custom_status:
                self._logger.info(
                    f"Outage ticket for devices {service_numbers} that belongs to client {client_id} created!"
                )
            else:
                err_msg = (
                    f"Error while creating outage ticket for devices {service_numbers} that belongs to client "
                    f"{client_id} in {self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def append_bec_note_to_ticket(
        self,
        ticket_id: int,
        subject: str,
        from_address: str,
        body: str,
        date: datetime,
        service_numbers: List[str],
        is_update_note: bool = False,
    ):
        new_ticket_message = "This ticket was opened via MetTel Email Center AI Engine."
        update_ticket_message = (
            "This note is new commentary from the client and posted via BEC AI engine."
        )
        operator_message = (
            update_ticket_message if is_update_note else new_ticket_message
        )

        body_cleaned = html2text.html2text(body)

        update_note = os.linesep.join(
            [
                "#*MetTel's IPA*#",
                "BEC AI RTA",
                "",
                operator_message,
                "Please review the full narrative provided in the email attached: \n"
                f"From: {from_address}",
                f"Date Stamp: {date}",
                f"Subject: {subject}",
                f"Body: \n {body_cleaned}",
            ]
        )

        return await self.append_note_to_ticket(
            ticket_id, update_note, service_numbers=service_numbers
        )

    async def append_note_to_ticket(
        self, ticket_id: int, note: str, *, service_numbers: List[str]
    ):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "ticket_id": ticket_id,
                "note": note,
                "service_numbers": service_numbers,
            },
        }
        try:
            self._logger.info(
                f'Appending note for service number(s) {", ".join(service_numbers)} in ticket {ticket_id}...'
            )
            response = await self._event_bus.rpc_request(
                "bruin.ticket.note.append.request", request, timeout=15
            )
        except Exception as e:
            err_msg = (
                f"An error occurred when appending a ticket note to ticket {ticket_id}. "
                f"Ticket note: {note}. Error: {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(f"Note appended to ticket {ticket_id} successfully!")
            else:
                err_msg = (
                    f"Error while appending note to ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. Note was {note}. Error: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_tickets_basic_info(self, ticket_statuses: List[str], **kwargs):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"],
                min=self._config.NATS_CONFIG["min"],
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def get_tickets_basic_info():
            err_msg = None
            request = {
                "request_id": uuid(),
                "body": {"ticket_statuses": ticket_statuses, **kwargs},
            }

            try:
                self._logger.info(
                    f"Getting all tickets with any status of {ticket_statuses},"
                    f"with keyword arguments {kwargs}"
                )
                response = await self._event_bus.rpc_request(
                    "bruin.ticket.basic.request", request, timeout=self._timeout
                )
            except Exception as e:
                err_msg = (
                    f"An error occurred when requesting tickets from Bruin API with any status of {ticket_statuses} "
                    f"with keyword arguments {kwargs} -> {e}"
                )
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status in range(200, 300):
                    self._logger.info(
                        f"Got all tickets with any status of {ticket_statuses}, with ticket topic "
                        f"and keyword arguments {kwargs} from Bruin!"
                    )

                else:
                    err_msg = (
                        f"Error while retrieving tickets with any status of {ticket_statuses} "
                        f"with keyword arguments {kwargs} in "
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )
            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)

            return response

        try:
            return await get_tickets_basic_info()
        except Exception as e:
            self._logger.error(
                f"Error getting tickets with keyword arguments {kwargs} from Bruin: {e}"
            )

    async def get_existing_tickets_with_service_numbers(
        self, client_id: str, site_ids: List[str]
    ) -> Dict[str, Any]:
        ticket_statuses = ["New", "InProgress", "Draft", "Resolved"]
        ticket_topic = ["VOO", "VAS"]

        # Get filter tickets by status and site_id
        tickets = []
        self._logger.info(
            "Getting tickets for client %s with status %s for site_ids %s with topics %s",
            client_id,
            ticket_statuses,
            site_ids,
            ticket_topic
        )
        for site_id in site_ids:
            for topic in ticket_topic:
                responsed_tickets = await self.get_tickets_basic_info(
                    ticket_statuses,
                    client_id=client_id,
                    site_id=site_id,
                    ticket_topic=topic,
                )
                if responsed_tickets["status"] != 200:
                    return {
                        "status": responsed_tickets["status"],
                        "body": "Error while retrieving tickets",
                    }
                tickets.extend(responsed_tickets["body"])
        if not tickets:
            return {"status": 404, "body": "No tickets found"}

        # Add services number to filtered tickets
        tickets_with_services_numbers = []
        for ticket in tickets:
            decamelize_ticket = self._decamelize_ticket(ticket)
            ticket_id = decamelize_ticket["ticket_id"]
            details = await self.get_ticket_details(ticket_id)
            if details["status"] != 200:
                err_msg = f"Error while retrieving details from ticket {ticket_id}"
                self._logger(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
                continue
            service_numbers = self._get_details_service_numbers(details["body"])
            decamelize_ticket["service_numbers"] = service_numbers

            if decamelize_ticket["ticket_status"] == "Resolved":
                decamelize_ticket["ticket_notes"] = details["body"].get("ticketNotes")

            tickets_with_services_numbers.append(decamelize_ticket)

        return {"status": 200, "body": tickets_with_services_numbers}

    def _decamelize_ticket(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        decamelized_ticket = humps.decamelize(ticket)
        decamelized_ticket["ticket_id"] = ticket["ticketID"]
        decamelized_ticket["client_id"] = ticket["clientID"]
        return decamelized_ticket

    def _get_details_service_numbers(self, ticket_details: Dict[str, Any]) -> List[str]:
        notes = ticket_details.get("ticketNotes")
        unique_service_numbers = set()
        for note in notes:
            note_service_numbers = note.get("serviceNumber", [])
            if note_service_numbers:
                unique_service_numbers.update(note_service_numbers)
        return list(unique_service_numbers)

    async def get_closed_tickets_with_creation_date_limit(
        self, limit: datetime
    ) -> Dict[str, Any]:
        ticket_topics = ["VOO", "VAS"]
        closed_tickets = []
        start_date = limit.strftime("%Y-%m-%dT%H:%M:%SZ")

        for topic in ticket_topics:
            ticket_response = await self.get_tickets_basic_info(
                ticket_statuses=["Closed"],
                ticket_topic=topic,
                start_date=start_date,
            )
            if ticket_response["status"] in range(200, 300):
                decamelized_tickets = [
                    self._decamelize_ticket(ticket)
                    for ticket in ticket_response["body"]
                ]
                closed_tickets.extend(decamelized_tickets)
            else:
                return ticket_response

        response = {"body": closed_tickets, "status": 200}

        return response

    async def get_status_and_cancellation_reasons(
        self, ticket_id: int
    ) -> Dict[str, Any]:
        # TODO: Check if we are using this method
        ticket_details = await self.get_ticket_details(ticket_id)
        if ticket_details["status"] not in range(200, 300):
            return ticket_details

        ticket_notes = ticket_details["body"]["ticketNotes"]
        (
            status,
            cancellation_reasons,
        ) = self._get_status_and_cancellation_reasons_from_notes(ticket_notes)
        response = {
            "body": {
                "ticket_status": status,
                "cancellation_reasons": cancellation_reasons,
            },
            "status": 200,
        }

        return response

    def _get_status_and_cancellation_reasons_from_notes(
        self, notes: List[Dict[str, Any]]
    ) -> Tuple[str, list]:
        cancellation_notes = filter(
            lambda x: x.get("noteType") == "CancellationReason", notes
        )
        cancellation_reasons = list(
            set([detail["noteValue"] for detail in cancellation_notes])
        )

        status = "cancelled" if cancellation_reasons else "resolved"

        return status, cancellation_reasons
