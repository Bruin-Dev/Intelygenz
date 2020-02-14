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
    async def send_ticket_details_no_ticket_id_test(self):
        logger = Mock()
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
        }
        ticket_details = {"body": {'ticket_details': 'Some ticket details'}, "status_code": 400}
        send_details_response = {
            'request_id': request_id,
            'ticket_details': 'You must include ticket_id in the request',
            'status': 400,
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = Mock(return_value=ticket_details)

        ticket_details = GetTicketDetails(logger, event_bus, bruin_repository)
        await ticket_details.send_ticket_details(msg)

        ticket_details._bruin_repository.get_ticket_details.assert_not_called()
        ticket_details._event_bus.publish_message.assert_awaited_once_with(
            response_topic, send_details_response
        )

    @pytest.mark.asyncio
    async def send_ticket_details_200_test(self):
        logger = Mock()
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        ticket_id = 123
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'ticket_id': ticket_id,
        }
        ticket_details = {"body": {'ticket_details': 'Some ticket details'}, "status_code": 200}
        send_details_response = {
            'request_id': request_id,
            'ticket_details': ticket_details["body"],
            'status': 200,
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = Mock(return_value=ticket_details)

        ticket_details = GetTicketDetails(logger, event_bus, bruin_repository)
        await ticket_details.send_ticket_details(msg)

        ticket_details._bruin_repository.get_ticket_details.assert_called_once_with(ticket_id)
        ticket_details._event_bus.publish_message.assert_awaited_once_with(
            response_topic, send_details_response
        )
