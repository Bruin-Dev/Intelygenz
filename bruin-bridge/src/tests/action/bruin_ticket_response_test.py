import json
from unittest.mock import Mock

import pytest
import requests
from application.actions.bruin_ticket_response import BruinTicketResponse
from asynctest import CoroutineMock

from config import testconfig as config


class TestBruinTicketResponse:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_client = Mock()
        bruin_ticket_response = BruinTicketResponse(logger, config.BRUIN_CONFIG, event_bus, bruin_client)
        assert bruin_ticket_response._logger is logger
        assert bruin_ticket_response._config is config.BRUIN_CONFIG
        assert bruin_ticket_response._event_bus is event_bus
        assert bruin_ticket_response._bruin_client is bruin_client

    @pytest.mark.asyncio
    async def report_all_bruin_tickets_no_ticket_id_test(self):
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_client = Mock()
        bruin_client.get_all_filtered_tickets = Mock(return_value=['Some ticket list'])
        msg = {'request_id': "123", 'response_topic': 'bruin.ticket.response',
               'client_id': 123}
        bruin_ticket_response = BruinTicketResponse(logger, config.BRUIN_CONFIG, event_bus, bruin_client)
        await bruin_ticket_response.report_all_bruin_tickets(json.dumps(msg))
        assert bruin_client.get_all_filtered_tickets.call_args[0][0] == msg['client_id']
        assert bruin_client.get_all_filtered_tickets.call_args[0][1] == ''
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert event_bus.publish_message.call_args[0][1] == json.dumps({'request_id': msg['request_id'],
                                                                        'tickets': ['Some ticket list'],
                                                                        'status': 200})

    @pytest.mark.asyncio
    async def report_all_bruin_tickets_ticket_id_test(self):
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_client = Mock()
        bruin_client.get_all_filtered_tickets = Mock(return_value=['Some ticket list'])
        msg = {'request_id': "123", 'response_topic': 'bruin.ticket.response',
               'client_id': 123, 'ticket_id': 321}
        bruin_ticket_response = BruinTicketResponse(logger, config.BRUIN_CONFIG, event_bus, bruin_client)
        await bruin_ticket_response.report_all_bruin_tickets(json.dumps(msg))
        assert bruin_client.get_all_filtered_tickets.call_args[0][0] == msg['client_id']
        assert bruin_client.get_all_filtered_tickets.call_args[0][1] == msg['ticket_id']
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert event_bus.publish_message.call_args[0][1] == json.dumps({'request_id': msg['request_id'],
                                                                        'tickets': ['Some ticket list'],
                                                                        'status': 200})

    @pytest.mark.asyncio
    async def report_all_bruin_tickets_none_return_test(self):
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_client = Mock()
        bruin_client.get_all_filtered_tickets = Mock(return_value=None)
        msg = {'request_id': "123", 'response_topic': 'bruin.ticket.response',
               'client_id': 123, 'ticket_id': 321}
        bruin_ticket_response = BruinTicketResponse(logger, config.BRUIN_CONFIG, event_bus, bruin_client)
        await bruin_ticket_response.report_all_bruin_tickets(json.dumps(msg))
        assert bruin_client.get_all_filtered_tickets.call_args[0][0] == msg['client_id']
        assert bruin_client.get_all_filtered_tickets.call_args[0][1] == msg['ticket_id']
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert event_bus.publish_message.call_args[0][1] == json.dumps({'request_id': msg['request_id'],
                                                                        'tickets': None,
                                                                        'status': 500})
