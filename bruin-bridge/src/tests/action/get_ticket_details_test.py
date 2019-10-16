import json
from unittest.mock import Mock

import pytest
from application.actions.get_ticket_details import GetTicketDetails
from asynctest import CoroutineMock


class TestGetTicketDetails:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        ticket_details = GetTicketDetails(logger, event_bus, bruin_repository)

        assert ticket_details._logger is logger
        assert ticket_details._event_bus is event_bus
        assert ticket_details._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def send_ticket_details_test(self):
        logger = Mock()
        request_id = "123"
        response_topic = "bruin.ticket.details.response"
        ticket_id = 123
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'ticket_id': ticket_id,
        }
        ticket_details = {'ticket_details': 'Some ticket details'}
        send_details_response = {
            'request_id': request_id,
            'ticket_details': ticket_details,
            'status': 200,
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = Mock(return_value=ticket_details)

        ticket_details = GetTicketDetails(logger, event_bus, bruin_repository)
        await ticket_details.send_ticket_details(json.dumps(msg))

        ticket_details._bruin_repository.get_ticket_details.assert_called_once_with(ticket_id)
        ticket_details._event_bus.publish_message.assert_awaited_once_with(
            response_topic, json.dumps(send_details_response)
        )

    @pytest.mark.asyncio
    async def send_ticket_details_with_no_ticket_details_returned_test(self):
        logger = Mock()
        request_id = "123"
        response_topic = "bruin.ticket.details.response"
        ticket_id = 123
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'ticket_id': ticket_id,
        }
        ticket_details = None
        send_details_response = {
            'request_id': request_id,
            'ticket_details': ticket_details,
            'status': 500,
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = Mock(return_value=ticket_details)

        ticket_details = GetTicketDetails(logger, event_bus, bruin_repository)
        await ticket_details.send_ticket_details(json.dumps(msg))

        ticket_details._bruin_repository.get_ticket_details.assert_called_once_with(ticket_id)
        ticket_details._event_bus.publish_message.assert_awaited_once_with(
            response_topic, json.dumps(send_details_response)
        )
