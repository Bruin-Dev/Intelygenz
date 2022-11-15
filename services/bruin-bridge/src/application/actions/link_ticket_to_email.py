import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class LinkTicketToEmail:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}
        body = payload.get("body")

        if body is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await msg.respond(to_json_bytes(response))
            return

        if not all(key in body.keys() for key in ("ticket_id", "email_id")):
            logger.error(f"Cannot link ticket to email using {json.dumps(payload)}. JSON malformed")

            response["body"] = 'You must include "ticket_id" and "email_id" in the "body" field of the request'
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        ticket_id = payload["body"]["ticket_id"]
        email_id = payload["body"]["email_id"]

        logger.info(f"Linking ticket {ticket_id} to email {email_id}...")

        result = await self._bruin_repository.link_ticket_to_email(ticket_id, email_id)

        response["body"] = result["body"]
        response["status"] = result["status"]
        logger.info(f"Ticket {ticket_id} successfully posted to email_id:{email_id} ")

        await msg.respond(to_json_bytes(response))
