from unittest.mock import Mock

import pytest
from asynctest import CoroutineMock

from application.actions.create_dispatch import CreateDispatch
from application.actions.get_dispatch import GetDispatch
from application.actions.update_dispatch import UpdateDispatch
from application.actions.upload_file import UploadFile
from application.repositories.lit_repository import LitRepository
from application.clients.lit_client import LitClient
from config import testconfig as config


# Scopes
# - function
# - module
# - session

@pytest.fixture(scope='function')
def mock_lit_repository():
    lit_repository = Mock()
    return lit_repository


@pytest.fixture(scope='function')
def mock_logger():
    logger = Mock()
    return logger


@pytest.fixture(scope='function')
def mock_event_bus():
    event_bus = Mock()
    return event_bus


@pytest.fixture(scope='function')
def mock_lit_client():
    lit_client = Mock()
    return lit_client


@pytest.fixture(scope='function')
def redis_client():
    _redis_client = Mock()
    return _redis_client


@pytest.fixture(scope='function')
def instance_dispatch(mock_logger, mock_event_bus, mock_lit_repository):
    mock_event_bus.publish_message = CoroutineMock()
    return CreateDispatch(mock_logger, config, mock_event_bus, mock_lit_repository)


@pytest.fixture(scope='function')
def instance_get_dispatch(mock_logger, mock_event_bus, mock_lit_repository):
    mock_lit_repository.get_dispatch = Mock()
    mock_event_bus.publish_message = CoroutineMock()
    return GetDispatch(mock_logger, config, mock_event_bus, mock_lit_repository)


@pytest.fixture(scope='function')
def instance_update_dispatch(mock_logger, mock_event_bus, mock_lit_repository):
    mock_event_bus.publish_message = CoroutineMock()
    return UpdateDispatch(mock_logger, config, mock_event_bus, mock_lit_repository)


@pytest.fixture(scope='function')
def instance_upload_dispatch(mock_logger, mock_event_bus, mock_lit_repository):
    mock_event_bus.publish_message = CoroutineMock()
    return UploadFile(mock_logger, config, mock_event_bus, mock_lit_repository)


@pytest.fixture(scope='function')
def instance_lit_repository(mock_lit_client, mock_logger, redis_client):
    scheduler = Mock()
    return LitRepository(mock_lit_client, mock_logger, scheduler, config, redis_client)


@pytest.fixture(scope='function')
def instance_lit_client(mock_logger, mock_lit_client):
    mock_logger.error = Mock()
    mock_lit_client = LitClient(mock_logger, config)
    mock_lit_client._bearer_token = "Someverysecretaccesstoken"
    mock_lit_client._base_url = "https://cs66.salesforce.com"
    mock_lit_client._salesforce_sdk = Mock()
    return mock_lit_client


@pytest.fixture(scope='function')
def dispatch():
    return {
        "RequestDispatch": {
            "Date_of_Dispatch": "2016-11-16",
            "MetTel_Bruin_TicketID": "D123",
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


@pytest.fixture(scope='function')
def required_dispatch_keys():
    return ["date_of_dispatch", "mettel_bruin_ticketid", "site_survey_quote_required",
            "local_time_of_dispatch", "time_zone_local",
            "job_site", "job_site_street",
            "job_site_city", "job_site_state", "job_site_zip_code",
            "job_site_contact_name_and_phone_number", "special_materials_needed_for_dispatch",
            "scope_of_work", "mettel_tech_call_in_instructions", "name_of_mettel_requester",
            "mettel_department", "mettel_requester_email", "mettel_department_phone_number"]


@pytest.fixture(scope='function')
def msg():
    return {
        'request_id': '123',
        'response_topic': 'some.response.topic',
        'body': 'test'
    }


@pytest.fixture(scope='function')
def return_msg():
    return {
        'request_id': '123',
        'status': 'test',
        'body': 'test'
    }
