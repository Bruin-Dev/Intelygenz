import copy
from unittest.mock import Mock

import pytest
from unittest import mock

from application.actions.lit_dispatch_monitor import LitDispatchMonitor

from application.repositories.lit_repository import LitRepository
from asynctest import CoroutineMock

from config import testconfig


# Scopes
# - function
# - module
# - session

@pytest.fixture(scope='function')
def lit_dispatch_monitor():
    redis_client = Mock()
    event_bus = Mock()
    logger = Mock()
    scheduler = Mock()
    config = testconfig
    lit_repository = Mock()
    bruin_repository = Mock()
    notifications_repository = Mock()

    lit_dispatch_monitor = LitDispatchMonitor(config, redis_client, event_bus, scheduler, logger,
                                              lit_repository, bruin_repository, notifications_repository)
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
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor.DISPATCH_CONFIRMED
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
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor.DISPATCH_CONFIRMED
    updated_dispatch["Hard_Time_of_Dispatch_Time_Zone_Local"] = "Eastern Time"
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = "10:30AM-11:30AM"
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_confirmed_skipped(lit_dispatch_monitor, dispatch):
    updated_dispatch = copy.deepcopy(dispatch)
    updated_dispatch["Dispatch_Number"] = "DIS37406"
    updated_dispatch["Tech_First_Name"] = "Hulk Hogan"
    updated_dispatch["Tech_Mobile_Number"] = "+12123595126"
    updated_dispatch["MetTel_Bruin_TicketID"] = "3544801|OTHER"
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor.DISPATCH_CONFIRMED
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
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor.DISPATCH_CONFIRMED
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
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor.DISPATCH_CONFIRMED
    updated_dispatch["Hard_Time_of_Dispatch_Time_Zone_Local"] = "Eastern Time"
    updated_dispatch["Hard_Time_of_Dispatch_Local"] = "10:30AM-11:30AM"
    updated_dispatch["Job_Site_Contact_Name_and_Phone_Number"] = "NOT VALID PHONE"
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
def dispatch_not_confirmed(dispatch):
    return dispatch.copy()


@pytest.fixture(scope='function')
def dispatch_tech_on_site(lit_dispatch_monitor, dispatch_confirmed):
    updated_dispatch = copy.deepcopy(dispatch_confirmed)
    updated_dispatch["Tech_Arrived_On_Site"] = True
    updated_dispatch["Time_of_Check_In"] = "6"
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor.DISPATCH_FIELD_ENGINEER_ON_SITE
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_tech_on_site_2(lit_dispatch_monitor, dispatch_confirmed_2):
    updated_dispatch = copy.deepcopy(dispatch_confirmed_2)
    updated_dispatch["Tech_Arrived_On_Site"] = True
    updated_dispatch["Time_of_Check_In"] = "10:30"
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor.DISPATCH_FIELD_ENGINEER_ON_SITE
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
    updated_dispatch["Dispatch_Status"] = lit_dispatch_monitor.DISPATCH_REPAIR_COMPLETED
    return updated_dispatch


@pytest.fixture(scope='function')
def dispatch_not_completed(dispatch_tech_on_site):
    return copy.deepcopy(dispatch_tech_on_site)


@pytest.fixture(scope='function')
def lit_repository():
    event_bus = Mock()
    logger = Mock()
    config = testconfig
    notifications_repository = Mock()

    lit_repository = LitRepository(logger, config, event_bus, notifications_repository)
    return lit_repository


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
                    "noteValue": "#*Automation Engine*#\nDispatch Management - Dispatch Requested\n\n"
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
                }
            ]
        },
        'status': 200
    }


