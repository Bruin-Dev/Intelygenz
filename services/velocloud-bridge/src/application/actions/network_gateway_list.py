import json
import logging
from http import HTTPStatus

from dataclasses import dataclass
from nats.aio.msg import Msg
from pydantic import BaseModel, ValidationError

from ..repositories.velocloud_repository import VelocloudRepository

logger = logging.getLogger(__name__)


class GatewayMessageBody(BaseModel):
    host: str


@dataclass
class NetworkGatewayList:
    _velocloud_repository: VelocloudRepository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        try:
            request_body = GatewayMessageBody.parse_obj(payload.get("body"))
        except ValidationError as e:
            logger.warning(f"Wrong request message: msg={msg}, validation_error={e}")
            response["body"] = e.errors()
            response["status"] = HTTPStatus.BAD_REQUEST
            await msg.respond(json.dumps(response).encode())
            return

        host = request_body.host

        logger.info(f"Getting network gateway list on host {host}...")
        gateway_list = await self._velocloud_repository.get_network_gateways(host=host)

        response = {
            **gateway_list,
        }
        await msg.respond(json.dumps(response).encode())
        logger.info(f"Sent network gateway list on host {host}")
