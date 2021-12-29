from application.clients import slack_client
from application.clients.slack_client import SlackClient
from unittest.mock import Mock, patch
from config import testconfig as config
import requests
import json


class TestSlackClient:

    def instantiation_test(self):
        mock_logger = Mock()

        test_client = SlackClient(config, mock_logger)

        assert test_client._config is config.SLACK_CONFIG
        assert test_client._url == config.SLACK_CONFIG['webhook']
        assert test_client._logger is mock_logger

    def send_to_slack_test(self):
        mock_logger = Mock()
        test_msg = {'text': 'This is a dummy message'}
        msg_delivery_status = 200
        test_response = (
            f'Request with message {str(test_msg)} '
            f'returned a response with status code {msg_delivery_status}'
        )

        test_client = SlackClient(config, mock_logger)
        test_client._logger.info = Mock()

        with patch.object(slack_client.requests, 'post') as post_mock:
            post_mock.return_value.status_code = msg_delivery_status

            response = test_client.send_to_slack(test_msg)

            post_mock.assert_called_once_with(
                test_client._url,
                json=test_msg
            )
            test_client._logger.info.assert_called_once()
            assert response == test_response

    def send_to_slack_with_bad_status_code_test(self):
        mock_logger = Mock()
        test_msg = {'text': 'This is a dummy message'}
        msg_delivery_status = 404
        test_response = f'ERROR - Request returned HTTP {msg_delivery_status}'

        test_client = SlackClient(config, mock_logger)
        test_client._logger.error = Mock()

        with patch.object(slack_client.requests, 'post') as post_mock:
            post_mock.return_value.status_code = msg_delivery_status

            response = test_client.send_to_slack(test_msg)

            post_mock.assert_called_once_with(
                test_client._url,
                json=test_msg
            )
            test_client._logger.error.assert_called_once()
            assert response == test_response

    def send_to_slack_with_insecure_url_test(self):
        mock_logger = Mock()
        test_msg = {'text': 'This is a dummy message'}

        test_client = SlackClient(config, mock_logger)
        test_client._url = 'http://slack.com'
        test_client._logger.error = Mock()

        response = test_client.send_to_slack(test_msg)

        test_client._logger.error.assert_called_once()
        assert response is None
