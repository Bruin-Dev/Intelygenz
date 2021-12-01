import pytest
from asynctest import CoroutineMock
from shortuuid import uuid
from unittest.mock import patch, Mock

from application.repositories.bruin_repository import BruinRepository
from config import testconfig as config

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
        with patch('application.repositories.bruin_repository.uuid', return_value=uuid_):
            result = await bruin_repository.get_single_ticket_basic_info(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.single_ticket.basic.request",
            request,
            timeout=config.MONITOR_CONFIG['nats_request_timeout']['bruin_request_seconds']
        )

        assert result == response

    @pytest.mark.asyncio
    async def get_service_number_information__not_2XX_test(
            self,
            event_bus,
            bruin_repository,
            notifications_repository,
            make_rpc_response, ):
        ticket_id = 5678

        response = make_rpc_response(request_id=uuid_, body="Error", status=400)
        event_bus.rpc_request.return_value = response

        with patch('application.repositories.bruin_repository.uuid', return_value=uuid_):
            result = await bruin_repository.get_single_ticket_basic_info(ticket_id)

        event_bus.rpc_request.assert_awaited()
        notifications_repository.send_slack_message.assert_awaited_once()

        assert result == response

    @pytest.mark.asyncio
    async def verify_service_number_information__ok_test(
            self,
            event_bus,
            bruin_repository,
            make_rpc_request,
            make_rpc_response,
    ):
        client_id = '12345'
        service_number = '1234'
        site_id = '1234'
        request = make_rpc_request(request_id=uuid_, client_id=client_id, service_number=service_number, status='A')
        response_body = {'client_id': client_id, 'client_name': client_id, 'site_id': site_id}
        response = make_rpc_response(request_id=uuid_, body=response_body, status=200)

        event_bus.rpc_request.return_value = response
        with patch('application.repositories.bruin_repository.uuid', return_value=uuid_):
            result = await bruin_repository.verify_service_number_information(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.customer.get.info",
            request,
            timeout=config.MONITOR_CONFIG['nats_request_timeout']['bruin_request_seconds']
        )

        assert result == response

    @pytest.mark.asyncio
    async def verify_service_number_information__non_2XX_status_test(
            self,
            event_bus,
            bruin_repository,
            make_rpc_response,
    ):
        client_id = '12345'
        service_number = '1234'
        response_body = {'error': 'error'}
        response = make_rpc_response(request_id=uuid_, body=response_body, status=400)

        event_bus.rpc_request.return_value = response
        with patch('application.repositories.bruin_repository.uuid', return_value=uuid_):
            result = await bruin_repository.verify_service_number_information(client_id, service_number)

        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_details__ok_test(
            self,
            bruin_repository,
            make_rpc_request,
            ticket_details_1,
            make_rpc_response,
            event_bus
    ):
        ticket_id = "1234"

        expected_request = make_rpc_request(request_id=uuid_, ticket_id=ticket_id)
        expected_response = make_rpc_response(request_id=uuid_, status=200, body=ticket_details_1)

        event_bus.rpc_request.return_value = expected_response

        with patch('application.repositories.bruin_repository.uuid', return_value=uuid_):
            response = await bruin_repository.get_ticket_details(ticket_id)

        event_bus.rpc_request.assert_awaited_with(
            "bruin.ticket.details.request",
            expected_request,
            config.MONITOR_CONFIG['nats_request_timeout']['bruin_request_seconds'],
        )
        assert response == expected_response

    @pytest.mark.asyncio
    async def get_ticket_details__non_2XX_status_test(
            self,
            event_bus,
            bruin_repository,
            make_rpc_response,
    ):
        ticket_id = "1234"

        response_body = {'error': 'error'}
        expected_response = make_rpc_response(request_id=uuid_, status=400, body=response_body)

        event_bus.rpc_request.return_value = expected_response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with patch('application.repositories.bruin_repository.uuid', return_value=uuid_):
            response = await bruin_repository.get_ticket_details(ticket_id)

        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()

        assert response == expected_response

    @pytest.mark.asyncio
    async def get_tickets_basic_info__ok_test(
            self,
            bruin_repository,
            make_ticket,
            make_rpc_request,
            make_rpc_response,
            event_bus
    ):
        client_id = 1234
        ticket_statuses = ['New', 'InProgress']
        request = make_rpc_request(request_id=uuid_, client_id=client_id, ticket_statuses=ticket_statuses)

        expected_response_body = [
            make_ticket(ticket_id=1234, client_id=client_id),
            make_ticket(ticket_id=4567, client_id=client_id)
        ]
        expected_response = make_rpc_response(request_id=uuid_, status=200, body=expected_response_body)
        event_bus.rpc_request.return_value = expected_response

        with patch('application.repositories.bruin_repository.uuid', return_value=uuid_):
            tickets = await bruin_repository.get_tickets_basic_info(client_id, ticket_statuses)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.basic.request",
            request,
            timeout=config.MONITOR_CONFIG['nats_request_timeout']['bruin_request_seconds']
        )

        assert tickets['body'] == expected_response_body

    @pytest.mark.asyncio
    async def get_tickets_basic_info__non_2XX_status_test(
            self,
            event_bus,
            bruin_repository,
            make_rpc_request,
            make_rpc_response,
    ):
        client_id = 1234
        ticket_statuses = ['New', 'InProgress']
        request = make_rpc_request(request_id=uuid_, client_id=client_id, ticket_statuses=ticket_statuses)

        expected_response = make_rpc_response(request_id=uuid_, status=400, body={'Error': 'Error message'})
        event_bus.rpc_request.return_value = expected_response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with patch('application.repositories.bruin_repository.uuid', return_value=uuid_):
            response = await bruin_repository.get_tickets_basic_info(client_id, ticket_statuses)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.basic.request",
            request,
            timeout=config.MONITOR_CONFIG['nats_request_timeout']['bruin_request_seconds']
        )

        assert response == expected_response

    @pytest.mark.asyncio
    async def get_open_tickets_with_service_numbers__ok_test(
            self,
            bruin_repository,
            make_rpc_response,
            make_ticket,
            ticket_details_1,
    ):
        client_id = "5687"
        ticket_id = "1234"
        tickets = [make_ticket(ticket_id=ticket_id)]
        expected_service_numbers = ['VC05200085666', 'VC05200085762']
        tickets_response = make_rpc_response(request_id=uuid_, status=200, body=tickets)
        details_response = make_rpc_response(request_id=uuid_, status=200, body=ticket_details_1)

        bruin_repository.get_tickets_basic_info = CoroutineMock(return_value=tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=details_response)
        bruin_repository._get_details_service_numbers = Mock(return_value=expected_service_numbers)

        open_tickets = await bruin_repository.get_open_tickets_with_service_numbers(client_id)

        assert open_tickets['status'] == 200
        assert open_tickets['body'] == tickets
        assert open_tickets['body'][0]['service_numbers'] == expected_service_numbers

    @pytest.mark.asyncio
    async def get_open_tickets_with_service_numbers__error_tickets_test(
            self,
            bruin_repository,
            make_rpc_response,
    ):
        client_id = "5687"
        error_message = {'Error': 'Error'}
        tickets_response = make_rpc_response(request_id=uuid_, status=400, body=error_message)
        bruin_repository.get_tickets_basic_info = CoroutineMock(return_value=tickets_response)

        tickets = await bruin_repository.get_open_tickets_with_service_numbers(client_id)

        assert tickets['status'] == 400
        assert tickets['body'] == 'Error while retrieving open tickets'

    @pytest.mark.asyncio
    async def get_open_tickets_with_service_numbers__empty_tickets_test(
            self,
            bruin_repository,
            make_rpc_response,
    ):
        client_id = "5687"
        error_message = []
        tickets_response = make_rpc_response(request_id=uuid_, status=200, body=error_message)
        bruin_repository.get_tickets_basic_info = CoroutineMock(return_value=tickets_response)

        tickets = await bruin_repository.get_open_tickets_with_service_numbers(client_id)

        assert tickets['status'] == 404
        assert tickets['body'] == 'No open tickets found'

    @pytest.mark.asyncio
    async def get_open_tickets_with_service_numbers__details_error_test(
            self,
            bruin_repository,
            make_ticket,
            make_rpc_response,
    ):
        client_id = "5687"
        ticket_id = "1234"
        tickets = [make_ticket(ticket_id=ticket_id)]
        error_details = 'Error in Bruin'
        tickets_response = make_rpc_response(request_id=uuid_, status=200, body=tickets)
        details_response = make_rpc_response(request_id=uuid_, status=400, body=error_details)

        bruin_repository.get_tickets_basic_info = CoroutineMock(return_value=tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=details_response)

        open_tickets = await bruin_repository.get_open_tickets_with_service_numbers(client_id)

        assert open_tickets['status'] == 200
        assert open_tickets['body'][0]['service_numbers'] == []

    def _get_details_service_numbers__ok_test(self, bruin_repository, ticket_details_1):
        expected_service_numbers = ['VC05200085666', 'VC05200085762']
        service_numbers = bruin_repository._get_details_service_numbers(ticket_details_1)

        assert sorted(service_numbers) == sorted(expected_service_numbers)

    def _get_details_service_numbers__emtpy_test(self, bruin_repository, ticket_details_no_service):
        expected_service_numbers = []
        service_numbers = bruin_repository._get_details_service_numbers(ticket_details_no_service)

        assert service_numbers == expected_service_numbers
