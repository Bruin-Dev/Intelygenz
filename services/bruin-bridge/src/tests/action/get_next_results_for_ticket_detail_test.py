from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.get_next_results_for_ticket_detail import GetNextResultsForTicketDetail
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestGetNextResultsForTicketDetail:
    def instance_test(self):
        bruin_repository = Mock()

        get_next_results = GetNextResultsForTicketDetail(bruin_repository)

        assert get_next_results._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_next_results_for_ticket_detail_with_body_not_in_message_test(self):
        request = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request)

        response = {
            "body": 'You must specify {.."body": {"ticket_id", "detail_id", "service_number"}...} in the request',
            "status": 400,
        }

        bruin_repository = Mock()

        get_next_results = GetNextResultsForTicketDetail(bruin_repository)

        await get_next_results(request_msg)

        request_msg.respond.assert_awaited_once_with(to_json_bytes(response))

    @pytest.mark.asyncio
    async def get_next_results_for_ticket_detail_with_missing_parameters_in_body_test(self):
        request = {
            "body": {
                "ticket_id": 12345,
                "service_number": "VC1234567",
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request)

        response = {
            "body": 'You must specify {.."body": {"ticket_id", "detail_id", "service_number"}...} in the request',
            "status": 400,
        }

        bruin_repository = Mock()

        get_next_results = GetNextResultsForTicketDetail(bruin_repository)

        await get_next_results(request_msg)

        request_msg.respond.assert_awaited_once_with(to_json_bytes(response))

    @pytest.mark.asyncio
    async def get_next_results_for_ticket_detail_with_all_conditions_met_test(self):
        ticket_id = 12345
        detail_id = 67890
        service_number = "VC1234567"
        request = {
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
                "service_number": service_number,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request)

        response_body = [
            {
                "resultTypeId": 620,
                "resultName": "No Trouble Found - Carrier Issue",
                "notes": [
                    {
                        "noteType": "Notes",
                        "noteDescription": "Notes",
                        "availableValueOptions": None,
                        "defaultValue": None,
                        "required": False,
                    }
                ],
            }
        ]
        response_status = 200
        repository_response = {
            "body": response_body,
            "status": response_status,
        }
        rpc_response = {
            **repository_response,
        }

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = AsyncMock(return_value=repository_response)

        get_next_results = GetNextResultsForTicketDetail(bruin_repository)

        await get_next_results(request_msg)

        bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, detail_id, service_number
        )
        request_msg.respond.assert_awaited_once_with(to_json_bytes(rpc_response))
