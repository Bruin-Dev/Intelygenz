from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.nats.clients import NATSClient
import pytest
from asynctest import CoroutineMock
from igz.config import testconfig as config
from unittest.mock import Mock
import logging

from datetime import datetime


class TestEventBus:

    def instantiation_test(self):
        mock_logger = Mock()
        event_bus1 = EventBus()
        event_bus2 = EventBus(logger=mock_logger)

        assert isinstance(event_bus1._consumers, dict)
        assert isinstance(event_bus1._logger, logging._loggerClass)
        assert event_bus1._logger.hasHandlers() is True
        assert event_bus1._logger.getEffectiveLevel() == 10
        assert event_bus2._logger is mock_logger

    @pytest.mark.asyncio
    async def connect_OK_test(self):
        mock_logger = Mock()
        event_bus = EventBus(logger=mock_logger)
        subscriber = NATSClient(config, logger=mock_logger)
        publisher = NATSClient(config, logger=mock_logger)
        sub_connect_mock = CoroutineMock()
        pub_connect_mock = CoroutineMock()

        subscriber.connect_to_nats = sub_connect_mock
        publisher.connect_to_nats = pub_connect_mock

        event_bus.add_consumer(subscriber, consumer_name="Some-name")
        event_bus.set_producer(publisher)

        await event_bus.connect()

        sub_connect_mock.assert_awaited_once()
        pub_connect_mock.assert_awaited_once()

    @pytest.mark.asyncio
    async def rpc_request_test(self):
        mock_logger = Mock()
        event_bus = EventBus(logger=mock_logger)
        publisher = NATSClient(config, logger=mock_logger)
        publisher.rpc_request = CoroutineMock()

        event_bus.set_producer(publisher)

        await event_bus.rpc_request(
            topic="some_topic",
            message={'msg': "some_message"},
            timeout=10
        )

        publisher.rpc_request.assert_awaited_once_with(
            "some_topic", '{"msg":"some_message"}', 10
        )

    @pytest.mark.asyncio
    async def rpc_request_with_complex_datatypes_test(self):
        mock_logger = Mock()
        event_bus = EventBus(logger=mock_logger)
        publisher = NATSClient(config, logger=mock_logger)
        publisher.rpc_request = CoroutineMock()

        event_bus.set_producer(publisher)

        await event_bus.rpc_request(
            topic="some_topic",
            message={'epoch_time': datetime(1970, 1, 1, 0, 0, 0)},
            timeout=10
        )

        publisher.rpc_request.assert_awaited_once_with(
            "some_topic", '{"epoch_time":"1970-01-01 00:00:00"}', 10,
        )

    def add_consumer_OK_test(self):
        mock_logger = Mock()
        event_bus = EventBus(logger=mock_logger)
        subscriber = NATSClient(config, logger=mock_logger)

        event_bus.add_consumer(subscriber, consumer_name="some-name")

        assert event_bus._consumers["some-name"] is subscriber

    def add_consumer_KO_repeated_test(self):
        mock_logger = Mock()
        event_bus = EventBus(logger=mock_logger)
        first_subscriber = NATSClient(config, logger=mock_logger)
        second_subscriber = NATSClient(config, logger=mock_logger)
        event_bus._logger.error = Mock()

        event_bus.add_consumer(first_subscriber, consumer_name="some-name")
        event_bus.add_consumer(second_subscriber, consumer_name="some-name")

        event_bus._logger.error.assert_called()
        assert event_bus._consumers["some-name"] is first_subscriber
        assert event_bus._consumers["some-name"] is not second_subscriber

    def set_producer_OK_test(self):
        mock_logger = Mock()
        event_bus = EventBus(logger=mock_logger)
        publisher = NATSClient(config, logger=mock_logger)

        event_bus.set_producer(publisher)

        assert event_bus._producer is publisher

    @pytest.mark.asyncio
    async def subscribe_consumer_OK_test(self):
        mock_logger = Mock()
        event_bus = EventBus(logger=mock_logger)
        subscriber = NATSClient(config, logger=mock_logger)
        action_mock = ActionWrapper(
            state_instance=None,
            target_function="",
            logger=mock_logger,
        )
        subscribe_action_mock = CoroutineMock()
        subscriber.subscribe_action = subscribe_action_mock

        event_bus.add_consumer(subscriber, consumer_name="Some-name")
        await event_bus.subscribe_consumer(
            consumer_name="Some-name",
            topic="Some-topic",
            action_wrapper=action_mock,
            queue="",
        )

        subscribe_action_mock.assert_awaited_once_with(
            "Some-topic", action_mock, "",
        )

    @pytest.mark.asyncio
    async def publish_message_test(self):
        mock_logger = Mock()
        event_bus = EventBus(logger=mock_logger)
        publisher = NATSClient(config, logger=mock_logger)
        publisher.publish = CoroutineMock()

        event_bus.set_producer(publisher)

        await event_bus.publish_message(
            topic="some_topic", msg={'msg': "some_message"}
        )

        publisher.publish.assert_awaited_once_with("some_topic", '{"msg":"some_message"}')

    @pytest.mark.asyncio
    async def publish_message_with_complex_datatypes_test(self):
        mock_logger = Mock()
        event_bus = EventBus(logger=mock_logger)
        publisher = NATSClient(config, logger=mock_logger)
        publisher.publish = CoroutineMock()

        event_bus.set_producer(publisher)

        await event_bus.publish_message(
            topic="some_topic", msg={'epoch_time': datetime(1970, 1, 1, 0, 0, 0)}
        )

        publisher.publish.assert_awaited_once_with("some_topic", '{"epoch_time":"1970-01-01 00:00:00"}')

    @pytest.mark.asyncio
    async def close_connections_OK_test(self):
        mock_logger = Mock()
        event_bus = EventBus(logger=mock_logger)
        subscriber = NATSClient(config, logger=mock_logger)
        publisher = NATSClient(config, logger=mock_logger)
        sub_disconnect_mock = CoroutineMock()
        pub_disconnect_mock = CoroutineMock()
        subscriber.close_nats_connections = sub_disconnect_mock
        publisher.close_nats_connections = pub_disconnect_mock

        event_bus.add_consumer(subscriber, consumer_name="Some-name")
        event_bus.set_producer(publisher)

        await event_bus.close_connections()

        sub_disconnect_mock.assert_awaited()
        pub_disconnect_mock.assert_awaited()
