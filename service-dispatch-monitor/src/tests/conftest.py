import copy
from unittest.mock import Mock

import pytest
from unittest import mock

from application.actions.lit_dispatch_monitor import LitDispatchMonitor

from application.repositories.lit_repository import LitRepository
from asynctest import CoroutineMock

from application.actions.cts_dispatch_monitor import CtsDispatchMonitor

from application.repositories.cts_repository import CtsRepository
from config import testconfig


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
def notifications_repository():
    return Mock()


@pytest.fixture(scope='function')
def bruin_repository():
    return Mock()


@pytest.fixture(scope='function')
def redis_client():
    return Mock()


@pytest.fixture(scope='function')
def lit_repository(logger, event_bus, notifications_repository, bruin_repository):
    config = testconfig
    _lit_repository = LitRepository(logger, config, event_bus, notifications_repository, bruin_repository)
    return _lit_repository


@pytest.fixture(scope='function')
def lit_dispatch_monitor(lit_repository, redis_client):
    scheduler = Mock()
    config = testconfig

    lit_dispatch_monitor = LitDispatchMonitor(config, redis_client, lit_repository._event_bus,
                                              scheduler, lit_repository._logger, lit_repository,
                                              lit_repository._bruin_repository,
                                              lit_repository._notifications_repository)
    return lit_dispatch_monitor


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
def bad_status_dispatch(dispatch):
    updated_dispatch = copy.deepcopy(dispatch)
    updated_dispatch["Dispatch_Status"] = "BAD_STATUS"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_confirmed(lit_dispatch_monitor, dispatch):
    updated_dispatch = copy.deepcopy(dispatch)
    updated_dispatch["Job_Site_Contact_Name_and_Phone_Number"] = "Test Client on site +12123595129"
    updated_dispatch["Tech_First_Name"] = "Joe Malone"
    updated_dispatch["Tech_Mobile_Number"] = "+12123595129"
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor._lit_repository.DISPATCH_CONFIRMED
    updated_dispatch["Hard_Time_of_Dispatch_Time_Zone_Local"] = "Pacific Time"
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = "4PM-6PM"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_confirmed_2(lit_dispatch_monitor, dispatch):
    updated_dispatch = copy.deepcopy(dispatch)
    updated_dispatch["Job_Site_Contact_Name_and_Phone_Number"] = "Test Client on site +12123595126"
    updated_dispatch["Dispatch_Number"] = "DIS37406"
    updated_dispatch["Tech_First_Name"] = "Hulk Hogan"
    updated_dispatch["Tech_Mobile_Number"] = "+12123595126"
    updated_dispatch["MetTel_Bruin_TicketID"] = "3544801"
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor._lit_repository.DISPATCH_CONFIRMED
    updated_dispatch["Hard_Time_of_Dispatch_Time_Zone_Local"] = "Eastern Time"
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = "10:30AM-11:30AM"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_cancelled(lit_dispatch_monitor, dispatch_confirmed):
    updated_dispatch = copy.deepcopy(dispatch_confirmed)
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor._lit_repository.DISPATCH_CANCELLED
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_not_valid_ticket_id(lit_dispatch_monitor, dispatch_confirmed_2):
    updated_dispatch = copy.deepcopy(dispatch_confirmed_2)
    updated_dispatch['MetTel_Bruin_TicketID'] = 'as|asdf'
    updated_dispatch['Status__c'] = lit_dispatch_monitor._lit_repository.DISPATCH_FIELD_ENGINEER_ON_SITE
    updated_dispatch["Hard_Time_of_Dispatch_Time_Zone_Local"] = "Eastern Time"
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = "10:30AM-11:30AM"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_cancelled_not_valid_ticket_id(lit_dispatch_monitor, dispatch_cancelled_2):
    updated_dispatch = copy.deepcopy(dispatch_cancelled_2)
    updated_dispatch['MetTel_Bruin_TicketID'] = 'as|asdf'
    updated_dispatch['Status__c'] = lit_dispatch_monitor._lit_repository.DISPATCH_CANCELLED
    updated_dispatch["Hard_Time_of_Dispatch_Time_Zone_Local"] = "Eastern Time"
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = "10:30AM-11:30AM"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_cancelled_2(lit_dispatch_monitor, dispatch_confirmed_2):
    updated_dispatch = copy.deepcopy(dispatch_confirmed_2)
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor._lit_repository.DISPATCH_CANCELLED
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_confirmed_tech_phone_none(lit_dispatch_monitor, dispatch):
    updated_dispatch = copy.deepcopy(dispatch)
    updated_dispatch["Job_Site_Contact_Name_and_Phone_Number"] = "Test Client on site +12123595126"
    updated_dispatch["Dispatch_Number"] = "DIS37407"
    updated_dispatch["Tech_First_Name"] = "Joe Malone"
    updated_dispatch["Tech_Mobile_Number"] = None
    updated_dispatch["MetTel_Bruin_TicketID"] = "3544803"
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor._lit_repository.DISPATCH_CONFIRMED
    updated_dispatch["Hard_Time_of_Dispatch_Time_Zone_Local"] = "Central Time"
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = "9:30AM-11:30AM"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_confirmed_skipped(lit_dispatch_monitor, dispatch):
    updated_dispatch = copy.deepcopy(dispatch)
    updated_dispatch["Dispatch_Number"] = "DIS37406"
    updated_dispatch["Tech_First_Name"] = "Hulk Hogan"
    updated_dispatch["Tech_Mobile_Number"] = "+12123595126"
    updated_dispatch["MetTel_Bruin_TicketID"] = "3544801|OTHER"
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor._lit_repository.DISPATCH_CONFIRMED
    updated_dispatch["Hard_Time_of_Dispatch_Time_Zone_Local"] = "Eastern Time"
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = "10:30AM-11:30AM"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_confirmed_skipped_datetime(lit_dispatch_monitor, dispatch):
    updated_dispatch = copy.deepcopy(dispatch)
    updated_dispatch["Dispatch_Number"] = "DIS37406"
    updated_dispatch["Tech_First_Name"] = "Hulk Hogan"
    updated_dispatch["Tech_Mobile_Number"] = "+12123595126"
    updated_dispatch["MetTel_Bruin_TicketID"] = "3544801"
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor._lit_repository.DISPATCH_CONFIRMED
    updated_dispatch["Hard_Time_of_Dispatch_Time_Zone_Local"] = "Eastern Time"
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = "BAD TIME"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_confirmed_skipped_bad_phone(lit_dispatch_monitor, dispatch):
    updated_dispatch = copy.deepcopy(dispatch)
    updated_dispatch["Dispatch_Number"] = "DIS37406"
    updated_dispatch["Tech_First_Name"] = "Hulk Hogan"
    updated_dispatch["Tech_Mobile_Number"] = "+12123595126"
    updated_dispatch["MetTel_Bruin_TicketID"] = "3544801"
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor._lit_repository.DISPATCH_CONFIRMED
    updated_dispatch["Hard_Time_of_Dispatch_Time_Zone_Local"] = "Eastern Time"
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = "10:30AM-11:30AM"
    updated_dispatch["Job_Site_Contact_Name_and_Phone_Number"] = "NOT VALID PHONE"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_confirmed_skipped_bad_phone_tech(lit_dispatch_monitor, dispatch):
    updated_dispatch = copy.deepcopy(dispatch)
    updated_dispatch["Dispatch_Number"] = "DIS37406"
    updated_dispatch["Tech_First_Name"] = "Hulk Hogan"
    updated_dispatch["Tech_Mobile_Number"] = "NOT VALID PHONE"
    updated_dispatch["MetTel_Bruin_TicketID"] = "3544801"
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor._lit_repository.DISPATCH_CONFIRMED
    updated_dispatch["Hard_Time_of_Dispatch_Time_Zone_Local"] = "Eastern Time"
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = "10:30AM-11:30AM"
    updated_dispatch["Job_Site_Contact_Name_and_Phone_Number"] = "Test Client on site +12123595126"
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
def dispatch_not_confirmed(dispatch):
    return dispatch.copy()


