import json


class RedisRepository:
    def __init__(self, redis_client):
        self.redis_client = redis_client

    def get_value_if_exist(self, key):

        if self.redis_client.exists(key):
            cache = self.redis_client.get(key)
            return json.loads(cache)

        return []

    def set_value_for_key(self, key, value):
        self.redis_client.set(key, json.dumps(value))
