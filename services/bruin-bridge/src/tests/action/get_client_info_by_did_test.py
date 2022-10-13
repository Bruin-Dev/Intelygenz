from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.get_client_info_by_did import GetClientInfoByDID
from application.repositories.utils_repository import to_json_bytes


class TestGetClientInfoByDID:
    def instance_test(self):
        bruin_repository = Mock()

        get_client_info_by_did = GetClientInfoByDID(bruin_repository)

        assert get_client_info_by_did._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_client_info_by_did_ok_test(self):
        bruin_repository = Mock()

        response = {
            "body": {"inventoryId": 12345678, "clientId": 87654, "clientName": "Test Client", "btn": "9876543210"},
            "status": 200,
        }
        bruin_repository.get_client_info_by_did = AsyncMock(return_value=response)

        body = {"did": "+14159999999"}

        event_bus_request = {"body": body}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            **response,
        }

        get_client_info_by_did = GetClientInfoByDID(bruin_repository)
        await get_client_info_by_did(request_msg)
        bruin_repository.get_client_info_by_did.assert_awaited_once_with(body["did"])
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def get_client_info_by_did_no_body_test(self):
        bruin_repository = Mock()
        bruin_repository.get_client_info_by_did = AsyncMock()

        event_bus_request = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            "body": "You must specify " '{.."body":{"did":...}} in the request',
            "status": 400,
        }

        get_client_info_by_did = GetClientInfoByDID(bruin_repository)
        await get_client_info_by_did(request_msg)
        bruin_repository.get_client_info_by_did.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def get_client_info_by_did_incomplete_body_test(self):
        bruin_repository = Mock()
        bruin_repository.get_client_info_by_did = AsyncMock()

        event_bus_request = {"body": {}}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {"body": 'You must specify "did" in the body', "status": 400}

        get_client_info_by_did = GetClientInfoByDID(bruin_repository)
        await get_client_info_by_did(request_msg)
        bruin_repository.get_client_info_by_did.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))
