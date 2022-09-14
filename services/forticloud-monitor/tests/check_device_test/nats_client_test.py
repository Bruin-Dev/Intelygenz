from typing import Any, Callable, Type
from unittest.mock import AsyncMock, Mock

import pytest
from check_device_test.fixtures import CustomException
from framework.nats.client import Client
from nats.aio.msg import Msg
from pydantic import BaseModel, ValidationError

from check_device.nats_client import NatsClient, NatsResponse, R


class AnySchema(BaseModel):
    a_string: str
    an_int: int


class AnyBody(BaseModel):
    a_string: str = "any_string"
    an_int: int = 1


@pytest.mark.parametrize(
    "a_body, serialized_body",
    [
        ("any_string", b'{"request_id":"any_uuid","body":"any_string"}'),
        (AnyBody(), b'{"request_id":"any_uuid","body":{"a_string":"any_string","an_int":1}}'),
    ],
)
async def nats_requests_are_properly_sent_test(
    a_body: Any,
    serialized_body: bytes,
    nats_client: NatsClient,
):
    # given
    a_subject = "any_subject"
    a_response = NatsResponse(status=hash("any_status"), body=AnyBody())
    nats_client.framework_client.request = ResponseMock(a_response.json().encode())

    # when
    await nats_client.request(a_subject, a_body, type(a_response.body))

    # then
    nats_client.framework_client.request.assert_awaited_once_with(a_subject, serialized_body)


@pytest.mark.parametrize(
    "serialized_response, parsed_response, response_body_type",
    [
        (b'{"status":200,"body":"1"}', NatsResponse(status=200, body=1), int),
        (
            b'{"status":300,"body":{"a_string":"any_string","an_int":"1"}}',
            NatsResponse(status=300, body=AnyBody()),
            AnyBody,
        ),
    ],
)
async def nats_responses_are_properly_parsed_test(
    serialized_response: bytes,
    parsed_response: NatsResponse,
    response_body_type: Type[R],
    nats_client: NatsClient,
):
    # given
    nats_client.framework_client.request = ResponseMock(serialized_response)

    # when
    a_response = await nats_client.request("any_subject", AnyBody(), response_body_type)

    # then
    assert a_response == parsed_response


@pytest.mark.parametrize(
    "serialized_response, response_body_type, expected_exception",
    [
        (b'{"status":200,"body":"not_an_int"}', int, ValueError),
        (b'{"status":300,"body":{"an_int":"not_an_int"}}', AnySchema, ValidationError),
    ],
)
async def nats_response_parsing_errors_are_properly_propagated_test(
    serialized_response: bytes,
    response_body_type: Type[R],
    expected_exception: Type[Exception],
    nats_client: NatsClient,
):
    nats_client.framework_client.request = ResponseMock(serialized_response)

    # then
    with pytest.raises(expected_exception):
        await nats_client.request("any_subject", AnyBody(), response_body_type)


async def client_errors_are_properly_propagated_test(nats_client: NatsClient):
    # given
    nats_client.framework_client.request = AsyncMock(side_effect=CustomException)

    # then
    with pytest.raises(CustomException):
        await nats_client.request("any_subject", AnyBody(), Any)


class ResponseMock(AsyncMock):
    def __init__(self, data: bytes):
        super().__init__(return_value=Msg(Mock(), data=data))


@pytest.fixture
def nats_client() -> NatsClient:
    return NatsClient(Mock(Client))


@pytest.fixture
def make_msg() -> Callable[..., Msg]:
    def builder(status: int = 200, body: Any = 1):
        nats_response = NatsResponse(status=status, body=body)
        msg = Mock(Msg)
        msg.data = nats_response.json().encode()
        return msg

    return builder
