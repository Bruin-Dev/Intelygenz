import json
from unittest.mock import Mock

import pytest
from application.actions.get_management_status import GetManagementStatus
from asynctest import CoroutineMock


class TestGetManagementStatus:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        get_management_status = GetManagementStatus(logger, event_bus, bruin_repository)

        assert get_management_status._logger is logger
        assert get_management_status._event_bus is event_bus
        assert get_management_status._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_management_status_ok_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        management_status = {
            "body": "Active – Platinum Monitoring",
            "status_code": 200
        }
        bruin_repository.get_management_status = Mock(return_value=management_status)

        filters = {
            "client_id": 9994,
            "status": "A",
            "service_number": "VC05400009999"
        }

        event_bus_request = {
            "request_id": 19,
            "filters": filters,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'body': management_status["body"],
            'status': 200
        }

        get_management_status = GetManagementStatus(logger, event_bus, bruin_repository)
        await get_management_status.get_management_status(event_bus_request)
        bruin_repository.get_management_status.assert_called_once_with(filters)
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.info.called

    @pytest.mark.asyncio
    async def get_management_status_no_filters_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        bruin_repository.get_management_status = Mock()

        event_bus_request = {
            "request_id": 19,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'body': 'You must specify {.."filter":{"client_id", "status", "service_number"}...} in the request',
            'status': 400
        }

        get_management_status = GetManagementStatus(logger, event_bus, bruin_repository)
        await get_management_status.get_management_status(event_bus_request)
        bruin_repository.get_management_status.assert_not_called()
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)

    @pytest.mark.asyncio
    async def get_management_status_filters_incomplete_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        bruin_repository.get_management_status = Mock()

        filters = {
            "client_id": 9994,
            "status": "A",
        }

        event_bus_request = {
            "request_id": 19,
            "filters": filters,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'body': 'You must specify "client_id", "status", "service_number" in the filter',
            'status': 400
        }

        get_management_status = GetManagementStatus(logger, event_bus, bruin_repository)
        await get_management_status.get_management_status(event_bus_request)
        bruin_repository.get_management_status.assert_not_called()
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
