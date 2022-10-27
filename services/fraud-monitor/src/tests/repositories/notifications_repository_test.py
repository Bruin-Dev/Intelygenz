from unittest.mock import patch

import pytest
from shortuuid import uuid

from application.repositories import notifications_repository as notifications_repository_module
from application.repositories.utils_repository import to_json_bytes
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


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
        service_number = "VC1234567"

        await notifications_repository.notify_successful_ticket_creation(
            ticket_id=ticket_id, service_number=service_number
        )

        message = (
            f"Fraud ticket has been created for service number {service_number}. "
            f"https://app.bruin.com/t/{ticket_id}"
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(message)

    @pytest.mark.asyncio
    async def notify_successful_reopen_test(self, notifications_repository):
        ticket_id = 12345
        service_number = "VC1234567"

        await notifications_repository.notify_successful_reopen(ticket_id=ticket_id, service_number=service_number)

        message = (
            f"Task for service number {service_number} of Fraud ticket {ticket_id} has been unresolved. "
            f"https://app.bruin.com/t/{ticket_id}"
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(message)

    @pytest.mark.asyncio
    async def notify_successful_note_append_test(self, notifications_repository):
        ticket_id = 12345
        service_number = "VC1234567"

        await notifications_repository.notify_successful_note_append(ticket_id=ticket_id, service_number=service_number)

        message = (
            f"Fraud note posted for service number {service_number} of ticket {ticket_id}. "
            f"https://app.bruin.com/t/{ticket_id}"
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(message)
