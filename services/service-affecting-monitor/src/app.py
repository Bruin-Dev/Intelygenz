import asyncio

import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from prometheus_client import start_http_server
from pytz import timezone

from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer

from application.actions.service_affecting_monitor import ServiceAffectingMonitor
from application.actions.service_affecting_monitor_reports import ServiceAffectingMonitorReports
from application.actions.bandwidth_reports import BandwidthReports
from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.metrics_repository import MetricsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.template_management import TemplateRenderer
from application.repositories.ticket_repository import TicketRepository
from application.repositories.trouble_repository import TroubleRepository
from application.repositories.utils_repository import UtilsRepository
from application.repositories.velocloud_repository import VelocloudRepository
from config import config


class Container:

    def __init__(self):
        # LOGGER
        self._logger = LoggerClient(config).get_logger()
        self._logger.info(f'Service Affecting Monitor starting in {config.MONITOR_CONFIG["environment"]}...')

        # REDIS
        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=timezone(config.MONITOR_CONFIG['timezone']))

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
        self._template_renderer = TemplateRenderer(config=config)
        self._notifications_repository = NotificationsRepository(event_bus=self._event_bus, config=config)
        self._bruin_repository = BruinRepository(event_bus=self._event_bus, logger=self._logger, config=config,
                                                 notifications_repository=self._notifications_repository)
        self._velocloud_repository = VelocloudRepository(event_bus=self._event_bus, logger=self._logger, config=config,
                                                         utils_repository=self._utils_repository,
                                                         notifications_repository=self._notifications_repository)
        self._customer_cache_repository = CustomerCacheRepository(
            event_bus=self._event_bus, logger=self._logger, config=config,
            notifications_repository=self._notifications_repository
        )
        self._trouble_repository = TroubleRepository(config=config, utils_repository=self._utils_repository)
        self._ticket_repository = TicketRepository(config=config, trouble_repository=self._trouble_repository,
                                                   utils_repository=self._utils_repository)

        # ACTIONS
        self._service_affecting_monitor = ServiceAffectingMonitor(
            logger=self._logger, scheduler=self._scheduler, config=config,
            metrics_repository=self._metrics_repository, bruin_repository=self._bruin_repository,
            velocloud_repository=self._velocloud_repository, customer_cache_repository=self._customer_cache_repository,
            notifications_repository=self._notifications_repository, ticket_repository=self._ticket_repository,
            trouble_repository=self._trouble_repository, utils_repository=self._utils_repository,
        )

        self._service_affecting_monitor_reports = ServiceAffectingMonitorReports(
            event_bus=self._event_bus, logger=self._logger, scheduler=self._scheduler, config=config,
            template_renderer=self._template_renderer, bruin_repository=self._bruin_repository,
            notifications_repository=self._notifications_repository,
            customer_cache_repository=self._customer_cache_repository,
        )

        self._bandwidth_reports = BandwidthReports(
            logger=self._logger, scheduler=self._scheduler, config=config,
            velocloud_repository=self._velocloud_repository, bruin_repository=self._bruin_repository,
            trouble_repository=self._trouble_repository, customer_cache_repository=self._customer_cache_repository,
            notifications_repository=self._notifications_repository, utils_repository=self._utils_repository,
            template_renderer=self._template_renderer,
        )

    async def _start(self):
        self._start_prometheus_metrics_server()

        await self._event_bus.connect()

        await self._service_affecting_monitor.start_service_affecting_monitor(exec_on_start=True)
        await self._service_affecting_monitor_reports.start_service_affecting_monitor_reports_job(exec_on_start=False)
        await self._bandwidth_reports.start_bandwidth_reports_job(exec_on_start=False)

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
