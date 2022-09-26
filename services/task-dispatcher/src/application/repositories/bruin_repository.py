import json
import logging

from shortuuid import uuid

from application.repositories import nats_error_response
from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class BruinRepository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
        self._config = config
        self._notifications_repository = notifications_repository

    async def change_detail_work_queue(self, target_queue: str, ticket_id: int, detail_id: int, serial_number: str):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "queue_name": target_queue,
                "ticket_id": ticket_id,
            },
        }

        if detail_id:
            request["body"]["detail_id"] = detail_id

        if serial_number:
            request["body"]["service_number"] = serial_number

        try:
            logger.info(
                f"Changing work queue for ticket {ticket_id}, detail {detail_id} and serial number {serial_number} "
                f"to the {target_queue} queue..."
            )
            response = await self._nats_client.request("bruin.ticket.change.work", to_json_bytes(request), timeout=90)
            response = json.loads(response.data)
        except Exception as e:
            err_msg = (
                f"An error occurred when changing work queue for ticket {ticket_id}, detail {detail_id} "
                f"and serial number {serial_number} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                success_msg = (
                    f"Work queue changed for ticket {ticket_id}, detail {detail_id} and serial number {serial_number} "
                    f"to the {target_queue} queue successfully!"
                )
                logger.info(success_msg)
                await self._notifications_repository.send_slack_message(success_msg)
            else:
                err_msg = (
                    f"Error while changing work queue for ticket {ticket_id}, detail {detail_id} "
                    f"and serial number {serial_number} to the {target_queue} queue in "
                    f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
