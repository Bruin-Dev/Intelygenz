import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class PostNote:
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

        if not all(key in body.keys() for key in ("ticket_id", "note")):
            logger.error(f"Cannot post a note to ticket using {json.dumps(payload)}. JSON malformed")

            response["body"] = 'You must include "ticket_id" and "note" in the "body" field of the response request'
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        ticket_id = payload["body"]["ticket_id"]
        note = payload["body"]["note"]

        logger.info(f"Putting note in: {ticket_id}...")

        service_numbers: list = payload["body"].get("service_numbers")
        result = await self._bruin_repository.post_ticket_note(ticket_id, note, service_numbers=service_numbers)

        response["body"] = result["body"]
        response["status"] = result["status"]
        logger.info(f"Note successfully posted to ticketID:{ticket_id} ")

        await msg.respond(to_json_bytes(response))
