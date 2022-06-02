from typing import Any, Dict

import pytest


# Model-as-dict generators
def __generate_rpc_request(*, request_id: str = None, **body: Dict[str, Any]):
    return {
        "request_id": request_id,
        "body": body,
    }


def __generate_rpc_response(*, request_id: str = None, body: Any, status: int):
    return {
        "request_id": request_id,
        "body": body,
        "status": status,
    }


# Factories
@pytest.fixture(scope="session")
def make_rpc_request():
    def _inner(*, request_id: str = None, **body: Dict[str, Any]):
        return __generate_rpc_request(request_id=request_id, **body)

    return _inner


@pytest.fixture(scope="session")
def make_rpc_response():
    def _inner(*, request_id: str = None, body: Any, status: int):
        return __generate_rpc_response(request_id=request_id, body=body, status=status)

    return _inner
