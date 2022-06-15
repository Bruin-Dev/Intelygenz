import json
import logging

from nats.aio.msg import Msg

from ..repositories.velocloud_repository import VelocloudRepository

logger = logging.getLogger(__name__)


class EnterpriseEdgeList:
    def __init__(self, velocloud_repository: VelocloudRepository):
        self._velocloud_repository = velocloud_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        if payload.get("body") is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await msg.respond(json.dumps(response).encode())
            return

        if not all(key in payload["body"].keys() for key in ("host", "enterprise_id")):
            response["status"] = 400
            response["body"] = 'Must include "host" and "enterprise_id" in request "body"'
            await msg.respond(json.dumps(response).encode())
            return

        host = payload["body"]["host"]
        enterprise_id = payload["body"]["enterprise_id"]

        logger.info("Getting enterprise edge list")
        enterprise_edge_list = await self._velocloud_repository.get_enterprise_edges(
            host=host,
            enterprise_id=enterprise_id,
        )

        response["body"] = enterprise_edge_list["body"]
        response["status"] = enterprise_edge_list["status"]

        await msg.respond(json.dumps(response).encode())
        logger.info(f"Sent list of enterprise edges for enterprise {enterprise_id} and host {host}")
