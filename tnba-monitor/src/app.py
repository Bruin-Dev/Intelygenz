import asyncio
import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer

from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.prediction_repository import PredictionRepository
from application.repositories.ticket_repository import TicketRepository
from application.repositories.t7_repository import T7Repository
from application.repositories.utils_repository import UtilsRepository
from application.repositories.velocloud_repository import VelocloudRepository
from application.actions.tnba_monitor import TNBAMonitor


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("TNBA Monitor starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()
        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        self._scheduler = AsyncIOScheduler(timezone=timezone(config.TIMEZONE))
        self._server = QuartServer(config)

        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)

        self._utils_repository = UtilsRepository()
        self._ticket_repo = TicketRepository(config, self._utils_repository)
        self._prediction_repo = PredictionRepository(self._utils_repository)
        self._notifications_repository = NotificationsRepository(event_bus=self._event_bus, config=config)
        self._velocloud_repository = VelocloudRepository(event_bus=self._event_bus, logger=self._logger, config=config,
                                                         notifications_repository=self._notifications_repository)
        self._bruin_repository = BruinRepository(event_bus=self._event_bus, logger=self._logger, config=config,
                                                 notifications_repository=self._notifications_repository)
        self._t7_repository = T7Repository(event_bus=self._event_bus, logger=self._logger, config=config,
                                           notifications_repository=self._notifications_repository)
        self._customer_cache_repository = CustomerCacheRepository(
            event_bus=self._event_bus, logger=self._logger,
            config=config, notifications_repository=self._notifications_repository,
        )

        self._tnba_monitor = TNBAMonitor(self._event_bus, self._logger, self._scheduler, config, self._t7_repository,
                                         self._ticket_repo, self._customer_cache_repository, self._bruin_repository,
                                         self._velocloud_repository, self._prediction_repo,
                                         self._notifications_repository)

    async def _start(self):
        await self._event_bus.connect()

        await self._tnba_monitor.start_tnba_automated_process(exec_on_start=True)

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
