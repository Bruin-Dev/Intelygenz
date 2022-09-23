import json
from unittest.mock import Mock

import pytest


class TestRedisRepository:
    def get_data_ok_test(self, redis_repository):
        random_key = "some.random.key"
        response = "any message"
        redis_repository.redis.get = Mock(return_value=json.dumps(response))

        result = redis_repository.get_value_if_exist(random_key)

        redis_repository.redis.get.assert_called_once_with(random_key)
        assert result == response

    def get_list_switches_of_redis_ok_test(self, redis_repository):
        response = "any message"
        redis_repository.redis.get = Mock(return_value=json.dumps(response))

        result = redis_repository.get_list_switches_of_redis()

        redis_repository.redis.get.assert_called_once_with("switches")
        assert result == response

    def get_list_access_points_of_redis_ok_test(self, redis_repository):
        response = "any message"
        redis_repository.redis.get = Mock(return_value=json.dumps(response))

        result = redis_repository.get_list_access_points_of_redis()

        redis_repository.redis.get.assert_called_once_with("access_points")
        assert result == response

    def get_data_request_failing_test(self, redis_repository):
        redis_repository.redis.get = Mock(side_effect=Exception)

        with pytest.raises(Exception):
            redis_repository.get_list_access_points_of_redis()
