from typing import Any, Dict

import pytest
from tests.fixtures.email import *
from tests.fixtures.rta import *


@pytest.fixture
def valid_inference_request(make_email, make_inference_request_payload) -> Dict[str, Any]:
    email_id = "1234"
    client_id = "5689"
    email_data = make_email(email_id=email_id, client_id=client_id, to=["test@marc.com"])
    tag_info = {"type": "Repair", "probability": 0.9}
    return make_inference_request_payload(email_data=email_data, tag_info=tag_info)


@pytest.fixture
def valid_inference_response(make_inference_data) -> Dict[str, Any]:
    potential_service_numbers = ["1234"]
    body = make_inference_data(potential_service_numbers=potential_service_numbers, predicted_class="VOO")
    return {
        "status": 200,
        "body": body,
    }


@pytest.fixture
def valid_output_request(make_save_outputs_request_payload, make_rta_ticket_payload) -> Dict[str, Any]:
    email_id = "1234"
    site_id = "1234"
    ticket_id = "58000"
    service_numbers = ["5689", "91011"]
    service_numbers_site_map = {"5689": "1234", "91011": "1234"}
    ticket_created = make_rta_ticket_payload(
        site_id=site_id,
        service_numbers=service_numbers,
        ticket_id=ticket_id,
    )

    return make_save_outputs_request_payload(
        email_id=email_id,
        service_numbers_sites_map=service_numbers_site_map,
        service_numbers=service_numbers,
        tickets_created=[ticket_created],
    )


@pytest.fixture
def valid_output_response():
    payload = {"success": True}
    return {"status": 200, "body": payload}


@pytest.fixture
def valid_created_ticket_request(make_created_ticket_request_payload):
    return make_created_ticket_request_payload(
        ticket_id="1245",
        email_id="5678",
        parent_id="91011",
        client_id="10000",
        real_service_numbers=["125", "568"],
        real_class="VOO",
        site_map={"125": "1235", "568": "1235"},
    )


@pytest.fixture
def valid_created_ticket_response():
    payload = {"success": True}
    return {"status": 200, "body": payload}


@pytest.fixture
def valid_closed_ticket_request__cancelled(make_closed_ticket_request_payload):
    return make_closed_ticket_request_payload(
        ticket_id="1234",
        client_id="5678",
        ticket_status="cancelled",
        cancelled_reasons=["cancelled cause ai", "duplicated ticket"],
    )


@pytest.fixture
def valid_closed_ticket_request__resolved(make_closed_ticket_request_payload):
    return make_closed_ticket_request_payload(ticket_id="1234", client_id="5678", ticket_status="resolved")


@pytest.fixture
def valid_closed_ticket_response():
    payload = {"success": True}
    return {"status": 200, "body": payload}
