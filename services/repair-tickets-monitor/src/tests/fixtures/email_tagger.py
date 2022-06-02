from datetime import datetime
from typing import List

import pytest
from tests.fixtures._helpers import bruinize_date


@pytest.fixture(scope="session")
def make_email():
    def _inner(
        *,
        email_id: int = 0,
        parent_id: int = 0,
        client_id: int = 0,
        body: str = "",
        subject: str = "",
        from_address: str = "",
        received_date: datetime = None,
        send_cc: List[str] = None,
        to_address: List[str] = None,
    ):
        send_cc = send_cc or []
        to_address = to_address or []
        received_date = received_date or bruinize_date(datetime.utcnow())

        return {
            "email": {
                "email_id": email_id,
                "parent_id": parent_id,
                "client_id": client_id,
                "body": body,
                "from_address": from_address,
                "to_address": to_address,
                "send_cc": send_cc,
                "date": received_date,
                "subject": subject,
            }
        }

    return _inner


@pytest.fixture(scope="session")
def make_email_tag_info(make_email):
    def builder():
        email = make_email().get("email")
        email["tag_probability"] = hash("any_probability")
        return email

    return builder
