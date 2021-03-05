import json
import pytest
from unittest.mock import Mock
from asynctest import CoroutineMock
from datetime import datetime

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

    def get_cache_key_exist_test(self, instance_storage_repository):
        redis_key = "VCO1"
        redis_cache = ["Edge list"]

        instance_storage_repository._redis.exists = Mock(return_value=True)
        instance_storage_repository._redis.get = Mock(return_value=json.dumps(redis_cache))

        cache = instance_storage_repository.get_cache(redis_key)

        assert cache == redis_cache

    def get_cache_key_doesnt_exist_test(self, instance_storage_repository):
        redis_key = "VCO1"
        redis_cache = ["Edge list"]

        instance_storage_repository._redis.exists = Mock(return_value=False)
        instance_storage_repository._redis.get = Mock(return_value=json.dumps(redis_cache))

        cache = instance_storage_repository.get_cache(redis_key)

        assert cache == []

    def set_cache_test(self, instance_storage_repository):
        redis_key = "VCO1"
        redis_cache = ["Edge list"]

        instance_storage_repository._redis.set = Mock()

        instance_storage_repository.set_cache(redis_key, redis_cache)

        instance_storage_repository._redis.set.assert_called_with(redis_key, json.dumps(redis_cache))
