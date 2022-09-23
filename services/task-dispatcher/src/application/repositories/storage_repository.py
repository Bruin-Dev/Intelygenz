import json
from datetime import datetime
from typing import List

from application import TaskTypes


class StorageRepository:
    def __init__(self, config, redis):
        self._config = config
        self._redis = redis

        self._redis_key_prefix = f"{config.ENVIRONMENT_NAME}-task_dispatcher"

    def get_due_tasks(self, task_type: TaskTypes) -> List[dict]:
        key = f"{self._redis_key_prefix}-z-{task_type.value}"
        timestamp = datetime.utcnow().timestamp()
        task_keys = self._redis.zrangebyscore(key, 0, timestamp)
        tasks = []

        for task_key in task_keys:
            task_data = self._get_task_data(task_type, task_key)
            tasks.append(
                {
                    "type": task_type,
                    "key": task_key,
                    "data": task_data,
                }
            )

        return tasks

    def _get_task_data(self, task_type: TaskTypes, task_key: str) -> dict:
        key = f"{self._redis_key_prefix}-h-{task_type.value}"
        task_data = self._redis.hget(key, task_key)

        if task_data:
            return json.loads(task_data)

    def delete_task(self, task_type: TaskTypes, task_key: str):
        zkey = f"{self._redis_key_prefix}-z-{task_type.value}"
        hkey = f"{self._redis_key_prefix}-h-{task_type.value}"
        self._redis.zrem(zkey, task_key)
        self._redis.hdel(hkey, task_key)
