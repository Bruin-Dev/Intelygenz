from unittest.mock import Mock
from application.actions.actions import Actions
from config import testconfig as config
from igz.packages.Logger.logger_client import LoggerClient
import logging
import sys


class TestActions:

    logger = LoggerClient().create_logger(str(Mock()))

    def instantiation_test(self):
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        test_actions = Actions(config, mock_slack_repository, mock_stats_repo, self.logger)
        assert test_actions._config == config

    def ok_send_to_slack_test(self):
        test_msg = Mock()
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        test_actions = Actions(config, mock_slack_repository, mock_stats_repo, self.logger)
        test_actions._slack_repository.send_to_slack = Mock()
        test_actions.send_to_slack(test_msg)
        assert test_actions._slack_repository.send_to_slack.called

    def ko_send_to_slack_test(self):
        test_msg = Mock()
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        test_actions = Actions(config, mock_slack_repository, mock_stats_repo, self.logger)
        test_actions._slack_repository.send_to_slack = None
        return_value = test_actions.send_to_slack(test_msg)
        assert return_value is None

    def ok_store_stats_test(self):
        test_msg = Mock()
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        test_actions = Actions(config, mock_slack_repository, mock_stats_repo, self.logger)
        test_actions._statistic_repository.send_to_stats_client = Mock()
        test_actions.store_stats(test_msg)
        assert test_actions._statistic_repository.send_to_stats_client.called

    def ko_store_stats_test(self):
        test_msg = Mock()
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        test_actions = Actions(config, mock_slack_repository, mock_stats_repo, self.logger)
        test_actions._statistic_repository.send_to_stats_client = None
        return_value = test_actions.store_stats(test_msg)
        assert return_value is None
