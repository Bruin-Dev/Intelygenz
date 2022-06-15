import json
from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from ...application.actions.edge_events_for_alert import EventEdgesForAlert
from ...application.repositories.velocloud_repository import VelocloudRepository


@pytest.fixture(scope="function")
def velocloud_repository():
    return Mock(spec_set=VelocloudRepository)


@pytest.fixture(scope="function")
def action(velocloud_repository):
    return EventEdgesForAlert(velocloud_repository=velocloud_repository)


@pytest.fixture(scope="function")
def any_msg():
    return Mock(spec_set=Msg)


@pytest.fixture(scope="function")
def any_payload():
    payload = {
        "body": {
            "edge": {"host": "any_host", "enterprise_id": hash("any_id"), "edge_id": hash("any_id")},
            "start_date": "any_date",
            "end_date": "any_date",
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
        "body": 'Must include "edge", "start_date", "end_date" in request body',
        "status": 400,
    }


async def ok_all_optional_filters_filled_in_test(action, any_msg, any_payload, any_response):
    # Given
    action._velocloud_repository.get_all_edge_events = AsyncMock(return_value=any_response)

    payload_json = json.loads(any_payload)
    payload_json["body"]["filter"] = ["any_filter"]
    payload_json["body"]["limit"] = hash("any_limit")

    any_msg.data = json.dumps(payload_json).encode()

    # When
    await action(any_msg)

    # Then
    action._velocloud_repository.get_all_edge_events.assert_awaited_once_with(
        edge=payload_json["body"]["edge"],
        start=payload_json["body"]["start_date"],
        end=payload_json["body"]["end_date"],
        filter_events_status_list=payload_json["body"]["filter"],
        limit=payload_json["body"]["limit"],
    )
    any_msg.respond.assert_awaited_once_with(json.dumps(any_response).encode())


async def ok_no_optional_filters_filled_in_test(action, any_msg, any_payload, any_response):
    # Given
    action._velocloud_repository.get_all_edge_events = AsyncMock(return_value=any_response)

    any_msg.data = any_payload

    payload_json = json.loads(any_payload)

    # When
    await action(any_msg)

    # Then
    action._velocloud_repository.get_all_edge_events.assert_awaited_once_with(
        edge=payload_json["body"]["edge"],
        start=payload_json["body"]["start_date"],
        end=payload_json["body"]["end_date"],
        filter_events_status_list=None,
        limit=None,
    )
    any_msg.respond.assert_awaited_once_with(json.dumps(any_response).encode())


async def ko_body_missing_in_request_test(action, any_msg, no_body_response):
    # Given
    action._velocloud_repository.get_all_edge_events = AsyncMock()

    any_msg.data = b"{}"

    # When
    await action(any_msg)

    # Then
    action._velocloud_repository.get_all_edge_events.assert_not_awaited()
    any_msg.respond.assert_awaited_once_with(json.dumps(no_body_response).encode())


async def ko_filters_missing_in_request_test(action, any_msg, missing_filters_response):
    # Given
    action._velocloud_repository.get_all_edge_events = AsyncMock()

    any_msg.data = b'{"body": {}}'

    # When
    await action(any_msg)

    # Then
    action._velocloud_repository.get_all_edge_events.assert_not_awaited()
    any_msg.respond.assert_awaited_once_with(json.dumps(missing_filters_response).encode())
