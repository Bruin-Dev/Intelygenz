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
    async def report_all_bruin_tickets_test(self):
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_client = Mock()
        bruin_client.get_request_headers = Mock()
        msg = {'request_id': "123", 'response_topic': 'bruin.ticket.response',
               'client_id': 123}
        response = Mock()
        response.json = Mock(return_value={"responses": [{"category": "SD-WAN", "ticketStatus": "Unopened"}]})
        response.status_code = 200
        requests.get = Mock(return_value=response)
        bruin_ticket_response = BruinTicketResponse(logger, config.BRUIN_CONFIG, event_bus, bruin_client)
        await bruin_ticket_response.report_all_bruin_tickets(json.dumps(msg))
        assert requests.get.called
        assert requests.get.call_args[1]['params']['ClientId'] == msg['client_id']
        assert requests.get.call_args[1]['params']['TicketId'] == ''
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert '{"category": "SD-WAN", "ticketStatus": "Unopened"}' in event_bus.publish_message.call_args[0][1]
        assert '200' in event_bus.publish_message.call_args[0][1]

    @pytest.mark.asyncio
    async def report_all_bruin_tickets_ticked_id_test(self):
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_client = Mock()
        bruin_client.get_request_headers = Mock()
        msg = {'request_id': "123", 'response_topic': 'bruin.ticket.response',
               'client_id': 123, 'ticket_id': 231}
        response = Mock()
        response.json = Mock(return_value={"responses": [{"category": "SD-WAN", "ticketStatus": "Unopened"}]})
        response.status_code = 200
        requests.get = Mock(return_value=response)
        bruin_ticket_response = BruinTicketResponse(logger, config.BRUIN_CONFIG, event_bus, bruin_client)
        await bruin_ticket_response.report_all_bruin_tickets(json.dumps(msg))
        assert requests.get.called
        assert requests.get.call_args[1]['params']['ClientId'] == msg['client_id']
        assert requests.get.call_args[1]['params']['TicketId'] == msg['ticket_id']
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert '{"category": "SD-WAN", "ticketStatus": "Unopened"}' in event_bus.publish_message.call_args[0][1]
        assert '200' in event_bus.publish_message.call_args[0][1]

    @pytest.mark.asyncio
    async def report_all_bruin_tickets_closed_ticket_test(self):
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_client = Mock()
        bruin_client.get_request_headers = Mock()
        msg = {'request_id': "123", 'response_topic': 'bruin.ticket.response',
               'client_id': 123, 'ticket_id': 231}
        response = Mock()
        response.json = Mock(return_value={"responses": [{"category": "SD-WAN", "ticketStatus": "Resolved"}]})
        response.status_code = 200
        requests.get = Mock(return_value=response)
        bruin_ticket_response = BruinTicketResponse(logger, config.BRUIN_CONFIG, event_bus, bruin_client)
        await bruin_ticket_response.report_all_bruin_tickets(json.dumps(msg))
        assert requests.get.called
        assert requests.get.call_args[1]['params']['ClientId'] == msg['client_id']
        assert requests.get.call_args[1]['params']['TicketId'] == msg['ticket_id']
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert event_bus.publish_message.call_args[0][1] == '{"request_id": "123", "tickets": [], "status": 200}'
