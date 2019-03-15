from application.clients.slack_client import SlackClient
from unittest.mock import Mock, patch
from config import testconfig as config
import requests


class TestSlackClient:

    def instantiation_test(self):
        mock_logger = Mock()
        test_client = SlackClient(config, mock_logger)
        assert test_client._config == config.SLACK_CONFIG
        assert test_client._url == config.SLACK_CONFIG['webhook'][0]

    def ok_send_to_slack_test(self):
        test_msg = {'text': str(Mock())}
        mock_logger = Mock()
        test_client = SlackClient(config, mock_logger)
        test_client._logger.info = Mock()
        with patch.object(requests, 'post') as post_mock:
            post_mock.return_value = mock_response = Mock()
            mock_response.status_code = 200
            response = test_client.send_to_slack(test_msg)
            test_response = str(test_msg) + 'sent with status code of ' + str(200)
            assert post_mock.called
            assert response == test_response
            assert test_client._logger.info.called

    def ko_send_to_slack_bad_status_code_test(self):
        test_msg = {'text': str(Mock())}
        mock_logger = Mock()
        test_client = SlackClient(config, mock_logger)
        test_client._logger.error = Mock()
        with patch.object(requests, 'post') as post_mock:
            post_mock.return_value = mock_response = Mock()
            mock_response.status_code = 404
            response = test_client.send_to_slack(test_msg)
            test_response = 'HTTP error ' + str(mock_response.status_code)
            assert response == test_response
            assert test_client._logger.error.called

    def ko_send_to_slack_invalid_url_test(self):
        test_msg = {'text': str(Mock())}
        mock_logger = Mock()
        test_client = SlackClient(config, mock_logger)
        test_client._logger.error = Mock()
        test_client._url = 'test_url.com'
        response = test_client.send_to_slack(test_msg)
        assert response is None
        assert test_client._logger.error.called
