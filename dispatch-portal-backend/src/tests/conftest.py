import copy
from unittest.mock import Mock
import pytest
from unittest import mock
from asynctest import CoroutineMock

from application.repositories.lit_repository import LitRepository
from application.repositories.cts_repository import CtsRepository
from application.server.api_server import DispatchServer
from config import testconfig as config


# Scopes
# - function
# - module
# - session


@pytest.fixture(scope='function')
def logger():
    return Mock()


@pytest.fixture(scope='function')
def event_bus():
    return Mock()


@pytest.fixture(scope='function')
def redis_client():
    return Mock()


@pytest.fixture(scope='function')
def bruin_repository():
    return Mock()


@pytest.fixture(scope='function')
def notifications_repository():
    return Mock()


@pytest.fixture(scope='function')
def lit_repository(logger, event_bus, bruin_repository, notifications_repository):
    return LitRepository(logger, config, event_bus, notifications_repository, bruin_repository)


@pytest.fixture(scope='function')
def cts_repository(logger, event_bus, bruin_repository, notifications_repository):
    return CtsRepository(logger, config, event_bus, notifications_repository)


@pytest.fixture(scope='function')
def api_server_test(logger, event_bus, redis_client, bruin_repository, lit_repository, cts_repository,
                    notifications_repository):
    return DispatchServer(config, redis_client, event_bus, logger,
                          bruin_repository, lit_repository, cts_repository, notifications_repository)


@pytest.fixture(scope='function')
def dispatch():
    return {
        "turn_up": "False",
        "Time_Zone_Local": "Pacific Time",
        "Time_of_Check_Out": None,
        "Time_of_Check_In": None,
        "Tech_Off_Site": False,
        "Tech_Mobile_Number": None,
        "Tech_First_Name": None,
        "Tech_Arrived_On_Site": False,
        "Special_Materials_Needed_for_Dispatch": "1,2,6",
        "Special_Dispatch_Notes": "none",
        "Site_Survey_Quote_Required": True,
        "Scope_of_Work": "test",
        "Name_of_MetTel_Requester": "Michael J. Fox",
        "MetTel_Tech_Call_In_Instructions": "test",
        "MetTel_Requester_Email": None,
        "MetTel_Note_Updates": None,
        "MetTel_Group_Email": "test@test.net",
        "MetTel_Department_Phone_Number": "+11234567890",
        "MetTel_Department": "Advanced Services Engineering",
        "MetTel_Bruin_TicketID": "3544800",
        "Local_Time_of_Dispatch": None,
        "Job_Site_Zip_Code": "10038-4201",
        "Job_Site_Street": "160 Broadway",
        "Job_Site_State": "NY",
        "Job_Site_Contact_Name_and_Phone_Number": None,
        "Job_Site_City": "New York",
        "Job_Site": "me test",
        "Information_for_Tech": "test",
        "Hard_Time_of_Dispatch_Time_Zone_Local": None,
        "Hard_Time_of_Dispatch_Local": None,
        "Dispatch_Status": "New Dispatch",
        "Dispatch_Number": "DIS37405",
        "Date_of_Dispatch": "2020-03-16",
        "Close_Out_Notes": None,
        "Backup_MetTel_Department_Phone_Number": "+1 (212) 359-5129"
    }


@pytest.fixture(scope='function')
def dispatch_confirmed(lit_repository, dispatch):
    updated_dispatch = copy.deepcopy(dispatch)
    updated_dispatch["Job_Site_Contact_Name_and_Phone_Number"] = "Test Client on site +12123595129"
    updated_dispatch["Tech_First_Name"] = "Joe Malone"
    updated_dispatch["Tech_Mobile_Number"] = "+12123595129"
    updated_dispatch["Dispatch_Status"] = lit_repository.DISPATCH_CONFIRMED
    updated_dispatch["Hard_Time_of_Dispatch_Time_Zone_Local"] = "Pacific Time"
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = "4PM-6PM"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_confirmed_2(lit_repository, dispatch):
    updated_dispatch = copy.deepcopy(dispatch)
    updated_dispatch["Job_Site_Contact_Name_and_Phone_Number"] = "Test Client on site +12123595126"
    updated_dispatch["Dispatch_Number"] = "DIS37406"
    updated_dispatch["Tech_First_Name"] = "Hulk Hogan"
    updated_dispatch["Tech_Mobile_Number"] = "+12123595126"
    updated_dispatch["MetTel_Bruin_TicketID"] = "3544801"
    updated_dispatch["Dispatch_Status"] = lit_repository.DISPATCH_CONFIRMED
    updated_dispatch["Hard_Time_of_Dispatch_Time_Zone_Local"] = "Eastern Time"
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = "10:30AM-11:30AM"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_confirmed_error(dispatch_confirmed):
    updated_dispatch = copy.deepcopy(dispatch_confirmed)
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = "10:30-11:30"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_confirmed_error_2(dispatch_confirmed):
    updated_dispatch = copy.deepcopy(dispatch_confirmed)
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = None
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_confirmed_error_3(dispatch_confirmed):
    updated_dispatch = copy.deepcopy(dispatch_confirmed)
    updated_dispatch["Hard_Time_of_Dispatch_Time_Zone_Local"] = None
    return updated_dispatch


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
def new_dispatch_validation_error(new_dispatch):
    updated_cts_new_dispatch = copy.deepcopy(new_dispatch)
    del updated_cts_new_dispatch['date_of_dispatch']
    return updated_cts_new_dispatch


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
            'API_Resource_Name__c': 'Tech Name',
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
            'Description__c': 'Onsite Time Needed: 2020-06-21 4.00PM\r\nOnsite Timezone: Pacific Time\r\n'
                              'Reference: 4680743\r\nSLA Level: 4-hour\r\nLocation Country: United States\r\n'
                              'Location: Hayes Valley Inn, San Francisco, CA, 94102\r\n\r\n'
                              'Location ID: Test Location\r\nLocation Owner: Hayes Valley Inn\r\n'
                              'Onsite Contact: John Smith\r\nContact #: +1 555 888 3333\r\n'
                              'Failure Experienced: TEST Device is bouncing constantly\r\n'
                              'Onsite SOW: This is a TEST\r\n'
                              'Materials Needed: Laptop, cable, tuner, ladder, internet hotspot\r\n'
                              'Service Category: Part Replacement\r\nMetTel Requester Name: Karen Doe\r\n'
                              'MetTel Requester Phone: +1 666 666 6666\r\n'
                              'MetTel Requester Email: karen.doe@mettel.net\r\nIGZ Dispatch Number: IGZ_0001',
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
            'api_resource_name__c': 'Tech Name',
            "billing_invoice_date__c": None,
            "billing_invoice_number__c": None,
            "billing_total__c": 0.0,
            "carrier__c": None,
            "carrier_id_num__c": None,
            "check_in_date__c": None,
            "check_out_date__c": None,
            "city__c": "San Francisco",
            "confirmed__c": False,
            "country__c": None,
            "description__c": "Onsite Time Needed: 2020-06-21 4.00PM\r\n"
                              "Onsite Timezone: Pacific Time\r\nReference: 4680743\r\n"
                              "SLA Level: 4-hour\r\nLocation Country: United States\r\n"
                              "Location: Hayes Valley Inn, San Francisco, CA, 94102\r\n\r\n"
                              "Location ID: Test Location\r\nLocation Owner: Hayes Valley Inn\r\n"
                              "Onsite Contact: John Smith\r\nContact #: +1 555 888 3333\r\n"
                              "Failure Experienced: TEST Device is bouncing constantly\r\n"
                              "Onsite SOW: This is a TEST\r\n"
                              "Materials Needed: Laptop, cable, tuner, ladder, internet hotspot\r\n"
                              "Service Category: Part Replacement\r\nMetTel Requester Name: Karen Doe\r\n"
                              "MetTel Requester Phone: +1 666 666 6666\r\nMetTel Requester "
                              "Email: karen.doe@mettel.net\r\n"
                              "IGZ Dispatch Number: IGZ_0001",
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
            "zip__c": "94102",
            'date_of_dispatch': 'Jun 21, 2020 @ 11:00 PM UTC',
            'requester_name': 'Karen Doe',
            'requester_phone': '+1 666 666 6666',
            'requester_email': 'karen.doe@mettel.net'
        }]
    }


@pytest.fixture(scope='function')
def cts_dispatch_confirmed(cts_repository, cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch['records'][0])
    updated_dispatch['Confirmed__c'] = True
    updated_dispatch['Resource_Assigned_Timestamp__c'] = '2020-06-22T22:44:32.000+0000'
    updated_dispatch['Status__c'] = cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['API_Resource_Name__c'] = 'Michael J. Fox'
    updated_dispatch['Resource_Phone_Number__c'] = '+1 (212) 359-5129'
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_2(cts_repository, cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch['records'][0])
    updated_dispatch['Name'] = 'S-147735'
    updated_dispatch['Confirmed__c'] = True
    updated_dispatch['Resource_Assigned_Timestamp__c'] = '2020-06-22T22:44:32.000+0000'
    updated_dispatch['Status__c'] = cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['API_Resource_Name__c'] = 'Michael J. Fox'
    updated_dispatch['Resource_Phone_Number__c'] = '+1 (212) 359-5129'
    updated_dispatch['Description__c'] = updated_dispatch['Description__c'].replace(
        'Onsite Time Needed: 2020-06-21 4.00PM', 'Onsite Time Needed: 2020-06-21 4.00AM'
    )
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_3(cts_repository, cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch['records'][0])
    updated_dispatch['Name'] = 'S-147735'
    updated_dispatch['Confirmed__c'] = True
    updated_dispatch['Resource_Assigned_Timestamp__c'] = '2020-06-22T22:44:32.000+0000'
    updated_dispatch['Status__c'] = cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['API_Resource_Name__c'] = 'Michael J. Fox'
    updated_dispatch['Resource_Phone_Number__c'] = '+1 (212) 359-5129'
    updated_dispatch['Description__c'] = updated_dispatch['Description__c'].replace(
        'Onsite Time Needed: 2020-06-21 4.00PM', 'Onsite Time Needed: 2020-06-21 12.00AM'
    )
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_none_description(cts_repository, cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch)
    updated_dispatch['Status__c'] = cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['Description__c'] = None

    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_bad_date(cts_repository, cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch)
    updated_dispatch['Status__c'] = cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['Description__c'] = 'No Date'

    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_empty_address(cts_repository, cts_dispatch_confirmed):
    updated_dispatch = copy.deepcopy(cts_dispatch_confirmed)
    updated_dispatch['Status__c'] = cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['Description__c'] = updated_dispatch['Description__c'].replace(
        'Onsite Time Needed: 2020-06-21 4.00PM', 'Onsite Time Needed: '
    )

    return updated_dispatch


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
def cts_all_dispatches(cts_dispatch):
    return cts_dispatch


@pytest.fixture(scope='function')
def cts_all_dispatches_mapped(cts_dispatch_mapped):
    return cts_dispatch_mapped


@pytest.fixture(scope='function')
def simple_ticket_note():
    return "#*MetTel's IPA*#\nDispatch Management - Dispatch Requested\n\n" \
           "Please see the summary below.\n--\n" \
           "Dispatch Number:  " \
           "[DIS37561|https://master.mettel-automation.net/dispatch_portal/dispatch/S-12345] " \
           "\nDate of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n" \
           "Time Zone (Local): Pacific Time\n\n" \
           "Location Owner/Name: Red Rose Inn\n" \
           "Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n" \
           "Phone: +1 666 6666 666\n\n" \
           "Issues Experienced:\nDevice is bouncing constantly TEST LUNES\n" \
           "Arrival Instructions: " \
           "When arriving to the site call HOLMDEL NOC for telematic assistance\n" \
           "Materials Needed:\nLaptop, cable, tuner, ladder,internet hotspot\n\n" \
           "Requester\nName: Karen Doe\nPhone: +1 666 6666 666\n" \
           "Email: karen.doe@mettel.net\nDepartment: Customer Care"


@pytest.fixture(scope='function')
def small_ticket_note(simple_ticket_note):
    return 'A' * 150 + '\n' + 'B' * 150 + '\n' + 'C' * 150 + '\n' + 'D' * 150


@pytest.fixture(scope='function')
def big_ticket_note(simple_ticket_note):
    return 'A' * 1200 + '\n' + 'B' * 1200 + '\n' + 'C' * 500 + '\n' + 'D' * 600


