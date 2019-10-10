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
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()
        bruin_repository.post_ticket_note = Mock(return_value='Note appeneded')
        msg = {'request_id': 123,
               'response_topic': f'bruin.ticket.note.append.response',
               'ticket_id': 321,
               'note': 'Some Note'}
        post_note = PostNote(logger, event_bus, bruin_repository)
        await post_note.post_note(json.dumps(msg))
        assert bruin_repository.post_ticket_note.called
        assert bruin_repository.post_ticket_note.call_args[0][0] == msg['ticket_id']
        assert bruin_repository.post_ticket_note.call_args[0][1] == msg['note']
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert event_bus.publish_message.call_args[0][1] == json.dumps({'request_id': msg['request_id'],
                                                                        'status': 200})

    @pytest.mark.asyncio
    async def post_note_long_message_test(self):
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()
        bruin_repository.post_ticket_note = Mock(return_value='Note appeneded')
        long_note = "This note is supposed to be 1500 characters long!!This note is supposed to be 1500 characters " \
                    "long!!This note is supposed to be 1500 characters long!!This note is supposed to be 1500 " \
                    "characters long!!This note is supposed to be 1500 characters long!!This note is supposed to be " \
                    "1500 characters long!!This note is supposed to be 1500 characters long!!This note is supposed to "\
                    "be 1500 characters long!!This note is supposed to be 1500 characters long!!This note is supposed "\
                    "to be 1500 characters long!!This note is supposed to be 1500 characters long!!This note is " \
                    "supposed to be 1500 characters long!!This note is supposed to be 1500 characters long!!This note "\
                    "is supposed to be 1500 characters long!!This note is supposed to be 1500 characters long!!This " \
                    "note is supposed to be 1500 characters long!!This note is supposed to be 1500 characters " \
                    "long!!This note is supposed to be 1500 characters long!!This note is supposed to be 1500 " \
                    "characters long!!This note is supposed to be 1500 characters long!!This note is supposed to be " \
                    "1500 characters long!!This note is supposed to be 1500 characters long!!This note is supposed to "\
                    "be 1500 characters long!!This note is supposed to be 1500 characters long!!This note is supposed "\
                    "to be 1500 characters long!!This note is supposed to be 1500 characters long!!!!This note is " \
                    "supposed to be 1500 characters long!!This note is supposed to be 1500 characters long!!This note "\
                    "is supposed to be 1500 characters long!!This note is supposed to be 1500 characters long!! "
        msg = {'request_id': 123,
               'response_topic': f'bruin.ticket.note.append.response',
               'ticket_id': 321,
               'note': long_note}
        post_note = PostNote(logger, event_bus, bruin_repository)
        await post_note.post_note(json.dumps(msg))
        assert bruin_repository.post_ticket_note.called is False
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert event_bus.publish_message.call_args[0][1] == json.dumps({'request_id': msg['request_id'],
                                                                        'status': 400})

    @pytest.mark.asyncio
    async def post_note_none_return_test(self):
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()
        bruin_repository.post_ticket_note = Mock(return_value=None)
        msg = {'request_id': 123,
               'response_topic': f'bruin.ticket.note.append.response',
               'ticket_id': 321,
               'note': 'Some Note'}
        post_note = PostNote(logger, event_bus, bruin_repository)
        await post_note.post_note(json.dumps(msg))
        assert bruin_repository.post_ticket_note.called
        assert bruin_repository.post_ticket_note.call_args[0][0] == msg['ticket_id']
        assert bruin_repository.post_ticket_note.call_args[0][1] == msg['note']
        assert event_bus.publish_message.called
        assert event_bus.publish_message.call_args[0][0] == msg['response_topic']
        assert event_bus.publish_message.call_args[0][1] == json.dumps({'request_id': msg['request_id'],
                                                                        'status': 500})
