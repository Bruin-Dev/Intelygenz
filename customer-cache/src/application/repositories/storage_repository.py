import json

from datetime import datetime
from datetime import timedelta


class StorageRepository:
    def __init__(self, config, logger, redis):
        self._config = config
        self._logger = logger
        self._redis = redis

        self._redis_key_prefix = config.ENVIRONMENT_NAME

        self.__next_refresh_key = f'{self._redis_key_prefix}-next_refresh_date'
        self.__next_refresh_date_format = '%m/%d/%Y, %H:%M:%S'

    def get_cache(self, key):
        key = f'{self._redis_key_prefix}-{key}'

        if self._redis.exists(key):
            cache = self._redis.get(key)
            return json.loads(cache)
        return []

    def get_host_cache(self, filters):
        caches = []
        # If not filter add all velocloud servers to search in all
        if len(filters.keys()) == 0:
            for velo_dict in self._config.REFRESH_CONFIG['velo_servers']:
                filters.update(velo_dict)
        for host in filters.keys():
            host_cache = self.get_cache(host)
            if len(filters[host]) != 0:
                host_cache = [edge for edge in host_cache if edge["edge"]["enterprise_id"] in filters[host]]
            caches = caches + host_cache
        return caches

    def set_cache(self, key, cache):
        key = f'{self._redis_key_prefix}-{key}'
        self._redis.set(key, json.dumps(cache))

    def get_refresh_date(self) -> datetime:
        self._logger.info("Getting next refresh date from Redis...")
        date = self._redis.get(self.__next_refresh_key)

        if date:
            self._logger.info(f"Got next refresh date from Redis: {date}")
            date = datetime.strptime(date, self.__next_refresh_date_format)
        else:
            self._logger.info(f'No {self.__next_refresh_key} key found in Redis')

        return date

    def update_refresh_date(self):
        self._logger.info('Setting new refresh date in Redis...')

        next_refresh = datetime.utcnow() + timedelta(minutes=self._config.REFRESH_CONFIG['refresh_map_minutes'])
        date = next_refresh.strftime(self.__next_refresh_date_format)
        self._redis.set(self.__next_refresh_key, date)

        self._logger.info(f'New refresh date: {date} set in Redis')
