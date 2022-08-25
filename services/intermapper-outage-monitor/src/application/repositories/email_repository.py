import json
import logging

from shortuuid import uuid

from application.repositories import nats_error_response
from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class EmailRepository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_unread_emails(self):
        err_msg = None
        email_account = self._config.INTERMAPPER_CONFIG["inbox_email"]
        email_filter = self._config.INTERMAPPER_CONFIG["sender_emails_list"]
        lookup_days = self._config.INTERMAPPER_CONFIG["events_lookup_days"]

        request = {
            "request_id": uuid(),
            "body": {
                "email_account": email_account,
                "email_filter": email_filter,
                "lookup_days": lookup_days,
            },
        }

        try:
            logger.info(
                f"Getting the unread emails from the inbox of {email_account} sent from the users: "
                f"{email_filter} in the last {lookup_days} days"
            )
            response = await self._nats_client.request("get.email.request", to_json_bytes(request), timeout=90)
            response = json.loads(response.data)
        except Exception as e:
            err_msg = f"An error occurred while getting the unread emails from the inbox of {email_account} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(f"Got the unread emails from the inbox of {email_account}")
            else:
                err_msg = (
                    f"Error getting the unread emails from the inbox of {email_account} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def mark_email_as_read(self, msg_uid):
        err_msg = None
        email_account = self._config.INTERMAPPER_CONFIG["inbox_email"]
        request = {
            "request_id": uuid(),
            "body": {"email_account": email_account, "msg_uid": msg_uid},
        }

        try:
            logger.info(f"Marking message {msg_uid} from the inbox of {email_account} as read")
            response = await self._nats_client.request("mark.email.read.request", to_json_bytes(request), timeout=90)
            response = json.loads(response.data)
        except Exception as e:
            err_msg = f"An error occurred while marking message {msg_uid} as read -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(f"Marked message {msg_uid} as read")
            else:
                err_msg = (
                    f"Error marking message {msg_uid} as read in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
