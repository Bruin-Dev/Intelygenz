from typing import Any, Dict

import pytest


@pytest.fixture(scope="session")
def make_rpc_request():
    def _inner(*, request_id: str, body: Dict[str, int]):
        request = {
            "request_id": request_id,
            "body": body,
        }
        return request

    return _inner


@pytest.fixture(scope="session")
def make_rpc_response():
    def _inner(*, request_id: str, body: Dict[str, int], status: int):
        return {
            "request_id": request_id,
            "body": body,
            "status": status,
        }

    return _inner
