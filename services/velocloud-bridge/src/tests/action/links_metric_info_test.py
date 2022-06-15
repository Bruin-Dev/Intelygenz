import json
from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from ...application.actions.links_metric_info import LinksMetricInfo
from ...application.repositories.velocloud_repository import VelocloudRepository


@pytest.fixture(scope="function")
def velocloud_repository():
    return Mock(spec_set=VelocloudRepository)


@pytest.fixture(scope="function")
def action(velocloud_repository):
    return LinksMetricInfo(velocloud_repository=velocloud_repository)


@pytest.fixture(scope="function")
def any_msg():
    return Mock(spec_set=Msg)


@pytest.fixture(scope="function")
def any_payload():
    payload = {
        "body": {
            "host": "any_host",
            "interval": {
                "start": "any_timestamp",
                "end": "any_timestamp",
            },
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
        "body": 'Must include "body" in the request',
        "status": 400,
    }


@pytest.fixture(scope="function")
def missing_filters_response():
    return {
        "body": 'Must include "host" and "interval" in the body of the request',
        "status": 400,
    }


async def ok_test(action, any_msg, any_payload, any_response):
    # Given
    action._velocloud_repository.get_links_metric_info = AsyncMock(return_value=any_response)

    any_msg.data = any_payload

    payload_json = json.loads(any_payload)

    # When
    await action(any_msg)

    # Then
    action._velocloud_repository.get_links_metric_info.assert_awaited_once_with(
        velocloud_host=payload_json["body"]["host"],
        interval=payload_json["body"]["interval"],
    )
    any_msg.respond.assert_awaited_once_with(json.dumps(any_response).encode())


async def ko_body_missing_in_request_test(action, any_msg, no_body_response):
    # Given
    action._velocloud_repository.get_links_metric_info = AsyncMock()

    any_msg.data = b"{}"

    # When
    await action(any_msg)

    # Then
    action._velocloud_repository.get_links_metric_info.assert_not_awaited()
    any_msg.respond.assert_awaited_once_with(json.dumps(no_body_response).encode())


async def ko_host_filter_missing_in_request_test(action, any_msg, missing_filters_response):
    # Given
    action._velocloud_repository.get_links_metric_info = AsyncMock()

    any_msg.data = b'{"body": {"interval": {}}}'

    # When
    await action(any_msg)

    # Then
    action._velocloud_repository.get_links_metric_info.assert_not_awaited()
    any_msg.respond.assert_awaited_once_with(json.dumps(missing_filters_response).encode())


async def ko_interval_filter_missing_in_request_test(action, any_msg, missing_filters_response):
    # Given
    action._velocloud_repository.get_links_metric_info = AsyncMock()

    any_msg.data = b'{"body": {"host": {}}}'

    # When
    await action(any_msg)

    # Then
    action._velocloud_repository.get_links_metric_info.assert_not_awaited()
    any_msg.respond.assert_awaited_once_with(json.dumps(missing_filters_response).encode())
