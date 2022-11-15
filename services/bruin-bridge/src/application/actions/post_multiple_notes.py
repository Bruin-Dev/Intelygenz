import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class PostMultipleNotes:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        body = payload.get("body")
        if body is None:
            logger.error(f"Cannot post a note to ticket using {json.dumps(payload)}. JSON malformed")
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await msg.respond(to_json_bytes(response))
            return

        if not all(key in body.keys() for key in ("ticket_id", "notes")):
            response["body"] = 'You must include "ticket_id" and "notes" in the body of the request'
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        ticket_id = body["ticket_id"]
        notes = body["notes"]

        for note in notes:
            if "text" not in note.keys() or not any(key in note.keys() for key in ("service_number", "detail_id")):
                response["body"] = (
                    'You must include "text" and any of "service_number" and "detail_id" for every '
                    'note in the "notes" field'
                )
                response["status"] = 400
                await msg.respond(to_json_bytes(response))
                return

        logger.info(f"Posting multiple notes for ticket {ticket_id}...")
        result = await self._bruin_repository.post_multiple_ticket_notes(ticket_id, notes)

        response["body"] = result["body"]
        response["status"] = result["status"]

        await msg.respond(to_json_bytes(response))
