import json
from unittest.mock import Mock

import pytest
from application.actions.send_to_email import SendToEmail
from asynctest import CoroutineMock
from config import testconfig as config


class TestEmailNotifier:
    def instantiation_test(self):
        test_bus = Mock()
        mock_email_repository = Mock()
        mock_logger = Mock()

        test_actions = SendToEmail(config, test_bus, mock_logger, mock_email_repository)

        assert test_actions._config is config
        assert test_actions._event_bus is test_bus
        assert test_actions._logger is mock_logger
        assert test_actions._email_repository is mock_email_repository

    @pytest.mark.asyncio
    async def send_to_email_job_test(self):
        mock_email_repository = Mock()
        test_bus = Mock()
        test_bus.publish_message = CoroutineMock()
        mock_logger = Mock()

        msg_delivery_status = 200
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg_body = "Failed Edges to be emailed"
        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
            "email_data": msg_body,
        }

        test_actions = SendToEmail(config, test_bus, mock_logger, mock_email_repository)
        test_actions._email_repository.send_to_email = Mock(return_value=msg_delivery_status)

        await test_actions.send_to_email(msg=msg_dict)

        test_actions._email_repository.send_to_email.assert_called_once_with(msg_body)
        test_actions._event_bus.publish_message.assert_awaited_once_with(
            response_topic, {"request_id": request_id, "status": msg_delivery_status}
        )

    @pytest.mark.asyncio
    async def send_to_email_job_no_message_test(self):
        mock_email_repository = Mock()
        test_bus = Mock()
        test_bus.publish_message = CoroutineMock()
        mock_logger = Mock()

        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1c"
        msg_body = ""
        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
            "email_data": msg_body,
        }

        test_actions = SendToEmail(config, test_bus, mock_logger, mock_email_repository)
        test_actions._email_repository.send_to_email = Mock()

        await test_actions.send_to_email(msg=msg_dict)

        test_actions._email_repository.send_to_email.assert_not_called()
        test_actions._event_bus.publish_message.assert_awaited_once_with(
            response_topic, {"request_id": request_id, "status": 500}
        )
