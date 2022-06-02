from unittest.mock import Mock

import pytest
from application.actions.get_next_results_for_ticket_detail import GetNextResultsForTicketDetail
from asynctest import CoroutineMock


class TestGetNextResultsForTicketDetail:
    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        get_next_results = GetNextResultsForTicketDetail(logger, event_bus, bruin_repository)

        assert get_next_results._logger is logger
        assert get_next_results._event_bus is event_bus
        assert get_next_results._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_next_results_for_ticket_detail_with_body_not_in_message_test(self):
        request_id = 9999
        response_topic = "some.topic"
        request = {"request_id": request_id, "response_topic": response_topic}

        response = {
            "request_id": 9999,
            "body": 'You must specify {.."body": {"ticket_id", "detail_id", "service_number"}...} in the request',
            "status": 400,
        }

        logger = Mock()
        bruin_repository = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        get_next_results = GetNextResultsForTicketDetail(logger, event_bus, bruin_repository)

        await get_next_results.get_next_results_for_ticket_detail(request)

        event_bus.publish_message.assert_awaited_once_with(response_topic, response)

    @pytest.mark.asyncio
    async def get_next_results_for_ticket_detail_with_missing_parameters_in_body_test(self):
        request_id = 9999
        response_topic = "some.topic"
        request = {
            "request_id": request_id,
            "body": {
                "ticket_id": 12345,
                "service_number": "VC1234567",
            },
            "response_topic": response_topic,
        }

        response = {
            "request_id": 9999,
            "body": 'You must specify {.."body": {"ticket_id", "detail_id", "service_number"}...} in the request',
            "status": 400,
        }

        logger = Mock()
        bruin_repository = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        get_next_results = GetNextResultsForTicketDetail(logger, event_bus, bruin_repository)

        await get_next_results.get_next_results_for_ticket_detail(request)

        event_bus.publish_message.assert_awaited_once_with(response_topic, response)

    @pytest.mark.asyncio
    async def get_next_results_for_ticket_detail_with_all_conditions_met_test(self):
        request_id = 9999
        response_topic = "some.topic"

        ticket_id = 12345
        detail_id = 67890
        service_number = "VC1234567"
        request = {
            "request_id": request_id,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
                "service_number": service_number,
            },
            "response_topic": response_topic,
        }

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
            "request_id": request_id,
            **repository_response,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=repository_response)

        get_next_results = GetNextResultsForTicketDetail(logger, event_bus, bruin_repository)

        await get_next_results.get_next_results_for_ticket_detail(request)

        bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, detail_id, service_number
        )
        event_bus.publish_message.assert_awaited_once_with(response_topic, rpc_response)
