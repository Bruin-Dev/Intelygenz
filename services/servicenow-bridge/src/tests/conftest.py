import json
from typing import Any, Callable
from unittest.mock import Mock, create_autospec

import pytest
from framework.nats.client import Client as NatsClient
from nats.aio.msg import Msg


@pytest.fixture(scope="function")
def nats_client():
    return create_autospec(NatsClient)


@pytest.fixture
def make_msg(nats_client: NatsClient) -> Callable[[Any], Msg]:
    def builder(data: Any) -> Msg:
        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(data).encode()
        return msg_mock

    return builder
