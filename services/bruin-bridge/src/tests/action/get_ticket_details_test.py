from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.get_ticket_details import GetTicketDetails
from application.repositories.utils_repository import to_json_bytes


class TestGetTicketDetails:
    def instance_test(self):
        bruin_repository = Mock()

        ticket_details = GetTicketDetails(bruin_repository)

        assert ticket_details._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def send_ticket_details_no_body_test(self):
        msg = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        ticket_details = {"body": {"ticket_details": "Some ticket details"}, "status": 400}
        send_details_response = {
            "body": 'Must include "body" in request',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = AsyncMock(return_value=ticket_details)

        ticket_details = GetTicketDetails(bruin_repository)
        await ticket_details(request_msg)

        ticket_details._bruin_repository.get_ticket_details.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(send_details_response))

    @pytest.mark.asyncio
    async def send_ticket_details_no_ticket_id_test(self):
        msg = {
            "body": {},
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        ticket_details = {"body": {"ticket_details": "Some ticket details"}, "status": 400}
        send_details_response = {
            "body": "You must include ticket_id in the request",
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = AsyncMock(return_value=ticket_details)

        ticket_details = GetTicketDetails(bruin_repository)
        await ticket_details(request_msg)

        ticket_details._bruin_repository.get_ticket_details.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(send_details_response))

    @pytest.mark.asyncio
    async def send_ticket_details_200_test(self):
        ticket_id = 123
        msg = {
            "body": {"ticket_id": ticket_id},
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        ticket_details = {"body": {"ticket_details": "Some ticket details"}, "status": 200}
        send_details_response = {
            "body": ticket_details["body"],
            "status": 200,
        }

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = AsyncMock(return_value=ticket_details)

        ticket_details = GetTicketDetails(bruin_repository)
        await ticket_details(request_msg)

        ticket_details._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(send_details_response))
