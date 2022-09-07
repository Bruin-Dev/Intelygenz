import asyncio

import redis
from application.actions.outage_monitoring import OutageMonitor
from application.actions.triage import Triage
from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.digi_repository import DiGiRepository
from application.repositories.ha_repository import HaRepository
from application.repositories.metrics_repository import MetricsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.email_repository import EmailRepository
from application.repositories.outage_repository import OutageRepository
from application.repositories.triage_repository import TriageRepository
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
        self._logger.info(f"Service Outage Monitor starting in {config.CURRENT_ENVIRONMENT}...")

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
        self._email_repository = EmailRepository(event_bus=self._event_bus)
        self._velocloud_repository = VelocloudRepository(
            event_bus=self._event_bus,
            logger=self._logger,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._bruin_repository = BruinRepository(
            event_bus=self._event_bus,
            logger=self._logger,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._digi_repository = DiGiRepository(
            event_bus=self._event_bus,
            logger=self._logger,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._utils_repository = UtilsRepository()
        self._triage_repository = TriageRepository(config=config, utils_repository=self._utils_repository)
        self._ha_repository = HaRepository(config=config, logger=self._logger)
        self._customer_cache_repository = CustomerCacheRepository(
            event_bus=self._event_bus,
            logger=self._logger,
            config=config,
            notifications_repository=self._notifications_repository,
        )

        # OUTAGE UTILS
        self._outage_repository = OutageRepository(self._logger, self._ha_repository)

        # ACTIONS
        if config.ENABLE_TRIAGE_MONITORING:
            self._triage = Triage(
                self._event_bus,
                self._logger,
                self._scheduler,
                config,
                self._outage_repository,
                self._customer_cache_repository,
                self._bruin_repository,
                self._velocloud_repository,
                self._notifications_repository,
                self._triage_repository,
                self._ha_repository,
            )
        else:
            # METRICS
            self._metrics_repository = MetricsRepository(config=config)

            self._outage_monitor = OutageMonitor(
                self._event_bus,
                self._logger,
                self._scheduler,
                config,
                self._utils_repository,
                self._outage_repository,
                self._bruin_repository,
                self._velocloud_repository,
                self._notifications_repository,
                self._triage_repository,
                self._customer_cache_repository,
                self._metrics_repository,
                self._digi_repository,
                self._ha_repository,
                self._email_repository,
            )

    async def _start(self):
        self._start_prometheus_metrics_server()
        await self._event_bus.connect()

        if config.ENABLE_TRIAGE_MONITORING:
            self._logger.info("Triage monitoring enabled in config file")
            await self._triage.start_triage_job(exec_on_start=True)
        else:
            self._logger.info(
                f"Outage monitoring enabled for host "
                f'{config.MONITOR_CONFIG["velocloud_instances_filter"]} in config file'
            )
            await self._outage_monitor.start_service_outage_monitoring(exec_on_start=True)

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
