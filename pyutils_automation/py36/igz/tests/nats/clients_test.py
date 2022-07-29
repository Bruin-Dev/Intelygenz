import json
import logging
from unittest.mock import Mock, call, patch

import pytest
from asynctest import CoroutineMock, mock
from igz.config import testconfig as config
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.nats.clients import NATSClient
from nats.aio.client import Client as NATS
from shortuuid import uuid
from tenacity import RetryError


class TestNATSClient:
    attempts = 0

    def instantiation_test(self):
        mock_logger = Mock()
        nats_client1 = NATSClient(config)
        nats_client2 = NATSClient(config, logger=mock_logger)

        assert nats_client1._config == config.NATS_CONFIG
        assert isinstance(nats_client1._logger, logging._loggerClass)
        assert nats_client1._logger.hasHandlers()
        assert nats_client1._logger.getEffectiveLevel() == 10
        assert nats_client2._logger is mock_logger

    @mock.patch("igz.packages.nats.clients.NATS.connect", new=CoroutineMock())
    @pytest.mark.asyncio
    async def connect_to_nats_test(self, *args):
        mock_logger = Mock()
        nats_client = NATSClient(config, logger=mock_logger)
        nats_client.connect = CoroutineMock()

        await nats_client.connect_to_nats()

        assert isinstance(nats_client._nc, NATS)
        nats_client._nc.connect.assert_awaited_once_with(
            servers=config.NATS_CONFIG["servers"], max_reconnect_attempts=config.NATS_CONFIG["reconnects"]
        )

    @mock.patch("igz.packages.nats.clients.NATS.connect", new=CoroutineMock(side_effect=Exception))
    @pytest.mark.asyncio
    async def connect_to_nats_retry_test(self):
        mock_logger = Mock()
        nats_client = NATSClient(config, logger=mock_logger)

        # TODO: Improve this by using a context manager
        # Maybe unittest.TestCase.assertRaises could make this easier
        try:
            await nats_client.connect_to_nats()
        except Exception as e:
            error = e

        assert isinstance(error, RetryError)
        assert nats_client._nc.connect.call_count > 1

    @pytest.mark.asyncio
    async def publish_message_test(self):
        message = {"foo": "bar"}
        message_encoded = json.dumps(message)

        mock_logger = Mock()

        nats_client = NATSClient(config, logger=mock_logger)
        nats_client._nc = Mock()
        nats_client._nc.is_connected = True
        nats_client._nc.publish = CoroutineMock()

        await nats_client.publish(topic="Test-topic", message=message_encoded)

        nats_client._nc.publish.assert_awaited_once_with("Test-topic", bytes(message_encoded, encoding="utf-8"))

    @pytest.mark.asyncio
    async def publish_message_retry_test(self):
        message = {"foo": "bar"}
        message_encoded = json.dumps(message)

        mock_logger = Mock()

        nats_client = NATSClient(config, logger=mock_logger)
        nats_client._nc = Mock()
        nats_client._nc.is_connected = True
        nats_client._nc.publish = CoroutineMock(side_effect=Exception)

        # TODO: Improve this by using a context manager
        # Maybe unittest.TestCase.assertRaises could make this easier
        try:
            await nats_client.publish(topic="Test-topic", message=message_encoded)
        except Exception as e:
            error = e

        assert isinstance(error, RetryError)
        assert nats_client._nc.publish.call_count > 1

    @pytest.mark.asyncio
    async def publish_message_disconnected_test(self):
        message = {"foo": "bar"}
        message_encoded = json.dumps(message)

        mock_logger = Mock()

        nats_client = NATSClient(config, logger=mock_logger)
        nats_client._nc = Mock()
        nats_client._nc.is_connected = False
        nats_client._nc.publish = CoroutineMock()
        nats_client.close_nats_connections = CoroutineMock()
        nats_client.connect_to_nats = CoroutineMock()

        await nats_client.publish(topic="Test-topic", message=message_encoded)

        nats_client.close_nats_connections.assert_awaited()
        nats_client.connect_to_nats.assert_awaited()
        nats_client._nc.publish.assert_awaited_once_with("Test-topic", bytes(message_encoded, encoding="utf-8"))

    @pytest.mark.asyncio
    async def rpc_request_test(self):
        message = {"foo": "bar"}
        message_encoded = json.dumps(message)

        rpc_response_dict = {"response": "some-data"}

        rpc_response = Mock()
        rpc_response.data = json.dumps(rpc_response_dict)

        mock_logger = Mock()

        nats_client = NATSClient(config, logger=mock_logger)
        nats_client._nc = Mock()
        nats_client._nc.is_connected = True
        nats_client._nc.timed_request = CoroutineMock(return_value=rpc_response)

        result = await nats_client.rpc_request(topic="Test-topic", message=message_encoded)

        nats_client._nc.timed_request.assert_awaited_once_with(
            "Test-topic", bytes(message_encoded, encoding="utf-8"), 10
        )
        assert result == rpc_response_dict

    @pytest.mark.asyncio
    async def rpc_request_retry_test(self):
        message = {"foo": "bar"}
        message_encoded = json.dumps(message)

        mock_logger = Mock()

        nats_client = NATSClient(config, logger=mock_logger)
        nats_client._nc = Mock()
        nats_client._nc.is_connected = True
        nats_client._nc.rpc_request = CoroutineMock(side_effect=Exception)

        # TODO: Improve this by using a context manager
        # Maybe unittest.TestCase.assertRaises could make this easier
        try:
            await nats_client.rpc_request(topic="Test-topic", message=message_encoded)
        except Exception as e:
            error = e

        assert isinstance(error, RetryError)
        assert nats_client._nc.timed_request.call_count > 1

    @pytest.mark.asyncio
    async def rpc_request_disconnected_test(self):
        message = {"foo": "bar"}
        message_encoded = json.dumps(message)

        rpc_response_dict = {"response": "some-data"}

        rpc_response = Mock()
        rpc_response.data = json.dumps(rpc_response_dict)

        mock_logger = Mock()

        nats_client = NATSClient(config, logger=mock_logger)
        nats_client._nc = Mock()
        nats_client._nc.is_connected = False
        nats_client._nc.timed_request = CoroutineMock(return_value=rpc_response)
        nats_client.close_nats_connections = CoroutineMock()
        nats_client.connect_to_nats = CoroutineMock()

        await nats_client.rpc_request(topic="Test-topic", message=message_encoded)

        nats_client.close_nats_connections.assert_awaited()
        nats_client.connect_to_nats.assert_awaited()
        nats_client._nc.timed_request.assert_awaited_once_with(
            "Test-topic", bytes(message_encoded, encoding="utf-8"), 10
        )

    @pytest.mark.asyncio
    async def register_basic_consumer_with_sync_action_OK_test(self):
        mock_logger = Mock()
        nats_client = NATSClient(config, logger=mock_logger)
        nats_client._subs.clear()
        nats_client._logger.error = Mock()
        nats_client._logger.info = Mock()
        nats_client._nc = Mock()
        nats_client._nc.is_connected = True

        message = Mock()
        message.data = json.dumps({"msg": "foo"})
        message.reply = "Response-topic"
        message.subject = "Test-topic"

        caller = Mock()
        caller.action = Mock()
        action_wrapped = ActionWrapper(
            state_instance=caller,
            target_function="action",
            logger=mock_logger,
            is_async=False,
        )
        nats_client._nc.subscribe = CoroutineMock(return_value=nats_client._cb_with_action(message))

        await nats_client.subscribe_action(topic="Test-topic", action=action_wrapped)

        nats_client._logger.error.assert_not_called()
        nats_client._logger.info.assert_called_once()
        assert nats_client._topic_action["Test-topic"] is action_wrapped
        nats_client._nc.subscribe.assert_awaited_once_with(
            "Test-topic",
            **{
                "queue": "",
                "is_async": True,
                "cb": nats_client._cb_with_action,
                "pending_msgs_limit": config.NATS_CONFIG["subscriber"]["pending_limits"],
            },
        )
        caller.action.assert_called_once()

    @pytest.mark.asyncio
    async def register_basic_consumer_with_async_action_OK_test(self):
        mock_logger = Mock()
        nats_client = NATSClient(config, logger=mock_logger)
        nats_client._subs.clear()
        nats_client._logger.error = Mock()
        nats_client._logger.info = Mock()
        nats_client._nc = Mock()
        nats_client._nc.is_connected = True

        message = Mock()
        message.data = json.dumps({"msg": "foo"})
        message.reply = "Response-topic"
        message.subject = "Test-topic"

        caller = Mock()
        caller.action = CoroutineMock()
        action_wrapped = ActionWrapper(
            state_instance=caller,
            target_function="action",
            logger=mock_logger,
            is_async=True,
        )
        nats_client._nc.subscribe = CoroutineMock(return_value=nats_client._cb_with_action(message))

        await nats_client.subscribe_action(topic="Test-topic", action=action_wrapped)

        nats_client._logger.error.assert_not_called()
        nats_client._logger.info.assert_called_once()
        assert nats_client._topic_action["Test-topic"] is action_wrapped
        nats_client._nc.subscribe.assert_awaited_once_with(
            "Test-topic",
            **{
                "queue": "",
                "is_async": True,
                "cb": nats_client._cb_with_action,
                "pending_msgs_limit": config.NATS_CONFIG["subscriber"]["pending_limits"],
            },
        )
        caller.action.assert_awaited_once()

    @pytest.mark.asyncio
    async def register_basic_consumer_with_none_action_KO_test(self):
        mock_logger = Mock()
        nats_client = NATSClient(config, logger=mock_logger)
        nats_client._subs.clear()
        nats_client.close_nats_connections = CoroutineMock()
        nats_client.connect_to_nats = CoroutineMock()
        nats_client._logger.error = Mock()
        nats_client._logger.info = Mock()
        nats_client._nc = Mock()
        nats_client._nc.is_connected = False

        message = Mock()
        message.data = json.dumps({"msg": "foo"})
        message.reply = "Response-topic"
        message.subject = "Test-topic"

        nats_client._nc.subscribe = CoroutineMock(return_value=nats_client._cb_with_action(message))

        await nats_client.subscribe_action(topic="Test-topic", action=None)

        nats_client._logger.info.assert_called_once()
        nats_client._logger.error.assert_called_once()
        nats_client.close_nats_connections.assert_awaited_once()
        nats_client.connect_to_nats.assert_awaited_once()
        assert nats_client._topic_action["Test-topic"] is None
        nats_client._nc.subscribe.assert_awaited_once_with(
            "Test-topic",
            **{
                "queue": "",
                "is_async": True,
                "cb": nats_client._cb_with_action,
                "pending_msgs_limit": config.NATS_CONFIG["subscriber"]["pending_limits"],
            },
        )

    @pytest.mark.asyncio
    async def cb_with_action_with_no_action_linked_to_topic_registered_in_nats_client_test(self):
        msg_data_dict = {"foo": "bar"}
        msg_subject = "some-topic"

        msg_object = Mock()
        msg_object.data = json.dumps(msg_data_dict)
        msg_object.reply = "_INBOX foo-bar-baz"
        msg_object.subject = msg_subject

        mock_logger = Mock()

        nats_client = NATSClient(config, logger=mock_logger)
        nats_client._topic_action = {msg_subject: None}

        await nats_client._cb_with_action(msg_object)

        mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def cb_with_action_with_improper_action_linked_to_topic_registered_in_nats_client_test(self):
        msg_data_dict = {"foo": "bar"}
        msg_subject = "some-topic"

        class FakeActionWrapper:
            pass

        msg_object = Mock()
        msg_object.data = json.dumps(msg_data_dict)
        msg_object.reply = "_INBOX foo-bar-baz"
        msg_object.subject = msg_subject

        mock_logger = Mock()

        nats_client = NATSClient(config, logger=mock_logger)
        nats_client._topic_action = {msg_subject: FakeActionWrapper()}

        await nats_client._cb_with_action(msg_object)

        mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def cb_with_action_with_action_linked_to_topic_and_stateful_action_raising_exception_test(self):
        msg_data_dict = {"foo": "bar"}
        msg_subject = "some-topic"
        nats_reply_topic = "_INBOX foo-bar-baz"
        action_message = {
            **msg_data_dict,
            "response_topic": nats_reply_topic,
        }

        msg_object = Mock()
        msg_object.data = json.dumps(msg_data_dict)
        msg_object.reply = nats_reply_topic
        msg_object.subject = msg_subject

        mock_logger = Mock()

        caller = Mock()
        caller.action = Mock()
        action_wrapped = ActionWrapper(
            state_instance=caller,
            target_function="action",
            logger=mock_logger,
            is_async=False,
        )
        action_wrapped.execute_stateful_action = Mock(side_effect=Exception)

        nats_client = NATSClient(config, logger=mock_logger)
        nats_client._topic_action = {msg_subject: action_wrapped}

        await nats_client._cb_with_action(msg_object)

        action_wrapped.execute_stateful_action.assert_called_once_with(action_message)
        mock_logger.exception.assert_called()

    @pytest.mark.asyncio
    async def cb_with_action_with_action_linked_to_topic_and_stateful_action_running_successfully_test(self):
        msg_data_dict = {"foo": "bar"}
        msg_subject = "some-topic"
        nats_reply_topic = "_INBOX foo-bar-baz"
        action_message = {
            **msg_data_dict,
            "response_topic": nats_reply_topic,
        }

        msg_object = Mock()
        msg_object.data = json.dumps(msg_data_dict)
        msg_object.reply = nats_reply_topic
        msg_object.subject = msg_subject

        mock_logger = Mock()

        caller = Mock()
        caller.action = Mock()
        action_wrapped = ActionWrapper(
            state_instance=caller,
            target_function="action",
            logger=mock_logger,
            is_async=False,
        )
        action_wrapped.execute_stateful_action = Mock()

        nats_client = NATSClient(config, logger=mock_logger)
        nats_client._topic_action = {msg_subject: action_wrapped}

        await nats_client._cb_with_action(msg_object)

        action_wrapped.execute_stateful_action.assert_called_once_with(action_message)

    @pytest.mark.asyncio
    async def close_nats_connection_with_nats_client_connection_open_test(self):
        mock_logger = Mock()
        nats_client = NATSClient(config, logger=mock_logger)
        nats_client._subs = list()
        nats_client._nc = Mock()
        nats_client._nc.is_closed = False
        nats_client._nc.close = CoroutineMock()
        nats_client._nc.drain = CoroutineMock()

        for _ in range(3):
            sub = Mock()
            sub.unsubscribe = CoroutineMock()
            nats_client._subs.append(sub)

        await nats_client.close_nats_connections()

        nats_client._nc.drain.assert_has_awaits(
            [
                call(nats_client._subs[0]),
                call(nats_client._subs[1]),
                call(nats_client._subs[2]),
            ],
            any_order=False,
        )
        nats_client._nc.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def close_nats_connection_with_nats_client_connection_closed_test(self):
        mock_logger = Mock()
        nats_client = NATSClient(config, logger=mock_logger)
        nats_client._subs = list()
        nats_client._nc = Mock()
        nats_client._nc.is_closed = True
        nats_client._nc.close = CoroutineMock()
        nats_client._nc.drain = CoroutineMock()

        for _ in range(3):
            sub = Mock()
            sub.unsubscribe = CoroutineMock()
            nats_client._subs.append(sub)

        await nats_client.close_nats_connections()

        nats_client._nc.drain.assert_has_awaits(
            [
                call(nats_client._subs[0]),
                call(nats_client._subs[1]),
                call(nats_client._subs[2]),
            ],
            any_order=False,
        )
        nats_client._nc.close.assert_not_awaited()
