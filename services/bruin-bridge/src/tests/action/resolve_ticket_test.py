from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.resolve_ticket import ResolveTicket
from application.repositories.utils_repository import to_json_bytes


class TestResolveTicket:
    def instance_test(self):
        bruin_repo = Mock()

        resolve_ticket = ResolveTicket(bruin_repo)

        assert resolve_ticket._bruin_repository == bruin_repo

    @pytest.mark.asyncio
    async def resolve_ticket_no_ticket_id_no_body_test(self):
        msg = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repo = Mock()
        bruin_repo.resolve_ticket = AsyncMock(return_value={"body": "Success", "status": 200})

        resolve_ticket = ResolveTicket(bruin_repo)
        await resolve_ticket(request_msg)

        bruin_repo.resolve_ticket.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": 'Must include "body" in request', "status": 400})
        )

    @pytest.mark.asyncio
    async def resolve_ticket_no_ticket_id_no_detail_id_test(self):
        msg = {"body": {}}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repo = Mock()
        bruin_repo.resolve_ticket = AsyncMock(return_value={"body": "Success", "status": 200})

        resolve_ticket = ResolveTicket(bruin_repo)
        await resolve_ticket(request_msg)

        bruin_repo.resolve_ticket.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": "You must include ticket_id and detail_id in the request", "status": 400})
        )

    @pytest.mark.asyncio
    async def resolve_ticket_200_test(self):
        ticket_id = 123
        detail_id = 432
        msg = {
            "body": {"ticket_id": ticket_id, "detail_id": detail_id},
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repo = Mock()
        bruin_repo.resolve_ticket = AsyncMock(return_value={"body": "Success", "status": 200})

        resolve_ticket = ResolveTicket(bruin_repo)
        await resolve_ticket(request_msg)

        bruin_repo.resolve_ticket.assert_awaited_once_with(ticket_id, detail_id)
        request_msg.respond.assert_awaited_once_with(to_json_bytes({"body": "Success", "status": 200}))
