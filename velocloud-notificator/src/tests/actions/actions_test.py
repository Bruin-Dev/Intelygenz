from unittest.mock import Mock
from application.actions.actions import Actions
from asynctest import CoroutineMock
from config import testconfig as config
import asyncio
import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
import json


class TestActions:

    def instantiation_test(self):
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        test_bus = Mock()
        mock_email_repository = Mock()
        mock_logger = Mock()
        scheduler = Mock()
        test_actions = Actions(config, test_bus, mock_slack_repository, mock_stats_repo, mock_logger,
                               mock_email_repository, scheduler)
        assert test_actions._config == config
        assert test_actions._event_bus == test_bus
        assert test_actions._slack_repository is mock_slack_repository
        assert test_actions._statistic_repository is mock_stats_repo
        assert test_actions._logger is mock_logger
        assert test_actions._email_repository is mock_email_repository

    def send_to_slack_test(self):
        test_msg = Mock()
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        test_bus = Mock()
        mock_email_repository = Mock()
        mock_logger = Mock()
        scheduler = Mock()
        test_actions = Actions(config, test_bus, mock_slack_repository, mock_stats_repo, mock_logger,
                               mock_email_repository, scheduler)
        test_actions._slack_repository.send_to_slack = Mock()
        test_actions.send_to_slack(test_msg)
        assert test_actions._slack_repository.send_to_slack.called

    def store_stats_test(self):
        test_msg = Mock()
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        test_bus = Mock()
        mock_email_repository = Mock()
        mock_logger = Mock()
        scheduler = Mock()
        test_actions = Actions(config, test_bus, mock_slack_repository, mock_stats_repo, mock_logger,
                               mock_email_repository, scheduler)
        test_actions._statistic_repository.send_to_stats_client = Mock()
        test_actions.store_stats(test_msg)
        assert test_actions._statistic_repository.send_to_stats_client.called

    @pytest.mark.asyncio
    async def send_to_email_job_test(self):
        test_msg = b'{"request_id":"123", "email_data":"Failed Edges to be emailed"}'
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        test_bus = Mock()
        test_bus.publish_message = CoroutineMock()
        mock_email_repository = Mock()
        mock_email_repository.send_to_email = Mock(return_value=200)
        mock_logger = Mock()
        scheduler = Mock()
        test_actions = Actions(config, test_bus, mock_slack_repository, mock_stats_repo, mock_logger,
                               mock_email_repository, scheduler)
        await test_actions.send_to_email_job(test_msg)
        assert test_actions._email_repository.send_to_email.called
        mock_email_repository.send_to_email.assert_called_with('Failed Edges to be emailed')
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == "notification.email.response"
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123", "status": 200})

    @pytest.mark.asyncio
    async def send_to_email_job_no_message_test(self):
        test_msg = b'{"request_id":"123", "email_data":""}'
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        test_bus = Mock()
        test_bus.publish_message = CoroutineMock()
        mock_email_repository = Mock()
        mock_email_repository.send_to_email = Mock(return_value=200)
        mock_logger = Mock()
        scheduler = Mock()
        test_actions = Actions(config, test_bus, mock_slack_repository, mock_stats_repo, mock_logger,
                               mock_email_repository, scheduler)
        await test_actions.send_to_email_job(test_msg)
        assert test_actions._email_repository.send_to_email.called is False
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == "notification.email.response"
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123", "status": 500})

    @pytest.mark.asyncio
    async def send_stats_to_slack_interval_test(self):
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        test_bus = Mock()
        mock_email_repository = Mock()
        mock_logger = Mock()
        scheduler = AsyncIOScheduler(timezone=utc)
        test_actions = Actions(config, test_bus, mock_slack_repository, mock_stats_repo, mock_logger,
                               mock_email_repository, scheduler)
        test_actions._statistic_repository._statistic_client.get_statistics = Mock(return_value='OK')
        test_actions._statistic_repository._statistic_client.clear_dictionaries = Mock()
        test_actions.send_to_slack = Mock()
        test_actions._logger.info = Mock()
        test_actions.set_stats_to_slack_job()
        scheduler.start()
        await asyncio.sleep(1.1)
        scheduler.shutdown(wait=False)
        assert test_actions._statistic_repository._statistic_client.get_statistics.called
        assert test_actions._statistic_repository._statistic_client.clear_dictionaries.called
        assert test_actions.send_to_slack.called
        assert test_actions._logger.info.called

    @pytest.mark.asyncio
    async def send_stats_to_slack_interval_no_message_test(self):
        mock_slack_repository = Mock()
        mock_stats_repo = Mock()
        mock_logger = Mock()
        test_bus = Mock()
        mock_email_repository = Mock()
        scheduler = AsyncIOScheduler(timezone=utc)
        test_actions = Actions(config, test_bus, mock_slack_repository, mock_stats_repo, mock_logger,
                               mock_email_repository, scheduler)
        test_actions._statistic_repository._statistic_client.get_statistics = Mock(return_value=None)
        test_actions._statistic_repository._statistic_client.clear_dictionaries = Mock()
        test_actions.send_to_slack = Mock()
        test_actions._logger.info = Mock()
        test_actions.set_stats_to_slack_job()
        scheduler.start()
        await asyncio.sleep(1.1)
        scheduler.shutdown(wait=False)
        assert test_actions._statistic_repository._statistic_client.get_statistics.called
        assert test_actions._statistic_repository._statistic_client.clear_dictionaries.called
        assert test_actions.send_to_slack.called is False
        assert test_actions._logger.info.called
