from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.unpause_ticket import UnpauseTicket
from application.repositories.utils_repository import to_json_bytes


class TestOpenTicket:
    def instance_test(self):
        bruin_repo = Mock()

        unpause_ticket = UnpauseTicket(bruin_repo)

        assert unpause_ticket._bruin_repository == bruin_repo

    @pytest.mark.asyncio
    async def unpause_ticket_no_ticket_id_no_body_test(self):
        msg = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repo = Mock()
        bruin_repo.unpause_ticket = AsyncMock(return_value={"body": "Success", "status": 200})

        unpause_ticket = UnpauseTicket(bruin_repo)
        await unpause_ticket(request_msg)

        bruin_repo.unpause_ticket.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": 'Must include "body" in request', "status": 400})
        )

    @pytest.mark.asyncio
    async def unpause_ticket_no_ticket_id_no_detail_id_test(self):
        msg = {"body": {}}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repo = Mock()
        bruin_repo.unpause_ticket = AsyncMock(return_value={"body": "Success", "status": 200})

        unpause_ticket = UnpauseTicket(bruin_repo)
        await unpause_ticket(request_msg)

        bruin_repo.unpause_ticket.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {"body": "You must include ticket_id and service_number or detail_id in the request", "status": 400}
            )
        )

    @pytest.mark.asyncio
    async def unpause_ticket_200_test(self):
        ticket_id = 123
        serial_number = 123456789
        detail_id = 987654321
        msg = {
            "body": {"ticket_id": ticket_id, "service_number": serial_number, "detail_id": detail_id},
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repo = Mock()
        bruin_repo.unpause_ticket = AsyncMock(return_value={"body": "Success", "status": 200})

        unpause_ticket = UnpauseTicket(bruin_repo)
        await unpause_ticket(request_msg)

        bruin_repo.unpause_ticket.assert_awaited_once_with(ticket_id, serial_number, detail_id)
        request_msg.respond.assert_awaited_once_with(to_json_bytes({"body": "Success", "status": 200}))
