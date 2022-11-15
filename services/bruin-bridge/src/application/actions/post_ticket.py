import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class PostTicket:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}
        payload = payload.get("body")

        if payload is None:
            logger.error(f"Cannot create a ticket using {json.dumps(payload)}. JSON malformed")
            response["status"] = 400
            response["body"] = (
                "You must specify " '{.."body":{"clientId", "category", "services", "contacts"}, in the request'
            )
            await msg.respond(to_json_bytes(response))
            return

        if not all(key in payload.keys() for key in ("clientId", "category", "services", "contacts")):
            logger.info(
                f"Cannot create ticket using {json.dumps(payload)}. "
                f'Need "clientId", "category", "services", "contacts"'
            )
            response["status"] = 400
            response["body"] = 'You must specify "clientId", "category", ' '"services", "contacts" in the body'
            await msg.respond(to_json_bytes(response))
            return

        if "notes" not in payload.keys():
            payload["notes"] = []

        logger.info(f'Creating ticket for client id: {payload["clientId"]}...')

        result = await self._bruin_repository.post_ticket(payload)

        response["body"] = result["body"]
        response["status"] = result["status"]
        if response["status"] in range(200, 300):
            logger.info(
                f'Ticket created for client id: {payload["clientId"]} with ticket id:'
                f' {result["body"]["ticketIds"][0]}'
            )
        else:
            logger.error(response["body"])

        await msg.respond(to_json_bytes(response))
