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
            'management_status': management_status["body"],
            'status': 200
        }

        get_management_status = GetManagementStatus(logger, event_bus, bruin_repository)
        await get_management_status.get_management_status(event_bus_request)
        bruin_repository.get_management_status.assert_called_once_with(filters)
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.info.called

    @pytest.mark.asyncio
    async def get_management_status_no_client_id_ko_test(self):
        logger = Mock()
        logger.error = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        management_status = None

        filters = {}

        event_bus_request = {
            "request_id": 19,
            "filters": filters,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            "management_status": management_status,
            "error_message": 'You must specify "client_id", "status", "service_number" in the filter',
            "status": 400
        }

        get_management_status = GetManagementStatus(logger, event_bus, bruin_repository)
        await get_management_status.get_management_status(event_bus_request)
        bruin_repository.get_management_status.assert_not_called()
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.info.called

    @pytest.mark.asyncio
    async def get_management_status_400_status_ko_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        management_status = {
            "status_code": 400,
            "body": "empty"

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
            'management_status': None,
            'error_message': 'Bad request when retrieving management status: empty',
            'status': 400
        }

        get_management_status = GetManagementStatus(logger, event_bus, bruin_repository)
        await get_management_status.get_management_status(event_bus_request)
        bruin_repository.get_management_status.assert_called_once_with(filters)
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.info.called

    @pytest.mark.asyncio
    async def get_management_status_400_no_filter_status_ko_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        management_status = 400
        bruin_repository.get_management_status = Mock(return_value=management_status)

        event_bus_request = {
            "request_id": 19,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'management_status': None,
            'error_message': 'You must specify '
                             '{.."filter":{"client_id", "status", "service_number"}...} in the request',
            'status': 400
        }

        get_management_status = GetManagementStatus(logger, event_bus, bruin_repository)
        await get_management_status.get_management_status(event_bus_request)
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.error.called

    @pytest.mark.asyncio
    async def get_management_status_401_in_response_from_bruin_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        management_status = {
            "body": {},
            "status_code": 401
        }
        bruin_repository.get_management_status = Mock(return_value=management_status)

        event_bus_request = {
            "request_id": 19,
            "filters": {
                "client_id": 12345,
                "status": "A",
                "service_number": "VC9876"
            },
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'management_status': None,
            'error_message': "Authentication error in bruin API.",
            'status': 400
        }

        get_management_status = GetManagementStatus(logger, event_bus, bruin_repository)
        await get_management_status.get_management_status(event_bus_request)
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.error.called

    @pytest.mark.asyncio
    async def get_management_status_500_in_response_from_bruin_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        management_status = {
            "body": {},
            "status_code": 500
        }
        bruin_repository.get_management_status = Mock(return_value=management_status)

        event_bus_request = {
            "request_id": 19,
            "filters": {
                "client_id": 12345,
                "status": "A",
                "service_number": "VC9876"
            },
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'management_status': None,
            'error_message': "Internal server error from bruin API",
            'status': 500
        }

        get_management_status = GetManagementStatus(logger, event_bus, bruin_repository)
        await get_management_status.get_management_status(event_bus_request)
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.error.called
