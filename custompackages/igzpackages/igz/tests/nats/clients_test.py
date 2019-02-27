from igz.packages.nats.clients import NatsStreamingClient
import pytest
from unittest.mock import Mock
from asynctest import CoroutineMock
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN
from igz.config import testconfig as config


class TestNatsStreamingClient():
    @pytest.mark.asyncio
    async def connect_to_nats_test(self):
        NATS.connect = CoroutineMock()
        STAN.connect = CoroutineMock()
        nats_s_client = NatsStreamingClient(config)
        await nats_s_client.connect_to_nats()
        assert isinstance(nats_s_client._nc, NATS)
        assert isinstance(nats_s_client._sc, STAN)
        assert nats_s_client._nc.connect.called
        assert nats_s_client._sc.connect.called
        assert nats_s_client._nc.connect.await_args[1] == dict(servers=config.NATS_CONFIG["servers"])
        assert nats_s_client._sc.connect.await_args[0] == (config.NATS_CONFIG["cluster_name"],
                                                           config.NATS_CONFIG["client_ID"],)
        max_pub_acks = config.NATS_CONFIG["publisher"]["max_pub_acks_inflight"]
        assert nats_s_client._sc.connect.await_args[1] == dict(nats=nats_s_client._nc,
                                                               max_pub_acks_inflight=max_pub_acks)

    @pytest.mark.asyncio
    async def publish_message_test(self):
        nats_s_client = NatsStreamingClient(config)
        nats_s_client._sc = Mock()
        nats_s_client._sc.publish = CoroutineMock()
        await nats_s_client.publish("Test-topic", "Test-message")
        assert nats_s_client._sc.publish.called
        assert nats_s_client._sc.publish.await_args[0] == ("Test-topic", b'Test-message')

    # TO DO #
    @pytest.mark.asyncio
    async def register_sequence_consumer_test(self):
        nats_s_client = NatsStreamingClient(config)
        nats_s_client._subs.clear()
        nats_s_client._sc = Mock()
        nats_s_client._sc.ack = CoroutineMock()
        message = Mock()
        message.seq = Mock()
        message.data = Mock()
        message.sub = Mock()
        message.sub.subject = "Test-topic"
        caller_callback = Mock()
        nats_s_client._sc.subscribe = CoroutineMock(return_value=nats_s_client._cb_with_ack(message))
        await nats_s_client.subscribe("Test-topic", caller_callback, sequence=[1, 2, 3, 4])
        assert nats_s_client._sc.subscribe.await_args[1]['sequence'] == [1, 2, 3, 4]

    @pytest.mark.asyncio
    async def register_time_consumer_test(self):
        nats_s_client = NatsStreamingClient(config)
        nats_s_client._subs.clear()
        nats_s_client._sc = Mock()
        nats_s_client._sc.ack = CoroutineMock()
        message = Mock()
        message.seq = Mock()
        message.data = Mock()
        message.sub = Mock()
        message.sub.subject = "Test-topic"
        caller_callback = Mock()
        nats_s_client._sc.subscribe = CoroutineMock(return_value=nats_s_client._cb_with_ack(message))
        await nats_s_client.subscribe("Test-topic", caller_callback, time='2/27/2019')
        assert nats_s_client._sc.subscribe.await_args[1]['time'] == '2/27/2019'

    @pytest.mark.asyncio
    async def register_durable_name_consumer_test(self):
        nats_s_client = NatsStreamingClient(config)
        nats_s_client._subs.clear()
        nats_s_client._sc = Mock()
        nats_s_client._sc.ack = CoroutineMock()
        message = Mock()
        message.seq = Mock()
        message.data = Mock()
        message.sub = Mock()
        message.sub.subject = "Test-topic"
        caller_callback = Mock()
        nats_s_client._sc.subscribe = CoroutineMock(return_value=nats_s_client._cb_with_ack(message))
        await nats_s_client.subscribe("Test-topic", caller_callback, durable_name='Test_Name')
        assert nats_s_client._sc.subscribe.await_args[1]['durable_name'] == 'Test_Name'
    ##########################################

    @pytest.mark.asyncio
    async def register_basic_consumer_and_callback_test(self):
        nats_s_client = NatsStreamingClient(config)
        nats_s_client._subs.clear()
        nats_s_client._sc = Mock()
        nats_s_client._sc.ack = CoroutineMock()
        message = Mock()
        message.seq = Mock()
        message.data = Mock()
        message.sub = Mock()
        message.sub.subject = "Test-topic"
        caller_callback = Mock()
        nats_s_client._sc.subscribe = CoroutineMock(return_value=nats_s_client._cb_with_ack(message))
        await nats_s_client.subscribe("Test-topic", caller_callback)
        assert nats_s_client._topic_action["Test-topic"] == caller_callback
        assert nats_s_client._sc.subscribe.await_args[0] == ("Test-topic",)
        assert nats_s_client._sc.subscribe.await_args[1] == dict(start_at='first',
                                                                 time=None,
                                                                 sequence=None,
                                                                 queue=None,
                                                                 durable_name=None,
                                                                 cb=nats_s_client._cb_with_ack,
                                                                 manual_acks=True,
                                                                 max_inflight=config.NATS_CONFIG["subscriber"][
                                                                     "max_inflight"],
                                                                 pending_limits=config.NATS_CONFIG["subscriber"][
                                                                     "pending_limits"]
                                                                 )

    @pytest.mark.asyncio
    async def close_nats_connection_test(self):
        nats_s_client = NatsStreamingClient(config)
        nats_s_client._subs = list()
        sub = Mock()
        sub.unsubscribe = CoroutineMock()
        nats_s_client._subs.append(sub)
        nats_s_client._sc = Mock()
        nats_s_client._nc = Mock()
        nats_s_client._sc.close = CoroutineMock()
        nats_s_client._nc.close = CoroutineMock()
        await nats_s_client.close_nats_connections()
        assert sub.unsubscribe.called and nats_s_client._sc.close.called and nats_s_client._nc.close.called
