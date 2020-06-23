import copy
from unittest.mock import Mock

import pytest
from unittest import mock

from asynctest import CoroutineMock

from application.server.api_server import DispatchServer
from config import testconfig


# Scopes
# - function
# - module
# - session


@pytest.fixture(scope='function')
def api_server_test():
    redis_client = Mock()
    event_bus = Mock()
    logger = Mock()
    config = testconfig
    bruin_repository = Mock()
    notifications_repository = Mock()
    return DispatchServer(config, redis_client, event_bus, logger, bruin_repository, notifications_repository)


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
        "done": True,
        "records": [{
            'attributes': {
                'type': 'Service__c',
                'url': '/services/data/v42.0/sobjects/Service__c/a260n000000dXywAAE'
            },
            'Id': 'a260n000000dXywAAE',
            'Name': 'S-147735',
            'Billing_Invoice_Date__c': None,
            'Billing_Invoice_Number__c': None,
            'Billing_Total__c': 0.0,
            'Carrier__c': None,
            'Carrier_ID_Num__c': None,
            'Check_In_Date__c': None,
            'Check_Out_Date__c': None,
            'City__c': 'San Francisco',
            'Confirmed__c': False,
            'Country__c': None,
            'Description__c': 'Onsite Time Needed: 2020-06-21 4:00PM\r\nOnsite Timezone: Pacific Time\r\n'
                              'Reference: 4680743\r\nSLA Level: 4-hour\r\nLocation Country: United States\r\n'
                              'Location: Hayes Valley Inn, San Francisco, CA, 94102\r\n\r\n'
                              'Location ID: Test Location\r\nLocation Owner: Hayes Valley Inn\r\n'
                              'Onsite Contact: John Smith\r\nContact #: +1 555 888 3333\r\n'
                              'Failure Experienced: TEST Device is bouncing constantly\r\n'
                              'Onsite SOW: This is a TEST\r\n'
                              'Materials Needed: Laptop, cable, tuner, ladder, internet hotspot\r\n'
                              'Service Category: Part Replacement\r\nName: Karen Doe\r\nPhone: +1 666 666 6666\r\n'
                              'Email: karen.doe@mettel.net',
            'Duration_Onsite__c': None,
            'Early_Start__c': '2020-06-21T23:00:00.000+0000',
            'Ext_Ref_Num__c': '4680743',
            'Finance_Notes__c': None,
            'Issue_Summary__c': 'TEST Device is bouncing constantly',
            'Lift_Delivery_Date__c': None,
            'Lift_Release_Date__c': None,
            'Lift_Vendor__c': None,
            'Local_Site_Time__c': '2020-06-21T20:00:00.000+0000',
            'Account__c': '0010n000017rOa2AAE',
            'Lookup_Location_Owner__c': 'Hayes Valley Inn',
            'On_Site_Elapsed_Time__c': 'Days  Hours  Minutes',
            'On_Time_Auto__c': False,
            'Open_Date__c': '2020-06-19T18:26:00.000+0000',
            'P1__c': None, 'P10__c': None, 'P10A__c': None, 'P11__c': None, 'P11A__c': None, 'P12__c': None,
            'P12A__c': None, 'P13__c': None, 'P13A__c': None, 'P14__c': None, 'P14A__c': None, 'P15__c': None,
            'P15A__c': None, 'P1A__c': None, 'P2__c': None, 'P2A__c': None, 'P3__c': None, 'P3A__c': None,
            'P4__c': None, 'P4A__c': None, 'P5__c': None, 'P5A__c': None, 'P6__c': None, 'P6A__c': None, 'P7__c': None,
            'P7A__c': None, 'P8__c': None, 'P8A__c': None, 'P9__c': None, 'P9A__c': None,
            'Parent_Account_Associated__c': 'Mettel',
            'Service_Order__c': 'a200n000000hKPNAA2',
            'Project_Name__c': 'Sevice Requests',
            'Location__c': None,
            'Release_Number__c': 'R-1920-134925',
            'Resource__c': None,
            'Resource_Assigned_Timestamp__c': None,
            'Resource_Email__c': None,
            'Resource_Phone_Number__c': None,
            'Site_Notes__c': None,
            'Site_Status__c': None,
            'Special_Shipping_Instructions__c': None,
            'State__c': 'CA',
            'Street__c': '1234 Test Drive',
            'Status__c': 'Requires Dispatch',
            'Resource_Trained__c': False,
            'Service_Type__c': 'a250n000000PMQ2AAO',
            'Zip__c': '94102'
        }]
    }


