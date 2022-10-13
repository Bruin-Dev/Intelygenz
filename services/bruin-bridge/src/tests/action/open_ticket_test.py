from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.open_ticket import OpenTicket
from application.repositories.utils_repository import to_json_bytes


class TestOpenTicket:
    def instance_test(self):
        bruin_repo = Mock()

        open_ticket = OpenTicket(bruin_repo)

        assert open_ticket._bruin_repository == bruin_repo

    @pytest.mark.asyncio
    async def open_ticket_no_ticket_id_no_body_test(self):
        msg = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repo = Mock()
        bruin_repo.open_ticket = AsyncMock(return_value={"body": "Success", "status": 200})

        open_ticket = OpenTicket(bruin_repo)
        await open_ticket(request_msg)

        bruin_repo.open_ticket.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": 'Must include "body" in request', "status": 400})
        )

    @pytest.mark.asyncio
    async def open_ticket_no_ticket_id_no_detail_id_test(self):
        msg = {"body": {}}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repo = Mock()
        bruin_repo.open_ticket = AsyncMock(return_value={"body": "Success", "status": 200})

        open_ticket = OpenTicket(bruin_repo)
        await open_ticket(request_msg)

        bruin_repo.open_ticket.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": "You must include ticket_id and detail_id in the request", "status": 400})
        )

    @pytest.mark.asyncio
    async def open_ticket_200_test(self):
        ticket_id = 123
        detail_id = 432
        msg = {
            "body": {"ticket_id": ticket_id, "detail_id": detail_id},
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repo = Mock()
        bruin_repo.open_ticket = AsyncMock(return_value={"body": "Success", "status": 200})

        open_ticket = OpenTicket(bruin_repo)
        await open_ticket(request_msg)

        bruin_repo.open_ticket.assert_awaited_once_with(ticket_id, detail_id)
        request_msg.respond.assert_awaited_once_with(to_json_bytes({"body": "Success", "status": 200}))
