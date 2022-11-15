import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class GetSite:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}
        if "body" not in payload.keys():
            logger.error(f"Cannot get bruin site using {json.dumps(payload)}. JSON malformed")
            response["status"] = 400
            response["body"] = "You must specify " '{.."body":{"client_id":...}} in the request'
            await msg.respond(to_json_bytes(response))
            return

        filters = payload["body"]

        if "client_id" not in filters.keys():
            logger.error(f'Cannot get bruin site using {json.dumps(filters)}. Need "client_id"')
            response["status"] = 400
            response["body"] = 'You must specify "client_id" in the body'
            await msg.respond(to_json_bytes(response))
            return

        if "site_id" not in filters.keys():
            logger.error(f'Cannot get bruin site using {json.dumps(filters)}. Need "site_id"')
            response["status"] = 400
            response["body"] = 'You must specify "site_id" in the body'
            await msg.respond(to_json_bytes(response))
            return

        logger.info(f"Getting Bruin site with filters: {json.dumps(filters)}")

        site = await self._bruin_repository.get_site(filters)

        response["body"] = site["body"]
        response["status"] = site["status"]

        await msg.respond(to_json_bytes(response))
        logger.info(
            f"Bruin get_site published in event bus for request {json.dumps(payload)}. Message published was {response}"
        )
