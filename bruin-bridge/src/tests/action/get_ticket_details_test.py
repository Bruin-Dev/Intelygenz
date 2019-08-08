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
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()
        bruin_repository.get_ticket_details = Mock(return_value={'ticket_details': 'Some ticket details'})
        msg = {'request_id': "123", 'response_topic': 'bruin.ticket.details.response', 'ticket_id': 123}
        ticket_details = GetTicketDetails(logger, event_bus, bruin_repository)
        await ticket_details.send_ticket_details(json.dumps(msg))
        assert bruin_repository.get_ticket_details.called
        assert bruin_repository.get_ticket_details.call_args[0][0] == msg['ticket_id']
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert event_bus.publish_message.call_args[0][1] == json.dumps({'request_id': msg['request_id'],
                                                                        'ticket_details': {'ticket_details':
                                                                                           'Some ticket details'},
                                                                        'status': 200})

    @pytest.mark.asyncio
    async def send_ticket_details_none_return_test(self):
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()
        bruin_repository.get_ticket_details = Mock(return_value=None)
        msg = {'request_id': "123", 'response_topic': 'bruin.ticket.details.response', 'ticket_id': 123}
        ticket_details = GetTicketDetails(logger, event_bus, bruin_repository)
        await ticket_details.send_ticket_details(json.dumps(msg))
        assert bruin_repository.get_ticket_details.called
        assert bruin_repository.get_ticket_details.call_args[0][0] == msg['ticket_id']
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert event_bus.publish_message.call_args[0][1] == json.dumps({'request_id': msg['request_id'],
                                                                        'ticket_details': None,
                                                                        'status': 500})
