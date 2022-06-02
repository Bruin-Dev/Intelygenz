import pytest


@pytest.fixture
def email_data(make_email):
    return make_email(email_id="12345")["email"]
