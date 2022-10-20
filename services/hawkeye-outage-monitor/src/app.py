import asyncio
import logging
import sys
from dataclasses import asdict

import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from framework.http.server import Config as QuartConfig
from framework.http.server import Server as QuartServer
from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler
from framework.nats.client import Client
from framework.nats.exceptions import NatsException
from framework.nats.models import Connection
from framework.nats.temp_payload_storage import RedisLegacy as RedisStorage
from prometheus_client import start_http_server

from application.actions.outage_monitoring import OutageMonitor
from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.hawkeye_repository import HawkeyeRepository
from application.repositories.metrics_repository import MetricsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.utils_repository import UtilsRepository
from config import config

base_handler = StdoutHandler()
base_handler.setFormatter(StandardFormatter(environment_name=config.ENVIRONMENT_NAME))

app_logger = logging.getLogger("application")
app_logger.setLevel(logging.DEBUG)
app_logger.addHandler(base_handler)

framework_logger = logging.getLogger("framework")
framework_logger.setLevel(logging.DEBUG)
framework_logger.addHandler(base_handler)

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


def bail_out():
    app_logger.critical("Stopping application...")
    sys.exit(1)


class Container:
    def __init__(self):
        # LOGGER
        app_logger.info(f"Hawkeye Outage Monitor starting in {config.CURRENT_ENVIRONMENT}...")

        # REDIS
        redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        redis_client.ping()

        tmp_redis_storage = RedisStorage(storage_client=redis_client)
        self._nats_client = Client(temp_payload_storage=tmp_redis_storage)

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

        # METRICS
        self._metrics_repository = MetricsRepository(config=config)

        # REPOSITORIES
        self._notifications_repository = NotificationsRepository(nats_client=self._nats_client)
        self._hawkeye_repository = HawkeyeRepository(
            nats_client=self._nats_client,
            notifications_repository=self._notifications_repository,
        )
        self._bruin_repository = BruinRepository(
            nats_client=self._nats_client,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._customer_cache_repository = CustomerCacheRepository(
            nats_client=self._nats_client,
            notifications_repository=self._notifications_repository,
        )
        self._utils_repository = UtilsRepository()

        # ACTIONS
        self._outage_monitor = OutageMonitor(
            nats_client=self._nats_client,
            scheduler=self._scheduler,
            config=config,
            metrics_repository=self._metrics_repository,
            bruin_repository=self._bruin_repository,
            hawkeye_repository=self._hawkeye_repository,
            notifications_repository=self._notifications_repository,
            customer_cache_repository=self._customer_cache_repository,
            utils_repository=self._utils_repository,
        )
        self._server = QuartServer(QuartConfig(port=config.QUART_CONFIG["port"]))

    async def _init_nats_conn(self):
        conn = Connection(servers=config.NATS_CONFIG["servers"])
        try:
            await self._nats_client.connect(**asdict(conn))
        except NatsException as e:
            app_logger.exception(e)
            bail_out()

    async def start(self):
        self._start_prometheus_metrics_server()

        await self._init_nats_conn()

        await self._outage_monitor.start_hawkeye_outage_monitoring(exec_on_start=True)
        self._scheduler.start()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])

    async def start_server(self):
        await self._server.run()

    async def run(self):
        await self.start()


if __name__ == "__main__":
    container = Container()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(container.start())
    loop.run_until_complete(container.start_server())
    loop.run_forever()
