import base64
from http import HTTPStatus

import pytest
from unittest.mock import Mock, patch
from unittest.mock import call

from quart.exceptions import HTTPException

import application
from application.mappers import cts_mapper
from application.templates.cts.dispatch_cancel_mail import render_cancel_email_template
from application.templates.cts.dispatch_request_mail import render_email_template
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

        bruin_repository = Mock()
        lit_repository = Mock()
        notifications_repository = Mock()

        api_server_test = DispatchServer(config, redis_client, event_bus, logger, bruin_repository,
                                         lit_repository, notifications_repository)

        assert api_server_test._logger is logger
        assert api_server_test._redis_client is redis_client
        assert api_server_test._event_bus is event_bus
        assert api_server_test._bruin_repository is bruin_repository
        assert api_server_test._lit_repository is lit_repository
        assert api_server_test._notifications_repository is notifications_repository

        assert api_server_test._title == config.QUART_CONFIG['title']
        assert api_server_test._port == config.QUART_CONFIG['port']
        assert isinstance(api_server_test._hypercorn_config, HyperCornConfig) is True
        assert api_server_test._new_bind == f'0.0.0.0:{api_server_test._port}'
        assert isinstance(api_server_test._app, Quart) is True
        assert api_server_test._app.title == api_server_test._title

    @pytest.mark.asyncio
    async def run_server_test(self, api_server_test):
        with patch.object(application.server.api_server, 'serve', new=CoroutineMock()) \
                as mock_serve:
            await api_server_test.run_server()
            assert api_server_test._hypercorn_config.bind == [api_server_test._new_bind]
            assert mock_serve.called

    @pytest.mark.asyncio
    async def ok_app_test(self, api_server_test):
        client = api_server_test._app.test_client()
        response = await client.get('/_health')
        data = await response.get_json()
        assert response.status_code == 200
        assert data is None

    def attach_swagger_test(self, api_server_test):
        with patch.object(api_server_module, 'quart_api_doc', new=CoroutineMock()) as quart_api_doc_mock:
            api_server_test.attach_swagger()
            quart_api_doc_mock.assert_called_once()

    def set_status_test(self, api_server_test):
        assert api_server_test._status == HTTPStatus.OK
        api_server_test.set_status(HTTPStatus.INTERNAL_SERVER_ERROR)
        assert api_server_test._status == HTTPStatus.INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def lit_get_dispatch_test(self, api_server_test):
        uuid_ = 'UUID1'

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
                    "MetTel_Department_Phone_Number": '(111) 111-1111',
                    "MetTel_Department": "Customer Care",
                    "MetTel_Bruin_TicketID": "T-12345",
                    "Local_Time_of_Dispatch": "7AM-8PM",
                    "Job_Site_Zip_Code": "99088",
                    "Job_Site_Street": "123 Fake Street",
                    "Job_Site_State": "CA",
                    "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                    "Job_Site_City": "Pleasantown",
                    "Job_Site": "test street",
                    "Information_for_Tech": None,
                    "Hard_Time_of_Dispatch_Time_Zone_Local": "Pacific Time",
                    "Hard_Time_of_Dispatch_Local": "7AM-8PM",
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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        expected_response = {
            "id": "DIS37450",
            "vendor": "lit",
            "dispatch": {
                "dispatch_number": "DIS37450",
                "date_of_dispatch": "2019-11-14",
                "site_survey_quote_required": False,
                "time_of_dispatch": "7AM-8PM",
                "time_zone": "Pacific Time",
                "mettel_bruin_ticket_id": "T-12345",
                "hard_time_of_dispatch_local": "7AM-8PM",
                "hard_time_of_dispatch_time_zone_local": "Pacific Time",
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
                'mettel_requester_phone_number': '(111) 111-1111',
                "dispatch_status": "New Dispatch"
            }
        }

        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch/{dispatch_number}')
            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", payload, timeout=30)

            assert response.status_code == HTTPStatus.OK
            assert data == expected_response

    @pytest.mark.asyncio
    async def lit_get_dispatch_not_found_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        expected_response = {
            "code": 400,
            "message": {
                "Status": "error",
                "Message": "List has no rows for assignment to SObject",
                "Dispatch": None,
                "APIRequestID": "a130v000001UG7sAAG"
            }
        }

        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch/{dispatch_number}')
            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", payload, timeout=30)

            # response = await api_server_test.get_dispatch('DIS37450')
            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response
            assert data['code'] == HTTPStatus.BAD_REQUEST

    @pytest.mark.asyncio
    async def lit_get_dispatch_error_from_lit_500_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        expected_response = {'code': 500, 'message': [{'errorCode': 'APEX_ERROR', 'message': ''}]}

        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch/{dispatch_number}')
            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", payload, timeout=30)

            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            assert data == expected_response
            assert data['code'] == HTTPStatus.INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def lit_get_all_dispatch_test(self, api_server_test):
        uuid_ = 'UUID1'

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
                        "Local_Time_of_Dispatch": "2:00pm",
                        "Job_Site_Zip_Code": "99088",
                        "Job_Site_Street": "123 Fake Street",
                        "Job_Site_State": "CA",
                        "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                        "Job_Site_City": "Pleasantown",
                        "Job_Site": "test site",
                        "Information_for_Tech": None,
                        "Hard_Time_of_Dispatch_Time_Zone_Local": "Pacific Time",
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
                        "Local_Time_of_Dispatch": "12.30AM",
                        "Job_Site_Zip_Code": "99088",
                        "Job_Site_Street": "123 Fake Street",
                        "Job_Site_State": "CA",
                        "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                        "Job_Site_City": "Pleasantown",
                        "Job_Site": "test site",
                        "Information_for_Tech": None,
                        "Hard_Time_of_Dispatch_Time_Zone_Local": "Pacific Time",
                        "Hard_Time_of_Dispatch_Local": "12.30AM",
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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        expected_response = {
            "vendor": "LIT",
            "list_dispatch": [
                {
                    "dispatch_number": "DIS37263",
                    "date_of_dispatch": "2019-11-14",
                    "site_survey_quote_required": True,
                    "time_of_dispatch": "2:00pm",
                    "time_zone": "Pacific Time",
                    "mettel_bruin_ticket_id": "T-12345",
                    "hard_time_of_dispatch_local": "2:00pm",
                    "hard_time_of_dispatch_time_zone_local": "Pacific Time",
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
                    'mettel_requester_phone_number': '(111) 111-1111',
                    "dispatch_status": "New Dispatch"
                },
                {
                    "dispatch_number": "DIS37264",
                    "date_of_dispatch": "2019-11-14",
                    "site_survey_quote_required": False,
                    "time_of_dispatch": "12.30AM",
                    "time_zone": "Pacific Time",
                    "mettel_bruin_ticket_id": "T-12345",
                    "hard_time_of_dispatch_local": "12.30AM",
                    "hard_time_of_dispatch_time_zone_local": "Pacific Time",
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
                    'mettel_requester_phone_number': '(111) 111-1111',
                    "dispatch_status": "Request Confirmed"
                }
            ]
        }

        payload = {"request_id": uuid_, "body": {}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch/')
            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", payload, timeout=30)

            assert response.status_code == HTTPStatus.OK
            assert data == expected_response

    @pytest.mark.asyncio
    async def lit_get_all_dispatch_error_500_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        payload = {"request_id": uuid_, "body": {}}

        expected_response_get_all_dispatches_error = {
            'code': 500, 'message': [{'errorCode': 'APEX_ERROR', 'message': ''}]
        }

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch', json=payload)

            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_awaited_once()

            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            assert data == expected_response_get_all_dispatches_error

    @pytest.mark.asyncio
    async def lit_get_all_dispatch_error_400_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        payload = {"request_id": uuid_, "body": {}}

        expected_response_get_all_dispatches_error = {
            'code': 400, 'message': [{'errorCode': 'APEX_ERROR', 'message': ''}]
        }

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch', json=payload)

            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_awaited_once()

            assert response.status_code == 400
            assert data == expected_response_get_all_dispatches_error

    @pytest.mark.asyncio
    async def lit_get_all_dispatch_error_in_response_test(self, api_server_test):
        uuid_ = 'UUID1'

        expected_response_lit = {
            "request_id": uuid_,
            "body": {},
            "status": 200
        }

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        payload = {"request_id": uuid_, "body": {}}

        expected_response_get_all_dispatches_error = {
            'code': 200, 'message': {}
        }

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch', json=payload)

            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_awaited_once()

            assert response.status_code == 200
            assert data == expected_response_get_all_dispatches_error

    @pytest.mark.asyncio
    async def lit_create_dispatch_with_note_test(self, api_server_test):
        uuid_ = 'UUID1'

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
                "Hard_Time_of_Dispatch_Time_Zone_Local": "Pacific Time",
                "Hard_Time_of_Dispatch_Local": "6PM-8PM",
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

        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[
            expected_response_lit,
            expected_response_bruin,
            expected_response_bruin_append_note
        ])

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
            "hard_time_of_dispatch_local": "6PM-8PM",
            "time_zone_local": "Pacific Time",
            "hard_time_of_dispatch_time_zone_local": "Pacific Time",
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
                      'Please see the summary below.\n' \
                      '--\nDate of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n' \
                      'Time Zone (Local): Pacific Time\n' \
                      '\nLocation Owner/Name: Red Rose Inn\n' \
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
                        'Please see the summary below.\n'
                        '--\n'
                        f'Dispatch Number: [{dispatch_number}|'
                        f'https://master.mettel-automation.net/dispatch_portal/dispatch/{dispatch_number}]\n'
                        'Date of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n'
                        'Time Zone (Local): Pacific Time\n\nLocation Owner/Name: Red Rose Inn\n'
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
        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])
        slack_msg = f"[dispatch-portal-backend] [LIT] Dispatch Created [{dispatch_number}] " \
                    f"with ticket id: T-12345"
        # api_server_test._notifications_repository.send_slack_message.assert_awaited_with(slack_msg)

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.post(f'/lit/dispatch', json=payload_lit)

            data = await response.get_json()

            api_server_test._event_bus.rpc_request.assert_has_awaits([
                call("lit.dispatch.post", payload_request, timeout=60),
            ])

            assert response.status_code == HTTPStatus.OK
            assert data == expected_response_create
            api_server_test._notifications_repository.send_slack_message.assert_awaited_with(slack_msg)

    @pytest.mark.asyncio
    async def lit_create_dispatch_with_error_appending_note_test(self, api_server_test):
        uuid_ = 'UUID1'

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
                "Hard_Time_of_Dispatch_Time_Zone_Local": "Pacific Time",
                "Hard_Time_of_Dispatch_Local": "12.30AM",
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

        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[
            expected_response_lit,
            expected_response_bruin,
            expected_response_bruin_append_note
        ])

        payload_lit = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "time_of_dispatch": "12.30AM",
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
            "hard_time_of_dispatch_local": "12.30AM",
            "local_time_of_dispatch": "12.30AM",
            "hard_time_of_dispatch_time_zone_local": "Pacific Time",
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
                        'Please see the summary below.\n'
                        f'--\nDispatch Number: '
                        f'[{dispatch_number}|'
                        f'https://master.mettel-automation.net/dispatch_portal/dispatch/{dispatch_number}]\n'
                        'Date of Dispatch: 2019-11-14\nTime of Dispatch (Local): 12.30AM\n'
                        'Time Zone (Local): Pacific Time\n\nLocation Owner/Name: Red Rose Inn\n'
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

        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])
        slack_msg = f"[dispatch-portal-backend] [LIT] Dispatch Created [{dispatch_number}] " \
                    f"with ticket id: T-12345"
        # api_server_test._notifications_repository.send_slack_message.assert_awaited_with(slack_msg)

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.post(f'/lit/dispatch', json=payload_lit)

            data = await response.get_json()

            api_server_test._event_bus.rpc_request.assert_has_awaits([
                call("lit.dispatch.post", payload_request, timeout=60),
            ])

            assert response.status_code == HTTPStatus.OK
            assert data == expected_response_create
            api_server_test._notifications_repository.send_slack_message.assert_awaited_with(slack_msg)

    @pytest.mark.asyncio
    async def lit_create_dispatch_error_exception_test(self, api_server_test):
        uuid_ = 'UUID1'
        ticket_id = 'T-12345'
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
            "body": {
                'NOT ticketNotes field': [
                    {
                        'noteValue': '#*Automation Engine*#\nDispatch Management - Dispatch Requested\n\n'
                                     'Please see the summary below.\n'
                                     f'--\nDispatch Number: '
                                     f'[{dispatch_number}|'
                                     f'https://master.mettel-automation.net/dispatch_portal/dispatch/DIS37266]\n'
                                     'Date of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n'
                                     'Time Zone (Local): Pacific Time\n'
                                     '\nLocation Owner/Name: Red Rose Inn\n'
                                     'Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n'
                                     'Phone: +1 666 6666 666\n\nIssues Experienced:\nDevice is bouncing constantly\n'
                                     'Arrival Instructions: When arriving to the site call '
                                     'HOLMDEL NOC for telematic assistance\nMaterials Needed:\n'
                                     'Laptop, cable, tuner, ladder,internet hotspot\n\nRequester\n'
                                     'Name: Karen Doe\nPhone: mettel_department_phone_number\n'
                                     'Email: karen.doe@mettel.net\nDepartment: Customer Care'
                    }
                ]
            },
            "status": 200
        }

        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[
            expected_response_lit,
            expected_response_bruin
        ])

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
            "hard_time_of_dispatch_local": "6PM-8PM",
            "local_time_of_dispatch": "6PM-8PM",
            "hard_time_of_dispatch_time_zone_local": "Pacific Time",
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
                      'Please see the summary below.\n' \
                      '--\nDate of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n' \
                      'Time Zone (Local): Pacific Time\n' \
                      '\nLocation Owner/Name: Red Rose Inn\n' \
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
                'ticket_id': ticket_id,
                'note': '#*Automation Engine*#\nDispatch Management - Dispatch Requested\n\n'
                        'Please see the summary below.\n--\n'
                        'Date of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n'
                        'Time Zone (Local): Pacific Time\n\nLocation Owner/Name: Red Rose Inn\n'
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

        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])
        slack_msg = f"[dispatch-portal-backend] [LIT] Dispatch Created [{dispatch_number}] " \
                    f"with ticket id: {ticket_id}"

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.post(f'/lit/dispatch', json=payload_lit)

            data = await response.get_json()

            api_server_test._event_bus.rpc_request.assert_has_awaits([
                call("lit.dispatch.post", payload_request, timeout=60),
            ])

            assert response.status_code == HTTPStatus.OK
            assert data == expected_response_create
            api_server_test._notifications_repository.send_slack_message.assert_awaited_with(slack_msg)

    @pytest.mark.asyncio
    async def lit_create_dispatch_validation_error_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

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
            api_server_test._event_bus.rpc_request.assert_not_awaited()

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_create_error

    @pytest.mark.asyncio
    async def lit_create_dispatch_error_from_lit_500_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

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
            api_server_test._event_bus.rpc_request.assert_awaited_once()

            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            assert data == expected_response_create_error

    @pytest.mark.asyncio
    async def lit_create_dispatch_not_body_response_error_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

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
            "hard_time_of_dispatch_local": "6PM-8PM",
            "local_time_of_dispatch": "6PM-8PM",
            "hard_time_of_dispatch_time_zone_local": "Pacific Time",
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
            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                "lit.dispatch.post", payload_request, timeout=60)

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_create_error

    @pytest.mark.asyncio
    async def lit_cancel_dispatch_test(
            self, api_server_test, dispatch_confirmed, ticket_details_1_no_requested_watermark):
        uuid_ = 'UUID1'
        dispatch_number = dispatch_confirmed['Dispatch_Number']
        ticket_id = dispatch_confirmed['MetTel_Bruin_TicketID']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}
        body = {
            'dispatch_number': dispatch_number,
            'ticket_id': ticket_id
        }
        email_template = render_cancel_email_template(body)
        email_html = f'<div>{email_template}</div>'
        email_data = {
            'request_id': uuid_,
            'email_data': {
                'subject': f'LIT - Service Submission - {ticket_id}',
                'recipient': api_server_test._config.LIT_CONFIG["email"],
                'text': 'this is the accessible text for the email',
                'html': email_html,
                'images': [],
                'attachments': []
            }
        }
        response_send_email_mock = {
            'status': 200
        }
        response_rpc_request_mock = {
            'body': {
                'Dispatch': dispatch_confirmed
            },
            'status': 200
        }

        expected_response = {
            'id': dispatch_number,
            'vendor': 'LIT'
        }

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            return_value=ticket_details_1_no_requested_watermark)
        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[response_rpc_request_mock])
        api_server_test._notifications_repository.send_email = CoroutineMock(side_effect=[response_send_email_mock])
        api_server_test._append_note_to_ticket = CoroutineMock()
        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])
        slack_msg = f"[dispatch-portal-backend] [LIT] Dispatch Cancel Requested by email " \
                    f"[{dispatch_number}] with ticket id: {ticket_id}"

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch/{dispatch_number}/cancel')
            response_data = await response.get_json()

            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                'lit.dispatch.get', payload, timeout=30)
            api_server_test._notifications_repository.send_email.assert_awaited_once_with(email_data)
            api_server_test._append_note_to_ticket.assert_awaited_once()
            api_server_test._notifications_repository.send_slack_message.assert_awaited_with(slack_msg)
            assert response_data == expected_response

    @pytest.mark.asyncio
    async def lit_cancel_dispatch_error_could_not_retrieve_dispatch_test(
            self, api_server_test, dispatch_confirmed, ticket_details_1_no_requested_watermark):
        uuid_ = 'UUID1'
        dispatch_number = dispatch_confirmed['Dispatch_Number']
        ticket_id = dispatch_confirmed['MetTel_Bruin_TicketID']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}
        body = {
            'dispatch_number': dispatch_number,
            'ticket_id': ticket_id
        }
        email_template = render_cancel_email_template(body)
        email_html = f'<div>{email_template}</div>'
        email_data = {
            'request_id': uuid_,
            'email_data': {
                'subject': f'LIT - Service Submission - {ticket_id}',
                'recipient': api_server_test._config.LIT_CONFIG["email"],
                'text': 'this is the accessible text for the email',
                'html': email_html,
                'images': [],
                'attachments': []
            }
        }
        response_send_email_mock = {
            'status': 200
        }
        response_rpc_request_mock = {
            'body': {},
            'status': 500
        }

        expected_response = {
            'id': dispatch_number,
            'vendor': 'LIT'
        }

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            return_value=ticket_details_1_no_requested_watermark)
        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[response_rpc_request_mock])
        api_server_test._notifications_repository.send_email = CoroutineMock(side_effect=[response_send_email_mock])
        api_server_test._append_note_to_ticket = CoroutineMock()
        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])
        slack_msg = f"[dispatch-portal-backend] [LIT] Dispatch Cancel Requested by email [{dispatch_number}] " \
                    f"with ticket id: {ticket_id}"

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch/{dispatch_number}/cancel')
            response_data = await response.get_json()
            assert response_data['code'] == 500
            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                'lit.dispatch.get', payload, timeout=30)
            api_server_test._notifications_repository.send_email.assert_not_awaited()
            api_server_test._append_note_to_ticket.assert_not_awaited()
            api_server_test._notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def lit_cancel_dispatch_error_retrieve_valid_dispatch_test(
            self, api_server_test, dispatch_confirmed, ticket_details_1_no_requested_watermark):
        uuid_ = 'UUID1'
        dispatch_number = dispatch_confirmed['Dispatch_Number']
        ticket_id = dispatch_confirmed['MetTel_Bruin_TicketID']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}
        body = {
            'dispatch_number': dispatch_number,
            'ticket_id': ticket_id
        }
        email_template = render_cancel_email_template(body)
        email_html = f'<div>{email_template}</div>'
        email_data = {
            'request_id': uuid_,
            'email_data': {
                'subject': f'LIT - Service Submission - {ticket_id}',
                'recipient': api_server_test._config.LIT_CONFIG["email"],
                'text': 'this is the accessible text for the email',
                'html': email_html,
                'images': [],
                'attachments': []
            }
        }
        response_send_email_mock = {
            'status': 200
        }
        response_rpc_request_mock = {
            'body': {},
            'status': 400
        }

        expected_response = {
            'id': dispatch_number,
            'vendor': 'LIT'
        }

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            return_value=ticket_details_1_no_requested_watermark)
        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[response_rpc_request_mock])
        api_server_test._notifications_repository.send_email = CoroutineMock(side_effect=[response_send_email_mock])
        api_server_test._append_note_to_ticket = CoroutineMock()
        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])
        slack_msg = f"[dispatch-portal-backend] [LIT] Dispatch Cancel Requested by email [{dispatch_number}] " \
                    f"with ticket id: {ticket_id}"

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch/{dispatch_number}/cancel')
            response_data = await response.get_json()
            assert response_data['code'] == 400
            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                'lit.dispatch.get', payload, timeout=30)
            api_server_test._notifications_repository.send_email.assert_not_awaited()
            api_server_test._append_note_to_ticket.assert_not_awaited()
            api_server_test._notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def lit_cancel_dispatch_error_dispatch_datetime_test(
            self, api_server_test, dispatch, ticket_details_1_no_requested_watermark):
        uuid_ = 'UUID1'
        dispatch_number = dispatch['Dispatch_Number']
        ticket_id = dispatch['MetTel_Bruin_TicketID']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}
        body = {
            'dispatch_number': dispatch_number,
            'ticket_id': ticket_id
        }
        email_template = render_cancel_email_template(body)
        email_html = f'<div>{email_template}</div>'
        email_data = {
            'request_id': uuid_,
            'email_data': {
                'subject': f'LIT - Service Submission - {ticket_id}',
                'recipient': api_server_test._config.LIT_CONFIG["email"],
                'text': 'this is the accessible text for the email',
                'html': email_html,
                'images': [],
                'attachments': []
            }
        }
        response_send_email_mock = {
            'status': 200
        }
        response_rpc_request_mock = {
            'body': {
                'Dispatch': dispatch
            },
            'status': 200
        }

        expected_response = {
            'id': dispatch_number,
            'vendor': 'LIT'
        }

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            return_value=ticket_details_1_no_requested_watermark)
        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[response_rpc_request_mock])
        api_server_test._notifications_repository.send_email = CoroutineMock(side_effect=[response_send_email_mock])
        api_server_test._append_note_to_ticket = CoroutineMock()
        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])
        slack_msg = f"[dispatch-portal-backend] [LIT] Dispatch Cancel Requested by email [{dispatch_number}] " \
                    f"with ticket id: {ticket_id}"

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch/{dispatch_number}/cancel')
            response_data = await response.get_json()
            assert response_data['code'] == 400
            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                'lit.dispatch.get', payload, timeout=30)
            api_server_test._notifications_repository.send_email.assert_not_awaited()
            api_server_test._append_note_to_ticket.assert_not_awaited()
            api_server_test._notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def lit_cancel_dispatch_with_error_getting_ticket_details_test(
            self, api_server_test, dispatch_confirmed, ticket_details_1_error):
        uuid_ = 'UUID1'
        dispatch_number = dispatch_confirmed['Dispatch_Number']
        ticket_id = dispatch_confirmed['MetTel_Bruin_TicketID']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}

        response_send_email_mock = {
            'status': 200
        }
        response_rpc_request_mock = {
            'body': {
                'Dispatch': dispatch_confirmed
            },
            'status': 200
        }

        expected_response = {
            'body': f"[LIT] Error: could not retrieve ticket [{ticket_id}] details",
            'status': 400
        }

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            return_value=ticket_details_1_error)
        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[response_rpc_request_mock])
        api_server_test._notifications_repository.send_email = CoroutineMock(side_effect=[response_send_email_mock])
        api_server_test._append_note_to_ticket = CoroutineMock()
        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch/{dispatch_number}/cancel')
            response_data = await response.get_json()

            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                'lit.dispatch.get', payload, timeout=30)
            api_server_test._notifications_repository.send_email.assert_not_awaited()
            api_server_test._append_note_to_ticket.assert_not_awaited()
            assert response_data == expected_response

    @pytest.mark.asyncio
    async def lit_cancel_dispatch_with_existing_cancel_watermark_test(
            self, api_server_test, dispatch_confirmed, ticket_details_1_with_cancel_requested_watermark):
        uuid_ = 'UUID1'
        dispatch_number = dispatch_confirmed['Dispatch_Number']
        ticket_id = dispatch_confirmed['MetTel_Bruin_TicketID']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}

        response_send_email_mock = {
            'status': 200
        }
        response_rpc_request_mock = {
            'body': {
                'Dispatch': dispatch_confirmed
            },
            'status': 200
        }

        expected_response = {
            'id': dispatch_number,
            'vendor': 'LIT'
        }

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            return_value=ticket_details_1_with_cancel_requested_watermark)
        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[response_rpc_request_mock])
        api_server_test._notifications_repository.send_email = CoroutineMock(side_effect=[response_send_email_mock])
        api_server_test._append_note_to_ticket = CoroutineMock()
        api_server_test._get_igz_dispatch_number = CoroutineMock(return_value='IGZ001')
        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch/{dispatch_number}/cancel')
            response_data = await response.get_json()

            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                'lit.dispatch.get', payload, timeout=30)
            api_server_test._notifications_repository.send_email.assert_not_awaited()
            api_server_test._append_note_to_ticket.assert_not_awaited()
            assert response_data == expected_response

    @pytest.mark.asyncio
    async def lit_cancel_dispatch_error_send_email_test(
            self, api_server_test, dispatch_confirmed, ticket_details_1_no_requested_watermark):
        uuid_ = 'UUID1'
        dispatch_number = dispatch_confirmed['Dispatch_Number']
        ticket_id = dispatch_confirmed['MetTel_Bruin_TicketID']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}
        body = {
            'dispatch_number': dispatch_number,
            'ticket_id': ticket_id
        }
        email_template = render_cancel_email_template(body)
        email_html = f'<div>{email_template}</div>'
        email_data = {
            'request_id': uuid_,
            'email_data': {
                'subject': f'LIT - Service Submission - {ticket_id}',
                'recipient': api_server_test._config.CTS_CONFIG["email"],
                'text': 'this is the accessible text for the email',
                'html': email_html,
                'images': [],
                'attachments': []
            }
        }
        response_send_email_mock = {
            'status': 400
        }
        response_rpc_request_mock = {
            'body': {
                'Dispatch': dispatch_confirmed
            },
            'status': 200
        }

        expected_response = {
            'id': dispatch_number,
            'vendor': 'LIT'
        }

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            return_value=ticket_details_1_no_requested_watermark)
        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[response_rpc_request_mock])
        api_server_test._notifications_repository.send_email = CoroutineMock(side_effect=[response_send_email_mock])
        api_server_test._append_note_to_ticket = CoroutineMock()
        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])
        slack_msg = f"[dispatch-portal-backend] [LIT] Dispatch Cancel Requested by email [{dispatch_number}] " \
                    f"with ticket id: {ticket_id}"

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/lit/dispatch/{dispatch_number}/cancel')
            response_data = await response.get_json()

            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                'lit.dispatch.get', payload, timeout=30)
            api_server_test._notifications_repository.send_email.assert_awaited_once_with(email_data)
            api_server_test._append_note_to_ticket.assert_not_awaited()
            api_server_test._notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def lit_update_dispatch_test(self, api_server_test):
        uuid_ = 'UUID1'

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
                "Local_Time_of_Dispatch": "6PM-8PM",
                "Job_Site_Zip_Code": "99088",
                "Job_Site_Street": "123 Fake Street",
                "Job_Site_State": "CA",
                "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
                "Job_Site_City": "Pleasantown",
                "Job_Site": "test street",
                "Information_for_Tech": None,
                "Hard_Time_of_Dispatch_Time_Zone_Local": "Pacific Time",
                "Hard_Time_of_Dispatch_Local": "6PM-8PM",
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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

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
            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                "lit.dispatch.update", payload_request, timeout=30)

            assert response.status_code == HTTPStatus.OK
            assert data == expected_response_create

    @pytest.mark.asyncio
    async def lit_update_dispatch_error_from_lit_500_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

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
            api_server_test._event_bus.rpc_request.assert_awaited_once()

            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            assert data == expected_response_create

    @pytest.mark.asyncio
    async def lit_update_dispatch_with_no_dispatch_number_error_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

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
            api_server_test._event_bus.rpc_request.assert_not_awaited()

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_create

    @pytest.mark.asyncio
    async def lit_update_dispatch_validation_error_test(self, api_server_test):
        uuid_ = 'UUID1'

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
                "Hard_Time_of_Dispatch_Time_Zone_Local": "Pacific Time",
                "Hard_Time_of_Dispatch_Local": "6am-8am",
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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

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

        expected_response_create = {'code': 400, 'message': "'dispatch_number' is a required property"}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.patch(f'/lit/dispatch', json=payload_lit)
            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_not_awaited()

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_create

    @pytest.mark.asyncio
    async def lit_update_dispatch_not_body_response_error_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

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
            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                "lit.dispatch.update", payload_request, timeout=30)

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_create_error

    @pytest.mark.asyncio
    async def lit_upload_file_to_dispatch_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

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
            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                "lit.dispatch.upload.file", payload_request, timeout=300)

            assert response.status_code == HTTPStatus.OK
            assert data == expected_response_upload_file

    @pytest.mark.asyncio
    async def lit_upload_file_to_dispatch_no_file_name_in_header_error_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

        expected_response_upload_file = {'code': HTTPStatus.BAD_REQUEST, 'message': 'No `filename` in headers'}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            headers = {"Content-Type": "application/octet-stream", "NO_FILE_NAME": "test.txt"}
            response = await client.post(f'/lit/dispatch/{dispatch_number}/upload-file',
                                         data=b'test', headers=headers)

            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_not_awaited()

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_upload_file

    @pytest.mark.asyncio
    async def lit_upload_file_to_dispatch_no_correct_content_type_in_header_error_test(self,
                                                                                       api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

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
            api_server_test._event_bus.rpc_request.assert_not_awaited()

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_upload_file

    @pytest.mark.asyncio
    async def lit_upload_file_to_dispatch_empty_body_error_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

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
            api_server_test._event_bus.rpc_request.assert_not_awaited()

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_upload_file

    @pytest.mark.asyncio
    async def lit_upload_file_to_dispatch_large_content_length_body_error_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

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
            api_server_test._event_bus.rpc_request.assert_not_awaited()

            assert response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE
            assert data == expected_response_upload_file

    @pytest.mark.asyncio
    async def lit_upload_file_to_dispatch_general_exception_error_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=http_exception)

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
                api_server_test._event_bus.rpc_request.assert_not_awaited()

                assert response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE
                assert data == expected_response_upload_file
            except HTTPException as ex:
                assert ex.status_code == 413
                assert ex.description == 'Entity too large'

    @pytest.mark.asyncio
    async def lit_upload_file_to_dispatch_error_from_lit_500_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

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
            api_server_test._event_bus.rpc_request.assert_awaited_once()

            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            assert data == expected_response_upload_file

    @pytest.mark.asyncio
    async def lit_upload_file_to_dispatch_response_status_not_200_error_test(self, api_server_test):
        uuid_ = 'UUID1'

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

        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_lit)

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
            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                "lit.dispatch.upload.file", payload_request, timeout=300)

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert data == expected_response_upload_error

    @pytest.mark.asyncio
    async def cts_get_dispatch_test(self, api_server_test, cts_dispatch_mapped):
        uuid_ = 'UUID1'
        dispatch_number = 'S-147735'
        expected_response_mapped = cts_dispatch_mapped
        expected_response_cts = {
            "request_id": uuid_,
            "body": expected_response_mapped,
            "status": 200
        }
        cts_expected_response = {
            'id': 'S-147735',
            'vendor': "cts",
            'dispatch': expected_response_cts['body']['records'][0]
        }
        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_cts)

        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/cts/dispatch/{dispatch_number}')
            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", payload, timeout=30)

            assert response.status_code == HTTPStatus.OK
            assert data == cts_expected_response

    @pytest.mark.asyncio
    async def cts_get_dispatch_error_500_test(self, api_server_test, cts_dispatch_mapped):
        uuid_ = 'UUID1'
        dispatch_number = 'S-147735'
        expected_response_mapped = cts_dispatch_mapped
        expected_response_cts = {
            "request_id": uuid_,
            "body": "ERROR",
            "status": 500
        }
        cts_expected_response = {
            'code': 500,
            'message': "ERROR"
        }
        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_cts)

        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/cts/dispatch/{dispatch_number}')
            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", payload, timeout=30)

            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            assert data == cts_expected_response

    @pytest.mark.asyncio
    async def cts_get_dispatch_error_cts_salesforce_no_records_test(
            self, api_server_test, cts_dispatch_mapped_without_record):
        uuid_ = 'UUID1'
        dispatch_number = 'S-147735'
        expected_response_mapped_without_records = cts_dispatch_mapped_without_record
        expected_response_cts = {
            "request_id": uuid_,
            "body": expected_response_mapped_without_records,
            "status": 200
        }
        cts_expected_response = {
            'code': 200,
            'message': {'done': True}
        }
        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_cts)

        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/cts/dispatch/{dispatch_number}')
            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", payload, timeout=30)

            assert response.status_code == HTTPStatus.OK
            assert data == cts_expected_response

    @pytest.mark.asyncio
    async def cts_get_dispatch_error_cts_salesforce_done_false_test(
            self, api_server_test, cts_dispatch_mapped_without_done_false):
        uuid_ = 'UUID1'
        dispatch_number = 'S-147735'
        expected_response_mapped_done_false = cts_dispatch_mapped_without_done_false
        expected_response_cts = {
            "request_id": uuid_,
            "body": {'done': False, 'records': []},
            "status": 200
        }
        cts_expected_response = {
            'code': 200,
            'message': {'done': False, 'records': []}
        }
        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_cts)

        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/cts/dispatch/{dispatch_number}')
            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", payload, timeout=30)

            assert response.status_code == HTTPStatus.OK
            assert data == cts_expected_response

    @pytest.mark.asyncio
    async def cts_get_all_dispatches_test(self, api_server_test, cts_all_dispatches_mapped):
        uuid_ = 'UUID1'
        expected_response_cts = {
            "request_id": uuid_,
            "body": cts_all_dispatches_mapped,
            "status": 200
        }
        cts_expected_response = {
            'vendor': "cts",
            'list_dispatch': [expected_response_cts['body']['records'][0]]
        }
        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_cts)

        payload = {"request_id": uuid_, "body": {}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/cts/dispatch/')
            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", payload, timeout=30)

            assert response.status_code == HTTPStatus.OK
            assert data == cts_expected_response

    @pytest.mark.asyncio
    async def cts_get_all_dispatches_error_500_test(self, api_server_test):
        uuid_ = 'UUID1'
        expected_response_cts = {
            "request_id": uuid_,
            "body": "ERROR",
            "status": 500
        }
        cts_expected_response = {
            'code': 500,
            'message': "ERROR"
        }
        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_cts)

        payload = {"request_id": uuid_, "body": {}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/cts/dispatch/')
            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", payload, timeout=30)

            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            assert data == cts_expected_response

    @pytest.mark.asyncio
    async def cts_get_all_dispatches_cts_salesforce_no_records_test(
            self, api_server_test, cts_dispatch_mapped_without_record):
        uuid_ = 'UUID1'
        expected_response_cts = {
            "request_id": uuid_,
            "body": cts_dispatch_mapped_without_record,
            "status": 500
        }
        cts_expected_response = {
            'code': 500,
            'message': {'done': True}
        }
        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_cts)

        payload = {"request_id": uuid_, "body": {}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/cts/dispatch/')
            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", payload, timeout=30)

            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            assert data == cts_expected_response

    @pytest.mark.asyncio
    async def cts_get_all_dispatches_cts_salesforce_done_false_test(
            self, api_server_test, cts_dispatch_mapped_without_done_false):
        uuid_ = 'UUID1'
        expected_response_cts = {
            "request_id": uuid_,
            "body": cts_dispatch_mapped_without_done_false,
            "status": 200
        }
        cts_expected_response = {
            'code': 200,
            'message': {'done': False, 'records': []}
        }
        api_server_test._event_bus.rpc_request = CoroutineMock(return_value=expected_response_cts)

        payload = {"request_id": uuid_, "body": {}}

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/cts/dispatch/')
            data = await response.get_json()
            api_server_test._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", payload, timeout=30)

            assert response.status_code == HTTPStatus.OK
            assert data == cts_expected_response

    @pytest.mark.asyncio
    async def cts_create_dispatch_test(self, api_server_test, new_dispatch, ticket_details_1_no_requested_watermark):
        uuid_ = 'UUID1'
        igz_dispatch_id = f"IGZ{uuid_}"
        ticket_id = new_dispatch['mettel_bruin_ticket_id']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        payload = {"request_id": uuid_, "body": {}}
        cts_expected_response = {}
        cts_expected_response['id'] = igz_dispatch_id
        cts_expected_response['vendor'] = 'CTS'
        response_get_ticket_details_mock = ticket_details_1_no_requested_watermark

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=[response_get_ticket_details_mock])
        cts_body_mapped = cts_mapper.map_create_dispatch(new_dispatch)
        email_template = render_email_template(cts_body_mapped)
        email_html = f'<div>{email_template}</div>'
        email_data = {
            'request_id': uuid_,
            'email_data': {
                'subject': f'CTS - Service Submission - {ticket_id}',
                'recipient': api_server_test._config.CTS_CONFIG["email"],
                'text': 'this is the accessible text for the email',
                'html': email_html,
                'images': [],
                'attachments': []
            }
        }
        response_send_email_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_email = CoroutineMock(side_effect=[response_send_email_mock])
        api_server_test._append_note_to_ticket = CoroutineMock()
        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])
        slack_msg = f"[dispatch-portal-backend] [CTS] Dispatch Requested by email [{igz_dispatch_id}] " \
                    f"with ticket id: {ticket_id}"

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.post(f'/cts/dispatch/', json=new_dispatch)
            response_data = await response.get_json()

            api_server_test._bruin_repository.get_ticket_details.assert_awaited_once()
            api_server_test._notifications_repository.send_email.assert_awaited_once_with(email_data)
            api_server_test._append_note_to_ticket.assert_awaited_once()
            api_server_test._notifications_repository.send_slack_message.assert_awaited_with(slack_msg)

            assert response_data == cts_expected_response

    @pytest.mark.asyncio
    async def cts_create_dispatch_error_validation_test(self, api_server_test, new_dispatch_validation_error):
        uuid_ = 'UUID1'
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        validation_error_msg = "'date_of_dispatch' is a required property"
        cts_expected_response = {
            'code': 400,
            'message': validation_error_msg
        }

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.post(f'/cts/dispatch/', json=new_dispatch_validation_error)
            response_data = await response.get_json()

            assert response_data == cts_expected_response

    @pytest.mark.asyncio
    async def cts_create_dispatch_error_could_not_retrieve_ticket_test(
            self, api_server_test, new_dispatch, ticket_details_2_error):
        uuid_ = 'UUID1'
        igz_dispatch_id = f"IGZ{uuid_}"
        ticket_id = new_dispatch['mettel_bruin_ticket_id']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        err_msg = f"[CTS] Error: could not retrieve ticket [{ticket_id}] details"
        cts_expected_response = {
            'status': 400,
            'body': err_msg
        }

        response_get_ticket_details_mock = ticket_details_2_error

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=[response_get_ticket_details_mock])

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.post(f'/cts/dispatch/', json=new_dispatch)
            response_data = await response.get_json()

            api_server_test._bruin_repository.get_ticket_details.assert_awaited_once()
            assert response_data == cts_expected_response

    @pytest.mark.asyncio
    async def cts_create_dispatch_error_send_email_test(
            self, api_server_test, new_dispatch, ticket_details_1_no_requested_watermark):
        uuid_ = 'UUID1'
        igz_dispatch_id = f"IGZ{uuid_}"
        ticket_id = new_dispatch['mettel_bruin_ticket_id']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        cts_expected_response = {
            'code': 400,
            'message': f'[CTS] An error ocurred sending the email for ticket id: {ticket_id}'
        }

        response_get_ticket_details_mock = ticket_details_1_no_requested_watermark

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=[response_get_ticket_details_mock])
        cts_body_mapped = cts_mapper.map_create_dispatch(new_dispatch)
        email_template = render_email_template(cts_body_mapped)
        email_html = f'<div>{email_template}</div>'
        email_data = {
            'request_id': uuid_,
            'email_data': {
                'subject': f'CTS - Service Submission - {ticket_id}',
                'recipient': api_server_test._config.CTS_CONFIG["email"],
                'text': 'this is the accessible text for the email',
                'html': email_html,
                'images': [],
                'attachments': []
            }
        }
        response_send_email_mock = {
            'status': 400
        }
        api_server_test._notifications_repository.send_email = CoroutineMock(side_effect=[response_send_email_mock])

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.post(f'/cts/dispatch/', json=new_dispatch)
            response_data = await response.get_json()

            api_server_test._bruin_repository.get_ticket_details.assert_awaited_once()
            api_server_test._notifications_repository.send_email.assert_awaited_once_with(email_data)

            assert response_data == cts_expected_response

    @pytest.mark.asyncio
    async def cts_cancel_dispatch_test(
            self, api_server_test, cts_dispatch, cts_ticket_details_1_no_requested_watermark):
        uuid_ = 'UUID1'
        igz_dispatch_number = 'IGZ001'
        dispatch = cts_dispatch["records"][0]
        dispatch_number = dispatch['Name']
        ticket_id = dispatch['Ext_Ref_Num__c']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}
        body = {
            'dispatch_number': dispatch_number,
            'ticket_id': ticket_id
        }
        email_template = render_cancel_email_template(body)
        email_html = f'<div>{email_template}</div>'
        email_data = {
            'request_id': uuid_,
            'email_data': {
                'subject': f'CTS - Service Submission - {ticket_id}',
                'recipient': api_server_test._config.CTS_CONFIG["email"],
                'text': 'this is the accessible text for the email',
                'html': email_html,
                'images': [],
                'attachments': []
            }
        }
        response_send_email_mock = {
            'status': 200
        }
        response_rpc_request_mock = {
            'body': cts_dispatch,
            'status': 200
        }

        expected_response = {
            'id': dispatch_number,
            'vendor': 'CTS'
        }

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            return_value=cts_ticket_details_1_no_requested_watermark)
        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[response_rpc_request_mock])
        api_server_test._notifications_repository.send_email = CoroutineMock(side_effect=[response_send_email_mock])
        api_server_test._append_note_to_ticket = CoroutineMock()
        api_server_test._get_igz_dispatch_number = CoroutineMock(return_value='IGZ001')
        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])
        slack_msg = f"[dispatch-portal-backend] [CTS] Dispatch Cancel Requested by email " \
                    f"[{dispatch_number}] [{igz_dispatch_number}] " \
                    f"with ticket id: {ticket_id}"

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/cts/dispatch/{dispatch_number}/cancel')
            response_data = await response.get_json()

            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                'cts.dispatch.get', payload, timeout=30)
            api_server_test._notifications_repository.send_email.assert_awaited_once_with(email_data)
            api_server_test._append_note_to_ticket.assert_awaited_once()
            api_server_test._notifications_repository.send_slack_message.assert_awaited_with(slack_msg)
            assert response_data == expected_response

    @pytest.mark.asyncio
    async def cts_cancel_dispatch_error_could_not_retrieve_dispatch_test(
            self, api_server_test, cts_dispatch, cts_ticket_details_1_no_requested_watermark):
        uuid_ = 'UUID1'
        dispatch = cts_dispatch["records"][0]
        dispatch_number = dispatch['Name']
        ticket_id = dispatch['Ext_Ref_Num__c']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}
        body = {
            'dispatch_number': dispatch_number,
            'ticket_id': ticket_id
        }
        email_template = render_cancel_email_template(body)
        email_html = f'<div>{email_template}</div>'
        email_data = {
            'request_id': uuid_,
            'email_data': {
                'subject': f'CTS - Service Submission - {ticket_id}',
                'recipient': api_server_test._config.CTS_CONFIG["email"],
                'text': 'this is the accessible text for the email',
                'html': email_html,
                'images': [],
                'attachments': []
            }
        }
        response_send_email_mock = {
            'status': 200
        }
        response_rpc_request_mock = {
            'body': {},
            'status': 500
        }

        expected_response = {
            'id': dispatch_number,
            'vendor': 'CTS'
        }

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            return_value=cts_ticket_details_1_no_requested_watermark)
        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[response_rpc_request_mock])
        api_server_test._notifications_repository.send_email = CoroutineMock(side_effect=[response_send_email_mock])
        api_server_test._append_note_to_ticket = CoroutineMock()
        api_server_test._get_igz_dispatch_number = CoroutineMock(return_value='IGZ001')
        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])
        slack_msg = f"[dispatch-portal-backend] [CTS] Dispatch Cancel Requested by email [{dispatch_number}] " \
                    f"with ticket id: {ticket_id}"

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/cts/dispatch/{dispatch_number}/cancel')
            response_data = await response.get_json()
            assert response_data['code'] == 500
            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                'cts.dispatch.get', payload, timeout=30)
            api_server_test._notifications_repository.send_email.assert_not_awaited()
            api_server_test._append_note_to_ticket.assert_not_awaited()
            api_server_test._notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def cts_cancel_dispatch_error_retrieve_valid_dispatch_test(
            self, api_server_test, cts_dispatch, cts_ticket_details_1_no_requested_watermark):
        uuid_ = 'UUID1'
        dispatch = cts_dispatch["records"][0]
        dispatch_number = dispatch['Name']
        ticket_id = dispatch['Ext_Ref_Num__c']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}
        body = {
            'dispatch_number': dispatch_number,
            'ticket_id': ticket_id
        }
        email_template = render_cancel_email_template(body)
        email_html = f'<div>{email_template}</div>'
        email_data = {
            'request_id': uuid_,
            'email_data': {
                'subject': f'CTS - Service Submission - {ticket_id}',
                'recipient': api_server_test._config.CTS_CONFIG["email"],
                'text': 'this is the accessible text for the email',
                'html': email_html,
                'images': [],
                'attachments': []
            }
        }
        response_send_email_mock = {
            'status': 200
        }
        response_rpc_request_mock = {
            'body': {
                "done": True,
                "records": None
            },
            'status': 200
        }

        expected_response = {
            'id': dispatch_number,
            'vendor': 'CTS'
        }

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            return_value=cts_ticket_details_1_no_requested_watermark)
        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[response_rpc_request_mock])
        api_server_test._notifications_repository.send_email = CoroutineMock(side_effect=[response_send_email_mock])
        api_server_test._append_note_to_ticket = CoroutineMock()
        api_server_test._get_igz_dispatch_number = CoroutineMock(return_value='IGZ001')
        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])
        slack_msg = f"[dispatch-portal-backend] [CTS] Dispatch Cancel Requested by email [{dispatch_number}] " \
                    f"with ticket id: {ticket_id}"

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/cts/dispatch/{dispatch_number}/cancel')
            response_data = await response.get_json()
            assert response_data['code'] == 200
            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                'cts.dispatch.get', payload, timeout=30)
            api_server_test._notifications_repository.send_email.assert_not_awaited()
            api_server_test._append_note_to_ticket.assert_not_awaited()
            api_server_test._notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def cts_cancel_dispatch_with_error_getting_ticket_details_test(
            self, api_server_test, cts_dispatch, cts_ticket_details_1_error):
        uuid_ = 'UUID1'
        igz_dispatch_number = 'IGZ001'
        dispatch = cts_dispatch["records"][0]
        dispatch_number = dispatch['Name']
        ticket_id = dispatch['Ext_Ref_Num__c']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}

        response_send_email_mock = {
            'status': 200
        }
        response_rpc_request_mock = {
            'body': cts_dispatch,
            'status': 200
        }

        expected_response = {
            'body': f"[CTS] Error: could not retrieve ticket [{ticket_id}] details",
            'status': 400
        }

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            return_value=cts_ticket_details_1_error)
        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[response_rpc_request_mock])
        api_server_test._notifications_repository.send_email = CoroutineMock(side_effect=[response_send_email_mock])
        api_server_test._append_note_to_ticket = CoroutineMock()
        api_server_test._get_igz_dispatch_number = CoroutineMock(return_value='IGZ001')
        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/cts/dispatch/{dispatch_number}/cancel')
            response_data = await response.get_json()

            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                'cts.dispatch.get', payload, timeout=30)
            api_server_test._notifications_repository.send_email.assert_not_awaited()
            api_server_test._append_note_to_ticket.assert_not_awaited()
            assert response_data == expected_response

    @pytest.mark.asyncio
    async def cts_cancel_dispatch_with_existing_cancel_watermark_test(
            self, api_server_test, cts_dispatch, cts_ticket_details_1_with_cancel_requested_watermark):
        uuid_ = 'UUID1'
        igz_dispatch_number = 'IGZ001'
        dispatch = cts_dispatch["records"][0]
        dispatch_number = dispatch['Name']
        ticket_id = dispatch['Ext_Ref_Num__c']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}

        response_send_email_mock = {
            'status': 200
        }
        response_rpc_request_mock = {
            'body': cts_dispatch,
            'status': 200
        }

        expected_response = {
            'id': dispatch_number,
            'vendor': 'CTS'
        }

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            return_value=cts_ticket_details_1_with_cancel_requested_watermark)
        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[response_rpc_request_mock])
        api_server_test._notifications_repository.send_email = CoroutineMock(side_effect=[response_send_email_mock])
        api_server_test._append_note_to_ticket = CoroutineMock()
        api_server_test._get_igz_dispatch_number = CoroutineMock(return_value='IGZ001')
        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/cts/dispatch/{dispatch_number}/cancel')
            response_data = await response.get_json()

            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                'cts.dispatch.get', payload, timeout=30)
            api_server_test._notifications_repository.send_email.assert_not_awaited()
            api_server_test._append_note_to_ticket.assert_not_awaited()
            assert response_data == expected_response

    @pytest.mark.asyncio
    async def cts_cancel_dispatch_error_send_email_test(
            self, api_server_test, cts_dispatch, cts_ticket_details_1_no_requested_watermark):
        uuid_ = 'UUID1'
        dispatch = cts_dispatch["records"][0]
        dispatch_number = dispatch['Name']
        ticket_id = dispatch['Ext_Ref_Num__c']
        api_server_test._config.ENVIRONMENT_NAME = 'production'
        payload = {"request_id": uuid_, "body": {"dispatch_number": dispatch_number}}
        body = {
            'dispatch_number': dispatch_number,
            'ticket_id': ticket_id
        }
        email_template = render_cancel_email_template(body)
        email_html = f'<div>{email_template}</div>'
        email_data = {
            'request_id': uuid_,
            'email_data': {
                'subject': f'CTS - Service Submission - {ticket_id}',
                'recipient': api_server_test._config.CTS_CONFIG["email"],
                'text': 'this is the accessible text for the email',
                'html': email_html,
                'images': [],
                'attachments': []
            }
        }
        response_send_email_mock = {
            'status': 400
        }
        response_rpc_request_mock = {
            'body': cts_dispatch,
            'status': 200
        }

        expected_response = {
            'id': dispatch_number,
            'vendor': 'CTS'
        }

        api_server_test._bruin_repository.get_ticket_details = CoroutineMock(
            return_value=cts_ticket_details_1_no_requested_watermark)
        api_server_test._event_bus.rpc_request = CoroutineMock(side_effect=[response_rpc_request_mock])
        api_server_test._notifications_repository.send_email = CoroutineMock(side_effect=[response_send_email_mock])
        api_server_test._append_note_to_ticket = CoroutineMock()
        api_server_test._get_igz_dispatch_number = CoroutineMock(return_value='IGZ001')
        response_send_slack_message_mock = {
            'status': 200
        }
        api_server_test._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=[response_send_slack_message_mock])
        slack_msg = f"[dispatch-portal-backend] [CTS] Dispatch Cancel Requested by email [{dispatch_number}] " \
                    f"with ticket id: {ticket_id}"

        with patch.object(api_server_module, 'uuid', return_value=uuid_):
            client = api_server_test._app.test_client()
            response = await client.get(f'/cts/dispatch/{dispatch_number}/cancel')
            response_data = await response.get_json()

            api_server_test._event_bus.rpc_request.assert_awaited_once_with(
                'cts.dispatch.get', payload, timeout=30)
            api_server_test._notifications_repository.send_email.assert_awaited_once_with(email_data)
            api_server_test._append_note_to_ticket.assert_not_awaited()
            api_server_test._notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_note_to_ticket_test(self, api_server_test, big_ticket_note):
        igz_dispatch_id = 'IGZ_XXX'
        ticket_id = '12345'

        note_1 = 'A' * 1500
        note_2 = 'B' * 1500

        response_note_1_mock = {
            'body': note_1,
            'status': 200
        }

        response_note_2_mock = {
            'body': note_2,
            'status': 400
        }
        api_server_test._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[
                response_note_1_mock,
                response_note_2_mock,
            ]
        )

        await api_server_test._append_note_to_ticket(igz_dispatch_id, ticket_id, big_ticket_note)

        api_server_test._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id, note_1),
            call(ticket_id, note_2)
        ])

    @pytest.mark.asyncio
    async def get_igz_dispatch_number_test(self, api_server_test, cts_ticket_details_1, cts_ticket_details_2):
        ticket_notes_1 = cts_ticket_details_1['body'].get('ticketNotes', [])
        ticket_notes_2 = cts_ticket_details_2['body'].get('ticketNotes', [])
        response_1 = await api_server_test._get_igz_dispatch_number(ticket_notes_1)
        response_2 = await api_server_test._get_igz_dispatch_number(ticket_notes_2)
        assert response_1 == 'IGZ_0001'
        assert response_2 == ''
