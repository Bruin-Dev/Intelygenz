from unittest.mock import AsyncMock, Mock

import pytest
from framework.nats.client import Client as FrameworkClient
from framework.nats.models import Subscription

from application.clients import NatsClient, NatsConsumer, NatsSettings


async def consumers_are_properly_subscribed_test(any_nats_client, any_subscription, any_consumer):
    # given
    subscribe = AsyncMock()
    nats_client = any_nats_client(subscribe=subscribe)

    any_consumer.subscription = Mock(return_value=any_subscription)

    # when
    await nats_client.add(any_consumer)

    # then
    subscribe.assert_awaited_once_with(**any_subscription.__dict__)


async def nats_clients_are_properly_connected_test(any_nats_client, any_nats_settings):
    # given
    connect = AsyncMock()
    any_nats_settings.servers = ["any_server"]
    nats_client = any_nats_client(connect=connect, settings=any_nats_settings)

    # when
    await nats_client.connect()

    # then
    connect.assert_awaited_once_with(servers=["any_server"])


async def nats_clients_are_properly_closed_test(any_nats_client):
    # given
    close = AsyncMock()
    nats_client = any_nats_client(close=close)

    # when
    await nats_client.close()

    # then
    close.assert_awaited_once()


@pytest.fixture
def any_nats_client(any_nats_settings):
    def builder(
        settings: NatsSettings = any_nats_settings,
        connect: AsyncMock = AsyncMock(),
        subscribe: AsyncMock = AsyncMock(),
        close: AsyncMock = AsyncMock(),
    ):
        framework_client = FrameworkClient(Mock())
        framework_client.connect = connect
        framework_client.subscribe = subscribe
        framework_client.close = close

        return NatsClient(settings=settings, framework_client=framework_client)

    return builder


@pytest.fixture
def any_nats_settings():
    return NatsSettings(servers=["any_server"])


@pytest.fixture
def any_subscription():
    return Subscription(subject="any_subject", queue="any_queue")


@pytest.fixture
def any_consumer(any_subscription):
    any_consumer = Mock(NatsConsumer)
    any_consumer.subscription = Mock(return_value=any_subscription)
    return any_consumer
