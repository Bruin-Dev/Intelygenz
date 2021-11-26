import json
from unittest.mock import Mock

import pytest
from application.actions.resolve_ticket import ResolveTicket
from asynctest import CoroutineMock


class TestResolveTicket:

    def instance_test(self):
        mock_logger = Mock()
        event_bus = Mock()
        bruin_repo = Mock()
        resolve_ticket = ResolveTicket(mock_logger, event_bus, bruin_repo)
        assert resolve_ticket._logger == mock_logger
        assert resolve_ticket._event_bus == event_bus
        assert resolve_ticket._bruin_repository == bruin_repo

    @pytest.mark.asyncio
    async def resolve_ticket_no_ticket_id_no_body_test(self):
        mock_logger = Mock()

        request_id = 'some.id'
        response_topic = 'some.response'
        msg = {'request_id': request_id, 'response_topic': response_topic}

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repo = Mock()
        bruin_repo.resolve_ticket = CoroutineMock(return_value={'body': 'Success', 'status': 200})

        resolve_ticket = ResolveTicket(mock_logger, event_bus, bruin_repo)
        await resolve_ticket.resolve_ticket(msg)

        bruin_repo.resolve_ticket.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic,
                                                           dict(request_id=request_id,
                                                                body='Must include "body" in request',
                                                                status=400))

    @pytest.mark.asyncio
    async def resolve_ticket_no_ticket_id_no_detail_id_test(self):
        mock_logger = Mock()

        request_id = 'some.id'
        response_topic = 'some.response'
        msg = {'request_id': request_id, 'body': {}, 'response_topic': response_topic}

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repo = Mock()
        bruin_repo.resolve_ticket = CoroutineMock(return_value={'body': 'Success', 'status': 200})

        resolve_ticket = ResolveTicket(mock_logger, event_bus, bruin_repo)
        await resolve_ticket.resolve_ticket(msg)

        bruin_repo.resolve_ticket.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic,
                                                           dict(request_id=request_id,
                                                                body='You must include ticket_id'
                                                                     ' and detail_id in the request',
                                                                status=400))

    @pytest.mark.asyncio
    async def resolve_ticket_200_test(self):
        mock_logger = Mock()

        request_id = 'some.id'
        response_topic = 'some.response'
        ticket_id = 123
        detail_id = 432
        msg = {'request_id': request_id, 'response_topic': response_topic, 'body': {'ticket_id': ticket_id,
               'detail_id': detail_id}}

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repo = Mock()
        bruin_repo.resolve_ticket = CoroutineMock(return_value={'body': 'Success', 'status': 200})

        resolve_ticket = ResolveTicket(mock_logger, event_bus, bruin_repo)
        await resolve_ticket.resolve_ticket(msg)

        bruin_repo.resolve_ticket.assert_awaited_once_with(ticket_id, detail_id)
        event_bus.publish_message.assert_awaited_once_with(response_topic,
                                                           dict(request_id=request_id, body="Success", status=200))