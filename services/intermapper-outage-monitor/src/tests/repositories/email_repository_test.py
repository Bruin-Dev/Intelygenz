from unittest.mock import Mock, patch

import pytest
from application.repositories import email_repository as email_repository_module
from application.repositories import nats_error_response
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(email_repository_module, "uuid", return_value=uuid_)


class TestEmailRepository:
    def instance_test(self, email_repository, event_bus, logger, notifications_repository):
        assert email_repository._logger is logger
        assert email_repository._event_bus is event_bus
        assert email_repository._config is testconfig
        assert email_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_unread_emails_test(self, email_repository):
        msg_dict = {
            "request_id": uuid_,
            "body": {
                "email_account": email_repository._config.INTERMAPPER_CONFIG["inbox_email"],
                "email_filter": email_repository._config.INTERMAPPER_CONFIG["sender_emails_list"],
                "lookup_days": email_repository._config.INTERMAPPER_CONFIG["events_lookup_days"],
            },
        }

        message_1 = {
            "message": {
                "From": "Alerts@ft-sys.com",
                "To": "<aaa@bbbb.com>, <ccc@dddd.com>",
                "Date": "Fri, 20 Mar 2020 04:34:50 -0400",
                "subject": "Idling Alert -- TT Bank - wert wert wert",
                "Content-Type": 'text/plain; charset="us-ascii"',
                "Content-Transfer-Encoding": "quoted-printable",
                "Message-ID": "<f2a81342-ba43-52d6-8899-babc10e001e5@JJJJ.KKKK.local>",
                "Return-Path": "Alerts@ft-sys.com",
                "X-CCSI-Disclaimer": "added",
            },
            "body": "tt Bank - yuio yuio has been idling for over 15 minute(s) at 04:28 AM 03/20/2020 \
                            It is located at LOCATION: zxcv zxcv. It is currently on job 000000.",
            "msg_uid": "1234",
        }
        expected_response = {"body": [message_1], "status": 200}
        email_repository._event_bus.rpc_request = CoroutineMock(return_value=expected_response)

        with uuid_mock:
            result = await email_repository.get_unread_emails()
        email_repository._event_bus.rpc_request.assert_awaited_once_with("get.email.request", msg_dict, timeout=90)
        assert result == expected_response

    @pytest.mark.asyncio
    async def get_unread_emails_failing_rpc_test(self, email_repository):
        email_repository._logger.error = Mock()

        msg_dict = {
            "request_id": uuid_,
            "body": {
                "email_account": email_repository._config.INTERMAPPER_CONFIG["inbox_email"],
                "email_filter": email_repository._config.INTERMAPPER_CONFIG["sender_emails_list"],
                "lookup_days": email_repository._config.INTERMAPPER_CONFIG["events_lookup_days"],
            },
        }

        email_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        email_repository._notifications_repository.send_slack_message = CoroutineMock()
        with uuid_mock:
            result = await email_repository.get_unread_emails()
        email_repository._event_bus.rpc_request.assert_awaited_once_with("get.email.request", msg_dict, timeout=90)
        email_repository._notifications_repository.send_slack_message.assert_awaited_once()
        email_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_unread_emails_non_2xx_test(self, email_repository):
        email_repository._logger.error = Mock()

        msg_dict = {
            "request_id": uuid_,
            "body": {
                "email_account": email_repository._config.INTERMAPPER_CONFIG["inbox_email"],
                "email_filter": email_repository._config.INTERMAPPER_CONFIG["sender_emails_list"],
                "lookup_days": email_repository._config.INTERMAPPER_CONFIG["events_lookup_days"],
            },
        }
        return_body = {"body": "Failed", "status": 400}
        email_repository._event_bus.rpc_request = CoroutineMock(return_value=return_body)

        email_repository._notifications_repository.send_slack_message = CoroutineMock()
        with uuid_mock:
            result = await email_repository.get_unread_emails()
        email_repository._event_bus.rpc_request.assert_awaited_once_with("get.email.request", msg_dict, timeout=90)
        email_repository._notifications_repository.send_slack_message.assert_awaited_once()
        email_repository._logger.error.assert_called_once()
        assert result == return_body

    @pytest.mark.asyncio
    async def mark_email_as_read_test(self, email_repository):
        msg_uid = "1234"
        msg_dict = {
            "request_id": uuid_,
            "body": {"email_account": email_repository._config.INTERMAPPER_CONFIG["inbox_email"], "msg_uid": msg_uid},
        }

        expected_response = {"body": "Success", "status": 200}
        email_repository._event_bus.rpc_request = CoroutineMock(return_value=expected_response)

        with uuid_mock:
            result = await email_repository.mark_email_as_read(msg_uid)
        email_repository._event_bus.rpc_request.assert_awaited_once_with(
            "mark.email.read.request", msg_dict, timeout=90
        )
        assert result == expected_response

    @pytest.mark.asyncio
    async def mark_email_as_read_failed_rpc_test(self, email_repository):
        msg_uid = "1234"
        msg_dict = {
            "request_id": uuid_,
            "body": {"email_account": email_repository._config.INTERMAPPER_CONFIG["inbox_email"], "msg_uid": msg_uid},
        }

        email_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        email_repository._notifications_repository.send_slack_message = CoroutineMock()
        with uuid_mock:
            result = await email_repository.mark_email_as_read(msg_uid)
        email_repository._event_bus.rpc_request.assert_awaited_once_with(
            "mark.email.read.request", msg_dict, timeout=90
        )
        email_repository._notifications_repository.send_slack_message.assert_awaited_once()
        email_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def mark_email_as_read_non_2xx_test(self, email_repository):
        msg_uid = "1234"
        msg_dict = {
            "request_id": uuid_,
            "body": {"email_account": email_repository._config.INTERMAPPER_CONFIG["inbox_email"], "msg_uid": msg_uid},
        }

        expected_response = {"body": "Failed", "status": 400}
        email_repository._event_bus.rpc_request = CoroutineMock(return_value=expected_response)

        email_repository._notifications_repository.send_slack_message = CoroutineMock()
        with uuid_mock:
            result = await email_repository.mark_email_as_read(msg_uid)
        email_repository._event_bus.rpc_request.assert_awaited_once_with(
            "mark.email.read.request", msg_dict, timeout=90
        )
        email_repository._notifications_repository.send_slack_message.assert_awaited_once()
        email_repository._logger.error.assert_called_once()
        assert result == expected_response
