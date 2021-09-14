import json


class StorageRepository:
    def __init__(self, config, logger, redis):
        self._config = config
        self._logger = logger
        self._redis = redis

        self._redis_key_prefix = config.ENVIRONMENT_NAME

    def get(self, key):
        key = f'{self._redis_key_prefix}-{key}'

        if not self._redis.exists(key):
            return None

        value = self._redis.get(key)
        return json.loads(value)

    def find_all(self, match):
        match = f'{self._redis_key_prefix}-{match}'

        matches = []
        for key in self._redis.scan_iter(match):
            v = json.loads(self._redis.get(key))
            matches.append(v)

        return matches

    def save(self, key, data):
        key = f'{self._redis_key_prefix}-{key}'
        self._redis.set(key, json.dumps(data))

    def increment(self, key):
        key = f'{self._redis_key_prefix}-{key}'
        self._redis.incr(key, amount=1)

    def remove(self, *keys):
        keys = [f'{self._redis_key_prefix}-{key}' for key in keys]
        self._redis.delete(*keys)
