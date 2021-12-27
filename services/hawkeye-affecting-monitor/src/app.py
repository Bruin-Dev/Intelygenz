import asyncio

import redis

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer
from prometheus_client import start_http_server

from application.actions.affecting_monitoring import AffectingMonitor
from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.hawkeye_repository import HawkeyeRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.utils_repository import UtilsRepository
from config import config


class Container:

    def __init__(self):
        # LOGGER
        self._logger = LoggerClient(config).get_logger()
        self._logger.info(f'Hawkeye Affecting Monitor starting in {config.MONITOR_CONFIG["environment"]}...')

        # REDIS
        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

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
        self._hawkeye_repository = HawkeyeRepository(event_bus=self._event_bus, logger=self._logger, config=config,
                                                     notifications_repository=self._notifications_repository)
        self._bruin_repository = BruinRepository(event_bus=self._event_bus, logger=self._logger, config=config,
                                                 notifications_repository=self._notifications_repository)
        self._customer_cache_repository = CustomerCacheRepository(
            event_bus=self._event_bus, logger=self._logger, config=config,
            notifications_repository=self._notifications_repository
        )
        self._utils_repository = UtilsRepository()

        # ACTIONS
        self._affecting_monitor = AffectingMonitor(
            logger=self._logger, scheduler=self._scheduler, config=config,
            bruin_repository=self._bruin_repository, hawkeye_repository=self._hawkeye_repository,
            notifications_repository=self._notifications_repository,
            customer_cache_repository=self._customer_cache_repository,
            utils_repository=self._utils_repository,
        )

    async def _start(self):
        await self._event_bus.connect()

        await self._affecting_monitor.start_hawkeye_affecting_monitoring(exec_on_start=True)
        self._scheduler.start()

    async def start_server(self):
        await self._server.run_server()

    async def run(self):
        await self._start()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
