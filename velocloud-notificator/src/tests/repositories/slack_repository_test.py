from unittest.mock import Mock
from config import testconfig as config
from application.repositories.slack_repository import SlackRepository


class TestSlackRepository:

    def instantiation_test(self):
        mock_client = Mock()
        mock_logger = Mock()
        test_repo = SlackRepository(config, mock_client, mock_logger)
        assert test_repo._config == config

    def ok_send_to_slack_test(self):
        test_msg = Mock()
        mock_client = Mock()
        mock_logger = Mock()
        test_repo = SlackRepository(config, mock_client, mock_logger)
        test_repo._slack_client.send_to_slack = Mock()
        test_repo.send_to_slack(test_msg)
        assert test_repo._slack_client.send_to_slack.called
        # Testing if the message that is being sent to send_to_slack is formatted correctly
        assert test_repo._slack_client.send_to_slack.mock_calls[0][1][0] == {'text': str(test_msg)}

    def ko_send_to_slack_test(self):
        test_msg = Mock()
        mock_client = Mock()
        mock_logger = Mock()
        test_repo = SlackRepository(config, mock_client, mock_logger)
        test_repo._logger.error = Mock()
        test_repo._slack_client.send_to_slack = None
        return_type = test_repo.send_to_slack(test_msg)
        assert return_type is None
        assert test_repo._logger.error.called
