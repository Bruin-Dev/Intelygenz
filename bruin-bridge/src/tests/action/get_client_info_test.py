from unittest.mock import Mock

import pytest
from asynctest import CoroutineMock

from application.actions.get_client_info import GetClientInfo


class TestGetClientInfo:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        get_client_info = GetClientInfo(logger, event_bus, bruin_repository)

        assert get_client_info._logger is logger
        assert get_client_info._event_bus is event_bus
        assert get_client_info._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_client_info_ok_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        client_info = {
            "body": {
                "client_id": 1919,
                "client_name": "Tet Corp"
            },
            "status_code": 200
        }
        bruin_repository.get_client_info = Mock(return_value=client_info)

        filters = {
            "service_number": "VC05400009999"
        }

        event_bus_request = {
            "request_id": 19,
            "body": filters,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'body': client_info["body"],
            'status': client_info["status_code"]
        }

        get_client_info = GetClientInfo(logger, event_bus, bruin_repository)
        await get_client_info.get_client_info(event_bus_request)
        bruin_repository.get_client_info.assert_called_once_with(filters)
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.info.called

    @pytest.mark.asyncio
    async def get_client_info_no_filters_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        event_bus_request = {
            "request_id": 19,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'body': 'You must specify '
                    '{.."body":{"service_number":...}} in the request',
            'status': 400
        }

        get_client_info = GetClientInfo(logger, event_bus, bruin_repository)
        await get_client_info.get_client_info(event_bus_request)
        bruin_repository.get_client_info.assert_not_called
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.error.called

    @pytest.mark.asyncio
    async def get_client_info_incomplete_filters_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        event_bus_request = {
            "request_id": 19,
            "body": {},
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'body': 'You must specify "service_number" in the body',
            'status': 400
        }

        get_client_info = GetClientInfo(logger, event_bus, bruin_repository)
        await get_client_info.get_client_info(event_bus_request)
        bruin_repository.get_client_info.assert_not_called
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.error.called
