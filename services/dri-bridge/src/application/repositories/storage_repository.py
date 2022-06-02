import json


class StorageRepository:
    def __init__(self, config, logger, redis):
        self._config = config
        self._logger = logger
        self._redis = redis

        self._redis_key_prefix = f"{config.ENVIRONMENT_NAME}-dri-serial"

    def get(self, key):
        key = f"{self._redis_key_prefix}-{key}"

        if not self._redis.exists(key):
            return None

        value = self._redis.get(key)
        return json.loads(value)

    def save(self, key, data):
        key = f"{self._redis_key_prefix}-{key}"
        self._redis.set(key, json.dumps(data), ex=self._config.DRI_CONFIG["redis_save_ttl"])

    def remove(self, *keys):
        keys = [f"{self._redis_key_prefix}-{key}" for key in keys]
        self._redis.delete(*keys)
