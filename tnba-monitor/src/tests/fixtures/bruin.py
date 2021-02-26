from datetime import datetime
from typing import List

import pytest

from tests.fixtures import _constants as constants


# Model-as-dict generators
def __generate_details_of_ticket(*, ticket_details: List[dict] = None, ticket_notes: List[dict] = None):
    ticket_details = ticket_details or []
    ticket_notes = ticket_notes or []

    return {
        "ticketDetails": ticket_details,
        "ticketNotes": ticket_notes,
    }


def __generate_ticket_detail(*, status: str, serial_number: str, detail_id: int = None):
    detail_id = detail_id or 999

    return {
        "detailID": detail_id,
        "detailType": "Repair_WTN",
        "detailStatus": status,
        "detailValue": serial_number,
        "assignedToName": "0",
        "currentTaskID": None,
        "currentTaskName": None,
        "lastUpdatedBy": 442301,
        "lastUpdatedAt": "2021-01-21T11:07:01.467-05:00"
    }


def __generate_ticket_note(*, serial_numbers: List[str], text: str, date: str = None):
    date = date or datetime.now()

    return {
        "noteId": 1,
        "noteValue": text,
        "serviceNumber": serial_numbers,
        "createdDate": date,
        "creator": "api_1@bruin.com"
    }


def __generate_payload_for_note_append(*, detail_id: int = None, serial_number: str = None, text: str):
    payload = {
        'text': text,
    }

    if detail_id:
        payload['detail_id'] = detail_id

    if serial_number:
        payload['service_number'] = serial_number

    return payload


def __generate_next_result_item(*, result_name: str):
    return {
        "resultTypeId": 620,
        "resultName": result_name,
        "notes": [
            {
                "noteType": "Notes",
                "noteDescription": "Notes",
                "availableValueOptions": None,
                "defaultValue": None,
                "required": False,
            }
        ]
    }


def __generate_next_results(*next_result_items: List[dict]):
    return {
        "currentTaskId": 10683187,
        "currentTaskKey": "344",
        "currentTaskName": "Holmdel NOC Investigate ",
        "nextResults": next_result_items,
    }


def __generate_task_history_item(*, serial_number: str, ticket_status: str = None):
    return {
        "Asset": serial_number,
        "Ticket Status": ticket_status,
    }


def __generate_task_history(*task_history_items: List[dict]):
    return [
        *task_history_items,
    ]


# Factories
@pytest.fixture(scope='session')
def make_ticket_note():
    def _inner(*, serial_number: str, date: str = None, text: str = None):
        return __generate_ticket_note(date=date, serial_numbers=[serial_number], text=text)

    return _inner


@pytest.fixture(scope='session')
def make_standard_tnba_note():
    def _inner(*, serial_number: str, prediction_name: str = None, date: str = None):
        prediction_name = prediction_name or constants.HOLMDEL_NOC_PREDICTION_NAME

        text = (
            "#*MetTel's IPA*#\n"
            'AI\n\n'
            f"MetTel's IPA AI indicates that the next best action for {serial_number} is: {prediction_name}.\n\n"
            "MetTel's IPA is based on an AI model designed specifically for MetTel."
        )
        return __generate_ticket_note(date=date, serial_numbers=[serial_number], text=text)

    return _inner


@pytest.fixture(scope='session')
def make_request_repair_completed_tnba_note():
    def _inner(*, serial_number: str, date: str = None):
        text = (
            "#*MetTel's IPA*#\n"
            'AI\n\n'
            f"MetTel's IPA AI is resolving the task for {serial_number}.\n\n"
            "MetTel's IPA is based on an AI model designed specifically for MetTel."
        )
        return __generate_ticket_note(date=date, serial_numbers=[serial_number], text=text)

    return _inner


@pytest.fixture(scope='session')
def make_reopen_note():
    def _inner(*, serial_number: str, date: str = None):
        text = (
            "#*MetTel's IPA*#\n"
            'Re-opening ticket.'
        )
        return __generate_ticket_note(date=date, serial_numbers=[serial_number], text=text)

    return _inner


@pytest.fixture(scope='session')
def make_triage_note():
    def _inner(*, serial_number: str, date: str = None):
        text = (
            "#*MetTel's IPA*#\n"
            'Triage (VeloCloud)'
        )
        return __generate_ticket_note(date=date, serial_numbers=[serial_number], text=text)

    return _inner


