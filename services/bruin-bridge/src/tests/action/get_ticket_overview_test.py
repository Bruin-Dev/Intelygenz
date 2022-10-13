from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.get_ticket_overview import GetTicketOverview
from application.repositories.utils_repository import to_json_bytes


class TestGetTicketOverview:
    def instance_test(self):
        bruin_repository = Mock()

        get_ticket_overview = GetTicketOverview(bruin_repository)

        assert get_ticket_overview._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_ticket_overview_test(self):
        filtered_tickets_list = {"ticket_id": 123}

        msg = {
            "body": filtered_tickets_list,
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        response_to_publish_in_topic = {"body": filtered_tickets_list, "status": 200}
        ticket_overview_mock = {"body": filtered_tickets_list, "status": 200}

        bruin_repository = Mock()
        bruin_repository.get_ticket_overview = AsyncMock(return_value=ticket_overview_mock)

        get_ticket_overview = GetTicketOverview(bruin_repository)
        await get_ticket_overview(request_msg)

        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_to_publish_in_topic))

    @pytest.mark.asyncio
    async def get_ticket_overview_not_body_test(self):
        filtered_tickets_list = {"ticket_id": 123}

        msg = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repository = Mock()
        bruin_repository.get_ticket_overview = AsyncMock(return_value={"body": filtered_tickets_list, "status": 200})

        get_ticket_overview = GetTicketOverview(bruin_repository)
        await get_ticket_overview(request_msg)

        bruin_repository.get_ticket_overview.assert_not_awaited()

    @pytest.mark.asyncio
    async def get_ticket_overview_not_ticket_id_test(self):
        filtered_tickets_list = {}

        msg = {
            "body": filtered_tickets_list,
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repository = Mock()
        bruin_repository.get_ticket_overview = AsyncMock(return_value={"body": filtered_tickets_list, "status": 200})

        get_ticket_overview = GetTicketOverview(bruin_repository)
        await get_ticket_overview(request_msg)

        bruin_repository.get_ticket_overview.assert_not_awaited()
