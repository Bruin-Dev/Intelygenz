import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class GetCircuitID:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}
        if "body" not in payload.keys():
            logger.error(f"Cannot get bruin circuit id using {json.dumps(payload)}. JSON malformed")
            response["status"] = 400
            response["body"] = "You must specify " '{.."body":{"circuit_id"}...} in the request'
            await msg.respond(to_json_bytes(response))
            return

        params = payload["body"]

        if "circuit_id" not in params.keys():
            logger.error(f'Cannot get bruin circuit id using {json.dumps(params)}. Need "circuit_id"')
            response["status"] = 400
            response["body"] = 'You must specify "circuit_id" in the body'
            await msg.respond(to_json_bytes(response))
            return

        logger.info(f"Getting Bruin circuit ID with filters: {json.dumps(params)}")

        circuit_id = await self._bruin_repository.get_circuit_id(params)

        response["body"] = circuit_id["body"]
        response["status"] = circuit_id["status"]

        await msg.respond(to_json_bytes(response))
        logger.info(
            f"Bruin circuit ID published in event bus for request {json.dumps(payload)}. "
            f"Message published was {response}"
        )
