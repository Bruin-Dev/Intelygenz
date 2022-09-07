from unittest.mock import patch

import pytest
from application.repositories import nats_error_response
from application.repositories import notifications_repository as notifications_repository_module
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


class TestNotificationsRepository:
    def instance_test(self, notifications_repository, logger, event_bus):
        assert notifications_repository._logger is logger
        assert notifications_repository._event_bus is event_bus
        assert notifications_repository._config is testconfig

    @pytest.mark.asyncio
    async def send_slack_message_test(self, notifications_repository):
        prefix = testconfig.LOG_CONFIG["name"]
        message = "Some message"

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        notifications_repository._event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                "request_id": uuid_,
                "body": {"message": f"[{prefix}] {message}"},
            },
            timeout=10,
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