@pytest.fixture(scope='function')
def cts_dispatch_mapped():
    return {
        "done": True,
        "records": [{
            "attributes": {
                "type": "Service__c",
                "url": "/services/data/v42.0/sobjects/Service__c/a260n000000dXywAAE"
            },
            "id": "a260n000000dXywAAE",
            "name": "S-147735",
            "billing_invoice_date__c": None,
            "billing_invoice_number__c": None,
            "billing_total__c": 0,
            "carrier__c": None,
            "carrier_id_num__c": None,
            "check_in_date__c": None,
            "check_out_date__c": None,
            "city__c": "San Francisco",
            "confirmed__c": False,
            "country__c": None,
            "description__c": "Onsite Time Needed: 2020-06-21 4:00PM\r\nOnsite Timezone: Pacific Time\r\nReference: 4680743\r\nSLA Level: 4-hour\r\nLocation Country: United States\r\nLocation: Hayes Valley Inn, San Francisco, CA, 94102\r\n\r\nLocation ID: Test Location\r\nLocation Owner: Hayes Valley Inn\r\nOnsite Contact: John Smith\r\nContact #: +1 555 888 3333\r\nFailure Experienced: TEST Device is bouncing constantly\r\nOnsite SOW: This is a TEST\r\nMaterials Needed: Laptop, cable, tuner, ladder, internet hotspot\r\nService Category: Part Replacement\r\nName: Karen Doe\r\nPhone: +1 666 666 6666\r\nEmail: karen.doe@mettel.net",
            "duration_onsite__c": None,
            "early_start__c": "2020-06-21T23:00:00.000+0000",
            "ext_ref_num__c": "4680743",
            "finance_notes__c": None,
            "issue_summary__c": "TEST Device is bouncing constantly",
            "lift_delivery_date__c": None,
            "lift_release_date__c": None,
            "lift_vendor__c": None,
            "local_site_time__c": "2020-06-21T20:00:00.000+0000",
            "account__c": "0010n000017rOa2AAE",
            "lookup_location_owner__c": "Hayes Valley Inn",
            "on_site_elapsed_time__c": "Days  Hours  Minutes",
            "on_time_auto__c": False,
            "open_date__c": "2020-06-19T18:26:00.000+0000",
            "p1__c": None,
            "p10__c": None,
            "p10a__c": None,
            "p11__c": None,
            "p11a__c": None,
            "p12__c": None,
            "p12a__c": None,
            "p13__c": None,
            "p13a__c": None,
            "p14__c": None,
            "p14a__c": None,
            "p15__c": None,
            "p15a__c": None,
            "p1a__c": None,
            "p2__c": None,
            "p2a__c": None,
            "p3__c": None,
            "p3a__c": None,
            "p4__c": None,
            "p4a__c": None,
            "p5__c": None,
            "p5a__c": None,
            "p6__c": None,
            "p6a__c": None,
            "p7__c": None,
            "p7a__c": None,
            "p8__c": None,
            "p8a__c": None,
            "p9__c": None,
            "p9a__c": None,
            "parent_account_associated__c": "Mettel",
            "service_order__c": "a200n000000hKPNAA2",
            "project_name__c": "Sevice Requests",
            "location__c": None,
            "release_number__c": "R-1920-134925",
            "resource__c": None,
            "resource_assigned_timestamp__c": None,
            "resource_email__c": None,
            "resource_phone_number__c": None,
            "site_notes__c": None,
            "site_status__c": None,
            "special_shipping_instructions__c": None,
            "state__c": "CA",
            "street__c": "1234 Test Drive",
            "status__c": "Requires Dispatch",
            "resource_trained__c": False,
            "service_type__c": "a250n000000PMQ2AAO",
            "zip__c": "94102"
        }]
    }


@pytest.fixture(scope='function')
def cts_dispatch_mapped_without_record(cts_dispatch_mapped):
    updated_cts_dispatch_mapped = copy.deepcopy(cts_dispatch_mapped)
    del updated_cts_dispatch_mapped['records']
    return updated_cts_dispatch_mapped


@pytest.fixture(scope='function')
def cts_dispatch_mapped_without_done_false(cts_dispatch_mapped):
    updated_cts_dispatch_mapped = copy.deepcopy(cts_dispatch_mapped)
    updated_cts_dispatch_mapped['done'] = False
    updated_cts_dispatch_mapped['records'] = []
    return updated_cts_dispatch_mapped


@pytest.fixture(scope='function')
def cts_all_dispatches(cts_dispatch_mapped):
    return {
        "done": True,
        "records": [cts_dispatch_mapped]
    }


@pytest.fixture(scope='function')
def cts_all_dispatches_mapped(cts_dispatch_mapped):
    return {
        "done": True,
        "records": [cts_dispatch_mapped]
    }
