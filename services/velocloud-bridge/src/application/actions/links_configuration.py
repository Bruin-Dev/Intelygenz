import json
import logging

from nats.aio.msg import Msg

from ..repositories.velocloud_repository import VelocloudRepository

logger = logging.getLogger(__name__)


class LinksConfiguration:
    def __init__(self, velocloud_repository: VelocloudRepository):
        self._velocloud_repository = velocloud_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        if payload.get("body") is None:
            logger.error(f"Cannot get links configuration with {json.dumps(payload)}. JSON malformed")

            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await msg.respond(json.dumps(response).encode())
            return

        if not all(key in payload["body"].keys() for key in ("host", "enterprise_id", "edge_id")):
            logger.error(
                f'Cannot get links configuration with {json.dumps(payload)}. Need parameters "host", "enterprise_id" '
                f'and "edge_id"'
            )

            response["status"] = 400
            response["body"] = 'You must specify {..."body": {"host", "enterprise_id", "edge_id"}...} in the request'
            await msg.respond(json.dumps(response).encode())
            return

        edge_full_id = payload["body"]

        logger.info(f"Getting links configuration for edge {edge_full_id}...")
        config_response = await self._velocloud_repository.get_links_configuration(edge_full_id=edge_full_id)
        response["status"] = config_response["status"]
        response["body"] = config_response["body"]

        await msg.respond(json.dumps(response).encode())
        logger.info(f"Published links configuration for edge {edge_full_id}")
