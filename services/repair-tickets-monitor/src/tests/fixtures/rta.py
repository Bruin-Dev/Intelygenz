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
            "from_address": email_data["email"]["from_address"],
            "to": email_data["email"]["to_address"],
            "cc": ', '.join(email_data["email"]["send_cc"]),
            "date": email_data["email"]["date"],
            "tag": {
                "type": tag_info["type"],
                "probability": tag_info["tag_probability"],
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
    ):
        real_service_numbers = real_service_numbers or []
        return {
            "ticket_id": ticket_id,
            "email_id": email_id,
            "parent_id": parent_id,
            "client_id": client_id,
            "real_service_numbers": real_service_numbers,
            "real_class": real_class,
        }

    return _inner
