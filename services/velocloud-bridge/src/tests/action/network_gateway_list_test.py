import json
from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from ...application.actions.network_gateway_list import NetworkGatewayList
from ...application.repositories.velocloud_repository import VelocloudRepository


@pytest.fixture(scope="function")
def velocloud_repository():
    return Mock(spec_set=VelocloudRepository)


@pytest.fixture(scope="function")
def action(velocloud_repository):
    return NetworkGatewayList(_velocloud_repository=velocloud_repository)


@pytest.fixture(scope="function")
def any_msg():
    return Mock(spec_set=Msg)


@pytest.fixture(scope="function")
def any_payload():
    payload = {
        "body": {
            "host": "any_host",
        }
    }
    return json.dumps(payload).encode()


@pytest.fixture(scope="function")
async def any_response():
    return {
        "body": [{"host": "any_host", "id": hash("any_id"), "name": "any_name"}],
        "status": 200,
    }


@pytest.fixture(scope="function")
def no_body_response():
    return {
        "body": [
            {"loc": ("__root__",), "msg": "GatewayMessageBody expected dict not NoneType", "type": "type_error"},
        ],
        "status": 400,
    }


@pytest.fixture(scope="function")
def missing_filters_response():
    return {
        "body": [
            {"loc": ("host",), "msg": "field required", "type": "value_error.missing"},
        ],
        "status": 400,
    }


async def ok_test(action, any_msg, any_payload, any_response):
    # Given
    action._velocloud_repository.get_network_gateways = AsyncMock(return_value=any_response)

    any_msg.data = any_payload

    payload_json = json.loads(any_payload)

    # When
    await action(any_msg)

    # Then
    action._velocloud_repository.get_network_gateways.assert_awaited_once_with(
        host=payload_json["body"]["host"],
    )
    any_msg.respond.assert_awaited_once_with(json.dumps(any_response).encode())


async def ko_body_missing_in_request_test(action, any_msg, no_body_response):
    # Given
    action._velocloud_repository.get_network_gateways = AsyncMock()

    any_msg.data = b"{}"

    # When
    await action(any_msg)

    # Then
    action._velocloud_repository.get_network_gateways.assert_not_awaited()
    any_msg.respond.assert_awaited_once_with(json.dumps(no_body_response).encode())


async def ko_filters_missing_in_request_test(action, any_msg, missing_filters_response):
    # Given
    action._velocloud_repository.get_network_gateways = AsyncMock()

    any_msg.data = b'{"body": {}}'

    # When
    await action(any_msg)

    # Then
    action._velocloud_repository.get_network_gateways.assert_not_awaited()
    any_msg.respond.assert_awaited_once_with(json.dumps(missing_filters_response).encode())
