from unittest.mock import Mock

import pytest
from application.actions.network_gateway_list import NetworkGatewayList
from asynctest import CoroutineMock
from shortuuid import uuid

uuid_ = uuid()
response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"


class TestNetworkGatewayList:
    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        velocloud_repository = Mock()

        action = NetworkGatewayList(event_bus, velocloud_repository, logger)

        assert action._event_bus is event_bus
        assert action._logger is logger
        assert action._velocloud_repository is velocloud_repository

    @pytest.mark.asyncio
    async def get_network_gateway_list_ok_test(self, network_gateway_list_action):
        velocloud_host = "mettel.velocloud.net"

        request = {
            "request_id": uuid_,
            "response_topic": response_topic,
            "body": {
                "host": velocloud_host,
            },
        }

        response = {
            "request_id": uuid_,
            "body": [],
            "status": 200,
        }

        network_gateway_list_action._velocloud_repository.get_network_gateways = CoroutineMock(return_value=response)

        await network_gateway_list_action.get_network_gateway_list(request)

        network_gateway_list_action._velocloud_repository.get_network_gateways.assert_awaited_once_with(velocloud_host)
        network_gateway_list_action._event_bus.publish_message.assert_awaited_once_with(response_topic, response)

    @pytest.mark.asyncio
    async def get_network_gateway_list_with_missing_body_in_request_test(self, network_gateway_list_action):
        request = {
            "request_id": uuid_,
            "response_topic": response_topic,
        }

        await network_gateway_list_action.get_network_gateway_list(request)

        network_gateway_list_action._velocloud_repository.get_network_gateways.assert_not_awaited()
        network_gateway_list_action._event_bus.publish_message.assert_awaited_once()
