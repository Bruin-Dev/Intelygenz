import collections
from http import HTTPStatus
from unittest.mock import Mock
from unittest.mock import patch

from application.clients.cts_client import CtsClient
from pytest import raises
from simple_salesforce import SalesforceGeneralError, SalesforceAuthenticationFailed, SalesforceError

from application.clients import cts_client as cts_client_module
from config import testconfig


class TestCTSClient:

    def instance_test(self):
        logger = Mock()
        config = testconfig

        cts_client = CtsClient(logger, config)

        assert cts_client._logger is logger
        assert cts_client._config is config

    def login_test(self):
        logger = Mock()
        config = testconfig
        cts_client = CtsClient(logger, config)
        with patch.object(cts_client_module, 'Salesforce', return_value=Mock()) as mock_login:
            response = cts_client.login()

            mock_login.assert_called_once()
            assert response is True

    def login_error_test(self):
        logger = Mock()
        config = testconfig

        cts_client = CtsClient(logger, config)

        with patch.object(cts_client_module, 'Salesforce', side_effect=Exception("mocked error")) as mock_login:
            response = cts_client.login()
            assert response is 'mocked error'

    def login_error_invalid_credentials_test(self):
        logger = Mock()
        config = testconfig
        cts_client = CtsClient(logger, config)
        salesforce_exception = SalesforceGeneralError("mocked error", "a", "b", "c")
        with patch.object(cts_client_module, 'Salesforce', side_effect=salesforce_exception) as mock_login:
            response = cts_client.login()
            assert response is "mocked error"
            assert mock_login.call_count == config.CTS_CONFIG['attempts']

    def login_error_authentication_failure_test(self):
        logger = Mock()
        config = testconfig
        cts_client = CtsClient(logger, config)
        salesforce_exception = SalesforceAuthenticationFailed('mocked_error', 'a')
        with patch.object(cts_client_module, 'Salesforce', side_effect=salesforce_exception) as mock_login:
            response = cts_client.login()
            assert response is 'mocked_error'
            assert mock_login.call_count == config.CTS_CONFIG['attempts']

    def get_headers_test(self):
        logger = Mock()
        config = testconfig
        expected_headers = {
            "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
        }
        cts_client = CtsClient(logger, config)
        with patch.object(cts_client_module, 'Salesforce', return_value=True) as mock_login:
            response = cts_client.login()
            assert response is True
            mock_login.assert_called_once()
            assert expected_headers == cts_client._get_request_headers()

    def create_dispatch_test(self, cts_client, new_dispatch):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        config.CTS_CONFIG['environment'] = 'dev'
        config.ENVIRONMENT_NAME = 'dev'
        cts_client._config = config

        dispatch_contents = new_dispatch
        # for dev - whatever
        expected_dispatch_response = {'fake': 'fake', 'success': True}

        cts_client._bearer_token = "Someverysecretaccesstoken"
        cts_client._base_url = "https://cs66.salesforce.com"
        cts_client._salesforce_sdk = Mock()
        cts_client._salesforce_sdk.Service__c = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 200

        with patch.object(cts_client._salesforce_sdk.Service__c, 'create',
                          return_value=expected_dispatch_response) as mock_apexecute:
            post_response = cts_client.create_dispatch(dispatch_contents)

            mock_apexecute.assert_called_once()

            assert post_response["body"] == expected_dispatch_response
            assert post_response["status"] == HTTPStatus.OK

        config.CTS_CONFIG['environment'] = 'production'
        config.ENVIRONMENT_NAME = 'production'
        cts_client._config = config
        expected_error_response = 'CTS create_dispatch: Not implemented in production.'

        post_response = cts_client.create_dispatch(dispatch_contents)
        assert post_response == expected_error_response

    def create_dispatch_with_error_400_test(self, cts_client, new_dispatch):
        logger = Mock()
        config = testconfig
        logger.error = Mock()
        dispatch_contents = new_dispatch
        config.CTS_CONFIG['environment'] = 'dev'
        config.ENVIRONMENT_NAME = 'dev'
        cts_client._config = config

        dipatch_contents = new_dispatch
        # for dev - whatever
        expected_dispatch_response = {'fake': 'fake', 'success': True}

        cts_client._bearer_token = "Someverysecretaccesstoken"
        cts_client._base_url = "https://cs66.salesforce.com"
        cts_client._salesforce_sdk = Mock()
        cts_client._salesforce_sdk.Service__c = Mock()

        expected_dispatch_response = {
            "Message": None,
            "success": False
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 400

        with patch.object(cts_client._salesforce_sdk.Service__c, 'create',
                          return_value=expected_dispatch_response) as mock_apexecute:
            post_response = cts_client.create_dispatch(dispatch_contents)
            mock_apexecute.assert_called_once()

            assert post_response["body"] == expected_dispatch_response
            assert post_response["status"] == HTTPStatus.BAD_REQUEST

    def create_dispatch_with_error_salesforce_sdk_test(self, cts_client, new_dispatch):
        logger = Mock()
        config = testconfig
        logger.error = Mock()
        dispatch_contents = new_dispatch
        config.CTS_CONFIG['environment'] = 'dev'
        config.ENVIRONMENT_NAME = 'dev'
        cts_client._config = config

        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }
        cts_client._bearer_token = "Someverysecretaccesstoken"
        cts_client._base_url = "https://cs66.salesforce.com"
        cts_client._salesforce_sdk = Mock()
        cts_client._salesforce_sdk.Service__c = Mock()

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 400

        salesforce_exception = SalesforceError('url', 500, 'resource_name', 'content')
        with patch.object(cts_client._salesforce_sdk.Service__c, 'create',
                          side_effect=salesforce_exception) as mock_apexecute:
            try:
                cts_client.create_dispatch(dispatch_contents)
            except SalesforceError as sfe:
                assert isinstance(sfe, SalesforceError)
                mock_apexecute.assert_called()
                assert mock_apexecute.call_count == 3

    def get_dispatch_test(self, cts_client, cts_repository):
        logger = Mock()
        config = testconfig
        logger.error = Mock()
        dispatch_number = 'S-12345'
        config.CTS_CONFIG['environment'] = 'dev'
        config.ENVIRONMENT_NAME = 'dev'
        cts_client._config = config

        cts_client._bearer_token = "Someverysecretaccesstoken"
        cts_client._base_url = "https://cs66.salesforce.com"
        cts_client._salesforce_sdk = Mock()
        expected_dispatch_response = {'fake': 'fake'}

        with patch.object(cts_client._salesforce_sdk, 'query',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = cts_client.get_dispatch(dispatch_number, cts_repository._cts_query_fields)
            mock_apexecute.assert_called_once()
            assert response["body"] == dict(expected_dispatch_response)
            assert response["status"] == HTTPStatus.OK

    def get_dispatch_with_error_salesforce_sdk_test(self, cts_client, cts_repository):
        logger = Mock()
        config = testconfig
        logger.error = Mock()
        config.CTS_CONFIG['environment'] = 'dev'
        config.ENVIRONMENT_NAME = 'dev'
        cts_client._config = config

        dispatch_number = "S-12345"
        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }
        cts_client._bearer_token = "Someverysecretaccesstoken"
        cts_client._base_url = "https://cs66.salesforce.com"
        cts_client._salesforce_sdk = Mock()
        cts_client._salesforce_sdk.Service__c = Mock()

        salesforce_exception = SalesforceError('url', 500, 'resource_name', 'content')
        with patch.object(cts_client._salesforce_sdk.Service__c, 'query',
                          side_effect=salesforce_exception) as mock_apexecute:
            try:
                cts_client.get_dispatch(dispatch_number, cts_repository._cts_query_fields)
            except SalesforceError as sfe:
                assert isinstance(sfe, SalesforceError)
                mock_apexecute.assert_called()
                assert mock_apexecute.call_count == 3

    def get_all_dispatches_test(self, cts_repository):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        dispatch_number = "S-12345"
        expected_dispatch_response = {
          "code": 200,
          "message": {
            "totalSize": 1,
            "done": True,
            "records": [
              {
                "attributes": {
                  "type": "Service__c",
                  "url": "/services/data/v42.0/sobjects/Service__c/a260n000000dXTkAAM"
                },
                "Check_In_Date__c": None,
                "Check_Out_Date__c": None,
                "City__c": "Pleasantown",
                "Confirmed__c": False,
                "Country__c": None,
                "Description__c": "Onsite Time Needed: 2020-06-20 12:30PM\r\n"
                                  "Onsite Timezone: Pacific Time\r\nReference: 4689549\r\n"
                                  "SLA Level: Pre-planned\r\nLocation Country: United States\r\n"
                                  "Location: TEST Red Rose Inn\r\nPleasantown, CA 99088\r\n"
                                  "Location ID: 123 Fake Street 123 Fake Street\r\n"
                                  "Location Owner: TEST Red Rose Inn\r\nOnsite Contact: Jane Doe\r\n"
                                  "Contact #: +1 666 6666 666\r\n"
                                  "Failure Experienced: TEST Device is bouncing constantly\r\n"
                                  "Onsite SOW: This is a TEST\r\nMaterials Needed:\r\n"
                                  "TEST Laptop, cable, tuner, ladder, internet hotspot\r\n"
                                  "Service Category: Troubleshooting\r\nName: Karen Doe\r\n"
                                  "Phone: +1 666 6666 666\r\nEmail: karen.doe@mettel.net",
                "Duration_Onsite__c": 2.02,
                "Early_Start__c": "2020-06-20T19:30:00.000+0000",
                "Ext_Ref_Num__c": "4689549",
                "Issue_Summary__c": "TEST Device is bouncing constantly",
                "Local_Site_Time__c": "2020-06-20T16:30:00.000+0000",
                "Account__c": "0010n000017dsThAAI",
                "Lookup_Location_Owner__c": "TEST Red Rose Inn",
                "On_Site_Elapsed_Time__c": "0 Days 2 Hours 1 Minutes",
                "On_Time_Auto__c": True,
                "Open_Date__c": "2020-06-18T16:03:00.000+0000",
                "Parent_Account_Associated__c": "Mettel",
                "Service_Order__c": "a200n000000hKPNAA2",
                "Project_Name__c": "Sevice Requests",
                "Location__c": None,
                "Resource__c": "a1s0n000000NuHOAA0",
                "Resource_Assigned_Timestamp__c": "2020-06-18T16:23:50.000+0000",
                "Resource_Email__c": "jsmith@test.com",
                "Resource_Phone_Number__c": "123-456-7890",
                "Site_Notes__c": "Site complete, no issues to report.",
                "Site_Status__c": "Site Complete",
                "Special_Shipping_Instructions__c": None,
                "State__c": "CA",
                "Street__c": "123 Fake Street",
                "Status__c": "Complete Pending Collateral",
                "Service_Type__c": "a250n000000PMQ2AAO",
                "Zip__c": "99088"
              }
            ]
          }
        }

        where = ""
        query = "SELECT {} FROM Service__c {}".format(cts_repository._cts_query_fields, where)

        cts_client = CtsClient(logger, config)
        cts_client._bearer_token = "Someverysecretaccesstoken"
        cts_client._base_url = "https://cs66.salesforce.com"
        cts_client._salesforce_sdk = Mock()
        cts_client._salesforce_sdk.query = Mock(return_value={})

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_dispatch_response)
        response_mock.status_code = 200
        with patch.object(cts_client._salesforce_sdk, 'query',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = cts_client.get_all_dispatches(cts_repository._cts_query_fields)
            cts_client._salesforce_sdk.query.assert_called_once()
            mock_apexecute.assert_called_once_with(query)

            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.OK

    def get_all_dispatches_with_error_salesforce_sdk_test(self):
        logger = Mock()
        config = testconfig
        logger.error = Mock()

        dispatch_number = "DIS37330"
        expected_dispatch_response = {
            "Message": None,
            "Status": "error"
        }
        describe_return = {'fields': [{'name': 'id'}]}
        query = "SELECT id FROM Service__c"

        cts_client = CtsClient(logger, config)
        cts_client._bearer_token = "Someverysecretaccesstoken"
        cts_client._base_url = "https://cs66.salesforce.com"
        cts_client._salesforce_sdk = Mock()
        cts_client._salesforce_sdk.Service__c = Mock()
        cts_client._salesforce_sdk.Service__c.describe = Mock(return_value=describe_return)

        salesforce_exception = SalesforceError('url', 500, 'resource_name', 'content')
        with patch.object(cts_client._salesforce_sdk, 'query',
                          side_effect=salesforce_exception) as mock_apexecute:
            try:
                cts_client.get_all_dispatches()
            except SalesforceError as sfe:
                assert isinstance(sfe, SalesforceError)
                mock_apexecute.assert_called()
                assert mock_apexecute.call_count == 3

    def update_dispatch_test(self):
        # TODO: not really implemented
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
        cts_client = CtsClient(logger, config)
        cts_client._bearer_token = "Someverysecretaccesstoken"
        cts_client._base_url = "https://cs66.salesforce.com"
        cts_client._salesforce_sdk = Mock()
        cts_client._salesforce_sdk.Service__c = Mock()

        with patch.object(cts_client._salesforce_sdk.Service__c, 'update',
                          return_value=expected_dispatch_response) as mock_apexecute:
            response = cts_client.update_dispatch(dispatch_number, dipatch_contents)
            mock_apexecute.assert_called_once()
            assert response["body"] == expected_dispatch_response
            assert response["status"] == HTTPStatus.OK

    def update_dispatch_with_error_salesforce_sdk_test(self):
        # TODO: not really implemented
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

        cts_client = CtsClient(logger, config)
        cts_client._bearer_token = "Someverysecretaccesstoken"
        cts_client._base_url = "https://cs66.salesforce.com"

        cts_client._salesforce_sdk = Mock()
        cts_client._salesforce_sdk.Service__c = Mock()

        salesforce_exception = SalesforceError('url', 500, 'resource_name', 'content')
        with patch.object(cts_client._salesforce_sdk.Service__c, 'update',
                          side_effect=salesforce_exception) as mock_apexecute:
            try:
                cts_client.update_dispatch(dispatch_number, dipatch_contents)
            except SalesforceError as sfe:
                assert isinstance(sfe, SalesforceError)
                mock_apexecute.assert_called()
                assert mock_apexecute.call_count == 3
