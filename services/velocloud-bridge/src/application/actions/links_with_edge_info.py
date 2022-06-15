import json
import logging

from nats.aio.msg import Msg

from ..repositories.velocloud_repository import VelocloudRepository

missing = object()


logger = logging.getLogger(__name__)


class LinksWithEdgeInfo:
    def __init__(self, velocloud_repository: VelocloudRepository):
        self._velocloud_repository = velocloud_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {
            "body": None,
            "status": None,
        }

        request_body: dict = payload.get("body", missing)
        if request_body is missing:
            logger.error(f'Cannot get links with edge info: "body" is missing in the request')
            response["body"] = 'Must include "body" in the request'
            response["status"] = 400
            await msg.respond(json.dumps(response).encode())
            return

        velocloud_host: str = request_body.get("host", missing)
        if velocloud_host is missing:
            logger.error(f'Cannot get links with edge info: "host" is missing in the body of the request')
            response["body"] = 'Must include "host" in the body of the request'
            response["status"] = 400
            await msg.respond(json.dumps(response).encode())
            return

        logger.info(f'Getting links with edge info from Velocloud host "{velocloud_host}"...')
        links_with_edge_info_response: dict = await self._velocloud_repository.get_links_with_edge_info(
            velocloud_host=velocloud_host,
        )

        await msg.respond(json.dumps(links_with_edge_info_response).encode())
        logger.info(f"Response sent for request {payload}")
