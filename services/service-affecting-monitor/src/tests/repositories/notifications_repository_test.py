import json
from typing import Any
from unittest.mock import patch

import pytest
from application import AffectingTroubles
from application.repositories import notifications_repository as notifications_repository_module
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


class TestNotificationsRepository:
    def instance_test(self, notifications_repository, nats_client):
        assert notifications_repository._nats_client is nats_client
        assert notifications_repository._config is testconfig

    @pytest.mark.asyncio
    async def send_slack_message_test(self, notifications_repository):
        prefix = testconfig.LOG_CONFIG["name"]
        message = "Some message"

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        notifications_repository._nats_client.publish.assert_awaited_once_with(
            "notification.slack.request",
            to_json_bytes(
                {
                    "request_id": uuid_,
                    "body": {"message": f"[{prefix}] {message}"},
                }
            ),
        )

    @pytest.mark.asyncio
    async def notify_successful_ticket_creation_test(self, notifications_repository):
        ticket_id = 12345
        serial_number = "VC1234567"
        trouble = AffectingTroubles.LATENCY

        await notifications_repository.notify_successful_ticket_creation(
            ticket_id=ticket_id,
            serial_number=serial_number,
            trouble=trouble,
        )

        message = (
            f"Service Affecting ticket has been created for serial number {serial_number}. Detected trouble was "
            f"{trouble.value.upper()}. https://app.bruin.com/t/{ticket_id}"
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(message)

    @pytest.mark.asyncio
    async def notify_successful_reopen_test(self, notifications_repository):
        ticket_id = 12345
        serial_number = "VC1234567"
        trouble = AffectingTroubles.LATENCY

        await notifications_repository.notify_successful_reopen(
            ticket_id=ticket_id,
            serial_number=serial_number,
            trouble=trouble,
        )

        message = (
            f"Task for serial number {serial_number} of Service Affecting ticket {ticket_id} has been unresolved. "
            f"Detected trouble was {trouble.value.upper()}. https://app.bruin.com/t/{ticket_id}"
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(message)

    @pytest.mark.asyncio
    async def notify_successful_autoresolve_test(self, notifications_repository):
        ticket_id = 12345
        serial_number = "VC1234567"

        await notifications_repository.notify_successful_autoresolve(ticket_id=ticket_id, serial_number=serial_number)

        message = (
            f"Task for serial number {serial_number} of Service Affecting ticket {ticket_id} has been autoresolved. "
            f"Details at https://app.bruin.com/t/{ticket_id}"
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(message)

    @pytest.mark.asyncio
    async def notify_successful_ticket_forward_test(self, notifications_repository):
        ticket_id = 12345
        serial_number = "VC1234567"

        await notifications_repository.notify_successful_ticket_forward(
            ticket_id=ticket_id, serial_number=serial_number
        )

        message = (
            f"Task for serial number {serial_number} of Service Affecting ticket {ticket_id} has been forwarded to "
            "the HNOC queue"
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(message)

    @pytest.mark.asyncio
    async def notify_successful_note_append_test(self, notifications_repository):
        ticket_id = 12345
        serial_number = "VC1234567"
        trouble = AffectingTroubles.LATENCY

        await notifications_repository.notify_successful_note_append(
            ticket_id=ticket_id,
            serial_number=serial_number,
            trouble=trouble,
        )

        message = (
            f"Service Affecting trouble note posted for serial number {serial_number} of ticket {ticket_id}. "
            f"Detected trouble was {trouble.value.upper()}. https://app.bruin.com/t/{ticket_id}"
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(message)

    @pytest.mark.asyncio
    async def notify_successful_reminder_note_append_test(self, notifications_repository):
        ticket_id = 12345
        serial_number = "VC1234567"

        await notifications_repository.notify_successful_reminder_note_append(
            ticket_id=ticket_id, serial_number=serial_number
        )

        message = (
            f"Service Affecting reminder note posted for serial number {serial_number} of ticket {ticket_id}. "
            f"https://app.bruin.com/t/{ticket_id}"
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(message)
