from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.close_ticket import CloseTicket
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestCloseTicket:
    def instance_test(self):
        bruin_repo = Mock()

        close_ticket = CloseTicket(bruin_repo)

        assert close_ticket._bruin_repository == bruin_repo

    @pytest.mark.asyncio
    async def close_ticket_no_ticket_id_no_body_test(self):
        msg = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repo = Mock()
        bruin_repo.close_ticket = AsyncMock(return_value={"body": "Success", "status": 200})

        close_ticket = CloseTicket(bruin_repo)
        await close_ticket(request_msg)

        bruin_repo.close_ticket.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": 'Must include "body" in request', "status": 400})
        )

    @pytest.mark.asyncio
    async def close_ticket_no_ticket_id_no_close_note_test(self):
        msg = {"body": {}}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repo = Mock()
        bruin_repo.close_ticket = AsyncMock(return_value={"body": "Success", "status": 200})

        close_ticket = CloseTicket(bruin_repo)
        await close_ticket(request_msg)

        bruin_repo.close_ticket.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": "You must include ticket_id and close_note in the request", "status": 400})
        )

    @pytest.mark.asyncio
    async def close_ticket_200_test(self):
        ticket_id = 123
        close_note = "Closing the ticket note"
        msg = {
            "body": {"ticket_id": ticket_id, "close_note": close_note},
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repo = Mock()
        bruin_repo.close_ticket = AsyncMock(return_value={"body": "Success", "status": 200})

        close_ticket = CloseTicket(bruin_repo)
        await close_ticket(request_msg)

        bruin_repo.close_ticket.assert_awaited_once_with(ticket_id, close_note)
        request_msg.respond.assert_awaited_once_with(to_json_bytes({"body": "Success", "status": 200}))
