import base64
from http import HTTPStatus

import pytest
from unittest.mock import Mock, patch
from unittest.mock import call

from quart.exceptions import HTTPException

import application
from config import testconfig as config
from application.server.api_server import DispatchServer
from asynctest import CoroutineMock
from quart import Quart
from hypercorn.config import Config as HyperCornConfig
import application.server.api_server as api_server_module


class TestApiServer:

    def instance_test(self):
        logger = Mock()
        redis_client = Mock()
        event_bus = Mock()

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        assert api_server_test._logger is logger
        assert api_server_test._redis_client is redis_client
        assert api_server_test._event_bus is event_bus

        assert api_server_test._title == config.QUART_CONFIG['title']
        assert api_server_test._port == config.QUART_CONFIG['port']
        assert isinstance(api_server_test._hypercorn_config, HyperCornConfig) is True
        assert api_server_test._new_bind == f'0.0.0.0:{api_server_test._port}'
        assert isinstance(api_server_test._app, Quart) is True
        assert api_server_test._app.title == api_server_test._title

    @pytest.mark.asyncio
    async def run_server_test(self):
        logger = Mock()
        redis_client = Mock()
        event_bus = Mock()
        api_server_test = DispatchServer(config, redis_client, event_bus, logger)
        with patch.object(application.server.api_server, 'serve', new=CoroutineMock()) \
                as mock_serve:
            await api_server_test.run_server()
            assert api_server_test._hypercorn_config.bind == [api_server_test._new_bind]
            assert mock_serve.called

    @pytest.mark.asyncio
    async def ok_app_test(self):
        logger = Mock()
        redis_client = Mock()
        event_bus = Mock()
        api_server_test = DispatchServer(config, redis_client, event_bus, logger)
        client = api_server_test._app.test_client()
        response = await client.get('/_health')
        data = await response.get_json()
        assert response.status_code == 200
        assert data is None

    def attach_swagger_test(self):
        logger = Mock()
        redis_client = Mock()
        event_bus = Mock()
        api_server_test = DispatchServer(config, redis_client, event_bus, logger)
        with patch.object(api_server_module, 'quart_api_doc', new=CoroutineMock()) as quart_api_doc_mock:
            api_server_test.attach_swagger()
            quart_api_doc_mock.assert_called_once()

    def set_status_test(self):
        logger = Mock()
        redis_client = Mock()
        event_bus = Mock()
        api_server_test = DispatchServer(config, redis_client, event_bus, logger)
        assert api_server_test._status == HTTPStatus.OK
        api_server_test.set_status(HTTPStatus.INTERNAL_SERVER_ERROR)
        assert api_server_test._status == HTTPStatus.INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def get_dispatch_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response_lit = {
            "request_id": uuid_,
            "body": {
                "Status": "Success",
                "Message": None,
                "Dispatch": {
                    "turn_up": None,
                    "Time_Zone_Local": "Pacific Time",
                    "Time_of_Check_Out": None,
                    "Time_of_Check_In": None,
                    "Tech_Off_Site": False,
                    "Tech_Mobile_Number": None,
                    "Tech_First_Name": None,
                    "Tech_Arrived_On_Site": False,
                    "Special_Materials_Needed_for_Dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
                    "Special_Dispatch_Notes": None,
                    "Site_Survey_Quote_Required": False,
                    "Scope_of_Work": "Device is bouncing constantly",
                    "Name_of_MetTel_Requester": "Karen Doe",
                    "MetTel_Tech_Call_In_Instructions":
                        "When arriving to the site call HOLMDEL NOC for telematic assistance",
                    "MetTel_Requester_Email": "karen.doe@mettel.net",
                    "MetTel_Note_Updates": None,
                    "MetTel_Group_Email": None,
                    "MetTel_Department_Phone_Number": None,
                    "MetTel_Department": "Customer Care",
                    "MetTel_Bruin_TicketID": "T-12345",
                    "Local_Time_of_Dispatch": None,
                    "Job_Site_Zip_Code": "99088",
                    "Job_Site_Street": "123 Fake Street",
                    "Job_Site_State": "CA",
                    "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                    "Job_Site_City": "Pleasantown",
                    "Job_Site": "test street",
                    "Information_for_Tech": None,
                    "Hard_Time_of_Dispatch_Time_Zone_Local": None,
                    "Hard_Time_of_Dispatch_Local": None,
                    "Dispatch_Status": "New Dispatch",
                    "Dispatch_Number": "DIS37450",
                    "Date_of_Dispatch": "2019-11-14",
                    "Close_Out_Notes": None,
                    "Backup_MetTel_Department_Phone_Number": None,
                    "dispatch_status": "New Dispatch"
                },
                "APIRequestID": "a130v000001U6iTAAS"
            },
            "status": 200
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        expected_response = {
            "id": "DIS37450",
            "vendor": "lit",
            "dispatch": {
                "dispatch_number": "DIS37450",
                "date_of_dispatch": "2019-11-14",
                "site_survey_quote_required": False,
                "time_of_dispatch": None,
                "time_zone": "Pacific Time",
                "mettel_bruin_ticket_id": "T-12345",
                "job_site": "test street",
                "job_site_street": "123 Fake Street",
                "job_site_city": "Pleasantown",
                "job_site_state": "CA",
                "job_site_zip_code": "99088",
                "job_site_contact_name": "Jane Doe",
                "job_site_contact_number": "+1 666 6666 666",
                "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
                "scope_of_work": "Device is bouncing constantly",
                "mettel_tech_call_in_instructions":
                    "When arriving to the site call HOLMDEL NOC for telematic assistance",
                "name_of_mettel_requester": "Karen Doe",
                "mettel_department": "Customer Care",
                "mettel_requester_email": "karen.doe@mettel.net",
                "dispatch_status": "New Dispatch"
            }
        }

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch/{dispatch_number}')
            data = await response.get_json()
            event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", payload, timeout=30)

            # response = await api_server_test.get_dispatch('DIS37450')
            assert response.status_code == HTTPStatus.OK
            assert data == expected_response

    @pytest.mark.asyncio
    async def get_dispatch_not_found_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS_NOT_EXISTS'
        expected_response_lit = {
            "request_id": uuid_,
            "body": {
                "Status": "error",
                "Message": "List has no rows for assignment to SObject",
                "Dispatch": None,
                "APIRequestID": "a130v000001UG7sAAG"
            },
            "status": 400
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        expected_response = {
            "code": 400,
            "message": {
                "Status": "error",
                "Message": "List has no rows for assignment to SObject",
                "Dispatch": None,
                "APIRequestID": "a130v000001UG7sAAG"
            }
        }

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch/{dispatch_number}')
            data = await response.get_json()
            event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", payload, timeout=30)

            # response = await api_server_test.get_dispatch('DIS37450')
            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response
            assert data['code'] == HTTPStatus.BAD_REQUEST

    @pytest.mark.asyncio
    async def get_dispatch_error_from_lit_500_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS_NOT_EXISTS'
        expected_response_lit = {
            "request_id": uuid_,
            "body": [
                {
                    "errorCode": "APEX_ERROR",
                    "message": ""
                }
            ],
            "status": HTTPStatus.INTERNAL_SERVER_ERROR
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        expected_response = {'code': 500, 'message': [{'errorCode': 'APEX_ERROR', 'message': ''}]}

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch/{dispatch_number}')
            data = await response.get_json()
            event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", payload, timeout=30)

            # response = await api_server_test.get_dispatch('DIS37450')
            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            assert data == expected_response
            assert data['code'] == HTTPStatus.INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def get_all_dispatch_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        expected_response_lit = {
            "request_id": uuid_,
            "body": {
                "Status": "Success",
                "Message": "Total Number of Dispatches: 236",
                "DispatchList": [
                    {
                        "turn_up": None,
                        "Time_Zone_Local": "Pacific Time",
                        "Time_of_Check_Out": None,
                        "Time_of_Check_In": None,
                        "Tech_Off_Site": False,
                        "Tech_Mobile_Number": None,
                        "Tech_First_Name": None,
                        "Tech_Arrived_On_Site": False,
                        "Special_Materials_Needed_for_Dispatch": "Special_Materials_Needed_for_Dispatch",
                        "Special_Dispatch_Notes": None,
                        "Site_Survey_Quote_Required": True,
                        "Scope_of_Work": "Device is bouncing constantly",
                        "Name_of_MetTel_Requester": "Karen Doe",
                        "MetTel_Tech_Call_In_Instructions": 'MetTel_Tech_Call_In_Instructions',
                        "MetTel_Requester_Email": "karen.doe@mettel.net",
                        "MetTel_Note_Updates": None,
                        "MetTel_Group_Email": "activations@mettel.net",
                        "MetTel_Department_Phone_Number": "(111) 111-1111",
                        "MetTel_Department": "1",
                        "MetTel_Bruin_TicketID": "T-12345",
                        "Local_Time_of_Dispatch": None,
                        "Job_Site_Zip_Code": "99088",
                        "Job_Site_Street": "123 Fake Street",
                        "Job_Site_State": "CA",
                        "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                        "Job_Site_City": "Pleasantown",
                        "Job_Site": "test site",
                        "Information_for_Tech": None,
                        "Hard_Time_of_Dispatch_Time_Zone_Local": None,
                        "Hard_Time_of_Dispatch_Local": "2:00pm",
                        "Dispatch_Status": "New Dispatch",
                        "Dispatch_Number": "DIS37263",
                        "Date_of_Dispatch": "2019-11-14",
                        "Close_Out_Notes": None,
                        "Backup_MetTel_Department_Phone_Number": "(111) 111-1111"
                    },
                    {
                        "turn_up": None,
                        "Time_Zone_Local": "Pacific Time",
                        "Time_of_Check_Out": None,
                        "Time_of_Check_In": None,
                        "Tech_Off_Site": False,
                        "Tech_Mobile_Number": None,
                        "Tech_First_Name": None,
                        "Tech_Arrived_On_Site": False,
                        "Special_Materials_Needed_for_Dispatch": "Special_Materials_Needed_for_Dispatch",
                        "Special_Dispatch_Notes": None,
                        "Site_Survey_Quote_Required": False,
                        "Scope_of_Work": "Device is bouncing constantly",
                        "Name_of_MetTel_Requester": "Karen Doe",
                        "MetTel_Tech_Call_In_Instructions": "MetTel_Tech_Call_In_Instructions",
                        "MetTel_Requester_Email": "karen.doe@mettel.net",
                        "MetTel_Note_Updates": None,
                        "MetTel_Group_Email": "activations@mettel.net",
                        "MetTel_Department_Phone_Number": "(111) 111-1111",
                        "MetTel_Department": "1",
                        "MetTel_Bruin_TicketID": "T-12345",
                        "Local_Time_of_Dispatch": None,
                        "Job_Site_Zip_Code": "99088",
                        "Job_Site_Street": "123 Fake Street",
                        "Job_Site_State": "CA",
                        "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                        "Job_Site_City": "Pleasantown",
                        "Job_Site": "test site",
                        "Information_for_Tech": None,
                        "Hard_Time_of_Dispatch_Time_Zone_Local": None,
                        "Hard_Time_of_Dispatch_Local": "2:00pm",
                        "Dispatch_Status": "Request Confirmed",
                        "Dispatch_Number": "DIS37264",
                        "Date_of_Dispatch": "2019-11-14",
                        "Close_Out_Notes": None,
                        "Backup_MetTel_Department_Phone_Number": "(111) 111-1111"
                    }
                ]
            },
            "status": 200
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        expected_response = {
            "vendor": "LIT",
            "list_dispatch": [
                {
                    "dispatch_number": "DIS37263",
                    "date_of_dispatch": "2019-11-14",
                    "site_survey_quote_required": True,
                    "time_of_dispatch": None,
                    "time_zone": "Pacific Time",
                    "mettel_bruin_ticket_id": "T-12345",
                    "job_site": "test site",
                    "job_site_street": "123 Fake Street",
                    "job_site_city": "Pleasantown",
                    "job_site_state": "CA",
                    "job_site_zip_code": "99088",
                    "job_site_contact_name": "Jane Doe",
                    "job_site_contact_number": "+1 666 6666 666",
                    "materials_needed_for_dispatch": "Special_Materials_Needed_for_Dispatch",
                    "scope_of_work": "Device is bouncing constantly",
                    "mettel_tech_call_in_instructions": "MetTel_Tech_Call_In_Instructions",
                    "name_of_mettel_requester": "Karen Doe",
                    "mettel_department": "1",
                    "mettel_requester_email": "karen.doe@mettel.net",
                    "dispatch_status": "New Dispatch"
                },
                {
                    "dispatch_number": "DIS37264",
                    "date_of_dispatch": "2019-11-14",
                    "site_survey_quote_required": False,
                    "time_of_dispatch": None,
                    "time_zone": "Pacific Time",
                    "mettel_bruin_ticket_id": "T-12345",
                    "job_site": "test site",
                    "job_site_street": "123 Fake Street",
                    "job_site_city": "Pleasantown",
                    "job_site_state": "CA",
                    "job_site_zip_code": "99088",
                    "job_site_contact_name": "Jane Doe",
                    "job_site_contact_number": "+1 666 6666 666",
                    "materials_needed_for_dispatch": "Special_Materials_Needed_for_Dispatch",
                    "scope_of_work": "Device is bouncing constantly",
                    "mettel_tech_call_in_instructions": "MetTel_Tech_Call_In_Instructions",
                    "name_of_mettel_requester": "Karen Doe",
                    "mettel_department": "1",
                    "mettel_requester_email": "karen.doe@mettel.net",
                    "dispatch_status": "Request Confirmed"
                }
            ]
        }

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload = {"request_id": uuid_, "body": {}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch/')
            data = await response.get_json()
            event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", payload, timeout=30)

            assert response.status_code == HTTPStatus.OK
            assert data == expected_response

    @pytest.mark.asyncio
    async def get_all_dispatch_error_500_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        expected_response_lit = {
            "request_id": uuid_,
            "body": [
                {
                    "errorCode": "APEX_ERROR",
                    "message": ""
                }
            ],
            "status": HTTPStatus.INTERNAL_SERVER_ERROR
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload = {"request_id": uuid_, "body": {}}

        expected_response_get_all_dispatches_error = {
            'code': 500, 'message': [{'errorCode': 'APEX_ERROR', 'message': ''}]
        }

        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch', json=payload)

            data = await response.get_json()
            event_bus.rpc_request.assert_awaited_once()

            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            assert data == expected_response_get_all_dispatches_error

    @pytest.mark.asyncio
    async def get_all_dispatch_error_400_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        expected_response_lit = {
            "request_id": uuid_,
            "body": [
                {
                    "errorCode": "APEX_ERROR",
                    "message": ""
                }
            ],
            "status": 400
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload = {"request_id": uuid_, "body": {}}

        expected_response_get_all_dispatches_error = {
            'code': 400, 'message': [{'errorCode': 'APEX_ERROR', 'message': ''}]
        }

        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch', json=payload)

            data = await response.get_json()
            event_bus.rpc_request.assert_awaited_once()

            assert response.status_code == 400
            assert data == expected_response_get_all_dispatches_error

    @pytest.mark.asyncio
    async def get_all_dispatch_error_in_response_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        expected_response_lit = {
            "request_id": uuid_,
            "body": {},
            "status": 200
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload = {"request_id": uuid_, "body": {}}

        expected_response_get_all_dispatches_error = {
            'code': 200, 'message': {}
        }

        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch', json=payload)

            data = await response.get_json()
            event_bus.rpc_request.assert_awaited_once()

            assert response.status_code == 200
            assert data == expected_response_get_all_dispatches_error

    @pytest.mark.asyncio
    async def lit_create_dispatch_with_note_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "Success",
            "Message": None,
            "Dispatch": {
                "turn_up": None,
                "Time_Zone_Local": "Pacific Time",
                "Time_of_Check_Out": None,
                "Time_of_Check_In": None,
                "Tech_Off_Site": False,
                "Tech_Mobile_Number": None,
                "Tech_First_Name": None,
                "Tech_Arrived_On_Site": False,
                "Special_Materials_Needed_for_Dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
                "Special_Dispatch_Notes": None,
                "Site_Survey_Quote_Required": False,
                "Scope_of_Work": "Device is bouncing constantly",
                "Name_of_MetTel_Requester": "Karen Doe",
                "MetTel_Tech_Call_In_Instructions":
                    "When arriving to the site call HOLMDEL NOC for telematic assistance",
                "MetTel_Requester_Email": "karen.doe@mettel.net",
                "MetTel_Note_Updates": None,
                "MetTel_Group_Email": None,
                "MetTel_Department_Phone_Number": None,
                "MetTel_Department": "Customer Care",
                "MetTel_Bruin_TicketID": None,
                "Local_Time_of_Dispatch": None,
                "Job_Site_Zip_Code": "99088",
                "Job_Site_Street": "123 Fake Street",
                "Job_Site_State": "CA",
                "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                "Job_Site_City": "Pleasantown",
                "Job_Site": "test street",
                "Information_for_Tech": None,
                "Hard_Time_of_Dispatch_Time_Zone_Local": None,
                "Hard_Time_of_Dispatch_Local": None,
                "Dispatch_Status": "New Dispatch",
                "Dispatch_Number": "DIS37450",
                "Date_of_Dispatch": "2019-11-14",
                "Close_Out_Notes": None,
                "Backup_MetTel_Department_Phone_Number": None
            },
            "APIRequestID": "a130v000001U6iTAAS"
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 200
        }

        expected_response_bruin = {
            "request_id": uuid_,
            "body": {},
            "status": 200
        }

        expected_response_bruin_append_note = {
            "request_id": uuid_,
            "body": {},
            "status": 200
        }

        event_bus = Mock()
        # event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        event_bus.rpc_request = CoroutineMock(side_effect=[
            expected_response_lit,
            expected_response_bruin,
            expected_response_bruin_append_note
        ])

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload_lit = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "time_of_dispatch": "6PM-8PM",
            "time_zone": "Pacific Time",
            "mettel_bruin_ticket_id": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name": "Jane Doe",
            "job_site_contact_number": "+1 666 6666 666",
            "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "mettel_department_phone_number"
        }

        payload_lit_mapped = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "local_time_of_dispatch": "6PM-8PM",
            "time_zone_local": "Pacific Time",
            "mettel_bruin_ticketid": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name_and_phone_number": "Jane Doe +1 666 6666 666",
            "special_materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "mettel_department_phone_number"
        }

        payload_request = {
            "request_id": uuid_,
            "body": {
                'RequestDispatch': payload_lit_mapped
            }
        }

        expected_response_create = {'id': 'DIS37450', 'vendor': 'LIT'}

        ticket_note = '#*Automation Engine*#\nDispatch Management - Dispatch Requested\n\n' \
                      'A dispatch has been requested with LIT. Please see the summary below.\n' \
                      '--\nDate of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n' \
                      'Time Zone (Local): Pacific Time\n' \
                      'Vendor: LIT\n\nLocation Owner/Name: Red Rose Inn\n' \
                      'Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n' \
                      'Phone: +1 666 6666 666\n\nIssues Experienced:\nDevice is bouncing constantly\n' \
                      'Arrival Instructions: When arriving to the site call ' \
                      'HOLMDEL NOC for telematic assistance\nMaterials Needed:\n' \
                      'Laptop, cable, tuner, ladder,internet hotspot\n\nRequester\n' \
                      'Name: Karen Doe\nPhone: mettel_department_phone_number\n' \
                      'Email: karen.doe@mettel.net\nDepartment: Customer Care'

        append_note_to_ticket_request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': 'T-12345',
                'note': '#*Automation Engine*#\nDispatch Management - Dispatch Requested\n\n'
                        'A dispatch has been requested with LIT. Please see the summary below.\n--\n'
                        f'Dispatch Number: [{dispatch_number}|'
                        f'https://master.mettel-automation.net/dispatch_portal/dispatch/{dispatch_number}]\n'
                        'Date of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n'
                        'Time Zone (Local): Pacific Time\nVendor: LIT\n\nLocation Owner/Name: Red Rose Inn\n'
                        'Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n'
                        'Phone: +1 666 6666 666\n\nIssues Experienced:\nDevice is bouncing constantly\n'
                        'Arrival Instructions: When arriving to the site call HOLMDEL NOC for telematic assistance\n'
                        'Materials Needed:\nLaptop, cable, tuner, ladder,internet hotspot\n\n'
                        'Requester\nName: Karen Doe\nPhone: mettel_department_phone_number\n'
                        'Email: karen.doe@mettel.net\nDepartment: Customer Care'
            },
        }

        payload_ticket_request_msg = {
            'request_id': uuid_,
            'body': {
                'ticket_id': 'T-12345'
            }
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.post(f'/lit/dispatch', json=payload_lit)

            data = await response.get_json()

            event_bus.rpc_request.assert_has_awaits([
                call("lit.dispatch.post", payload_request, timeout=30),
                call("bruin.ticket.details.request", payload_ticket_request_msg, timeout=200),
                call("bruin.ticket.note.append.request", append_note_to_ticket_request, timeout=15)
            ])

            assert response.status_code == HTTPStatus.OK
            assert data == expected_response_create

    @pytest.mark.asyncio
    async def lit_create_dispatch_with_error_appending_note_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "Success",
            "Message": None,
            "Dispatch": {
                "turn_up": None,
                "Time_Zone_Local": "Pacific Time",
                "Time_of_Check_Out": None,
                "Time_of_Check_In": None,
                "Tech_Off_Site": False,
                "Tech_Mobile_Number": None,
                "Tech_First_Name": None,
                "Tech_Arrived_On_Site": False,
                "Special_Materials_Needed_for_Dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
                "Special_Dispatch_Notes": None,
                "Site_Survey_Quote_Required": False,
                "Scope_of_Work": "Device is bouncing constantly",
                "Name_of_MetTel_Requester": "Karen Doe",
                "MetTel_Tech_Call_In_Instructions":
                    "When arriving to the site call HOLMDEL NOC for telematic assistance",
                "MetTel_Requester_Email": "karen.doe@mettel.net",
                "MetTel_Note_Updates": None,
                "MetTel_Group_Email": None,
                "MetTel_Department_Phone_Number": None,
                "MetTel_Department": "Customer Care",
                "MetTel_Bruin_TicketID": None,
                "Local_Time_of_Dispatch": None,
                "Job_Site_Zip_Code": "99088",
                "Job_Site_Street": "123 Fake Street",
                "Job_Site_State": "CA",
                "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                "Job_Site_City": "Pleasantown",
                "Job_Site": "test street",
                "Information_for_Tech": None,
                "Hard_Time_of_Dispatch_Time_Zone_Local": None,
                "Hard_Time_of_Dispatch_Local": None,
                "Dispatch_Status": "New Dispatch",
                "Dispatch_Number": dispatch_number,
                "Date_of_Dispatch": "2019-11-14",
                "Close_Out_Notes": None,
                "Backup_MetTel_Department_Phone_Number": None
            },
            "APIRequestID": "a130v000001U6iTAAS"
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 200
        }

        expected_response_bruin = {
            "request_id": uuid_,
            "body": {},
            "status": 200
        }

        expected_response_bruin_append_note = {
            "request_id": uuid_,
            "body": {},
            "status": 404
        }

        event_bus = Mock()
        # event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        event_bus.rpc_request = CoroutineMock(side_effect=[
            expected_response_lit,
            expected_response_bruin,
            expected_response_bruin_append_note
        ])

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload_lit = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "time_of_dispatch": "6PM-8PM",
            "time_zone": "Pacific Time",
            "mettel_bruin_ticket_id": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name": "Jane Doe",
            "job_site_contact_number": "+1 666 6666 666",
            "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "mettel_department_phone_number"
        }

        payload_lit_mapped = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "local_time_of_dispatch": "6PM-8PM",
            "time_zone_local": "Pacific Time",
            "mettel_bruin_ticketid": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name_and_phone_number": "Jane Doe +1 666 6666 666",
            "special_materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "mettel_department_phone_number"
        }

        payload_request = {
            "request_id": uuid_,
            "body": {
                'RequestDispatch': payload_lit_mapped
            }
        }

        expected_response_create = {'id': dispatch_number, 'vendor': 'LIT'}

        append_note_to_ticket_request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': 'T-12345',
                'note': '#*Automation Engine*#\nDispatch Management - Dispatch Requested\n\n'
                        'A dispatch has been requested with LIT. Please see the summary below.\n'
                        f'--\nDispatch Number: '
                        f'[{dispatch_number}|'
                        f'https://master.mettel-automation.net/dispatch_portal/dispatch/{dispatch_number}]\n'
                        'Date of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n'
                        'Time Zone (Local): Pacific Time\nVendor: LIT\n\nLocation Owner/Name: Red Rose Inn\n'
                        'Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n'
                        'Phone: +1 666 6666 666\n\nIssues Experienced:\nDevice is bouncing constantly\n'
                        'Arrival Instructions: When arriving to the site call HOLMDEL NOC for telematic assistance\n'
                        'Materials Needed:\nLaptop, cable, tuner, ladder,internet hotspot\n\n'
                        'Requester\nName: Karen Doe\nPhone: mettel_department_phone_number\n'
                        'Email: karen.doe@mettel.net\nDepartment: Customer Care'
            },
        }

        payload_ticket_request_msg = {
            'request_id': uuid_,
            'body': {
                'ticket_id': 'T-12345'
            }
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.post(f'/lit/dispatch', json=payload_lit)

            data = await response.get_json()

            event_bus.rpc_request.assert_has_awaits([
                call("lit.dispatch.post", payload_request, timeout=30),
                call("bruin.ticket.details.request", payload_ticket_request_msg, timeout=200),
                call("bruin.ticket.note.append.request", append_note_to_ticket_request, timeout=15)
            ])

            assert response.status_code == HTTPStatus.OK
            assert data == expected_response_create

    @pytest.mark.asyncio
    async def lit_create_dispatch_note_already_exists_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "Success",
            "Message": None,
            "Dispatch": {
                "turn_up": None,
                "Time_Zone_Local": "Pacific Time",
                "Time_of_Check_Out": None,
                "Time_of_Check_In": None,
                "Tech_Off_Site": False,
                "Tech_Mobile_Number": None,
                "Tech_First_Name": None,
                "Tech_Arrived_On_Site": False,
                "Special_Materials_Needed_for_Dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
                "Special_Dispatch_Notes": None,
                "Site_Survey_Quote_Required": False,
                "Scope_of_Work": "Device is bouncing constantly",
                "Name_of_MetTel_Requester": "Karen Doe",
                "MetTel_Tech_Call_In_Instructions":
                    "When arriving to the site call HOLMDEL NOC for telematic assistance",
                "MetTel_Requester_Email": "karen.doe@mettel.net",
                "MetTel_Note_Updates": None,
                "MetTel_Group_Email": None,
                "MetTel_Department_Phone_Number": None,
                "MetTel_Department": "Customer Care",
                "MetTel_Bruin_TicketID": None,
                "Local_Time_of_Dispatch": None,
                "Job_Site_Zip_Code": "99088",
                "Job_Site_Street": "123 Fake Street",
                "Job_Site_State": "CA",
                "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                "Job_Site_City": "Pleasantown",
                "Job_Site": "test street",
                "Information_for_Tech": None,
                "Hard_Time_of_Dispatch_Time_Zone_Local": None,
                "Hard_Time_of_Dispatch_Local": None,
                "Dispatch_Status": "New Dispatch",
                "Dispatch_Number": dispatch_number,
                "Date_of_Dispatch": "2019-11-14",
                "Close_Out_Notes": None,
                "Backup_MetTel_Department_Phone_Number": None
            },
            "APIRequestID": "a130v000001U6iTAAS"
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 200
        }

        expected_response_bruin = {
            "request_id": uuid_,
            "body": [{'noteValue': '#*Automation Engine*#\nDispatch Management - Dispatch Requested\n\n'
                      'A dispatch has been requested with LIT. Please see the summary below.\n'
                      f'--\nDispatch Number: '
                      f'[{dispatch_number}|https://master.mettel-automation.net/dispatch_portal/dispatch/DIS37266]\n'
                      'Date of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n'
                      'Time Zone (Local): Pacific Time\n'
                      'Vendor: LIT\n\nLocation Owner/Name: Red Rose Inn\n'
                      'Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n'
                      'Phone: +1 666 6666 666\n\nIssues Experienced:\nDevice is bouncing constantly\n'
                      'Arrival Instructions: When arriving to the site call '
                      'HOLMDEL NOC for telematic assistance\nMaterials Needed:\n'
                      'Laptop, cable, tuner, ladder,internet hotspot\n\nRequester\n'
                      'Name: Karen Doe\nPhone: mettel_department_phone_number\n'
                      'Email: karen.doe@mettel.net\nDepartment: Customer Care'}],
            "status": 200
        }

        event_bus = Mock()

        event_bus.rpc_request = CoroutineMock(side_effect=[
            expected_response_lit,
            expected_response_bruin
        ])

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload_lit = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "time_of_dispatch": "6PM-8PM",
            "time_zone": "Pacific Time",
            "mettel_bruin_ticket_id": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name": "Jane Doe",
            "job_site_contact_number": "+1 666 6666 666",
            "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "mettel_department_phone_number"
        }

        payload_lit_mapped = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "local_time_of_dispatch": "6PM-8PM",
            "time_zone_local": "Pacific Time",
            "mettel_bruin_ticketid": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name_and_phone_number": "Jane Doe +1 666 6666 666",
            "special_materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "mettel_department_phone_number"
        }

        payload_request = {
            "request_id": uuid_,
            "body": {
                'RequestDispatch': payload_lit_mapped
            }
        }

        expected_response_create = {'id': 'DIS37450', 'vendor': 'LIT'}

        ticket_note = '#*Automation Engine*#\nDispatch Management - Dispatch Requested\n\n' \
                      'A dispatch has been requested with LIT. Please see the summary below.\n' \
                      '--\nDate of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n' \
                      'Time Zone (Local): Pacific Time\n' \
                      'Vendor: LIT\n\nLocation Owner/Name: Red Rose Inn\n' \
                      'Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n' \
                      'Phone: +1 666 6666 666\n\nIssues Experienced:\nDevice is bouncing constantly\n' \
                      'Arrival Instructions: When arriving to the site call ' \
                      'HOLMDEL NOC for telematic assistance\nMaterials Needed:\n' \
                      'Laptop, cable, tuner, ladder,internet hotspot\n\nRequester\n' \
                      'Name: Karen Doe\nPhone: mettel_department_phone_number\n' \
                      'Email: karen.doe@mettel.net\nDepartment: Customer Care'

        append_note_to_ticket_request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': 'T-12345',
                'note': '#*Automation Engine*#\nDispatch Management - Dispatch Requested\n\n'
                        'A dispatch has been requested with LIT. Please see the summary below.\n--\n'
                        'Date of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n'
                        'Time Zone (Local): Pacific Time\nVendor: LIT\n\nLocation Owner/Name: Red Rose Inn\n'
                        'Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n'
                        'Phone: +1 666 6666 666\n\nIssues Experienced:\nDevice is bouncing constantly\n'
                        'Arrival Instructions: When arriving to the site call HOLMDEL NOC for telematic assistance\n'
                        'Materials Needed:\nLaptop, cable, tuner, ladder,internet hotspot\n\n'
                        'Requester\nName: Karen Doe\nPhone: mettel_department_phone_number\n'
                        'Email: karen.doe@mettel.net\nDepartment: Customer Care'
            },
        }

        payload_ticket_request_msg = {
            'request_id': uuid_,
            'body': {
                'ticket_id': 'T-12345'
            }
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.post(f'/lit/dispatch', json=payload_lit)

            data = await response.get_json()

            event_bus.rpc_request.assert_has_awaits([
                call("lit.dispatch.post", payload_request, timeout=30),
                call("bruin.ticket.details.request", payload_ticket_request_msg, timeout=200)
            ])

            assert response.status_code == HTTPStatus.OK
            assert data == expected_response_create

    @pytest.mark.asyncio
    async def lit_create_dispatch_error_getting_ticket_details_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "Success",
            "Message": None,
            "Dispatch": {
                "turn_up": None,
                "Time_Zone_Local": "Pacific Time",
                "Time_of_Check_Out": None,
                "Time_of_Check_In": None,
                "Tech_Off_Site": False,
                "Tech_Mobile_Number": None,
                "Tech_First_Name": None,
                "Tech_Arrived_On_Site": False,
                "Special_Materials_Needed_for_Dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
                "Special_Dispatch_Notes": None,
                "Site_Survey_Quote_Required": False,
                "Scope_of_Work": "Device is bouncing constantly",
                "Name_of_MetTel_Requester": "Karen Doe",
                "MetTel_Tech_Call_In_Instructions":
                    "When arriving to the site call HOLMDEL NOC for telematic assistance",
                "MetTel_Requester_Email": "karen.doe@mettel.net",
                "MetTel_Note_Updates": None,
                "MetTel_Group_Email": None,
                "MetTel_Department_Phone_Number": None,
                "MetTel_Department": "Customer Care",
                "MetTel_Bruin_TicketID": None,
                "Local_Time_of_Dispatch": None,
                "Job_Site_Zip_Code": "99088",
                "Job_Site_Street": "123 Fake Street",
                "Job_Site_State": "CA",
                "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                "Job_Site_City": "Pleasantown",
                "Job_Site": "test street",
                "Information_for_Tech": None,
                "Hard_Time_of_Dispatch_Time_Zone_Local": None,
                "Hard_Time_of_Dispatch_Local": None,
                "Dispatch_Status": "New Dispatch",
                "Dispatch_Number": "DIS37450",
                "Date_of_Dispatch": "2019-11-14",
                "Close_Out_Notes": None,
                "Backup_MetTel_Department_Phone_Number": None
            },
            "APIRequestID": "a130v000001U6iTAAS"
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 200
        }

        expected_response_bruin = {
            "request_id": uuid_,
            "body": None,
            "status": 404
        }

        event_bus = Mock()
        # event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        event_bus.rpc_request = CoroutineMock(side_effect=[
            expected_response_lit,
            expected_response_bruin
        ])

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload_lit = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "time_of_dispatch": "6PM-8PM",
            "time_zone": "Pacific Time",
            "mettel_bruin_ticket_id": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name": "Jane Doe",
            "job_site_contact_number": "+1 666 6666 666",
            "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "mettel_department_phone_number"
        }

        payload_lit_mapped = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "local_time_of_dispatch": "6PM-8PM",
            "time_zone_local": "Pacific Time",
            "mettel_bruin_ticketid": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name_and_phone_number": "Jane Doe +1 666 6666 666",
            "special_materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "mettel_department_phone_number"
        }

        payload_request = {
            "request_id": uuid_,
            "body": {
                'RequestDispatch': payload_lit_mapped
            }
        }

        expected_response_create = {'id': 'DIS37450', 'vendor': 'LIT'}

        ticket_note = '#*Automation Engine*#\nDispatch Management - Dispatch Requested\n\n' \
                      'A dispatch has been requested with LIT. Please see the summary below.\n' \
                      '--\nDate of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n' \
                      'Time Zone (Local): Pacific Time\n' \
                      'Vendor: LIT\n\nLocation Owner/Name: Red Rose Inn\n' \
                      'Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n' \
                      'Phone: +1 666 6666 666\n\nIssues Experienced:\nDevice is bouncing constantly\n' \
                      'Arrival Instructions: When arriving to the site call ' \
                      'HOLMDEL NOC for telematic assistance\nMaterials Needed:\n' \
                      'Laptop, cable, tuner, ladder,internet hotspot\n\nRequester\n' \
                      'Name: Karen Doe\nPhone: mettel_department_phone_number\n' \
                      'Email: karen.doe@mettel.net\nDepartment: Customer Care'

        payload_ticket_request_msg = {
            'request_id': uuid_,
            'body': {
                'ticket_id': 'T-12345'
            }
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.post(f'/lit/dispatch', json=payload_lit)

            data = await response.get_json()

            event_bus.rpc_request.assert_has_awaits([
                call("lit.dispatch.post", payload_request, timeout=30),
                call("bruin.ticket.details.request", payload_ticket_request_msg, timeout=200)
            ])

            assert response.status_code == HTTPStatus.OK
            assert data == expected_response_create

    def exists_watermark_in_ticket_is_true_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()
        watermark = 'Dispatch Management - Dispatch Requested'
        ticket_notes = [
            {
                'noteValue':
                    '#*Automation Engine*#\nDispatch Management - Dispatch Requested\n\n'
                    'A dispatch has been requested with LIT. Please see the summary below.\n'
                    '--\nDate of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n'
                    'Time Zone (Local): Pacific Time\n'
                    'Vendor: LIT\n\nLocation Owner/Name: Red Rose Inn\n'
                    'Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n'
                    'Phone: +1 666 6666 666\n\nIssues Experienced:\nDevice is bouncing constantly\n'
                    'Arrival Instructions: When arriving to the site call '
                    'HOLMDEL NOC for telematic assistance\nMaterials Needed:\n'
                    'Laptop, cable, tuner, ladder,internet hotspot\n\nRequester\n'
                    'Name: Karen Doe\nPhone: mettel_department_phone_number\n'
                    'Email: karen.doe@mettel.net\nDepartment: Customer Care'
            }, {
                'noteValue': 'whatever'
            }
        ]
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)
        response = api_server_test._exists_watermark_in_ticket(watermark, ticket_notes)
        assert response is True

    @pytest.mark.asyncio
    async def create_dispatch_validation_error_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "Success",
            "Message": None,
            "Dispatch": {
                "turn_up": None,
                "Time_Zone_Local": "Pacific Time",
                "Time_of_Check_Out": None,
                "Time_of_Check_In": None,
                "Tech_Off_Site": False,
                "Tech_Mobile_Number": None,
                "Tech_First_Name": None,
                "Tech_Arrived_On_Site": False,
                "Special_Materials_Needed_for_Dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
                "Special_Dispatch_Notes": None,
                "Site_Survey_Quote_Required": False,
                "Scope_of_Work": "Device is bouncing constantly",
                "Name_of_MetTel_Requester": "Karen Doe",
                "MetTel_Tech_Call_In_Instructions":
                    "When arriving to the site call HOLMDEL NOC for telematic assistance",
                "MetTel_Requester_Email": "karen.doe@mettel.net",
                "MetTel_Note_Updates": None,
                "MetTel_Group_Email": None,
                "MetTel_Department_Phone_Number": None,
                "MetTel_Department": "Customer Care",
                "MetTel_Bruin_TicketID": None,
                "Local_Time_of_Dispatch": None,
                "Job_Site_Zip_Code": "99088",
                "Job_Site_Street": "123 Fake Street",
                "Job_Site_State": "CA",
                "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                "Job_Site_City": "Pleasantown",
                "Job_Site": "test street",
                "Information_for_Tech": None,
                "Hard_Time_of_Dispatch_Time_Zone_Local": None,
                "Hard_Time_of_Dispatch_Local": None,
                "Dispatch_Status": "New Dispatch",
                "Dispatch_Number": "DIS37450",
                "Date_of_Dispatch": "2019-11-14",
                "Close_Out_Notes": None,
                "Backup_MetTel_Department_Phone_Number": None
            },
            "APIRequestID": "a130v000001U6iTAAS"
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 200
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload_lit = {
            "BAD_FIELD": "2019-11-14",
            "site_survey_quote_required": False,
            "time_of_dispatch": "6PM-8PM",
            "time_zone": "Pacific Time",
            "mettel_bruin_ticket_id": 123,
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name": "Jane Doe",
            "job_site_contact_number": "+1 666 6666 666",
            "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "mettel_department_phone_number"
        }

        payload_lit_mapped = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "local_time_of_dispatch": "6PM-8PM",
            "time_zone_local": "Pacific Time",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name_and_phone_number": "Jane Doe +1 666 6666 666",
            "special_materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "mettel_department_phone_number"
        }

        payload_request = {
            "request_id": uuid_,
            "body": {
                'RequestDispatch': payload_lit_mapped
            }
        }

        expected_response_create_error = {
            'code': 400,
            'message': "'date_of_dispatch' is a required property"
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.post(f'/lit/dispatch', json=payload_lit)

            data = await response.get_json()
            event_bus.rpc_request.assert_not_awaited()

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_create_error

    @pytest.mark.asyncio
    async def create_dispatch_error_from_lit_500_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "Success",
            "Message": None,
            "Dispatch": {
                "turn_up": None,
                "Time_Zone_Local": "Pacific Time",
                "Time_of_Check_Out": None,
                "Time_of_Check_In": None,
                "Tech_Off_Site": False,
                "Tech_Mobile_Number": None,
                "Tech_First_Name": None,
                "Tech_Arrived_On_Site": False,
                "Special_Materials_Needed_for_Dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
                "Special_Dispatch_Notes": None,
                "Site_Survey_Quote_Required": False,
                "Scope_of_Work": "Device is bouncing constantly",
                "Name_of_MetTel_Requester": "Karen Doe",
                "MetTel_Tech_Call_In_Instructions":
                    "When arriving to the site call HOLMDEL NOC for telematic assistance",
                "MetTel_Requester_Email": "karen.doe@mettel.net",
                "MetTel_Note_Updates": None,
                "MetTel_Group_Email": None,
                "MetTel_Department_Phone_Number": None,
                "MetTel_Department": "Customer Care",
                "MetTel_Bruin_TicketID": "T-12345",
                "Local_Time_of_Dispatch": None,
                "Job_Site_Zip_Code": "99088",
                "Job_Site_Street": "123 Fake Street",
                "Job_Site_State": "CA",
                "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                "Job_Site_City": "Pleasantown",
                "Job_Site": "test street",
                "Information_for_Tech": None,
                "Hard_Time_of_Dispatch_Time_Zone_Local": None,
                "Hard_Time_of_Dispatch_Local": None,
                "Dispatch_Status": "New Dispatch",
                "Dispatch_Number": "DIS37450",
                "Date_of_Dispatch": "2019-11-14",
                "Close_Out_Notes": None,
                "Backup_MetTel_Department_Phone_Number": None
            },
            "APIRequestID": "a130v000001U6iTAAS"
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": [
                {
                    "errorCode": "APEX_ERROR",
                    "message": ""
                }
            ],
            "status": HTTPStatus.INTERNAL_SERVER_ERROR
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload_lit = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "time_of_dispatch": "6PM-8PM",
            "time_zone": "Pacific Time",
            "mettel_bruin_ticket_id": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name": "Jane Doe",
            "job_site_contact_number": "+1 666 6666 666",
            "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "mettel_department_phone_number"
        }

        payload_lit_mapped = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "local_time_of_dispatch": "6PM-8PM",
            "time_zone_local": "Pacific Time",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name_and_phone_number": "Jane Doe +1 666 6666 666",
            "special_materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "mettel_department_phone_number"
        }

        payload_request = {
            "request_id": uuid_,
            "body": {
                'RequestDispatch': payload_lit_mapped
            }
        }

        expected_response_create_error = {
            'code': 500, 'message': [{'errorCode': 'APEX_ERROR', 'message': ''}]
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.post(f'/lit/dispatch', json=payload_lit)

            data = await response.get_json()
            event_bus.rpc_request.assert_awaited_once()

            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            assert data == expected_response_create_error

    @pytest.mark.asyncio
    async def create_dispatch_not_body_response_error_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "error",
            "Message": None,
            "Dispatch": None,
            "APIRequestID": "a130v000001U6iTAAS"
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 400
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload_lit = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "time_of_dispatch": "6PM-8PM",
            "time_zone": "Pacific Time",
            "mettel_bruin_ticket_id": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name": "Jane Doe",
            "job_site_contact_number": "+1 666 6666 666",
            "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "+1 666 6666 666"
        }

        payload_lit_mapped = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "local_time_of_dispatch": "6PM-8PM",
            "time_zone_local": "Pacific Time",
            "mettel_bruin_ticketid": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name_and_phone_number": "Jane Doe +1 666 6666 666",
            "special_materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "+1 666 6666 666"
        }

        payload_request = {
            "request_id": uuid_,
            "body": {
                'RequestDispatch': payload_lit_mapped
            }
        }

        expected_response_create_error = {
            'code': 400,
            'message': {
                'APIRequestID': 'a130v000001U6iTAAS',
                'Dispatch': None,
                'Message': None,
                'Status': 'error'
            }
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.post(f'/lit/dispatch', json=payload_lit)

            data = await response.get_json()
            event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.post", payload_request, timeout=30)

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_create_error

    @pytest.mark.asyncio
    async def update_dispatch_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "Success",
            "Message": None,
            "Dispatch": {
                "turn_up": None,
                "Time_Zone_Local": "Pacific Time",
                "Time_of_Check_Out": None,
                "Time_of_Check_In": None,
                "Tech_Off_Site": False,
                "Tech_Mobile_Number": None,
                "Tech_First_Name": None,
                "Tech_Arrived_On_Site": False,
                "Special_Materials_Needed_for_Dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
                "Special_Dispatch_Notes": None,
                "Site_Survey_Quote_Required": False,
                "Scope_of_Work": "Device is bouncing constantly",
                "Name_of_MetTel_Requester": "Karen Doe",
                "MetTel_Tech_Call_In_Instructions":
                    "When arriving to the site call HOLMDEL NOC for telematic assistance",
                "MetTel_Requester_Email": "karen.doe@mettel.net",
                "MetTel_Note_Updates": None,
                "MetTel_Group_Email": None,
                "MetTel_Department_Phone_Number": None,
                "MetTel_Department": "Customer Care",
                "MetTel_Bruin_TicketID": "T-12345",
                "Local_Time_of_Dispatch": None,
                "Job_Site_Zip_Code": "99088",
                "Job_Site_Street": "123 Fake Street",
                "Job_Site_State": "CA",
                "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                "Job_Site_City": "Pleasantown",
                "Job_Site": "test street",
                "Information_for_Tech": None,
                "Hard_Time_of_Dispatch_Time_Zone_Local": None,
                "Hard_Time_of_Dispatch_Local": None,
                "Dispatch_Status": "New Dispatch",
                "Dispatch_Number": dispatch_number,
                "Date_of_Dispatch": "2019-11-14",
                "Close_Out_Notes": None,
                "Backup_MetTel_Department_Phone_Number": None
            },
            "APIRequestID": "a130v000001U6iTAAS"
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 200
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload_lit = {
            "dispatch_number": dispatch_number,
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "time_of_dispatch": "6PM-8PM",
            "time_zone": "Pacific Time",
            "mettel_bruin_ticket_id": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street MODIFIED",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name": "Jane Doe",
            "job_site_contact_number": "+1 666 6666 666",
            "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "+1 666 6666 666"
        }

        payload_lit_mapped = {
            "dispatch_number": dispatch_number,
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "local_time_of_dispatch": "6PM-8PM",
            "time_zone_local": "Pacific Time",
            "mettel_bruin_ticketid": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street MODIFIED",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name_and_phone_number": "Jane Doe +1 666 6666 666",
            "special_materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "+1 666 6666 666"
        }

        payload_request = {
            "request_id": uuid_,
            "body": {
                'RequestDispatch': payload_lit_mapped
            }
        }

        expected_response_create = {'id': 'DIS37450', 'vendor': 'lit'}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.patch(f'/lit/dispatch', json=payload_lit)

            data = await response.get_json()
            event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.update", payload_request, timeout=30)

            assert response.status_code == HTTPStatus.OK
            assert data == expected_response_create

    @pytest.mark.asyncio
    async def update_dispatch_error_from_lit_500_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response_lit = {
            "request_id": uuid_,
            "body": [
                {
                    "errorCode": "APEX_ERROR",
                    "message": ""
                }
            ],
            "status": HTTPStatus.INTERNAL_SERVER_ERROR
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload_lit = {
            "dispatch_number": dispatch_number,
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "time_of_dispatch": "6PM-8PM",
            "time_zone": "Pacific Time",
            "mettel_bruin_ticket_id": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street MODIFIED",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name": "Jane Doe",
            "job_site_contact_number": "+1 666 6666 666",
            "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "+1 666 6666 666"
        }

        expected_response_create = {
            'code': 500, 'message': [{'errorCode': 'APEX_ERROR', 'message': ''}]
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.patch(f'/lit/dispatch', json=payload_lit)

            data = await response.get_json()
            event_bus.rpc_request.assert_awaited_once()

            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            assert data == expected_response_create

    @pytest.mark.asyncio
    async def update_dispatch_with_no_dispatch_number_error_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "Success",
            "Message": None,
            "Dispatch": {
                "turn_up": None,
                "Time_Zone_Local": "Pacific Time",
                "Time_of_Check_Out": None,
                "Time_of_Check_In": None,
                "Tech_Off_Site": False,
                "Tech_Mobile_Number": None,
                "Tech_First_Name": None,
                "Tech_Arrived_On_Site": False,
                "Special_Materials_Needed_for_Dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
                "Special_Dispatch_Notes": None,
                "Site_Survey_Quote_Required": False,
                "Scope_of_Work": "Device is bouncing constantly",
                "Name_of_MetTel_Requester": "Karen Doe",
                "MetTel_Tech_Call_In_Instructions":
                    "When arriving to the site call HOLMDEL NOC for telematic assistance",
                "MetTel_Requester_Email": "karen.doe@mettel.net",
                "MetTel_Note_Updates": None,
                "MetTel_Group_Email": None,
                "MetTel_Department_Phone_Number": None,
                "MetTel_Department": "Customer Care",
                "MetTel_Bruin_TicketID": "T-12345",
                "Local_Time_of_Dispatch": None,
                "Job_Site_Zip_Code": "99088",
                "Job_Site_Street": "123 Fake Street",
                "Job_Site_State": "CA",
                "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                "Job_Site_City": "Pleasantown",
                "Job_Site": "test street",
                "Information_for_Tech": None,
                "Hard_Time_of_Dispatch_Time_Zone_Local": None,
                "Hard_Time_of_Dispatch_Local": None,
                "Dispatch_Status": "New Dispatch",
                "Dispatch_Number": dispatch_number,
                "Date_of_Dispatch": "2019-11-14",
                "Close_Out_Notes": None,
                "Backup_MetTel_Department_Phone_Number": None
            },
            "APIRequestID": "a130v000001U6iTAAS"
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 200
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload_lit = {
            "dispatch_number_BAD_FIELD": dispatch_number,
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "time_of_dispatch": "6PM-8PM",
            "time_zone": "Pacific Time",
            "mettel_bruin_ticket_id": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street MODIFIED",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name": "Jane Doe",
            "job_site_contact_number": "+1 666 6666 666",
            "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "+1 666 6666 666"
        }

        expected_response_create = {'code': 400, 'message': "'dispatch_number' is a required property"}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.patch(f'/lit/dispatch', json=payload_lit)

            data = await response.get_json()
            event_bus.rpc_request.assert_not_awaited()

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_create

    @pytest.mark.asyncio
    async def update_dispatch_validation_error_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "Success",
            "Message": None,
            "Dispatch": {
                "turn_up": None,
                "Time_Zone_Local": "Pacific Time",
                "Time_of_Check_Out": None,
                "Time_of_Check_In": None,
                "Tech_Off_Site": False,
                "Tech_Mobile_Number": None,
                "Tech_First_Name": None,
                "Tech_Arrived_On_Site": False,
                "Special_Materials_Needed_for_Dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
                "Special_Dispatch_Notes": None,
                "Site_Survey_Quote_Required": False,
                "Scope_of_Work": "Device is bouncing constantly",
                "Name_of_MetTel_Requester": "Karen Doe",
                "MetTel_Tech_Call_In_Instructions":
                    "When arriving to the site call HOLMDEL NOC for telematic assistance",
                "MetTel_Requester_Email": "karen.doe@mettel.net",
                "MetTel_Note_Updates": None,
                "MetTel_Group_Email": None,
                "MetTel_Department_Phone_Number": None,
                "MetTel_Department": "Customer Care",
                "MetTel_Bruin_TicketID": None,
                "Local_Time_of_Dispatch": None,
                "Job_Site_Zip_Code": "99088",
                "Job_Site_Street": "123 Fake Street",
                "Job_Site_State": "CA",
                "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                "Job_Site_City": "Pleasantown",
                "Job_Site": "test street",
                "Information_for_Tech": None,
                "Hard_Time_of_Dispatch_Time_Zone_Local": None,
                "Hard_Time_of_Dispatch_Local": None,
                "Dispatch_Status": "New Dispatch",
                "Dispatch_Number": dispatch_number,
                "Date_of_Dispatch": "2019-11-14",
                "Close_Out_Notes": None,
                "Backup_MetTel_Department_Phone_Number": None
            },
            "APIRequestID": "a130v000001U6iTAAS"
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 200
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload_lit = {
            "dispatch_number_BAD_FIELD": dispatch_number,
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "time_of_dispatch": "6PM-8PM",
            "time_zone": "Pacific Time",
            "mettel_bruin_ticket_id": 123,
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street MODIFIED",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name": "Jane Doe",
            "job_site_contact_number": "+1 666 6666 666",
            "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "+1 666 6666 666"
        }

        payload_lit_mapped = {
            "dispatch_number": dispatch_number,
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "local_time_of_dispatch": "6PM-8PM",
            "time_zone_local": "Pacific Time",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name_and_phone_number_BAD_FIELD": "Jane Doe +1 666 6666 666",
            "special_materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "+1 666 6666 666"
        }

        expected_response_create = {'code': 400, 'message': "'dispatch_number' is a required property"}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.patch(f'/lit/dispatch', json=payload_lit)
            data = await response.get_json()
            event_bus.rpc_request.assert_not_awaited()

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_create

    @pytest.mark.asyncio
    async def update_dispatch_not_body_response_error_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "error",
            "Message": None,
            "Dispatch": None,
            "APIRequestID": "a130v000001U6iTAAS"
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 400
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload_lit = {
            "dispatch_number": dispatch_number,
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "time_of_dispatch": "6PM-8PM",
            "time_zone": "Pacific Time",
            "mettel_bruin_ticket_id": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name": "Jane Doe",
            "job_site_contact_number": "+1 666 6666 666",
            "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "+1 666 6666 666"
        }

        payload_lit_mapped = {
            "dispatch_number": dispatch_number,
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "local_time_of_dispatch": "6PM-8PM",
            "time_zone_local": "Pacific Time",
            "mettel_bruin_ticketid": "T-12345",
            "job_site": "Red Rose Inn",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name_and_phone_number": "Jane Doe +1 666 6666 666",
            "special_materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "+1 666 6666 666"
        }

        payload_request = {
            "request_id": uuid_,
            "body": {
                'RequestDispatch': payload_lit_mapped
            }
        }

        expected_response_create_error = {
            'code': 400,
            'message': {
                'APIRequestID': 'a130v000001U6iTAAS',
                'Dispatch': None,
                'Message': None,
                'Status': 'error'
            }
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.patch(f'/lit/dispatch', json=payload_lit)

            data = await response.get_json()
            event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.update", payload_request, timeout=30)

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_create_error

    @pytest.mark.asyncio
    async def upload_file_to_dispatch_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "Success",
            "Message": "File ID:00P0v000004ti2gEAA",
            "Dispatch": None,
            "APIRequestID": None
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 200
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload_lit = {
            'dispatch_number': dispatch_number,
            'payload': base64.b64encode(b'test').decode('utf-8'),
            'file_name': 'test.txt'
        }

        payload_request = {
            "request_id": uuid_,
            "body": payload_lit
        }

        expected_response_upload_file = {
            'id': 'DIS37450',
            'vendor': 'lit',
            'file_id': '00P0v000004ti2gEAA'
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            headers = {"Content-Type": "application/octet-stream", "filename": "test.txt"}
            response = await client.post(f'/lit/dispatch/{dispatch_number}/upload-file',
                                         data=b'test', headers=headers)

            data = await response.get_json()
            event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.upload.file", payload_request, timeout=300)

            assert response.status_code == HTTPStatus.OK
            assert data == expected_response_upload_file

    @pytest.mark.asyncio
    async def upload_file_to_dispatch_no_file_name_in_header_error_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "Success",
            "Message": "File ID:00P0v000004ti2gEAA",
            "Dispatch": None,
            "APIRequestID": None
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 200
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        expected_response_upload_file = {'code': HTTPStatus.BAD_REQUEST, 'message': 'No `filename` in headers'}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            headers = {"Content-Type": "application/octet-stream", "NO_FILE_NAME": "test.txt"}
            response = await client.post(f'/lit/dispatch/{dispatch_number}/upload-file',
                                         data=b'test', headers=headers)

            data = await response.get_json()
            event_bus.rpc_request.assert_not_awaited()

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_upload_file

    @pytest.mark.asyncio
    async def upload_file_to_dispatch_no_correct_content_type_in_header_error_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "Success",
            "Message": "File ID:00P0v000004ti2gEAA",
            "Dispatch": None,
            "APIRequestID": None
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 200
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        expected_response_upload_file = {
            'code': HTTPStatus.BAD_REQUEST,
            'message': '`content-type` in headers not present or different to `application/octet-stream`'
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            headers = {"Content-Type": "application/json", "filename": "test.txt"}
            response = await client.post(f'/lit/dispatch/{dispatch_number}/upload-file',
                                         data=b'test', headers=headers)

            data = await response.get_json()
            event_bus.rpc_request.assert_not_awaited()

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_upload_file

    @pytest.mark.asyncio
    async def upload_file_to_dispatch_empty_body_error_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "Success",
            "Message": "File ID:00P0v000004ti2gEAA",
            "Dispatch": None,
            "APIRequestID": None
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 200
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        expected_response_upload_file = {
            'code': HTTPStatus.BAD_REQUEST,
            'message': "Body provided is empty"
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            headers = {"Content-Type": "application/octet-stream", "filename": "test.txt"}
            response = await client.post(f'/lit/dispatch/{dispatch_number}/upload-file',
                                         data=b'', headers=headers)

            data = await response.get_json()
            event_bus.rpc_request.assert_not_awaited()

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_upload_file

    @pytest.mark.asyncio
    async def upload_file_to_dispatch_large_content_length_body_error_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "Success",
            "Message": "File ID:00P0v000004ti2gEAA",
            "Dispatch": None,
            "APIRequestID": None
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 200
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        expected_response_upload_file = {
            'code': HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            'message': 'Entity too large'
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            headers = {
                "Content-Type": "application/octet-stream",
                "filename": "test.txt",
                "Content-length": (api_server_test._max_content_length) + 1  # 16mb + 1 byte more
            }
            response = await client.post(f'/lit/dispatch/{dispatch_number}/upload-file',
                                         data=b'', headers=headers)

            data = await response.get_json()
            event_bus.rpc_request.assert_not_awaited()

            assert response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE
            assert data == expected_response_upload_file

    @pytest.mark.asyncio
    async def upload_file_to_dispatch_general_exception_error_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "Success",
            "Message": "File ID:00P0v000004ti2gEAA",
            "Dispatch": None,
            "APIRequestID": None
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 200
        }
        http_exception = HTTPException(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Entity too large", "http_exception")
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=http_exception)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        expected_response_upload_file = {
            'code': HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            'message': 'Entity too large'
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            try:
                client = api_server_test._app.test_client()
                headers = {
                    "Content-Type": "application/octet-stream",
                    "filename": "test.txt",
                    "Content-length": (api_server_test._max_content_length) + 1  # 16mb + 1 byte more
                }
                data_payload = b'0' * (32 * (1024 * 1024))
                response = await client.post(f'/lit/dispatch/{dispatch_number}/upload-file',
                                             data=data_payload, headers=headers)
                data = await response.get_json()
                event_bus.rpc_request.assert_not_awaited()

                assert response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE
                assert data == expected_response_upload_file
            except HTTPException as ex:
                assert ex.status_code == 413
                assert ex.description == 'Entity too large'

    @pytest.mark.asyncio
    async def upload_file_to_dispatch_error_from_lit_500_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'

        expected_response_lit = {
            "request_id": uuid_,
            "body": [
                {
                    "errorCode": "APEX_ERROR",
                    "message": ""
                }
            ],
            "status": HTTPStatus.INTERNAL_SERVER_ERROR
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        expected_response_upload_file = {
            'code': 500, 'message': [{'errorCode': 'APEX_ERROR', 'message': ''}]
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            headers = {
                "Content-Type": "application/octet-stream",
                "filename": "test.txt",
                "Content-length": (api_server_test._max_content_length)  # 16mb + 1 byte more
            }
            data_payload = b'0000'
            response = await client.post(f'/lit/dispatch/{dispatch_number}/upload-file',
                                         data=data_payload, headers=headers)
            data = await response.get_json()
            event_bus.rpc_request.assert_awaited_once()

            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            assert data == expected_response_upload_file

    @pytest.mark.asyncio
    async def upload_file_to_dispatch_response_status_not_200_error_test(self):
        uuid_ = 'UUID1'
        logger = Mock()
        redis_client = Mock()

        dispatch_number = 'DIS37450'
        expected_response = {
            "Status": "error",
            "Message": "SOME ERROR",
            "Dispatch": None,
            "APIRequestID": 'a130v000001U6iTAAS'
        }
        expected_response_lit = {
            "request_id": uuid_,
            "body": expected_response,
            "status": 400
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        api_server_test = DispatchServer(config, redis_client, event_bus, logger)

        payload_lit = {
            'dispatch_number': dispatch_number,
            'payload': base64.b64encode(b'test').decode('utf-8'),
            'file_name': 'test.txt'
        }

        payload_request = {
            "request_id": uuid_,
            "body": payload_lit
        }

        expected_response_upload_error = {
            'code': 400,
            'message': {
                'APIRequestID': 'a130v000001U6iTAAS',
                'Dispatch': None,
                'Message': "SOME ERROR",
                'Status': 'error'
            }
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            headers = {"Content-Type": "application/octet-stream", "filename": "test.txt"}
            response = await client.post(f'/lit/dispatch/{dispatch_number}/upload-file',
                                         data=b'test', headers=headers)

            data = await response.get_json()
            event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.upload.file", payload_request, timeout=300)

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_upload_error
