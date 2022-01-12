from unittest.mock import Mock

import pytest
from application.actions.get_attributes_serial import GetAttributeSerial
from asynctest import CoroutineMock


class TestGetAttributeSerial:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        get_attributes_serial = GetAttributeSerial(logger, event_bus, bruin_repository)

        assert get_attributes_serial._logger is logger
        assert get_attributes_serial._event_bus is event_bus
        assert get_attributes_serial._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_attributes_serial_ok_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        attributes_serial = {
            "body": "705286",
            "status": 200
        }
        bruin_repository.get_attributes_serial = CoroutineMock(return_value=attributes_serial)

        filters = {
            "client_id": 89267,
            "status": "A",
            "service_number": "5006950173"
        }

        event_bus_request = {
            "request_id": 19,
            "body": filters,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'body': attributes_serial["body"],
            'status': 200
        }

        get_attributes_serial = GetAttributeSerial(logger, event_bus, bruin_repository)
        await get_attributes_serial.get_attributes_serial(event_bus_request)
        bruin_repository.get_attributes_serial.assert_awaited_once_with(filters)
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.info.called

    @pytest.mark.asyncio
    async def get_attributes_serial_no_filters_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        bruin_repository.get_attributes_serial = CoroutineMock()

        event_bus_request = {
            "request_id": 19,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'body': 'You must specify {.."body":{"client_id", "status", "service_number"}...} in the request',
            'status': 400
        }

        get_attributes_serial = GetAttributeSerial(logger, event_bus, bruin_repository)
        await get_attributes_serial.get_attributes_serial(event_bus_request)
        bruin_repository.get_attributes_serial.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)

    @pytest.mark.asyncio
    async def get_attributes_serial_filters_incomplete_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        bruin_repository.get_attributes_serial = CoroutineMock()

        filters = {
            "client_id": 9994,
            "status": "A",
        }

        event_bus_request = {
            "request_id": 19,
            "body": filters,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'body': 'You must specify "client_id", "status", "service_number" in the filter',
            'status': 400
        }

        get_attributes_serial = GetAttributeSerial(logger, event_bus, bruin_repository)
        await get_attributes_serial.get_attributes_serial(event_bus_request)
        bruin_repository.get_attributes_serial.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
