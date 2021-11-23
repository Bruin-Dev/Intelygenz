from typing import List

import pytest


# Factories
def __generate_ticket_detail(*, status: str, serial_number: str):
    return {
        "detailID": 999,
        "detailType": "Repair_WTN",
        "detailStatus": status,
        "detailValue": serial_number,
        "assignedToName": "0",
        "currentTaskID": None,
        "currentTaskName": None,
        "lastUpdatedBy": 442301,
        "lastUpdatedAt": "2021-01-21T11:07:01.467-05:00"
    }


def __generate_in_progress_ticket_detail(*, serial_number: str):
    return __generate_ticket_detail(status='I', serial_number=serial_number)


def __generate_resolved_ticket_detail(*, serial_number: str):
    return __generate_ticket_detail(status='R', serial_number=serial_number)


def __generate_ticket_note(*, id_: int, date: str, serial_numbers: List[str], **kwargs):
    note_contents = kwargs.get('contents', 'This is a note')

    return {
        "noteId": id_,
        "noteValue": note_contents,
        "serviceNumber": serial_numbers,
        "createdDate": date,
        "creator": "api_1@bruin.com"
    }


# Client info
@pytest.fixture(scope='session')
def bruin_client_id():
    return 9994


@pytest.fixture(scope='session')
def bruin_client_name():
    return 'METTEL/NEW YORK'


# Serial numbers
@pytest.fixture(scope='session')
def serial_number_1():
    return 'B827EB76A8DE'


@pytest.fixture(scope='session')
def serial_number_2():
    return 'C827FC76B8EF'


@pytest.fixture(scope='session')
def serial_number_3():
    return 'D8270D76C8F0'


# Ticket details
@pytest.fixture(scope='session')
def ticket_detail_in_progress_for_serial_1(serial_number_1):
    return __generate_in_progress_ticket_detail(serial_number=serial_number_1)


@pytest.fixture(scope='session')
def ticket_detail_resolved_for_serial_1(serial_number_1):
    return __generate_resolved_ticket_detail(serial_number=serial_number_1)


@pytest.fixture(scope='session')
def ticket_detail_in_progress_for_serial_2(serial_number_2):
    return __generate_in_progress_ticket_detail(serial_number=serial_number_2)


@pytest.fixture(scope='session')
def ticket_detail_resolved_for_serial_2(serial_number_2):
    return __generate_resolved_ticket_detail(serial_number=serial_number_2)


# Ticket notes
@pytest.fixture(scope='session')
def ticket_note_for_serial_1_posted_on_2020_01_16(serial_number_1):
    return __generate_ticket_note(id_=1, date='2020-01-16T00:00:00.000-05:00', serial_numbers=[serial_number_1])


@pytest.fixture(scope='session')
def ticket_note_for_serial_1_posted_on_2020_01_17(serial_number_1):
    return __generate_ticket_note(id_=2, date='2020-01-17T00:00:00.000-05:00', serial_numbers=[serial_number_1])


@pytest.fixture(scope='session')
def ticket_note_for_serial_2_posted_on_2020_01_16(serial_number_2):
    return __generate_ticket_note(id_=3, date='2020-01-16T00:00:00.000-05:00', serial_numbers=[serial_number_2])


@pytest.fixture(scope='session')
def ticket_note_for_serial_2_posted_on_2020_01_17(serial_number_2):
    return __generate_ticket_note(id_=4, date='2020-01-17T00:00:00.000-05:00', serial_numbers=[serial_number_2])


@pytest.fixture(scope='session')
def ticket_note_for_serial_1_and_2_posted_on_2020_01_16(serial_number_1, serial_number_2):
    return __generate_ticket_note(
        id_=5,
        date='2020-01-16T00:00:00.000-05:00',
        serial_numbers=[serial_number_1, serial_number_2],
    )


@pytest.fixture(scope='session')
def ticket_note_for_serial_1_and_2_posted_on_2020_01_17(serial_number_1, serial_number_2):
    return __generate_ticket_note(
        id_=6,
        date='2020-01-17T00:00:00.000-05:00',
        serial_numbers=[serial_number_1, serial_number_2],
    )


@pytest.fixture(scope='session')
def note_text_about_passed_icmp_test(test_type_icmp_test):
    return (
        "#*MetTel's IPA*#\n"
        'Service Affecting (Ixia)\n'
        'Device Name: ATL_XR2000_1\n'
        '\n'
        'All thresholds are normal.\n'
        '\n'
        'Test Status: PASSED\n'
        f'Test Type: {test_type_icmp_test}\n'
        'Test: 316 - Test Result: 2569942'
    )


@pytest.fixture(scope='session')
def note_text_about_failed_icmp_test(test_type_icmp_test):
    return (
        "#*MetTel's IPA*#\n"
        'Service Affecting (Ixia)\n'
        'Device Name: ATL_XR2000_1\n'
        '\n'
        'Trouble: Loss\n'
        'Threshold: 5\n'
        'Value: 7\n'
        '\n'
        'Test Status: FAILED\n'
        f'Test Type: {test_type_icmp_test}\n'
        'Test: 316 - Test Result: 2569942'
    )


