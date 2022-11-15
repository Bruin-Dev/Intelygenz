import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

missing = object()

logger = logging.getLogger(__name__)


class GetSingleTicketBasicInfo:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response_msg = {"body": None, "status": None}

        bruin_payload: dict = payload.get("body", missing)
        if bruin_payload is missing:
            logger.error(f"Cannot get tickets basic info using {json.dumps(payload)}. JSON malformed")
            response_msg["body"] = 'Must include "body" in the request message'
            response_msg["status"] = 400

            await msg.respond(to_json_bytes(response_msg))
            return

        ticket_id: int = bruin_payload.pop("ticket_id", missing)

        if ticket_id is missing:
            logger.error(f"Cannot get tickets basic info using {json.dumps(payload)}. Need a TicketId to keep going.")
            response_msg["body"] = f'Must specify "ticket_id" in the body of the request'
            response_msg["status"] = 400

            await msg.respond(to_json_bytes(response_msg))
            return

        logger.info(f"Fetching basic info for ticket {ticket_id}")

        tickets_basic_info: dict = await self._bruin_repository.get_single_ticket_basic_info(ticket_id)

        response_msg["body"] = tickets_basic_info["body"]
        response_msg["status"] = tickets_basic_info["status"]

        logger.info(f"Publishing ticket data to the event bus...")
        await msg.respond(to_json_bytes(response_msg))
