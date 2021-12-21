import json
from unittest.mock import Mock, MagicMock

from application.repositories.storage_repository import StorageRepository

from config import testconfig


class TestStorageRepository:

    def instance_test(self):
        config = testconfig
        logger = Mock()
        redis = Mock()
        storage_repo = StorageRepository(config, logger, redis)

        assert storage_repo._config == config
        assert storage_repo._logger == logger
        assert storage_repo._redis == redis

    def get_exist_test(self, storage_repository):
        key = "test_123"
        fixed_key = f"{storage_repository._config.ENVIRONMENT_NAME}-{key}"

        expected = {"test": 12345}
        storage_repository._redis.exists = Mock(return_value=True)
        storage_repository._redis.get = Mock(return_value=json.dumps(expected))

        actual = storage_repository.get(key)

        storage_repository._redis.get.assert_called_once_with(fixed_key)
        assert actual == expected

    def get_not_exist_test(self, storage_repository):
        key = "test_123"

        storage_repository._redis.exists = Mock(return_value=False)
        storage_repository._redis.get = Mock()

        actual = storage_repository.get(key)

        storage_repository._redis.get.assert_not_called()
        assert actual is None

    def find_test(self, storage_repository):
        lookup_key = "test"
        fixed_lookup_key = f"{storage_repository._config.ENVIRONMENT_NAME}-{lookup_key}"

        match_1 = "test_1"
        fixed_match_1 = f"{storage_repository._config.ENVIRONMENT_NAME}-{match_1}"

        match_2 = "test_2"
        fixed_match_2 = f"{storage_repository._config.ENVIRONMENT_NAME}-{match_2}"

        expected = [{fixed_match_1: 12345}, {fixed_match_2: 12345}]
        expected_raw = [json.dumps(e) for e in expected]

        storage_repository._redis.scan_iter = MagicMock()
        storage_repository._redis.scan_iter.return_value = [fixed_match_1, fixed_match_2]
        storage_repository._redis.get = Mock(side_effect=expected_raw)

        actual = storage_repository.find_all(lookup_key)

        storage_repository._redis.scan_iter.assert_called_once_with(fixed_lookup_key)
        assert actual == expected

    def save_test(self, storage_repository):
        key = "test_123"
        fixed_key = f"{storage_repository._config.ENVIRONMENT_NAME}-{key}"

        payload = {"some": "payload"}

        storage_repository._redis.set = Mock()

        storage_repository.save(key, payload)

        storage_repository._redis.set.assert_called_once_with(fixed_key, json.dumps(payload))

    def remove_test(self, storage_repository):
        key_1 = "test_123"
        fixed_key_1 = f"{storage_repository._config.ENVIRONMENT_NAME}-{key_1}"

        key_2 = "test_234"
        fixed_key_2 = f"{storage_repository._config.ENVIRONMENT_NAME}-{key_2}"

        storage_repository._redis.delete = Mock()

        actual = storage_repository.remove(key_1, key_2)

        storage_repository._redis.delete.assert_called_once_with(fixed_key_1, fixed_key_2)
        assert actual is None

    def increment_test(self, storage_repository):
        key = "incr_test"
        storage_key = f"{storage_repository._config.ENVIRONMENT_NAME}-{key}"
        value = 1
        storage_repository._redis.incr = Mock(return_value=value)

        counter = storage_repository.increment(key)
        storage_repository._redis.incr.assert_called_once_with(storage_key, amount=1)
        assert counter == value

    def rename_test(self, storage_repository):
        key_1 = "test_123"
        fixed_key_1 = f"{storage_repository._config.ENVIRONMENT_NAME}-{key_1}"

        key_2 = "test_234"
        fixed_key_2 = f"{storage_repository._config.ENVIRONMENT_NAME}-{key_2}"

        storage_repository._redis.rename = Mock()

        storage_repository.rename(key_1, key_2)

        storage_repository._redis.rename.assert_called_once_with(fixed_key_1, fixed_key_2)

    def expire_test(self, storage_repository):
        key_1 = "test_123"
        fixed_key_1 = f"{storage_repository._config.ENVIRONMENT_NAME}-{key_1}"
        timeout = 100

        storage_repository._redis.expire = Mock()

        storage_repository.expire(key_1, timeout)

        storage_repository._redis.expire.assert_called_once_with(fixed_key_1, timeout)