@pytest.fixture(scope='function')
def dispatch_tech_on_site(lit_dispatch_monitor, dispatch_confirmed):
    updated_dispatch = copy.deepcopy(dispatch_confirmed)
    updated_dispatch["Tech_Arrived_On_Site"] = True
    updated_dispatch["Time_of_Check_In"] = "6"
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor._lit_repository.DISPATCH_FIELD_ENGINEER_ON_SITE
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_tech_on_site_2(lit_dispatch_monitor, dispatch_confirmed_2):
    updated_dispatch = copy.deepcopy(dispatch_confirmed_2)
    updated_dispatch["Tech_Arrived_On_Site"] = True
    updated_dispatch["Time_of_Check_In"] = "10:30"
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor._lit_repository.DISPATCH_FIELD_ENGINEER_ON_SITE
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_tech_on_site_bad_datetime(lit_dispatch_monitor, dispatch_confirmed_2):
    updated_dispatch = copy.deepcopy(dispatch_confirmed_2)
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = None
    updated_dispatch["Tech_Arrived_On_Site"] = True
    updated_dispatch["Time_of_Check_In"] = "10:30"
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor._lit_repository.DISPATCH_FIELD_ENGINEER_ON_SITE
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_cancelled_bad_datetime(lit_dispatch_monitor, dispatch_cancelled_2):
    updated_dispatch = copy.deepcopy(dispatch_cancelled_2)
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = None
    updated_dispatch["Tech_Arrived_On_Site"] = True
    updated_dispatch["Time_of_Check_In"] = "10:30"
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor._lit_repository.DISPATCH_CANCELLED
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_tech_on_site_skipped(lit_dispatch_monitor, dispatch_tech_on_site):
    updated_dispatch = copy.deepcopy(dispatch_tech_on_site)
    updated_dispatch["MetTel_Bruin_TicketID"] = "3544800|OTHER"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_tech_on_site_skipped_2(lit_dispatch_monitor, dispatch_tech_on_site_2):
    updated_dispatch = copy.deepcopy(dispatch_tech_on_site_2)
    updated_dispatch["MetTel_Bruin_TicketID"] = "3544801-OTHER"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_tech_on_site_skipped_bad_phone(lit_dispatch_monitor, dispatch_tech_on_site_skipped):
    updated_dispatch = copy.deepcopy(dispatch_tech_on_site_skipped)
    updated_dispatch["MetTel_Bruin_TicketID"] = "3544800"
    updated_dispatch["Job_Site_Contact_Name_and_Phone_Number"] = "NOT VALID PHONE"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_tech_not_on_site(dispatch_confirmed):
    return copy.deepcopy(dispatch_confirmed)


@pytest.fixture(scope='function')
def dispatch_completed(lit_dispatch_monitor, dispatch_tech_on_site):
    updated_dispatch = copy.deepcopy(dispatch_tech_on_site)
    updated_dispatch["Time_of_Check_Out"] = "8"
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor._lit_repository.DISPATCH_REPAIR_COMPLETED
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_not_completed(dispatch_tech_on_site):
    return copy.deepcopy(dispatch_tech_on_site)


@pytest.fixture(scope='function')
def sms_success_response():
    sms_from = '+16666666666'
    sms_to = '+19876543276'
    return {
          'sid': 'SM74b94f1bd0da4546ad034fc7c69791c0',
          'date_created': 'Fri, 29 May 2020 10:22:40 +0000',
          'date_updated': 'Fri, 29 May 2020 10:22:40 +0000',
          'account_sid': 'AC0dcb17b068164ddcf208df8c63783383',
          'from': sms_from,
          'to': sms_to,
          'body': 'This is a dummy SMS',
          'status': 'queued',
          'direction': 'outbound-api',
          'price': '0',
          'price_unit': 'USD',
          'api_version': '2012-04-24',
          'uri': f'/2012-04-24/Accounts/'
                 f'AC0dcb17b068164ddcf208df8c63783383/SMS/Messages/SM74b94f1bd0da4546ad034fc7c69791c0.json'
        }


