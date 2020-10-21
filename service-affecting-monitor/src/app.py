import asyncio
import redis
from application.actions.service_affecting_monitor import ServiceAffectingMonitor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.velocloud_repository import VelocloudRepository
from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer
from prometheus_client import start_http_server

from application.repositories.metrics_repository import MetricsRepository
from application.repositories.template_management import TemplateRenderer


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info(f'Service Affecting Monitor starting in {config.MONITOR_CONFIG["environment"]}...')

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._scheduler = AsyncIOScheduler(timezone=timezone('US/Eastern'))
        self._server = QuartServer(config)

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)
        self._template_renderer = TemplateRenderer(config)
        self._metrics_repository = MetricsRepository()
        self._notifications_repository = NotificationsRepository(event_bus=self._event_bus)
        self._bruin_repository = BruinRepository(event_bus=self._event_bus, logger=self._logger, config=config,
                                                 notifications_repository=self._notifications_repository)
        self._velocloud_repository = VelocloudRepository(event_bus=self._event_bus, logger=self._logger, config=config,
                                                         notifications_repository=self._notifications_repository)
        self._customer_cache_repository = CustomerCacheRepository(
            event_bus=self._event_bus,
            logger=self._logger,
            config=config,
            notifications_repository=self._notifications_repository
        )

        self._service_affecting_monitor = ServiceAffectingMonitor(self._event_bus, self._logger, self._scheduler,
                                                                  config, self._template_renderer,
                                                                  self._metrics_repository, self._bruin_repository,
                                                                  self._velocloud_repository,
                                                                  self._customer_cache_repository)

    async def _start(self):
        self._start_prometheus_metrics_server()

        await self._event_bus.connect()

        await self._service_affecting_monitor.start_service_affecting_monitor_job(exec_on_start=True)

        self._scheduler.start()

    def _start_prometheus_metrics_server(self):
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
