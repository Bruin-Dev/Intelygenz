from application.repositories import nats_error_response
from shortuuid import uuid


class BruinRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_ticket_task_history(self, ticket_id):
        err_msg = None

        self._logger.info(f"Getting ticket task history for app.bruin.com/t/{ticket_id}")
        request_msg = {"request_id": uuid(), "body": {"ticket_id": ticket_id}}
        try:
            response = await self._event_bus.rpc_request("bruin.ticket.get.task.history", request_msg, timeout=60)
            self._logger.info(f"Got task_history of ticket {ticket_id} from Bruin!")

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
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
