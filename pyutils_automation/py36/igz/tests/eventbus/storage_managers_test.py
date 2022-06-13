import json

from unittest.mock import Mock
from unittest.mock import patch

from pytest import raises
from shortuuid import uuid

from igz.packages.eventbus import storage_managers as storage_managers_module
from igz.packages.eventbus.storage_managers import MessageStorageManager
from igz.packages.eventbus.storage_managers import RedisStorageManager


class TestAbstractMessageStorageManager:
    def test_is_message_larger_than_1mb_with_string_payload_test(self):
        bytes_in_1mb = 1048576

        payload = json.dumps({"foo": "X" * (bytes_in_1mb - 100)})
        result = MessageStorageManager.is_message_larger_than_1mb(payload)
        assert result is False

        payload = json.dumps({"foo": "X" * (bytes_in_1mb + 100)})
        result = MessageStorageManager.is_message_larger_than_1mb(payload)
        assert result is True

    def test_is_message_larger_than_1mb_with_dict_payload_test(self):
        bytes_in_1mb = 1048576

        payload = {"foo": "X" * (bytes_in_1mb - 100)}
        result = MessageStorageManager.is_message_larger_than_1mb(payload)
        assert result is False

        payload = {"foo": "X" * (bytes_in_1mb + 100)}
        result = MessageStorageManager.is_message_larger_than_1mb(payload)
        assert result is True


class TestRedisStorageManager:
    def instantiation_test(self):
        logger = Mock()
        redis_client = Mock()

        redis_manager = RedisStorageManager(logger, redis_client)

        assert redis_manager._logger is logger
        assert redis_manager._storage_client is redis_client

    def store_message_with_dict_payload_test(self):
        payload = {
            'foo': 'bar',
            'baz': 'mec',
        }

        logger = Mock()
        redis_client = Mock()

        redis_manager = RedisStorageManager(logger, redis_client)

        uuid_ = uuid()
        with patch.object(storage_managers_module, 'uuid', return_value=uuid_):
            result = redis_manager.store_message(payload)

        redis_client.set.assert_called_once_with(name=uuid_, value='{"foo":"bar","baz":"mec"}', ex=300)

        expected = {'token': uuid_, 'is_stored': True}
        assert result == expected

    def store_message_with_encoded_payload_test(self):
        payload = {
            'foo': 'bar',
            'baz': 'mec',
        }
        encoded_payload = json.dumps(payload)

        logger = Mock()
        redis_client = Mock()

        redis_manager = RedisStorageManager(logger, redis_client)

        uuid_ = uuid()
        with patch.object(storage_managers_module, 'uuid', return_value=uuid_):
            result = redis_manager.store_message(encoded_payload)

        redis_client.set.assert_called_once_with(name=uuid_, value=encoded_payload, ex=300)

        expected = {'token': uuid_, 'is_stored': True}
        assert result == expected

    def store_message_with_encode_result_flag_activated_test(self):
        payload = {
            'foo': 'bar',
            'baz': 'mec',
        }

        logger = Mock()
        redis_client = Mock()

        redis_manager = RedisStorageManager(logger, redis_client)

        uuid_ = uuid()
        with patch.object(storage_managers_module, 'uuid', return_value=uuid_):
            result = redis_manager.store_message(payload, encode_result=True)

        expected = f'{{"token": "{uuid_}", "is_stored": true}}'
        assert result == expected

    def recover_message_with_dict_payload_test(self):
        uuid_ = uuid()
        payload = {
            'token': uuid_,
            'is_stored': True,
        }
        stored_msg = {'foo': 'bar', 'baz': 'mec'}
        encoded_stored_msg = json.dumps(stored_msg)

        logger = Mock()

        redis_client = Mock()
        redis_client.get = Mock(return_value=encoded_stored_msg)

        redis_manager = RedisStorageManager(logger, redis_client)

        result = redis_manager.recover_message(payload)

        redis_client.get.assert_called_once_with(uuid_)
        redis_client.delete.assert_called_once_with(uuid_)

        assert result == stored_msg

    def recover_message_with_encoded_payload_test(self):
        uuid_ = uuid()
        payload = {
            'token': uuid_,
            'is_stored': True,
        }
        encoded_payload = json.dumps(payload)

        stored_msg = {'foo': 'bar', 'baz': 'mec'}
        encoded_stored_msg = json.dumps(stored_msg)

        logger = Mock()

        redis_client = Mock()
        redis_client.get = Mock(return_value=encoded_stored_msg)

        redis_manager = RedisStorageManager(logger, redis_client)

        result = redis_manager.recover_message(encoded_payload)

        redis_client.get.assert_called_once_with(uuid_)
        redis_client.delete.assert_called_once_with(uuid_)

        assert result == stored_msg

    def recover_message_with_encode_result_flag_activated_test(self):
        uuid_ = uuid()
        payload = {
            'token': uuid_,
            'is_stored': True,
        }

        stored_msg = {'foo': 'bar', 'baz': 'mec'}
        encoded_stored_msg = json.dumps(stored_msg)

        logger = Mock()

        redis_client = Mock()
        redis_client.get = Mock(return_value=encoded_stored_msg)

        redis_manager = RedisStorageManager(logger, redis_client)

        uuid_ = uuid()
        with patch.object(storage_managers_module, 'uuid', return_value=uuid_):
            result = redis_manager.recover_message(payload, encode_result=True)

        assert result == encoded_stored_msg

    def recover_message_with_no_token_in_payload_test(self):
        payload = {
            'foo': 'bar',
            'is_stored': True,
        }

        logger = Mock()
        redis_client = Mock()

        redis_manager = RedisStorageManager(logger, redis_client)

        with raises(KeyError):
            redis_manager.recover_message(payload, encode_result=True)
