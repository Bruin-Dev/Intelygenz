from unittest.mock import Mock

from application.repositories.slack_repository import SlackRepository
from config import testconfig as config


class TestSlackRepository:
    def instantiation_test(self):
        mock_client = Mock()
        mock_logger = Mock()

        test_repo = SlackRepository(config, mock_client, mock_logger)

        assert test_repo._config is config
        assert test_repo._slack_client is mock_client
        assert test_repo._logger is mock_logger

    def send_to_slack_test(self):
        mock_client = Mock()
        mock_logger = Mock()
        test_msg = "This is a dummy message"

        test_repo = SlackRepository(config, mock_client, mock_logger)
        test_repo._slack_client.send_to_slack = Mock()

        test_repo.send_to_slack(test_msg)

        test_repo._slack_client.send_to_slack.assert_called_once_with({"text": test_msg})
