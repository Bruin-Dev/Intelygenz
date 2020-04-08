from http import HTTPStatus
from unittest.mock import Mock
from unittest.mock import patch

from application.clients.lit_client import LitClient
from pytest import raises
from simple_salesforce import SalesforceGeneralError, SalesforceAuthenticationFailed, SalesforceError

from application.clients import lit_client as lit_client_module
from config import testconfig


class TestLitClient:

    def instance_test(self):
        logger = Mock()
        config = testconfig

        lit_client = LitClient(logger, config)

        assert lit_client._logger is logger
        assert lit_client._config is config

    def login_test(self):
        logger = Mock()
        config = testconfig
        lit_client = LitClient(logger, config)
        with patch.object(lit_client_module, 'Salesforce', return_value=Mock()) as mock_login:
            response = lit_client.login()

            mock_login.assert_called_once()
            assert response is True

    def login_error_test(self):
        logger = Mock()
        config = testconfig

        lit_client = LitClient(logger, config)

        with patch.object(lit_client_module, 'Salesforce', side_effect=Exception("mocked error")) as mock_login:
            response = lit_client.login()
            assert response is 'mocked error'

    def login_error_invalid_credentials_test(self):
        logger = Mock()
        config = testconfig
        lit_client = LitClient(logger, config)
        salesforce_exception = SalesforceGeneralError("mocked error", "a", "b", "c")
        with patch.object(lit_client_module, 'Salesforce', side_effect=salesforce_exception) as mock_login:
            response = lit_client.login()
            assert response is "mocked error"
            assert mock_login.call_count == config.LIT_CONFIG['attempts']

    def login_error_authentication_failure_test(self):
        logger = Mock()
        config = testconfig
        lit_client = LitClient(logger, config)
        salesforce_exception = SalesforceAuthenticationFailed('mocked_error', 'a')
        with patch.object(lit_client_module, 'Salesforce', side_effect=salesforce_exception) as mock_login:
            response = lit_client.login()
            assert response is 'mocked_error'
            assert mock_login.call_count == config.LIT_CONFIG['attempts']

    def get_headers_test(self):
        logger = Mock()
        config = testconfig
        expected_headers = {
            "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
        }
        lit_client = LitClient(logger, config)
        with patch.object(lit_client_module, 'Salesforce', return_value=True) as mock_login:
            response = lit_client.login()
            assert response is True
            mock_login.assert_called_once()
            assert expected_headers == lit_client._get_request_headers()

    def post_create_dispatch_test(self):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        dipatch_contents = {
            "RequestDispatch": {
                "Date_of_Dispatch": "2016-11-16",
                "Site_Survey_Quote_Required": False,
                "Local_Time_of_Dispatch": "7AM-9AM",
                "Time_Zone_Local": "Pacific Time",
                "Turn_Up": "Yes",
                "Hard_Time_of_Dispatch_Local": "7AM-9AM",
                "Hard_Time_of_Dispatch_Time_Zone_Local": "Eastern Time",
                "Name_of_MetTel_Requester": "Test User1",
                "MetTel_Group_Email": "test@mettel.net",
                "MetTel_Requester_Email": "test@mettel.net",
                "MetTel_Department": "Customer Care",
                "MetTel_Department_Phone_Number": "1233211234",
                "Backup_MetTel_Department_Phone_Number": "1233211234",
                "Job_Site": "test",
                "Job_Site_Street": "test street",
                "Job_Site_City": "test city",
                "Job_Site_State": "test state2",
                "Job_Site_Zip_Code": "123321",
                "Scope_of_Work": "test",
                "MetTel_Tech_Call_In_Instructions": "test",
                "Special_Dispatch_Notes": "Test Create No Special Dispatch Notes to Pass Forward",
                "Job_Site_Contact_Name_and_Phone_Number": "test",
                "Information_for_Tech": "test",
                "Special_Materials_Needed_for_Dispatch": "test"
            }
        }
        expected_dispatch_response = {
            "APIRequestID": "a130v000001hWcNAAU",
            "Dispatch": {
                "Backup_MetTel_Department_Phone_Number": "1233211234",
                "Close_Out_Notes": None,
                "Date_of_Dispatch": "2016-11-16",
                "Dispatch_Number": "DIS37330",
                "Dispatch_Status": "New Dispatch",
                "Hard_Time_of_Dispatch_Local": "7AM-9AM",
                "Hard_Time_of_Dispatch_Time_Zone_Local": "Eastern Time",
                "Information_for_Tech": "test",
                "Job_Site": "test",
                "Job_Site_City": "test city",
                "Job_Site_Contact_Name_and_Phone_Number": "test",
                "Job_Site_State": "test state2",
                "Job_Site_Street": "test street",
                "Job_Site_Zip_Code": "123321",
                "Local_Time_of_Dispatch": None,
                "MetTel_Bruin_TicketID": None,
                "MetTel_Department": "Customer Care",
                "MetTel_Department_Phone_Number": "1233211234",
                "MetTel_Group_Email": "test@mettel.net",
                "MetTel_Note_Updates": None,
                "MetTel_Requester_Email": "test@mettel.net",
                "MetTel_Tech_Call_In_Instructions": "test",
                "Name_of_MetTel_Requester": "Test User1",
                "Scope_of_Work": "test",
                "Site_Survey_Quote_Required": None,
                "Special_Dispatch_Notes": "Test Create No Special Dispatch Notes to Pass Forward",
                "Special_Materials_Needed_for_Dispatch": "test",
                "Tech_Arrived_On_Site": None,
                "Tech_First_Name": None,
                "Tech_Mobile_Number": None,
                "Tech_Off_Site": None,
                "Time_Zone_Local": "Pacific Time",
                "Time_of_Check_In": None,
                "Time_of_Check_Out": None,
                "turn_up": "Yes"
            },
            "Message": None,
            "Status": "Success"
        }

        lit_client = LitClient(logger, config)
        lit_client._bearer_token = "Someverysecretaccesstoken"
        lit_client._base_url = "https://cs66.salesforce.com"
        lit_client._salesforce_sdk = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 200

        with patch.object(lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            post_response = lit_client.create_dispatch(dipatch_contents)

            mock_apexecute.assert_called_once()

            assert post_response["body"] == expected_dispatch_response
            assert post_response["status"] == HTTPStatus.OK

    def post_create_dispatch_with_error_400_test(self):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        dipatch_contents = {
            "RequestDispatch": {
                "Date_of_Dispatch": "2016-11-16",
                "Site_Survey_Quote_Required": False,
                "Local_Time_of_Dispatch": "7AM-9AM",
                "Time_Zone_Local": "Pacific Time",
                "Turn_Up": "Yes",
                "Hard_Time_of_Dispatch_Local": "7AM-9AM",
                "Hard_Time_of_Dispatch_Time_Zone_Local": "Eastern Time",
                "Name_of_MetTel_Requester": "Test User1",
                "MetTel_Group_Email": "test@mettel.net",
                "MetTel_Requester_Email": "test@mettel.net",
                "MetTel_Department": "Customer Care",
                "MetTel_Department_Phone_Number": "1233211234",
                "Backup_MetTel_Department_Phone_Number": "1233211234",
                "Job_Site": "test",
                "Job_Site_Street": "test street",
                "Job_Site_City": "test city",
                "Job_Site_State": "test state2",
                "Job_Site_Zip_Code": "123321",
                "Scope_of_Work": "test",
                "MetTel_Tech_Call_In_Instructions": "test",
                "Special_Dispatch_Notes": "Test Create No Special Dispatch Notes to Pass Forward",
                "Job_Site_Contact_Name_and_Phone_Number": "test",
                "Information_for_Tech": "test",
                "Special_Materials_Needed_for_Dispatch": "test"
            }
        }
        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }
        lit_client = LitClient(logger, config)
        lit_client._bearer_token = "Someverysecretaccesstoken"
        lit_client._base_url = "https://cs66.salesforce.com"
        lit_client._salesforce_sdk = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 400

        with patch.object(lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            post_response = lit_client.create_dispatch(dipatch_contents)
            mock_apexecute.assert_called_once()

            assert post_response["body"] == expected_dispatch_response
            assert post_response["status"] == HTTPStatus.BAD_REQUEST

    def post_create_dispatch_with_error_salesforce_sdk_test(self):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        dipatch_contents = {
            "RequestDispatch": {
                "Date_of_Dispatch": "2016-11-16",
                "Site_Survey_Quote_Required": False,
                "Local_Time_of_Dispatch": "7AM-9AM",
                "Time_Zone_Local": "Pacific Time",
                "Turn_Up": "Yes",
                "Hard_Time_of_Dispatch_Local": "7AM-9AM",
                "Hard_Time_of_Dispatch_Time_Zone_Local": "Eastern Time",
                "Name_of_MetTel_Requester": "Test User1",
                "MetTel_Group_Email": "test@mettel.net",
                "MetTel_Requester_Email": "test@mettel.net",
                "MetTel_Department": "Customer Care",
                "MetTel_Department_Phone_Number": "1233211234",
                "Backup_MetTel_Department_Phone_Number": "1233211234",
                "Job_Site": "test",
                "Job_Site_Street": "test street",
                "Job_Site_City": "test city",
                "Job_Site_State": "test state2",
                "Job_Site_Zip_Code": "123321",
                "Scope_of_Work": "test",
                "MetTel_Tech_Call_In_Instructions": "test",
                "Special_Dispatch_Notes": "Test Create No Special Dispatch Notes to Pass Forward",
                "Job_Site_Contact_Name_and_Phone_Number": "test",
                "Information_for_Tech": "test",
                "Special_Materials_Needed_for_Dispatch": "test"
            }
        }
        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }
        lit_client = LitClient(logger, config)
        lit_client._bearer_token = "Someverysecretaccesstoken"
        lit_client._base_url = "https://cs66.salesforce.com"
        lit_client._salesforce_sdk = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 400

        salesforce_exception = SalesforceError('url', 500, 'resource_name', 'content')
        with patch.object(lit_client._salesforce_sdk, 'apexecute',
                          side_effect=salesforce_exception) as mock_apexecute:
            try:
                lit_client.create_dispatch(dipatch_contents)
            except SalesforceError as sfe:
                assert isinstance(sfe, SalesforceError)
                mock_apexecute.assert_called()
                assert mock_apexecute.call_count == 3

    def get_dispatch_test(self):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        dipatch_number = "DIS37330"
        expected_dispatch_response = {
            "APIRequestID": "a130v000001hWcNAAU",
            "Dispatch": {
                "Backup_MetTel_Department_Phone_Number": "1233211234",
                "Close_Out_Notes": None,
                "Date_of_Dispatch": "2016-11-16",
                "Dispatch_Number": "DIS37330",
                "Dispatch_Status": "New Dispatch",
                "Hard_Time_of_Dispatch_Local": "7AM-9AM",
                "Hard_Time_of_Dispatch_Time_Zone_Local": "Eastern Time",
                "Information_for_Tech": "test",
                "Job_Site": "test",
                "Job_Site_City": "test city",
                "Job_Site_Contact_Name_and_Phone_Number": "test",
                "Job_Site_State": "test state2",
                "Job_Site_Street": "test street",
                "Job_Site_Zip_Code": "123321",
                "Local_Time_of_Dispatch": None,
                "MetTel_Bruin_TicketID": None,
                "MetTel_Department": "Customer Care",
                "MetTel_Department_Phone_Number": "1233211234",
                "MetTel_Group_Email": "test@mettel.net",
                "MetTel_Note_Updates": None,
                "MetTel_Requester_Email": "test@mettel.net",
                "MetTel_Tech_Call_In_Instructions": "test",
                "Name_of_MetTel_Requester": "Test User1",
                "Scope_of_Work": "test",
                "Site_Survey_Quote_Required": None,
                "Special_Dispatch_Notes": "Test Create No Special Dispatch Notes to Pass Forward",
                "Special_Materials_Needed_for_Dispatch": "test",
                "Tech_Arrived_On_Site": None,
                "Tech_First_Name": None,
                "Tech_Mobile_Number": None,
                "Tech_Off_Site": None,
                "Time_Zone_Local": "Pacific Time",
                "Time_of_Check_In": None,
                "Time_of_Check_Out": None,
                "turn_up": "Yes"
            },
            "Message": None,
            "Status": "Success"
        }
        lit_client = LitClient(logger, config)
        lit_client._bearer_token = "Someverysecretaccesstoken"
        lit_client._base_url = "https://cs66.salesforce.com"
        lit_client._salesforce_sdk = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 200
        with patch.object(lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = lit_client.get_dispatch(dipatch_number)
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.OK

    def get_dispatch_with_error_400_test(self):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        dipatch_number = "DIS37330"
        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }
        lit_client = LitClient(logger, config)
        lit_client._bearer_token = "Someverysecretaccesstoken"
        lit_client._base_url = "https://cs66.salesforce.com"
        lit_client._salesforce_sdk = Mock()

        with patch.object(lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = lit_client.get_dispatch(dipatch_number)
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.BAD_REQUEST

    def get_dispatch_with_error_salesforce_sdk_test(self):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        dipatch_number = "DIS37330"
        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }
        lit_client = LitClient(logger, config)
        lit_client._bearer_token = "Someverysecretaccesstoken"
        lit_client._base_url = "https://cs66.salesforce.com"
        lit_client._salesforce_sdk = Mock()
        salesforce_exception = SalesforceError('url', 500, 'resource_name', 'content')
        with patch.object(lit_client._salesforce_sdk, 'apexecute',
                          side_effect=salesforce_exception) as mock_apexecute:
            try:
                lit_client.get_dispatch(dipatch_number)
            except SalesforceError as sfe:
                assert isinstance(sfe, SalesforceError)
                mock_apexecute.assert_called()
                assert mock_apexecute.call_count == 3

    def post_update_dispatch_test(self):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        dispatch_number = "DIS37330"
        dipatch_contents = {
            "RequestDispatch": {
                "Date_of_Dispatch": "2016-11-16",
                "Site_Survey_Quote_Required": False,
                "Local_Time_of_Dispatch": "7AM-9AM",
                "Time_Zone_Local": "Pacific Time",
                "Turn_Up": "Yes",
                "Hard_Time_of_Dispatch_Local": "7AM-9AM",
                "Hard_Time_of_Dispatch_Time_Zone_Local": "Eastern Time",
                "Name_of_MetTel_Requester": "Test User1",
                "MetTel_Group_Email": "test@mettel.net",
                "MetTel_Requester_Email": "test@mettel.net",
                "MetTel_Department": "Customer Care",
                "MetTel_Department_Phone_Number": "1233211234",
                "Backup_MetTel_Department_Phone_Number": "1233211234",
                "Job_Site": "test",
                "Job_Site_Street": "test street",
                "Job_Site_City": "test city",
                "Job_Site_State": "test state2",
                "Job_Site_Zip_Code": "123321",
                "Scope_of_Work": "test",
                "MetTel_Tech_Call_In_Instructions": "test",
                "Special_Dispatch_Notes": "Test Create No Special Dispatch Notes to Pass Forward",
                "Job_Site_Contact_Name_and_Phone_Number": "test",
                "Information_for_Tech": "test",
                "Special_Materials_Needed_for_Dispatch": "test"
            }
        }
        expected_dispatch_response = {
            "APIRequestID": "a130v000001hWcNAAU",
            "Dispatch": {
                "Backup_MetTel_Department_Phone_Number": "1233211234",
                "Close_Out_Notes": None,
                "Date_of_Dispatch": "2016-11-16",
                "Dispatch_Number": "DIS37330",
                "Dispatch_Status": "New Dispatch",
                "Hard_Time_of_Dispatch_Local": "7AM-9AM",
                "Hard_Time_of_Dispatch_Time_Zone_Local": "Eastern Time",
                "Information_for_Tech": "test",
                "Job_Site": "test",
                "Job_Site_City": "test city",
                "Job_Site_Contact_Name_and_Phone_Number": "test",
                "Job_Site_State": "test state2",
                "Job_Site_Street": "test street",
                "Job_Site_Zip_Code": "123321",
                "Local_Time_of_Dispatch": None,
                "MetTel_Bruin_TicketID": None,
                "MetTel_Department": "Customer Care",
                "MetTel_Department_Phone_Number": "1233211234",
                "MetTel_Group_Email": "test@mettel.net",
                "MetTel_Note_Updates": None,
                "MetTel_Requester_Email": "test@mettel.net",
                "MetTel_Tech_Call_In_Instructions": "test",
                "Name_of_MetTel_Requester": "Test User1",
                "Scope_of_Work": "test",
                "Site_Survey_Quote_Required": None,
                "Special_Dispatch_Notes": "Test Create No Special Dispatch Notes to Pass Forward",
                "Special_Materials_Needed_for_Dispatch": "test",
                "Tech_Arrived_On_Site": None,
                "Tech_First_Name": None,
                "Tech_Mobile_Number": None,
                "Tech_Off_Site": None,
                "Time_Zone_Local": "Pacific Time",
                "Time_of_Check_In": None,
                "Time_of_Check_Out": None,
                "turn_up": "Yes"
            },
            "Message": None,
            "Status": "Success"
        }
        lit_client = LitClient(logger, config)
        lit_client._bearer_token = "Someverysecretaccesstoken"
        lit_client._base_url = "https://cs66.salesforce.com"
        lit_client._salesforce_sdk = Mock()

        with patch.object(lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = lit_client.update_dispatch(dipatch_contents)
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.OK

    def post_update_dispatch_with_error_400_test(self):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        dispatch_number = "DIS37330"
        dipatch_contents = {
            "RequestDispatch": {
                "Date_of_Dispatch": "2016-11-16",
                "Site_Survey_Quote_Required": False,
                "Local_Time_of_Dispatch": "7AM-9AM",
                "Time_Zone_Local": "Pacific Time",
                "Turn_Up": "Yes",
                "Hard_Time_of_Dispatch_Local": "7AM-9AM",
                "Hard_Time_of_Dispatch_Time_Zone_Local": "Eastern Time",
                "Name_of_MetTel_Requester": "Test User1",
                "MetTel_Group_Email": "test@mettel.net",
                "MetTel_Requester_Email": "test@mettel.net",
                "MetTel_Department": "Customer Care",
                "MetTel_Department_Phone_Number": "1233211234",
                "Backup_MetTel_Department_Phone_Number": "1233211234",
                "Job_Site": "test",
                "Job_Site_Street": "test street",
                "Job_Site_City": "test city",
                "Job_Site_State": "test state2",
                "Job_Site_Zip_Code": "123321",
                "Scope_of_Work": "test",
                "MetTel_Tech_Call_In_Instructions": "test",
                "Special_Dispatch_Notes": "Test Create No Special Dispatch Notes to Pass Forward",
                "Job_Site_Contact_Name_and_Phone_Number": "test",
                "Information_for_Tech": "test",
                "Special_Materials_Needed_for_Dispatch": "test"
            }
        }
        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }
        lit_client = LitClient(logger, config)
        lit_client._bearer_token = "Someverysecretaccesstoken"
        lit_client._base_url = "https://cs66.salesforce.com"

        lit_client._salesforce_sdk = Mock()

        with patch.object(lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = lit_client.update_dispatch(dipatch_contents)
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.BAD_REQUEST

    def post_update_dispatch_with_error_salesforce_sdk_test(self):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        dispatch_number = "DIS37330"
        dipatch_contents = {
            "RequestDispatch": {
                "Date_of_Dispatch": "2016-11-16",
                "Site_Survey_Quote_Required": False,
                "Local_Time_of_Dispatch": "7AM-9AM",
                "Time_Zone_Local": "Pacific Time",
                "Turn_Up": "Yes",
                "Hard_Time_of_Dispatch_Local": "7AM-9AM",
                "Hard_Time_of_Dispatch_Time_Zone_Local": "Eastern Time",
                "Name_of_MetTel_Requester": "Test User1",
                "MetTel_Group_Email": "test@mettel.net",
                "MetTel_Requester_Email": "test@mettel.net",
                "MetTel_Department": "Customer Care",
                "MetTel_Department_Phone_Number": "1233211234",
                "Backup_MetTel_Department_Phone_Number": "1233211234",
                "Job_Site": "test",
                "Job_Site_Street": "test street",
                "Job_Site_City": "test city",
                "Job_Site_State": "test state2",
                "Job_Site_Zip_Code": "123321",
                "Scope_of_Work": "test",
                "MetTel_Tech_Call_In_Instructions": "test",
                "Special_Dispatch_Notes": "Test Create No Special Dispatch Notes to Pass Forward",
                "Job_Site_Contact_Name_and_Phone_Number": "test",
                "Information_for_Tech": "test",
                "Special_Materials_Needed_for_Dispatch": "test"
            }
        }
        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }
        lit_client = LitClient(logger, config)
        lit_client._bearer_token = "Someverysecretaccesstoken"
        lit_client._base_url = "https://cs66.salesforce.com"

        lit_client._salesforce_sdk = Mock()

        salesforce_exception = SalesforceError('url', 500, 'resource_name', 'content')
        with patch.object(lit_client._salesforce_sdk, 'apexecute',
                          side_effect=salesforce_exception) as mock_apexecute:
            try:
                lit_client.update_dispatch(dipatch_contents)
            except SalesforceError as sfe:
                assert isinstance(sfe, SalesforceError)
                mock_apexecute.assert_called()
                assert mock_apexecute.call_count == 3

    def post_upload_file_dispatch_test(self):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        file_name = "test.txt"
        file_content_type = "application/octet-stream"
        dispatch_number = "DIS37330"
        dipatch_contents = b"bytes from the file"
        expected_dispatch_response = {
            "Status": "Success",
            "Message": "File ID:00P0v000003K1p6EAC",
            "Dispatch": None,
            "APIRequestID": None
        }
        lit_client = LitClient(logger, config)
        lit_client._bearer_token = "Someverysecretaccesstoken"
        lit_client._base_url = "https://cs66.salesforce.com"
        lit_client._salesforce_sdk = Mock()

        with patch.object(lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = lit_client.upload_file(
                dispatch_number, dipatch_contents, file_name, file_content_type)
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.OK

    def post_upload_file_dispatch_pdf_test(self):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        file_name = "test.txt"
        file_content_type = "application/pdf"
        dispatch_number = "DIS37330"
        dipatch_contents = b"bytes from the file"
        expected_dispatch_response = {
            "Status": "Success",
            "Message": "File ID:00P0v000003K1p6EAC",
            "Dispatch": None,
            "APIRequestID": None
        }
        lit_client = LitClient(logger, config)
        lit_client._bearer_token = "Someverysecretaccesstoken"
        lit_client._base_url = "https://cs66.salesforce.com"
        lit_client._salesforce_sdk = Mock()

        with patch.object(lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = lit_client.upload_file(
                dispatch_number, dipatch_contents, file_name, file_content_type)
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.OK

    def post_upload_file_dispatch_with_error_400_test(self):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        file_name = "test.txt"
        file_content_type = "application/octet-stream"
        dispatch_number = "DIS37330"
        dipatch_contents = b"bytes from the file"
        expected_dispatch_response = {
            "Status": "error",
            "Message": "Insert failed",
            "Dispatch": None,
            "APIRequestID": None
        }
        lit_client = LitClient(logger, config)
        lit_client._bearer_token = "Someverysecretaccesstoken"
        lit_client._base_url = "https://cs66.salesforce.com"
        lit_client._salesforce_sdk = Mock()

        with patch.object(lit_client._salesforce_sdk, 'apexecute',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = lit_client.upload_file(
                dispatch_number, dipatch_contents, file_name, file_content_type)
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.BAD_REQUEST

    def post_upload_file_dispatch_with_error_salesforce_sdk_test(self):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        file_name = "test.txt"
        file_content_type = "application/octet-stream"
        dispatch_number = "DIS37330"
        dipatch_contents = b"bytes from the file"
        expected_dispatch_response = {
            "Status": "error",
            "Message": "Insert failed",
            "Dispatch": None,
            "APIRequestID": None
        }
        lit_client = LitClient(logger, config)
        lit_client._bearer_token = "Someverysecretaccesstoken"
        lit_client._base_url = "https://cs66.salesforce.com"
        lit_client._salesforce_sdk = Mock()

        salesforce_exception = SalesforceError('url', 500, 'resource_name', 'content')
        with patch.object(lit_client._salesforce_sdk, 'apexecute',
                          side_effect=salesforce_exception) as mock_apexecute:
            try:
                lit_client.upload_file(
                    dispatch_number, dipatch_contents, file_name, file_content_type)
            except SalesforceError as sfe:
                assert isinstance(sfe, SalesforceError)
                mock_apexecute.assert_called()
                assert mock_apexecute.call_count == 3
