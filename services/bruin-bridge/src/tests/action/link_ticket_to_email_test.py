import json
from unittest.mock import Mock

import pytest
from application.actions.link_ticket_to_email import LinkTicketToEmail
from asynctest import CoroutineMock


class TestLinkTicketToEmail:

    def instance_test(self):
        mock_logger = Mock()
        event_bus = Mock()
        bruin_repo = Mock()
        resolve_ticket = LinkTicketToEmail(mock_logger, event_bus, bruin_repo)
        assert resolve_ticket._logger == mock_logger
        assert resolve_ticket._event_bus == event_bus
        assert resolve_ticket._bruin_repository == bruin_repo

    @pytest.mark.asyncio
    async def link_ticket_to_email_no_body_test(self):
        mock_logger = Mock()

        request_id = 'some.id'
        response_topic = 'some.response'
        msg = {'request_id': request_id, 'response_topic': response_topic}

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.link_ticket_to_email = CoroutineMock(return_value={})

        link_ticket_to_email = LinkTicketToEmail(mock_logger, event_bus, bruin_repository)
        await link_ticket_to_email.link_ticket_to_email(msg)

        bruin_repository.link_ticket_to_email.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic,
                                                           dict(request_id=request_id,
                                                                body='Must include "body" in request',
                                                                status=400))

    @pytest.mark.asyncio
    async def link_ticket_to_email_no_ticket_id(self):
        mock_logger = Mock()

        request_id = 'some.id'
        response_topic = 'some.response'
        msg = {'request_id': request_id, 'body': {"email_id": 1234}, 'response_topic': response_topic}

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.link_ticket_to_email = CoroutineMock(return_value={})

        link_ticket_to_email = LinkTicketToEmail(mock_logger, event_bus, bruin_repository)
        await link_ticket_to_email.link_ticket_to_email(msg)

        bruin_repository.link_ticket_to_email.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic,
                                                           dict(request_id=request_id,
                                                                body='You must include email_id in the request',
                                                                status=400))

    @pytest.mark.asyncio
    async def link_ticket_to_email_200_test(self):
        mock_logger = Mock()

        request_id = 'some.id'
        response_topic = 'some.response'
        email_id = 1234
        ticket_id = 5678
        msg = {'request_id': request_id, 'response_topic': response_topic,
               'body': {'email_id': email_id, 'ticket_id': ticket_id}}
        response_body = {
            "Success": True,
            "EmailId": email_id,
            "TicketId": ticket_id,
            "TotalEmailAffected": 3,
            "Warnings": []
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.link_ticket_to_email = CoroutineMock(return_value={'body': response_body, 'status': 200})

        link_ticket_to_email = LinkTicketToEmail(mock_logger, event_bus, bruin_repository)
        await link_ticket_to_email.link_ticket_to_email(msg)

        bruin_repository.link_ticket_to_email.assert_awaited_once_with(ticket_id, email_id)
        event_bus.publish_message.assert_awaited_once_with(response_topic,
                                                           dict(request_id=request_id, body=response_body, status=200))
