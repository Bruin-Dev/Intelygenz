from datetime import datetime

import pytest
from typing import Any, Dict, List
from tests.fixtures._helpers import bruinize_date


@pytest.fixture(scope='session')
def make_filter_flags():
    def _inner(
            *,
            tagger_is_below_threshold: bool = False,
            rta_model1_is_below_threshold: bool = False,
            rta_model2_is_below_threshold: bool = False,
            in_validation_set: bool = False,
            is_filtered: bool = False,
    ):
        return {
            "tagger_is_below_threshold": tagger_is_below_threshold,
            "rta_model1_is_below_threshold": rta_model1_is_below_threshold,
            "rta_model2_is_below_threshold": rta_model2_is_below_threshold,
            "is_filtered": is_filtered,
            "in_validation_set": in_validation_set,
        }

    return _inner


@pytest.fixture(scope='session')
def make_existing_ticket(make_address):
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
            severity: int = 0,
            service_numbers: List[str] = None,
            site_id: str = '',
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
            "severity": severity,
            "service_numbers": service_numbers,
            "site_id": site_id,
        }

    return _inner


@pytest.fixture(scope='session')
def make_inference_data(make_filter_flags):
    def _inner(
            *,
            potential_service_numbers: List[str] = None,
            filter_flags: Dict[str, Any] = None,
            predicted_class: str = "",
    ):
        filter_flags = filter_flags or make_filter_flags()
        return {
            "potential_service_numbers": potential_service_numbers,
            "predicted_class": predicted_class,
            "filter_flags": filter_flags
        }

    return _inner


@pytest.fixture(scope='session')
def make_inference_request_payload(make_email):
    def _inner(
            *,
            email_data: Dict[str, Any] = None,
            tag_info: Dict[str, Any] = None
    ):
        email_data = email_data or make_email()
        tag_info = tag_info or {"type": "", "probability": ""}
        return {
            "email_id": email_data["email"]["email_id"],
            "client_id": email_data["email"]["client_id"],
            "subject": email_data["email"]["client_id"],
            "body": email_data["email"]["body"],
            "from_address": email_data["email"]["from"],
            "to": email_data["email"]["to"],
            "cc": email_data["email"]["cc"],
            "date": email_data["email"]["date"],
            "tag": {
                "type": tag_info["type"],
                "probability": tag_info["probability"],
            }
        }

    return _inner


@pytest.fixture(scope='session')
def make_rta_ticket_payload():
    def _inner(
            *,
            site_id: str = None,
            service_numbers: List[str] = None,
            ticket_id: str = None,
            not_created_reason: str = None,

    ):
        return {
            "site_id": site_id,
            "service_numbers": service_numbers,
            "ticket_id": ticket_id,
            "not_creation_reason": not_created_reason,
        }
    return _inner


@pytest.fixture(scope='session')
def make_save_outputs_request_payload(make_rta_ticket_payload):
    def _inner(
            *,
            email_id: str = "",
            service_numbers: List[str] = None,
            service_numbers_sites_map: Dict[str, str] = None,
            tickets_created: List[Dict[str, Any]] = None,
            tickets_updated: List[Dict[str, Any]] = None,
            tickets_could_be_created: List[Dict[str, Any]] = None,
            tickets_could_be_updated: List[Dict[str, Any]] = None,
            tickets_cannot_be_created: List[Dict[str, Any]] = None,
    ):
        service_numbers = service_numbers or []
        service_numbers_sites_map = service_numbers_sites_map or {}
        tickets_created = tickets_created or []
        tickets_updated = tickets_updated or []
        tickets_could_be_created = tickets_could_be_created or []
        tickets_could_be_updated = tickets_could_be_updated or []
        tickets_cannot_be_created = tickets_cannot_be_created or []

        return {
            'email_id': email_id,
            'validated_service_numbers': service_numbers,
            'service_numbers_sites_map': service_numbers_sites_map,
            'tickets_created': tickets_created,
            'tickets_updated': tickets_updated,
            'tickets_could_be_created': tickets_could_be_created,
            'tickets_could_be_updated': tickets_could_be_updated,
            'tickets_cannot_be_created': tickets_cannot_be_created,
        }

    return _inner


@pytest.fixture
def make_created_ticket_request_payload():
    def _inner(
            ticket_id: str = "",
            email_id: str = "",
            parent_id: str = "",
            client_id: str = "",
            real_service_numbers: List[str] = None,
            real_class: str = "",
            site_map: Dict[str, Any] = None
    ):
        site_map = site_map or {}
        real_service_numbers = real_service_numbers or []
        return {
            "ticket_id": ticket_id,
            "email_id": email_id,
            "parent_id": parent_id,
            "client_id": client_id,
            "real_service_numbers": real_service_numbers,
            "real_class": real_class,
            "site_map": site_map
        }

    return _inner


@pytest.fixture
def make_closed_ticket_request_payload():
    def _inner(
            ticket_id: str = "",
            client_id: str = "",
            ticket_status: str = "",
            cancellation_reasons: List[str] = None,
    ):
        cancellation_reasons = cancellation_reasons or []
        return {
            "ticket_id": ticket_id,
            "client_id": client_id,
            "ticket_status": ticket_status,
            "cancellation_reasons": cancellation_reasons,
        }

    return _inner
