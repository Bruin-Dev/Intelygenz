from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.post_ticket import PostTicket
from application.repositories.utils_repository import to_json_bytes


class TestPostTicket:
    def instance_test(self):
        bruin_repository = Mock()

        post_ticket = PostTicket(bruin_repository)

        assert post_ticket._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def post_ticket_200_test(self):
        post_ticket_response = {"ticketIds": [123]}
        client_id = 321
        category = "Some Category"
        notes = ["some notes"]
        services = ["List of Services"]
        contacts = ["List of Contacts"]

        msg = {
            "body": {
                "clientId": client_id,
                "category": category,
                "services": services,
                "contacts": contacts,
                "notes": notes,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {"body": post_ticket_response, "status": 200}

        bruin_repository = Mock()
        bruin_repository.post_ticket = AsyncMock(return_value={"body": post_ticket_response, "status": 200})

        post_ticket = PostTicket(bruin_repository)
        await post_ticket(request_msg)

        post_ticket._bruin_repository.post_ticket.assert_awaited_once_with(msg["body"])
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))

    @pytest.mark.asyncio
    async def post_ticket_not_200_test(self):
        post_ticket_response = {"ticketIds": [123]}
        client_id = 321
        category = "Some Category"
        notes = ["some notes"]
        services = ["List of Services"]
        contacts = ["List of Contacts"]

        msg = {
            "body": {
                "clientId": client_id,
                "category": category,
                "services": services,
                "contacts": contacts,
                "notes": notes,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {"body": post_ticket_response, "status": 400}

        bruin_repository = Mock()
        bruin_repository.post_ticket = AsyncMock(return_value={"body": post_ticket_response, "status": 400})

        post_ticket = PostTicket(bruin_repository)
        await post_ticket(request_msg)

        post_ticket._bruin_repository.post_ticket.assert_awaited_once_with(msg["body"])
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))

    @pytest.mark.asyncio
    async def post_ticket_no_notes_test(self):
        post_ticket_response = {"ticketIds": [123]}
        client_id = 321
        category = "Some Category"
        services = ["List of Services"]
        contacts = ["List of Contacts"]

        msg = {
            "body": {
                "clientId": client_id,
                "category": category,
                "services": services,
                "contacts": contacts,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        payload_copy = msg["body"].copy()
        payload_copy["notes"] = []
        msg_published_in_topic = {"body": post_ticket_response, "status": 200}

        bruin_repository = Mock()
        bruin_repository.post_ticket = AsyncMock(return_value={"body": post_ticket_response, "status": 200})

        post_ticket = PostTicket(bruin_repository)
        await post_ticket(request_msg)

        post_ticket._bruin_repository.post_ticket.assert_awaited_once_with(payload_copy)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))

    @pytest.mark.asyncio
    async def post_ticket_missing_keys_in_payload_test(self):
        post_ticket_response = {"ticketIds": [123]}
        category = "Some Category"
        contacts = ["List of Contacts"]

        msg = {
            "body": {
                "category": category,
                "contacts": contacts,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {
            "body": 'You must specify "clientId", "category", ' '"services", "contacts" in the body',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.post_ticket = AsyncMock(return_value={"body": post_ticket_response, "status": 200})

        post_ticket = PostTicket(bruin_repository)
        await post_ticket(request_msg)

        post_ticket._bruin_repository.post_ticket.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))

    @pytest.mark.asyncio
    async def post_ticket_missing_payload_test(self):
        post_ticket_response = {"ticketIds": [123]}

        msg = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {
            "body": "You must specify " '{.."body":{"clientId", "category", "services", "contacts"},' " in the request",
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.post_ticket = AsyncMock(return_value={"body": post_ticket_response, "status": 200})

        post_ticket = PostTicket(bruin_repository)
        await post_ticket(request_msg)

        post_ticket._bruin_repository.post_ticket.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))
