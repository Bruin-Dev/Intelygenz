from application.clients.slack_client import SlackClient
from unittest.mock import Mock
from config import testconfig as config
import requests


class TestSlackClient:

    def instantiation_test(self):
        test__client = SlackClient(config)
        assert test__client._config == config.SLACK_CONFIG
        assert test__client._url == config.SLACK_CONFIG['webhook']

    def send_to_slack_test(self):
        test_msg = {'text': str(Mock())}
        test__client = SlackClient(config)
        requests.post = Mock()

        test__client.send_to_slack(test_msg)
        assert requests.post.called
