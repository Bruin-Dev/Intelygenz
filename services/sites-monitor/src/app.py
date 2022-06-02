import asyncio

import redis
from application.actions.edge_monitoring import EdgeMonitoring
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.prometheus_repository import PrometheusRepository
from application.repositories.velocloud_repository import VelocloudRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer
from pytz import timezone


class Container:
    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Sites Monitor starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)
        self._server = QuartServer(config)

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)

        self._prometheus_repository = PrometheusRepository(config)
        self._notifications_repository = NotificationsRepository(event_bus=self._event_bus, config=config)

        self._velocloud_repository = VelocloudRepository(
            event_bus=self._event_bus,
            logger=self._logger,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._edge_monitoring = EdgeMonitoring(
            self._event_bus,
            self._logger,
            self._prometheus_repository,
            self._scheduler,
            self._velocloud_repository,
            config,
        )

    async def _start(self):
        self._edge_monitoring.start_prometheus_metrics_server()
        self._prometheus_repository.reset_counter()
        self._prometheus_repository.reset_edges_counter()

        await self._event_bus.connect()
        await self._edge_monitoring.start_edge_monitor_job(exec_on_start=True)
        self._scheduler.start()

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
