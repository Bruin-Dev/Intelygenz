from unittest.mock import Mock

import pytest
from application.actions.change_ticket_severity import ChangeTicketSeverity
from asynctest import CoroutineMock
from shortuuid import uuid

uuid_ = uuid()


class TestChangeTicketSeverity:
    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        action = ChangeTicketSeverity(logger, event_bus, bruin_repository)

        assert action._logger is logger
        assert action._event_bus is event_bus
        assert action._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def change_ticket_severity_ok_test(self):
        ticket_id = 12345
        severity_level = 2
        reason_for_change = "WTN has been under troubles for a long time"

        bruin_payload = {
            "severity": severity_level,
            "reason": reason_for_change,
        }

        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        request_message = {
            "request_id": uuid_,
            "response_topic": response_topic,
            "body": {
                "ticket_id": ticket_id,
                **bruin_payload,
            },
        }

        change_ticket_severity_response = {
            "body": {
                "TicketId": ticket_id,
                "Result": True,
            },
            "status": 200,
        }
        response_message = {
            "request_id": uuid_,
            **change_ticket_severity_response,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.change_ticket_severity = CoroutineMock(return_value=change_ticket_severity_response)

        action = ChangeTicketSeverity(logger, event_bus, bruin_repository)

        await action.change_ticket_severity(request_message)

        bruin_repository.change_ticket_severity.assert_awaited_once_with(ticket_id, bruin_payload)
        event_bus.publish_message.assert_awaited_once_with(response_topic, response_message)

    @pytest.mark.asyncio
    async def change_ticket_severity_with_body_missing_in_request_message_test(self):
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        request_message = {
            "request_id": uuid_,
            "response_topic": response_topic,
        }

        response_message = {
            "request_id": uuid_,
            "body": 'Must include "body" in the request message',
            "status": 400,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.change_ticket_severity = CoroutineMock()

        action = ChangeTicketSeverity(logger, event_bus, bruin_repository)

        await action.change_ticket_severity(request_message)

        bruin_repository.change_ticket_severity.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic, response_message)

    @pytest.mark.asyncio
    async def change_ticket_severity_with_mandatory_fields_missing_in_request_body_test(self):
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        request_message = {
            "request_id": uuid_,
            "response_topic": response_topic,
            "body": {
                "ticket_id": 123,
                # "severity" field missing on purpose
                "reason": "WTN has been under troubles for a long time",
            },
        }

        response_message = {
            "request_id": uuid_,
            "body": 'You must specify "ticket_id", "severity" and "reason" in the body',
            "status": 400,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.change_ticket_severity = CoroutineMock()

        action = ChangeTicketSeverity(logger, event_bus, bruin_repository)

        await action.change_ticket_severity(request_message)

        bruin_repository.change_ticket_severity.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic, response_message)
