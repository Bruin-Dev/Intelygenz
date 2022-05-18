from unittest.mock import Mock, ANY

import pytest
from asynctest import CoroutineMock

from application.actions.get_asset_topics import *
from application.clients.bruin_session import BruinResponse


class TestGetAssetTopics:
    @pytest.mark.asyncio
    async def get_asset_topics_ok_test(self, get_asset_topics, mocked_response, event_bus):
        # When
        await get_asset_topics.get_asset_topics({
            "request_id": "any_request_id",
            "response_topic": "any_response_topic",
            "body": {
                "client_id": 321,
                "service_number": "VC1234567",
            }
        })

        # Then
        event_bus.publish_message.assert_awaited_once_with("any_response_topic", {
            "request_id": "any_request_id",
            "status": mocked_response.status,
            "body": mocked_response.body
        })

    @pytest.mark.asyncio
    async def get_asset_topics_without_body_test(self, get_asset_topics, event_bus):
        # When
        await get_asset_topics.get_asset_topics({
            "request_id": "any",
            "response_topic": "any",
        })

        # Then
        event_bus.publish_message.assert_awaited_once_with(ANY, {
            "request_id": ANY,
            "status": 400,
            "body": NO_BODY_MSG
        })

    @pytest.mark.asyncio
    async def get_asset_topics_without_client_id_test(self, get_asset_topics, event_bus):
        # When
        await get_asset_topics.get_asset_topics({
            "request_id": "any",
            "response_topic": "any",
            "body": {
                "service_number": "VC1234567",
            }
        })

        # Then
        event_bus.publish_message.assert_awaited_once_with(ANY, {
            "request_id": ANY,
            "status": 400,
            "body": MISSING_PARAMS_MSG
        })

    @pytest.mark.asyncio
    async def get_asset_topics_without_service_number_test(self, get_asset_topics, event_bus):
        # When
        await get_asset_topics.get_asset_topics({
            "request_id": "any",
            "response_topic": "any",
            "body": {
                "client_id": 123,
            }
        })

        # Then
        event_bus.publish_message.assert_awaited_once_with(ANY, {
            "request_id": ANY,
            "status": 400,
            "body": MISSING_PARAMS_MSG
        })

    @pytest.mark.asyncio
    async def get_asset_topics_with_string_client_id_test(self, get_asset_topics, event_bus):
        # When
        await get_asset_topics.get_asset_topics({
            "request_id": "any",
            "response_topic": "any",
            "body": {
                "client_id": "a_string",
                "service_number": "VC1234567",
            }
        })

        # Then
        event_bus.publish_message.assert_awaited_once_with(ANY, {
            "request_id": ANY,
            "status": 400,
            "body": WRONG_CLIENT_ID_MSG
        })

    @pytest.mark.asyncio
    async def get_asset_topics_with_empty_service_number_test(self, get_asset_topics, event_bus):
        # When
        await get_asset_topics.get_asset_topics({
            "request_id": "any",
            "response_topic": "any",
            "body": {
                "client_id": 1234,
                "service_number": "",
            }
        })

        # Then
        event_bus.publish_message.assert_awaited_once_with(ANY, {
            "request_id": ANY,
            "status": 400,
            "body": EMPTY_SERVICE_NUMBER_MSG
        })


#
# Fixtures
#

@pytest.fixture
def get_asset_topics(mocked_response, event_bus):
    logger = Mock()
    bruin_repository = Mock()
    bruin_repository.get_asset_topics = CoroutineMock(return_value=mocked_response)
    return GetAssetTopics(logger, event_bus, bruin_repository)


@pytest.fixture
def event_bus():
    event_bus = Mock()
    event_bus.publish_message = CoroutineMock()
    return event_bus


@pytest.fixture
def mocked_response():
    return BruinResponse(
        status=200,
        body={
            "callTypes": [
                {
                    "callType": "CHG",
                    "callTypeDescription": "Service Changes",
                    "category": "053",
                    "categoryDescription": "Add Additional Lines"
                },
            ]
        }
    )
