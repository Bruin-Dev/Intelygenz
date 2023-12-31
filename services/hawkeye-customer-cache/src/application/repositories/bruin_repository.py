import asyncio
import json
import logging

from application import nats_error_response
from application.repositories.utils_repository import to_json_bytes
from shortuuid import uuid
from tenacity import retry, stop_after_delay, wait_exponential

logger = logging.getLogger(__name__)


class BruinRepository:
    def __init__(self, config, nats_client, notifications_repository):
        self._config = config
        self._nats_client = nats_client
        self._semaphore = asyncio.BoundedSemaphore(self._config.REFRESH_CONFIG["semaphore"])
        self._notifications_repository = notifications_repository
        self._serials_with_multiple_inventories = {}

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
            await self._notify_error(err_msg)

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
            await self._notify_error(err_msg)

        return response

    def is_management_status_active(self, management_status) -> bool:
        return management_status in self._config.REFRESH_CONFIG["monitorable_management_statuses"]

    async def _notify_error(self, err_msg):
        logger.error(err_msg)
        await self._notifications_repository.send_slack_message(err_msg)

    async def filter_probe(self, probe):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.REFRESH_CONFIG["multiplier"], min=self._config.REFRESH_CONFIG["min"]
            ),
            stop=stop_after_delay(self._config.REFRESH_CONFIG["stop_delay"]),
            reraise=True,
        )
        async def _filter_probe():
            async with self._semaphore:
                serial_number = probe["serialNumber"]
                logger.info(f"Checking if device with serial {serial_number} should be monitored...")

                client_info_response = await self.get_client_info(serial_number)
                client_info_response_status = client_info_response["status"]
                if client_info_response_status not in range(200, 300):
                    logger.error(f"Error while fetching client info for device {serial_number}: {client_info_response}")
                    return

                client_info_response_body = client_info_response["body"]
                if len(client_info_response_body) > 1:
                    logger.info(f"Device {serial_number} has {len(client_info_response_body)} inventories in Bruin")
                    self._serials_with_multiple_inventories[serial_number] = client_info_response_body

                if not client_info_response_body:
                    logger.warning(f"Device with serial {serial_number} doesn't have any Bruin client info associated")
                    return

                client_id = client_info_response_body[0].get("client_id")

                management_status_response = await self.get_management_status(client_id, serial_number)
                management_status_response_status = management_status_response["status"]
                if management_status_response_status not in range(200, 300):
                    logger.error(
                        f"Error while fetching management status for device {serial_number}: "
                        f"{management_status_response}"
                    )
                    return

                management_status_response_body = management_status_response["body"]
                if not self.is_management_status_active(management_status_response_body):
                    logger.warning(f"Management status is not active for serial {serial_number}. Skipping...")
                    return
                else:
                    logger.info(f"Management status for serial {serial_number} seems active")

                return {
                    "probe_id": probe["probeId"],
                    "probe_uid": probe["uid"],
                    "probe_group": probe["probeGroup"],
                    "device_type_name": probe["typeName"],
                    "last_contact": max(
                        "" if probe["nodetonode"]["lastUpdate"] == "never" else probe["nodetonode"]["lastUpdate"],
                        "" if probe["realservice"]["lastUpdate"] == "never" else probe["realservice"]["lastUpdate"],
                    ),
                    "serial_number": serial_number,
                    "bruin_client_info": client_info_response_body[0],
                }

        try:
            return await _filter_probe()
        except Exception as e:
            logger.error(f"An error occurred while checking if probe {probe['probeId']} should be cached or not -> {e}")
