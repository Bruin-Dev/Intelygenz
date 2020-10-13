from application.clients import t7_client as t7_client_module, public_input_pb2 as pb2, \
    public_input_pb2_grpc as pb2_grpc
from application.clients.t7_client import T7Client

from unittest.mock import patch
from unittest.mock import Mock
from config import testconfig


class TestT7Client:
    valid_ticket_id = 123
    valid_ticket_rows = [
        {
            "asset": "asset1",
            "call_ticket_id": valid_ticket_id,
            "initial_note_ticket_creation": "9/22/2020 11:45:08 AM",
            "entered_date_n": "2020-09-22T11:44:54.85-04:00",
            "notes": "note 1",
            "task_result": None,
            "ticket_status": "Closed",
            "address1": "address 1",
            "sla": 1,
        },
        {
            "asset": None,
            "call_ticket_id": valid_ticket_id,
            "initial_note_ticket_creation": "9/22/2020 11:45:08 AM",
            "entered_date_n": "2020-09-22T11:44:54.85-04:00",
            "notes": "note 2",
            "task_result": None,
            "ticket_status": "Closed",
            "address1": "address 2",
            "sla": 1,
        }
    ]

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

        response_mock_1 = Mock()
        prediction_value = pb2.PredictionResponse
        prediction_value.message = 'test1'
        response_mock_1.Prediction = Mock(return_value=prediction_value)

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'get', return_value=response_mock) as mock_get, \
                patch.object(pb2_grpc, 'EntrypointStub', return_value=response_mock_1):

            prediction_list = t7_client.get_prediction(ticket_id=self.valid_ticket_id,
                                                       ticket_rows=self.valid_ticket_rows)

            assert logger.info.called
            mock_get.assert_called_once()
            assert mock_get.call_args[0][0] == 'http://test-url.com/api/v1/suggestions?ticketId=123'
            assert prediction_list == {
                "body": get_response,
                "status": 200,
                "kre_response": {"body": "test1", "status_code": "SUCCESS"}
            }

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

        response_mock_1 = Mock()
        prediction_value = pb2.PredictionResponse
        prediction_value.message = 'test1'
        response_mock_1.Prediction = Mock(return_value=prediction_value)

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'get', return_value=response_mock) as mock_get, \
                patch.object(pb2_grpc, 'EntrypointStub', return_value=response_mock_1):

            prediction_list = t7_client.get_prediction(ticket_id=self.valid_ticket_id,
                                                       ticket_rows=self.valid_ticket_rows)

            assert logger.error.called
            mock_get.assert_called_once()
            assert mock_get.call_args[0][0] == 'http://test-url.com/api/v1/suggestions?ticketId=123'
            assert prediction_list == {
                "body": get_response,
                "status": 400,
                "kre_response": {"body": "test1", "status_code": "SUCCESS"}
            }

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

        response_mock_1 = Mock()
        prediction_value = pb2.PredictionResponse
        prediction_value.message = 'test1'
        response_mock_1.Prediction = Mock(return_value=prediction_value)

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'get', return_value=response_mock) as mock_get, \
                patch.object(pb2_grpc, 'EntrypointStub', return_value=response_mock_1):
            prediction_list = t7_client.get_prediction(ticket_id=self.valid_ticket_id,
                                                       ticket_rows=self.valid_ticket_rows)

            assert logger.error.called
            mock_get.assert_called_once()
            assert mock_get.call_args[0][0] == 'http://test-url.com/api/v1/suggestions?ticketId=123'
            assert prediction_list == {
                "body": get_response,
                "status": 401,
                "kre_response": {"body": "test1", "status_code": "SUCCESS"}
            }

    def get_prediction_403_test(self):
        config = testconfig

        logger = Mock()
        logger.info = Mock()

        response_mock = Mock()
        response_mock.status_code = 403

        response_mock_1 = Mock()
        prediction_value = pb2.PredictionResponse
        prediction_value.message = 'test1'
        response_mock_1.Prediction = Mock(return_value=prediction_value)

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'get', return_value=response_mock) as mock_get, \
                patch.object(pb2_grpc, 'EntrypointStub', return_value=response_mock_1):
            prediction_list = t7_client.get_prediction(ticket_id=self.valid_ticket_id,
                                                       ticket_rows=self.valid_ticket_rows)

            assert logger.error.called
            mock_get.assert_called_once()
            assert mock_get.call_args[0][0] == 'http://test-url.com/api/v1/suggestions?ticketId=123'
            assert prediction_list == {
                "body": "Got 403 Forbidden from TNBA API",
                "status": 403,
                "kre_response": {"body": "test1", "status_code": "SUCCESS"}
            }

    def get_prediction_404_as_500_test(self):
        config = testconfig
        get_response = {'error': 'error_getting_ticket_data',
                        'message': 'Unexpected error getting ticket data from Bruin API.'}

        logger = Mock()
        logger.info = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value=get_response)
        response_mock.status_code = 500

        response_mock_1 = Mock()
        prediction_value = pb2.PredictionResponse
        prediction_value.message = 'test1'
        response_mock_1.Prediction = Mock(return_value=prediction_value)

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'get', return_value=response_mock) as mock_get, \
                patch.object(pb2_grpc, 'EntrypointStub', return_value=response_mock_1):
            prediction_list = t7_client.get_prediction(ticket_id=self.valid_ticket_id,
                                                       ticket_rows=self.valid_ticket_rows)

            assert logger.error.called
            mock_get.assert_called_once()
            assert mock_get.call_args[0][0] == 'http://test-url.com/api/v1/suggestions?ticketId=123'
            assert prediction_list == {
                "body": f'Got possible 404 as 500 from TNBA API: {get_response}',
                "status": 500,
                "kre_response": {"body": "test1", "status_code": "SUCCESS"}
            }

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
            prediction_list = t7_client.get_prediction(ticket_id=self.valid_ticket_id,
                                                       ticket_rows=self.valid_ticket_rows)

            assert logger.error.called
            mock_get.assert_called()
            assert mock_get.call_args[0][0] == 'http://test-url.com/api/v1/suggestions?ticketId=123'
            assert prediction_list == {"body": f'Got 500 from TNBA API: {get_response}',
                                       "status": 500}

    def post_automation_metrics_200_test(self):
        config = testconfig
        post_response = "Successfully posted metrics"

        logger = Mock()
        logger.info = Mock()

        params = {"ticket_id": 123, "ticket_rows": []}
        response_mock = Mock()
        response_mock.status_code = 204

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'post', return_value=response_mock) as mock_post:
            automation_metrics_response = t7_client.post_automation_metrics(params)

            assert logger.info.called
            mock_post.assert_called_once()
            assert mock_post.call_args[0][0] == 'http://test-url.com/api/v2/metrics'
            assert automation_metrics_response == {
                "body": post_response,
                "status": 204,
                "kre_response": {
                    "body": "Error: camel_ticket_rows",
                    "status_code": "UNKNOWN_ERROR",
                }
            }

    def post_automation_metrics_400_test(self):
        config = testconfig
        post_response = "Failed"

        logger = Mock()
        logger.info = Mock()

        params = {"ticket_id": 123, "ticket_rows": []}
        response_mock = Mock()
        response_mock.json = Mock(return_value=post_response)
        response_mock.status_code = 400

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'post', return_value=response_mock) as mock_post:
            automation_metrics_response = t7_client.post_automation_metrics(params)

            assert logger.info.called
            mock_post.assert_called_once()
            assert mock_post.call_args[0][0] == 'http://test-url.com/api/v2/metrics'
            assert automation_metrics_response == {
                "body": post_response,
                "status": 400,
                "kre_response": {
                    "body": "Error: camel_ticket_rows",
                    "status_code": "UNKNOWN_ERROR",
                }
            }

    def post_automation_metrics_401_test(self):
        config = testconfig
        post_response = "Failed"

        logger = Mock()
        logger.info = Mock()

        params = {"ticket_id": 123, "ticket_rows": []}
        response_mock = Mock()
        response_mock.json = Mock(return_value=post_response)
        response_mock.status_code = 401

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'post', return_value=response_mock) as mock_post:
            automation_metrics_response = t7_client.post_automation_metrics(params)

            assert logger.info.called
            mock_post.assert_called_once()
            assert mock_post.call_args[0][0] == 'http://test-url.com/api/v2/metrics'
            assert automation_metrics_response == {
                "body": post_response,
                "status": 401,
                "kre_response": {
                    "body": "Error: camel_ticket_rows",
                    "status_code": "UNKNOWN_ERROR",
                }
            }

    def post_automation_metrics_403_test(self):
        config = testconfig
        post_response = "Failed"

        logger = Mock()
        logger.info = Mock()

        params = {"ticket_id": 123, "ticket_rows": []}
        response_mock = Mock()
        response_mock.json = Mock(return_value=post_response)
        response_mock.status_code = 403

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'post', return_value=response_mock) as mock_post:
            automation_metrics_response = t7_client.post_automation_metrics(params)

            assert logger.info.called
            mock_post.assert_called_once()
            assert mock_post.call_args[0][0] == 'http://test-url.com/api/v2/metrics'
            assert automation_metrics_response == {
                "body": 'Got 403 Forbidden from TNBA API',
                "status": 403,
                "kre_response": {
                    "body": "Error: camel_ticket_rows",
                    "status_code": "UNKNOWN_ERROR",
                }
            }

    def post_automation_metrics_404_as_500_test(self):
        config = testconfig
        post_response = {'error': 'error_getting_ticket_data',
                         'message': 'Unexpected error getting ticket data from Bruin API.'}

        logger = Mock()
        logger.info = Mock()

        params = {"ticket_id": 123, "ticket_rows": []}
        response_mock = Mock()
        response_mock.json = Mock(return_value=post_response)
        response_mock.status_code = 500

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'post', return_value=response_mock) as mock_post:
            automation_metrics_response = t7_client.post_automation_metrics(params)

            assert logger.info.called
            mock_post.assert_called_once()
            assert mock_post.call_args[0][0] == 'http://test-url.com/api/v2/metrics'
            assert automation_metrics_response == {
                "body": f"Got possible 404 as 500 from TNBA API: {post_response}",
                "status": 500,
                "kre_response": {
                    "body": "Error: camel_ticket_rows",
                    "status_code": "UNKNOWN_ERROR",
                }
            }

    def post_automation_metrics_500_test(self):
        config = testconfig
        post_response = {
            "error": "unexpected error",
            "message": "Unexpected error"
        }

        logger = Mock()
        logger.info = Mock()

        params = {"ticket_id": 123, "ticket_rows": []}
        response_mock = Mock()
        response_mock.json = Mock(return_value=post_response)
        response_mock.status_code = 500

        t7_client = T7Client(logger, config)
        t7_client._get_request_headers = Mock()
        with patch.object(t7_client_module.requests, 'post', return_value=response_mock) as mock_post:
            automation_metrics_response = t7_client.post_automation_metrics(params)

            assert logger.info.called
            mock_post.assert_called()
            assert mock_post.call_args[0][0] == 'http://test-url.com/api/v2/metrics'
            assert automation_metrics_response == {"body": f"Got 500 from TNBA API: {post_response}",
                                                   "status": 500}
