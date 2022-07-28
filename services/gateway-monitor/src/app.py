import asyncio

import redis
from application.actions.monitoring import Monitor as GatewayMonitor
from application.repositories.metrics_repository import MetricsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.servicenow_repository import ServiceNowRepository
from application.repositories.utils_repository import UtilsRepository
from application.repositories.velocloud_repository import VelocloudRepository
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
        self._logger.info(f"Gateway Monitor starting in {config.CURRENT_ENVIRONMENT}...")

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

        # METRICS
        self._metrics_repository = MetricsRepository()

        # REPOSITORIES
        self._utils_repository = UtilsRepository()
        self._notifications_repository = NotificationsRepository(event_bus=self._event_bus)
        self._velocloud_repository = VelocloudRepository(
            event_bus=self._event_bus,
            logger=self._logger,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._servicenow_repository = ServiceNowRepository(
            event_bus=self._event_bus,
            logger=self._logger,
            config=config,
            notifications_repository=self._notifications_repository,
        )

        # ACTIONS
        self._monitor = GatewayMonitor(
            self._event_bus,
            self._logger,
            self._scheduler,
            config,
            self._metrics_repository,
            self._servicenow_repository,
            self._velocloud_repository,
            self._notifications_repository,
            self._utils_repository,
        )

    async def _start(self):
        self._start_prometheus_metrics_server()

        await self._event_bus.connect()
        await self._monitor.start_monitoring(exec_on_start=True)

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