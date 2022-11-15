from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.get_management_status import GetManagementStatus
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestGetManagementStatus:
    def instance_test(self):
        bruin_repository = Mock()

        get_management_status = GetManagementStatus(bruin_repository)

        assert get_management_status._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_management_status_ok_test(self):
        bruin_repository = Mock()

        management_status = {"body": "Active – Platinum Monitoring", "status": 200}
        bruin_repository.get_management_status = AsyncMock(return_value=management_status)

        filters = {"client_id": 9994, "status": "A", "service_number": "VC05400009999"}

        event_bus_request = {"body": filters}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {"body": management_status["body"], "status": 200}

        get_management_status = GetManagementStatus(bruin_repository)
        await get_management_status(request_msg)
        bruin_repository.get_management_status.assert_awaited_once_with(filters)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def get_management_status_no_filters_test(self):
        bruin_repository = Mock()

        bruin_repository.get_management_status = AsyncMock()

        event_bus_request = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            "body": 'You must specify {.."body":{"client_id", "status", "service_number"}...} in the request',
            "status": 400,
        }

        get_management_status = GetManagementStatus(bruin_repository)
        await get_management_status(request_msg)
        bruin_repository.get_management_status.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def get_management_status_filters_incomplete_test(self):
        bruin_repository = Mock()

        bruin_repository.get_management_status = AsyncMock()

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

        get_management_status = GetManagementStatus(bruin_repository)
        await get_management_status(request_msg)
        bruin_repository.get_management_status.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))