@pytest.fixture(scope='function')
def sms_success_response_2(sms_success_response):
    sms_to = '+19876546666'
    updated_sms = copy.deepcopy(sms_success_response)
    updated_sms["sid"] = 'SM74b94f1bd0da4546ad034fc7c69791c1'
    updated_sms["to"] = sms_to
    updated_sms["uri"] = f'/2012-04-24/Accounts/' \
                         f'AC0dcb17b068164ddcf208df8c63783383/SMS/Messages/SM74b94f1bd0da4546ad034fc7c69791c1.json'
    return updated_sms


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
                    "noteValue": "#*Automation Engine*# DIS37405\nDispatch Management - Dispatch Requested\n\n"
                                 "Please see the summary below.\n--\n"
                                 "Dispatch Number:  "
                                 "[DIS37405|https://master.mettel-automation.net/dispatch_portal/dispatch/DIS37405] "
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
def ticket_details_1(ticket_details):
    updated_ticket_details = copy.deepcopy(ticket_details)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_2():
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
                    "noteValue": "#*Automation Engine*# DIS37406\nDispatch Management - Dispatch Requested\n\n"
                                 "Please see the summary below.\n--\n"
                                 "Dispatch Number:  "
                                 "[DIS37406|https://master.mettel-automation.net/dispatch_portal/dispatch/DIS37406] "
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
def ticket_details_3():
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
                    "noteValue": "#*Automation Engine*# DIS37407\nDispatch Management - Dispatch Requested\n\n"
                                 "Please see the summary below.\n--\n"
                                 "Dispatch Number:  "
                                 "[DIS37407|https://master.mettel-automation.net/dispatch_portal/dispatch/DIS37407] "
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
def ticket_details_no_watermark():
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
                    "noteValue": "#*NO WATERMARK*# DIS37561\nDispatch Management - Dispatch Requested\n\n"
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
                }
            ]
        },
        'status': 200
    }


