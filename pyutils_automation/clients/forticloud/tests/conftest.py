from http import HTTPStatus
from unittest.mock import AsyncMock, Mock

import pytest

from forticloud_client.client import ForticloudClient


@pytest.fixture(scope="function")
def forticloud_client():
    config = {"account_id": "", "username": "", "password": "", "base_url": ""}
    forticloud_client = ForticloudClient(config=config)
    return forticloud_client


@pytest.fixture(scope="function")
def login_request():
    response_login = {"access_token": "example token", "expires_in": 3600}
    response_mock = Mock()
    response_mock.status = HTTPStatus.OK
    response_mock.json = AsyncMock(return_value=response_login)
    return response_mock
