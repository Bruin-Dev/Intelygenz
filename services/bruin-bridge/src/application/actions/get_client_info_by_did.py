import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class GetClientInfoByDID:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}
        if "body" not in payload.keys():
            logger.error(f"Cannot get Bruin client info by DID using {json.dumps(payload)}. JSON malformed")
            response["status"] = 400
            response["body"] = "You must specify " '{.."body":{"did":...}} in the request'
            await msg.respond(to_json_bytes(response))
            return

        body = payload["body"]

        if "did" not in body.keys():
            logger.error(f'Cannot get Bruin client info by DID using {json.dumps(body)}. Need "did"')
            response["status"] = 400
            response["body"] = 'You must specify "did" in the body'
            await msg.respond(to_json_bytes(response))
            return

        logger.info(f"Getting Bruin client info by DID with body: {json.dumps(body)}")

        client_info = await self._bruin_repository.get_client_info_by_did(body["did"])

        response["body"] = client_info["body"]
        response["status"] = client_info["status"]

        await msg.respond(to_json_bytes(response))
        logger.info(
            f"Bruin client_info_by_did published in event bus for request {json.dumps(payload)}. "
            f"Message published was {response}"
        )
