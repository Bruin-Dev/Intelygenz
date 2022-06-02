from datetime import datetime
from typing import List

import pytest
from tests.fixtures._helpers import bruinize_date


@pytest.fixture(scope="session")
def make_email():
    def _inner(
        *,
        email_id: int = 0,
        client_id: int = 0,
        body: str = "",
        received_date: str = "",
        subject: str = "",
        from_address: str = "",
        cc: str = "",
        to: List[str] = None,
    ):
        to = to or []
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
