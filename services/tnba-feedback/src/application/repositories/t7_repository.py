import json
import logging

from shortuuid import uuid

from application.repositories import nats_error_response
from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class T7Repository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
        self._config = config
        self._notifications_repository = notifications_repository

    async def post_metrics(self, ticket_id: int, ticket_rows: list):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {"ticket_id": ticket_id, "ticket_rows": ticket_rows},
        }

        try:
            logger.info(f"Posting metrics for ticket {ticket_id} to T7...")
            response = await self._nats_client.request("t7.automation.metrics", to_json_bytes(request), timeout=120)
            response = json.loads(response.data)
            logger.info(f"Metrics posted for ticket {ticket_id}!")
        except Exception as e:
            err_msg = f"An error occurred when posting metrics for ticket {ticket_id} to T7. Error: {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error when posting metrics for ticket {ticket_id} to T7 in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} "
                    f"environment. Error: Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    def tnba_note_in_task_history(self, task_history):
        task_history_tnba_filter = [
            task
            for task in task_history
            if task["Notes"] is not None
            if ("TNBA" in task["Notes"] or "AI" in task["Notes"])
        ]
        if len(task_history_tnba_filter) > 0:
            return True

        return False
