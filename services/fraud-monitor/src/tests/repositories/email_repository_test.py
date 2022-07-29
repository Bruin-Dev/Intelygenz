from unittest.mock import patch

import pytest
from application.repositories import email_repository as email_repository_module
from application.repositories import nats_error_response
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(email_repository_module, "uuid", return_value=uuid_)


class TestEmailRepository:
    def instance_test(self, email_repository, logger, event_bus, notifications_repository):
        assert email_repository._logger is logger
        assert email_repository._event_bus is event_bus
        assert email_repository._config is testconfig
        assert email_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_unread_emails__rpc_request_success_test(
        self, email_repository, make_get_unread_emails_request, get_unread_emails_response
    ):
        request = make_get_unread_emails_request(request_id=uuid_)
        response = get_unread_emails_response

        email_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            result = await email_repository.get_unread_emails()

        email_repository._event_bus.rpc_request.assert_awaited_once_with("get.email.request", request, timeout=90)
        assert result == response

    @pytest.mark.asyncio
    async def get_unread_emails__rpc_request_failing_test(self, email_repository, make_get_unread_emails_request):
        request = make_get_unread_emails_request(request_id=uuid_)

        email_repository._event_bus.rpc_request.side_effect = Exception
        email_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await email_repository.get_unread_emails()

        email_repository._event_bus.rpc_request.assert_awaited_once_with("get.email.request", request, timeout=90)
        email_repository._logger.error.assert_called_once()
        email_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_unread_emails__rpc_request_has_not_2xx_status_test(
        self, email_repository, make_get_unread_emails_request, gmail_500_response
    ):
        request = make_get_unread_emails_request(request_id=uuid_)
        response = gmail_500_response

        email_repository._event_bus.rpc_request.return_value = response
        email_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await email_repository.get_unread_emails()

        email_repository._event_bus.rpc_request.assert_awaited_once_with("get.email.request", request, timeout=90)
        email_repository._logger.error.assert_called_once()
        email_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response

    @pytest.mark.asyncio
    async def mark_email_as_read__rpc_request_success_test(
        self, email_repository, make_mark_email_as_read_request, mark_email_as_read_response
    ):
        msg_uid = "123456"
        request = make_mark_email_as_read_request(request_id=uuid_, msg_uid=msg_uid)
        response = mark_email_as_read_response

        email_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            result = await email_repository.mark_email_as_read(msg_uid)

        email_repository._event_bus.rpc_request.assert_awaited_once_with("mark.email.read.request", request, timeout=90)
        assert result == response

    @pytest.mark.asyncio
    async def mark_email_as_read__rpc_request_failing_test(self, email_repository, make_mark_email_as_read_request):
        msg_uid = "123456"
        request = make_mark_email_as_read_request(request_id=uuid_, msg_uid=msg_uid)

        email_repository._event_bus.rpc_request.side_effect = Exception
        email_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await email_repository.mark_email_as_read(msg_uid)

        email_repository._event_bus.rpc_request.assert_awaited_once_with("mark.email.read.request", request, timeout=90)
        email_repository._logger.error.assert_called_once()
        email_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def mark_email_as_read__rpc_request_has_not_2xx_status_test(
        self, email_repository, make_mark_email_as_read_request, gmail_500_response
    ):
        msg_uid = "123456"
        request = make_mark_email_as_read_request(request_id=uuid_, msg_uid=msg_uid)
        response = gmail_500_response

        email_repository._event_bus.rpc_request.return_value = response
        email_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await email_repository.mark_email_as_read(msg_uid)

        email_repository._event_bus.rpc_request.assert_awaited_once_with("mark.email.read.request", request, timeout=90)
        email_repository._logger.error.assert_called_once()
        email_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response
