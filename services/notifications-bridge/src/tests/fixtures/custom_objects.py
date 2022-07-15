from typing import Any

import pytest
from aiohttp import ClientResponse
from asynctest import CoroutineMock, Mock


# Factories
@pytest.fixture(scope="function")
def client_response() -> ClientResponse:
    def _inner(*, body: Any, status: int):
        client_response = Mock(ClientResponse)
        client_response.json = CoroutineMock(return_value=body)
        client_response.status = status

        return client_response

    return _inner
