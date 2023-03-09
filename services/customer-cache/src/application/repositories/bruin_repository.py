import json
import logging

from application.repositories import nats_error_response
from application.repositories.utils_repository import to_json_bytes
from shortuuid import uuid

logger = logging.getLogger(__name__)


class BruinRepository:
    def __init__(self, config, nats_client, notifications_repository):
        self._config = config
        self._nats_client = nats_client
        self._notifications_repository = notifications_repository

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
            logger.info(f"Got client info for service number {service_number}!")
        except Exception as e:
            err_msg = f"An error occurred when claiming client info for service number {service_number} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while claiming client info for service number {service_number} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_management_status(self, client_id: int, service_number: str):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "client_id": client_id,
                "service_number": service_number,
                "status": "A",
            },
        }

        try:
            logger.info(f"Claiming management status for service number {service_number} and client {client_id}...")
            response = await self._nats_client.request(
                "bruin.inventory.management.status", to_json_bytes(request), timeout=90
            )
            response = json.loads(response.data)
            logger.info(f"Got management status for service number {service_number} and client {client_id}!")
        except Exception as e:
            err_msg = (
                f"An error occurred when claiming management status for service number {service_number} and "
                f"client {client_id} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while claiming management status for service number {service_number} and "
                    f"client {client_id} in {self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_inventory_attributes(self, client_id: int, service_number: str):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "client_id": client_id,
                "service_number": service_number,
                "status": "A",
            },
        }

        try:
            logger.info(f"Getting inventory attributes for service number {service_number} and client {client_id}...")
            response = await self._nats_client.request(
                "bruin.inventory.attributes", to_json_bytes(request), timeout=90
            )
            response = json.loads(response.data)
            logger.info(f"Got inventory attributes for service number {service_number} and client {client_id}!")
        except Exception as e:
            err_msg = (
                f"An error occurred when getting inventory attributes for service number {service_number} and "
                f"client {client_id} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while getting inventory attributes for service number {service_number} and "
                    f"client {client_id} in {self._config.ENVIRONMENT_NAME.upper()} environment: "
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
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_ticket_contact(self, client_id: int):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "client_id": client_id
            },
        }

        try:
            logger.info(f"Getting ticket contact for client {client_id}...")
            response = await self._nats_client.request("bruin.get.ticket.contacts", to_json_bytes(request), timeout=120)
            response = json.loads(response.data)
        except Exception as e:
            err_msg = f"An error occurred while getting ticket contact for client {client_id}... -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(f"Got ticket contact for client {client_id} successfully!")
            else:
                err_msg = (
                    f"Error while getting ticket contact for client {client_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    def get_management_status_from_inventory_attributes(inventory_attributes):
        attr_key = "Management Status"
        attribute = [
            attribute["value"]
            for attribute in inventory_attributes["attributes"]
            if attribute["key"] == attr_key
        ]
        if len(attribute) > 0:
            attribute = attribute[0]
        else:
            attribute = None

        return attribute

    def is_management_status_active(self, management_status) -> bool:
        return management_status in self._config.REFRESH_CONFIG["monitorable_management_statuses"]
