from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.get_ticket_contacts import GetTicketContacts
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestGetTicketContacts:
    def instance_test(self):
        bruin_repository = Mock()

        get_ticket_contacts = GetTicketContacts(bruin_repository)

        assert get_ticket_contacts._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_ticket_contacts_ok_test(self):
        bruin_repository = Mock()

        client_id = 72959
        params = {"client_id": client_id}
        get_ticket_contacts_response = {"body": {"client_id": client_id}, "status": 200}
        bruin_repository.get_ticket_contacts = AsyncMock(return_value=get_ticket_contacts_response)

        event_bus_request = {"body": params}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            **get_ticket_contacts_response,
        }

        get_ticket_contacts = GetTicketContacts(bruin_repository)
        await get_ticket_contacts(request_msg)
        bruin_repository.get_ticket_contacts.assert_awaited_once_with(params)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def get_ticket_contacts_no_filters_test(self):
        bruin_repository = Mock()
        bruin_repository.get_ticket_contacts = AsyncMock()

        event_bus_request = {"response_topic": "some.topic"}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            "body": 'You must specify {.."body":{"client_id":...}} in the request',
            "status": 400,
        }

        get_ticket_contacts = GetTicketContacts(bruin_repository)
        await get_ticket_contacts(request_msg)
        bruin_repository.get_ticket_contacts.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def get_ticket_contacts_incomplete_filter_test(self):
        ticket_contacts_id = 343443

        bruin_repository = Mock()
        bruin_repository.get_ticket_contacts = AsyncMock()

        event_bus_request = {"body": {}}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {"body": 'You must specify "client_id" in the body', "status": 400}

        get_ticket_contacts = GetTicketContacts(bruin_repository)
        await get_ticket_contacts(request_msg)
        bruin_repository.get_ticket_contacts.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))
