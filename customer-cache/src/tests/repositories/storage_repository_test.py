import json
from unittest.mock import Mock
from unittest.mock import patch
from datetime import datetime
from datetime import timedelta

from application.repositories import storage_repository as storage_repository_module
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

    def get_refresh_date_with_key_missing_in_redis_test(self, instance_storage_repository):
        instance_storage_repository._redis.get = Mock(return_value=None)

        result = instance_storage_repository.get_refresh_date()

        assert result is None

    def get_refresh_date_with_key_stored_in_redis_test(self, instance_storage_repository):
        next_refresh_date_str = '06/30/2021, 11:55:00'
        next_refresh_date = datetime.strptime(next_refresh_date_str, '%m/%d/%Y, %H:%M:%S')

        instance_storage_repository._redis.get = Mock(return_value=next_refresh_date_str)

        result = instance_storage_repository.get_refresh_date()

        assert result == next_refresh_date

    def update_refresh_date_test(self, instance_storage_repository):
        next_refresh_key = 'next_refresh_date'

        current_datetime = datetime.utcnow()
        next_refresh_interval = instance_storage_repository._config.REFRESH_CONFIG['refresh_map_minutes']
        next_refresh_date = current_datetime + timedelta(minutes=next_refresh_interval)
        next_refresh_date_str = next_refresh_date.strftime('%m/%d/%Y, %H:%M:%S')

        instance_storage_repository._redis.set = Mock()

        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.object(storage_repository_module, 'datetime', new=datetime_mock):
            instance_storage_repository.update_refresh_date()

        instance_storage_repository._redis.set.assert_called_once_with(next_refresh_key, next_refresh_date_str)
