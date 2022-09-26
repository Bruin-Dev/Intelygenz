import json
from datetime import datetime
from enum import Enum


class TaskTypes(Enum):
    TICKET_FORWARDS = "ticket_forwards"


class TaskDispatcherClient:
    def __init__(self, config, redis):
        self._config = config
        self._redis = redis

        self._redis_key_prefix = f"{config.ENVIRONMENT_NAME}-task_dispatcher"

    def schedule_task(self, date: datetime, task_type: TaskTypes, task_key: str, task_data: dict):
        zkey = f"{self._redis_key_prefix}-z-{task_type.value}"
        hkey = f"{self._redis_key_prefix}-h-{task_type.value}"
        timestamp = date.timestamp()

        self._redis.zadd(zkey, {task_key: timestamp})
        self._redis.hset(hkey, task_key, json.dumps(task_data))

    def clear_task(self, task_type: TaskTypes, task_key: str) -> int:
        zkey = f"{self._redis_key_prefix}-z-{task_type.value}"
        hkey = f"{self._redis_key_prefix}-h-{task_type.value}"

        zresult = self._redis.zrem(zkey, task_key)
        hresult = self._redis.hdel(hkey, task_key)
        return zresult + hresult
