import asyncio
import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.nats.clients import NATSClient

from application.repositories.storage_repository import StorageRepository
from application.repositories.bruin_repository import BruinRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.repair_tickets_repository import RepairTicketsRepository
from application.repositories.repair_tickets_kre_repository import RepairTicketsKRERepository

from application.actions.repair_tickets_monitor import RepairTicketsMonitor
from application.actions.repair_tickets_feedback_monitor import RepairTicketsFeedbackMonitor


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Repair Tickets Monitor starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()
        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        # Redis for data storage
        self._redis_cache_client = redis.Redis(host=config.REDIS_CACHE["host"], port=6379,
                                               decode_responses=True)
        self._redis_cache_client.ping()

        self._scheduler = AsyncIOScheduler(timezone=timezone(config.MONITOR_CONFIG["timezone"]))

        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)

        self._storage_repository = StorageRepository(config, self._logger, self._redis_cache_client)
        self._notifications_repository = NotificationsRepository(self._event_bus)
        self._bruin_repository = BruinRepository(self._event_bus, self._logger, config, self._notifications_repository)

        self._repair_tickets_repository = RepairTicketsRepository(self._logger, config,
                                                                  self._notifications_repository,
                                                                  self._storage_repository)
        self._repair_tickets_kre_repository = RepairTicketsKRERepository(self._logger, config,
                                                                         self._notifications_repository)

        self._repair_tickets_monitor = RepairTicketsMonitor(self._event_bus, self._logger, self._scheduler, config,
                                                            self._repair_tickets_repository,
                                                            self._repair_tickets_kre_repository,
                                                            self._bruin_repository)
        self._repair_tickets_feedback_monitor = RepairTicketsFeedbackMonitor(
            self._event_bus, self._logger, self._scheduler, config, self._repair_tickets_repository,
            self._repair_tickets_kre_repository)

    async def _start(self):
        await self._event_bus.connect()

        await self._repair_tickets_monitor.start_repair_tickets_monitor(exec_on_start=True)
        # await self._repair_tickets_feedback_monitor.start_repair_tickets_feedback_monitor(exec_on_start=True)

        self._scheduler.start()

    async def run(self):
        await self._start()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    loop.run_forever()
