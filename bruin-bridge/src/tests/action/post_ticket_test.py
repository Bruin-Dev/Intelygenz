import json
from unittest.mock import Mock

import pytest
from application.actions.post_ticket import PostTicket
from asynctest import CoroutineMock

from config import testconfig as config


class TestPostTicket:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()
        post_ticket = PostTicket(logger, event_bus, bruin_repository)
        assert post_ticket._logger is logger
        assert post_ticket._event_bus is event_bus
        assert post_ticket._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def post_ticket_test(self):
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()
        bruin_repository.post_ticket = Mock(return_value={"ticketIds": [123]})
        msg = {'request_id': 123,
               'response_topic': f'bruin.ticket.creation.response',
               'clientId': 321,
               'category': 'Some Category',
               'services': ['List of Services'],
               'contacts': ['List of Contacts']}
        post_ticket = PostTicket(logger, event_bus, bruin_repository)
        await post_ticket.post_ticket(json.dumps(msg))
        assert bruin_repository.post_ticket.called
        assert bruin_repository.post_ticket.call_args[0][0] == msg['clientId']
        assert bruin_repository.post_ticket.call_args[0][1] == msg['category']
        assert bruin_repository.post_ticket.call_args[0][2] == msg['services']
        assert bruin_repository.post_ticket.call_args[0][3] == []
        assert bruin_repository.post_ticket.call_args[0][4] == msg['contacts']
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert event_bus.publish_message.call_args[0][1] == json.dumps({'request_id': msg['request_id'],
                                                                        'ticketIds': {"ticketIds": [123]},
                                                                        'status': 200})

    @pytest.mark.asyncio
    async def post_ticket_none_return_test(self):
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()
        bruin_repository.post_ticket = Mock(return_value=None)
        msg = {'request_id': 123,
               'response_topic': f'bruin.ticket.creation.response',
               'clientId': 321,
               'category': 'Some Category',
               'services': ['List of Services'],
               'notes': ['List of Notes'],
               'contacts': ['List of Contacts']}
        post_ticket = PostTicket(logger, event_bus, bruin_repository)
        await post_ticket.post_ticket(json.dumps(msg))
        assert bruin_repository.post_ticket.called
        assert bruin_repository.post_ticket.call_args[0][0] == msg['clientId']
        assert bruin_repository.post_ticket.call_args[0][1] == msg['category']
        assert bruin_repository.post_ticket.call_args[0][2] == msg['services']
        assert bruin_repository.post_ticket.call_args[0][3] == msg['notes']
        assert bruin_repository.post_ticket.call_args[0][4] == msg['contacts']
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert event_bus.publish_message.call_args[0][1] == json.dumps({'request_id': msg['request_id'],
                                                                        'ticketIds': None,
                                                                        'status': 500})