@pytest.fixture(scope='session')
def make_payload_for_note_append():
    def _inner(*, detail_id: int = None, serial_number: str = None, text: str):
        return __generate_payload_for_note_append(detail_id=detail_id, serial_number=serial_number, text=text)

    return _inner


@pytest.fixture(scope='session')
def make_details_of_ticket():
    def _inner(*, ticket_details: List[dict] = None, ticket_notes: List[dict] = None):
        return __generate_details_of_ticket(ticket_details=ticket_details, ticket_notes=ticket_notes)

    return _inner


@pytest.fixture(scope='session')
def make_resolved_ticket_detail():
    def _inner(*, serial_number: str):
        detail_status = 'R'
        return __generate_ticket_detail(status=detail_status, serial_number=serial_number)

    return _inner


@pytest.fixture(scope='session')
def make_in_progress_ticket_detail():
    def _inner(*, serial_number: str, detail_id: int = None):
        detail_status = 'I'
        return __generate_ticket_detail(status=detail_status, serial_number=serial_number, detail_id=detail_id)

    return _inner


@pytest.fixture(scope='session')
def make_next_result_item():
    def _inner(*, result_name: str):
        return __generate_next_result_item(result_name=result_name)

    return _inner


@pytest.fixture(scope='session')
def make_next_results():
    def _inner(*next_result_item: List[dict]):
        return __generate_next_results(*next_result_item)

    return _inner


@pytest.fixture(scope='session')
def make_task_history_item():
    def _inner(*, serial_number: str, ticket_status: str = None):
        return __generate_task_history_item(serial_number=serial_number, ticket_status=ticket_status)

    return _inner


@pytest.fixture(scope='session')
def make_task_history():
    def _inner(*task_history_items: List[dict]):
        return __generate_task_history(*task_history_items)

    return _inner


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
    return 'VC1234567'


@pytest.fixture(scope='session')
def serial_number_2():
    return 'VC8901234'


@pytest.fixture(scope='session')
def serial_number_3():
    return 'VC5678901'


# Tickets
@pytest.fixture(scope='session')
def open_affecting_ticket(bruin_client_id, bruin_client_name):
    return {
        "clientID": bruin_client_id,
        "clientName": bruin_client_name,
        "ticketID": 5118129,
        "category": "SD-WAN",
        "topic": "Service Affecting Trouble",
        "referenceTicketNumber": 0,
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
        "creationNote": None,
        "resolveDate": "",
        "resolvedby": None,
        "closeDate": None,
        "closedBy": None,
        "lastUpdate": None,
        "updatedBy": None,
        "mostRecentNote": "1/21/2021 4:06:56 PM Intelygenz Ai",
        "nextScheduledDate": "1/28/2021 5:00:00 AM",
        "flags": "",
        "severity": "2"
    }


@pytest.fixture(scope='session')
def open_outage_ticket(bruin_client_id, bruin_client_name):
    return {
        "clientID": bruin_client_id,
        "clientName": bruin_client_name,
        "ticketID": 5118129,
        "category": "SD-WAN",
        "topic": "Service Outage Trouble",
        "referenceTicketNumber": 0,
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
        "creationNote": None,
        "resolveDate": "",
        "resolvedby": None,
        "closeDate": None,
        "closedBy": None,
        "lastUpdate": None,
        "updatedBy": None,
        "mostRecentNote": "1/21/2021 4:06:56 PM Intelygenz Ai",
        "nextScheduledDate": "1/28/2021 5:00:00 AM",
        "flags": "",
        "severity": "2"
    }


# Ticket task histories
@pytest.fixture(scope='session')
def task_history_with_invalid_assets():
    return [
        {
            "Asset": None,
            "Ticket Status": "To do"
        },
        {
            "Asset": None,
            "Ticket Status": "In Progress"
        }
    ]


@pytest.fixture(scope='session')
def task_history_with_valid_assets(serial_number_1, serial_number_2):
    return [
        {
            "Asset": serial_number_1,
            "Ticket Status": "To do"
        },
        {
            "Asset": serial_number_2,
            "Ticket Status": "In Progress"
        }
    ]


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
def get_open_outage_ticket_200_response(open_outage_ticket):
    return {
        'body': [
            open_outage_ticket,
        ],
        'status': 200,
    }


@pytest.fixture(scope='session')
def get_open_ticket_empty_response(open_affecting_ticket):
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
def resolve_ticket_detail_200_response():
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
