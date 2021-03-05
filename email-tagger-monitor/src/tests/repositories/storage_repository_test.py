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
        expected = {"test": 12345}
        storage_repository._redis.exists = Mock(return_value=True)
        storage_repository._redis.get = Mock(return_value=json.dumps(expected))

        actual = storage_repository.get("test_123")

        storage_repository._redis.get.assert_called_once_with("test_123")
        assert actual == expected

    def get_not_exist_test(self, storage_repository):
        storage_repository._redis.exists = Mock(return_value=False)
        storage_repository._redis.get = Mock()

        actual = storage_repository.get("test_123")

        storage_repository._redis.get.assert_not_called()
        assert actual is None

    def find_test(self, storage_repository):
        expected = [{"test_1": 12345}, {"test_2": 12345}]
        storage_repository.get = Mock()
        storage_repository.get.side_effect = expected
        storage_repository._redis.scan_iter = MagicMock()
        storage_repository._redis.scan_iter.return_value = ["test_1", "test_2"]

        actual = storage_repository.find_all("test")

        storage_repository._redis.scan_iter.assert_called_once_with("test")
        assert actual == expected

    def remove_test(self, storage_repository):
        storage_repository._redis.delete = Mock()

        actual = storage_repository.remove("test_123", "test_234")

        storage_repository._redis.delete.assert_called_once_with("test_123", "test_234")
        assert actual is None
