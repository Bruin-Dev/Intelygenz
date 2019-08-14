import json
from unittest.mock import Mock

import pytest
from application.actions.get_tickets import GetTicket
from asynctest import CoroutineMock

from config import testconfig as config


class TestGetTicket:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()
        bruin_ticket_response = GetTicket(logger, config.BRUIN_CONFIG, event_bus, bruin_repository)
        assert bruin_ticket_response._logger is logger
        assert bruin_ticket_response._config is config.BRUIN_CONFIG
        assert bruin_ticket_response._event_bus is event_bus
        assert bruin_ticket_response._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def report_all_bruin_tickets_no_ticket_id_test(self):
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()
        bruin_repository.get_all_filtered_tickets = Mock(return_value=['Some ticket list'])
        msg = {'request_id': "123", 'response_topic': 'bruin.ticket.response',
               'client_id': 123, 'ticket_status': ['New', 'In-Progress'], 'category': 'SD-WAN'}
        bruin_ticket_response = GetTicket(logger, config.BRUIN_CONFIG, event_bus, bruin_repository)
        await bruin_ticket_response.get_all_tickets(json.dumps(msg))
        assert bruin_repository.get_all_filtered_tickets.called
        assert bruin_repository.get_all_filtered_tickets.call_args[0][0] == msg['client_id']
        assert bruin_repository.get_all_filtered_tickets.call_args[0][1] == ''
        assert bruin_repository.get_all_filtered_tickets.call_args[0][2] == msg['ticket_status']
        assert bruin_repository.get_all_filtered_tickets.call_args[0][3] == msg['category']
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
        bruin_repository = Mock()
        bruin_repository.get_all_filtered_tickets = Mock(return_value=['Some ticket list'])
        msg = {'request_id': "123", 'response_topic': 'bruin.ticket.response',
               'client_id': 123, 'ticket_id': 321, 'ticket_status': ['New', 'In-Progress'], 'category': 'SD-WAN'}
        bruin_ticket_response = GetTicket(logger, config.BRUIN_CONFIG, event_bus, bruin_repository)
        await bruin_ticket_response.get_all_tickets(json.dumps(msg))
        assert bruin_repository.get_all_filtered_tickets.called
        assert bruin_repository.get_all_filtered_tickets.call_args[0][0] == msg['client_id']
        assert bruin_repository.get_all_filtered_tickets.call_args[0][1] == msg['ticket_id']
        assert bruin_repository.get_all_filtered_tickets.call_args[0][2] == msg['ticket_status']
        assert bruin_repository.get_all_filtered_tickets.call_args[0][3] == msg['category']
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
        bruin_repository = Mock()
        bruin_repository.get_all_filtered_tickets = Mock(return_value=None)
        msg = {'request_id': "123", 'response_topic': 'bruin.ticket.response',
               'client_id': 123, 'ticket_id': 321, 'ticket_status': ['New', 'In-Progress'], 'category': 'SD-WAN'}
        bruin_ticket_response = GetTicket(logger, config.BRUIN_CONFIG, event_bus, bruin_repository)
        await bruin_ticket_response.get_all_tickets(json.dumps(msg))
        assert bruin_repository.get_all_filtered_tickets.called
        assert bruin_repository.get_all_filtered_tickets.call_args[0][0] == msg['client_id']
        assert bruin_repository.get_all_filtered_tickets.call_args[0][1] == msg['ticket_id']
        assert bruin_repository.get_all_filtered_tickets.call_args[0][2] == msg['ticket_status']
        assert bruin_repository.get_all_filtered_tickets.call_args[0][3] == msg['category']
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert event_bus.publish_message.call_args[0][1] == json.dumps({'request_id': msg['request_id'],
                                                                        'tickets': None,
                                                                        'status': 500})
