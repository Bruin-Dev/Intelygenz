import json
from unittest.mock import Mock

import pytest
from application.actions.post_note import PostNote
from asynctest import CoroutineMock

from config import testconfig as config


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
    async def post_note_test(self):
        logger = Mock()
        append_note_response = 'Note appended'
        request_id = 123
        ticket_id = 321
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        note_contents = 'Some Note'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'ticket_id': ticket_id,
            'note': note_contents,
        }
        msg_published_in_topic = {
            'request_id': request_id,
            'status': 200
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_ticket_note = Mock(return_value=append_note_response)

        post_note = PostNote(logger, event_bus, bruin_repository)
        await post_note.post_note(msg)

        post_note._bruin_repository.post_ticket_note.assert_called_once_with(
            ticket_id, note_contents
        )
        post_note._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )

    @pytest.mark.asyncio
    async def post_note_with_very_long_message_test(self):
        logger = Mock()
        append_note_response = 'Note appended'
        request_id = 123
        ticket_id = 321
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        note_contents = 'X' * 1500
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'ticket_id': ticket_id,
            'note': note_contents,
        }
        msg_published_in_topic = {
            'request_id': request_id,
            'status': 400
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_ticket_note = Mock(return_value=append_note_response)

        post_note = PostNote(logger, event_bus, bruin_repository)
        await post_note.post_note(msg)

        post_note._bruin_repository.post_ticket_note.assert_not_called()
        post_note._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )

    @pytest.mark.asyncio
    async def post_note_returning_none_result_test(self):
        logger = Mock()
        append_note_response = None
        request_id = 123
        ticket_id = 321
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        note_contents = 'Some Note'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'ticket_id': ticket_id,
            'note': note_contents,
        }
        msg_published_in_topic = {
            'request_id': request_id,
            'status': 500
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_ticket_note = Mock(return_value=append_note_response)

        post_note = PostNote(logger, event_bus, bruin_repository)
        await post_note.post_note(msg)

        post_note._bruin_repository.post_ticket_note.assert_called_once_with(
            ticket_id, note_contents
        )
        post_note._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )
