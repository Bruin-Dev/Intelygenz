from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.action import ActionWrapper
import pytest
from unittest.mock import Mock
from asynctest import CoroutineMock
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN
from igz.config import testconfig as config
import logging
from tenacity import RetryError


class TestNatsStreamingClient:
    attempts = 0

    def instantiation_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id")
        nats_s_client_2 = NatsStreamingClient(config, "test-client-id-2", logger=mock_logger)
        client_id = "test-client-id" + nats_s_client._uuid
        assert nats_s_client._config == config.NATS_CONFIG
        assert nats_s_client._client_id == client_id
        assert isinstance(nats_s_client._logger, logging._loggerClass) is True
        assert nats_s_client._logger.hasHandlers() is True
        assert nats_s_client._logger.getEffectiveLevel() is 10
        assert nats_s_client_2._logger is mock_logger

    @pytest.mark.asyncio
    async def connect_to_nats_test(self):
        NATS.connect = CoroutineMock()
        STAN.connect = CoroutineMock()
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
        client_id = "test-client-id" + nats_s_client._uuid
        await nats_s_client.connect_to_nats()
        assert isinstance(nats_s_client._nc, NATS)
        assert isinstance(nats_s_client._sc, STAN)
        assert nats_s_client._nc.connect.called
        assert nats_s_client._sc.connect.called
        assert nats_s_client._nc.connect.await_args[1] == dict(servers=config.NATS_CONFIG["servers"],
                                                               max_reconnect_attempts=config.NATS_CONFIG["reconnects"])
        assert nats_s_client._sc.connect.await_args[0] == (config.NATS_CONFIG["cluster_name"],)
        max_pub_acks = config.NATS_CONFIG["publisher"]["max_pub_acks_inflight"]
        assert nats_s_client._sc.connect.await_args[1] == dict(nats=nats_s_client._nc,
                                                               max_pub_acks_inflight=max_pub_acks,
                                                               client_id=client_id)

    @pytest.mark.asyncio
    async def connect_to_nats_retry_test(self):
        NATS.connect = CoroutineMock(side_effect=Exception())
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
        try:
            await nats_s_client.connect_to_nats()
        except Exception as e:
            error = e
        assert isinstance(error, RetryError)
        assert NATS.connect.call_count > 1

    @pytest.mark.asyncio
    async def publish_message_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
        nats_s_client._nc = Mock()
        nats_s_client._nc.is_connected = True
        nats_s_client._sc = Mock()
        nats_s_client._sc.publish = CoroutineMock()
        await nats_s_client.publish("Test-topic", "Test-message")
        assert nats_s_client._sc.publish.called
        assert nats_s_client._sc.publish.await_args[0] == ("Test-topic", b'Test-message')

    @pytest.mark.asyncio
    async def publish_message_retry_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
        nats_s_client._nc = Mock()
        nats_s_client._nc.is_connected = True
        nats_s_client._sc = Mock()
        nats_s_client._sc.publish = CoroutineMock(side_effect=Exception())
        try:
            await nats_s_client.publish("Test-topic", "Test-message")
        except Exception as e:
            error = e
        assert isinstance(error, RetryError)
        assert nats_s_client._sc.publish.call_count > 1

    @pytest.mark.asyncio
    async def publish_message_disconnected_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
        nats_s_client._nc = Mock()
        nats_s_client._nc.is_connected = False
        nats_s_client.close_nats_connections = CoroutineMock()
        nats_s_client.connect_to_nats = CoroutineMock()
        nats_s_client._sc = Mock()
        nats_s_client._sc.publish = CoroutineMock()
        await nats_s_client.publish("Test-topic", "Test-message")
        assert nats_s_client.close_nats_connections.called
        assert nats_s_client.connect_to_nats.called
        assert nats_s_client._sc.publish.called
        assert nats_s_client._sc.publish.await_args[0] == ("Test-topic", b'Test-message')

    @pytest.mark.asyncio
    async def register_sequence_consumer_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
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
        await nats_s_client.subscribe("Test-topic", caller_callback, sequence=5)
        assert nats_s_client._sc.subscribe.await_args[1] == dict(start_at='first',
                                                                 time=None,
                                                                 sequence=5,
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
    async def register_time_consumer_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
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
        assert nats_s_client._sc.subscribe.await_args[1] == dict(start_at='first',
                                                                 time='2/27/2019',
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
    async def register_durable_group_consumer_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
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
        await nats_s_client.subscribe("Test-topic", caller_callback, durable_name="test-name", queue="test-queue")
        assert nats_s_client._sc.subscribe.await_args[1] == dict(start_at='first',
                                                                 time=None,
                                                                 sequence=None,
                                                                 queue="test-queue",
                                                                 durable_name="test-name",
                                                                 cb=nats_s_client._cb_with_ack,
                                                                 manual_acks=True,
                                                                 max_inflight=config.NATS_CONFIG["subscriber"][
                                                                     "max_inflight"],
                                                                 pending_limits=config.NATS_CONFIG["subscriber"][
                                                                     "pending_limits"]
                                                                 )

    @pytest.mark.asyncio
    async def register_durable_name_consumer_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
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
        assert nats_s_client._sc.subscribe.await_args[1] == dict(start_at='first',
                                                                 time=None,
                                                                 sequence=None,
                                                                 queue=None,
                                                                 durable_name='Test_Name',
                                                                 cb=nats_s_client._cb_with_ack,
                                                                 manual_acks=True,
                                                                 max_inflight=config.NATS_CONFIG["subscriber"][
                                                                     "max_inflight"],
                                                                 pending_limits=config.NATS_CONFIG["subscriber"][
                                                                     "pending_limits"]
                                                                 )

    @pytest.mark.asyncio
    async def register_basic_consumer_and_callback_OK_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
        nats_s_client._subs.clear()
        nats_s_client._sc = Mock()
        nats_s_client._sc.ack = CoroutineMock()
        nats_s_client._logger.error = Mock()
        nats_s_client._logger.info = Mock()
        message = Mock()
        message.seq = Mock()
        message.data = Mock()
        message.sub = Mock()
        message.sub.subject = "Test-topic"
        caller_callback = Mock()
        nats_s_client._sc.subscribe = CoroutineMock(return_value=nats_s_client._cb_with_ack(message))
        await nats_s_client.subscribe("Test-topic", caller_callback)
        assert nats_s_client._logger.error.called is False
        assert nats_s_client._logger.info.called
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
    async def not_ack_on_callback_failure_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
        nats_s_client._subs.clear()
        nats_s_client._sc = Mock()
        nats_s_client._sc.ack = CoroutineMock()
        nats_s_client._logger.exception = Mock()
        nats_s_client._logger.info = Mock()
        message = Mock()
        message.seq = Mock()
        message.data = Mock()
        message.sub = Mock()
        message.sub.subject = "Test-topic"
        caller_callback = Mock(side_effect=Exception())
        nats_s_client._sc.subscribe = CoroutineMock(return_value=nats_s_client._cb_with_ack(message))
        await nats_s_client.subscribe("Test-topic", caller_callback)
        assert nats_s_client._logger.exception.called
        assert nats_s_client._logger.info.called
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
        assert not nats_s_client._sc.ack.called

    @pytest.mark.asyncio
    async def register_basic_consumer_and_callback_KO_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
        nats_s_client._subs.clear()
        nats_s_client._sc = Mock()
        nats_s_client._sc.ack = CoroutineMock()
        nats_s_client._logger.error = Mock()
        nats_s_client._logger.info = Mock()
        message = Mock()
        message.seq = Mock()
        message.data = Mock()
        message.sub = Mock()
        message.sub.subject = "Test-topic"
        caller_callback = None
        nats_s_client._sc.subscribe = CoroutineMock(return_value=nats_s_client._cb_with_ack(message))
        await nats_s_client.subscribe("Test-topic", caller_callback)
        assert nats_s_client._logger.error.called
        assert nats_s_client._logger.info.called
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
    async def register_basic_consumer_with_sync_action_OK_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
        nats_s_client._subs.clear()
        nats_s_client._sc = Mock()
        nats_s_client._sc.ack = CoroutineMock()
        nats_s_client._logger.error = Mock()
        nats_s_client._logger.info = Mock()
        nats_s_client._nc = Mock()
        nats_s_client._nc.is_connected = True
        message = Mock()
        message.seq = Mock()
        message.data = Mock()
        message.sub = Mock()
        message.sub.subject = "Test-topic"
        caller = Mock()
        caller.action = Mock()
        action_wrapped = ActionWrapper(caller, "action", logger=mock_logger)
        nats_s_client._sc.subscribe = CoroutineMock(return_value=nats_s_client._cb_with_ack_and_action(message))
        await nats_s_client.subscribe_action("Test-topic", action=action_wrapped)
        assert nats_s_client._logger.error.called is False
        assert nats_s_client._logger.info.called
        assert nats_s_client._topic_action["Test-topic"] == action_wrapped
        assert nats_s_client._sc.subscribe.await_args[0] == ("Test-topic",)
        assert nats_s_client._sc.subscribe.await_args[1] == dict(start_at='first',
                                                                 time=None,
                                                                 sequence=None,
                                                                 queue=None,
                                                                 durable_name=None,
                                                                 cb=nats_s_client._cb_with_ack_and_action,
                                                                 manual_acks=True,
                                                                 max_inflight=config.NATS_CONFIG["subscriber"][
                                                                     "max_inflight"],
                                                                 pending_limits=config.NATS_CONFIG["subscriber"][
                                                                     "pending_limits"]
                                                                 )
        assert caller.action.called

    @pytest.mark.asyncio
    async def register_basic_consumer_with_sync_action_KO_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
        nats_s_client._subs.clear()
        nats_s_client._sc = Mock()
        nats_s_client._sc.ack = CoroutineMock()
        nats_s_client._logger.error = Mock()
        nats_s_client._logger.info = Mock()
        nats_s_client._nc = Mock()
        nats_s_client._nc.is_connected = False
        nats_s_client.close_nats_connections = CoroutineMock()
        nats_s_client.connect_to_nats = CoroutineMock()
        message = Mock()
        message.seq = Mock()
        message.data = Mock()
        message.sub = Mock()
        message.sub.subject = "Test-topic"
        nats_s_client._sc.subscribe = CoroutineMock(return_value=nats_s_client._cb_with_ack_and_action(message))
        await nats_s_client.subscribe_action("Test-topic", action=None)
        assert nats_s_client.close_nats_connections.called
        assert nats_s_client.connect_to_nats.called
        assert nats_s_client._topic_action["Test-topic"] is None
        assert nats_s_client._sc.subscribe.await_args[0] == ("Test-topic",)
        assert nats_s_client._sc.subscribe.await_args[1] == dict(start_at='first',
                                                                 time=None,
                                                                 sequence=None,
                                                                 queue=None,
                                                                 durable_name=None,
                                                                 cb=nats_s_client._cb_with_ack_and_action,
                                                                 manual_acks=True,
                                                                 max_inflight=config.NATS_CONFIG["subscriber"][
                                                                     "max_inflight"],
                                                                 pending_limits=config.NATS_CONFIG["subscriber"][
                                                                     "pending_limits"]
                                                                 )

    @pytest.mark.asyncio
    async def not_ack_on_action_failure_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
        nats_s_client._subs.clear()
        nats_s_client._sc = Mock()
        nats_s_client._sc.ack = CoroutineMock()
        nats_s_client._logger.exception = Mock()
        nats_s_client._logger.info = Mock()
        nats_s_client._nc = Mock()
        nats_s_client._nc.is_connected = True
        message = Mock()
        message.seq = Mock()
        message.data = Mock()
        message.sub = Mock()
        message.sub.subject = "Test-topic"
        caller = Mock()
        caller.action = CoroutineMock(side_effect=Exception())
        action_wrapped = ActionWrapper(caller, "action", is_async=True, logger=mock_logger)
        nats_s_client._sc.subscribe = CoroutineMock(return_value=nats_s_client._cb_with_ack_and_action(message))
        await nats_s_client.subscribe_action("Test-topic", action=action_wrapped)
        assert nats_s_client._logger.exception.called
        assert nats_s_client._logger.info.called
        assert nats_s_client._topic_action["Test-topic"] is action_wrapped
        assert nats_s_client._sc.subscribe.await_args[0] == ("Test-topic",)
        assert nats_s_client._sc.subscribe.await_args[1] == dict(start_at='first',
                                                                 time=None,
                                                                 sequence=None,
                                                                 queue=None,
                                                                 durable_name=None,
                                                                 cb=nats_s_client._cb_with_ack_and_action,
                                                                 manual_acks=True,
                                                                 max_inflight=config.NATS_CONFIG["subscriber"][
                                                                     "max_inflight"],
                                                                 pending_limits=config.NATS_CONFIG["subscriber"][
                                                                     "pending_limits"]
                                                                 )
        assert caller.action.called
        assert not nats_s_client._sc.ack.called

    @pytest.mark.asyncio
    async def register_basic_consumer_with_not_sync_action_KO_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
        nats_s_client._subs.clear()
        nats_s_client._sc = Mock()
        nats_s_client._sc.ack = CoroutineMock()
        nats_s_client._logger.error = Mock()
        nats_s_client._logger.info = Mock()
        nats_s_client._nc = Mock()
        nats_s_client._nc.is_connected = True
        message = Mock()
        message.seq = Mock()
        message.data = Mock()
        message.sub = Mock()
        message.sub.subject = "Test-topic"
        caller = Mock()
        caller.action = CoroutineMock()
        action_wrapped = ActionWrapper(caller, "action", is_async=True, logger=mock_logger)
        nats_s_client._sc.subscribe = CoroutineMock(return_value=nats_s_client._cb_with_ack_and_action(message))
        await nats_s_client.subscribe_action("Test-topic", action=action_wrapped)
        assert nats_s_client._logger.error.called is False
        assert nats_s_client._logger.info.called
        assert nats_s_client._topic_action["Test-topic"] is action_wrapped
        assert nats_s_client._sc.subscribe.await_args[0] == ("Test-topic",)
        assert nats_s_client._sc.subscribe.await_args[1] == dict(start_at='first',
                                                                 time=None,
                                                                 sequence=None,
                                                                 queue=None,
                                                                 durable_name=None,
                                                                 cb=nats_s_client._cb_with_ack_and_action,
                                                                 manual_acks=True,
                                                                 max_inflight=config.NATS_CONFIG["subscriber"][
                                                                     "max_inflight"],
                                                                 pending_limits=config.NATS_CONFIG["subscriber"][
                                                                     "pending_limits"]
                                                                 )
        assert caller.action.called

    @pytest.mark.asyncio
    async def close_nats_connection_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
        nats_s_client._subs = list()
        sub = Mock()
        sub.unsubscribe = CoroutineMock()
        nats_s_client._subs.append(sub)
        nats_s_client._sc = Mock()
        nats_s_client._nc = Mock()
        nats_s_client._nc.is_closed = False
        nats_s_client._nc.is_connected = True
        nats_s_client._sc.close = CoroutineMock()
        nats_s_client._nc.close = CoroutineMock()
        await nats_s_client.close_nats_connections()
        assert sub.unsubscribe.called and nats_s_client._sc.close.called and nats_s_client._nc.close.called

    @pytest.mark.asyncio
    async def close_disconnected_nats_connection_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
        nats_s_client._subs = list()
        sub = Mock()
        sub.unsubscribe = CoroutineMock()
        nats_s_client._subs.append(sub)
        nats_s_client._sc = Mock()
        nats_s_client._nc = Mock()
        nats_s_client._nc.is_closed = False
        nats_s_client._nc.is_connected = False
        nats_s_client._sc.close = CoroutineMock()
        nats_s_client._nc.close = CoroutineMock()
        await nats_s_client.close_nats_connections()
        assert sub.unsubscribe.called and nats_s_client._sc.close.called is False and nats_s_client._nc.close.called

    @pytest.mark.asyncio
    async def close_closed_nats_connection_test(self):
        mock_logger = Mock()
        nats_s_client = NatsStreamingClient(config, "test-client-id", logger=mock_logger)
        nats_s_client._subs = list()
        sub = Mock()
        sub.unsubscribe = CoroutineMock()
        nats_s_client._subs.append(sub)
        nats_s_client._sc = Mock()
        nats_s_client._nc = Mock()
        nats_s_client._nc.is_closed = True
        nats_s_client._nc.is_connected = False
        nats_s_client._sc.close = CoroutineMock()
        nats_s_client._nc.close = CoroutineMock()
        await nats_s_client.close_nats_connections()
        assert sub.unsubscribe.called and nats_s_client._sc.close.called is False
        assert nats_s_client._nc.close.called is False
