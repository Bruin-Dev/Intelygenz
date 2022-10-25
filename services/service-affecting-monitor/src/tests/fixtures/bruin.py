from datetime import datetime
from typing import List, Optional

import pytest

from tests.fixtures._helpers import _missing, _undefined, bruinize_date


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
def make_ticket_details():
    def _inner(*, detail_items: List[dict] = None, notes: List[dict] = None):
        detail_items = detail_items or []
        notes = notes or []

        return {
            "ticketDetails": detail_items,
            "ticketNotes": notes,
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


@pytest.fixture(scope="session")
def make_site_details(make_address):
    def _inner(
        *,
        client_id: int = 0,
        client_name: str = "",
        site_id: int = 0,
        site_label: str = "",
        site_add_date: str = "",
        address: dict = None,
        longitude: float = 0.0,
        latitude: float = 0.0,
        business_hours: str = "",
        timezone: str = None,
        tz_offset: int = 0,
        contact_name: Optional[str] = "",
        contact_phone: Optional[str] = "",
        contact_email: Optional[str] = "",
    ):
        address = address or make_address()
        site_add_date = site_add_date or bruinize_date(datetime.now())

        return {
            "clientID": client_id,
            "clientName": client_name,
            "siteID": site_id,
            "siteLabel": site_label,
            "siteAddDate": site_add_date,
            "address": address,
            "longitude": longitude,
            "latitude": latitude,
            "businessHours": business_hours,
            "timeZone": timezone,
            "tzOffset": tz_offset,
            "primaryContactName": contact_name,
            "primaryContactPhone": contact_phone,
            "primaryContactEmail": contact_email,
        }

    return _inner


@pytest.fixture(scope="session")
def make_contact_info():
    def _inner(*, email: Optional[str] = "", phone: str = _missing, name: Optional[str] = ""):
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

        if phone is not _missing:
            obj[0]["phone"] = phone
            obj[1]["phone"] = phone

        return obj

    return _inner


# RPC requests
@pytest.fixture(scope="session")
def make_get_tickets_request(make_rpc_request):
    def _inner(
        *,
        request_id: str = "",
        bruin_client_id: int = 0,
        ticket_statuses: List[str] = None,
        product_category: str = "",
        ticket_topic: str = "",
        service_number: str = _undefined,
    ):
        payload = {
            "client_id": bruin_client_id,
            "ticket_statuses": ticket_statuses,
            "ticket_topic": ticket_topic,
            "product_category": product_category,
        }

        if service_number is not _undefined:
            payload["service_number"] = service_number

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope="session")
def make_get_ticket_details_request(make_rpc_request):
    def _inner(*, request_id: str = "", ticket_id: int = 0):
        payload = {
            "ticket_id": ticket_id,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope="session")
def make_append_ticket_note_request(make_rpc_request):
    def _inner(*, request_id: str = "", ticket_id: int = 0, note: str = "", service_numbers: List[str] = _undefined):
        payload = {
            "ticket_id": ticket_id,
            "note": note,
        }

        if service_numbers is not _undefined:
            payload["service_numbers"] = service_numbers

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope="session")
def make_unpause_ticket_detail_request(make_rpc_request):
    def _inner(*, request_id: str = "", ticket_id: int = 0, service_number: str = ""):
        payload = {
            "ticket_id": ticket_id,
            "service_number": service_number,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope="session")
def make_create_ticket_request(make_contact_info, make_rpc_request):
    def _inner(*, request_id: str = "", bruin_client_id: int = 0, service_number: str = "", contact_info: list = None):

        contact_info = contact_info or make_contact_info()

        payload = {
            "clientId": bruin_client_id,
            "category": "VAS",
            "services": [
                {
                    "serviceNumber": service_number,
                }
            ],
            "contacts": contact_info,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope="session")
def make_open_or_resolve_ticket_request(make_rpc_request):
    def _inner(*, request_id: str = "", ticket_id: int = 0, detail_id: int = 0):
        payload = {
            "ticket_id": ticket_id,
            "detail_id": detail_id,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope="session")
def make_change_detail_work_queue_request(make_rpc_request):
    def _inner(
        *,
        request_id: str = "",
        ticket_id: int = 0,
        detail_id: int = 0,
        service_number: str = "",
        target_queue: str = "",
    ):
        payload = {
            "ticket_id": ticket_id,
            "queue_name": target_queue,
            "service_number": service_number,
            "detail_id": detail_id,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


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


@pytest.fixture(scope="session")
def make_get_site_details_request(make_rpc_request):
    def _inner(*, request_id: str = "", client_id: int = 0, site_id: int = 0):
        payload = {
            "client_id": client_id,
            "site_id": site_id,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


# RPC responses
@pytest.fixture(scope="session")
def make_create_ticket_200_response(make_rpc_response):
    def _inner(*, request_id: str = "", ticket_id: int = 0):
        return make_rpc_response(
            request_id=request_id,
            body={
                "ticketIds": [ticket_id],
            },
            status=200,
        )

    return _inner


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
