from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.get_client_info import GetClientInfo
from application.repositories.utils_repository import to_json_bytes


class TestGetClientInfo:
    def instance_test(self):
        bruin_repository = Mock()

        get_client_info = GetClientInfo(bruin_repository)

        assert get_client_info._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_client_info_ok_test(self):
        bruin_repository = Mock()

        client_info = {"body": {"client_id": 1919, "client_name": "Tet Corp"}, "status": 200}
        bruin_repository.get_client_info = AsyncMock(return_value=client_info)

        filters = {"service_number": "VC05400009999"}

        event_bus_request = {"body": filters}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            **client_info,
        }

        get_client_info = GetClientInfo(bruin_repository)
        await get_client_info(request_msg)
        bruin_repository.get_client_info.assert_awaited_once_with(filters)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def get_client_info_no_filters_test(self):
        bruin_repository = Mock()
        bruin_repository.get_client_info = AsyncMock()

        event_bus_request = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            "body": "You must specify " '{.."body":{"service_number":...}} in the request',
            "status": 400,
        }

        get_client_info = GetClientInfo(bruin_repository)
        await get_client_info(request_msg)
        bruin_repository.get_client_info.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def get_client_info_incomplete_filters_test(self):
        bruin_repository = Mock()
        bruin_repository.get_client_info = AsyncMock()

        event_bus_request = {"body": {}}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {"body": 'You must specify "service_number" in the body', "status": 400}

        get_client_info = GetClientInfo(bruin_repository)
        await get_client_info(request_msg)
        bruin_repository.get_client_info.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))
