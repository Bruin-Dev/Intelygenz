from http import HTTPStatus
from logging import Logger

from application.repositories.velocloud_repository import VelocloudRepository
from dataclasses import dataclass
from igz.packages.eventbus.eventbus import EventBus
from pydantic import BaseModel, ValidationError


class GatewayMessageBody(BaseModel):
    host: str


@dataclass
class NetworkGatewayList:
    _event_bus: EventBus
    _velocloud_repository: VelocloudRepository
    _logger: Logger

    async def get_network_gateway_list(self, msg: dict):
        try:
            message_body = GatewayMessageBody.parse_obj(msg.get("body"))
        except ValidationError as e:
            self._logger.warning(f"Wrong request message: msg={msg}, validation_error={e}")
            await self._event_bus.publish_message(
                msg["response_topic"],
                {"request_id": msg["request_id"], "status": HTTPStatus.BAD_REQUEST, "body": e.errors()},
            )
            return

        network_gateway_list_response = {"request_id": msg["request_id"], "body": None, "status": None}

        host = message_body.host

        self._logger.info("Getting network gateway list")
        gateway_list = await self._velocloud_repository.get_network_gateways(host)
        network_gateway_list_response["body"] = gateway_list["body"]
        network_gateway_list_response["status"] = gateway_list["status"]

        await self._event_bus.publish_message(msg["response_topic"], network_gateway_list_response)
        self._logger.info(f"Sent list of network gateways for host {host}")
