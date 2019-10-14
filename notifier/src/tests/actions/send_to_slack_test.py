from unittest.mock import Mock
from application.actions.send_to_slack import SendToSlack
from asynctest import CoroutineMock
from config import testconfig as config
import pytest
import json


class TestSlackNotifier:

    def instantiation_test(self):
        """
        Test that the SendToSlack action instance contains the expected
        attributes.
        """
        mock_slack_repository = Mock()
        test_bus = Mock()
        mock_logger = Mock()

        test_actions = SendToSlack(config, test_bus, mock_slack_repository, mock_logger)

        assert test_actions._config is config
        assert test_actions._event_bus is test_bus
        assert test_actions._slack_repository is mock_slack_repository
        assert test_actions._logger is mock_logger

    @pytest.mark.asyncio
    async def send_to_slack_test(self):
        """
        Test that the notification is sent to the Slack channel and also
        published in the corresponding topic.
        """
        mock_slack_repository = Mock()
        test_bus = Mock()
        test_bus.publish_message = CoroutineMock()
        mock_logger = Mock()

        msg_delivery_status = 200
        request_id = "123"
        response_topic = "some.topic"
        msg_body = "Failed Edges to be slacked"
        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
            "message": msg_body,
        }

        test_actions = SendToSlack(config, test_bus, mock_slack_repository, mock_logger)
        test_actions._slack_repository.send_to_slack = Mock(return_value=msg_delivery_status)

        await test_actions.send_to_slack(msg=json.dumps(msg_dict))

        test_actions._slack_repository.send_to_slack.assert_called_once_with(msg_body)
        test_bus.publish_message.assert_awaited_once_with(
            response_topic,
            json.dumps({'request_id': request_id, 'status': msg_delivery_status}),
        )
