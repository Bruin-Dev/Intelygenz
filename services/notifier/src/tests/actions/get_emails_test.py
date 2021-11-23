from unittest.mock import Mock

import pytest
from application.actions.get_emails import GetEmails
from asynctest import CoroutineMock

from config import testconfig as config


class TestGetEmails:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        email_reader_repository = Mock()

        get_emails = GetEmails(config, event_bus, logger, email_reader_repository)

        assert get_emails._logger == logger
        assert get_emails._config == config
        assert get_emails._event_bus == event_bus
        assert get_emails._email_reader_repository == email_reader_repository

    @pytest.mark.asyncio
    async def get_unread_emails_ok_test(self):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        email = 'fake@gmail.com'
        email_filter = ['filter@gmail.com']

        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": {
                        'email_account': email,
                        'email_filter': email_filter
            },
        }

        unread_emails = ['unread_email']
        unread_emails_response = {
                                    'body': unread_emails,
                                    'status': 200
        }
        event_bus_response = {
                                'request_id': request_id,
                                **unread_emails_response
        }
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        email_reader_repository = Mock()
        email_reader_repository.get_unread_emails = CoroutineMock(return_value=unread_emails_response)

        get_emails = GetEmails(config, event_bus, logger, email_reader_repository)

        await get_emails.get_unread_emails(msg_dict)

        email_reader_repository.get_unread_emails.assert_awaited_once_with(email, email_filter)
        event_bus.publish_message.assert_awaited_once_with(response_topic, event_bus_response)

    @pytest.mark.asyncio
    async def get_unread_emails_ko_no_body_test(self):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        email = 'fake@gmail.com'

        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
        }

        event_bus_response = {
                                'request_id': request_id,
                                'body': 'Must include "body" in request',
                                'status': 400
        }
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        email_reader_repository = Mock()
        email_reader_repository.get_unread_emails = CoroutineMock()

        get_emails = GetEmails(config, event_bus, logger, email_reader_repository)

        await get_emails.get_unread_emails(msg_dict)

        email_reader_repository.get_unread_emails.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic, event_bus_response)

    @pytest.mark.asyncio
    async def get_unread_emails_ko_no_email_or_email_filter_test(self):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        email = 'fake@gmail.com'

        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": {}
        }

        event_bus_response = {
                                'request_id': request_id,
                                'body': 'You must include "email_account" and "email_filter" '
                                        'in the "body" field of the response request',
                                'status': 400
        }
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        email_reader_repository = Mock()
        email_reader_repository.get_unread_emails = CoroutineMock()

        get_emails = GetEmails(config, event_bus, logger, email_reader_repository)

        await get_emails.get_unread_emails(msg_dict)

        email_reader_repository.get_unread_emails.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic, event_bus_response)
