import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class GetInventoryAttributes:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        filters = payload.get("body")
        if "body" not in payload.keys():
            logger.error(f"Cannot get inventory attributes using {json.dumps(payload)}. JSON malformed")
            response["status"] = 400
            response["body"] = (
                "You must specify " '{.."body":{"client_id", "status", "service_number"}...} in the request'
            )
            await msg.respond(to_json_bytes(response))
            return

        if not all(key in filters.keys() for key in ("client_id", "status", "service_number")):
            logger.info(
                f"Cannot get inventory attributes using {json.dumps(filters)}. "
                f'Need "client_id", "status", "service_number"'
            )
            response["status"] = 400
            response["body"] = 'You must specify "client_id", "status", "service_number" in the filter'
            await msg.respond(to_json_bytes(response))
            return

        logger.info(f"'Getting inventory attributes with filters: {json.dumps(filters)}'")

        get_inventory_attributes = await self._bruin_repository.get_inventory_attributes(filters)

        response["body"] = get_inventory_attributes["body"]
        response["status"] = get_inventory_attributes["status"]

        await msg.respond(to_json_bytes(response))
        logger.info(
            f"Inventory attributes published in event bus for request {json.dumps(payload)}. "
            f"Message published was {response}"
        )
