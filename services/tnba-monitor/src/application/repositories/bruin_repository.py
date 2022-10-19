import json
import logging
from typing import List

from shortuuid import uuid

from application.repositories import nats_error_response
from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class BruinRepository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_tickets(self, client_id: int, ticket_topic: str, ticket_statuses: list):
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

        try:
            logger.info(
                f"Getting all tickets with any status of {ticket_statuses}, with ticket topic "
                f"{ticket_topic} and belonging to client {client_id} from Bruin..."
            )
            response = await self._nats_client.request("bruin.ticket.basic.request", to_json_bytes(request), timeout=90)
            response = json.loads(response.data)
            logger.info(
                f"Got all tickets with any status of {ticket_statuses}, with ticket topic "
                f"{ticket_topic} and belonging to client {client_id} from Bruin!"
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

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while retrieving tickets with any status of {ticket_statuses}, with ticket topic "
                    f"{ticket_topic} and belonging to client {client_id} in {self._config.ENVIRONMENT_NAME.upper()} "
                    f"environment: Error {response_status} - {response_body}"
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
            response = await self._nats_client.request(
                "bruin.ticket.details.request", to_json_bytes(request), timeout=15
            )
            response = json.loads(response.data)
            logger.info(f"Got details of ticket {ticket_id} from Bruin!")
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

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_ticket_task_history(self, ticket_id: int):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {"ticket_id": ticket_id},
        }

        try:
            logger.info(f"Getting task history of ticket {ticket_id} from Bruin...")
            response = await self._nats_client.request(
                "bruin.ticket.get.task.history", to_json_bytes(request), timeout=15
            )
            response = json.loads(response.data)
            logger.info(f"Got task history of ticket {ticket_id} from Bruin!")
        except Exception as e:
            err_msg = f"An error occurred when requesting task history from Bruin API for ticket {ticket_id} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while retrieving task history of ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def resolve_ticket_detail(self, ticket_id: int, detail_id: int):
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
            response = await self._nats_client.request(
                "bruin.ticket.status.resolve", to_json_bytes(request), timeout=15
            )
            response = json.loads(response.data)
        except Exception as e:
            err_msg = f"An error occurred when resolving detail {detail_id} of affecting ticket {ticket_id} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while resolving detail {detail_id} of ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )
            else:
                logger.info(f"Detail {detail_id} of ticket {ticket_id} resolved successfully!")

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_next_results_for_ticket_detail(self, ticket_id: int, detail_id: int, service_number: str):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
                "service_number": service_number,
            },
        }

        try:
            logger.info(
                f"Claiming next results for ticket {ticket_id}, detail {detail_id} and "
                f"service number {service_number}..."
            )
            response = await self._nats_client.request(
                "bruin.ticket.detail.get.next.results", to_json_bytes(request), timeout=15
            )
            response = json.loads(response.data)
            logger.info(
                f"Got next results for ticket {ticket_id}, detail {detail_id} and service number {service_number}!"
            )
        except Exception as e:
            err_msg = (
                f"An error occurred when claiming next results for ticket {ticket_id}, detail {detail_id} and "
                f"service number {service_number} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if not (response_status in range(200, 300) or response_status == 409 or response_status == 471):
                err_msg = (
                    f"Error while claiming next results for ticket {ticket_id}, detail {detail_id} and "
                    f"service number {service_number} in {self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def append_multiple_notes_to_ticket(self, ticket_id: int, notes: List[dict]):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "ticket_id": ticket_id,
                "notes": notes,
            },
        }

        try:
            logger.info(f"Posting multiple notes for ticket {ticket_id}...")
            response = await self._nats_client.request(
                "bruin.ticket.multiple.notes.append.request", to_json_bytes(request), timeout=15
            )
            response = json.loads(response.data)
            logger.info(f"Posted multiple notes for ticket {ticket_id}!")
        except Exception as e:
            err_msg = (
                f"An error occurred when appending multiple ticket notes to ticket {ticket_id}. "
                f"Notes: {notes}. Error: {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if not (response_status in range(200, 300) or response_status == 409 or response_status == 471):
                err_msg = (
                    f"Error while appending multiple notes to ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. Notes were {notes}. "
                    f"Error: Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def unpause_ticket_detail(self, ticket_id: int, *, detail_id: int = None, service_number: str = None):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "ticket_id": ticket_id,
            },
        }

        if detail_id:
            request["body"]["detail_id"] = detail_id

        if service_number:
            request["body"]["service_number"] = service_number

        try:
            logger.info(f"Unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id}...")
            response = await self._nats_client.request("bruin.ticket.unpause", to_json_bytes(request), timeout=30)
            response = json.loads(response.data)

        except Exception as e:
            err_msg = (
                f"An error occurred when unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id}. "
                f"Error: {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(f"Detail {detail_id} (serial {service_number}) of ticket {ticket_id} was unpaused!")
            else:
                err_msg = (
                    f"Error while unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. "
                    f"Error: Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_outage_tickets(self, client_id: int, ticket_statuses: list):
        ticket_topic = "VOO"

        return await self.get_tickets(client_id, ticket_topic, ticket_statuses)

    async def get_open_outage_tickets(self, client_id: int):
        ticket_topic = "VOO"
        ticket_statuses = ["New", "InProgress", "Draft"]

        return await self.get_tickets(client_id, ticket_topic, ticket_statuses)

    async def get_affecting_tickets(self, client_id: int, ticket_statuses: list):
        ticket_topic = "VAS"

        return await self.get_tickets(client_id, ticket_topic, ticket_statuses)

    async def get_open_affecting_tickets(self, client_id: int):
        ticket_topic = "VAS"
        ticket_statuses = ["New", "InProgress", "Draft"]

        return await self.get_tickets(client_id, ticket_topic, ticket_statuses)
