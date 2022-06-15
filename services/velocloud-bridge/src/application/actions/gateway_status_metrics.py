import json
import logging
from dataclasses import dataclass
from http import HTTPStatus

from nats.aio.msg import Msg
from pydantic import BaseModel, ValidationError

from ..repositories.velocloud_repository import VelocloudRepository

logger = logging.getLogger(__name__)


class GatewayStatusMetricsMessageBody(BaseModel):
    host: str
    gateway_id: int
    interval: dict
    metrics: list[str]


@dataclass
class GatewayStatusMetrics:
    _velocloud_repository: VelocloudRepository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        try:
            request_body = GatewayStatusMetricsMessageBody.parse_obj(payload.get("body"))
        except ValidationError as e:
            logger.warning(f"Wrong request message: msg={msg}, validation_error={e}")
            response["body"] = e.errors()
            response["status"] = HTTPStatus.BAD_REQUEST
            await msg.respond(json.dumps(response).encode())
            return

        host = request_body.host
        gateway_id = request_body.gateway_id
        interval = request_body.interval
        metrics = request_body.metrics

        logger.info(f"Getting gateway status metrics for gateway {gateway_id} on host {host} in interval {interval}...")
        gateway_status_metrics = await self._velocloud_repository.get_gateway_status_metrics(
            host=host, gateway_id=gateway_id, interval=interval, metrics=metrics
        )

        response = {
            **gateway_status_metrics,
        }
        await msg.respond(json.dumps(response).encode())
        logger.info(f"Sent gateway status metrics for gateway {gateway_id} on host {host} in interval {interval}")
