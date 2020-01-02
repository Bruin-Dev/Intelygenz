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

        post_ticket_response = {"ticketIds": [123]}
        request_id = 123
        client_id = 321
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        category = 'Some Category'
        notes = []
        services = ['List of Services']
        contacts = ['List of Contacts']

        msg = {'request_id': request_id,
               'response_topic': response_topic,
               'clientId': client_id,
               'category': category,
               'services': services,
               'contacts': contacts
               }

        msg_published_in_topic = {
                                  'request_id': msg['request_id'],
                                  'ticketIds': post_ticket_response,
                                  'status': 200
                                 }
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_ticket = Mock(return_value=post_ticket_response)

        post_ticket = PostTicket(logger, event_bus, bruin_repository)
        await post_ticket.post_ticket(msg)

        post_ticket._bruin_repository.post_ticket.assert_called_once_with(
            client_id, category, services, notes, contacts
        )
        post_ticket._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )

    @pytest.mark.asyncio
    async def post_ticket_none_return_test(self):
        logger = Mock()
        post_ticket_response = None
        request_id = 123
        client_id = 321
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        category = 'Some Category'
        notes = ['List of Notes']
        services = ['List of Services']
        contacts = ['List of Contacts']

        msg = {'request_id': request_id,
               'response_topic': response_topic,
               'clientId': client_id,
               'category': category,
               'services': services,
               'notes': notes,
               'contacts': contacts
               }

        msg_published_in_topic = {
            'request_id': msg['request_id'],
            'ticketIds': post_ticket_response,
            'status': 500
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_ticket = Mock(return_value=post_ticket_response)

        post_ticket = PostTicket(logger, event_bus, bruin_repository)
        await post_ticket.post_ticket(msg)
        post_ticket._bruin_repository.post_ticket.assert_called_once_with(
            client_id, category, services, notes, contacts
        )
        post_ticket._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )
