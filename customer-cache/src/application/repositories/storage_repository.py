import json
from pytz import utc
from dateutil.parser import parse


class StorageRepository:
    def __init__(self, config, logger, redis):
        self._config = config
        self._logger = logger
        self._redis = redis

    def get_cache(self, key):
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
        self._redis.set(key, json.dumps(cache))
