from application.clients import t7_client as t7_client_module
from application.clients.t7_client import T7Client

from unittest.mock import patch
from unittest.mock import Mock
from config import testconfig
from pytest import raises


class TestT7Client:

    def instance_test(self):
        logger = Mock()
        config = Mock()

        t7_client = T7Client(logger, config)

        assert t7_client._logger is logger
        assert t7_client._config is config

    def get_request_headers_test(self):
        logger = Mock()
        config = testconfig

        t7_client = T7Client(logger, config)
        headers = t7_client._get_request_headers()

        assert headers['X-Client-Name'] == config.T7CONFIG['client_name']
        assert headers['X-Client-Version'] == config.T7CONFIG['version']
        assert headers['X-Auth-Token'] == config.T7CONFIG['auth-token']

    def get_prediction_200_test(self):
        config = testconfig
        get_response = {
            "assets": [
                {
                    "assetId": "some_serial_number",
                    "predictions": [
                        {
                            "name": "Some action",
                            "probability": 0.9484384655952454
                        },
                    ]
                }
            ],
            "requestId": "e676150a-73b9-412b-8207-ac2a3bbc9cbc"
        }

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
            assert prediction_list == {"body": get_response, "status": 200}

    def get_prediction_400_test(self):
        config = testconfig
        get_response = {
            "error": "ticket_id_required",
            "message": "The [ticketId] param is required."
        }

        logger = Mock()
        logger.info = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value=get_response)
        response_mock.status_code = 400

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'get', return_value=response_mock) as mock_get:
            prediction_list = t7_client.get_prediction(ticket_id=123)

            assert logger.error.called
            mock_get.assert_called_once()
            assert mock_get.call_args[0][0] == 'http://test-url.com/api/v1/suggestions?ticketId=123'
            assert prediction_list == {"body": get_response, "status": 400}

    def get_prediction_401_test(self):
        config = testconfig
        get_response = {
            "error": "auth_token_not_valid",
            "message": "[X-Auth-Token] is not valid."
        }

        logger = Mock()
        logger.info = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value=get_response)
        response_mock.status_code = 401

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'get', return_value=response_mock) as mock_get:
            prediction_list = t7_client.get_prediction(ticket_id=123)

            assert logger.error.called
            mock_get.assert_called_once()
            assert mock_get.call_args[0][0] == 'http://test-url.com/api/v1/suggestions?ticketId=123'
            assert prediction_list == {"body": get_response, "status": 401}

    def get_prediction_403_test(self):
        config = testconfig

        logger = Mock()
        logger.info = Mock()

        response_mock = Mock()
        response_mock.status_code = 403

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'get', return_value=response_mock) as mock_get:
            prediction_list = t7_client.get_prediction(ticket_id=123)

            assert logger.error.called
            mock_get.assert_called_once()
            assert mock_get.call_args[0][0] == 'http://test-url.com/api/v1/suggestions?ticketId=123'
            assert prediction_list == {"body": "Got 403 Forbidden from TNBA API", "status": 403}

    def get_prediction_404_as_500_test(self):
        config = testconfig
        get_response = {'error': 'error_getting_ticket_data',
                        'message': 'Unexpected error getting ticket data from Bruin API.'}

        logger = Mock()
        logger.info = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value=get_response)
        response_mock.status_code = 500

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'get', return_value=response_mock) as mock_get:
            prediction_list = t7_client.get_prediction(ticket_id=123)

            assert logger.error.called
            mock_get.assert_called_once()
            assert mock_get.call_args[0][0] == 'http://test-url.com/api/v1/suggestions?ticketId=123'
            assert prediction_list == {"body": f'Got possible 404 as 500 from TNBA API: {get_response}',
                                       "status": 500}

    def get_prediction_500_test(self):
        config = testconfig
        get_response = {'error': 'unexpected error',
                        'message': 'internal server error'}

        logger = Mock()
        logger.info = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value=get_response)
        response_mock.status_code = 500

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'get', return_value=response_mock) as mock_get:
            prediction_list = t7_client.get_prediction(ticket_id=123)

            assert logger.error.called
            mock_get.assert_called()
            assert mock_get.call_args[0][0] == 'http://test-url.com/api/v1/suggestions?ticketId=123'
            assert prediction_list == {"body": f'Got 500 from TNBA API: {get_response}',
                                       "status": 500}
