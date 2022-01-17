from datetime import datetime

from typing import List
import pytest
from tests.fixtures._helpers import bruinize_date


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
    def _inner(
            *,
            client_id: int = 0,
            ticket_id: int = 0,
            ticket_status: str = '',
            address: dict = None,
            create_date: str = '',
            created_by: str = '',
            call_type: str = '',
            category: str = '',
            severity: int = 0
    ):
        address = address or make_address()
        create_date = create_date or bruinize_date(datetime.now())

        return {
            "clientID": client_id,
            "ticketID": ticket_id,
            "ticketStatus": ticket_status,
            "address": address,
            "createDate": create_date,
            "createdBy": created_by,
            "callType": call_type,
            "category": category,
            "severity": severity
        }

    return _inner


@pytest.fixture(scope='session')
def make_ticket_decamelized(make_address):
    def _inner(
            *,
            client_id: int = 0,
            ticket_id: int = 0,
            ticket_status: str = '',
            address: dict = None,
            create_date: str = '',
            created_by: str = '',
            call_type: str = '',
            category: str = '',
            severity: int = 0
    ):
        address = address or make_address()
        create_date = create_date or bruinize_date(datetime.now())

        return {
            "client_id": client_id,
            "ticket_id": ticket_id,
            "ticket_status": ticket_status,
            "address": address,
            "create_date": create_date,
            "created_by": created_by,
            "call_type": call_type,
            "category": category,
            "severity": severity
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
