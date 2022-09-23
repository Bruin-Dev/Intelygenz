class StorageRepository:
    def __init__(self, config, redis):
        self._config = config
        self._redis = redis

        self._redis_key_prefix = f"{config.ENVIRONMENT_NAME}-task_dispatcher"
