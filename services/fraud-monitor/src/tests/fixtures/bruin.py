import pytest
from datetime import datetime
from typing import List, Optional
from config import testconfig


# Factories
@pytest.fixture(scope='session')
def make_address():
    def _inner(*, street: str = '', city: str = '', state: str = '', zip_code: str = '', country: str = ''):
        return {
            "address": street,
            "city": city,
            "state": state,
            "zip": zip_code,
            "country": country,
        }

    return _inner


@pytest.fixture(scope='session')
def make_ticket(make_address):
    def _inner(*, client_id: int = 0, ticket_id: int = 0, ticket_status: str = '', address: dict = None,
               create_date: str = '', created_by: str = '', call_type: str = '', category: str = '',
               severity: int = 0):
        address = address or make_address()
        create_date = create_date or str(datetime.now())

        return {
            "clientID": client_id,
            "ticketID": ticket_id,
            "ticketStatus": ticket_status,
            "address": address,
            "createDate": create_date,
            "createdBy": created_by,
            "callType": call_type,
            "category": category,
            "severity": severity,
        }

    return _inner


@pytest.fixture(scope='session')
def make_ticket_details():
    def _inner(*, detail_items: List[dict] = None, notes: List[dict] = None):
        detail_items = detail_items or []
        notes = notes or []

        return {
            "ticketDetails": detail_items,
            "ticketNotes": notes,
        }

    return _inner


@pytest.fixture(scope='session')
def make_detail_item():
    def _inner(*, id_: int = 0, type_: str = '', status: str = '', value: str = '', assigned_to: str = '',
               current_task_id: Optional[int] = 0, current_task_name: Optional[str] = '',
               last_updated_by_id: int = 0, last_updated_at: str = str(datetime.now())):
        return {
            'detailID': id_,
            'detailType': type_,
            'detailStatus': status,
            'detailValue': value,
            'assignedToName': assigned_to,
            'currentTaskID': current_task_id,
            'currentTaskName': current_task_name,
            'lastUpdatedBy': last_updated_by_id,
            'lastUpdatedAt': last_updated_at,
        }

    return _inner


@pytest.fixture(scope='session')
def make_ticket_note():
    def _inner(*, id_: int = 0, text: Optional[str] = '', service_numbers: List[str] = None,
               creation_date: str = str(datetime.now()), creator_email: str = ''):
        service_numbers = service_numbers or []

        return {
            'noteId': id_,
            'noteValue': text,
            'serviceNumber': service_numbers,
            'createdDate': creation_date,
            'creator': creator_email,
        }

    return _inner


@pytest.fixture(scope='session')
def default_contact():
    return testconfig.FRAUD_CONFIG['default_contact']


@pytest.fixture(scope='session')
def make_contact_info(default_contact):
    def _inner(*, email: str = default_contact['email'], name: str = default_contact['name'], phone: str = None):
        obj = [
            {
                "email": email,
                "name": name,
                "type": "ticket",
            },
            {
                "email": email,
                "name": name,
                "type": "site",
            },
        ]

        if phone is not None:
            obj[0]["phone"] = phone
            obj[1]["phone"] = phone

        return obj

    return _inner


@pytest.fixture(scope='session')
def make_detail_item_with_notes_and_ticket_info(make_ticket, make_detail_item):
    def _inner(*, detail_item: dict = None, notes: List[dict] = None, ticket_info: dict = None):
        detail_item = detail_item or make_detail_item()
        ticket_info = ticket_info or make_ticket()
        notes = notes or []

        return {
            'ticket_overview': ticket_info,
            'ticket_task': detail_item,
            'ticket_notes': notes,
        }

    return _inner


# RPC requests
@pytest.fixture(scope='session')
def make_get_client_info_by_did_request(make_rpc_request):
    def _inner(*, request_id: str = '', did: str = ''):
        payload = {
            'did': did,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope='session')
