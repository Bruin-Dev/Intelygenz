from typing import Any
from typing import Dict

import pytest


# Factories
@pytest.fixture(scope='session')
def make_rpc_request():
    def _inner(*, request_id: str = None, **body: Dict[str, Any]):
        return {
            'request_id': request_id,
            'body': body,
        }

    return _inner


@pytest.fixture(scope='session')
def make_rpc_response():
    def _inner(*, request_id: str = None, body: Any, status: int):
        return {
            'request_id': request_id,
            'body': body,
            'status': status,
        }

    return _inner
