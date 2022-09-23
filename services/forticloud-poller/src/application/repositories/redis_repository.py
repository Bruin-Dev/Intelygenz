import json
from typing import List


class RedisRepository:
    def __init__(self, redis):
        self.redis = redis

    def get_value_if_exist(self, key: str) -> List:
        if self.redis.exists(key):
            data = self.redis.get(key)
            return json.loads(data)

        return []

    def get_list_switches_of_redis(self) -> List:
        return self.get_value_if_exist(key="switches")

    def get_list_access_points_of_redis(self) -> List:
        return self.get_value_if_exist(key="access_points")
