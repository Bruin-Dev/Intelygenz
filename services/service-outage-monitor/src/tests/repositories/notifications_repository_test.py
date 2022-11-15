from unittest.mock import patch

import pytest
from application.repositories import notifications_repository as notifications_repository_module
from application.repositories.utils_repository import to_json_bytes
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


class TestNotificationsRepository:
    def instance_test(self, notifications_repository, nats_client):
        assert notifications_repository._nats_client is nats_client

    @pytest.mark.asyncio
    async def send_slack_message_test(self, notifications_repository):
        message = "Some message"

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        notifications_repository._nats_client.publish.assert_awaited_once_with(
            "notification.slack.request",
            to_json_bytes(
                {
                    "request_id": uuid_,
                    "body": {"message": message},
                }
            ),
        )

    @pytest.mark.asyncio
    async def notify_successful_reminder_note_append_test(self, notifications_repository):
        ticket_id = 12345
        serial_number = "VC1234567"

        await notifications_repository.notify_successful_reminder_note_append(
            ticket_id=ticket_id, serial_number=serial_number
        )

        message = (
            f"Service Outage reminder note posted for serial number {serial_number} of ticket {ticket_id}. "
            f"https://app.bruin.com/t/{ticket_id}"
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(message)
