from unittest.mock import Mock

import pytest
from application.actions.mark_email_as_read import MarkEmailAsRead
from asynctest import CoroutineMock

from config import testconfig as config


class TestGetEmails:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        email_reader_repository = Mock()

        mark_emails = MarkEmailAsRead(config, event_bus, logger, email_reader_repository)

        assert mark_emails._logger == logger
        assert mark_emails._config == config
        assert mark_emails._event_bus == event_bus
        assert mark_emails._email_reader_repository == email_reader_repository

    @pytest.mark.asyncio
    async def mark_email_as_read_ok_test(self):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        email = 'fake@gmail.com'
        msg_uid = '123'

        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": {
                'msg_uid': msg_uid,
                'email_account': email
            },
        }

        mark_emails_response = {
            'body': f'Email {msg_uid} marked as read',
            'status': 200
        }
        event_bus_response = {
            'request_id': request_id,
            **mark_emails_response
        }

        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        email_reader_repository = Mock()
        email_reader_repository.mark_as_read = Mock(return_value=mark_emails_response)

        mark_emails = MarkEmailAsRead(config, event_bus, logger, email_reader_repository)

        await mark_emails.mark_email_as_read(msg_dict)

        email_reader_repository.mark_as_read.assert_called_once_with(msg_uid, email)
        event_bus.publish_message.assert_awaited_once_with(response_topic, event_bus_response)

    @pytest.mark.asyncio
    async def mark_email_as_read_ko_empty_body_test(self):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        email = 'fake@gmail.com'
        msg_uid = '123'

        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": {},
        }

        mark_emails_response = {
            'body': 'You must include "msg_uid" and "email_account" in the "body" field of the response request',
            'status': 400
        }
        event_bus_response = {
            'request_id': request_id,
            **mark_emails_response
        }

        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        email_reader_repository = Mock()
        email_reader_repository.mark_as_read = Mock()

        mark_emails = MarkEmailAsRead(config, event_bus, logger, email_reader_repository)

        await mark_emails.mark_email_as_read(msg_dict)

        email_reader_repository.mark_as_read.assert_not_called()
        event_bus.publish_message.assert_awaited_once_with(response_topic, event_bus_response)

    @pytest.mark.asyncio
    async def mark_email_as_read_ko_no_body_test(self):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        email = 'fake@gmail.com'
        msg_uid = '123'

        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
        }

        mark_emails_response = {
            'body': 'Must include "body" in request',
            'status': 400
        }
        event_bus_response = {
            'request_id': request_id,
            **mark_emails_response
        }

        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        email_reader_repository = Mock()
        email_reader_repository.mark_as_read = Mock()

        mark_emails = MarkEmailAsRead(config, event_bus, logger, email_reader_repository)

        await mark_emails.mark_email_as_read(msg_dict)

        email_reader_repository.mark_as_read.assert_not_called()
        event_bus.publish_message.assert_awaited_once_with(response_topic, event_bus_response)
