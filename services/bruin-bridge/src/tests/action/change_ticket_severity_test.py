from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.change_ticket_severity import ChangeTicketSeverity
from application.repositories.utils_repository import to_json_bytes


class TestChangeTicketSeverity:
    def instance_test(self):
        bruin_repository = Mock()

        action = ChangeTicketSeverity(bruin_repository)

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

        request_message = {
            "body": {
                "ticket_id": ticket_id,
                **bruin_payload,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request_message)

        change_ticket_severity_response = {
            "body": {
                "TicketId": ticket_id,
                "Result": True,
            },
            "status": 200,
        }
        response_message = {
            **change_ticket_severity_response,
        }

        bruin_repository = Mock()
        bruin_repository.change_ticket_severity = AsyncMock(return_value=change_ticket_severity_response)

        action = ChangeTicketSeverity(bruin_repository)

        await action(request_msg)

        bruin_repository.change_ticket_severity.assert_awaited_once_with(ticket_id, bruin_payload)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_message))

    @pytest.mark.asyncio
    async def change_ticket_severity_with_body_missing_in_request_message_test(self):
        request_message = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request_message)

        response_message = {
            "body": 'Must include "body" in the request message',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.change_ticket_severity = AsyncMock()

        action = ChangeTicketSeverity(bruin_repository)

        await action(request_msg)

        bruin_repository.change_ticket_severity.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_message))

    @pytest.mark.asyncio
    async def change_ticket_severity_with_mandatory_fields_missing_in_request_body_test(self):
        request_message = {
            "body": {
                "ticket_id": 123,
                # "severity" field missing on purpose
                "reason": "WTN has been under troubles for a long time",
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request_message)

        response_message = {
            "body": 'You must specify "ticket_id", "severity" and "reason" in the body',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.change_ticket_severity = AsyncMock()

        action = ChangeTicketSeverity(bruin_repository)

        await action(request_msg)

        bruin_repository.change_ticket_severity.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_message))
