from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.post_outage_ticket import PostOutageTicket
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestPostOutageTicket:
    def instance_test(self):
        bruin_repository = Mock()

        post_outage_ticket = PostOutageTicket(bruin_repository)

        assert post_outage_ticket._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def post_outage_ticket_with_missing_client_id_test(self):
        bruin_repository = Mock()
        bruin_repository.post_outage_ticket = AsyncMock()

        parameters = {"service_number": "VC05400009999"}
        event_bus_request = {"body": parameters}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        post_outage_ticket = PostOutageTicket(bruin_repository)

        await post_outage_ticket(request_msg)

        bruin_repository.post_outage_ticket.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "body": 'Must specify "client_id" and "service_number" to post an outage ticket',
                    "status": 400,
                }
            )
        )

    @pytest.mark.asyncio
    async def post_outage_ticket_with_missing_service_number_test(self):
        bruin_repository = Mock()
        bruin_repository.post_outage_ticket = AsyncMock()

        parameters = {
            "client_id": 9994,
        }
        event_bus_request = {"body": parameters}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        post_outage_ticket = PostOutageTicket(bruin_repository)

        await post_outage_ticket(request_msg)

        bruin_repository.post_outage_ticket.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "body": 'Must specify "client_id" and "service_number" to post an outage ticket',
                    "status": 400,
                }
            )
        )

    @pytest.mark.asyncio
    async def post_outage_ticket_with_missing_body_test(self):
        bruin_repository = Mock()
        bruin_repository.post_outage_ticket = AsyncMock()

        event_bus_request = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        post_outage_ticket = PostOutageTicket(bruin_repository)

        await post_outage_ticket(request_msg)

        bruin_repository.post_outage_ticket.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "body": 'Must include "body" in request',
                    "status": 400,
                }
            )
        )

    @pytest.mark.asyncio
    async def post_outage_ticket_with_invalid_client_id_test(self):
        bruin_repository = Mock()
        bruin_repository.post_outage_ticket = AsyncMock()

        parameters = {"client_id": None, "service_number": "VC05400009999"}
        event_bus_request = {"body": parameters}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        post_outage_ticket = PostOutageTicket(bruin_repository)

        await post_outage_ticket(request_msg)

        bruin_repository.post_outage_ticket.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "body": '"client_id" and "service_number" must have non-null values',
                    "status": 400,
                }
            )
        )

    @pytest.mark.asyncio
    async def post_outage_ticket_with_invalid_client_id_test(self):
        bruin_repository = Mock()
        bruin_repository.post_outage_ticket = AsyncMock()

        parameters = {"client_id": 9994, "service_number": None}
        event_bus_request = {"body": parameters}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        post_outage_ticket = PostOutageTicket(bruin_repository)

        await post_outage_ticket(request_msg)

        bruin_repository.post_outage_ticket.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "body": '"client_id" and "service_number" must have non-null values',
                    "status": 400,
                }
            )
        )

    @pytest.mark.asyncio
    async def post_outage_ticket_successful_test(self):
        client_id = 9994
        service_number = "VC05400002265"

        outage_ticket_id = 123456
        response_status_code = 200

        repository_response = {
            "body": outage_ticket_id,
            "status": response_status_code,
        }

        bruin_repository = Mock()
        bruin_repository.post_outage_ticket = AsyncMock(return_value=repository_response)

        parameters = {"client_id": client_id, "service_number": service_number}
        event_bus_request = {"body": parameters}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        post_outage_ticket = PostOutageTicket(bruin_repository)

        await post_outage_ticket(request_msg)

        bruin_repository.post_outage_ticket.assert_awaited_once_with(
            client_id, service_number, ticket_contact=None, interfaces=None)
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    **repository_response,
                }
            )
        )

    @pytest.mark.asyncio
    async def post_outage_ticket_successful_with_contact_info_test(self):
        client_id = 9994
        ticket_contact = {"email": "test@test.com"}
        service_number = "VC05400002265"
        interfaces = ["GE1", "GE2"]

        outage_ticket_id = 123456
        response_status_code = 200

        repository_response = {
            "body": outage_ticket_id,
            "status": response_status_code,
        }

        bruin_repository = Mock()
        bruin_repository.post_outage_ticket = AsyncMock(return_value=repository_response)

        parameters = {"client_id": client_id, "service_number": service_number,
                      "ticket_contact": ticket_contact, "interfaces": interfaces}
        event_bus_request = {"body": parameters}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        post_outage_ticket = PostOutageTicket(bruin_repository)

        await post_outage_ticket(request_msg)

        bruin_repository.post_outage_ticket.assert_awaited_once_with(
            client_id, service_number, ticket_contact=ticket_contact, interfaces=interfaces
        )
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    **repository_response,
                }
            )
        )

    @pytest.mark.asyncio
    async def post_outage_ticket_successful_with_full_response_test(self):
        client_id = 9994
        ticket_contact = {"email": "test@test.com"}
        service_number = "VC05400002265"
        interfaces = ["GE1", "GE2"]

        outage_ticket_full_response = {
            'message': 'WTN [7BJR363]: Cannot find any valid WTN for interfaces. [SFP3]',
            'items': [
                {
                    'ticketId': 7586785,
                    'inventoryId': 14517364,
                    'wtn': '7BJR363',
                    'errorMessage': ("Warning: Ticket already exists. We'll add an additional line.\n "
                                     "Failed to add additional line: The item already exists in 7586785, "
                                     "could not add another dulplicate one"),
                    'errorCode': 409
                }
            ]
        }
        response_status_code = 200

        repository_response = {
            "body": outage_ticket_full_response,
            "status": response_status_code,
        }

        bruin_repository = Mock()
        bruin_repository.post_outage_ticket_full_response = AsyncMock(return_value=repository_response)

        parameters = {"client_id": client_id, "service_number": service_number,
                      "ticket_contact": ticket_contact, "interfaces": interfaces,
                      "get_full_response": True}
        event_bus_request = {"body": parameters}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        post_outage_ticket = PostOutageTicket(bruin_repository)

        await post_outage_ticket(request_msg)

        bruin_repository.post_outage_ticket_full_response.assert_awaited_once_with(
            client_id, service_number, ticket_contact=ticket_contact, interfaces=interfaces
        )
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    **repository_response,
                }
            )
        )
