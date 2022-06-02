from datetime import datetime
from typing import List, Optional

import pytest
from tests.fixtures._helpers import _undefined, bruinize_date


# Factories
@pytest.fixture(scope="session")
def make_address():
    def _inner(*, street: str = "", city: str = "", state: str = "", zip_code: str = "", country: str = ""):
        return {
            "address": street,
            "city": city,
            "state": state,
            "zip": zip_code,
            "country": country,
        }

    return _inner


@pytest.fixture(scope="session")
def make_ticket(make_address):
    def _inner(
        *,
        client_id: int = 0,
        ticket_id: int = 0,
        ticket_status: str = "",
        address: dict = None,
        create_date: str = "",
        created_by: str = "",
        call_type: str = "",
        category: str = "",
        severity: int = 0,
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
            "severity": severity,
        }

    return _inner


@pytest.fixture(scope="session")
def make_detail_item():
    def _inner(
        *,
        id_: int = 0,
        type_: str = "",
        status: str = "",
        value: str = "",
        assigned_to: str = "",
        current_task_id: Optional[int] = _undefined,
        current_task_name: Optional[str] = _undefined,
        last_updated_by_id: int = 0,
        last_updated_at: str = "",
    ):
        current_task_id = current_task_id if current_task_id is not _undefined else 0
        current_task_name = current_task_name if current_task_name is not _undefined else ""
        last_updated_at = last_updated_at or bruinize_date(datetime.now())

        return {
            "detailID": id_,
            "detailType": type_,
            "detailStatus": status,
            "detailValue": value,
            "assignedToName": assigned_to,
            "currentTaskID": current_task_id,
            "currentTaskName": current_task_name,
            "lastUpdatedBy": last_updated_by_id,
            "lastUpdatedAt": last_updated_at,
        }

    return _inner


@pytest.fixture(scope="session")
def make_ticket_note():
    def _inner(
        *,
        id_: int = 0,
        text: Optional[str] = _undefined,
        service_numbers: List[str] = None,
        creation_date: str = "",
        creator_email: str = "",
    ):
        text = text if text is not _undefined else ""
        service_numbers = service_numbers or []
        creation_date = creation_date or bruinize_date(datetime.now())

        return {
            "noteId": id_,
            "noteValue": text,
            "serviceNumber": service_numbers,
            "createdDate": creation_date,
            "creator": creator_email,
        }

    return _inner


# RPC requests
@pytest.fixture(scope="session")
def make_post_notification_email_milestone_request(make_rpc_request):
    def _inner(*, request_id: str = "", ticket_id: int = 0, service_number: str = "", notification_type: str = ""):
        payload = {
            "notification_type": notification_type,
            "ticket_id": ticket_id,
            "service_number": service_number,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


# RPC responses
@pytest.fixture(scope="session")
def bruin_generic_200_response(make_rpc_response):
    return make_rpc_response(
        body="ok",
        status=200,
    )


@pytest.fixture(scope="session")
def bruin_500_response(make_rpc_response):
    return make_rpc_response(
        body="Got internal error from Bruin",
        status=500,
    )
