from unittest.mock import Mock

import requests

from application.clients.bruin_client import BruinClient
from config import testconfig as config


class TestBruinClient:

    def instance_test(self):
        logger = Mock()
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        assert bruin_client._logger is logger
        assert bruin_client._config is config.BRUIN_CONFIG

    def login_ok_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value={"access_token": "Someverysecretaccesstoken"})
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        bruin_client.login()
        assert "Someverysecretaccesstoken" in bruin_client._bearer_token
        assert requests.post.called

    def login_ko_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock()
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        bruin_client.login()
        assert bruin_client._bearer_token == ""
        assert requests.post.called
