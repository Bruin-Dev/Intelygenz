from unittest.mock import Mock

import pytest
from application.actions.create_dispatch import CreateDispatch
from asynctest import CoroutineMock

from config import testconfig as config


class TestCreateDispatch:

    def instance_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        cts_repo = Mock()

        create_dispatch = CreateDispatch(logger, configs, event_bus, cts_repo)

        assert create_dispatch._config == configs
        assert create_dispatch._logger == logger
        assert create_dispatch._event_bus == event_bus
        assert create_dispatch._cts_repository == cts_repo

    @pytest.mark.asyncio
    async def create_dispatch_200_ok_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        return_body = {'Dispatch': {'Dispatch_Number': 123}}
        return_status = 200
        create_dispatch_return = {'body': return_body, 'status': return_status}
        cts_repo = Mock()
        cts_repo.create_dispatch = Mock(return_value=create_dispatch_return)

        dipatch_contents = {
            "RequestDispatch": {
                "Date_of_Dispatch": "2016-11-16",
                "MetTel_Bruin_TicketID": 145,
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
        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': dipatch_contents
        }
        expected_return = {
            'request_id': request_id,
            'body': return_body,
            'status': return_status
        }
        create_dispatch_action = CreateDispatch(logger, configs, event_bus, cts_repo)
        await create_dispatch_action.create_dispatch(msg)

        cts_repo.create_dispatch.assert_called_once_with(dipatch_contents)
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def create_dispatch_400_ok_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        return_body = {'status': 'Error'}
        return_status = 400
        create_dispatch_return = {'body': return_body, 'status': return_status}
        cts_repo = Mock()
        cts_repo.create_dispatch = Mock(return_value=create_dispatch_return)

        dipatch_contents = {
            "RequestDispatch": {
                "Date_of_Dispatch": "2016-11-16",
                "MetTel_Bruin_TicketID": 145,
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
        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
                'request_id': request_id,
                'response_topic': response_topic,
                'body': dipatch_contents
        }
        expected_return = {
                            'request_id': request_id,
                            'body': return_body,
                            'status': return_status

        }
        create_dispatch_action = CreateDispatch(logger, configs, event_bus, cts_repo)
        await create_dispatch_action.create_dispatch(msg)

        cts_repo.create_dispatch.assert_called_once_with(dipatch_contents)
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def create_dispatch_missing_keys_ko_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        cts_repo = Mock()

        dipatch_contents = {
            "RequestDispatch": {
                "Special_Materials_Needed_for_Dispatch": "test"
            }
        }
        dispatch_required_keys = ["date_of_dispatch", "mettel_bruin_ticketid", "site_survey_quote_required",
                                  "local_time_of_dispatch", "time_zone_local", "job_site", "job_site_street",
                                  "job_site_city", "job_site_state", "job_site_zip_code",
                                  "job_site_contact_name_and_phone_number", "special_materials_needed_for_dispatch",
                                  "scope_of_work", "mettel_tech_call_in_instructions", "name_of_mettel_requester",
                                  "mettel_department", "mettel_requester_email"]

        request_id = '123'
        response_topic = 'some.response.topic'

        msg = {
                'request_id': request_id,
                'response_topic': response_topic,
                'body': dipatch_contents
        }

        expected_return = {
                            'request_id': request_id,
                            'body': f'Must include the following keys in request: {dispatch_required_keys}',
                            'status': 400

        }
        create_dispatch_action = CreateDispatch(logger, configs, event_bus, cts_repo)
        await create_dispatch_action.create_dispatch(msg)

        cts_repo.create_dispatch.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def create_dispatch_missing_request_dispatch_ko_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        cts_repo = Mock()

        request_id = '123'
        response_topic = 'some.response.topic'

        msg = {
                'request_id': request_id,
                'response_topic': response_topic,
                'body': {}
        }

        expected_return = {
                            'request_id': request_id,
                            'body': 'Must include "RequestDispatch" in request',
                            'status': 400

        }
        create_dispatch_action = CreateDispatch(logger, configs, event_bus, cts_repo)
        await create_dispatch_action.create_dispatch(msg)

        cts_repo.create_dispatch.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def create_dispatch_missing_body_ko_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        cts_repo = Mock()

        request_id = '123'
        response_topic = 'some.response.topic'

        msg = {
                'request_id': request_id,
                'response_topic': response_topic,
        }

        expected_return = {
                            'request_id': request_id,
                            'body': 'Must include "body" in request',
                            'status': 400

        }
        create_dispatch_action = CreateDispatch(logger, configs, event_bus, cts_repo)
        await create_dispatch_action.create_dispatch(msg)

        cts_repo.create_dispatch.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)
