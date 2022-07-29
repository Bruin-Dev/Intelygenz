import json
from unittest.mock import Mock, patch

import pytest
from framework.nats import temp_payload_storage
from framework.nats.temp_payload_storage import Redis as RedisStorage
from framework.nats.temp_payload_storage import RedisLegacy as RedisLegacyStorage
from framework.nats.temp_payload_storage import TempPayloadStorage
from pytest import fixture
from redis import Redis


class Dummy(TempPayloadStorage):
    """
    Dummy temporary payload storage. It does nothing.
    """

    def is_stored(self, payload: bytes) -> bool:
        pass

    def store(self, payload: bytes) -> bytes:
        pass

    def recover(self, token: bytes) -> bytes:
        pass


@fixture(scope="function")
def any_payload():
    return b"any_payload"


@fixture(scope="function")
def any_uuid():
    return "any_uuid"


@fixture(scope="function")
def any_token():
    return b"any_token"


@fixture(scope="function")
def redis_client():
    return Mock(spec_set=Redis)


@fixture(scope="function")
def redis_temp_payload_storage(redis_client):
    return RedisStorage(storage_client=redis_client)


@fixture(scope="function")
def redis_legacy_temp_payload_storage(redis_client):
    return RedisLegacyStorage(storage_client=redis_client)


class TestRedisStorage:
    @pytest.mark.parametrize(
        "input_,expected", [(f"{RedisStorage.TMP_PAYLOAD_PREFIX.decode()} foo".encode(), True), (b"foo", False)]
    )
    def is_stored_test(self, redis_temp_payload_storage, input_, expected):
        # When
        result = redis_temp_payload_storage.is_stored(input_)

        # Then
        assert result is expected

    def store_test(self, redis_temp_payload_storage, any_payload, any_uuid):
        # When
        with patch.object(temp_payload_storage, "uuid", new=Mock(return_value=any_uuid)):
            result = redis_temp_payload_storage.store(any_payload)

        # Then
        recover_token = f"{RedisStorage.TMP_PAYLOAD_PREFIX.decode()} {any_uuid}".encode()
        redis_temp_payload_storage._client.set.assert_called_once_with(
            name=recover_token,
            value=any_payload,
            ex=300,
        )
        assert result == recover_token

    def recover_test(self, redis_temp_payload_storage, any_payload, any_token):
        # Given
        redis_temp_payload_storage._client.get.return_value = any_payload

        # When
        result = redis_temp_payload_storage.recover(any_token)

        # Then
        redis_temp_payload_storage._client.get.assert_called_once_with(name=any_token)
        assert result == any_payload


class TestRedisLegacyStorage:
    def is_stored_false_test(self, redis_legacy_temp_payload_storage):
        # Given
        payload = json.dumps({"foo": "bar"}).encode()

        # When
        result = redis_legacy_temp_payload_storage.is_stored(payload)

        # Then
        assert result is False

    def is_stored_true_test(self, redis_legacy_temp_payload_storage, any_uuid):
        # Given
        payload = json.dumps({"is_stored": True, "token": any_uuid}).encode()

        # When
        result = redis_legacy_temp_payload_storage.is_stored(payload)

        # Then
        assert result is True

    def store_test(self, redis_legacy_temp_payload_storage, any_payload, any_uuid):
        # When
        with patch.object(temp_payload_storage, "uuid", new=Mock(return_value=any_uuid)):
            result = redis_legacy_temp_payload_storage.store(any_payload)

        # Then
        recover_payload = json.dumps({"is_stored": True, "token": any_uuid}).encode()
        redis_legacy_temp_payload_storage._client.set.assert_called_once_with(
            name=any_uuid,
            value=any_payload,
            ex=300,
        )
        assert result == recover_payload

    def recover_test(self, redis_legacy_temp_payload_storage, any_payload, any_uuid):
        # Given
        recover_payload = json.dumps({"is_stored": True, "token": any_uuid}).encode()
        redis_legacy_temp_payload_storage._client.get.return_value = any_payload

        # When
        result = redis_legacy_temp_payload_storage.recover(recover_payload)

        # Then
        redis_legacy_temp_payload_storage._client.get.assert_called_once_with(name=any_uuid)
        assert result == any_payload
