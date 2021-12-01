from datetime import datetime

from typing import List
import pytest
from fixtures._helpers import bruinize_date


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
            "clientId": client_id,
            "ticketId": ticket_id,
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
def make_email():
    def _inner(
            *,
            email_id: int = 0,
            client_id: int = 0,
            body: str = '',
            received_date: str = '',
            subject: str = '',
            from_address: str = '',
            cc: str = '',
            to: str = '',
    ):
        received_date = received_date or bruinize_date(datetime.now())

        return {
            "email": {
                "email_id": email_id,
                "client_id": client_id,
                "body": body,
                "from": from_address,
                "to": to,
                "cc": cc,
                "date": received_date,
                "subject": subject,
            }
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
