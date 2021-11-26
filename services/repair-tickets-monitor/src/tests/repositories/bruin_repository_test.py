import pytest
from shortuuid import uuid
from unittest.mock import patch

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
            make_rpc_response,):

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
