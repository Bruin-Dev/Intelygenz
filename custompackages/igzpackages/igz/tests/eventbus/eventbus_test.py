from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.nats.clients import NatsStreamingClient
import pytest
from asynctest import CoroutineMock
from igz.config import testconfig as config
from igz.packages.Logger.logger_client import LoggerClient


class TestEventBus:

    logger = LoggerClient(config).get_logger()

    def instantiation_test(self):
        e = EventBus(self.logger)
        assert isinstance(e._consumers, dict)

    @pytest.mark.asyncio
    async def connect_OK_test(self):
        e = EventBus(self.logger)
        subscriber = NatsStreamingClient(config, "Some-subs-ID", self.logger)
        publisher = NatsStreamingClient(config, "Some-pub-ID", self.logger)

        sub_connect_mock = CoroutineMock()
        pub_connect_mock = CoroutineMock()

        subscriber.connect_to_nats = sub_connect_mock
        publisher.connect_to_nats = pub_connect_mock

        e.add_consumer(subscriber, "Some-name")
        e.set_producer(publisher)

        await e.connect()
        assert sub_connect_mock.called
        assert pub_connect_mock.called

    def add_consumer_OK_test(self):
        e = EventBus(self.logger)
        subscriber = NatsStreamingClient(config, "Some-subs-ID", self.logger)
        e.add_consumer(subscriber, "some-name")

        assert e._consumers["some-name"] is subscriber

    def add_consumer_KO_repeated_test(self):
        e = EventBus(self.logger)
        first_subscriber = NatsStreamingClient(config, "Some-subs-ID", self.logger)
        second_subscriber = NatsStreamingClient(config, "Some-subs-ID-2", self.logger)
        e.add_consumer(first_subscriber, "some-name")
        e.add_consumer(second_subscriber, "some-name")

        assert e._consumers["some-name"] is first_subscriber
        assert e._consumers["some-name"] is not second_subscriber

    def set_producer_OK_test(self):
        e = EventBus(self.logger)
        publisher = NatsStreamingClient(config, "Some-pub-ID", self.logger)
        e.set_producer(publisher)
        assert e._producer is publisher

    @pytest.mark.asyncio
    async def subscribe_consumer_OK_test(self):
        e = EventBus(self.logger)
        subscriber = NatsStreamingClient(config, "Some-subs-ID", self.logger)
        subscribe_action_mock = CoroutineMock()
        action_mock = ActionWrapper(self.logger, None, "")
        subscriber.subscribe_action = subscribe_action_mock
        e.add_consumer(subscriber, "Some-name")
        await e.subscribe_consumer("Some-name", "Some-topic", action_mock)
        assert subscribe_action_mock.called
        assert subscribe_action_mock.call_args[0] == ('Some-topic', action_mock, 'first', None, None, None, None)

    @pytest.mark.asyncio
    async def publish_message_OK_test(self):
        e = EventBus(self.logger)
        publisher = NatsStreamingClient(config, "Some-pub-ID", self.logger)
        publish_mock = CoroutineMock()
        publisher.publish = publish_mock
        e.set_producer(publisher)
        await e.publish_message("some-topic", "some-message")
        assert publish_mock.called
        assert publish_mock.call_args[0] == ("some-topic", "some-message")

    @pytest.mark.asyncio
    async def close_connections_OK_test(self):
        e = EventBus(self.logger)
        subscriber = NatsStreamingClient(config, "Some-subs-ID", self.logger)
        publisher = NatsStreamingClient(config, "Some-pub-ID", self.logger)

        sub_disconnect_mock = CoroutineMock()
        pub_disconnect_mock = CoroutineMock()

        subscriber.close_nats_connections = sub_disconnect_mock
        publisher.close_nats_connections = pub_disconnect_mock

        e.add_consumer(subscriber, "Some-name")
        e.set_producer(publisher)

        await e.close_connections()
        assert sub_disconnect_mock.called
        assert pub_disconnect_mock.called