@pytest.fixture(scope='session')
def note_text_about_passed_network_kpi_test(test_type_network_kpi):
    return (
        "#*MetTel's IPA*#\n"
        'Service Affecting (Ixia)\n'
        'Device Name: ATL_XR2000_1\n'
        '\n'
        'All thresholds are normal.\n'
        '\n'
        'Test Status: PASSED\n'
        f'Test Type: {test_type_network_kpi}\n'
        'Test: 316 - Test Result: 2569942'
    )


@pytest.fixture(scope='session')
def note_text_about_failed_network_kpi_test(test_type_network_kpi):
    return (
        "#*MetTel's IPA*#\n"
        'Service Affecting (Ixia)\n'
        'Device Name: ATL_XR2000_1\n'
        '\n'
        'Trouble: Jitter Max (ms)\n'
        'Threshold: 8\n'
        'Value: 8.3\n'
        '\n'
        'Test Status: FAILED\n'
        f'Test Type: {test_type_network_kpi}\n'
        'Test: 316 - Test Result: 2569942'
    )


# Tickets
@pytest.fixture(scope='session')
def open_affecting_ticket(bruin_client_id, bruin_client_name):
    return {
        "clientID": bruin_client_id,
        "ticketID": 5118129,
        "ticketStatus": "In-Progress",
        "address": {
            "address": "55 Water St Fl 32",
            "city": "New York",
            "state": "NY",
            "zip": "10041-3299",
            "country": "USA"
        },
        "createDate": "1/21/2021 4:02:30 PM",
        "createdBy": "Intelygenz Ai",
        "callType": "REP",
        "category": "VAS",
    }


# RPC responses
@pytest.fixture(scope='session')
def get_open_affecting_ticket_200_response(open_affecting_ticket):
    return {
        'body': [
            open_affecting_ticket,
        ],
        'status': 200,
    }


@pytest.fixture(scope='session')
def get_open_affecting_ticket_empty_response(open_affecting_ticket):
    return {
        'body': [],
        'status': 200,
    }


@pytest.fixture(scope='session')
def get_ticket_details_200_response(ticket_detail_in_progress_for_serial_1,
                                    ticket_note_for_serial_1_posted_on_2020_01_16,
                                    ticket_note_for_serial_1_posted_on_2020_01_17):
    return {
        'body': {
            'ticketDetails': [
                ticket_detail_in_progress_for_serial_1,
            ],
            'ticketNotes': [
                ticket_note_for_serial_1_posted_on_2020_01_16,
                ticket_note_for_serial_1_posted_on_2020_01_17,
            ],
        },
        'status': 200,
    }


@pytest.fixture(scope='session')
def create_affecting_ticket_200_response():
    return {
        'body': {
            'ticketIds': [
                1234,
            ],
        },
        'status': 200,
    }


@pytest.fixture(scope='session')
def append_multiple_notes_200_response():
    return {
        'body': {
            "ticketNotes": [
                {
                    "noteID": 70646090,
                    "noteType": "ADN",
                    "noteValue": "This is ticket note 1",
                    "actionID": None,
                    "detailID": 123,
                    "enteredBy": 442301,
                    "enteredDate": "2020-05-20T06:00:38.803-04:00",
                    "lastViewedBy": None,
                    "lastViewedDate": None,
                    "refNoteID": None,
                    "noteStatus": None,
                    "noteText": None,
                    "childNotes": None,
                    "documents": None,
                    "alerts": None,
                    "taggedUserDirIDs": None,
                },
                {
                    "noteID": 70646091,
                    "noteType": "ADN",
                    "noteValue": "This is ticket note 2",
                    "actionID": None,
                    "detailID": 999,
                    "enteredBy": 442301,
                    "enteredDate": "2020-05-20T06:00:38.803-04:00",
                    "lastViewedBy": None,
                    "lastViewedDate": None,
                    "refNoteID": None,
                    "noteStatus": None,
                    "noteText": None,
                    "childNotes": None,
                    "documents": None,
                    "alerts": None,
                    "taggedUserDirIDs": None,
                },
                {
                    "noteID": 70646092,
                    "noteType": "ADN",
                    "noteValue": "This is ticket note 3",
                    "actionID": None,
                    "detailID": 456,
                    "enteredBy": 442301,
                    "enteredDate": "2020-05-20T06:00:38.803-04:00",
                    "lastViewedBy": None,
                    "lastViewedDate": None,
                    "refNoteID": None,
                    "noteStatus": None,
                    "noteText": None,
                    "childNotes": None,
                    "documents": None,
                    "alerts": None,
                    "taggedUserDirIDs": None,
                },
            ],
        },
        'status': 200,
    }


@pytest.fixture(scope='session')
def unresolve_ticket_detail_200_response():
    return {
        'body': 'ok',
        'status': 200,
    }


@pytest.fixture(scope='session')
def bruin_500_response():
    return {
        'body': 'Got internal error from Bruin',
        'status': 500,
    }
