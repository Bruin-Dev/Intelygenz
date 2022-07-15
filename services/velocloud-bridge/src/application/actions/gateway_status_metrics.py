from http import HTTPStatus
from logging import Logger
from typing import List

from application.repositories.velocloud_repository import VelocloudRepository
from dataclasses import dataclass
from igz.packages.eventbus.eventbus import EventBus
from pydantic import BaseModel, ValidationError


class GatewayStatusMetricsMessageBody(BaseModel):
    host: str
    gateway_id: int
    interval: dict
    metrics: List[str]


@dataclass
class GatewayStatusMetrics:
    _event_bus: EventBus
    _velocloud_repository: VelocloudRepository
    _logger: Logger

    async def get_gateway_status_metrics(self, msg: dict):
        try:
            message_body = GatewayStatusMetricsMessageBody.parse_obj(msg.get("body"))
        except ValidationError as e:
            self._logger.warning(f"Wrong request message: msg={msg}, validation_error={e}")
            await self._event_bus.publish_message(
                msg["response_topic"],
                {"request_id": msg["request_id"], "status": HTTPStatus.BAD_REQUEST, "body": e.errors()},
            )
            return

        gateway_status_metrics_response = {"request_id": msg["request_id"], "body": None, "status": None}

        host = message_body.host
        gateway_id = message_body.gateway_id
        interval = message_body.interval
        metrics = message_body.metrics

        self._logger.info("Getting gateway status metrics")
        gateway_status_metrics = await self._velocloud_repository.get_gateway_status_metrics(
            host, gateway_id, interval, metrics
        )
        gateway_status_metrics_response["body"] = gateway_status_metrics["body"]
        gateway_status_metrics_response["status"] = gateway_status_metrics["status"]

        await self._event_bus.publish_message(msg["response_topic"], gateway_status_metrics_response)
        self._logger.info(f"Sent network gateway metrics for gateway {gateway_id} on host {host}")
