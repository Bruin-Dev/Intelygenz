from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.nats.clients import NATSClient
import pytest
from asynctest import CoroutineMock
from igz.config import testconfig as config
from unittest.mock import Mock
from unittest.mock import patch
import logging
import json

from datetime import datetime
from shortuuid import uuid

from igz.packages.eventbus import storage_managers as storage_managers_module


class TestEventBus:

    def instantiation_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        event_bus1 = EventBus(storage_manager)
        event_bus2 = EventBus(storage_manager, logger=mock_logger)

        assert isinstance(event_bus1._consumers, dict)
        assert isinstance(event_bus1._logger, logging._loggerClass)
        assert event_bus1._logger.hasHandlers() is True
        assert event_bus1._logger.getEffectiveLevel() == 10
        assert event_bus2._logger is mock_logger
        assert event_bus1._messages_storage_manager is storage_manager
        assert event_bus2._messages_storage_manager is storage_manager

    @pytest.mark.asyncio
    async def connect_OK_test(self):
        mock_logger = Mock()
        storage_manager = Mock()

        event_bus = EventBus(storage_manager, logger=mock_logger)
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

        storage_manager = Mock()
        storage_manager.is_message_larger_than_1mb = Mock(return_value=False)

        event_bus = EventBus(storage_manager, logger=mock_logger)
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

        storage_manager = Mock()
        storage_manager.is_message_larger_than_1mb = Mock(return_value=False)

        event_bus = EventBus(storage_manager, logger=mock_logger)
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

    @pytest.mark.asyncio
    async def rpc_request_with_non_dict_payload_test(self):
        mock_logger = Mock()

        storage_manager = Mock()
        storage_manager.is_message_larger_than_1mb = Mock(return_value=False)

        event_bus = EventBus(storage_manager, logger=mock_logger)
        publisher = NATSClient(config, logger=mock_logger)
        publisher.rpc_request = CoroutineMock()

        event_bus.set_producer(publisher)

        await event_bus.rpc_request(
            topic="some_topic",
            message="some_str_message",
            timeout=10
        )

        publisher.rpc_request.assert_awaited_once_with(
            "some_topic", '{"message":"some_str_message"}', 10,
        )

        publisher.rpc_request.reset_mock()
        await event_bus.rpc_request(
            topic="some_topic",
            message=9999,
            timeout=10
        )

        publisher.rpc_request.assert_awaited_once_with(
            "some_topic", '{"message":9999}', 10,
        )

        publisher.rpc_request.reset_mock()
        await event_bus.rpc_request(
            topic="some_topic",
            message=datetime(1970, 1, 1, 0, 0, 0),
            timeout=10
        )

        publisher.rpc_request.assert_awaited_once_with(
            "some_topic", '{"message":"1970-01-01 00:00:00"}', 10,
        )

    @pytest.mark.asyncio
    async def rpc_request_with_message_larger_than_1mb_in_request_stage_test(self):
        uuid_ = uuid()
        bytes_in_1mb = 1048576
        payload = {'foo': 'X' * (bytes_in_1mb + 100)}

        published_message = {"token": uuid_, "is_stored": True}
        encoded_published_message = f'{{"token":"{uuid_}","is_stored":true}}'

        mock_logger = Mock()

        storage_manager = Mock()
        storage_manager.is_message_larger_than_1mb = Mock(return_value=True)
        storage_manager.store_message = Mock(return_value=published_message)

        event_bus = EventBus(storage_manager, logger=mock_logger)
        publisher = NATSClient(config, logger=mock_logger)
        publisher.rpc_request = CoroutineMock()

        event_bus.set_producer(publisher)

        with patch.object(storage_managers_module, 'uuid', return_value=uuid_):
            await event_bus.rpc_request(
                topic="some_topic",
                message=payload,
                timeout=10
            )

        storage_manager.is_message_larger_than_1mb.assert_called_once_with(payload)
        storage_manager.store_message.assert_called_once_with(payload, encode_result=False)
        publisher.rpc_request.assert_awaited_once_with("some_topic", encoded_published_message, 10)

    @pytest.mark.asyncio
    async def rpc_request_with_message_larger_than_1mb_in_reply_stage_test(self):
        uuid_ = uuid()
        payload = {'data': 'some-data'}
        encoded_payload = '{"data":"some-data"}'
        response_message = {"token": uuid_, "is_stored": True}

        bytes_in_1mb = 1048576
        recovered_message = {'foo': 'X' * (bytes_in_1mb + 100)}

        mock_logger = Mock()

        storage_manager = Mock()
        storage_manager.is_message_larger_than_1mb = Mock(return_value=False)
        storage_manager.recover_message = Mock(return_value=recovered_message)

        event_bus = EventBus(storage_manager, logger=mock_logger)
        publisher = NATSClient(config, logger=mock_logger)
        publisher.rpc_request = CoroutineMock(return_value=response_message)

        event_bus.set_producer(publisher)

        with patch.object(storage_managers_module, 'uuid', return_value=uuid_):
            response = await event_bus.rpc_request(
                topic="some_topic",
                message=payload,
                timeout=10
            )

        storage_manager.is_message_larger_than_1mb.assert_called_once_with(payload)
        publisher.rpc_request.assert_awaited_once_with("some_topic", encoded_payload, 10)
        storage_manager.recover_message.assert_called_once_with(response_message, encode_result=False)
        assert response == recovered_message

    def add_consumer_OK_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        event_bus = EventBus(storage_manager, logger=mock_logger)
        subscriber = NATSClient(config, logger=mock_logger)

        event_bus.add_consumer(subscriber, consumer_name="some-name")

        assert event_bus._consumers["some-name"] is subscriber

    def add_consumer_KO_repeated_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        event_bus = EventBus(storage_manager, logger=mock_logger)
        first_subscriber = NATSClient(config, logger=mock_logger)
        second_subscriber = NATSClient(config, logger=mock_logger)
        event_bus._logger.error = Mock()

        event_bus.add_consumer(first_subscriber, consumer_name="some-name")
        event_bus.add_consumer(second_subscriber, consumer_name="some-name")

        event_bus._logger.error.assert_called()
        assert event_bus._consumers["some-name"] is first_subscriber
        assert event_bus._consumers["some-name"] is not second_subscriber

    @pytest.mark.asyncio
    async def add_consumer_check_behavior_of_decorated_callback_in_consumer_when_message_length_exceeds_1mb_test(self):
        bytes_in_1mb = 1048576
        topic = 'some-topic'
        recovered_message = {'data': 'X' * (bytes_in_1mb + 100)}
        recovered_message_encoded = json.dumps(recovered_message)
        message_needed_for_recover = {'token': uuid(), 'is_stored': True}
        message_needed_for_recover_encoded = json.dumps(message_needed_for_recover)

        mock_logger = Mock()

        storage_manager = Mock()
        storage_manager.recover_message = Mock(return_value=recovered_message_encoded)

        event_bus = EventBus(storage_manager, logger=mock_logger)

        action_wrapper = ActionWrapper(state_instance=None, target_function="", logger=mock_logger)
        action_wrapper.execute_stateful_action = Mock()

        subscriber = NATSClient(config, logger=mock_logger)
        subscriber._topic_action = {topic: action_wrapper}

        event_bus.add_consumer(subscriber, consumer_name="some-name")

        message_instance = Mock()
        message_instance.data = message_needed_for_recover_encoded
        message_instance.subject = topic
        message_instance.reply = '_INBOX abcdefgh12345'

        await subscriber._cb_with_action(message_instance)

        storage_manager.recover_message.assert_called_once_with(message_needed_for_recover, encode_result=True)
        action_wrapper.execute_stateful_action.assert_called_once_with({
            **recovered_message, 'response_topic': message_instance.reply
        })

    def set_producer_OK_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        event_bus = EventBus(storage_manager, logger=mock_logger)
        publisher = NATSClient(config, logger=mock_logger)

        event_bus.set_producer(publisher)

        assert event_bus._producer is publisher

    @pytest.mark.asyncio
    async def subscribe_consumer_OK_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        event_bus = EventBus(storage_manager, logger=mock_logger)
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

        storage_manager = Mock()
        storage_manager.is_message_larger_than_1mb = Mock(return_value=False)

        event_bus = EventBus(storage_manager, logger=mock_logger)
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

        storage_manager = Mock()
        storage_manager.is_message_larger_than_1mb = Mock(return_value=False)

        event_bus = EventBus(storage_manager, logger=mock_logger)
        publisher = NATSClient(config, logger=mock_logger)
        publisher.publish = CoroutineMock()

        event_bus.set_producer(publisher)

        await event_bus.publish_message(
            topic="some_topic", msg={'epoch_time': datetime(1970, 1, 1, 0, 0, 0)}
        )

        publisher.publish.assert_awaited_once_with("some_topic", '{"epoch_time":"1970-01-01 00:00:00"}')

    @pytest.mark.asyncio
    async def publish_message_with_non_dict_payload_test(self):
        mock_logger = Mock()

        storage_manager = Mock()
        storage_manager.is_message_larger_than_1mb = Mock(return_value=False)

        event_bus = EventBus(storage_manager, logger=mock_logger)
        publisher = NATSClient(config, logger=mock_logger)
        publisher.publish = CoroutineMock()

        event_bus.set_producer(publisher)

        await event_bus.publish_message(topic="some_topic", msg="some_str_message")
        publisher.publish.assert_awaited_once_with("some_topic", '{"message":"some_str_message"}')

        publisher.publish.reset_mock()
        await event_bus.publish_message(topic="some_topic", msg=9999)
        publisher.publish.assert_awaited_once_with("some_topic", '{"message":9999}')

        publisher.publish.reset_mock()
        await event_bus.publish_message(topic="some_topic", msg=datetime(1970, 1, 1, 0, 0, 0))
        publisher.publish.assert_awaited_once_with("some_topic", '{"message":"1970-01-01 00:00:00"}')

    @pytest.mark.asyncio
    async def publish_message_larger_than_1mb_test(self):
        uuid_ = uuid()
        bytes_in_1mb = 1048576
        payload = {'foo': 'X' * (bytes_in_1mb + 100)}

        published_message = {"token": uuid_, "is_stored": True}
        encoded_published_message = f'{{"token":"{uuid_}","is_stored":true}}'

        mock_logger = Mock()

        storage_manager = Mock()
        storage_manager.is_message_larger_than_1mb = Mock(return_value=True)
        storage_manager.store_message = Mock(return_value=published_message)

        event_bus = EventBus(storage_manager, logger=mock_logger)
        publisher = NATSClient(config, logger=mock_logger)
        publisher.publish = CoroutineMock()

        event_bus.set_producer(publisher)

        with patch.object(storage_managers_module, 'uuid', return_value=uuid_):
            await event_bus.publish_message(topic="Test-topic", msg=payload)

        storage_manager.is_message_larger_than_1mb.assert_called_once_with(payload)
        storage_manager.store_message.assert_called_once_with(payload, encode_result=False)
        publisher.publish.assert_awaited_once_with("Test-topic", encoded_published_message)

    @pytest.mark.asyncio
    async def close_connections_OK_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        event_bus = EventBus(storage_manager, logger=mock_logger)
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
