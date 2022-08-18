import json
import logging

from nats.aio.msg import Msg

from ..repositories.email_reader_repository import EmailReaderRepository

logger = logging.getLogger(__name__)


class MarkEmailAsRead:
    def __init__(self, email_reader_repository: EmailReaderRepository):
        self._email_reader_repository = email_reader_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"request_id": payload["request_id"], "body": None, "status": None}

        if payload.get("body") is None:
            logger.error(f"Cannot mark email as read using {json.dumps(payload)}. Must include body in request")
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await msg.respond(json.dumps(response).encode())
            return

        if not all(
            key in payload["body"].keys()
            for key in (
                "msg_uid",
                "email_account",
            )
        ):
            logger.error(f"Cannot mark email as read using {json.dumps(payload)}. JSON malformed")

            response["status"] = 400
            response[
                "body"
            ] = 'You must include "msg_uid" and "email_account" in the "body" field of the response request'
            await msg.respond(json.dumps(response).encode())
            return

        msg_uid = payload["body"]["msg_uid"]
        email_account = payload["body"]["email_account"]

        logger.info(f"Attempting to mark message {msg_uid} from email account {email_account} as read")

        mark_as_read_response = await self._email_reader_repository.mark_as_read(msg_uid, email_account)
        response["body"] = mark_as_read_response["body"]
        response["status"] = mark_as_read_response["status"]

        logger.info(
            f"Received the following from attempting to mark message {msg_uid} as read: "
            f'{json.dumps(response["body"], indent=2)}'
        )
        await msg.respond(json.dumps(response).encode())
