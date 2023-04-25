from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.get_ticket_detail_ids_by_ticket_detail_interfaces import GetDetailIdsByTicketDetailInterfaces
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestGetDetailIdsByTicketDetailInterfaces:
    def instance_test(self):
        bruin_repository = Mock()

        ticket_details = GetDetailIdsByTicketDetailInterfaces(bruin_repository)

        assert ticket_details._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def send_get_ticket_detail_ids_by_ticket_detail_interfaces_no_body_test(self):
        msg = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        ticket_detail_ids_by_ticket_detail_interfaces_response = {
            "status": 400
        }
        send_ticket_detail_ids_by_ticket_detail_interfaces_response = {
            "body": 'Must include "body" in request',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.get_ticket_detail_ids_by_ticket_detail_interfaces = (
            AsyncMock(return_value=ticket_detail_ids_by_ticket_detail_interfaces_response))

        get_ticket_detail_ids_by_ticket_detail_interfaces = GetDetailIdsByTicketDetailInterfaces(bruin_repository)
        await get_ticket_detail_ids_by_ticket_detail_interfaces(request_msg)

        (get_ticket_detail_ids_by_ticket_detail_interfaces._bruin_repository
            .get_ticket_detail_ids_by_ticket_detail_interfaces.assert_not_awaited())
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(send_ticket_detail_ids_by_ticket_detail_interfaces_response))

    @pytest.mark.asyncio
    async def send_get_ticket_detail_ids_by_ticket_detail_interfaces_missing_params_test(self):
        msg = {
            "body": {},
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        ticket_detail_ids_by_ticket_detail_interfaces_response = {
            "status": 400
        }
        send_ticket_detail_ids_by_ticket_detail_interfaces_response = {
            "body": "You must include ticket_id, detail_id and interfaces in the request",
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.get_ticket_detail_ids_by_ticket_detail_interfaces = (
            AsyncMock(return_value=ticket_detail_ids_by_ticket_detail_interfaces_response))

        get_ticket_detail_ids_by_ticket_detail_interfaces = GetDetailIdsByTicketDetailInterfaces(bruin_repository)
        await get_ticket_detail_ids_by_ticket_detail_interfaces(request_msg)

        (get_ticket_detail_ids_by_ticket_detail_interfaces._bruin_repository
            .get_ticket_detail_ids_by_ticket_detail_interfaces.assert_not_awaited())
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(send_ticket_detail_ids_by_ticket_detail_interfaces_response))

    @pytest.mark.asyncio
    async def send_get_ticket_detail_ids_by_ticket_detail_interfaces_200_test(self):
        ticket_id = 123
        detail_id = 234
        interfaces = ["GE1", "GE2"]
        msg = {
            "body": {"ticket_id": ticket_id, "detail_id": detail_id, "interfaces": interfaces},
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        ticket_detail_ids_by_ticket_detail_interfaces_response = {
            "body":
                {
                    "detailIds":
                        [
                            345,
                            435
                        ]
                },
            "status": 200
        }

        bruin_repository = Mock()
        bruin_repository.get_ticket_detail_ids_by_ticket_detail_interfaces = (
            AsyncMock(return_value=ticket_detail_ids_by_ticket_detail_interfaces_response))

        get_ticket_detail_ids_by_ticket_detail_interfaces = GetDetailIdsByTicketDetailInterfaces(bruin_repository)
        await get_ticket_detail_ids_by_ticket_detail_interfaces(request_msg)

        (get_ticket_detail_ids_by_ticket_detail_interfaces._bruin_repository
            .get_ticket_detail_ids_by_ticket_detail_interfaces
         .assert_awaited_once_with(ticket_id, detail_id, interfaces))
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(ticket_detail_ids_by_ticket_detail_interfaces_response))