@pytest.fixture(scope='function')
def ticket_details_1_with_confirmation_note(ticket_details_1, dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(ticket_details_1)
    confirmed_ticket_note = {
                    "noteId": 70805301,
                    "noteValue": "#*Automation Engine*#\n"
                                 "Dispatch Management - Dispatch Confirmed\n"
                                 "Dispatch scheduled for {date_of_dispatch} @ {time_of_dispatch} {time_zone}\n\n"
                                 "Field Engineer"
                                 "{tech_name}"
                                 "{tech_phone}".format(date_of_dispatch=dispatch_confirmed.get('Date_of_Dispatch'),
                                                       time_of_dispatch=dispatch_confirmed.get('Hard_Time_of_Dispatch_Local'),
                                                       time_zone=dispatch_confirmed.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
                                                       tech_name=dispatch_confirmed.get('Tech_First_Name'),
                                                       tech_phone=dispatch_confirmed.get('Tech_Mobile_Number')),
                    "serviceNumber": [
                        "4664325"
                    ],
                    "createdDate": "2020-05-28T06:06:40.27-04:00",
                    "creator": None
                }
    confirmed_sms_ticket_note_2 = {
        "noteId": 70805301,
        "noteValue": "#*Automation Engine*#\n"
                     "Dispatch confirmation SMS sent to {phone_number}".format(phone_number="+12123595129"),
        "serviceNumber": [
            "4664325"
        ],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(confirmed_ticket_note)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_2)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_2_with_confirmation_note(ticket_details_2, dispatch_confirmed_2):
    updated_ticket_details = copy.deepcopy(ticket_details_2)
    confirmed_ticket_note = {
        "noteId": 70805303,
        "noteValue": "#*Automation Engine*#\n"
                     "Dispatch Management - Dispatch Confirmed\n"
                     "Dispatch scheduled for {date_of_dispatch} @ {time_of_dispatch} {time_zone}\n\n"
                     "Field Engineer"
                     "{tech_name}"
                     "{tech_phone}".format(date_of_dispatch=dispatch_confirmed_2.get('Date_of_Dispatch'),
                                           time_of_dispatch=dispatch_confirmed_2.get('Hard_Time_of_Dispatch_Local'),
                                           time_zone=dispatch_confirmed_2.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
                                           tech_name=dispatch_confirmed_2.get('Tech_First_Name'),
                                           tech_phone=dispatch_confirmed_2.get('Tech_Mobile_Number')),
        "serviceNumber": [
            "4664325"
        ],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    confirmed_sms_ticket_note_2 = {
        "noteId": 70805304,
        "noteValue": "#*Automation Engine*#\n"
                     "Dispatch confirmation SMS sent to {phone_number}".format(phone_number="+12123595126"),
        "serviceNumber": [
            "4664325"
        ],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(confirmed_ticket_note)
    updated_ticket_details['body']['ticketNotes'].append(confirmed_sms_ticket_note_2)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_1_with_24h_sms_note(ticket_details_1_with_confirmation_note, dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(ticket_details_1_with_confirmation_note)
    sms_to = "+12123595129"
    note_24h_sms_ticket_note = {
        "noteId": 70805310,
        "noteValue": "#*Automation Engine*#"
                     "Dispatch 24h prior reminder SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": [
            "4664325"
        ],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_24h_sms_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_2_with_24h_sms_note(ticket_details_2_with_confirmation_note, dispatch_confirmed_2):
    updated_ticket_details = copy.deepcopy(ticket_details_2_with_confirmation_note)
    sms_to = "+12123595126"
    note_24h_sms_ticket_note = {
        "noteId": 70805310,
        "noteValue": "#*Automation Engine*#"
                     "Dispatch 24h prior reminder SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": [
            "4664325"
        ],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_24h_sms_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_1_with_2h_sms_note(ticket_details_1_with_24h_sms_note, dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(ticket_details_1_with_24h_sms_note)
    sms_to = "+12123595129"
    note_24h_sms_ticket_note = {
        "noteId": 70805310,
        "noteValue": "#*Automation Engine*#"
                     "Dispatch 2h prior reminder SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": [
            "4664325"
        ],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_24h_sms_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_2_with_2h_sms_note(ticket_details_2_with_24h_sms_note, dispatch_confirmed_2):
    updated_ticket_details = copy.deepcopy(ticket_details_2_with_24h_sms_note)
    sms_to = "+12123595126"
    note_24h_sms_ticket_note = {
        "noteId": 70805310,
        "noteValue": "#*Automation Engine*#"
                     "Dispatch 2h prior reminder SMS sent to {phone_number}".format(phone_number=sms_to),
        "serviceNumber": [
            "4664325"
        ],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_24h_sms_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_1_with_tech_on_site_sms_note(ticket_details_1_with_2h_sms_note, dispatch_confirmed):
    updated_ticket_details = copy.deepcopy(ticket_details_1_with_2h_sms_note)
    field_engineer_name = dispatch_confirmed.get('Tech_First_Name')
    note_24h_sms_ticket_note = {
        "noteId": 70805315,
        "noteValue": "#*Automation Engine*#"
                     "Dispatch Management - Field Engineer On Site\n\n"
                     "{field_engineer_name} has arrived\n".format(field_engineer_name=field_engineer_name),
        "serviceNumber": [
            "4664325"
        ],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_24h_sms_ticket_note)
    return updated_ticket_details


@pytest.fixture(scope='function')
def ticket_details_2_with_tech_on_site_sms_note(ticket_details_2_with_2h_sms_note, dispatch_confirmed_2):
    updated_ticket_details = copy.deepcopy(ticket_details_2_with_2h_sms_note)
    field_engineer_name = dispatch_confirmed_2.get('Tech_First_Name')
    note_24h_sms_ticket_note = {
        "noteId": 70805316,
        "noteValue": "#*Automation Engine*#"
                     "Dispatch Management - Field Engineer On Site\n\n"
                     "{field_engineer_name} has arrived\n".format(field_engineer_name=field_engineer_name),
        "serviceNumber": [
            "4664325"
        ],
        "createdDate": "2020-05-28T06:06:40.27-04:00",
        "creator": None
    }
    updated_ticket_details['body']['ticketNotes'].append(note_24h_sms_ticket_note)
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
