import asyncio
from datetime import datetime
from unittest.mock import Mock, call, patch

import pytest
from application.repositories.bruin_repository import BruinRepository
from asynctest import CoroutineMock
from config import testconfig as config
from shortuuid import uuid

uuid_ = uuid()


class TestBruinRepository:
    def instance_test(self, event_bus, logger, notifications_repository):
        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        assert bruin_repository._event_bus is event_bus
        assert bruin_repository._logger is logger
        assert bruin_repository._config is config
        assert bruin_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_single_ticket_basic_info__ok_test(
        self,
        event_bus,
        bruin_repository,
        make_ticket,
        make_rpc_request,
        make_rpc_response,
    ):
        ticket_id = 1234

        request = make_rpc_request(request_id=uuid_, ticket_id=ticket_id)

        response_body = make_ticket(ticket_id=ticket_id)
        response = make_rpc_response(request_id=uuid_, body=response_body, status=200)

        event_bus.rpc_request.return_value = response
        with patch("application.repositories.bruin_repository.uuid", return_value=uuid_):
            result = await bruin_repository.get_single_ticket_basic_info(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.single_ticket.basic.request",
            request,
            timeout=config.MONITOR_CONFIG["nats_request_timeout"]["bruin_request_seconds"],
        )

        assert result == response

    @pytest.mark.asyncio
    async def get_service_number_information__not_2xx_test(
        self,
        event_bus,
        bruin_repository,
        notifications_repository,
        make_rpc_response,
    ):
        ticket_id = 5678

        response = make_rpc_response(request_id=uuid_, body="Error", status=400)
        event_bus.rpc_request.return_value = response

        with patch("application.repositories.bruin_repository.uuid", return_value=uuid_):
            result = await bruin_repository.get_single_ticket_basic_info(ticket_id)

        event_bus.rpc_request.assert_awaited()
        notifications_repository.send_slack_message.assert_awaited_once()

        assert result == response

    @pytest.mark.asyncio
    async def get_single_ticket_info_with_service_numbers__ok_test(
        self,
        bruin_repository,
        make_ticket_details,
        make_rpc_response,
    ):
        ticket_id = 1234
        service_numbers = ["1234", "5678"]
        ticket = {
            "ticket_id": ticket_id,
            "ticket_status": "New",
            "call_type": "Repair",
            "category": "VOO",
            "creation_date": "2021-12-01T00:00:00Z",
        }

        detail_items = []
        notes = [{"serviceNumber": ["1234"]}, {"serviceNumber": ["5678"]}]
        details = make_ticket_details(detail_items=detail_items, notes=notes)

        ticket_basic_response = make_rpc_response(status=200, body=ticket)
        ticket_details_response = make_rpc_response(status=200, body=details)

        get_single_ticket_basic_info = CoroutineMock(return_value=ticket_basic_response)
        get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.get_single_ticket_basic_info = get_single_ticket_basic_info
        bruin_repository.get_ticket_details = get_ticket_details

        response = await bruin_repository.get_single_ticket_info_with_service_numbers(ticket_id)

        assert response["status"] == 200
        assert response["body"]["ticket_id"] == ticket_id
        assert sorted(response["body"]["service_numbers"]) == sorted(service_numbers)

    @pytest.mark.asyncio
    async def get_single_ticket_info_with_service_numbers__basic_ticket_error_test(
        self,
        bruin_repository,
        make_rpc_response,
    ):
        ticket_id = 1234

        ticket_basic_response = make_rpc_response(status=500, body="Error while retrieving basic ticket info")

        get_single_ticket_basic_info = CoroutineMock(return_value=ticket_basic_response)
        get_ticket_details = CoroutineMock()

        bruin_repository.get_single_ticket_basic_info = get_single_ticket_basic_info
        bruin_repository.get_ticket_details = get_ticket_details

        response = await bruin_repository.get_single_ticket_info_with_service_numbers(ticket_id)

        get_single_ticket_basic_info.assert_awaited_once_with(ticket_id)
        get_ticket_details.assert_not_awaited()

        assert response["status"] == 500
        assert response["body"] == "Error while retrieving basic ticket info"

    @pytest.mark.asyncio
    async def get_single_ticket_info_with_service_numbers__details_error_test(
        self,
        bruin_repository,
        make_rpc_response,
    ):
        ticket_id = 1234
        ticket = {
            "ticket_id": ticket_id,
            "ticket_status": "New",
            "call_type": "Repair",
            "category": "VOO",
            "creation_date": "2021-12-01T00:00:00Z",
        }

        ticket_basic_response = make_rpc_response(status=200, body=ticket)
        ticket_details_response = make_rpc_response(status=500, body="Error")

        get_single_ticket_basic_info = CoroutineMock(return_value=ticket_basic_response)
        get_ticket_details = CoroutineMock(return_value=ticket_details_response)

        bruin_repository.get_single_ticket_basic_info = get_single_ticket_basic_info
        bruin_repository.get_ticket_details = get_ticket_details

        response = await bruin_repository.get_single_ticket_info_with_service_numbers(ticket_id)

        get_single_ticket_basic_info.assert_awaited_once_with(ticket_id)
        get_ticket_details.assert_awaited_once_with(ticket_id)

        assert response["status"] == 500
        assert response["body"] == "Error while retrieving ticket service_numbers"

    @pytest.mark.asyncio
    async def get_single_ticket_info_with_service_numbers__404_test(self, bruin_repository, make_rpc_response):
        ticket_id = 1234
        ticket_basic_response = make_rpc_response(status=200, body=[])

        get_single_ticket_basic_info = CoroutineMock(return_value=ticket_basic_response)
        get_ticket_details = CoroutineMock()

        bruin_repository.get_single_ticket_basic_info = get_single_ticket_basic_info
        bruin_repository.get_ticket_details = get_ticket_details

        response = await bruin_repository.get_single_ticket_info_with_service_numbers(ticket_id)

        get_single_ticket_basic_info.assert_awaited_once_with(ticket_id)
        get_ticket_details.assert_not_awaited()

        assert response["status"] == 404
        assert response["body"] == "Ticket not found"

    @pytest.mark.asyncio
    async def verify_service_number_information__ok_test(
        self,
        event_bus,
        bruin_repository,
        make_rpc_request,
        make_rpc_response,
    ):
        client_id = "12345"
        service_number = "1234"
        site_id = "1234"
        request = make_rpc_request(request_id=uuid_, client_id=client_id, service_number=service_number, status="A")
        response_body = [{"client_id": client_id, "client_name": client_id, "site_id": site_id}]
        response = make_rpc_response(request_id=uuid_, body=response_body, status=200)

        event_bus.rpc_request.return_value = response
        with patch("application.repositories.bruin_repository.uuid", return_value=uuid_):
            result = await bruin_repository.verify_service_number_information(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.customer.get.info",
            request,
            timeout=config.MONITOR_CONFIG["nats_request_timeout"]["bruin_request_seconds"],
        )

        assert result == response

    @pytest.mark.asyncio
    async def verify_service_number_information__non_2xx_status_test(
        self,
        event_bus,
        bruin_repository,
        make_rpc_response,
    ):
        client_id = "12345"
        service_number = "1234"
        response_body = {"error": "error"}
        response = make_rpc_response(request_id=uuid_, body=response_body, status=400)

        event_bus.rpc_request.return_value = response
        with patch("application.repositories.bruin_repository.uuid", return_value=uuid_):
            result = await bruin_repository.verify_service_number_information(client_id, service_number)

        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_details__ok_test(
        self, bruin_repository, make_rpc_request, ticket_details_1, make_rpc_response, event_bus
    ):
        ticket_id = "1234"

        expected_request = make_rpc_request(request_id=uuid_, ticket_id=ticket_id)
        expected_response = make_rpc_response(request_id=uuid_, status=200, body=ticket_details_1)

        event_bus.rpc_request.return_value = expected_response

        with patch("application.repositories.bruin_repository.uuid", return_value=uuid_):
            response = await bruin_repository.get_ticket_details(ticket_id)

        event_bus.rpc_request.assert_awaited_with(
            "bruin.ticket.details.request",
            expected_request,
            config.MONITOR_CONFIG["nats_request_timeout"]["bruin_request_seconds"],
        )
        assert response == expected_response

    @pytest.mark.asyncio
    async def get_ticket_details__non_2xx_status_test(
        self,
        event_bus,
        bruin_repository,
        make_rpc_response,
    ):
        ticket_id = "1234"

        response_body = {"error": "error"}
        expected_response = make_rpc_response(request_id=uuid_, status=400, body=response_body)

        event_bus.rpc_request.return_value = expected_response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with patch("application.repositories.bruin_repository.uuid", return_value=uuid_):
            response = await bruin_repository.get_ticket_details(ticket_id)

        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()

        assert response == expected_response

    @pytest.mark.asyncio
    async def get_tickets_basic_info__ok_test(
        self, bruin_repository, make_ticket, make_rpc_request, make_rpc_response, event_bus
    ):
        client_id = 1234
        ticket_statuses = ["New", "InProgress"]
        request = make_rpc_request(request_id=uuid_, client_id=client_id, ticket_statuses=ticket_statuses)

        expected_response_body = [
            make_ticket(ticket_id=1234, client_id=client_id),
            make_ticket(ticket_id=4567, client_id=client_id),
        ]
        expected_response = make_rpc_response(request_id=uuid_, status=200, body=expected_response_body)
        event_bus.rpc_request.return_value = expected_response

        with patch("application.repositories.bruin_repository.uuid", return_value=uuid_):
            tickets = await bruin_repository.get_tickets_basic_info(ticket_statuses, client_id=client_id)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.basic.request",
            request,
            timeout=config.MONITOR_CONFIG["nats_request_timeout"]["bruin_request_seconds"],
        )

        assert tickets["body"] == expected_response_body

    @pytest.mark.asyncio
    async def get_tickets_basic_info__non_2xx_status_test(
        self,
        event_bus,
        bruin_repository,
        make_rpc_request,
        make_rpc_response,
    ):
        client_id = 1234
        ticket_statuses = ["New", "InProgress"]
        request = make_rpc_request(request_id=uuid_, client_id=client_id, ticket_statuses=ticket_statuses)

        expected_response = make_rpc_response(request_id=uuid_, status=400, body={"Error": "Error message"})
        event_bus.rpc_request.return_value = expected_response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with patch("application.repositories.bruin_repository.uuid", return_value=uuid_):
            response = await bruin_repository.get_tickets_basic_info(ticket_statuses, client_id=client_id)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.basic.request",
            request,
            timeout=config.MONITOR_CONFIG["nats_request_timeout"]["bruin_request_seconds"],
        )

        assert response == expected_response

    @pytest.mark.asyncio
    async def get_existing_tickets_with_service_number__ok_test(
        self,
        bruin_repository,
        make_rpc_response,
        make_ticket,
        ticket_details_1,
    ):
        client_id = "5687"
        ticket_id = "1234"
        site_ids = ["1234"]
        tickets_input = [make_ticket(ticket_id=ticket_id)]
        expected_service_numbers = ["VC05200085666", "VC05200085762"]
        basic_info_response = make_rpc_response(request_id=uuid_, status=200, body=tickets_input)
        details_response = make_rpc_response(request_id=uuid_, status=200, body=ticket_details_1)

        bruin_repository.get_tickets_basic_info = CoroutineMock(return_value=basic_info_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=details_response)
        bruin_repository._get_details_service_numbers = Mock(return_value=expected_service_numbers)

        existing_tickets = await bruin_repository.get_existing_tickets_with_service_numbers(client_id, site_ids)

        assert existing_tickets["status"] == 200
        assert existing_tickets["body"][0]["ticket_id"] == ticket_id
        assert len(existing_tickets["body"]) == 2
        assert existing_tickets["body"][0]["service_numbers"] == expected_service_numbers

    @pytest.mark.asyncio
    async def get_existing_tikets__error_tickets_test(
        self,
        bruin_repository,
        make_rpc_response,
    ):
        client_id = "5687"
        site_ids = ["1234", "6579"]
        error_message = {"Error": "Error"}
        tickets_response = make_rpc_response(request_id=uuid_, status=400, body=error_message)
        bruin_repository.get_tickets_basic_info = CoroutineMock(return_value=tickets_response)

        existing_tickets = await bruin_repository.get_existing_tickets_with_service_numbers(client_id, site_ids)

        assert existing_tickets["status"] == 400
        assert existing_tickets["body"] == "Error while retrieving tickets"

    @pytest.mark.asyncio
    async def get_existing_tickets_with_service_numbers__empty_tickets_test(
        self,
        bruin_repository,
        make_rpc_response,
    ):
        client_id = "5687"
        site_ids = ["1234", "6579"]
        error_message = []
        tickets_response = make_rpc_response(request_id=uuid_, status=200, body=error_message)
        bruin_repository.get_tickets_basic_info = CoroutineMock(return_value=tickets_response)

        tickets = await bruin_repository.get_existing_tickets_with_service_numbers(client_id, site_ids)

        assert tickets["status"] == 404
        assert tickets["body"] == "No tickets found"

    @pytest.mark.asyncio
    async def get_existing_tickets_with_service_numbers__details_error_test(
        self,
        bruin_repository,
        make_ticket,
        make_rpc_response,
    ):
        client_id = "5687"
        ticket_id = "1234"
        site_ids = ["1234", "6579"]
        tickets = [make_ticket(ticket_id=ticket_id)]
        error_details = "Error in Bruin"
        tickets_response = make_rpc_response(request_id=uuid_, status=200, body=tickets)
        details_response = make_rpc_response(request_id=uuid_, status=400, body=error_details)

        bruin_repository.get_tickets_basic_info = CoroutineMock(return_value=tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=details_response)

        existing_tickets = await bruin_repository.get_existing_tickets_with_service_numbers(client_id, site_ids)

        assert existing_tickets["status"] == 200
        assert existing_tickets["body"] == []

    def _decamelize_ticket_test(self, bruin_repository, make_ticket):
        input_ticket = make_ticket(ticket_id="1234", client_id="5678", created_by="Test author")

        result = bruin_repository._decamelize_ticket(input_ticket)

        assert "ticket_id" in result.keys()
        assert "client_id" in result.keys()
        assert "created_by" in result.keys()

    def _get_details_service_numbers__ok_test(self, bruin_repository, ticket_details_1):
        expected_service_numbers = ["VC05200085666", "VC05200085762"]
        service_numbers = bruin_repository._get_details_service_numbers(ticket_details_1)

        assert sorted(service_numbers) == sorted(expected_service_numbers)

    def _get_details_service_numbers__empty_test(self, bruin_repository, ticket_details_no_service):
        expected_service_numbers = []
        service_numbers = bruin_repository._get_details_service_numbers(ticket_details_no_service)

        assert service_numbers == expected_service_numbers

    @pytest.mark.asyncio
    async def get_closed_tickets_with_creation_date_limit__ok_test(
        self,
        bruin_repository,
        make_ticket,
        make_ticket_decamelized,
        make_rpc_response,
    ):
        limit = datetime.now()
        expected_limit_date_str = limit.strftime("%Y-%m-%dT%H:%M:%SZ")

        ticket_bruin = make_ticket(
            ticket_id=1234,
            client_id=5678,
        )

        ticket_response = make_ticket_decamelized(ticket_id=1234, client_id=5678)

        bruin_response = make_rpc_response(status=200, body=[ticket_bruin])

        expected_ticket_basic_info_calls = (
            call(ticket_statuses=["Closed"], ticket_topic="VOO", start_date=expected_limit_date_str),
            call(ticket_statuses=["Closed"], ticket_topic="VAS", start_date=expected_limit_date_str),
        )

        get_tickets_basic_info = CoroutineMock(return_value=bruin_response)
        bruin_repository.get_tickets_basic_info = get_tickets_basic_info

        response = await bruin_repository.get_closed_tickets_with_creation_date_limit(limit)

        get_tickets_basic_info.assert_has_awaits(expected_ticket_basic_info_calls)

        assert response["status"] == 200
        assert len(response["body"]) == 2
        assert response["body"][0]["ticket_id"] == ticket_response["ticket_id"]

    @pytest.mark.asyncio
    async def get_closed_tickets_with_creation_date_limit__basic_info_error_test(
        self,
        bruin_repository,
        make_rpc_response,
    ):
        limit = datetime.now()

        bruin_response = make_rpc_response(status=500, body="Error")

        get_tickets_basic_info = CoroutineMock(return_value=bruin_response)
        bruin_repository.get_tickets_basic_info = get_tickets_basic_info

        response = await bruin_repository.get_closed_tickets_with_creation_date_limit(limit)

        get_tickets_basic_info.assert_awaited_once()

        assert response["status"] == 500
        assert response["body"] == "Error"

    @pytest.mark.asyncio
    async def get_status_and_cancellation_reasons__ok_test(
        self, bruin_repository, make_rpc_response, make_ticket_details
    ):
        ticket_id = 1234
        notes = [{"noteType": "CancellationReason", "noteValue": "Test AI"}]
        details = [{}]

        ticket_details = make_ticket_details(detail_items=details, notes=notes)
        details_response = make_rpc_response(status=200, body=ticket_details)

        get_details = CoroutineMock(return_value=details_response)
        bruin_repository.get_ticket_details = get_details

        response = await bruin_repository.get_status_and_cancellation_reasons(ticket_id)
        assert response["status"] == 200
        assert response["body"]["ticket_status"] == "cancelled"
        assert response["body"]["cancellation_reasons"] == ["Test AI"]

    @pytest.mark.asyncio
    async def get_status_and_cancellation_reasons__details_errors_test(
        self,
        bruin_repository,
        make_rpc_response,
    ):
        ticket_id = 1234

        details_response = make_rpc_response(status=500, body="error")

        get_details = CoroutineMock(return_value=details_response)
        bruin_repository.get_ticket_details = get_details

        response = await bruin_repository.get_status_and_cancellation_reasons(ticket_id)
        assert response["status"] == 500
        assert response["body"] == "error"

    def _get_status_and_cancellation_reasons_from_notes__cancelled_test(self, bruin_repository):
        notes = [
            {"noteType": "CancellationReason", "noteValue": "Test AI"},
            {"noteType": "CancellationReason", "noteValue": "Other"},
        ]

        status, cancellation_reasons = bruin_repository._get_status_and_cancellation_reasons_from_notes(notes)

        assert status == "cancelled"
        assert sorted(cancellation_reasons) == sorted(["Test AI", "Other"])

    def _get_status_and_cancellation_reasons_from_notes__cancelled_repeated_reasons_test(self, bruin_repository):
        notes = [
            {"noteType": "CancellationReason", "noteValue": "Test AI"},
            {"noteType": "CancellationReason", "noteValue": "Test AI"},
        ]

        status, cancellation_reasons = bruin_repository._get_status_and_cancellation_reasons_from_notes(notes)

        assert status == "cancelled"
        assert cancellation_reasons == ["Test AI"]

    def _get_status_and_cancellation_reasons_from_notes__resolved_test(self, bruin_repository):
        notes = [{"noteType": "email", "noteValue": "test"}]

        status, cancellation_reasons = bruin_repository._get_status_and_cancellation_reasons_from_notes(notes)

        assert status == "resolved"
        assert cancellation_reasons == []

    @pytest.mark.asyncio
    async def append_notes_to_ticket_rpc_error_test(self, bruin_repository_real):
        # given
        ticket_id = "12345"
        note = [
            {
                "text": "I'm a note of test",
                "service_number": "VC05200011984",
                "is_private": True,
            }
        ]  # when
        bruin_bridge_response = await bruin_repository_real.append_notes_to_ticket(ticket_id=ticket_id, notes=note)

        # then
        bruin_repository_real._notifications_repository.send_slack_message.assert_awaited_once()
        assert bruin_bridge_response == {"body": None, "status": 503}

    @pytest.mark.asyncio
    async def append_notes_to_ticket_400__test(self, bruin_repository_real):
        """
        When request_rpc was successful and return a status code not equal
        to 200
        Then the request_rpc response is returned
        """
        # given
        ticket_id = "12345"
        note = [
            {
                "text": "I'm a note of test",
                "service_number": "VC05200011984",
                "is_private": True,
            }
        ]
        rpc_response = {"status": 400, "body": "400 error"}
        # when
        with patch.object(bruin_repository_real._event_bus, "rpc_request", return_value=asyncio.Future()) as rpc_mock:
            rpc_mock.return_value.set_result(rpc_response)

            bruin_bridge_response = await bruin_repository_real.append_notes_to_ticket(ticket_id=ticket_id, notes=note)
        # then
        bruin_repository_real._notifications_repository.send_slack_message.assert_awaited_once()
        assert bruin_bridge_response == rpc_response

    @pytest.mark.asyncio
    async def append_notes_to_ticket_200__test(self, bruin_repository_real):
        """
        When request_rpc was successful and return status code 200
        Then the request_rpc response is returned
        """
        # given
        ticket_id = "12345"
        note = [
            {
                "text": "I'm a note of test",
                "service_number": "VC05200011984",
                "is_private": True,
            }
        ]
        rpc_response = {"status": 200, "body": "All my body"}
        # when
        with patch.object(bruin_repository_real._event_bus, "rpc_request", return_value=asyncio.Future()) as rpc_mock:
            rpc_mock.return_value.set_result(rpc_response)

            bruin_bridge_response = await bruin_repository_real.append_notes_to_ticket(ticket_id=ticket_id, notes=note)
        # then
        assert bruin_bridge_response == rpc_response
