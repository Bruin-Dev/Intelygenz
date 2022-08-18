from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from aiohttp import ClientResponse


# Factories
@pytest.fixture(scope="function")
def client_response() -> ClientResponse:
    def _inner(*, body: Any, status: int):
        client_response = Mock(ClientResponse)
        client_response.json = AsyncMock(return_value=body)
        client_response.body = body
        client_response.status = status

        return client_response

    return _inner
