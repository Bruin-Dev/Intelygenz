import json
from http import HTTPStatus
from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg


class TestMarkEmailAsRead:
    def instance_test(self, mark_email_as_read_action, email_reader_repository):
        assert mark_email_as_read_action._email_reader_repository == email_reader_repository

    @pytest.mark.asyncio
    async def mark_email_as_read_ok_test(self, mark_email_as_read_action):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        email = "fake@gmail.com"
        msg_uid = "123"
        payload = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": {"msg_uid": msg_uid, "email_account": email},
        }
        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(payload).encode()
        response_status = HTTPStatus.OK
        mark_emails_response = {"body": f"Email {msg_uid} marked as read", "status": response_status}
        mark_email_as_read_action._email_reader_repository.mark_as_read = AsyncMock(return_value=mark_emails_response)

        await mark_email_as_read_action(msg_mock)

        mark_email_as_read_action._email_reader_repository.mark_as_read.assert_awaited_once_with(msg_uid, email)

    @pytest.mark.asyncio
    async def mark_email_as_read_ko_empty_body_test(self, mark_email_as_read_action):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        payload = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": {},
        }
        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(payload).encode()
        mark_emails_response = {
            "body": 'You must include "msg_uid" and "email_account" in the "body" field of the response request',
            "status": 400,
        }
        mark_email_as_read_action._email_reader_repository.mark_as_read = AsyncMock()

        await mark_email_as_read_action(msg_mock)

        mark_email_as_read_action._email_reader_repository.mark_as_read.assert_not_awaited()

    @pytest.mark.asyncio
    async def mark_email_as_read_ko_no_body_test(self, mark_email_as_read_action):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        payload = {
            "request_id": request_id,
            "response_topic": response_topic,
        }
        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(payload).encode()
        mark_emails_response = {"body": 'Must include "body" in request', "status": 400}
        mark_email_as_read_action._email_reader_repository.mark_as_read = AsyncMock()

        await mark_email_as_read_action(msg_mock)

        mark_email_as_read_action._email_reader_repository.mark_as_read.assert_not_awaited()
