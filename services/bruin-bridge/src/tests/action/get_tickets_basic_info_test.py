from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.get_tickets_basic_info import GetTicketsBasicInfo
from application.repositories.utils_repository import to_json_bytes


class TestGetTicketsBasicInfo:
    def instance_test(self):
        bruin_repository = Mock()

        action = GetTicketsBasicInfo(bruin_repository)

        assert action._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_tickets_basic_info_ok_test(self):
        ticket_statuses = [
            "New",
            "In-Progress",
            "Draft",
        ]
        shared_payload = {
            "client_id": 9994,
            "service_number": "VC1234567",
            "product_category": "SD-WAN",
            "ticket_topic": "VAS",
            "start_date": "2020-08-19T20:12:00Z",
            "end_date": "2020-08-20T20:12:00Z",
        }
        bruin_payload = {
            **shared_payload,
            "ticket_statuses": ticket_statuses,
        }

        request_message = {
            "body": bruin_payload,
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request_message)

        tickets_response = {
            "body": [
                {
                    "clientID": 9994,
                    "ticketID": 5262293,
                    "ticketStatus": "New",
                    "address": {
                        "address": "1090 Vermont Ave NW",
                        "city": "Washington",
                        "state": "DC",
                        "zip": "20005-4905",
                        "country": "USA",
                    },
                    "createDate": "3/13/2021 12:59:36 PM",
                },
            ],
            "status": 200,
        }
        response_message = {
            **tickets_response,
        }

        bruin_repository = Mock()
        bruin_repository.get_tickets_basic_info = AsyncMock(return_value=tickets_response)

        action = GetTicketsBasicInfo(bruin_repository)

        await action(request_msg)

        bruin_repository.get_tickets_basic_info.assert_awaited_once_with(shared_payload, ticket_statuses)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_message))

    @pytest.mark.asyncio
    async def get_tickets_basic_info_with_body_missing_in_request_message_test(self):
        request_message = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request_message)

        response_message = {
            "body": 'Must include "body" in the request message',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.get_tickets_basic_info = AsyncMock()

        action = GetTicketsBasicInfo(bruin_repository)

        await action(request_msg)

        bruin_repository.get_tickets_basic_info.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_message))

    @pytest.mark.asyncio
    async def get_tickets_basic_info_with_ticket_statuses_missing_in_request_body_test(self):
        request_message = {
            "body": {
                "service_number": "VC1234567",
                "product_category": "SD-WAN",
                "ticket_topic": "VAS",
                "start_date": "2020-08-19T20:12:00Z",
                "end_date": "2020-08-20T20:12:00Z",
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request_message)

        response_message = {
            "body": 'Must specify "ticket_statuses" in the body of the request',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.get_tickets_basic_info = AsyncMock()

        action = GetTicketsBasicInfo(bruin_repository)

        await action(request_msg)

        bruin_repository.get_tickets_basic_info.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_message))
