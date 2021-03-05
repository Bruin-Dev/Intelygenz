import json


class StorageRepository:
    def __init__(self, config, logger, redis):
        self._config = config
        self._logger = logger
        self._redis = redis

    def get(self, key):
        if not self._redis.exists(key):
            return None

        value = self._redis.get(key)
        return json.loads(value)

    def find_all(self, match):
        matches = []
        for key in self._redis.scan_iter(match):
            v = self.get(key)
            matches.append(v)

        return matches

    def save(self, key, data):
        self._redis.set(key, json.dumps(data))

    def remove(self, *keys):
        self._redis.delete(*keys)