@pytest.fixture(scope='function')
def ticket_details():
    return {
        'request_id': '12345',
        'body': {
            "ticketDetails": [
                {
                    "detailID": 5016058,
                    "detailType": "TicketId",
                    "detailStatus": "I",
                    "detailValue": "4664325",
                    "assignedToName": "0",
                    "currentTaskID": None,
                    "currentTaskName": None,
                    "lastUpdatedBy": 0,
                    "lastUpdatedAt": "2020-05-28T06:05:58.55-04:00"
                }
            ],
            "ticketNotes": [
                {
                    "noteId": 70805299,
                    "noteValue": "TEST first note",
                    "serviceNumber": [
                        "4664325"
                    ],
                    "createdDate": "2020-05-28T06:05:54.987-04:00",
                    "creator": None
                },
                {
                    "noteId": 70805300,
                    "noteValue": "#*Automation Engine*# DIS37561\nDispatch Management - Dispatch Requested\n\n"
                                 "Please see the summary below.\n--\n"
                                 "Dispatch Number:  "
                                 "[DIS37561|https://master.mettel-automation.net/dispatch_portal/dispatch/DIS37561] "
                                 "\nDate of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n"
                                 "Time Zone (Local): Pacific Time\n\n"
                                 "Location Owner/Name: Red Rose Inn\n"
                                 "Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n"
                                 "Phone: +1 666 6666 666\n\n"
                                 "Issues Experienced:\nDevice is bouncing constantly TEST LUNES\n"
                                 "Arrival Instructions: "
                                 "When arriving to the site call HOLMDEL NOC for telematic assistance\n"
                                 "Materials Needed:\nLaptop, cable, tuner, ladder,internet hotspot\n\n"
                                 "Requester\nName: Karen Doe\nPhone: +1 666 6666 666\n"
                                 "Email: karen.doe@mettel.net\nDepartment: Customer Care",
                    "serviceNumber": [
                        "4664325"
                    ],
                    "createdDate": "2020-05-28T06:06:40.27-04:00",
                    "creator": None
                },
                {
                    "noteId": 70805299,
                    "noteValue": None,
                    "serviceNumber": [
                        "4664325"
                    ],
                    "createdDate": "2020-05-28T06:05:54.987-04:00",
                    "creator": None
                },
                {
                    "noteId": 70805300,
                    "noteValue": "#*MetTel's IPA*# DIS37561\nDispatch Management - Dispatch Requested\n\n"
                                 "Please see the summary below.\n--\n"
                                 "Dispatch Number:  "
                                 "[DIS37561|https://master.mettel-automation.net/dispatch_portal/dispatch/DIS37561] "
                                 "\nDate of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n"
                                 "Time Zone (Local): Pacific Time\n\n"
                                 "Location Owner/Name: Red Rose Inn\n"
                                 "Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n"
                                 "Phone: +1 666 6666 666\n\n"
                                 "Issues Experienced:\nDevice is bouncing constantly TEST LUNES\n"
                                 "Arrival Instructions: "
                                 "When arriving to the site call HOLMDEL NOC for telematic assistance\n"
                                 "Materials Needed:\nLaptop, cable, tuner, ladder,internet hotspot\n\n"
                                 "Requester\nName: Karen Doe\nPhone: +1 666 6666 666\n"
                                 "Email: karen.doe@mettel.net\nDepartment: Customer Care",
                    "serviceNumber": [
                        "4664325"
                    ],
                    "createdDate": "2020-05-28T06:06:40.27-04:00",
                    "creator": None
                },
            ]
        },
        'status': 200
    }


@pytest.fixture(scope='function')
def ticket_details_1(ticket_details):
    updated_ticket_details = copy.deepcopy(ticket_details)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_2(ticket_details):
    updated_ticket_details = copy.deepcopy(ticket_details)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_2_error(ticket_details):
    updated_ticket_details = copy.deepcopy(ticket_details)
    updated_ticket_details['body'] = None
    updated_ticket_details['status'] = 400
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_1_error():
    return {
        'request_id': '12345',
        'body': {},
        'status': 400
    }


@pytest.fixture(scope='function')
def ticket_details_1_no_requested_watermark():
    return {
        'request_id': '12345',
        'body': {
            "ticketDetails": [
                {
                    "detailID": 5016058,
                    "detailType": "TicketId",
                    "detailStatus": "I",
                    "detailValue": "4664325",
                    "assignedToName": "0",
                    "currentTaskID": None,
                    "currentTaskName": None,
                    "lastUpdatedBy": 0,
                    "lastUpdatedAt": "2020-05-28T06:05:58.55-04:00"
                }
            ],
            "ticketNotes": [
                {
                    "noteId": 70805299,
                    "noteValue": "TEST first note",
                    "serviceNumber": [
                        "4664325"
                    ],
                    "createdDate": "2020-05-28T06:05:54.987-04:00",
                    "creator": None
                }
            ]
        },
        'status': 200
    }


