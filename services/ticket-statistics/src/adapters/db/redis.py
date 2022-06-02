import json

import redis


class Redis:
    prefix = "ticket-statistics"

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.logger.info("Connecting to Redis")
        self.client = redis.Redis(host=config["redis"]["host"], port=6379, decode_responses=True)
        self.client.ping()

    def get(self, start, end):
        key = f"{self.prefix}_{start}_{end}"

        if self.client.exists(key):
            return json.loads(self.client.get(key))

    def set(self, statistics, start, end):
        key = f"{self.prefix}_{start}_{end}"
        self.client.setex(key, self.config["redis"]["ttl"], json.dumps(statistics))
