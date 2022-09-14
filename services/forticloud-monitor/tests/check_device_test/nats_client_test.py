from typing import Any, Type
from unittest.mock import AsyncMock, Mock

import pytest
from check_device_test.fixtures import AnyBaseModel, AnyNatsResponse, CustomException
from framework.nats.client import Client
from nats.aio.msg import Msg
from pydantic import ValidationError

from check_device.nats_client import NatsClient, NatsResponse, R, Settings

any_subject = "any_subject"
any_payload = AnyBaseModel(a_string="any_string", an_int=hash("any_int"))


@pytest.mark.parametrize(
    "payload, serialized_body",
    [
        (
            "any_string",
            b'{"request_id":"any_uuid","body":"any_string"}',
        ),
        (
            AnyBaseModel(a_string="any_string", an_int=1),
            b'{"request_id":"any_uuid","body":{"a_string":"any_string","an_int":1}}',
        ),
    ],
)
async def nats_requests_are_properly_sent_test(
    payload,
    serialized_body: bytes,
    nats_client_builder,
):
    # given
    request = AnyResponseMock()
    nats_client = nats_client_builder(request=request)

    # when
    await nats_client.request("any_subject", payload, Any)

    # then
    request.assert_awaited_once_with("any_subject", serialized_body)


@pytest.mark.parametrize(
    "serialized_response, parsed_response, response_body_type",
    [
        (
            b'{"status":200,"body":"1"}',
            NatsResponse(status=200, body=1),
            int,
        ),
        (
            b'{"status":300,"body":{"a_string":"any_string","an_int":"1"}}',
            NatsResponse(status=300, body=AnyBaseModel(a_string="any_string", an_int=1)),
            AnyBaseModel,
        ),
    ],
)
async def nats_responses_are_properly_parsed_test(
    serialized_response: bytes,
    parsed_response: NatsResponse,
    response_body_type: Type[R],
    nats_client_builder,
):
    # given
    nats_client = nats_client_builder(request=ResponseMock(serialized_response))

    # when
    response = await nats_client.request(any_subject, any_payload, response_body_type)

    # then
    assert response == parsed_response


@pytest.mark.parametrize(
    "serialized_response, response_body_type, expected_exception",
    [
        (b'{"status":200,"body":"not_an_int"}', int, ValueError),
        (b'{"status":300,"body":"not_a_base_model"}', AnyBaseModel, ValidationError),
        (b'{"status":300,"body":{"an_int":"not_an_int"}}', AnyBaseModel, ValidationError),
    ],
)
async def nats_response_parsing_errors_are_properly_propagated_test(
    serialized_response: bytes,
    response_body_type: Type[R],
    expected_exception: Type[Exception],
    nats_client_builder,
):
    # given
    nats_client = nats_client_builder(request=ResponseMock(serialized_response))

    # then
    with pytest.raises(expected_exception):
        await nats_client.request(any_subject, any_payload, response_body_type)


async def client_errors_are_properly_propagated_test(nats_client_builder):
    # given
    nats_client = nats_client_builder(request=AsyncMock(side_effect=CustomException))

    # then
    with pytest.raises(CustomException):
        await nats_client.request(any_subject, any_payload, Any)


class ResponseMock(AsyncMock):
    def __init__(self, data: bytes):
        super().__init__(return_value=Msg(Mock(), data=data))


class AnyResponseMock(ResponseMock):
    def __init__(self):
        super().__init__(AnyNatsResponse().json().encode())


@pytest.fixture
def nats_client_builder():
    def builder(request: AsyncMock = AnyResponseMock(), settings: Settings = Settings()):
        framework_client = Client(Mock())
        framework_client.request = request

        return NatsClient(settings=settings, framework_client=framework_client)

    return builder
