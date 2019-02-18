from src.application.clients.nats_streaming_client import NatsStreamingClient
import pytest
from unittest.mock import MagicMock
from asynctest import CoroutineMock
from asgiref.sync import sync_to_async
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN


class TestNatsStreamingSClient():
    @pytest.mark.asyncio
    async def connect_to_nats_test(self):
        NATS.connect = sync_to_async(MagicMock())
        STAN.connect = sync_to_async(MagicMock())
        nats_s_client = NatsStreamingClient()
        await nats_s_client.connect_to_nats()
        assert isinstance(nats_s_client.nc, NATS)
        assert isinstance(nats_s_client.sc, STAN)

    @pytest.mark.asyncio
    async def publish_message_test(self):
        nats_s_client = NatsStreamingClient()
        nats_s_client.sc = MagicMock()
        nats_s_client.sc.publish = CoroutineMock()
        await nats_s_client.publish_message("Test-topic", "Test-message")
        assert nats_s_client.sc.publish.called == True
        assert nats_s_client.sc.publish.await_args[0] == ("Test-topic", b'Test-message')
