import json
import logging
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

from framework.nats.client import Client as NatsClient
from shortuuid import uuid

logger = logging.getLogger(__name__)


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


@dataclass
class BruinClient:
    def __init__(self, nats_client: NatsClient):
        self.nats_client = nats_client

    async def get_customer_info_from_serial(self, serial_number: str):
        customer_info = []
        request = {
            "request_id": uuid(),
            "body": {
                "service_number": serial_number,
            },
        }
        try:
            get_customer_info_response = await self.nats_client.request(
                "bruin.customer.get.info", to_json_bytes(request), timeout=30
            )
            get_customer_info_response = json.loads(get_customer_info_response.data)
        except Exception as e:
            logger.warning(
                f"Exception calling to bruin-bridge to obtain customer info with request: {request} because {e}"
            )
        else:
            if get_customer_info_response["status"] == HTTPStatus.OK:
                customer_info = get_customer_info_response["body"]
        finally:
            return customer_info

    async def get_management_status(self, client_id: int, serial_number: str):
        management_status = None
        request = {
            "request_id": uuid(),
            "body": {
                "client_id": client_id,
                "service_number": serial_number,
                "status": "A",
            },
        }

        try:
            get_management_status_response = await self.nats_client.request(
                "bruin.inventory.management.status", to_json_bytes(request), timeout=30
            )
            get_management_status_response = json.loads(get_management_status_response.data)
        except Exception as e:
            logger.warning(
                f"Exception calling to bruin-bridge to obtain management status with request: {request} because {e}"
            )
        else:
            if get_management_status_response["status"] == HTTPStatus.OK:
                management_status = get_management_status_response["body"]

        return management_status
