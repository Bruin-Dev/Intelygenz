from unittest.mock import Mock
from application.actions.actions import Actions
from config import testconfig as config


class TestActions:

    def instantiation_test(self):
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        mock_logger = Mock()
        test_actions = Actions(config, mock_slack_repository, mock_stats_repo, mock_logger)
        assert test_actions._config == config
        assert test_actions._slack_repository is mock_slack_repository
        assert test_actions._statistic_repository is mock_stats_repo
        assert test_actions._logger is mock_logger

    def ok_send_to_slack_test(self):
        test_msg = Mock()
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        mock_logger = Mock()
        test_actions = Actions(config, mock_slack_repository, mock_stats_repo, mock_logger)
        test_actions._slack_repository.send_to_slack = Mock()
        test_actions.send_to_slack(test_msg)
        assert test_actions._slack_repository.send_to_slack.called

    def ko_send_to_slack_test(self):
        test_msg = Mock()
        mock_slack_repository = Mock(spec=[])
        mock_stats_repo = Mock()
        mock_logger = Mock()
        test_actions = Actions(config, mock_slack_repository, mock_stats_repo, mock_logger)
        test_actions._logger.error = Mock()
        return_value = test_actions.send_to_slack(test_msg)
        assert return_value is None
        assert test_actions._logger.error.called

    def ok_store_stats_test(self):
        test_msg = Mock()
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        mock_logger = Mock()
        test_actions = Actions(config, mock_slack_repository, mock_stats_repo, mock_logger)
        test_actions._statistic_repository.send_to_stats_client = Mock()
        test_actions.store_stats(test_msg)
        assert test_actions._statistic_repository.send_to_stats_client.called

    def ko_store_stats_test(self):
        test_msg = Mock()
        mock_slack_repository = Mock()
        mock_stats_repo = Mock(spec=[])
        mock_logger = Mock()
        test_actions = Actions(config, mock_slack_repository, mock_stats_repo, mock_logger)
        test_actions._logger.error = Mock()
        return_value = test_actions.store_stats(test_msg)
        assert return_value is None
        assert test_actions._logger.error.called
