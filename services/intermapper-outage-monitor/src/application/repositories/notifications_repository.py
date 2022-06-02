from application.repositories import nats_error_response
from shortuuid import uuid


class NotificationsRepository:
    def __init__(self, logger, event_bus, config):
        self._logger = logger
        self._event_bus = event_bus
        self._config = config

    async def send_slack_message(self, message: str):
        message = {
            "request_id": uuid(),
            "message": f"[{self._config.LOG_CONFIG['name']}]: {message}",
        }
        await self._event_bus.rpc_request("notification.slack.request", message, timeout=10)

    async def get_unread_emails(self):
        err_msg = None
        email_account = self._config.INTERMAPPER_CONFIG["inbox_email"]
        email_filter = self._config.INTERMAPPER_CONFIG["sender_emails_list"]
        request = {
            "request_id": uuid(),
            "body": {"email_account": email_account, "email_filter": email_filter},
        }

        try:
            self._logger.info(
                f"Getting the unread emails from the inbox of {email_account} sent from the users: " f"{email_filter}"
            )
            response = await self._event_bus.rpc_request("get.email.request", request, timeout=90)
        except Exception as e:
            err_msg = f"An error occurred while getting the unread emails from the inbox of {email_account} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(f"Got the unread emails from the inbox of {email_account}")
            else:
                err_msg = (
                    f"Error getting the unread emails from the inbox of {email_account} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self.send_slack_message(err_msg)

        return response

    async def mark_email_as_read(self, msg_uid):
        err_msg = None
        email_account = self._config.INTERMAPPER_CONFIG["inbox_email"]
        request = {
            "request_id": uuid(),
            "body": {"email_account": email_account, "msg_uid": msg_uid},
        }

        try:
            self._logger.info(f"Marking message {msg_uid} from the inbox of {email_account} as read")
            response = await self._event_bus.rpc_request("mark.email.read.request", request, timeout=90)
        except Exception as e:
            err_msg = f"An error occurred while marking message {msg_uid} as read -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(f"Marked message {msg_uid} as read")
            else:
                err_msg = (
                    f"Error marking message {msg_uid} as read in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self.send_slack_message(err_msg)

        return response
