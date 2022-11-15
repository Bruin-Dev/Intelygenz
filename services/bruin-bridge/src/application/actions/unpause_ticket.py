import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class UnpauseTicket:
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
        serial_number = body.get("service_number")
        detail_id = body.get("detail_id")

        if not ticket_id or (not serial_number and not detail_id):
            logger.error(f"Cannot unpause a ticket using {json.dumps(payload)}. JSON malformed")
            response["body"] = "You must include ticket_id and service_number or detail_id in the request"
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        logger.info(
            f"Unpause the ticket for ticket id: {ticket_id}, "
            f"serial number: {serial_number} and detail id: {detail_id}"
        )
        result = await self._bruin_repository.unpause_ticket(ticket_id, serial_number, detail_id)

        response["body"] = result["body"]
        response["status"] = result["status"]

        logger.info(
            f"Response from unpause: {response} to the ticket with ticket id: {ticket_id}, "
            f"serial number: {serial_number} and detail id {detail_id}"
        )

        await msg.respond(to_json_bytes(response))
