import json
import logging
from typing import Any

from shortuuid import uuid

from application import nats_error_response

logger = logging.getLogger(__name__)


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


def get_data_from_response_message(message):
    return json.loads(message.data)


class HawkeyeRepository:
    def __init__(self, nats_client, notifications_repository):
        self._nats_client = nats_client
        self._notifications_repository = notifications_repository

    async def get_probes(self):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {},
        }

        try:
            logger.info(f"Getting all probes from Hawkeye...")
            response = get_data_from_response_message(
                await self._nats_client.request("hawkeye.probe.request", to_json_bytes(request), timeout=120)
            )
        except Exception as e:
            err_msg = f"An error occurred when requesting all probes from Hawkeye -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = f"Error while retrieving probes: Error {response_status} - {response_body}"
            else:
                logger.info("Got all probes from Hawkeye!")

        if err_msg:
            await self.__notify_error(err_msg)

        return response

    async def __notify_error(self, err_msg):
        logger.error(err_msg)
        await self._notifications_repository.send_slack_message(err_msg)