@pytest.fixture(scope='function')
def ticket_details_2_error(ticket_details):
    updated_ticket_details = copy.deepcopy(ticket_details)
    updated_ticket_details['body'] = None
    updated_ticket_details['status'] = 400
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_2_no_ticket_id_in_watermark():
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
                    "noteId": 70805299,
                    "noteValue": "#*Automation Engine*# XX\n\nblah blah blah\nblah 2",
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
                    "noteId": 70805299,
                    "noteValue": "#*Automation Engine*# DIS37406\n\nblah blah blah\nblah 2",
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
def ticket_details_1_with_confirmation_note(ticket_details_1, dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(ticket_details_1)
    dispatch_number = dispatch_confirmed.get('Dispatch_Number')
    confirmed_ticket_note = {
        "noteId": 70805301,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch Management - Dispatch Confirmed\n"
                     "Dispatch scheduled for {date_of_dispatch} @ {time_of_dispatch} {time_zone}\n\n"
                     "Field Engineer\n"
                     "{tech_name}\n"
                     "{tech_phone}".format(date_of_dispatch=dispatch_confirmed.get('Date_of_Dispatch'),
                                           time_of_dispatch=dispatch_confirmed.get('Hard_Time_of_Dispatch_Local'),
                                           time_zone=dispatch_confirmed.get('Time_Zone_Local'),
                                           tech_name=dispatch_confirmed.get('Tech_First_Name'),
                                           tech_phone=dispatch_confirmed.get('Tech_Mobile_Number')),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    confirmed_sms_ticket_note_2 = {
        "noteId": 70805301,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch confirmation SMS sent to {phone_number}".format(phone_number="+12123595129"),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    confirmed_sms_ticket_note_3 = {
        "noteId": 70805301,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch confirmation SMS tech sent to {phone_number}".format(phone_number="+12123595129"),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(confirmed_ticket_note)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_2)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_3)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_1_with_confirmation_note_but_not_tech(ticket_details_1, dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(ticket_details_1)
    dispatch_number = dispatch_confirmed.get('Dispatch_Number')
    confirmed_ticket_note = {
        "noteId": 70805301,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch Management - Dispatch Confirmed\n"
                     "Dispatch scheduled for {date_of_dispatch} @ {time_of_dispatch} {time_zone}\n\n"
                     "Field Engineer\n"
                     "{tech_name}\n"
                     "{tech_phone}".format(date_of_dispatch=dispatch_confirmed.get('Date_of_Dispatch'),
                                           time_of_dispatch=dispatch_confirmed.get('Hard_Time_of_Dispatch_Local'),
                                           time_zone=dispatch_confirmed.get('Time_Zone_Local'),
                                           tech_name=dispatch_confirmed.get('Tech_First_Name'),
                                           tech_phone=dispatch_confirmed.get('Tech_Mobile_Number')),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    confirmed_sms_ticket_note_2 = {
        "noteId": 70805301,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch confirmation SMS sent to {phone_number}".format(phone_number="+12123595129"),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(confirmed_ticket_note)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_2)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_1_with_cancelled_note(ticket_details_1, dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(ticket_details_1)
    note_cancelled_note = {
        "noteId": 70805315,
        "noteValue": "#*Automation Engine*# DIS12345"
                     "Dispatch Management - Dispatch Cancelled\n\n"
                     "Dispatch for {date_of_dispatch} has been cancelled.\n".format(date_of_dispatch='AAA'),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_cancelled_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_1_with_confirmation_and_outdated_tech_note(ticket_details_1, dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(ticket_details_1)
    dispatch_number = dispatch_confirmed.get('Dispatch_Number')
    confirmed_ticket_note = {
        "noteId": 70805301,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch Management - Dispatch Confirmed\n"
                     "Dispatch scheduled for {date_of_dispatch} @ {time_of_dispatch} {time_zone}\n\n"
                     "Field Engineer\n"
                     "{tech_name}\n"
                     "{tech_phone}".format(date_of_dispatch=dispatch_confirmed.get('Date_of_Dispatch'),
                                           time_of_dispatch=dispatch_confirmed.get('Hard_Time_of_Dispatch_Local'),
                                           time_zone=dispatch_confirmed.get('Time_Zone_Local'),
                                           tech_name='Test TechName',
                                           tech_phone=dispatch_confirmed.get('Tech_Mobile_Number')),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    confirmed_sms_ticket_note_2 = {
        "noteId": 70805301,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch confirmation SMS sent to {phone_number}".format(phone_number="+12123595129"),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    confirmed_sms_ticket_note_3 = {
        "noteId": 70805301,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch confirmation SMS tech sent to {phone_number}".format(phone_number="+12123595129"),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(confirmed_ticket_note)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_2)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_3)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_1_with_confirmation_and_multiple_outdated_tech_note(
        ticket_details_1_with_confirmation_and_outdated_tech_note, dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(ticket_details_1_with_confirmation_and_outdated_tech_note)
    dispatch_number = dispatch_confirmed.get('Dispatch_Number')
    confirmed_ticket_note = {
        "noteId": 70805301,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "The Field Engineer assigned to this dispatch has changed.\n"
                     "Reference: {ticket_id}\n\n"
                     "Field Engineer\n"
                     "{tech_name}\n"
                     "{tech_phone}".format(ticket_id=dispatch_confirmed.get('MetTel_Bruin_TicketID'),
                                           tech_name='SecondTest TechName',
                                           tech_phone=dispatch_confirmed.get('Tech_Mobile_Number')),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(confirmed_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_2_with_confirmation_note(ticket_details_2, dispatch_confirmed_2):
    updated_ticket_details = copy.deepcopy(ticket_details_2)
    dispatch_number = dispatch_confirmed_2.get('Dispatch_Number')
    confirmed_ticket_note = {
        "noteId": 70805303,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch Management - Dispatch Confirmed\n"
                     "Dispatch scheduled for {date_of_dispatch} @ {time_of_dispatch} {time_zone}\n\n"
                     "Field Engineer\n"
                     "{tech_name}\n"
                     "{tech_phone}".format(date_of_dispatch=dispatch_confirmed_2.get('Date_of_Dispatch'),
                                           time_of_dispatch=dispatch_confirmed_2.get('Hard_Time_of_Dispatch_Local'),
                                           time_zone=dispatch_confirmed_2.get('Time_Zone_Local'),
                                           tech_name=dispatch_confirmed_2.get('Tech_First_Name'),
                                           tech_phone=dispatch_confirmed_2.get('Tech_Mobile_Number')),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    confirmed_sms_ticket_note_2 = {
        "noteId": 70805304,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch confirmation SMS sent to {phone_number}".format(phone_number="+12123595126"),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    confirmed_sms_ticket_note_3 = {
        "noteId": 70805304,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch confirmation SMS tech sent to {phone_number}".format(phone_number="+12123595126"),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(confirmed_ticket_note)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_2)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_3)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_2_with_confirmation_note_but_not_tech(ticket_details_2, dispatch_confirmed_2):
    updated_ticket_details = copy.deepcopy(ticket_details_2)
    dispatch_number = dispatch_confirmed_2.get('Dispatch_Number')
    confirmed_ticket_note = {
        "noteId": 70805303,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch Management - Dispatch Confirmed\n"
                     "Dispatch scheduled for {date_of_dispatch} @ {time_of_dispatch} {time_zone}\n\n"
                     "Field Engineer\n"
                     "{tech_name}\n"
                     "{tech_phone}".format(date_of_dispatch=dispatch_confirmed_2.get('Date_of_Dispatch'),
                                           time_of_dispatch=dispatch_confirmed_2.get('Hard_Time_of_Dispatch_Local'),
                                           time_zone=dispatch_confirmed_2.get('Time_Zone_Local'),
                                           tech_name=dispatch_confirmed_2.get('Tech_First_Name'),
                                           tech_phone=dispatch_confirmed_2.get('Tech_Mobile_Number')),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    confirmed_sms_ticket_note_2 = {
        "noteId": 70805304,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch confirmation SMS sent to {phone_number}".format(phone_number="+12123595126"),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(confirmed_ticket_note)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_2)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_1_with_12h_sms_note(ticket_details_1_with_confirmation_note, dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(ticket_details_1_with_confirmation_note)
    dispatch_number = dispatch_confirmed.get('Dispatch_Number')
    sms_to = "+12123595129"
    note_12h_sms_ticket_note = {
        "noteId": 70805310,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch 12h prior reminder SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    note_12h_sms_ticket_tech_note = {
        "noteId": 70805310,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch 12h prior reminder tech SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_12h_sms_ticket_note)
    updated_ticket_details['body']['ticketNotes'].append(note_12h_sms_ticket_tech_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_2_with_12h_sms_note(ticket_details_2_with_confirmation_note, dispatch_confirmed_2):
    updated_ticket_details = copy.deepcopy(ticket_details_2_with_confirmation_note)
    dispatch_number = dispatch_confirmed_2.get('Dispatch_Number')
    sms_to = "+12123595126"
    note_12h_sms_ticket_note = {
        "noteId": 70805310,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch 12h prior reminder SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    note_12h_sms_ticket_tech_note = {
        "noteId": 70805310,
        "noteValue": f"#*Automation Engine*# {dispatch_number}"
                     "Dispatch 12h prior reminder tech SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_12h_sms_ticket_note)
    updated_ticket_details['body']['ticketNotes'].append(note_12h_sms_ticket_tech_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_1_with_2h_sms_note(ticket_details_1_with_12h_sms_note, dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(ticket_details_1_with_12h_sms_note)
    dispatch_number = dispatch_confirmed.get('Dispatch_Number')
    sms_to = "+12123595129"
    note_2h_sms_ticket_note = {
        "noteId": 70805310,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch 2h prior reminder SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_2h_sms_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_2_with_2h_sms_note(ticket_details_2_with_12h_sms_note, dispatch_confirmed_2):
    updated_ticket_details = copy.deepcopy(ticket_details_2_with_12h_sms_note)
    dispatch_number = dispatch_confirmed_2.get('Dispatch_Number')
    sms_to = "+12123595126"
    note_2h_sms_ticket_note = {
        "noteId": 70805310,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch 2h prior reminder SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_2h_sms_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_detail_1_with_2h_tech_sms_note(ticket_details_1_with_2h_sms_note, dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(ticket_details_1_with_2h_sms_note)
    dispatch_number = dispatch_confirmed.get('Dispatch_Number')
    sms_to = "+12123595129"
    note_2h_sms_ticket_note = {
        "noteId": 70805310,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch 2h prior reminder tech SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_2h_sms_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_1_with_tech_on_site_sms_note(ticket_details_1_with_2h_sms_note, dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(ticket_details_1_with_2h_sms_note)
    dispatch_number = dispatch_confirmed.get('Dispatch_Number')
    field_engineer_name = dispatch_confirmed.get('Tech_First_Name')
    note_tech_sms_ticket_note = {
        "noteId": 70805315,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch Management - Field Engineer On Site\n\n"
                     "{field_engineer_name} has arrived\n".format(field_engineer_name=field_engineer_name),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_tech_sms_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_2_with_tech_on_site_sms_note(ticket_details_2_with_2h_sms_note, dispatch_confirmed_2):
    updated_ticket_details = copy.deepcopy(ticket_details_2_with_2h_sms_note)
    dispatch_number = dispatch_confirmed_2.get('Dispatch_Number')
    field_engineer_name = dispatch_confirmed_2.get('Tech_First_Name')
    note_tech_sms_ticket_note = {
        "noteId": 70805316,
        "noteValue": f"#*Automation Engine*# {dispatch_number}\n"
                     "Dispatch Management - Field Engineer On Site\n\n"
                     "{field_engineer_name} has arrived\n".format(field_engineer_name=field_engineer_name),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_tech_sms_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def append_note_response():
    return {
        "ticketNotes": [
            {
                "noteID": 70897911,
                "noteType": "ADN",
                "noteValue": "NOTE_TEST",
                "actionID": None,
                "detailID": None,
                "enteredBy": 442301,
                "enteredDate": "2020-06-02T07:59:43.057-04:00",
                "lastViewedBy": None,
                "lastViewedDate": None,
                "refNoteID": None,
                "noteStatus": None,
                "noteText": None,
                "childNotes": None,
                "documents": None,
                "alerts": None,
                "taggedUserDirIDs": None
            }
        ]
    }


@pytest.fixture(scope='function')
def append_note_response_2(append_note_response):
    updated_note = copy.deepcopy(append_note_response)
    updated_note["ticketNotes"][0]["noteID"] = 70897912
    updated_note["ticketNotes"][0]["noteValue"] = '#*Automation Engine*#\n' \
                                                  'Dispatch Management - Dispatch Confirmed\n' \
                                                  'Dispatch scheduled for 2020-03-16 @ None None\n\n' \
                                                  'Field Engineer\nJoe Malone\n+12123595129\n'
    return updated_note


@pytest.fixture(scope='function')
def cts_repository(logger, event_bus, redis_client, notifications_repository):
    event_bus = Mock()
    logger = Mock()
    config = testconfig
    redis_client = Mock()

    cts_repository = CtsRepository(logger, config, event_bus, notifications_repository, redis_client)
    return cts_repository


@pytest.fixture(scope='function')
def cts_dispatch_monitor(cts_repository):
    scheduler = Mock()
    config = testconfig
    bruin_repository = Mock()

    _cts_dispatch_monitor = CtsDispatchMonitor(config, redis_client, cts_repository._event_bus,
                                               scheduler, cts_repository._logger, cts_repository, bruin_repository,
                                               cts_repository._notifications_repository)
    return _cts_dispatch_monitor


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
def cts_dispatch_confirmed(cts_dispatch_monitor, cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch)
    updated_dispatch['Confirmed__c'] = True
    updated_dispatch['Resource_Assigned_Timestamp__c'] = '2020-06-22T22:44:32.000+0000'
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['API_Resource_Name__c'] = 'Michael J. Fox'
    updated_dispatch['Resource_Phone_Number__c'] = '+1 (212) 359-5129'
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_cancelled(cts_dispatch_monitor, cts_dispatch_confirmed):
    updated_dispatch = copy.deepcopy(cts_dispatch_confirmed)
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_CANCELLED
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_cancelled_2(cts_dispatch_monitor, cts_dispatch_confirmed_2):
    updated_dispatch = copy.deepcopy(cts_dispatch_confirmed_2)
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_CANCELLED
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_bad_date(cts_dispatch_monitor, cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch)
    updated_dispatch['Confirmed__c'] = True
    updated_dispatch['Resource_Assigned_Timestamp__c'] = '2020-06-22T22:44:32.000+0000'
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['API_Resource_Name__c'] = 'Michael J. Fox'
    updated_dispatch['Resource_Phone_Number__c'] = '+1 (212) 359-5129'

    updated_dispatch['Local_Site_Time__c'] = None

    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_skipped(cts_dispatch_monitor, cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch)
    updated_dispatch['Confirmed__c'] = True
    updated_dispatch['Resource_Assigned_Timestamp__c'] = '2020-06-22T22:44:32.000+0000'
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['API_Resource_Name__c'] = 'Michael J. Fox'
    updated_dispatch['Resource_Phone_Number__c'] = '+1 (212) 359-5129'
    updated_dispatch['Ext_Ref_Num__c'] = "3544801|OTHER"

    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_skipped_datetime(cts_dispatch_monitor, cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch)
    updated_dispatch['Confirmed__c'] = True
    updated_dispatch['Resource_Assigned_Timestamp__c'] = '2020-06-22T22:44:32.000+0000'
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['API_Resource_Name__c'] = 'Michael J. Fox'
    updated_dispatch['Resource_Phone_Number__c'] = '+1 (212) 359-5129'

    updated_dispatch['Local_Site_Time__c'] = None

    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_skipped_bad_phone(cts_dispatch_monitor, cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch)
    updated_dispatch['Confirmed__c'] = True
    updated_dispatch['Resource_Assigned_Timestamp__c'] = '2020-06-22T22:44:32.000+0000'
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['API_Resource_Name__c'] = 'Michael J. Fox'
    updated_dispatch['Resource_Phone_Number__c'] = '+1 (212) 359-5129'

    updated_dispatch['Description__c'] = updated_dispatch['Description__c'].replace('Contact #: (202) 772-3610',
                                                                                    'Contact #: NO CONTACT')

    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_skipped_bad_phone_tech(cts_dispatch_monitor, cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch)
    updated_dispatch['Confirmed__c'] = True
    updated_dispatch['Resource_Assigned_Timestamp__c'] = '2020-06-22T22:44:32.000+0000'
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['API_Resource_Name__c'] = 'Michael J. Fox'
    updated_dispatch['Resource_Phone_Number__c'] = 'NOT VALID PHONE'

    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_no_contact(cts_dispatch_monitor, cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch)
    updated_dispatch['Confirmed__c'] = True
    updated_dispatch['Resource_Assigned_Timestamp__c'] = '2020-06-22T22:44:32.000+0000'
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['API_Resource_Name__c'] = 'Michael J. Fox'
    updated_dispatch['Resource_Phone_Number__c'] = '+1 (212) 359-5129'

    updated_dispatch['Description__c'] = updated_dispatch['Description__c'].replace('Contact #:', 'NO CONTACT')

    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_error_number(cts_dispatch_monitor, cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch)
    updated_dispatch['Confirmed__c'] = True
    updated_dispatch['Resource_Assigned_Timestamp__c'] = '2020-06-22T22:44:32.000+0000'
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['API_Resource_Name__c'] = 'Michael J. Fox'
    updated_dispatch['Resource_Phone_Number__c'] = '+1 (212) 359-5129'

    updated_dispatch['Description__c'] = updated_dispatch['Description__c'].replace('Contact #: (202) 772-3610',
                                                                                    'Contact #: A00123222430A 99 98989')

    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_2(cts_dispatch_monitor, cts_dispatch_confirmed):
    updated_dispatch = copy.deepcopy(cts_dispatch_confirmed)
    updated_dispatch['Confirmed__c'] = True
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['Name'] = 'S-12346'
    updated_dispatch['Ext_Ref_Num__c'] = '123456'

    updated_dispatch['Description__c'] = updated_dispatch['Description__c'].replace('Contact #: (202) 772-3610',
                                                                                    'Contact #: (202) 772-3611')

    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_confirmed_no_main_watermark(cts_dispatch_monitor, cts_dispatch_confirmed):
    updated_dispatch = copy.deepcopy(cts_dispatch_confirmed)
    updated_dispatch['Confirmed__c'] = True
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_CONFIRMED
    updated_dispatch['Name'] = 'S-12347'
    updated_dispatch['Ext_Ref_Num__c'] = '123456'

    updated_dispatch['Description__c'] = updated_dispatch['Description__c'].replace('Contact #: (202) 772-3610',
                                                                                    'Contact #: (202) 772-3611')

    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_not_confirmed(cts_dispatch_monitor, cts_dispatch):
    updated_dispatch = copy.deepcopy(cts_dispatch)
    updated_dispatch['Confirmed__c'] = False
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_REQUESTED
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_tech_on_site(cts_dispatch_monitor, cts_dispatch_confirmed):
    updated_dispatch = copy.deepcopy(cts_dispatch_confirmed)
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_FIELD_ENGINEER_ON_SITE
    updated_dispatch['Check_In_Date__c'] = '2020-06-19T18:29:45.000+0000'
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_tech_on_site_2(cts_dispatch_monitor, cts_dispatch_confirmed_2):
    updated_dispatch = copy.deepcopy(cts_dispatch_confirmed_2)
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_FIELD_ENGINEER_ON_SITE
    updated_dispatch['Check_In_Date__c'] = '2020-06-19T18:29:45.000+0000'
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_not_valid_ticket_id(cts_dispatch_monitor, cts_dispatch_confirmed_2):
    updated_dispatch = copy.deepcopy(cts_dispatch_confirmed_2)
    updated_dispatch['Ext_Ref_Num__c'] = 'as|asdf'
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_FIELD_ENGINEER_ON_SITE
    updated_dispatch['Check_In_Date__c'] = '2020-06-19T18:29:45.000+0000'
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_cancelled_not_valid_ticket_id(cts_dispatch_monitor, cts_dispatch_cancelled):
    updated_dispatch = copy.deepcopy(cts_dispatch_cancelled)
    updated_dispatch['Ext_Ref_Num__c'] = 'as|asdf'
    updated_dispatch['Check_In_Date__c'] = '2020-06-19T18:29:45.000+0000'
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_cts_dispatch_cancelled_bad_datetime(cts_dispatch_monitor, cts_dispatch_cancelled):
    updated_dispatch = copy.deepcopy(cts_dispatch_cancelled)
    updated_dispatch['Check_In_Date__c'] = '2020-06-19T18:29:45.000+0000'
    updated_dispatch['Local_Site_Time__c'] = None
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_tech_on_site_bad_datetime(cts_dispatch_monitor, cts_dispatch_confirmed):
    updated_dispatch = copy.deepcopy(cts_dispatch_confirmed)
    updated_dispatch['Status__c'] = cts_dispatch_monitor._cts_repository.DISPATCH_FIELD_ENGINEER_ON_SITE
    updated_dispatch['Check_In_Date__c'] = '2020-06-19T18:29:45.000+0000'
    updated_dispatch['Local_Site_Time__c'] = None
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_tech_not_on_site(cts_dispatch_confirmed):
    updated_dispatch = copy.deepcopy(cts_dispatch_confirmed)
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_tech_on_site_skipped(cts_dispatch_confirmed):
    updated_dispatch = copy.deepcopy(cts_dispatch_confirmed)
    updated_dispatch["Ext_Ref_Num__c"] = "3544801|OTHER"
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_bad_status_dispatch(dispatch):
    updated_dispatch = copy.deepcopy(dispatch)
    updated_dispatch["Status__c"] = "BAD_STATUS"
    return updated_dispatch


@pytest.fixture(scope='function')
def cts_dispatch_tech_on_site_skipped_bad_phone(cts_dispatch_tech_on_site):
    updated_dispatch = copy.deepcopy(cts_dispatch_tech_on_site)
    updated_dispatch['Description__c'] = updated_dispatch['Description__c'].replace(
        'Contact #: (202) 772-3610', 'Contact #: A00123222430A 99 98989')
    return updated_dispatch


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
                    "noteValue": "#*Automation Engine*# IGZ_0001\nDispatch Management - Dispatch Requested\n\n"
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
                    "noteValue": "#*Automation Engine*# IGZ_0002\nDispatch Management - Dispatch Requested\n\n"
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
def cts_ticket_details_no_dispatch_2():
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
                    "noteValue": "#*Automation Engine*# \nDispatch Management - Dispatch Requested\n\n"
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
def cts_ticket_details_3():
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
                    "noteValue": "#*Automation Engine*# IGZ_0003\nDispatch Management - Dispatch Requested\n\n"
                                 "Please see the summary below.\n--\n"
                                 "Dispatch Number:  "
                                 "[IGZ_0003|https://master.mettel-automation.net/dispatch_portal/dispatch/IGZ_0003] "
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
def cts_ticket_details_no_watermark():
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
                    "noteValue": "#*NO WATERMARK*# IGZ_0002\nDispatch Management - Dispatch Requested\n\n"
                                 "Please see the summary below.\n--\n"
                                 "Dispatch Number:  "
                                 "[IGZ_0003|https://master.mettel-automation.net/dispatch_portal/dispatch/IGZ_0003] "
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
def cts_ticket_details_2_error(cts_ticket_details):
    updated_ticket_details = copy.deepcopy(cts_ticket_details)
    updated_ticket_details['body'] = None
    updated_ticket_details['status'] = 400
    return updated_ticket_details


@pytest.fixture(scope='function')
def cts_ticket_details_2_no_ticket_id_in_watermark():
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
                    "noteId": 70805299,
                    "noteValue": "#*Automation Engine* # IGZ_0002\n\nblah blah blah\nblah 2",
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
def cts_ticket_details_2_no_requested_watermark():
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
                    "noteId": 70805299,
                    "noteValue": "#*Automation Engine*# IGZ_0002\n\nblah blah blah\nblah 2",
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
def cts_ticket_details_1_with_confirmation_note(cts_ticket_details_1, cts_dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(cts_ticket_details_1)
    confirmed_ticket_note = {
        "noteId": 70805301,
        "noteValue": "#*Automation Engine*# IGZ_0001\n"
                     "Dispatch Management - Dispatch Confirmed\n"
                     "Dispatch scheduled for {date_of_dispatch} @ {time_of_dispatch} {time_zone}\n\n"
                     "Field Engineer\n"
                     "{tech_name}\n"
                     "{tech_phone}".format(date_of_dispatch=cts_dispatch_confirmed.get('Date_of_Dispatch'),
                                           time_of_dispatch=cts_dispatch_confirmed.get('Hard_Time_of_Dispatch_Local'),
                                           time_zone=cts_dispatch_confirmed.get('Time_Zone_Local'),
                                           tech_name=cts_dispatch_confirmed.get('Tech_First_Name'),
                                           tech_phone=cts_dispatch_confirmed.get('Tech_Mobile_Number')),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    confirmed_sms_ticket_note_2 = {
        "noteId": 70805301,
        "noteValue": "#*Automation Engine*# IGZ_0001\n"
                     "Dispatch confirmation SMS sent to {phone_number}".format(phone_number="+12123595129"),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    confirmed_sms_ticket_note_3 = {
        "noteId": 70805301,
        "noteValue": "#*Automation Engine*# IGZ_0001\n"
                     "Dispatch confirmation SMS tech sent to {phone_number}".format(phone_number="+12123595129"),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(confirmed_ticket_note)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_2)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_3)
    return updated_ticket_details


@pytest.fixture(scope='function')
def cts_ticket_details_1_with_confirmation_note_but_not_tech(cts_ticket_details_1, cts_dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(cts_ticket_details_1)
    confirmed_ticket_note = {
        "noteId": 70805301,
        "noteValue": "#*Automation Engine*# IGZ_0001\n"
                     "Dispatch Management - Dispatch Confirmed\n"
                     "Dispatch scheduled for {date_of_dispatch} @ {time_of_dispatch} {time_zone}\n\n"
                     "Field Engineer\n"
                     "{tech_name}\n"
                     "{tech_phone}".format(date_of_dispatch=dispatch_confirmed.get('Date_of_Dispatch'),
                                           time_of_dispatch=dispatch_confirmed.get('Hard_Time_of_Dispatch_Local'),
                                           time_zone=dispatch_confirmed.get('Time_Zone_Local'),
                                           tech_name=dispatch_confirmed.get('Tech_First_Name'),
                                           tech_phone=dispatch_confirmed.get('Tech_Mobile_Number')),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    confirmed_sms_ticket_note_2 = {
        "noteId": 70805301,
        "noteValue": "#*Automation Engine*# IGZ_0001\n"
                     "Dispatch confirmation SMS sent to {phone_number}".format(phone_number="+12123595129"),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(confirmed_ticket_note)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_2)
    return updated_ticket_details


@pytest.fixture(scope='function')
def cts_ticket_details_2_with_confirmation_note(cts_ticket_details_2, cts_dispatch_confirmed_2):
    updated_ticket_details = copy.deepcopy(cts_ticket_details_2)
    confirmed_ticket_note = {
        "noteId": 70805303,
        "noteValue": "#*Automation Engine*# IGZ_0002\n"
                     "Dispatch Management - Dispatch Confirmed\n"
                     "Dispatch scheduled for {date_of_dispatch} @ {time_of_dispatch} {time_zone}\n\n"
                     "Field Engineer\n"
                     "{tech_name}\n"
                     "{tech_phone}".format(date_of_dispatch=cts_dispatch_confirmed_2.get('Date_of_Dispatch'),
                                           time_of_dispatch=cts_dispatch_confirmed_2.get('Hard_Time_of_Dispatch_Local'),
                                           time_zone=cts_dispatch_confirmed_2.get('Time_Zone_Local'),
                                           tech_name=cts_dispatch_confirmed_2.get('Tech_First_Name'),
                                           tech_phone=cts_dispatch_confirmed_2.get('Tech_Mobile_Number')),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    confirmed_sms_ticket_note_2 = {
        "noteId": 70805304,
        "noteValue": "#*Automation Engine*# IGZ_0002\n"
                     "Dispatch confirmation SMS sent to {phone_number}".format(phone_number="+12123595126"),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    confirmed_sms_ticket_note_3 = {
        "noteId": 70805304,
        "noteValue": "#*Automation Engine*# IGZ_0002\n"
                     "Dispatch confirmation SMS tech sent to {phone_number}".format(phone_number="+12123595126"),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(confirmed_ticket_note)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_2)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_3)
    return updated_ticket_details


@pytest.fixture(scope='function')
def cts_ticket_details_2_with_confirmation_note_but_not_tech(cts_ticket_details_2, cts_dispatch_confirmed_2):
    updated_ticket_details = copy.deepcopy(cts_ticket_details_2)
    confirmed_ticket_note = {
        "noteId": 70805303,
        "noteValue": "#*Automation Engine*# IGZ_0002\n"
                     "Dispatch Management - Dispatch Confirmed\n"
                     "Dispatch scheduled for {date_of_dispatch} @ {time_of_dispatch} {time_zone}\n\n"
                     "Field Engineer\n"
                     "{tech_name}\n"
                     "{tech_phone}".format(date_of_dispatch=cts_dispatch_confirmed_2.get('Date_of_Dispatch'),
                                           time_of_dispatch=cts_dispatch_confirmed_2.get('Hard_Time_of_Dispatch_Local'),
                                           time_zone=cts_dispatch_confirmed_2.get('Time_Zone_Local'),
                                           tech_name=cts_dispatch_confirmed_2.get('Tech_First_Name'),
                                           tech_phone=cts_dispatch_confirmed_2.get('Tech_Mobile_Number')),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    confirmed_sms_ticket_note_2 = {
        "noteId": 70805304,
        "noteValue": "#*Automation Engine*# IGZ_0002\n"
                     "Dispatch confirmation SMS sent to {phone_number}".format(phone_number="+12123595126"),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(confirmed_ticket_note)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_2)
    return updated_ticket_details


@pytest.fixture(scope='function')
def cts_ticket_details_1_with_12h_sms_note(cts_ticket_details_1_with_confirmation_note, cts_dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(cts_ticket_details_1_with_confirmation_note)
    sms_to = "+12123595129"
    note_12h_sms_ticket_note = {
        "noteId": 70805310,
        "noteValue": "#*Automation Engine*# IGZ_0001"
                     "Dispatch 12h prior reminder SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    note_12h_sms_ticket_tech_note = {
        "noteId": 70805310,
        "noteValue": "#*Automation Engine*# IGZ_0001"
                     "Dispatch 12h prior reminder tech SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_12h_sms_ticket_note)
    updated_ticket_details['body']['ticketNotes'].append(note_12h_sms_ticket_tech_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def cts_ticket_details_2_with_12h_sms_note(cts_ticket_details_2_with_confirmation_note, cts_dispatch_confirmed_2):
    updated_ticket_details = copy.deepcopy(cts_ticket_details_2_with_confirmation_note)
    sms_to = "+12123595126"
    note_12h_sms_ticket_note = {
        "noteId": 70805310,
        "noteValue": "#*Automation Engine*# IGZ_0002"
                     "Dispatch 12h prior reminder SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    note_12h_sms_ticket_tech_note = {
        "noteId": 70805310,
        "noteValue": "#*Automation Engine*# IGZ_0002"
                     "Dispatch 12h prior reminder tech SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_12h_sms_ticket_note)
    updated_ticket_details['body']['ticketNotes'].append(note_12h_sms_ticket_tech_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def cts_ticket_details_1_with_2h_sms_note(cts_ticket_details_1_with_12h_sms_note, cts_dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(cts_ticket_details_1_with_12h_sms_note)
    sms_to = "+12123595129"
    note_2h_sms_ticket_note = {
        "noteId": 70805310,
        "noteValue": "#*Automation Engine*# IGZ_0001"
                     "Dispatch 2h prior reminder SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_2h_sms_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def cts_ticket_details_2_with_2h_sms_note(cts_ticket_details_2_with_12h_sms_note, cts_dispatch_confirmed_2):
    updated_ticket_details = copy.deepcopy(cts_ticket_details_2_with_12h_sms_note)
    sms_to = "+12123595126"
    note_2h_sms_ticket_note = {
        "noteId": 70805310,
        "noteValue": "#*Automation Engine*# IGZ_0002"
                     "Dispatch 2h prior reminder SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_2h_sms_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def cts_ticket_details_1_with_2h_sms_tech_note(cts_ticket_details_1_with_2h_sms_note, cts_dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(cts_ticket_details_1_with_2h_sms_note)
    sms_to = "+12123595129"
    note_2h_sms_ticket_note = {
        "noteId": 70805310,
        "noteValue": "#*Automation Engine*# IGZ_0001"
                     "Dispatch 2h prior reminder tech SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_2h_sms_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def cts_ticket_details_1_with_tech_on_site_sms_note(cts_ticket_details_1_with_2h_sms_note, cts_dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(cts_ticket_details_1_with_2h_sms_note)
    field_engineer_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
    note_tech_sms_ticket_note = {
        "noteId": 70805315,
        "noteValue": "#*Automation Engine*# IGZ_0001"
                     "Dispatch Management - Field Engineer On Site\n\n"
                     "{field_engineer_name} has arrived\n".format(field_engineer_name=field_engineer_name),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_tech_sms_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def cts_ticket_details_2_with_tech_on_site_sms_note(cts_ticket_details_2_with_2h_sms_note, cts_dispatch_confirmed_2):
    updated_ticket_details = copy.deepcopy(cts_ticket_details_2_with_2h_sms_note)
    field_engineer_name = cts_dispatch_confirmed_2.get('API_Resource_Name__c')
    note_tech_sms_ticket_note = {
        "noteId": 70805316,
        "noteValue": "#*Automation Engine*# IGZ_0002"
                     "Dispatch Management - Field Engineer On Site\n\n"
                     "{field_engineer_name} has arrived\n".format(field_engineer_name=field_engineer_name),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_tech_sms_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def cts_ticket_details_1_with_cancelled_note(cts_ticket_details_1, cts_dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(cts_ticket_details_1)
    date_of_dispatch = cts_dispatch_confirmed.get('Date_of_Dispatch')
    field_engineer_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
    note_cancelled_note = {
        "noteId": 70805315,
        "noteValue": "#*Automation Engine*# IGZ_0001"
                     "Dispatch Management - Dispatch Cancelled\n\n"
                     "Dispatch for {date_of_dispatch} has been cancelled.\n".format(date_of_dispatch=date_of_dispatch),
        "serviceNumber": ["4664325"],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_cancelled_note)
    return updated_ticket_details
