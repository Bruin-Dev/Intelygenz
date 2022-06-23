import pytest
from asynctest import CoroutineMock
from config import testconfig as config


class TestGetEmails:
    def instance_test(self, get_emails_action, logger, event_bus, email_reader_repository):
        assert get_emails_action._logger == logger
        assert get_emails_action._config == config
        assert get_emails_action._event_bus == event_bus
        assert get_emails_action._email_reader_repository == email_reader_repository

    @pytest.mark.asyncio
    async def get_unread_emails_ok_test(self, get_emails_action):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        email = "fake@gmail.com"
        email_filter = ["filter@gmail.com"]
        lookup_days = hash("any_days")

        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": {
                "email_account": email,
                "email_filter": email_filter,
                "lookup_days": lookup_days,
            },
        }

        unread_emails = ["unread_email"]
        unread_emails_response = {"body": unread_emails, "status": 200}
        event_bus_response = {"request_id": request_id, **unread_emails_response}
        get_emails_action._email_reader_repository.get_unread_emails = CoroutineMock(
            return_value=unread_emails_response
        )

        await get_emails_action.get_unread_emails(msg_dict)

        get_emails_action._email_reader_repository.get_unread_emails.assert_awaited_once_with(
            email, email_filter, lookup_days
        )
        get_emails_action._event_bus.publish_message.assert_awaited_once_with(response_topic, event_bus_response)

    @pytest.mark.asyncio
    async def get_unread_emails_ko_no_body_test(self, get_emails_action):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
        }
        event_bus_response = {"request_id": request_id, "body": 'Must include "body" in request', "status": 400}
        get_emails_action._email_reader_repository.get_unread_emails = CoroutineMock()

        await get_emails_action.get_unread_emails(msg_dict)

        get_emails_action._email_reader_repository.get_unread_emails.assert_not_awaited()
        get_emails_action._event_bus.publish_message.assert_awaited_once_with(response_topic, event_bus_response)

    @pytest.mark.asyncio
    async def get_unread_emails_ko_missing_parameters_test(self, get_emails_action):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"

        msg_dict = {"request_id": request_id, "response_topic": response_topic, "body": {}}

        event_bus_response = {
            "request_id": request_id,
            "body": 'You must include "email_account", "email_filter" and "lookup_days" '
            'in the "body" field of the response request',
            "status": 400,
        }
        get_emails_action._email_reader_repository.get_unread_emails = CoroutineMock()

        await get_emails_action.get_unread_emails(msg_dict)

        get_emails_action._email_reader_repository.get_unread_emails.assert_not_awaited()
        get_emails_action._event_bus.publish_message.assert_awaited_once_with(response_topic, event_bus_response)
