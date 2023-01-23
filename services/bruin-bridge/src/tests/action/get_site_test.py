from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.get_site import GetSite
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestGetSite:
    def instance_test(self):
        bruin_repository = Mock()

        get_site = GetSite(bruin_repository)

        assert get_site._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_site_ok_test(self):
        bruin_repository = Mock()

        client_id = 72959
        site_id = 343443
        params = {"client_id": client_id, "site_id": site_id}
        get_site_response = {"body": {"client_id": client_id, "site_id": site_id}, "status": 200}
        bruin_repository.get_site = AsyncMock(return_value=get_site_response)

        event_bus_request = {"body": params}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            **get_site_response,
        }

        get_site = GetSite(bruin_repository)
        await get_site(request_msg)
        bruin_repository.get_site.assert_awaited_once_with(params)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def get_site_no_filters_test(self):
        bruin_repository = Mock()
        bruin_repository.get_site = AsyncMock()

        event_bus_request = {"response_topic": "some.topic"}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            "body": 'You must specify {.."body":{"client_id":...}} in the request',
            "status": 400,
        }

        get_site = GetSite(bruin_repository)
        await get_site(request_msg)
        bruin_repository.get_site.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def get_site_incomplete_filters_test(self):
        client_id = 72959

        bruin_repository = Mock()
        bruin_repository.get_site = AsyncMock()

        event_bus_request = {"body": {"client_id": client_id}}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {"body": 'You must specify "site_id" in the body', "status": 400}

        get_site = GetSite(bruin_repository)
        await get_site(request_msg)
        bruin_repository.get_site.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def get_site_incomplete_filters_site_id_test(self):
        site_id = 343443

        bruin_repository = Mock()
        bruin_repository.get_site = AsyncMock()

        event_bus_request = {"body": {"site_id": site_id}}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {"body": 'You must specify "client_id" in the body', "status": 400}

        get_site = GetSite(bruin_repository)
        await get_site(request_msg)
        bruin_repository.get_site.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))
