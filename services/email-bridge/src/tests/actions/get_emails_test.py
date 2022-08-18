import json
from http import HTTPStatus
from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg


class TestGetEmails:
    def instance_test(self, get_emails_action, email_reader_repository):
        assert get_emails_action._email_reader_repository == email_reader_repository

    @pytest.mark.asyncio
    async def get_unread_emails_ok_test(self, get_emails_action):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        email = "fake@gmail.com"
        email_filter = ["filter@gmail.com"]
        lookup_days = hash("any_days")
        payload = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": {
                "email_account": email,
                "email_filter": email_filter,
                "lookup_days": lookup_days,
            },
        }
        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(payload).encode()
        response_status = HTTPStatus.OK
        unread_emails = ["unread_email"]
        unread_emails_response = {"body": unread_emails, "status": response_status}
        get_emails_action._email_reader_repository.get_unread_emails = AsyncMock(return_value=unread_emails_response)

        await get_emails_action(msg_mock)

        get_emails_action._email_reader_repository.get_unread_emails.assert_awaited_once_with(
            email, email_filter, lookup_days
        )

    @pytest.mark.asyncio
    async def get_unread_emails_ko_no_body_test(self, get_emails_action):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        payload = {
            "request_id": request_id,
            "response_topic": response_topic,
        }
        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(payload).encode()
        get_emails_action._email_reader_repository.get_unread_emails = AsyncMock()

        await get_emails_action(msg_mock)

        get_emails_action._email_reader_repository.get_unread_emails.assert_not_awaited()

    @pytest.mark.asyncio
    async def get_unread_emails_ko_missing_parameters_test(self, get_emails_action):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"

        payload = {"request_id": request_id, "response_topic": response_topic, "body": {}}
        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(payload).encode()
        get_emails_action._email_reader_repository.get_unread_emails = AsyncMock()

        await get_emails_action(msg_mock)

        get_emails_action._email_reader_repository.get_unread_emails.assert_not_awaited()
