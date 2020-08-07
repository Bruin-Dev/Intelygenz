import copy
from unittest.mock import Mock

import pytest
from unittest import mock

from application.clients.cts_client import CtsClient
from application.repositories.cts_repository import CtsRepository

from asynctest import CoroutineMock

from config import testconfig


# Scopes
# - function
# - module
# - session

@pytest.fixture(scope='function')
def cts_client():
    logger = Mock()
    config = testconfig
    client = CtsClient(logger, config)
    return client


@pytest.fixture(scope='function')
def cts_repository(cts_client):
    # cts_client, logger, scheduler, config
    logger = Mock()
    scheduler = Mock()
    config = testconfig
    redis_client = Mock()

    repository = CtsRepository(cts_client, logger, scheduler, config, redis_client)
    return repository


@pytest.fixture(scope='function')
def dispatch_required_keys():
    dispatch_required_keys = ['date_of_dispatch', 'site_survey_quote_required', 'time_of_dispatch', 'time_zone',
                              'mettel_bruin_ticket_id', 'sla_level', 'location_country', 'job_site',
                              'job_site_street_1', 'job_site_city', 'job_site_state',
                              'job_site_zip_code', 'job_site_contact_name', 'job_site_contact_lastname',
                              'job_site_contact_number', 'materials_needed_for_dispatch', 'scope_of_work',
                              'mettel_tech_call_in_instructions', 'service_type', 'name_of_mettel_requester',
                              'lastname_of_mettel_requester', 'mettel_department', 'mettel_requester_email',
                              'mettel_department_phone_number']
    return dispatch_required_keys


@pytest.fixture(scope='function')
def new_dispatch():
    return {
        "date_of_dispatch": "2019-11-14",
        "site_survey_quote_required": False,
        "time_of_dispatch": "6PM-8PM",
        "time_zone": "Pacific Time",
        "mettel_bruin_ticket_id": "123456",
        "sla_level": "Pre-planned",
        "location_country": "United States",
        "job_site": "Red Rose Inn",
        "job_site_street_1": "123 Fake Street",
        "job_site_street_2": "123 Fake Street",
        "job_site_city": "Pleasantown",
        "job_site_state": "CA",
        "job_site_zip_code": "99088",
        "job_site_contact_name": "Jane",
        "job_site_contact_lastname": "Doe",
        "job_site_contact_number": "+1 666 6666 666",
        "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
        "scope_of_work": "Device is bouncing constantly",
        "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
        "service_type": "Troubleshooting",
        "name_of_mettel_requester": "Karen",
        "lastname_of_mettel_requester": "Doe",
        "mettel_department": "Customer Care",
        "mettel_requester_email": "karen.doe@mettel.net",
        "mettel_department_phone_number": "+1 666 6666 666"
    }


