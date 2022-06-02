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
                "message": f"[{prefix}] {message}",
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def get_unread_emails__rpc_request_success_test(
        self, notifications_repository, make_get_unread_emails_request, get_unread_emails_response
    ):
        request = make_get_unread_emails_request(request_id=uuid_)
        response = get_unread_emails_response

        notifications_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            result = await notifications_repository.get_unread_emails()

        notifications_repository._event_bus.rpc_request.assert_awaited_once_with(
            "get.email.request", request, timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_unread_emails__rpc_request_failing_test(
        self, notifications_repository, make_get_unread_emails_request
    ):
        request = make_get_unread_emails_request(request_id=uuid_)

        notifications_repository._event_bus.rpc_request.side_effect = Exception
        notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await notifications_repository.get_unread_emails()

        notifications_repository._event_bus.rpc_request.assert_awaited_once_with(
            "get.email.request", request, timeout=90
        )
        notifications_repository._logger.error.assert_called_once()
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_unread_emails__rpc_request_has_not_2xx_status_test(
        self, notifications_repository, make_get_unread_emails_request, gmail_500_response
    ):
        request = make_get_unread_emails_request(request_id=uuid_)
        response = gmail_500_response

        notifications_repository._event_bus.rpc_request.return_value = response
        notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await notifications_repository.get_unread_emails()

        notifications_repository._event_bus.rpc_request.assert_awaited_once_with(
            "get.email.request", request, timeout=90
        )
        notifications_repository._logger.error.assert_called_once()
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response

    @pytest.mark.asyncio
    async def mark_email_as_read__rpc_request_success_test(
        self, notifications_repository, make_mark_email_as_read_request, mark_email_as_read_response
    ):
        msg_uid = "123456"
        request = make_mark_email_as_read_request(request_id=uuid_, msg_uid=msg_uid)
        response = mark_email_as_read_response

        notifications_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            result = await notifications_repository.mark_email_as_read(msg_uid)

        notifications_repository._event_bus.rpc_request.assert_awaited_once_with(
            "mark.email.read.request", request, timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def mark_email_as_read__rpc_request_failing_test(
        self, notifications_repository, make_mark_email_as_read_request
    ):
        msg_uid = "123456"
        request = make_mark_email_as_read_request(request_id=uuid_, msg_uid=msg_uid)

        notifications_repository._event_bus.rpc_request.side_effect = Exception
        notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await notifications_repository.mark_email_as_read(msg_uid)

        notifications_repository._event_bus.rpc_request.assert_awaited_once_with(
            "mark.email.read.request", request, timeout=90
        )
        notifications_repository._logger.error.assert_called_once()
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def mark_email_as_read__rpc_request_has_not_2xx_status_test(
        self, notifications_repository, make_mark_email_as_read_request, gmail_500_response
    ):
        msg_uid = "123456"
        request = make_mark_email_as_read_request(request_id=uuid_, msg_uid=msg_uid)
        response = gmail_500_response

        notifications_repository._event_bus.rpc_request.return_value = response
        notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await notifications_repository.mark_email_as_read(msg_uid)

        notifications_repository._event_bus.rpc_request.assert_awaited_once_with(
            "mark.email.read.request", request, timeout=90
        )
        notifications_repository._logger.error.assert_called_once()
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response

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
