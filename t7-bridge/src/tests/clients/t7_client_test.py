from application.clients import t7_client as t7_client_module
from application.clients.t7_client import T7Client

from unittest.mock import patch
from unittest.mock import Mock
from config import testconfig as configs
from pytest import raises


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

        assert headers['X-Client-Name'] == configs.T7CONFIG['client_name']
        assert headers['X-Client-Version'] == configs.T7CONFIG['version']
        assert headers['X-Auth-Token'] == configs.T7CONFIG['auth-token']

    def get_prediction_test(self):
        config = configs
        get_response = {'assets': ['List of predictions']}

        logger = Mock()
        logger.info = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value=get_response)
        response_mock.status_code = 200

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'get', return_value=response_mock) as mock_get:
            prediction_list = t7_client.get_prediction(ticket_id=123)

            assert logger.info.called
            mock_get.assert_called_once()
            assert mock_get.call_args[0][0] == 'http://test-url.com/api/v1/suggestions?ticketId=123'
            assert prediction_list == ['List of predictions']

    def get_prediction_with_bad_status_code_test(self):
        config = configs
        get_response = {'assets': ['List of predictions']}

        logger = Mock()
        logger.info = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value=get_response)
        response_mock.status_code = 200

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'get', return_value=response_mock) as mock_get:
            with raises(Exception):
                prediction_list = t7_client.get_prediction(ticket_id=123)
                assert prediction_list is None
