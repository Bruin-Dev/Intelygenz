from unittest.mock import Mock
from application.actions.actions import Actions
from config import testconfig as config


class TestActions:

    def instantiation_test(self):
        mock_repository = Mock()
        test_actions = Actions(config, mock_repository)
        assert test_actions._config == config

    def base_notification_test(self):
        test_msg = Mock()
        mock_repository = Mock()
        test_actions = Actions(config, mock_repository)
        test_actions._slack_repository.send_to_slack = Mock()
        test_actions.base_notification(test_msg)
        assert test_actions._slack_repository.send_to_slack.called
