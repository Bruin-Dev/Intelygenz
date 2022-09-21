from unittest.mock import AsyncMock, Mock

import pytest
from framework.nats.client import Client as FrameworkClient
from framework.nats.models import Subscription

from clients import NatsClient, NatsConsumer, NatsSettings


async def consumers_are_properly_subscribed_test(nats_client_builder, any_subscription, any_consumer):
    # given
    subscribe = AsyncMock()
    nats_client = nats_client_builder(subscribe=subscribe)

    any_consumer.subscription = Mock(return_value=any_subscription)

    # when
    await nats_client.add(any_consumer)

    # then
    subscribe.assert_awaited_once_with(**any_subscription.__dict__)


@pytest.fixture
def nats_client_builder(any_nats_settings):
    def builder(
        settings: NatsSettings = any_nats_settings,
        connect: AsyncMock = AsyncMock(),
        subscribe: AsyncMock = AsyncMock(),
        is_connected: bool = False,
    ):
        framework_client = FrameworkClient(Mock())
        framework_client.connect = connect
        framework_client.subscribe = subscribe

        nats_client = NatsClient(settings=settings, framework_client=framework_client)
        nats_client.is_connected = is_connected

        return nats_client

    return builder


@pytest.fixture
def any_nats_settings():
    return NatsSettings(servers=["any_server"])


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
