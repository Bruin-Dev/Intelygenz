from unittest.mock import Mock

import pytest
from asynctest import CoroutineMock

from application.actions.get_client_info_by_did import GetClientInfoByDID


class TestGetClientInfoByDID:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        get_client_info_by_did = GetClientInfoByDID(logger, event_bus, bruin_repository)

        assert get_client_info_by_did._logger is logger
        assert get_client_info_by_did._event_bus is event_bus
        assert get_client_info_by_did._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_client_info_by_did_ok_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        response = {
            "body": {
                "inventoryId": 12345678,
                "clientId": 87654,
                "clientName": "Test Client",
                "btn": "9876543210"
            },
            "status": 200
        }
        bruin_repository.get_client_info_by_did = CoroutineMock(return_value=response)

        body = {
            "did": "+14159999999"
        }

        event_bus_request = {
            "request_id": 1,
            "body": body,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 1,
            **response,
        }

        get_client_info_by_did = GetClientInfoByDID(logger, event_bus, bruin_repository)
        await get_client_info_by_did.get_client_info_by_did(event_bus_request)
        bruin_repository.get_client_info_by_did.assert_awaited_once_with(body["did"])
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.info.called

    @pytest.mark.asyncio
    async def get_client_info_by_did_no_body_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_client_info_by_did = CoroutineMock()

        event_bus_request = {
            "request_id": 1,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 1,
            'body': 'You must specify '
                    '{.."body":{"did":...}} in the request',
            'status': 400
        }

        get_client_info_by_did = GetClientInfoByDID(logger, event_bus, bruin_repository)
        await get_client_info_by_did.get_client_info_by_did(event_bus_request)
        bruin_repository.get_client_info_by_did.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.error.called

    @pytest.mark.asyncio
    async def get_client_info_by_did_incomplete_body_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_client_info_by_did = CoroutineMock()

        event_bus_request = {
            "request_id": 1,
            "body": {},
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 1,
            'body': 'You must specify "did" in the body',
            'status': 400
        }

        get_client_info_by_did = GetClientInfoByDID(logger, event_bus, bruin_repository)
        await get_client_info_by_did.get_client_info_by_did(event_bus_request)
        bruin_repository.get_client_info_by_did.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.error.called
