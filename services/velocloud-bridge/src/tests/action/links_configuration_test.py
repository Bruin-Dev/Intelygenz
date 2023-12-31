import json
from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from ...application.actions.links_configuration import LinksConfiguration
from ...application.repositories.velocloud_repository import VelocloudRepository


@pytest.fixture(scope="function")
def velocloud_repository():
    return Mock(spec_set=VelocloudRepository)


@pytest.fixture(scope="function")
def action(velocloud_repository):
    return LinksConfiguration(velocloud_repository=velocloud_repository)


@pytest.fixture(scope="function")
def any_msg():
    return Mock(spec_set=Msg)


@pytest.fixture(scope="function")
def any_payload():
    payload = {
        "body": {
            "host": "any_host",
            "enterprise_id": hash("any_id"),
            "edge_id": hash("any_id"),
        }
    }
    return json.dumps(payload).encode()


@pytest.fixture(scope="function")
def any_response():
    return {
        "body": [],
        "status": hash("any_status"),
    }


@pytest.fixture(scope="function")
def no_body_response():
    return {
        "body": 'Must include "body" in request',
        "status": 400,
    }


@pytest.fixture(scope="function")
def missing_filters_response():
    return {
        "body": 'You must specify {..."body": {"host", "enterprise_id", "edge_id"}...} in the request',
        "status": 400,
    }


async def ok_test(action, any_msg, any_payload, any_response):
    # Given
    action._velocloud_repository.get_links_configuration = AsyncMock(return_value=any_response)

    any_msg.data = any_payload

    payload_json = json.loads(any_payload)

    # When
    await action(any_msg)

    # Then
    action._velocloud_repository.get_links_configuration.assert_awaited_once_with(
        edge_full_id=payload_json["body"],
    )
    any_msg.respond.assert_awaited_once_with(json.dumps(any_response).encode())


async def ko_body_missing_in_request_test(action, any_msg, no_body_response):
    # Given
    action._velocloud_repository.get_links_configuration = AsyncMock()

    any_msg.data = b"{}"

    # When
    await action(any_msg)

    # Then
    action._velocloud_repository.get_links_configuration.assert_not_awaited()
    any_msg.respond.assert_awaited_once_with(json.dumps(no_body_response).encode())


async def ko_filters_missing_in_request_test(action, any_msg, missing_filters_response):
    # Given
    action._velocloud_repository.get_links_configuration = AsyncMock()

    any_msg.data = b'{"body": {}}'

    # When
    await action(any_msg)

    # Then
    action._velocloud_repository.get_links_configuration.assert_not_awaited()
    any_msg.respond.assert_awaited_once_with(json.dumps(missing_filters_response).encode())
