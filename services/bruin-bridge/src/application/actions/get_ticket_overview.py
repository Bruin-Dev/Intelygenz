import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class GetTicketOverview:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        ticket_response = {"body": None, "status": None}
        body = payload.get("body")

        if body is None:
            ticket_response["status"] = 400
            ticket_response["body"] = 'Must include "body" in request'
            await msg.respond(to_json_bytes(ticket_response))
            return

        if "ticket_id" not in body.keys():
            ticket_response["status"] = 400
            ticket_response["body"] = 'Must include "ticket_id" in body'
            await msg.respond(to_json_bytes(ticket_response))
            return

        ticket_id = body["ticket_id"]

        logger.info(f"Getting ticket for ticket_id: {ticket_id}...")

        ticket = await self._bruin_repository.get_ticket_overview(ticket_id)

        logger.info(f"Got ticket overview for ticket id: {ticket_id}...")

        await msg.respond(to_json_bytes(ticket))
