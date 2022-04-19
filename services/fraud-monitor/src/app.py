import asyncio

import redis
from prometheus_client import start_http_server

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer

from application.repositories.utils_repository import UtilsRepository
from application.repositories.bruin_repository import BruinRepository
from application.repositories.ticket_repository import TicketRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.actions.fraud_monitoring import FraudMonitor
from config import config


class Container:

    def __init__(self):
        # LOGGER
        self._logger = LoggerClient(config).get_logger()
        self._logger.info(f'Fraud Monitor starting in {config.CURRENT_ENVIRONMENT}...')

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
        self._utils_repository = UtilsRepository()
        self._notifications_repository = NotificationsRepository(self._logger, self._event_bus, config)
        self._bruin_repository = BruinRepository(self._event_bus, self._logger, config, self._notifications_repository)
        self._ticket_repository = TicketRepository(self._utils_repository)

        # ACTIONS
        self._fraud_monitoring = FraudMonitor(self._event_bus, self._logger, self._scheduler, config,
                                              self._notifications_repository, self._bruin_repository,
                                              self._ticket_repository, self._utils_repository)

    async def _start(self):
        self._start_prometheus_metrics_server()

        await self._event_bus.connect()
        await self._fraud_monitoring.start_fraud_monitoring(exec_on_start=True)
        self._scheduler.start()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG['port'])

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