@pytest.fixture(scope='function')
def cts_dispatch():
    return {
        'attributes': {
            'type': 'Service__c',
            'url': '/services/data/v42.0/sobjects/Service__c/a261C000003V0UAQA0'
        },
        'Id': 'a261C000003V0UAQA0',
        'Name': 'S-12345',
        'API_Resource_Name__c': 'Geppert, Nicholas',
        'Billing_Invoice_Date__c': None,
        'Billing_Invoice_Number__c': None,
        'Billing_Total__c': 0.0,
        'Carrier__c': None,
        'Carrier_ID_Num__c': None,
        'Check_In_Date__c': None,
        'Check_Out_Date__c': None,
        'City__c': 'Washington',
        'Confirmed__c': False,
        'Country__c': 'United States',
        'Description__c': "Onsite Time Needed: Jun 22, 2020 03:00 PM\r\n\r\nReference: 4694961\r\n\r\n"
                          "SLA Level: 4-Hour\r\n\r\nLocation Country: United States\r\n\r\n"
                          "Location - US: 1501 K St NW\r\nWashington, DC 20005\r\n\r\n"
                          "Location ID: 88377\r\n\r\nLocation Owner: Premier Financial Bancorp\r\n\r\n"
                          "Onsite Contact: Manager On Duty\r\n\r\nContact #: (202) 772-3610\r\n\r\n"
                          "Failure Experienced: Comcast cable internet circuit is down. "
                          "Comcast shows the modem offline without cause.\r\n"
                          "Basic troubleshooting already done including power cycling of the VCE and modem. "
                          "Client added it's showing red led on the VCE cloud.\r\n"
                          "Need to check the cabling and check out the Velo device and see if it needs replaced."
                          "\r\n\r\nStatic IP Address 50.211.140.109\r\nStatic IP Block 50.211.140.108/30\r\n"
                          "Gateway IP 50.211.140.110\r\nSubnet Mask 255.255.255.252\r\nPrimary DNS 75.75.75.75\r\n"
                          "Secondary DNS 75.75.76.76\r\n\r\n\r\n"
                          "Onsite SOW: phone # 877-515-0911 and email address for pictures to be sent to "
                          "T1repair@mettel.net\r\n\r\nLCON: Mgr on Duty\r\n"
                          "Phone: (202) 772-3610\r\nAcccess: M-F 9AM-5PM\r\n\r\n"
                          "Materials Needed: Laptop, Ethernet cable, console cable, Jetpack/Mobile Hotspot, "
                          "TeamViewer installed, other IW tools (CAT5e, punch down, wall jacks, "
                          "telecom standard toolkit)\r\n\r\n"
                          "Service Category: Troubleshoot\r\n\r\nName: Brad Gunnell\r\n\r\n"
                          "Phone: (877) 515-0911\r\n\r\nEmail: t1repair@mettel.net",
        'Duration_Onsite__c': 0.6,
        'Early_Start__c': None,
        'Ext_Ref_Num__c': '4694961',
        'Finance_Notes__c': None,
        'Issue_Summary__c': 'Troubleshoot Modem/Check Cabling',
        'Lift_Delivery_Date__c': None,
        'Lift_Release_Date__c': None,
        'Lift_Vendor__c': None,
        'Local_Site_Time__c': '2020-06-23T13:00:00.000+0000',
        'Account__c': '0011C00002oFpvIQAS',
        'Lookup_Location_Owner__c': 'Premier Financial Bancorp',
        'On_Site_Elapsed_Time__c': '0 Days 0 Hours 36 Minutes',
        'On_Time_Auto__c': False,
        'Open_Date__c': '2020-06-22T20:14:00.000+0000',
        'P1__c': None, 'P10__c': None, 'P10A__c': None, 'P11__c': None, 'P11A__c': None, 'P12__c': None,
        'P12A__c': None, 'P13__c': None, 'P13A__c': None, 'P14__c': None, 'P14A__c': None, 'P15__c': None,
        'P15A__c': None, 'P1A__c': None, 'P2__c': None, 'P2A__c': None, 'P3__c': None, 'P3A__c': None,
        'P4__c': None, 'P4A__c': None, 'P5__c': None, 'P5A__c': None, 'P6__c': None, 'P6A__c': None,
        'P7__c': None, 'P7A__c': None, 'P8__c': None, 'P8A__c': None, 'P9__c': None, 'P9A__c': None,
        'Resource_Assigned_Timestamp__c': None,
        'Resource_Email__c': None,
        'Resource_Phone_Number__c': None,
        'Site_Notes__c': None,
        'Site_Status__c': 'Requires Dispatch',
        'Special_Shipping_Instructions__c': None,
        'Street__c': '1501 K St NW',
        'Status__c': 'Open',
        'Resource_Trained__c': False,
        'Service_Type__c': 'a251C000005Ics1QAC',
        'Zip__c': '20005'
    }


@pytest.fixture(scope='function')
def cts_dispatch_2(cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch)
    updated_dispatch['Name'] = 'S-12346'
    updated_dispatch['Ext_Ref_Num__c'] = '4694962'
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_1(cts_repository, cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch)
    updated_dispatch['Resource_Assigned_Timestamp__c'] = '2020-06-22T22:44:32.000+0000'
    updated_dispatch['Status__c'] = cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['API_Resource_Name__c'] = 'Michael J. Fox'
    updated_dispatch['Resource_Phone_Number__c'] = '+1 (212) 359-5129'
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_2(cts_repository, cts_dispatch_2):
    updated_dispatch = copy.deepcopy(cts_dispatch_2)
    updated_dispatch['Resource_Assigned_Timestamp__c'] = '2020-06-22T22:44:32.000+0000'
    updated_dispatch['Status__c'] = cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['API_Resource_Name__c'] = 'Michael J. Fox'
    updated_dispatch['Resource_Phone_Number__c'] = '+1 (212) 359-5129'
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_all_dispatches_response(cts_dispatch_confirmed_1, cts_dispatch_confirmed_2):
    return {
        "done": True,
        "records": [
            cts_dispatch_confirmed_1,
            cts_dispatch_confirmed_2,
        ]
    }
