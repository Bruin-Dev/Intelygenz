from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.get_attributes_serial import GetAttributeSerial
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestGetAttributeSerial:
    def instance_test(self):
        bruin_repository = Mock()

        get_attributes_serial = GetAttributeSerial(bruin_repository)

        assert get_attributes_serial._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_attributes_serial_ok_test(self):
        bruin_repository = Mock()

        attributes_serial = {"body": "705286", "status": 200}
        bruin_repository.get_attributes_serial = AsyncMock(return_value=attributes_serial)

        filters = {"client_id": 89267, "status": "A", "service_number": "5006950173"}

        event_bus_request = {"body": filters}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {"body": attributes_serial["body"], "status": 200}

        get_attributes_serial = GetAttributeSerial(bruin_repository)
        await get_attributes_serial(request_msg)
        bruin_repository.get_attributes_serial.assert_awaited_once_with(filters)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def get_attributes_serial_no_filters_test(self):
        bruin_repository = Mock()

        bruin_repository.get_attributes_serial = AsyncMock()

        event_bus_request = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            "body": 'You must specify {.."body":{"client_id", "status", "service_number"}...} in the request',
            "status": 400,
        }

        get_attributes_serial = GetAttributeSerial(bruin_repository)
        await get_attributes_serial(request_msg)
        bruin_repository.get_attributes_serial.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def get_attributes_serial_filters_incomplete_test(self):
        bruin_repository = Mock()

        bruin_repository.get_attributes_serial = AsyncMock()

        filters = {
            "client_id": 9994,
            "status": "A",
        }

        event_bus_request = {"body": filters}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            "body": 'You must specify "client_id", "status", "service_number" in the filter',
            "status": 400,
        }

        get_attributes_serial = GetAttributeSerial(bruin_repository)
        await get_attributes_serial(request_msg)
        bruin_repository.get_attributes_serial.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))
