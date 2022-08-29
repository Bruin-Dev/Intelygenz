import asyncio
import logging
from dataclasses import asdict

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from framework.http.server import Config as HealthConfig
from framework.http.server import Server as HealthServer
from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler
from framework.nats.client import Client
from framework.nats.models import Connection
from framework.nats.temp_payload_storage import RedisLegacy as RedisStorage
from prometheus_client import start_http_server
from redis.client import Redis

from application.actions.intermapper_monitoring import InterMapperMonitor
from application.repositories.bruin_repository import BruinRepository
from application.repositories.dri_repository import DRIRepository
from application.repositories.email_repository import EmailRepository
from application.repositories.metrics_repository import MetricsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.utils_repository import UtilsRepository
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


class Container:
    def __init__(self):
        # LOGGER
        app_logger.info(f"InterMapper Outage Monitor starting in {config.CURRENT_ENVIRONMENT}...")

        # HEALTHCHECK ENDPOINT
        self._server = HealthServer(HealthConfig(port=config.QUART_CONFIG["port"]))

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

        # REDIS
        redis = Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        redis.ping()

        # NATS
        tmp_redis_storage = RedisStorage(storage_client=redis)
        self._nats_client = Client(temp_payload_storage=tmp_redis_storage)

        # METRICS
        self._metrics_repository = MetricsRepository()

        # REPOSITORIES
        self._utils_repository = UtilsRepository()
        self._notifications_repository = NotificationsRepository(self._nats_client, config)
        self._email_repository = EmailRepository(self._nats_client, config, self._notifications_repository)
        self._dri_repository = DRIRepository(self._nats_client, config, self._notifications_repository)
        self._bruin_repository = BruinRepository(self._nats_client, config, self._notifications_repository)

        # ACTIONS
        self._intermapper_monitoring = InterMapperMonitor(
            self._scheduler,
            config,
            self._utils_repository,
            self._metrics_repository,
            self._notifications_repository,
            self._email_repository,
            self._bruin_repository,
            self._dri_repository,
        )

    async def run(self):
        # Prometheus
        self._start_prometheus_metrics_server()

        # Start NATS connection
        conn = Connection(servers=config.NATS_CONFIG["servers"])
        await self._nats_client.connect(**asdict(conn))

        # Prepare scheduler jobs
        await self._intermapper_monitoring.start_intermapper_outage_monitoring(exec_on_start=True)

        # Start scheduler
        self._scheduler.start()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])

    async def start_server(self):
        await self._server.run()


if __name__ == "__main__":
    container = Container()

    loop = asyncio.get_event_loop()

    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)

    loop.run_forever()
