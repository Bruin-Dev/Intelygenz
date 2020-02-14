from unittest.mock import Mock

import pytest
from application.actions.post_ticket import PostTicket
from asynctest import CoroutineMock


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
    async def post_ticket_200_test(self):
        logger = Mock()
        logger.error = Mock()

        post_ticket_response = {"ticketIds": [123]}
        request_id = 123
        client_id = 321
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        category = 'Some Category'
        notes = ['some notes']
        services = ['List of Services']
        contacts = ['List of Contacts']

        msg = {'request_id': request_id,
               'response_topic': response_topic,
               'payload': {
                           'clientId': client_id,
                           'category': category,
                           'services': services,
                           'contacts': contacts,
                           'notes': notes
                           }
               }
        msg_published_in_topic = {
                                  'request_id': msg['request_id'],
                                  'ticketIds': post_ticket_response,
                                  'status': 200
                                 }
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_ticket = Mock(return_value={'body': post_ticket_response,
                                                          'status_code': 200})

        post_ticket = PostTicket(logger, event_bus, bruin_repository)
        await post_ticket.post_ticket(msg)

        logger.error.assert_not_called()

        post_ticket._bruin_repository.post_ticket.assert_called_once_with(
            msg['payload']
        )
        post_ticket._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )

    @pytest.mark.asyncio
    async def post_ticket_not_200_test(self):
        logger = Mock()
        logger.error = Mock()

        post_ticket_response = {"ticketIds": [123]}
        request_id = 123
        client_id = 321
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        category = 'Some Category'
        notes = ['some notes']
        services = ['List of Services']
        contacts = ['List of Contacts']

        msg = {'request_id': request_id,
               'response_topic': response_topic,
               'payload': {
                   'clientId': client_id,
                   'category': category,
                   'services': services,
                   'contacts': contacts,
                   'notes': notes
               }
               }
        msg_published_in_topic = {
            'request_id': msg['request_id'],
            'ticketIds': post_ticket_response,
            'status': 400
        }
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_ticket = Mock(return_value={'body': post_ticket_response,
                                                          'status_code': 400})

        post_ticket = PostTicket(logger, event_bus, bruin_repository)
        await post_ticket.post_ticket(msg)

        logger.error.assert_called()

        post_ticket._bruin_repository.post_ticket.assert_called_once_with(
            msg['payload']
        )
        post_ticket._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )

    @pytest.mark.asyncio
    async def post_ticket_no_notes_test(self):
        logger = Mock()

        post_ticket_response = {"ticketIds": [123]}
        request_id = 123
        client_id = 321
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        category = 'Some Category'
        services = ['List of Services']
        contacts = ['List of Contacts']

        msg = {'request_id': request_id,
               'response_topic': response_topic,
               'payload': {
                           'clientId': client_id,
                           'category': category,
                           'services': services,
                           'contacts': contacts,
                           }
               }
        payload_copy = msg['payload'].copy()
        payload_copy['notes'] = []
        msg_published_in_topic = {
                                  'request_id': msg['request_id'],
                                  'ticketIds': post_ticket_response,
                                  'status': 200
                                 }
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_ticket = Mock(return_value={'body': post_ticket_response,
                                                          'status_code': 200})

        post_ticket = PostTicket(logger, event_bus, bruin_repository)
        await post_ticket.post_ticket(msg)

        post_ticket._bruin_repository.post_ticket.assert_called_once_with(
            payload_copy
        )
        post_ticket._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )

    @pytest.mark.asyncio
    async def post_ticket_missing_keys_in_payload_test(self):
        logger = Mock()

        post_ticket_response = {"ticketIds": [123]}
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        category = 'Some Category'
        contacts = ['List of Contacts']

        msg = {'request_id': request_id,
               'response_topic': response_topic,
               'payload': {
                           'category': category,
                           'contacts': contacts,
                           }
               }

        msg_published_in_topic = {
                                  'request_id': msg['request_id'],
                                  'ticketIds': 'You must specify "clientId", "category", '
                                               '"services", "contacts" in the payload',
                                  'status': 400
                                 }
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_ticket = Mock(return_value={'body': post_ticket_response,
                                                          'status_code': 200})

        post_ticket = PostTicket(logger, event_bus, bruin_repository)
        await post_ticket.post_ticket(msg)

        post_ticket._bruin_repository.post_ticket.assert_not_called()
        post_ticket._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )

    @pytest.mark.asyncio
    async def post_ticket_missing_payload_test(self):
        logger = Mock()

        post_ticket_response = {"ticketIds": [123]}
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'

        msg = {'request_id': request_id,
               'response_topic': response_topic
               }

        msg_published_in_topic = {
                                  'request_id': msg['request_id'],
                                  'ticketIds': 'You must specify '
                                               '{.."payload":{"clientId", "category", "services", "contacts"},'
                                               ' in the request',
                                  'status': 400
                                 }
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_ticket = Mock(return_value={'body': post_ticket_response,
                                                          'status_code': 200})

        post_ticket = PostTicket(logger, event_bus, bruin_repository)
        await post_ticket.post_ticket(msg)

        post_ticket._bruin_repository.post_ticket.assert_not_called()
        post_ticket._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )
