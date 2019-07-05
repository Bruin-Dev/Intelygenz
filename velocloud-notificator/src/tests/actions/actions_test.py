from unittest.mock import Mock
from application.actions.actions import Actions
from asynctest import CoroutineMock
from config import testconfig as config
import pytest
import json


class TestActions:

    def instantiation_test(self):
        mock_slack_repository = Mock()
        test_bus = Mock()
        mock_email_repository = Mock()
        mock_logger = Mock()
        test_actions = Actions(config, test_bus, mock_slack_repository, mock_logger, mock_email_repository)
        assert test_actions._config == config
        assert test_actions._event_bus == test_bus
        assert test_actions._slack_repository is mock_slack_repository
        assert test_actions._logger is mock_logger
        assert test_actions._email_repository is mock_email_repository

    @pytest.mark.asyncio
    async def send_to_slack_test(self):
        test_msg = b'{"request_id":"123", "response_topic": "some.topic","message": "Failed Edges to be slacked"}'
        dict_msg = json.loads(test_msg.decode('utf-8'))
        mock_slack_repository = Mock()
        test_bus = Mock()
        test_bus.publish_message = CoroutineMock()
        mock_email_repository = Mock()
        mock_logger = Mock()
        test_actions = Actions(config, test_bus, mock_slack_repository, mock_logger, mock_email_repository)
        test_actions._slack_repository.send_to_slack = Mock(return_value=200)
        await test_actions.send_to_slack(test_msg)
        assert test_actions._slack_repository.send_to_slack.called
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == dict_msg['response_topic']
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123", "status": 200})

    @pytest.mark.asyncio
    async def send_to_email_job_test(self):
        test_msg = b'{"request_id":"123", "response_topic": "some.topic","email_data":"Failed Edges to be emailed"}'
        dict_msg = json.loads(test_msg.decode('utf-8'))
        mock_slack_repository = Mock()
        test_bus = Mock()
        test_bus.publish_message = CoroutineMock()
        mock_email_repository = Mock()
        mock_email_repository.send_to_email = Mock(return_value=200)
        mock_logger = Mock()
        test_actions = Actions(config, test_bus, mock_slack_repository, mock_logger, mock_email_repository)
        await test_actions.send_to_email_job(test_msg)
        assert test_actions._email_repository.send_to_email.called
        mock_email_repository.send_to_email.assert_called_with('Failed Edges to be emailed')
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == dict_msg['response_topic']
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123", "status": 200})

    @pytest.mark.asyncio
    async def send_to_email_job_no_message_test(self):
        test_msg = b'{"request_id":"123", "response_topic": "some.topic", "email_data":""}'
        dict_msg = json.loads(test_msg.decode('utf-8'))
        mock_slack_repository = Mock()
        test_bus = Mock()
        test_bus.publish_message = CoroutineMock()
        mock_email_repository = Mock()
        mock_email_repository.send_to_email = Mock(return_value=200)
        mock_logger = Mock()
        test_actions = Actions(config, test_bus, mock_slack_repository, mock_logger, mock_email_repository)
        await test_actions.send_to_email_job(test_msg)
        assert test_actions._email_repository.send_to_email.called is False
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == dict_msg['response_topic']
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123", "status": 500})
