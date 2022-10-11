import json
import logging
from typing import Any

from shortuuid import uuid

from application.repositories import nats_error_response

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

    async def get_ticket_task_history(self, ticket_id):
        err_msg = None

        logger.info(f"Getting ticket task history for app.bruin.com/t/{ticket_id}")
        request_msg = {"request_id": uuid(), "body": {"ticket_id": ticket_id}}
        try:
            response = get_data_from_response_message(
                await self._nats_client.request("bruin.ticket.get.task.history", to_json_bytes(request_msg), timeout=60)
            )
            logger.info(f"Got task_history of ticket {ticket_id} from Bruin!")

        except Exception as e:

            err_msg = (
                f"An error occurred when requesting ticket task_history from Bruin API for ticket {ticket_id} "
                f"-> {e}"
            )

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