@pytest.fixture(scope='function')
def ticket_details_1_with_cancel_requested_watermark():
    return {
        'request_id': '12345',
        'body': {
            "ticketDetails": [
                {
                    "detailID": 5016058,
                    "detailType": "TicketId",
                    "detailStatus": "I",
                    "detailValue": "4664325",
                    "assignedToName": "0",
                    "currentTaskID": None,
                    "currentTaskName": None,
                    "lastUpdatedBy": 0,
                    "lastUpdatedAt": "2020-05-28T06:05:58.55-04:00"
                }
            ],
            "ticketNotes": [
                {
                    "noteId": 70805299,
                    "noteValue": "TEST first note",
                    "serviceNumber": [
                        "4664325"
                    ],
                    "createdDate": "2020-05-28T06:05:54.987-04:00",
                    "creator": None
                },
                {
                    "noteId": 70805300,
                    "noteValue": "#*MetTel's IPA*# DIS37405\n"
                                 "Dispatch Management - Dispatch Cancel Requested\n\n"
                                 "The rest of the note\n--\n",
                    "serviceNumber": [
                        "4664325"
                    ],
                    "createdDate": "2020-05-28T06:05:54.987-04:00",
                    "creator": None
                }
            ]
        },
        'status': 200
    }


@pytest.fixture(scope='function')
def ticket_details_2_no_requested_watermark():
    return {
        'request_id': '12345',
        'body': {
            "ticketDetails": [
                {
                    "detailID": 5016058,
                    "detailType": "TicketId",
                    "detailStatus": "I",
                    "detailValue": "4664326",
                    "assignedToName": "0",
                    "currentTaskID": None,
                    "currentTaskName": None,
                    "lastUpdatedBy": 0,
                    "lastUpdatedAt": "2020-05-28T06:05:58.55-04:00"
                }
            ],
            "ticketNotes": [
                {
                    "noteId": 70805299,
                    "noteValue": "TEST first note",
                    "serviceNumber": [
                        "4664325"
                    ],
                    "createdDate": "2020-05-28T06:05:54.987-04:00",
                    "creator": None
                }
            ]
        },
        'status': 200
    }


@pytest.fixture(scope='function')
def cts_ticket_details():
    return {
        'request_id': '12345',
        'body': {
            "ticketDetails": [
                {
                    "detailID": 5016058,
                    "detailType": "TicketId",
                    "detailStatus": "I",
                    "detailValue": "4664325",
                    "assignedToName": "0",
                    "currentTaskID": None,
                    "currentTaskName": None,
                    "lastUpdatedBy": 0,
                    "lastUpdatedAt": "2020-05-28T06:05:58.55-04:00"
                }
            ],
            "ticketNotes": [
                {
                    "noteId": 70805299,
                    "noteValue": "TEST first note",
                    "serviceNumber": [
                        "4664325"
                    ],
                    "createdDate": "2020-05-28T06:05:54.987-04:00",
                    "creator": None
                },
                {
                    "noteId": 70805300,
                    "noteValue": "#*MetTel's IPA*# IGZ_0001\nDispatch Management - Dispatch Requested\n\n"
                                 "Please see the summary below.\n--\n"
                                 "Dispatch Number:  "
                                 "[IGZ_0001|https://master.mettel-automation.net/dispatch_portal/dispatch/IGZ_0001] "
                                 "\nDate of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n"
                                 "Time Zone (Local): Pacific Time\n\n"
                                 "Location Owner/Name: Red Rose Inn\n"
                                 "Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n"
                                 "Phone: +1 666 6666 666\n\n"
                                 "Issues Experienced:\nDevice is bouncing constantly TEST LUNES\n"
                                 "Arrival Instructions: "
                                 "When arriving to the site call HOLMDEL NOC for telematic assistance\n"
                                 "Materials Needed:\nLaptop, cable, tuner, ladder,internet hotspot\n\n"
                                 "Requester\nName: Karen Doe\nPhone: +1 666 6666 666\n"
                                 "Email: karen.doe@mettel.net\nDepartment: Customer Care",
                    "serviceNumber": [
                        "4664325"
                    ],
                    "createdDate": "2020-05-28T06:06:40.27-04:00",
                    "creator": None
                },
                {
                    "noteId": 70805299,
                    "noteValue": None,
                    "serviceNumber": [
                        "4664325"
                    ],
                    "createdDate": "2020-05-28T06:05:54.987-04:00",
                    "creator": None
                }
            ]
        },
        'status': 200
    }


@pytest.fixture(scope='function')
def cts_ticket_details_1(cts_ticket_details):
    updated_ticket_details = copy.deepcopy(cts_ticket_details)
    return updated_ticket_details


