import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class GetClientInfo:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}
        if "body" not in payload.keys():
            logger.error(f"Cannot get bruin client info using {json.dumps(payload)}. JSON malformed")
            response["status"] = 400
            response["body"] = "You must specify " '{.."body":{"service_number":...}} in the request'
            await msg.respond(to_json_bytes(response))
            return

        filters = payload["body"]

        if "service_number" not in filters.keys():
            logger.error(f'Cannot get bruin client info using {json.dumps(filters)}. Need "service_number"')
            response["status"] = 400
            response["body"] = 'You must specify "service_number" in the body'
            await msg.respond(to_json_bytes(response))
            return

        logger.info(f"Getting Bruin client ID with filters: {json.dumps(filters)}")

        client_info = await self._bruin_repository.get_client_info(filters)

        response["body"] = client_info["body"]
        response["status"] = client_info["status"]

        await msg.respond(to_json_bytes(response))
        logger.info(
            f"Bruin client_info published in event bus for request {json.dumps(payload)}. "
            f"Message published was {response}"
        )
