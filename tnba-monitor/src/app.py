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
from application.repositories.monitoring_map_repository import MonitoringMapRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.velocloud_repository import VelocloudRepository

from application.repositories.ticket_repository import TicketRepository
from application.repositories.prediction_repository import PredictionRepository
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

        self._ticket_repo = TicketRepository(config, self._logger, self._event_bus)
        self._prediction_repo = PredictionRepository(config, self._logger, self._event_bus)
        self._notifications_repository = NotificationsRepository(event_bus=self._event_bus)
        self._velocloud_repository = VelocloudRepository(event_bus=self._event_bus, logger=self._logger, config=config,
                                                         notifications_repository=self._notifications_repository)
        self._bruin_repository = BruinRepository(event_bus=self._event_bus, logger=self._logger, config=config,
                                                 notifications_repository=self._notifications_repository)
        self._monitoring_map_repository = MonitoringMapRepository(config=config, scheduler=self._scheduler,
                                                                  event_bus=self._event_bus, logger=self._logger,
                                                                  velocloud_repository=self._velocloud_repository,
                                                                  bruin_repository=self._bruin_repository)

        self._tnba_monitor = TNBAMonitor(self._event_bus, self._logger, self._scheduler, config, self._prediction_repo,
                                         self._ticket_repo, self._monitoring_map_repository, self._bruin_repository,
                                         self._velocloud_repository)

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
