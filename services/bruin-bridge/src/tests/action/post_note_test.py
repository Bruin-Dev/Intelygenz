from unittest.mock import Mock

import pytest
from application.actions.post_note import PostNote
from asynctest import CoroutineMock


class TestPostNote:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        post_note = PostNote(logger, event_bus, bruin_repository)

        assert post_note._logger is logger
        assert post_note._event_bus is event_bus
        assert post_note._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def post_note_no_body_test(self):
        logger = Mock()
        append_note_response = 'Note appended'
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
        }
        msg_published_in_topic = {
            'request_id': request_id,
            'body': 'Must include "body" in request',
            'status': 400
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_ticket_note = CoroutineMock(return_value=append_note_response)

        post_note = PostNote(logger, event_bus, bruin_repository)
        await post_note.post_note(msg)

        post_note._bruin_repository.post_ticket_note.assert_not_awaited()
        post_note._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )

    @pytest.mark.asyncio
    async def post_note_no_ticket_id_or_note_test(self):
        logger = Mock()
        append_note_response = 'Note appended'
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        msg = {
            'request_id': request_id,
            'body': {},
            'response_topic': response_topic,
        }
        msg_published_in_topic = {
            'request_id': request_id,
            'body': 'You must include "ticket_id" and "note" in the "body" field of the response request',
            'status': 400
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_ticket_note = CoroutineMock(return_value=append_note_response)

        post_note = PostNote(logger, event_bus, bruin_repository)
        await post_note.post_note(msg)

        post_note._bruin_repository.post_ticket_note.assert_not_awaited()
        post_note._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )

    @pytest.mark.asyncio
    async def post_note_200_test(self):
        logger = Mock()
        append_note_response = {'body': 'Note appended', 'status': 200}
        request_id = 123
        ticket_id = 321
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        note_contents = 'Some Note'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': {
                     'ticket_id': ticket_id,
                     'note': note_contents,
            }
        }
        msg_published_in_topic = {
            'request_id': request_id,
            'body': append_note_response['body'],
            'status': 200
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_ticket_note = CoroutineMock(return_value=append_note_response)

        post_note = PostNote(logger, event_bus, bruin_repository)
        await post_note.post_note(msg)

        post_note._bruin_repository.post_ticket_note.assert_awaited_once_with(
            ticket_id, note_contents, service_numbers=None
        )
        post_note._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )

    @pytest.mark.asyncio
    async def post_note_with_optional_service_numbers_list_test(self):
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'

        ticket_id = 321
        note_contents = 'Some Note'
        service_numbers = ['VC1234567']

        append_note_response = {'body': 'Note appended', 'status': 200}

        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': {
                'ticket_id': ticket_id,
                'note': note_contents,
                'service_numbers': service_numbers,
            }
        }
        msg_published_in_topic = {
            'request_id': request_id,
            'body': append_note_response['body'],
            'status': 200
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_ticket_note = CoroutineMock(return_value=append_note_response)

        post_note = PostNote(logger, event_bus, bruin_repository)
        await post_note.post_note(msg)

        post_note._bruin_repository.post_ticket_note.assert_awaited_once_with(
            ticket_id, note_contents, service_numbers=service_numbers
        )
        post_note._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )
