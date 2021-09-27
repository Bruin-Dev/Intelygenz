from typing import Any, Dict
import pytest


@pytest.fixture(scope='session')
def make_rpc_request():
    def _inner(*, request_id: str = None, response_topic: str = None, **body: Dict[str, Any]):
        request = {
            'request_id': request_id,
            'response_topic': response_topic,
        }
        if body:
            request['body'] = body
        return request

    return _inner
