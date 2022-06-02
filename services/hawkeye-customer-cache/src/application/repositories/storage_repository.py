import json


class StorageRepository:
    def __init__(self, config, logger, redis):
        self._config = config
        self._logger = logger
        self._redis = redis

        self.__cache_key = f"{config.ENVIRONMENT_NAME}-hawkeye"

    def get_hawkeye_cache(self):
        if self._redis.exists(self.__cache_key):
            cache = self._redis.get(self.__cache_key)
            return json.loads(cache)
        return []

    def set_hawkeye_cache(self, cache):
        self._redis.set(self.__cache_key, json.dumps(cache))
