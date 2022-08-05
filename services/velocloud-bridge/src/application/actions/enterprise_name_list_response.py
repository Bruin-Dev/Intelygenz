import json
import logging

from nats.aio.msg import Msg

from ..repositories.velocloud_repository import VelocloudRepository

logger = logging.getLogger(__name__)


class EnterpriseNameList:
    def __init__(self, velocloud_repository: VelocloudRepository):
        self._velocloud_repository = velocloud_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        if payload.get("body") is None:
            logger.error(f"Cannot get enterprise names with {json.dumps(payload)}. JSON malformed")

            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await msg.respond(json.dumps(response).encode())
            return

        logger.info("Sending enterprise name list")
        enterprise_names = await self._velocloud_repository.get_all_enterprise_names(msg=payload["body"])

        response["body"] = enterprise_names["body"]
        response["status"] = enterprise_names["status"]

        await msg.respond(json.dumps(response).encode())
        logger.info("Enterprise name list sent")
