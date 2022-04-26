from unittest.mock import Mock

import pytest
from asynctest import CoroutineMock

from application.actions.get_service_number_topics import *
from application.clients.bruin_session import BruinResponse


class TestGetServiceNumberTopics:
    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        get_service_number_topics = GetServiceNumberTopics(logger, event_bus, bruin_repository)

        assert get_service_number_topics._logger is logger
        assert get_service_number_topics._event_bus is event_bus
        assert get_service_number_topics._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_service_number_topics_ok_test(
        self, get_service_number_topics, mocked_response, event_bus, a_request_id, a_request_topic
    ):
        # When
        await get_service_number_topics.get_service_number_topics({
            "request_id": a_request_id,
            "response_topic": a_request_topic,
            "body": {
                "client_id": 321,
                "service_number": "VC1234567",
            }
        })

        # Then
        event_bus.publish_message.assert_awaited_once_with(a_request_topic, {
            "request_id": a_request_id,
            "status": mocked_response.status,
            "body": mocked_response.body
        })

    @pytest.mark.asyncio
    async def get_service_number_topics_without_body_test(
        self, get_service_number_topics, event_bus, a_request_id, a_request_topic
    ):
        # When
        await get_service_number_topics.get_service_number_topics({
            "request_id": a_request_id,
            "response_topic": a_request_topic,
        })

        # Then
        event_bus.publish_message.assert_awaited_once_with(a_request_topic, {
            "request_id": a_request_id,
            "status": 400,
            "body": NO_BODY_MSG
        })

    @pytest.mark.asyncio
    async def get_service_number_topics_without_client_id_test(
        self, get_service_number_topics, event_bus, a_request_id, a_request_topic
    ):
        # When
        await get_service_number_topics.get_service_number_topics({
            "request_id": a_request_id,
            "response_topic": a_request_topic,
            "body": {
                "service_number": "VC1234567",
            }
        })

        # Then
        event_bus.publish_message.assert_awaited_once_with(a_request_topic, {
            "request_id": a_request_id,
            "status": 400,
            "body": MISSING_PARAMS_MSG
        })

    @pytest.mark.asyncio
    async def get_service_number_topics_without_service_number_test(
        self, get_service_number_topics, event_bus, a_request_id, a_request_topic
    ):
        # When
        await get_service_number_topics.get_service_number_topics({
            "request_id": a_request_id,
            "response_topic": a_request_topic,
            "body": {
                "client_id": 123,
            }
        })

        # Then
        event_bus.publish_message.assert_awaited_once_with(a_request_topic, {
            "request_id": a_request_id,
            "status": 400,
            "body": MISSING_PARAMS_MSG
        })

    @pytest.mark.asyncio
    async def get_service_number_topics_with_string_client_id_test(
        self, get_service_number_topics, event_bus, a_request_id, a_request_topic
    ):
        # When
        await get_service_number_topics.get_service_number_topics({
            "request_id": a_request_id,
            "response_topic": a_request_topic,
            "body": {
                "client_id": "a_string",
                "service_number": "VC1234567",
            }
        })

        # Then
        event_bus.publish_message.assert_awaited_once_with(a_request_topic, {
            "request_id": a_request_id,
            "status": 400,
            "body": WRONG_CLIENT_ID_MSG
        })

    @pytest.mark.asyncio
    async def get_service_number_topics_with_empty_service_number_test(
        self, get_service_number_topics, event_bus, a_request_id, a_request_topic
    ):
        # When
        await get_service_number_topics.get_service_number_topics({
            "request_id": a_request_id,
            "response_topic": a_request_topic,
            "body": {
                "client_id": 1234,
                "service_number": "",
            }
        })

        # Then
        event_bus.publish_message.assert_awaited_once_with(a_request_topic, {
            "request_id": a_request_id,
            "status": 400,
            "body": EMPTY_SERVICE_NUMBER_MSG
        })


#
# Fixtures
#

@pytest.fixture
def a_request_id():
    return 1


@pytest.fixture
def a_request_topic():
    return "request.topic"


@pytest.fixture
def get_service_number_topics(mocked_response, event_bus):
    logger = Mock()
    bruin_repository = Mock()
    bruin_repository.get_service_number_topics = CoroutineMock(return_value=mocked_response)
    return GetServiceNumberTopics(logger, event_bus, bruin_repository)


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
