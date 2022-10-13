import asyncio
import logging
import sys
from dataclasses import asdict

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from framework.http.server import Config as HealthConfig
from framework.http.server import Server as HealthServer
from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler
from framework.nats.client import Client
from framework.nats.exceptions import NatsException
from framework.nats.models import Connection
from framework.nats.temp_payload_storage import RedisLegacy as RedisStorage
from framework.storage.task_dispatcher_client import TaskDispatcherClient
from prometheus_client import start_http_server
from redis.client import Redis

from application.actions.handle_ticket_forward import HandleTicketForward
from application.actions.outage_monitoring import OutageMonitor
from application.actions.triage import Triage
from application.models import subscriptions
from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.digi_repository import DiGiRepository
from application.repositories.email_repository import EmailRepository
from application.repositories.ha_repository import HaRepository
from application.repositories.metrics_repository import MetricsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.outage_repository import OutageRepository
from application.repositories.triage_repository import TriageRepository
from application.repositories.utils_repository import UtilsRepository
from application.repositories.velocloud_repository import VelocloudRepository
from config import config

# Standard output logging
base_handler = StdoutHandler()
base_handler.setFormatter(StandardFormatter(environment_name=config.ENVIRONMENT_NAME))

app_logger = logging.getLogger("application")
app_logger.setLevel(logging.DEBUG)
app_logger.addHandler(base_handler)

framework_logger = logging.getLogger("framework")
framework_logger.setLevel(logging.DEBUG)
framework_logger.addHandler(base_handler)

# Papertrail logging
if config.LOG_CONFIG["papertrail"]["active"]:
    pt_handler = PapertrailHandler(
        host=config.LOG_CONFIG["papertrail"]["host"],
        port=config.LOG_CONFIG["papertrail"]["port"],
    )
    pt_handler.setFormatter(
        PapertrailFormatter(
            environment_name=config.ENVIRONMENT_NAME,
            papertrail_prefix=config.LOG_CONFIG["papertrail"]["prefix"],
        )
    )
    app_logger.addHandler(pt_handler)
    framework_logger.addHandler(pt_handler)

# APScheduler logging
apscheduler_logger = logging.getLogger("apscheduler")
apscheduler_logger.setLevel(logging.DEBUG)
apscheduler_logger.addHandler(base_handler)


def bail_out():
    app_logger.critical("Stopping application...")
    sys.exit(1)


class Container:
    def __init__(self):
        app_logger.info(f"Service Outage Monitor starting in {config.CURRENT_ENVIRONMENT}...")

        # REDIS
        self._redis_client = Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()
        self._task_dispatcher_client = TaskDispatcherClient(config, self._redis_client)

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

        # HEALTHCHECK ENDPOINT
        self._server = HealthServer(HealthConfig(port=config.QUART_CONFIG["port"]))

        # NATS
        tmp_redis_storage = RedisStorage(storage_client=self._redis_client)
        self._nats_client = Client(temp_payload_storage=tmp_redis_storage)

        # REPOSITORIES
        self._notifications_repository = NotificationsRepository(nats_client=self._nats_client)
        self._email_repository = EmailRepository(nats_client=self._nats_client)
        self._velocloud_repository = VelocloudRepository(
            nats_client=self._nats_client,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._bruin_repository = BruinRepository(
            nats_client=self._nats_client,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._digi_repository = DiGiRepository(
            nats_client=self._nats_client,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._utils_repository = UtilsRepository()
        self._triage_repository = TriageRepository(config=config, utils_repository=self._utils_repository)
        self._ha_repository = HaRepository(config=config)
        self._customer_cache_repository = CustomerCacheRepository(
            nats_client=self._nats_client,
            config=config,
            notifications_repository=self._notifications_repository,
        )

        # OUTAGE UTILS
        self._outage_repository = OutageRepository(self._ha_repository)

        # ACTIONS
        if config.ENABLE_TRIAGE_MONITORING:
            self._triage = Triage(
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
                self._scheduler,
                self._task_dispatcher_client,
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

    async def _init_nats_conn(self):
        conn = Connection(servers=config.NATS_CONFIG["servers"])

        try:
            await self._nats_client.connect(**asdict(conn))
        except NatsException as e:
            app_logger.exception(e)
            bail_out()

    async def _init_subscriptions(self):
        try:
            # NOTE: Using dataclasses::asdict() throws a pickle error, so we need to use <dataclass>.__dict__instead
            cb = HandleTicketForward(self._metrics_repository)
            await self._nats_client.subscribe(**subscriptions.HandleTicketForwardSuccess(cb=cb.success).__dict__)
        except NatsException as e:
            app_logger.exception(e)
            bail_out()

    async def run(self):
        # Prometheus
        self._start_prometheus_metrics_server()

        # Start NATS connection
        await self._init_nats_conn()

        if not config.ENABLE_TRIAGE_MONITORING:
            await self._init_subscriptions()

        # Prepare scheduler jobs
        if config.ENABLE_TRIAGE_MONITORING:
            app_logger.info("Triage monitoring enabled in config file")
            await self._triage.start_triage_job(exec_on_start=True)
        else:
            app_logger.info(
                f"Outage monitoring enabled for host "
                f'{config.MONITOR_CONFIG["velocloud_instances_filter"]} in config file'
            )
            await self._outage_monitor.start_service_outage_monitoring(exec_on_start=True)

        # Start scheduler
        self._scheduler.start()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])

    async def start_server(self):
        await self._server.run()


if __name__ == "__main__":
    container = Container()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(container.run())
    loop.run_until_complete(container.start_server())
    loop.run_forever()
