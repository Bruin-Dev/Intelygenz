from unittest.mock import Mock
from application.actions.actions import Actions
from config import testconfig as config


class TestActions:

    def instantiation_test(self):
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        test_actions = Actions(config,  mock_slack_repository, mock_stats_repo)
        assert test_actions._config == config

    def send_to_slack_test(self):
        test_msg = Mock()
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        test_actions = Actions(config, mock_slack_repository, mock_stats_repo)
        test_actions._slack_repository.send_to_slack = Mock()
        test_actions.send_to_slack(test_msg)
        assert test_actions._slack_repository.send_to_slack.called

    def store_stats_test(self):
        test_msg = Mock()
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        test_actions = Actions(config, mock_slack_repository, mock_stats_repo)
        test_actions._statistic_repository.send_to_stats_client = Mock()
        test_actions.store_stats(test_msg)
        assert test_actions._statistic_repository.send_to_stats_client.called

