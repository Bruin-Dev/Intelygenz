import json
import logging

from nats.aio.msg import Msg

from ..repositories.velocloud_repository import VelocloudRepository

logger = logging.getLogger(__name__)


class NetworkEnterpriseEdgeList:
    def __init__(self, velocloud_repository: VelocloudRepository):
        self._velocloud_repository = velocloud_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        if payload.get("body") is None:
            logger.error(f"Cannot get network enterprise edge list with {json.dumps(payload)}. JSON malformed")

            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await msg.respond(json.dumps(response).encode())
            return

        if not all(key in payload["body"].keys() for key in ("host", "enterprise_ids")):
            logger.error(
                f'Cannot get network enterprise edge list with {json.dumps(payload)}. Need parameters "host" and '
                f'"enterprise_ids"'
            )

            response["status"] = 400
            response["body"] = 'Must include "host" and "enterprise_ids" in request body'
            await msg.respond(json.dumps(response).encode())
            return

        host = payload["body"]["host"]
        enterprise_ids = payload["body"]["enterprise_ids"]

        logger.info(f"Getting network enterprise edge list for host {host} and enterprises {enterprise_ids}")
        enterprise_edge_list = await self._velocloud_repository.get_network_enterprise_edges(
            host=host,
            enterprise_ids=enterprise_ids,
        )

        response["body"] = enterprise_edge_list["body"]
        response["status"] = enterprise_edge_list["status"]

        await msg.respond(json.dumps(response).encode())
        logger.info(f"Sent list of network enterprises edges for enterprises: {enterprise_ids} and host {host}")
