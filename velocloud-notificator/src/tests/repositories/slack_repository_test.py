from unittest.mock import Mock
from config import testconfig as config
from application.repositories.slack_repository import SlackRepository


class TestSlackRepository:

    def instantiation_test(self):
        mock_client = Mock()
        test_repo = SlackRepository(config, mock_client)
        assert test_repo._config == config

    def send_to_slack_test(self):
        test_msg = Mock()
        mock_client = Mock()
        test_repo = SlackRepository(config, mock_client)
        test_repo._slack_client.send_to_slack = Mock()
        test_repo.send_to_slack(test_msg)
        assert test_repo._slack_client.send_to_slack.called
        # Testing if the message that is being sent to send_to_slack is formatted correctly
        assert test_repo._slack_client.send_to_slack.mock_calls[0][1][0] == {'text': str(test_msg)}
