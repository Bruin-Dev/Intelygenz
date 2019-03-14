from application.clients.slack_client import SlackClient
from unittest.mock import Mock, patch
from config import testconfig as config
import requests
from igz.packages.Logger.logger_client import LoggerClient
import logging
import sys


class TestSlackClient:

    logger = LoggerClient().create_logger(str(Mock()))

    def instantiation_test(self):
        test__client = SlackClient(config, self.logger)
        assert test__client._config == config.SLACK_CONFIG
        assert test__client._url == config.SLACK_CONFIG['webhook'][0]

    def ok_send_to_slack_test(self):
        test_msg = {'text': str(Mock())}
        test__client = SlackClient(config, self.logger)
        with patch.object(requests, 'post') as post_mock:
            post_mock.return_value = mock_response = Mock()
            mock_response.status_code = 200
            response = test__client.send_to_slack(test_msg)
            test_response = str(test_msg) + 'sent with status code of ' + str(200)
            assert post_mock.called
            assert response == test_response

    def ko_send_to_slack_bad_status_code_test(self):
        test_msg = {'text': str(Mock())}
        test__client = SlackClient(config, self.logger)
        with patch.object(requests, 'post') as post_mock:
            post_mock.return_value = mock_response = Mock()
            mock_response.status_code = 404
            response = test__client.send_to_slack(test_msg)
            test_response = 'HTTP error ' + str(mock_response.status_code)
            assert response == test_response

    def ko_send_to_slack_invalid_url_test(self):
        test_msg = {'text': str(Mock())}
        test__client = SlackClient(config, self.logger)
        test__client._url = 'test_url.com'
        response = test__client.send_to_slack(test_msg)
        assert response is None
