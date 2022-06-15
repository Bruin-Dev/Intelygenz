import json
import logging

from nats.aio.msg import Msg

from ..repositories.velocloud_repository import VelocloudRepository

logger = logging.getLogger(__name__)

missing = object()


class LinksMetricInfo:
    def __init__(self, velocloud_repository: VelocloudRepository):
        self._velocloud_repository = velocloud_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        request_body: dict = payload.get("body", missing)
        if request_body is missing:
            logger.error(f'Cannot get links metric info: "body" is missing in the request')
            response["body"] = 'Must include "body" in the request'
            response["status"] = 400
            await msg.respond(json.dumps(response).encode())
            return

        velocloud_host: str = request_body.get("host", missing)
        if velocloud_host is missing:
            logger.error(f'Cannot get links metric info: "host" is missing in the body of the request')
            response["body"] = 'Must include "host" and "interval" in the body of the request'
            response["status"] = 400
            await msg.respond(json.dumps(response).encode())
            return

        interval: dict = request_body.get("interval", missing)
        if interval is missing:
            logger.error(f'Cannot get links metric info: "interval" is missing in the body of the request')
            response["body"] = 'Must include "host" and "interval" in the body of the request'
            response["status"] = 400
            await msg.respond(json.dumps(response).encode())
            return

        logger.info(f'Getting links metric info from Velocloud host "{velocloud_host}"...')
        links_metric_info_response: dict = await self._velocloud_repository.get_links_metric_info(
            velocloud_host=velocloud_host,
            interval=interval,
        )

        response = {
            **links_metric_info_response,
        }
        await msg.respond(json.dumps(response).encode())
        logger.info(f"Published links metric info for request {payload}")
