import json
from unittest.mock import Mock

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

    def get_cache_exist_test(self, storage_repository, cache_probes):
        storage_repository._redis.exists = Mock(return_value=True)
        storage_repository._redis.get = Mock(return_value=json.dumps(cache_probes))

        cache = storage_repository.get_hawkeye_cache()

        assert cache == cache_probes

    def get_cache_not_exist_test(self, storage_repository):
        storage_repository._redis.exists = Mock(return_value=False)

        cache = storage_repository.get_hawkeye_cache()

        assert cache == []

    def set_cache_test(self, storage_repository, cache_probes):
        storage_repository._redis.set = Mock()
        storage_repository.set_hawkeye_cache(cache_probes)

        redis_key = f"{storage_repository._config.ENVIRONMENT_NAME}-hawkeye"
        storage_repository._redis.set.assert_called_with(redis_key, json.dumps(cache_probes))
