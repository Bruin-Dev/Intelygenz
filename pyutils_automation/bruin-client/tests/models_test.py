from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from models import BruinCredentials, BruinToken


@patch("models.base64")
def bruin_credentials_are_properly_encoded_test(base64):
    # given
    bruin_credentials = BruinCredentials(client_id="any_client_id", client_secret="any_client_secret")
    base64.b64encode = Mock(return_value=b"any_b64encode")

    # when
    bruin_credentials.b64encoded()

    # then
    base64.b64encode.assert_called_once_with(b"any_client_id:any_client_secret")


@patch("models.base64")
def encoded_bruin_credentials_are_properly_returned_test(base64):
    # given
    bruin_credentials = BruinCredentials(client_id="any_client_id", client_secret="any_client_secret")
    base64.b64encode = Mock(b"any_base64_credentials")

    # then
    bruin_credentials.b64encoded() == "any_base64_credentials"


@patch("models.datetime")
@pytest.mark.parametrize(
    ["issued_at", "expires_in", "utcnow", "is_expired"],
    [
        (datetime(1, 1, 1, hour=0), 3600, datetime(1, 1, 1, hour=0, minute=30), False),
        (datetime(1, 1, 1, hour=0), 3600, datetime(1, 1, 1, hour=1), True),
        (datetime(1, 1, 1, hour=0), 3600, datetime(1, 1, 1, hour=2), True),
    ],
    ids=[
        "valid value",
        "just expired value",
        "expired value",
    ],
)
def token_expiration_is_properly_detected_test(_datetime, issued_at, expires_in, utcnow, is_expired):
    # given
    bruin_token = BruinToken(expires_in=expires_in)
    bruin_token.issued_at = issued_at
    _datetime.utcnow = Mock(return_value=utcnow)

    # then
    assert bruin_token.is_expired() == is_expired