@pytest.fixture(scope='function')
def cts_ticket_details_2():
    # NOT VALID
    return {
        'request_id': '12345',
        'body': {
            "ticketDetails": [
                {
                    "detailID": 5016058,
                    "detailType": "TicketId",
                    "detailStatus": "I",
                    "detailValue": "4664326",
                    "assignedToName": "0",
                    "currentTaskID": None,
                    "currentTaskName": None,
                    "lastUpdatedBy": 0,
                    "lastUpdatedAt": "2020-05-28T06:05:58.55-04:00"
                }
            ],
            "ticketNotes": [
                {
                    "noteId": 70805299,
                    "noteValue": "TEST first note",
                    "serviceNumber": [
                        "4664326"
                    ],
                    "createdDate": "2020-05-28T06:05:54.987-04:00",
                    "creator": None
                },
                {
                    "noteId": 70805300,
                    "noteValue": "#*MetTel's IPA*# NOT_FOUND\nDispatch Management - Dispatch Requested\n\n"
                                 "Please see the summary below.\n--\n"
                                 "Dispatch Number:  "
                                 "[IGZ_0002|https://master.mettel-automation.net/dispatch_portal/dispatch/IGZ_0002] "
                                 "\nDate of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n"
                                 "Time Zone (Local): Pacific Time\n\n"
                                 "Location Owner/Name: Red Rose Inn\n"
                                 "Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n"
                                 "Phone: +1 666 6666 666\n\n"
                                 "Issues Experienced:\nDevice is bouncing constantly TEST LUNES\n"
                                 "Arrival Instructions: "
                                 "When arriving to the site call HOLMDEL NOC for telematic assistance\n"
                                 "Materials Needed:\nLaptop, cable, tuner, ladder,internet hotspot\n\n"
                                 "Requester\nName: Karen Doe\nPhone: +1 666 6666 666\n"
                                 "Email: karen.doe@mettel.net\nDepartment: Customer Care",
                    "serviceNumber": [
                        "4664326"
                    ],
                    "createdDate": "2020-05-28T06:06:40.27-04:00",
                    "creator": None
                },
                {
                    "noteId": 70805299,
                    "noteValue": None,
                    "serviceNumber": [
                        "4664326"
                    ],
                    "createdDate": "2020-05-28T06:05:54.987-04:00",
                    "creator": None
                }
            ]
        },
        'status': 400
    }


@pytest.fixture(scope='function')
def cts_ticket_details_1_error():
    return {
        'request_id': '12345',
        'body': {},
        'status': 400
    }


@pytest.fixture(scope='function')
def cts_ticket_details_1_no_requested_watermark():
    return {
        'request_id': '12345',
        'body': {
            "ticketDetails": [
                {
                    "detailID": 5016058,
                    "detailType": "TicketId",
                    "detailStatus": "I",
                    "detailValue": "4664325",
                    "assignedToName": "0",
                    "currentTaskID": None,
                    "currentTaskName": None,
                    "lastUpdatedBy": 0,
                    "lastUpdatedAt": "2020-05-28T06:05:58.55-04:00"
                }
            ],
            "ticketNotes": [
                {
                    "noteId": 70805299,
                    "noteValue": "TEST first note",
                    "serviceNumber": [
                        "4664325"
                    ],
                    "createdDate": "2020-05-28T06:05:54.987-04:00",
                    "creator": None
                }
            ]
        },
        'status': 200
    }


@pytest.fixture(scope='function')
def cts_ticket_details_1_with_cancel_requested_watermark():
    return {
        'request_id': '12345',
        'body': {
            "ticketDetails": [
                {
                    "detailID": 5016058,
                    "detailType": "TicketId",
                    "detailStatus": "I",
                    "detailValue": "4664325",
                    "assignedToName": "0",
                    "currentTaskID": None,
                    "currentTaskName": None,
                    "lastUpdatedBy": 0,
                    "lastUpdatedAt": "2020-05-28T06:05:58.55-04:00"
                }
            ],
            "ticketNotes": [
                {
                    "noteId": 70805299,
                    "noteValue": "TEST first note",
                    "serviceNumber": [
                        "4664325"
                    ],
                    "createdDate": "2020-05-28T06:05:54.987-04:00",
                    "creator": None
                },
                {
                    "noteId": 70805300,
                    "noteValue": "#*MetTel's IPA*# IGZ_0001\n"
                                 "Dispatch Management - Dispatch Cancel Requested\n\n"
                                 "The rest of the note\n--\n",
                    "serviceNumber": [
                        "4664325"
                    ],
                    "createdDate": "2020-05-28T06:05:54.987-04:00",
                    "creator": None
                }
            ]
        },
        'status': 200
    }
