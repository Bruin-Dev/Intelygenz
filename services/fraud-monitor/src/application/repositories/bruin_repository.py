import json
import logging
import os
from datetime import datetime

from application import ForwardQueues
from application.repositories import nats_error_response
from application.repositories.utils_repository import to_json_bytes
from pytz import timezone
from shortuuid import uuid

logger = logging.getLogger(__name__)


class BruinRepository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_client_info_by_did(self, did: str):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "did": did,
            },
        }

        try:
            logger.info(f"Getting client info by DID {did}...")
            response = await self._nats_client.request(
                "bruin.customer.get.info_by_did", to_json_bytes(request), timeout=75
            )
            response = json.loads(response.data)
        except Exception as e:
            err_msg = f"An error occurred when getting client info by DID {did} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(f"Got client info by DID {did}!")
            else:
                err_msg = (
                    f"Error while getting client info by DID {did} in {self._config.ENVIRONMENT_NAME.upper()} "
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_tickets(self, client_id: int, ticket_topic: str, ticket_statuses: list, service_number: str):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "client_id": client_id,
                "ticket_statuses": ticket_statuses,
                "ticket_topic": ticket_topic,
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

            response = await self._nats_client.request(
                "bruin.ticket.basic.request", to_json_bytes(request), timeout=150
            )
            response = json.loads(response.data)
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

    async def get_fraud_tickets(self, client_id: int, ticket_statuses: list, service_number: str):
        ticket_topic = "VAS"
        return await self.get_tickets(client_id, ticket_topic, ticket_statuses, service_number)

    async def get_open_fraud_tickets(self, client_id: int, service_number: str):
        ticket_statuses = ["New", "InProgress", "Draft"]
        return await self.get_fraud_tickets(client_id, ticket_statuses, service_number)

    async def get_resolved_fraud_tickets(self, client_id: int, service_number: str):
        ticket_statuses = ["Resolved"]
        return await self.get_fraud_tickets(client_id, ticket_statuses, service_number)

    async def get_ticket_details(self, ticket_id: int):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {"ticket_id": ticket_id},
        }

        try:
            logger.info(f"Getting details of ticket {ticket_id} from Bruin...")
            response = await self._nats_client.request(
                "bruin.ticket.details.request", to_json_bytes(request), timeout=75
            )
            response = json.loads(response.data)
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

    async def get_client_info(self, service_number: str):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "service_number": service_number,
            },
        }

        try:
            logger.info(f"Claiming client info for service number {service_number}...")
            response = await self._nats_client.request("bruin.customer.get.info", to_json_bytes(request), timeout=90)
            response = json.loads(response.data)
        except Exception as e:
            err_msg = f"An error occurred when claiming client info for service number {service_number} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(f"Got client info for service number {service_number}!")
            else:
                err_msg = (
                    f"Error while claiming client info for service number {service_number} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_site_details(self, client_id: int, site_id: int):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "client_id": client_id,
                "site_id": site_id,
            },
        }

        try:
            logger.info(f"Getting site details of site {site_id} and client {client_id}...")
            response = await self._nats_client.request("bruin.get.site", to_json_bytes(request), timeout=120)
            response = json.loads(response.data)
        except Exception as e:
            err_msg = f"An error occurred while getting site details of site {site_id} and client {client_id}... -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(f"Got site details of site {site_id} and client {client_id} successfully!")
            else:
                err_msg = (
                    f"Error while getting site details of site {site_id} and client {client_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    @staticmethod
    def get_contact_info(site_details):
        site_name = site_details["primaryContactName"]
        site_phone = site_details["primaryContactPhone"]
        site_email = site_details["primaryContactEmail"]

        contact_info = {
            "name": site_name,
            "email": site_email,
        }

        if site_phone:
            contact_info["phone"] = site_phone

        return contact_info

    @staticmethod
    def get_contacts(contact_info):
        return [
            {**contact_info, "type": "ticket"},
            {**contact_info, "type": "site"},
        ]

    async def append_note_to_ticket(
        self, ticket_id: int, service_number: str, email_body: str, msg_uid: str, reopening: bool = False
    ):
        err_msg = None
        note = self._build_fraud_note(email_body, msg_uid, reopening)

        request = {
            "request_id": uuid(),
            "body": {
                "ticket_id": ticket_id,
                "note": note,
            },
        }

        if service_number:
            request["body"]["service_numbers"] = [service_number]

        try:
            logger.info(f"Appending note to ticket {ticket_id}... Note contents:\n{note}")
            response = await self._nats_client.request(
                "bruin.ticket.note.append.request", to_json_bytes(request), timeout=120
            )
            response = json.loads(response.data)
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
                logger.info(f"Note appended to ticket {ticket_id}!")
            else:
                err_msg = (
                    f"Error while appending note to ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. Note was {note}. Error: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def create_fraud_ticket(self, client_id: int, service_number: str, contacts: list):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "category": "VAS",
                "clientId": client_id,
                "services": [{"serviceNumber": service_number}],
                "contacts": contacts,
            },
        }

        try:
            logger.info(
                f"Creating fraud ticket for service number {service_number} that belongs to client {client_id}..."
            )
            response = await self._nats_client.request(
                "bruin.ticket.creation.request", to_json_bytes(request), timeout=150
            )
            response = json.loads(response.data)
        except Exception as e:
            err_msg = (
                f"An error occurred when creating fraud ticket for service number {service_number} "
                f"that belongs to client {client_id} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(
                    f"Fraud ticket for service number {service_number} that belongs to client {client_id} created!"
                )
            else:
                err_msg = (
                    f"Error while creating fraud ticket for service number {service_number} that belongs to client "
                    f"{client_id} in {self._config.ENVIRONMENT_NAME.upper()} environment: "
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
            response = await self._nats_client.request("bruin.ticket.status.open", to_json_bytes(request), timeout=75)
            response = json.loads(response.data)
        except Exception as e:
            err_msg = f"An error occurred when opening ticket {ticket_id} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(f"Ticket {ticket_id} opened!")
            else:
                err_msg = (
                    f"Error while opening ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    def _build_fraud_note(self, email_body: str, msg_uid: str, reopening: bool) -> str:
        note_lines = ["#*MetTel's IPA*#"]

        if reopening:
            note_lines.append("Re-opening ticket.")

        note_lines += [
            email_body,
            "",
            f"Email UID: {msg_uid}",
            f"TimeStamp: {datetime.now(timezone(self._config.TIMEZONE))}",
        ]

        return os.linesep.join(note_lines)

    async def change_detail_work_queue(self, ticket_id: int, task_result: str, *, service_number: str = None):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {"ticket_id": ticket_id, "queue_name": task_result},
        }

        if service_number:
            request["body"]["service_number"] = service_number

        try:
            logger.info(f"Changing task result of serial {service_number} in ticket {ticket_id} to {task_result}...")
            response = await self._nats_client.request("bruin.ticket.change.work", to_json_bytes(request), timeout=150)
            response = json.loads(response.data)
        except Exception as e:
            err_msg = (
                f"An error occurred when changing task result of serial {service_number} "
                f"in ticket {ticket_id} to {task_result} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(
                    f"Task result of detail serial {service_number} in ticket {ticket_id} "
                    f"changed to {task_result} successfully!"
                )
            else:
                err_msg = (
                    f"Error while changing task result of serial {service_number} in ticket "
                    f"{ticket_id} to {task_result} in {self._config.ENVIRONMENT_NAME.upper()} "
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def change_detail_work_queue_to_hnoc(self, ticket_id: int, *, service_number: str = None):
        target_queue = ForwardQueues.HNOC.value

        return await self.change_detail_work_queue(
            ticket_id=ticket_id, task_result=target_queue, service_number=service_number
        )
