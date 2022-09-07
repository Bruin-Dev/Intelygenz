import json
import logging

from nats.aio.msg import Msg

from ..repositories.email_repository import EmailRepository

logger = logging.getLogger(__name__)


class SendToEmail:
    def __init__(self, email_repository: EmailRepository):
        self._email_repository = email_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)
        response = {"request_id": payload["request_id"], "body": None, "status": None}

        if payload.get("body") is None:
            logger.error(f"Cannot send to email with {json.dumps(payload)}. Must include body in request")

            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await msg.respond(json.dumps(response).encode())
            return

        if not all(key in payload["body"].keys() for key in ("email_data",)):
            logger.error(f"Cannot send to email with {json.dumps(payload)}. JSON malformed")

            response["status"] = 400
            response["body"] = 'Must include "email_data" in request body'
            await msg.respond(json.dumps(response).encode())
            return

        email_data = payload["body"]["email_data"]
        if email_data == "":
            logger.error(f'Cannot send to email with {json.dumps(payload)}. Parameter "email_data" cannot be empty')

            response["status"] = 400
            response["body"] = 'Must include a valid "email_data" in request body'
            await msg.respond(json.dumps(response).encode())
            return

        send_to_email_response = self._email_repository.send_to_email(email_data)
        response["body"] = send_to_email_response["body"]
        response["status"] = send_to_email_response["status"]
        logger.info(
            f"Received the following from attempting to send {json.dumps(payload)}"
            f" to email: {send_to_email_response['body']}"
        )
        await msg.respond(json.dumps(response).encode())
