from unittest.mock import AsyncMock, Mock, patch

import pytest
from nats.aio.msg import Msg
from shortuuid import uuid

from application.repositories import email_repository as email_repository_module
from application.repositories import nats_error_response
from application.repositories.utils_repository import to_json_bytes
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(email_repository_module, "uuid", return_value=uuid_)


class TestEmailRepository:
    def instance_test(self, email_repository, nats_client, notifications_repository):
        assert email_repository._nats_client is nats_client
        assert email_repository._config is testconfig
        assert email_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_unread_emails__rpc_request_success_test(
        self, email_repository, make_get_unread_emails_request, get_unread_emails_response
    ):
        request = make_get_unread_emails_request(request_id=uuid_)
        response = get_unread_emails_response

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        email_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await email_repository.get_unread_emails()

        email_repository._nats_client.request.assert_awaited_once_with(
            "get.email.request", to_json_bytes(request), timeout=150
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_unread_emails__rpc_request_failing_test(self, email_repository, make_get_unread_emails_request):
        request = make_get_unread_emails_request(request_id=uuid_)

        email_repository._nats_client.request.side_effect = Exception
        email_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await email_repository.get_unread_emails()

        email_repository._nats_client.request.assert_awaited_once_with(
            "get.email.request", to_json_bytes(request), timeout=150
        )
        email_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_unread_emails__rpc_request_has_not_2xx_status_test(
        self, email_repository, make_get_unread_emails_request, gmail_500_response
    ):
        request = make_get_unread_emails_request(request_id=uuid_)
        response = gmail_500_response

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        email_repository._nats_client.request = AsyncMock(return_value=response_msg)
        email_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await email_repository.get_unread_emails()

        email_repository._nats_client.request.assert_awaited_once_with(
            "get.email.request", to_json_bytes(request), timeout=150
        )
        email_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response

    @pytest.mark.asyncio
    async def mark_email_as_read__rpc_request_success_test(
        self, email_repository, make_mark_email_as_read_request, mark_email_as_read_response
    ):
        msg_uid = "123456"
        request = make_mark_email_as_read_request(request_id=uuid_, msg_uid=msg_uid)
        response = mark_email_as_read_response

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        email_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await email_repository.mark_email_as_read(msg_uid)

        email_repository._nats_client.request.assert_awaited_once_with(
            "mark.email.read.request", to_json_bytes(request), timeout=150
        )
        assert result == response

    @pytest.mark.asyncio
    async def mark_email_as_read__rpc_request_failing_test(self, email_repository, make_mark_email_as_read_request):
        msg_uid = "123456"
        request = make_mark_email_as_read_request(request_id=uuid_, msg_uid=msg_uid)

        email_repository._nats_client.request.side_effect = Exception
        email_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await email_repository.mark_email_as_read(msg_uid)

        email_repository._nats_client.request.assert_awaited_once_with(
            "mark.email.read.request", to_json_bytes(request), timeout=150
        )
        email_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def mark_email_as_read__rpc_request_has_not_2xx_status_test(
        self, email_repository, make_mark_email_as_read_request, gmail_500_response
    ):
        msg_uid = "123456"
        request = make_mark_email_as_read_request(request_id=uuid_, msg_uid=msg_uid)
        response = gmail_500_response

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        email_repository._nats_client.request = AsyncMock(return_value=response_msg)
        email_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await email_repository.mark_email_as_read(msg_uid)

        email_repository._nats_client.request.assert_awaited_once_with(
            "mark.email.read.request", to_json_bytes(request), timeout=150
        )
        email_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response
