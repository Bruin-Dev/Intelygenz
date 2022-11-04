import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class StorageRepository:
    def __init__(self, config, redis):
        self._config = config
        self._redis = redis

        self._redis_key_prefix = config.ENVIRONMENT_NAME

        self.__next_refresh_key = f"{self._redis_key_prefix}-next_refresh_date"
        self.__next_refresh_date_format = "%m/%d/%Y, %H:%M:%S"

    def get_cache(self, key):
        key = f"{self._redis_key_prefix}-{key}"

        if self._redis.exists(key):
            logger.info(f"Cache found for {key}")
            cache = self._redis.get(key)
            return json.loads(cache)
        else:
            logger.warning(f"No cache found for {key}")
            return []

    def get_host_cache(self, filters):
        caches = []
        # If not filter add all velocloud servers to search in all
        if len(filters.keys()) == 0:
            logger.info("No VeloCloud hosts' filter was specified. Fetching caches for all hosts...")
            for velo_dict in self._config.REFRESH_CONFIG["velo_servers"]:
                filters.update(velo_dict)
        else:
            logger.info(f"Fetching caches for VeloCloud hosts: {filters.keys()}...")

        for host in filters.keys():
            host_cache = self.get_cache(host)

            if len(filters[host]) != 0:
                logger.info(
                    f"Filtering cache of {len(host_cache)} edges for host {host} by enterprises: {filters[host]}..."
                )
                host_cache = [edge for edge in host_cache if edge["edge"]["enterprise_id"] in filters[host]]
                logger.info(f"Cache for host {host} and filtered by enterprises has {len(host_cache)} edges")
            else:
                logger.info(f"No enterprises were specified to filter cache of {len(host_cache)} edges for host {host}")

            caches = caches + host_cache

        return caches

    def set_cache(self, key, cache):
        logger.info(f"Saving cache of {len(cache)} edges for {key}...")
        key = f"{self._redis_key_prefix}-{key}"
        self._redis.set(key, json.dumps(cache))
        logger.info(f"Cache saved for {key}")

    def get_refresh_date(self) -> datetime:
        logger.info("Getting next refresh date from Redis...")
        date = self._redis.get(self.__next_refresh_key)

        if date:
            logger.info(f"Got next refresh date from Redis: {date}")
            date = datetime.strptime(date, self.__next_refresh_date_format)
        else:
            logger.info(f"No {self.__next_refresh_key} key found in Redis")

        return date

    def update_refresh_date(self):
        logger.info("Setting new refresh date in Redis...")

        next_refresh = datetime.utcnow() + timedelta(minutes=self._config.REFRESH_CONFIG["refresh_map_minutes"])
        date = next_refresh.strftime(self.__next_refresh_date_format)
        self._redis.set(self.__next_refresh_key, date)

        logger.info(f"New refresh date: {date} set in Redis")
