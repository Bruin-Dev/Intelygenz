import json
import logging

from nats.aio.msg import Msg

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class ResolveTicket:
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

        if body.get("ticket_id") and body.get("detail_id"):
            ticket_id = body["ticket_id"]
            detail_id = body["detail_id"]

            logger.info(f"Updating the ticket status for ticket id: {ticket_id} to RESOLVED")
            result = await self._bruin_repository.resolve_ticket(ticket_id, detail_id)

            response["body"] = result["body"]
            response["status"] = result["status"]
        else:
            logger.error(f"Cannot resolve a ticket using {json.dumps(payload)}. JSON malformed")

            response["body"] = "You must include ticket_id and detail_id in the request"
            response["status"] = 400

        await msg.respond(to_json_bytes(response))
