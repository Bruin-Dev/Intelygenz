import json
from unittest.mock import MagicMock, Mock

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

    def get_exist_test(self):
        config = testconfig
        logger = Mock()

        key = "test_123"
        fixed_key = f"{config.ENVIRONMENT_NAME}-dri-serial-{key}"
        expected = {"test": 12345}

        redis = Mock()
        redis.exists = Mock(return_value=True)
        redis.get = Mock(return_value=json.dumps(expected))

        storage_repo = StorageRepository(config, logger, redis)

        actual = storage_repo.get(key)

        redis.get.assert_called_once_with(fixed_key)
        assert actual == expected

    def get_not_exist_test(self):
        config = testconfig
        logger = Mock()

        key = "test_123"

        redis = Mock()
        redis.exists = Mock(return_value=False)
        redis.get = Mock()

        storage_repo = StorageRepository(config, logger, redis)

        actual = storage_repo.get(key)

        redis.get.assert_not_called()
        assert actual is None

    def save_test(self):
        config = testconfig
        logger = Mock()

        key = "test_123"
        fixed_key = f"{config.ENVIRONMENT_NAME}-dri-serial-{key}"

        payload = {"some": "payload"}

        redis = Mock()
        redis.set = Mock()

        storage_repo = StorageRepository(config, logger, redis)

        storage_repo.save(key, payload)

        redis.set.assert_called_once_with(fixed_key, json.dumps(payload), ex=300)

    def remove_test(self):
        config = testconfig
        logger = Mock()

        key_1 = "test_123"
        fixed_key_1 = f"{config.ENVIRONMENT_NAME}-dri-serial-{key_1}"

        key_2 = "test_234"
        fixed_key_2 = f"{config.ENVIRONMENT_NAME}-dri-serial-{key_2}"

        redis = Mock()
        redis.delete = Mock()

        storage_repo = StorageRepository(config, logger, redis)

        storage_repo.remove(key_1, key_2)

        redis.delete.assert_called_once_with(fixed_key_1, fixed_key_2)
