import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

missing = object()

logger = logging.getLogger(__name__)


class GetTicketsBasicInfo:
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

        ticket_statuses: list = bruin_payload.pop("ticket_statuses", missing)
        if ticket_statuses is missing:
            logger.error(
                f"Cannot get tickets basic info using {json.dumps(payload)}. Need a list of ticket statuses to keep "
                f"going."
            )
            response_msg["body"] = f'Must specify "ticket_statuses" in the body of the request'
            response_msg["status"] = 400

            await msg.respond(to_json_bytes(response_msg))
            return

        logger.info(
            f'Fetching basic info of all tickets with statuses {", ".join(ticket_statuses)} and matching filters '
            f"{json.dumps(bruin_payload)}..."
        )
        tickets_basic_info: dict = await self._bruin_repository.get_tickets_basic_info(bruin_payload, ticket_statuses)

        response_msg["body"] = tickets_basic_info["body"]
        response_msg["status"] = tickets_basic_info["status"]

        logger.info(f'Publishing {len(response_msg["body"])} tickets to the event bus...')
        await msg.respond(to_json_bytes(response_msg))
