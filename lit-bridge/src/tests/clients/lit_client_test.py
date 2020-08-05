from http import HTTPStatus
from unittest.mock import Mock
from unittest.mock import patch

from application.clients.lit_client import LitClient
from simple_salesforce import SalesforceGeneralError, SalesforceAuthenticationFailed, SalesforceError

from application.clients import lit_client as lit_client_module
from config import testconfig as config


class TestLitClient:

    def instance_test(self):
        logger = Mock()

        lit_client = LitClient(logger, config)

        assert lit_client._logger is logger
        assert lit_client._config is config

    def login_test(self, instance_lit_client):
        with patch.object(lit_client_module, 'Salesforce', return_value=Mock()) as mock_login:
            response = instance_lit_client.login()

            mock_login.assert_called_once()
            assert response is True

    def login_error_test(self, instance_lit_client):

        with patch.object(lit_client_module, 'Salesforce', side_effect=Exception("mocked error")) as mock_login:
            response = instance_lit_client.login()
            assert response is 'mocked error'

    def login_error_invalid_credentials_test(self, instance_lit_client):
        salesforce_exception = SalesforceGeneralError("mocked error", "a", "b", "c")
        with patch.object(lit_client_module, 'Salesforce', side_effect=salesforce_exception) as mock_login:
            response = instance_lit_client.login()
            assert response is "mocked error"
            assert mock_login.call_count == config.LIT_CONFIG['attempts']

    def login_error_authentication_failure_test(self, instance_lit_client):
        salesforce_exception = SalesforceAuthenticationFailed('mocked_error', 'a')
        with patch.object(lit_client_module, 'Salesforce', side_effect=salesforce_exception) as mock_login:
            response = instance_lit_client.login()
            assert response is 'mocked_error'
            assert mock_login.call_count == config.LIT_CONFIG['attempts']

    def get_headers_test(self, instance_lit_client):
        with patch.object(lit_client_module, 'Salesforce', return_value=True) as mock_login:
            response = instance_lit_client.login()
            assert response is True
            mock_login.assert_called_once()
            assert {
                       "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
                   } == instance_lit_client._get_request_headers()

    def post_create_dispatch_test(self, instance_lit_client, dispatch):

        expected_dispatch_response = {
            "APIRequestID": "a130v000001hWcNAAU",
            "Dispatch": dispatch,
            "Message": None,
            "Status": "Success"
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 200

        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            post_response = instance_lit_client.create_dispatch(dispatch)

            mock_apexecute.assert_called_once()

            assert post_response["body"] == expected_dispatch_response
            assert post_response["status"] == HTTPStatus.OK

    def post_create_dispatch_with_error_400_test(self, instance_lit_client, dispatch):

        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 400

        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            post_response = instance_lit_client.create_dispatch(dispatch)
            mock_apexecute.assert_called_once()

            assert post_response["body"] == expected_dispatch_response
            assert post_response["status"] == HTTPStatus.BAD_REQUEST

    def post_create_dispatch_with_error_500_test(self, instance_lit_client, dispatch):
        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 500

        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          side_effect=Exception("Error")) as mock_apexecute:
            post_response = instance_lit_client.create_dispatch(dispatch)
            mock_apexecute.assert_called()
            assert mock_apexecute.call_count == 3
            assert post_response == "Error"

    def post_create_dispatch_with_error_salesforce_sdk_test(self, instance_lit_client, dispatch):
        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 400

        salesforce_exception = SalesforceError('url', 500, 'resource_name', 'content')
        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          side_effect=salesforce_exception) as mock_apexecute:
            try:
                instance_lit_client.create_dispatch(dispatch)
            except SalesforceError as sfe:
                assert isinstance(sfe, SalesforceError)
                mock_apexecute.assert_called()
                assert mock_apexecute.call_count == 3

    def post_cancel_dispatch_status_2xx_ok_test(self, instance_lit_client, dispatch):
        expected_dispatch_response = {
            "Message": None,
            "Status": "Success"
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 200

        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            instance_lit_client.cancel_dispatch(dispatch)
            mock_apexecute.assert_called()
            assert mock_apexecute.call_count == 1

    def post_cancel_dispatch_status_error_ko_test(self, instance_lit_client, dispatch):
        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 400

        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            instance_lit_client.cancel_dispatch(dispatch)
            mock_apexecute.assert_called()
            assert mock_apexecute.call_count == 1

    def post_cancel_dispatch_exception_test(self, instance_lit_client, dispatch):

        response_mock = Mock()
        response_mock.json = Mock(side_effect=Exception)
        response_mock.status_code = 500

        instance_lit_client._salesforce_sdk = Mock(return_value={'status': 200})

        salesforce_exception = SalesforceError('url', 500, 'resource_name', 'content')
        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          side_effect=salesforce_exception) as mock_apexecute:
            instance_lit_client.cancel_dispatch(dispatch)
            mock_apexecute.assert_called()
            assert mock_apexecute.call_count == 1

    def get_dispatch_test(self, instance_lit_client, dispatch):
        expected_dispatch_response = {
            "APIRequestID": "a130v000001hWcNAAU",
            "Dispatch": dispatch,
            "Message": None,
            "Status": "Success"
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 200
        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = instance_lit_client.get_dispatch("DIS37330")
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.OK

    def get_dispatch_with_error_400_test(self, instance_lit_client):
        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }

        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = instance_lit_client.get_dispatch("DIS37330")
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.BAD_REQUEST

    def get_dispatch_with_error_500_test(self, instance_lit_client):
        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          side_effect=Exception("Error")) as mock_apexecute:
            response = instance_lit_client.get_dispatch("DIS37330")
            mock_apexecute.assert_called()
            assert mock_apexecute.call_count == 3
            assert response == "Error"

    def get_dispatch_with_error_salesforce_sdk_test(self, instance_lit_client):
        salesforce_exception = SalesforceError('url', 500, 'resource_name', 'content')
        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          side_effect=salesforce_exception) as mock_apexecute:
            try:
                instance_lit_client.get_dispatch("DIS37330")
            except SalesforceError as sfe:
                assert isinstance(sfe, SalesforceError)
                mock_apexecute.assert_called()
                assert mock_apexecute.call_count == 3

    def get_all_dispatches_test(self, instance_lit_client, dispatch):
        expected_dispatch_response = {
            "APIRequestID": "a130v000001hWcNAAU",
            "DispatchList": [dispatch],
            "Message": "Total Number of Dispatches: 1",
            "Status": "Success"
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 200
        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = instance_lit_client.get_all_dispatches()
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.OK

    def get_all_dispatches_with_error_400_test(self, instance_lit_client):
        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }

        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = instance_lit_client.get_all_dispatches()
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.BAD_REQUEST

    def get_all_dispatches_with_error_500_test(self, instance_lit_client):
        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          side_effect=Exception("Error")) as mock_apexecute:
            response = instance_lit_client.get_all_dispatches()
            mock_apexecute.assert_called()
            assert mock_apexecute.call_count == 3
            assert response == "Error"

    def get_all_dispatches_with_error_salesforce_sdk_test(self, instance_lit_client):
        salesforce_exception = SalesforceError('url', 500, 'resource_name', 'content')
        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          side_effect=salesforce_exception) as mock_apexecute:
            try:
                instance_lit_client.get_all_dispatches()
            except SalesforceError as sfe:
                assert isinstance(sfe, SalesforceError)
                mock_apexecute.assert_called()
                assert mock_apexecute.call_count == 3

    def post_update_dispatch_test(self, instance_lit_client, dispatch):

        expected_dispatch_response = {
            "APIRequestID": "a130v000001hWcNAAU",
            "Dispatch": dispatch,
            "Message": None,
            "Status": "Success"
        }

        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = instance_lit_client.update_dispatch(dispatch)
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.OK

    def post_update_dispatch_with_error_400_test(self, instance_lit_client, dispatch):
        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }

        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = instance_lit_client.update_dispatch(dispatch)
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.BAD_REQUEST

    def post_update_dispatch_with_error_500_test(self, instance_lit_client, dispatch):
        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          side_effect=Exception("Error")) as mock_apexecute:
            response = instance_lit_client.update_dispatch(dispatch)
            mock_apexecute.assert_called()
            assert mock_apexecute.call_count == 3
            assert response == "Error"

    def post_update_dispatch_with_error_salesforce_sdk_test(self, instance_lit_client, dispatch):
        salesforce_exception = SalesforceError('url', 500, 'resource_name', 'content')
        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          side_effect=salesforce_exception) as mock_apexecute:
            try:
                instance_lit_client.update_dispatch(dispatch)
            except SalesforceError as sfe:
                assert isinstance(sfe, SalesforceError)
                mock_apexecute.assert_called()
                assert mock_apexecute.call_count == 3

    def post_upload_file_dispatch_test(self, instance_lit_client):
        expected_dispatch_response = {
            "Status": "Success",
            "Message": "File ID:00P0v000003K1p6EAC",
            "Dispatch": None,
            "APIRequestID": None
        }
        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = instance_lit_client.upload_file(
                "DIS37330", b"bytes from the file", "test.txt", "application/octet-stream")
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.OK

    def post_upload_file_dispatch_pdf_test(self, instance_lit_client):
        expected_dispatch_response = {
            "Status": "Success",
            "Message": "File ID:00P0v000003K1p6EAC",
            "Dispatch": None,
            "APIRequestID": None
        }

        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = instance_lit_client.upload_file(
                "DIS37330", b"bytes from the file", "test.txt", "application/pdf")
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.OK

    def post_upload_file_dispatch_with_error_400_test(self, instance_lit_client):
        expected_dispatch_response = {
            "Status": "error",
            "Message": "Insert failed",
            "Dispatch": None,
            "APIRequestID": None
        }

        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = instance_lit_client.upload_file(
                "DIS37330", b"bytes from the file", "test.txt", "application/octet-stream")
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.BAD_REQUEST

    def post_upload_file_dispatch_with_error_500_test(self, instance_lit_client):
        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          side_effect=Exception("Error")) as mock_apexecute:
            response = instance_lit_client.upload_file(
                "DIS37330", b"bytes from the file", "test.txt", "application/octet-stream")
            mock_apexecute.assert_called()
            assert mock_apexecute.call_count == 3
            assert response == "Error"

    def post_upload_file_dispatch_with_error_salesforce_sdk_test(self, instance_lit_client):
        salesforce_exception = SalesforceError('url', 500, 'resource_name', 'content')
        with patch.object(instance_lit_client._salesforce_sdk, 'apexecute',
                          side_effect=salesforce_exception) as mock_apexecute:
            try:
                instance_lit_client.upload_file(
                    "DIS37330", b"bytes from the file", "test.txt", "application/octet-stream")
            except SalesforceError as sfe:
                assert isinstance(sfe, SalesforceError)
                mock_apexecute.assert_called()
                assert mock_apexecute.call_count == 3
