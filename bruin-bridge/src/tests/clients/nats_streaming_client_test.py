from src.application.clients.nats_streaming_client import NatsStreamingClient
import pytest
from unittest.mock import Mock
from asynctest import CoroutineMock
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN


class TestNatsStreamingSClient():
    @pytest.mark.asyncio
    async def connect_to_nats_test(self):
        NATS.connect = CoroutineMock()
        STAN.connect = CoroutineMock()
        nats_s_client = NatsStreamingClient()
        await nats_s_client.connect_to_nats()
        assert isinstance(nats_s_client.nc, NATS)
        assert isinstance(nats_s_client.sc, STAN)
        assert nats_s_client.nc.connect.called
        assert nats_s_client.sc.connect.called
        assert nats_s_client.nc.connect.await_args[1] == dict(servers=["nats://nats-streaming:4222"])
        assert nats_s_client.sc.connect.await_args[0] == ("automation-engine-nats", "client-123")
        assert nats_s_client.sc.connect.await_args[1] == dict(nats=nats_s_client.nc)

    @pytest.mark.asyncio
    async def publish_message_test(self):
        nats_s_client = NatsStreamingClient()
        nats_s_client.sc = Mock()
        nats_s_client.sc.publish = CoroutineMock()
        await nats_s_client.publish_message("Test-topic", "Test-message")
        assert nats_s_client.sc.publish.called
        assert nats_s_client.sc.publish.await_args[0] == ("Test-topic", b'Test-message')

    @pytest.mark.asyncio
    async def register_consumer_and_callback_test(self):
        nats_s_client = NatsStreamingClient()
        nats_s_client.subs.clear()
        nats_s_client.sc = Mock()
        message = Mock()
        message.seq = Mock()
        message.data = Mock()
        nats_s_client.sc.subscribe = CoroutineMock(return_value=nats_s_client._cb(message))
        await nats_s_client.register_consumer("Topic")
        assert nats_s_client.sc.subscribe.await_args[0] == ("Topic", )
        assert nats_s_client.sc.subscribe.await_args[1] == dict(start_at="first", cb=nats_s_client._cb )

    @pytest.mark.asyncio
    async def close_nats_connection_test(self):
        nats_s_client = NatsStreamingClient()
        nats_s_client.subs = list()
        sub = Mock()
        sub.unsubscribe = CoroutineMock()
        nats_s_client.subs.append(sub)
        nats_s_client.sc = Mock()
        nats_s_client.nc = Mock()
        nats_s_client.sc.close = CoroutineMock()
        nats_s_client.nc.close = CoroutineMock()
        await nats_s_client.close_nats_connections()
        assert sub.unsubscribe.called and nats_s_client.sc.close.called and nats_s_client.sc.close.called
