from unittest.mock import patch

import pytest
from shortuuid import uuid

from application.repositories import notifications_repository as notifications_repository_module

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, 'uuid', return_value=uuid_)


class TestNotificationsRepository:
    def instance_test(self, notifications_repository, event_bus):
        assert notifications_repository._event_bus is event_bus

    @pytest.mark.asyncio
    async def send_slack_message_test(self, notifications_repository):
        message = "Some message"

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        notifications_repository._event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': message,
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def notify_successful_reminder_note_append_test(self, notifications_repository):
        ticket_id = 12345
        serial_number = 'VC1234567'

        await notifications_repository.notify_successful_reminder_note_append(
            ticket_id=ticket_id,
            serial_number=serial_number
        )

        message = (
            f'Service Outage reminder note posted for serial number {serial_number} of ticket {ticket_id}. '
            f'https://app.bruin.com/t/{ticket_id}'
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(message)
