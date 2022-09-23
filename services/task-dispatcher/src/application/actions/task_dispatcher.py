import logging

logger = logging.getLogger(__name__)


class TaskDispatcher:
    def __init__(
        self,
        nats_client,
        scheduler,
        config,
        storage_repository,
        bruin_repository,
    ):
        self._nats_client = nats_client
        self._scheduler = scheduler
        self._config = config
        self._storage_repository = storage_repository
        self._bruin_repository = bruin_repository

    async def start_dispatching(self):
        pass