def make_get_tickets_request(make_rpc_request):
    def _inner(*, request_id: str = '', bruin_client_id: int = 0, ticket_statuses: List[str] = None,
               ticket_topic: str = '', service_number: str = None):
        payload = {
            'client_id': bruin_client_id,
            'ticket_statuses': ticket_statuses,
            'ticket_topic': ticket_topic,
        }

        if service_number is not None:
            payload['service_number'] = service_number

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope='session')
def make_get_ticket_details_request(make_rpc_request):
    def _inner(*, request_id: str = '', ticket_id: int = 0):
        payload = {
            'ticket_id': ticket_id,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope='session')
def make_get_client_info_request(make_rpc_request):
    def _inner(*, request_id: str = '', service_number: str = ''):
        payload = {
            'service_number': service_number,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope='session')
def make_get_site_details_request(make_rpc_request):
    def _inner(*, request_id: str = '', client_id: int = 0, site_id: int = 0):
        payload = {
            'client_id': client_id,
            'site_id': site_id,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope='session')
def make_append_ticket_note_request(make_rpc_request):
    def _inner(*, request_id: str = '', ticket_id: int = 0, note: str = '', service_numbers: List[str] = None):
        payload = {
            'ticket_id': ticket_id,
            'note': note,
        }

        if service_numbers is not None:
            payload['service_numbers'] = service_numbers

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope='session')
def make_unpause_ticket_detail_request(make_rpc_request):
    def _inner(*, request_id: str = '', ticket_id: int = 0, service_number: str = ''):
        payload = {
            'ticket_id': ticket_id,
            'service_number': service_number,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope='session')
def make_create_ticket_request(make_contact_info, make_rpc_request):
    def _inner(*, request_id: str = '', bruin_client_id: int = 0, service_number: str = '', contact_info: list = None):

        contact_info = contact_info or make_contact_info()

        payload = {
            'clientId': bruin_client_id,
            'category': 'VAS',
            'services': [
                {
                    'serviceNumber': service_number,
                }
            ],
            'contacts': contact_info
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope='session')
def make_open_or_resolve_ticket_request(make_rpc_request):
    def _inner(*, request_id: str = '', ticket_id: int = 0, detail_id: int = 0):
        payload = {
            'ticket_id': ticket_id,
            'detail_id': detail_id,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


# RPC responses
@pytest.fixture(scope='session')
def make_get_client_info_by_did_response(make_rpc_response):
    def _inner(request_id: str = '', service_number: str = '', client_id: int = 0):
        return make_rpc_response(
            request_id=request_id,
            body={
                'btn': service_number,
                'clientId': client_id,
                'clientName': '',
                'inventoryId': 0
            },
            status=200,
        )

    return _inner


@pytest.fixture(scope='session')
def make_get_tickets_response(make_rpc_response):
    def _inner(request_id: str = '', *tickets: List[dict]):
        return make_rpc_response(
            request_id=request_id,
            body=tickets,
            status=200,
        )

    return _inner


@pytest.fixture(scope='session')
def make_get_client_info_200_response(make_rpc_response):
    def _inner(*, request_id: str = '', site_id: int = 0):
        return make_rpc_response(
            request_id=request_id,
            body=[{
                'site_id': site_id,
            }],
            status=200,
        )

    return _inner


@pytest.fixture(scope='session')
def make_get_site_details_200_response(make_rpc_response, default_contact):
    def _inner(*, request_id: str = '', contact: dict = default_contact):
        return make_rpc_response(
            request_id=request_id,
            body={
                'primaryContactName': contact.get('name'),
                'primaryContactEmail': contact.get('email'),
                'primaryContactPhone': contact.get('phone'),
            },
            status=200,
        )

    return _inner


@pytest.fixture(scope='session')
def make_create_ticket_200_response(make_rpc_response):
    def _inner(*, request_id: str = '', ticket_id: int = 0):
        return make_rpc_response(
            request_id=request_id,
            body={
                'ticketIds': [ticket_id],
            },
            status=200,
        )

    return _inner


@pytest.fixture(scope='session')
def bruin_generic_200_response(make_rpc_response):
    return make_rpc_response(
        body='ok',
        status=200,
    )


@pytest.fixture(scope='session')
def bruin_500_response(make_rpc_response):
    return make_rpc_response(
        body='Got internal error from Bruin',
        status=500,
    )
