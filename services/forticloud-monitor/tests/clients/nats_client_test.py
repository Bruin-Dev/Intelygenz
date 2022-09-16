from dataclasses import asdict
from typing import Any, Type
from unittest.mock import AsyncMock, Mock

import pytest
from framework.nats.client import Client
from framework.nats.models import Subscription
from nats.aio.msg import Msg
from pydantic import BaseModel, ValidationError

from clients import NatsClient, NatsConsumer, NatsResponse, NatsSettings, R


class AnyPydanticModel(BaseModel):
    a_string: str
    an_int: int


@pytest.mark.parametrize(
    "payload, serialized_body",
    [
        (
            "any_string",
            b'{"request_id":"any_uuid","body":"any_string"}',
        ),
        (
            AnyPydanticModel(a_string="any_string", an_int=1),
            b'{"request_id":"any_uuid","body":{"a_string":"any_string","an_int":1}}',
        ),
    ],
)
async def nats_requests_are_properly_sent_test(
    payload,
    serialized_body: bytes,
    nats_client_builder,
    any_response_mock,
    any_subject,
):
    # given
    request = any_response_mock
    nats_client = nats_client_builder(request=request)

    # when
    await nats_client.request(any_subject, payload, Any)

    # then
    request.assert_awaited_once_with(any_subject, serialized_body)


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
            NatsResponse(status=300, body=AnyPydanticModel(a_string="any_string", an_int=1)),
            AnyPydanticModel,
        ),
    ],
)
async def nats_responses_are_properly_parsed_test(
    serialized_response: bytes,
    parsed_response: NatsResponse,
    response_body_type: Type[R],
    nats_client_builder,
    any_subject,
    any_payload,
    response_mock,
):
    # given
    nats_client = nats_client_builder(request=response_mock(serialized_response))

    # when
    response = await nats_client.request(any_subject, any_payload, response_body_type)

    # then
    assert response == parsed_response


@pytest.mark.parametrize(
    "serialized_response, response_body_type, expected_exception",
    [
        (b'{"status":200,"body":"not_an_int"}', int, ValueError),
        (b'{"status":300,"body":"not_a_model"}', AnyPydanticModel, ValidationError),
        (b'{"status":300,"body":{"an_int":"not_an_int"}}', AnyPydanticModel, ValidationError),
    ],
)
async def nats_response_parsing_errors_are_properly_propagated_test(
    serialized_response: bytes,
    response_body_type: Type[R],
    expected_exception: Type[Exception],
    nats_client_builder,
    any_subject,
    any_payload,
    response_mock,
):
    # given
    nats_client = nats_client_builder(request=response_mock(serialized_response))

    # then
    with pytest.raises(expected_exception):
        await nats_client.request(any_subject, any_payload, response_body_type)


async def client_errors_are_properly_propagated_test(nats_client_builder, any_subject, any_payload, any_exception):
    # given
    nats_client = nats_client_builder(request=AsyncMock(side_effect=any_exception))

    # then
    with pytest.raises(any_exception):
        await nats_client.request(any_subject, any_payload, Any)


async def consumers_are_properly_subscribed_test(nats_client_builder, any_subscription, any_consumer):
    # given
    subscribe = AsyncMock()
    nats_client = nats_client_builder(subscribe=subscribe)

    any_consumer.subscription = Mock(return_value=any_subscription)

    # when
    await nats_client.add(any_consumer)

    # then
    subscribe.assert_awaited_once_with(**asdict(any_subscription))


async def nats_clients_are_automatically_connected_when_adding_a_consumer_test(nats_client_builder, any_consumer):
    # given
    nats_client = nats_client_builder(is_connected=False)

    # when
    await nats_client.add(any_consumer)

    # then
    assert nats_client.is_connected


async def nats_client_are_only_connected_once_when_adding_multiple_consumers_test(nats_client_builder, any_consumer):
    # given
    connect = AsyncMock()
    nats_client = nats_client_builder(connect=connect)

    # when
    await nats_client.add(any_consumer)
    await nats_client.add(any_consumer)

    # then
    connect.assert_awaited_once()


@pytest.fixture
def nats_client_builder(any_response_mock):
    def builder(
        request: AsyncMock = any_response_mock,
        settings: NatsSettings = NatsSettings(),
        connect: AsyncMock = AsyncMock(),
        subscribe: AsyncMock = AsyncMock(),
        is_connected: bool = False,
    ):
        framework_client = Client(Mock())
        framework_client.request = request
        framework_client.connect = connect
        framework_client.subscribe = subscribe

        nats_client = NatsClient(settings=settings, framework_client=framework_client)
        nats_client.is_connected = is_connected

        return nats_client

    return builder


@pytest.fixture
def any_subject():
    return "any_subject"


@pytest.fixture
def any_payload():
    return AnyPydanticModel(a_string="any_string", an_int=hash("any_int"))


@pytest.fixture
def any_subscription():
    return Subscription(subject="any_subject", queue="any_queue")


@pytest.fixture
def any_consumer(any_subscription):
    any_consumer = Mock(NatsConsumer)
    any_consumer.subscription = Mock(return_value=any_subscription)
    return any_consumer


@pytest.fixture
def any_nats_response():
    return NatsResponse(status=200, body="any_body")


@pytest.fixture
def response_mock():
    def builder(data: bytes):
        return AsyncMock(return_value=Msg(Mock(), data=data))

    return builder


@pytest.fixture
def any_response_mock(response_mock, any_nats_response):
    return response_mock(any_nats_response.json().encode())
