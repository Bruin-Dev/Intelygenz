from application.clients.t7_client import T7Client
import json
import requests

from unittest.mock import Mock
from config import testconfig as configs
from tenacity import RetryError


class TestT7Client:

    def instance_test(self):
        logger = Mock()
        config = Mock()
        t7_client = T7Client(logger, config)
        assert t7_client ._logger is logger
        assert t7_client ._config is config

    def get_request_headers_test(self):
        logger = Mock()
        config = configs
        t7_client = T7Client(logger, config)
        headers = t7_client._get_request_headers()
        assert headers['X-Client-Name'] == 'test-name'
        assert headers['X-Client-Version'] == '1.0.0'
        assert headers['X-Auth-Token'] == 'test-token'

    def get_predication_ok_test(self):
        logger = Mock()
        logger.info = Mock()
        config = configs
        response = Mock()
        response.json = Mock(return_value={'assets': ['List of predictions']})
        response.status_code = 200
        requests.get = Mock(return_value=response)
        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        prediction_list = t7_client.get_prediction(123)

        assert logger.info.called
        assert requests.get.called
        assert requests.get.call_args[0][0] == 'http//:test-url.com/api/v1/suggestions?ticketId=123'
        assert prediction_list == ['List of predictions']

    def get_predication_ko_test(self):
        logger = Mock()
        logger.info = Mock()
        config = configs
        response = Mock()
        response.json = Mock(return_value=None)
        response.status_code = 500
        requests.get = Mock(return_value=response)
        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        prediction_list = None
        try:
            prediction_list = t7_client.get_prediction(123)
        except Exception as e:
            error = e
        assert isinstance(error, RetryError)
        assert logger.info.called
        assert requests.get.called
        assert prediction_list is None
