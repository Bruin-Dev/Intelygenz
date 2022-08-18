import json
import logging

from nats.aio.msg import Msg

from ..repositories.email_reader_repository import EmailReaderRepository

logger = logging.getLogger(__name__)


class GetEmails:
    def __init__(self, email_reader_repository: EmailReaderRepository):
        self._email_reader_repository = email_reader_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"request_id": payload["request_id"], "body": None, "status": None}

        if payload.get("body") is None:
            logger.error(f"Cannot get unread emails with {json.dumps(payload)}. Must include body in request")
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await msg.respond(json.dumps(response).encode())
            return

        if not all(
            key in payload["body"].keys()
            for key in (
                "email_account",
                "email_filter",
                "lookup_days",
            )
        ):
            logger.error(f"Cannot get unread emails with {json.dumps(payload)}. JSON malformed")

            response["status"] = 400
            response["body"] = (
                'You must include "email_account", "email_filter" and "lookup_days" '
                'in the "body" field of the response request'
            )
            await msg.respond(json.dumps(response).encode())
            return

        email_account = payload["body"]["email_account"]
        email_filter = payload["body"]["email_filter"]
        lookup_days = payload["body"]["lookup_days"]

        logger.info(
            f"Attempting to get all unread messages from email account {email_account} from the past {lookup_days} "
            f"days coming from {email_filter}"
        )

        unread_messages_response = await self._email_reader_repository.get_unread_emails(
            email_account,
            email_filter,
            lookup_days,
        )
        response["body"] = unread_messages_response["body"]
        response["status"] = unread_messages_response["status"]

        logger.info(f"Received the following from the gmail account {email_account}: " f'{response["body"]}')
        await msg.respond(json.dumps(response).encode())
