from application.clients.slack_client import SlackClient
from unittest.mock import Mock, patch
from config import testconfig as config
import requests


class TestSlackClient:

    def instantiation_test(self):
        test__client = SlackClient(config)
        assert test__client._config == config.SLACK_CONFIG
        assert test__client._url == config.SLACK_CONFIG['webhook'][0]

    def send_to_slack_test(self):
        test_msg = {'text': str(Mock())}
        test__client = SlackClient(config)
        with patch.object(requests, 'post') as post_mock:
            post_mock.return_value = mock_response = Mock()
            mock_response.status_code = 200
            response = test__client.send_to_slack(test_msg)
            test_response = str(test_msg) + 'sent with status code of ' + str(200)
            assert post_mock.called
            assert response == test_response

