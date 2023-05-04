import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class CloseTicket:
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

        ticket_id = body.get("ticket_id")
        close_note = body.get("close_note")

        if not ticket_id or not close_note:
            logger.error(f"Cannot close a ticket using {json.dumps(payload)}. JSON malformed")
            response["body"] = "You must include ticket_id and close_note in the request"
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        logger.info(f"Closing ticket id: {ticket_id}")
        result = await self._bruin_repository.close_ticket(ticket_id, close_note)

        response["body"] = result["body"]
        response["status"] = result["status"]

        await msg.respond(to_json_bytes(response))
