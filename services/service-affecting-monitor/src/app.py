import asyncio

import redis
from application.actions.bandwidth_reports import BandwidthReports
from application.actions.service_affecting_monitor import ServiceAffectingMonitor
from application.actions.service_affecting_monitor_reports import ServiceAffectingMonitorReports
from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.email_repository import EmailRepository
from application.repositories.metrics_repository import MetricsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.template_repository import TemplateRepository
from application.repositories.ticket_repository import TicketRepository
from application.repositories.trouble_repository import TroubleRepository
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
from pytz import timezone


class Container:
    def __init__(self):
        # LOGGER
        self._logger = LoggerClient(config).get_logger()
        self._logger.info(
            f"Service Affecting Monitor starting for host {config.VELOCLOUD_HOST} in {config.CURRENT_ENVIRONMENT}..."
        )

        # REDIS
        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=timezone(config.TIMEZONE))

        # HEALTHCHECK ENDPOINT
        self._server = QuartServer(config)

        # MESSAGES STORAGE MANAGER
        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        # EVENT BUS
        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)

        # METRICS
        self._metrics_repository = MetricsRepository(config=config)

        # REPOSITORIES
        self._utils_repository = UtilsRepository()
        self._template_repository = TemplateRepository(config=config)
        self._notifications_repository = NotificationsRepository(event_bus=self._event_bus, config=config)
        self._email_repository = EmailRepository(event_bus=self._event_bus, config=config)
        self._bruin_repository = BruinRepository(
            event_bus=self._event_bus,
            logger=self._logger,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._velocloud_repository = VelocloudRepository(
            event_bus=self._event_bus,
            logger=self._logger,
            config=config,
            utils_repository=self._utils_repository,
            notifications_repository=self._notifications_repository,
        )
        self._customer_cache_repository = CustomerCacheRepository(
            event_bus=self._event_bus,
            logger=self._logger,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._trouble_repository = TroubleRepository(config=config, utils_repository=self._utils_repository)
        self._ticket_repository = TicketRepository(
            config=config, trouble_repository=self._trouble_repository, utils_repository=self._utils_repository
        )

        # ACTIONS
        self._service_affecting_monitor = ServiceAffectingMonitor(
            logger=self._logger,
            scheduler=self._scheduler,
            config=config,
            metrics_repository=self._metrics_repository,
            bruin_repository=self._bruin_repository,
            velocloud_repository=self._velocloud_repository,
            customer_cache_repository=self._customer_cache_repository,
            notifications_repository=self._notifications_repository,
            ticket_repository=self._ticket_repository,
            trouble_repository=self._trouble_repository,
            utils_repository=self._utils_repository,
        )

        self._service_affecting_monitor_reports = ServiceAffectingMonitorReports(
            event_bus=self._event_bus,
            logger=self._logger,
            scheduler=self._scheduler,
            config=config,
            template_repository=self._template_repository,
            bruin_repository=self._bruin_repository,
            notifications_repository=self._notifications_repository,
            email_repository=self._email_repository,
            customer_cache_repository=self._customer_cache_repository,
        )

        self._bandwidth_reports = BandwidthReports(
            logger=self._logger,
            scheduler=self._scheduler,
            config=config,
            velocloud_repository=self._velocloud_repository,
            bruin_repository=self._bruin_repository,
            trouble_repository=self._trouble_repository,
            customer_cache_repository=self._customer_cache_repository,
            email_repository=self._email_repository,
            utils_repository=self._utils_repository,
            template_repository=self._template_repository,
        )

    async def _start(self):
        self._start_prometheus_metrics_server()

        await self._event_bus.connect()

        await self._service_affecting_monitor.start_service_affecting_monitor(exec_on_start=True)

        if config.VELOCLOUD_HOST in config.MONITOR_REPORT_CONFIG["recipients_by_host_and_client_id"]:
            await self._service_affecting_monitor_reports.start_service_affecting_monitor_reports_job(
                exec_on_start=config.MONITOR_REPORT_CONFIG["exec_on_start"]
            )
        else:
            self._logger.warning(
                f"Job for Reoccurring Affecting Trouble Reports will not be scheduled for {config.VELOCLOUD_HOST} "
                "as these reports are disabled for this host"
            )

        if config.VELOCLOUD_HOST in config.BANDWIDTH_REPORT_CONFIG["client_ids_by_host"]:
            await self._bandwidth_reports.start_bandwidth_reports_job(
                exec_on_start=config.BANDWIDTH_REPORT_CONFIG["exec_on_start"]
            )
        else:
            self._logger.warning(
                f"Job for Daily Bandwidth Reports will not be scheduled for {config.VELOCLOUD_HOST} "
                "as these reports are disabled for this host"
            )

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
