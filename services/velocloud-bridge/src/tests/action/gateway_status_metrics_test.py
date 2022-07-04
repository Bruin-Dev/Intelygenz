from unittest.mock import Mock

import pytest
from application.actions.gateway_status_metrics import GatewayStatusMetrics
from asynctest import CoroutineMock
from shortuuid import uuid

uuid_ = uuid()
response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"


class TestGatewayStatusMetrics:
    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        velocloud_repository = Mock()

        action = GatewayStatusMetrics(event_bus, velocloud_repository, logger)

        assert action._event_bus is event_bus
        assert action._logger is logger
        assert action._velocloud_repository is velocloud_repository

    @pytest.mark.asyncio
    async def get_gateway_status_metrics_ok_test(self, gateway_status_metrics_action):
        velocloud_host = "mettel.velocloud.net"
        gateway_id = 1
        interval = {}
        metrics = []

        request = {
            "request_id": uuid_,
            "response_topic": response_topic,
            "body": {
                "host": velocloud_host,
                "gateway_id": gateway_id,
                "interval": interval,
                "metrics": metrics,
            },
        }

        response = {
            "request_id": uuid_,
            "body": {},
            "status": 200,
        }

        gateway_status_metrics_action._velocloud_repository.get_gateway_status_metrics = CoroutineMock(
            return_value=response
        )

        await gateway_status_metrics_action.get_gateway_status_metrics(request)

        gateway_status_metrics_action._velocloud_repository.get_gateway_status_metrics.assert_awaited_once_with(
            velocloud_host, gateway_id, interval, metrics
        )
        gateway_status_metrics_action._event_bus.publish_message.assert_awaited_once_with(response_topic, response)

    @pytest.mark.asyncio
    async def get_gateway_status_metrics_with_missing_body_in_request_test(self, gateway_status_metrics_action):
        request = {
            "request_id": uuid_,
            "response_topic": response_topic,
        }

        await gateway_status_metrics_action.get_gateway_status_metrics(request)

        gateway_status_metrics_action._velocloud_repository.get_gateway_status_metrics.assert_not_awaited()
        gateway_status_metrics_action._event_bus.publish_message.assert_awaited_once()
