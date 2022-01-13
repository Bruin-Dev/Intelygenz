import json
from unittest.mock import Mock

import pytest
from application.actions.mark_email_as_done import MarkEmailAsDone
from asynctest import CoroutineMock


class TestMarkEmailAsDone:

    def instance_test(self):
        mock_logger = Mock()
        event_bus = Mock()
        bruin_repo = Mock()
        resolve_ticket = MarkEmailAsDone(mock_logger, event_bus, bruin_repo)
        assert resolve_ticket._logger == mock_logger
        assert resolve_ticket._event_bus == event_bus
        assert resolve_ticket._bruin_repository == bruin_repo

    @pytest.mark.asyncio
    async def mark_email_as_done_no_body_test(self):
        mock_logger = Mock()

        request_id = 'some.id'
        response_topic = 'some.response'
        msg = {'request_id': request_id, 'response_topic': response_topic}

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.mark_email_as_done = CoroutineMock(return_value={})

        mark_email_as_done = MarkEmailAsDone(mock_logger, event_bus, bruin_repository)
        await mark_email_as_done.mark_email_as_done(msg)

        bruin_repository.mark_email_as_done.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic,
                                                           dict(request_id=request_id,
                                                                body='Must include "body" in request',
                                                                status=400))

    @pytest.mark.asyncio
    async def mark_email_as_done_no_email_id(self):
        mock_logger = Mock()

        request_id = 'some.id'
        response_topic = 'some.response'
        msg = {'request_id': request_id, 'body': {}, 'response_topic': response_topic}

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.mark_email_as_done = CoroutineMock(return_value={})

        mark_email_as_done = MarkEmailAsDone(mock_logger, event_bus, bruin_repository)
        await mark_email_as_done.mark_email_as_done(msg)

        bruin_repository.mark_email_as_done.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic,
                                                           dict(request_id=request_id,
                                                                body='You must include email_id in the request',
                                                                status=400))

    @pytest.mark.asyncio
    async def mark_email_as_done_200_test(self):
        mock_logger = Mock()

        request_id = 'some.id'
        response_topic = 'some.response'
        email_id = 1234
        msg = {'request_id': request_id, 'response_topic': response_topic, 'body': {'email_id': email_id}}
        response_body = {"success": True, "email_id": email_id}

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.mark_email_as_done = CoroutineMock(return_value={'body': response_body, 'status': 200})

        mark_email_as_done = MarkEmailAsDone(mock_logger, event_bus, bruin_repository)
        await mark_email_as_done.mark_email_as_done(msg)

        bruin_repository.mark_email_as_done.assert_awaited_once_with(email_id)
        event_bus.publish_message.assert_awaited_once_with(response_topic,
                                                           dict(request_id=request_id, body=response_body, status=200))
