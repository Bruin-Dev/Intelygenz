import asyncio

import redis
from application.actions.tnba_feedback_action import TNBAFeedback
from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.t7_repository import T7Repository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer
from prometheus_client import start_http_server


class Container:
    def __init__(self):
        # LOGGER
        self._logger = LoggerClient(config).get_logger()
        self._logger.info(f"TNBA feedback starting in {config.CURRENT_ENVIRONMENT}...")

        # REDIS
        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._redis_tnba_client = redis.Redis(host=config.REDIS_TNBA_FEEDBACK["host"], port=6379, decode_responses=True)
        self._redis_tnba_client.ping()

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

        # HEALTHCHECK ENDPOINT
        self._server = QuartServer(config)

        # MESSAGES STORAGE MANAGER
        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        # EVENT BUS
        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)

        # REPOSITORIES
        self._notifications_repository = NotificationsRepository(event_bus=self._event_bus)
        self._bruin_repository = BruinRepository(
            event_bus=self._event_bus,
            logger=self._logger,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._customer_cache = CustomerCacheRepository(
            event_bus=self._event_bus,
            logger=self._logger,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._t7_repository = T7Repository(
            event_bus=self._event_bus,
            logger=self._logger,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        # ACTIONS
        self._tnba_feedback = TNBAFeedback(
            self._event_bus,
            self._logger,
            self._scheduler,
            config,
            self._t7_repository,
            self._customer_cache,
            self._bruin_repository,
            self._notifications_repository,
            self._redis_tnba_client,
        )

    async def _start(self):
        self._start_prometheus_metrics_server()

        await self._event_bus.connect()

        await self._tnba_feedback.start_tnba_automated_process(exec_on_start=True)

        self._scheduler.start()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])

    async def start_server(self):
        await self._server.run_server()

    async def run(self):
        await self._start()


if __name__ == "__main__":
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
