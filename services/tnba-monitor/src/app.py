import asyncio
import logging
import sys
from dataclasses import asdict

import redis
from application.actions.tnba_monitor import TNBAMonitor
from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.metrics_repository import MetricsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.prediction_repository import PredictionRepository
from application.repositories.t7_repository import T7Repository
from application.repositories.ticket_repository import TicketRepository
from application.repositories.trouble_repository import TroubleRepository
from application.repositories.utils_repository import UtilsRepository
from application.repositories.velocloud_repository import VelocloudRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from framework.http.server import Config as HealthConfig
from framework.http.server import Server as HealthServer
from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler
from framework.nats.client import Client
from framework.nats.exceptions import NatsException
from framework.nats.models import *
from framework.nats.models import Connection
from framework.nats.temp_payload_storage import RedisLegacy as RedisStorage
from prometheus_client import start_http_server
from pytz import timezone

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
        app_logger.info("TNBA Monitor starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()
        tmp_redis_storage = RedisStorage(self._redis_client)
        self._nats_client = Client(temp_payload_storage=tmp_redis_storage)

        self._scheduler = AsyncIOScheduler(timezone=timezone(config.TIMEZONE))

        self._metrics_repository = MetricsRepository(config=config)

        self._utils_repository = UtilsRepository()
        self._ticket_repo = TicketRepository(config, self._utils_repository)
        self._prediction_repo = PredictionRepository(config, self._utils_repository)
        self._notifications_repository = NotificationsRepository(nats_client=self._nats_client, config=config)
        self._bruin_repository = BruinRepository(
            nats_client=self._nats_client,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._velocloud_repository = VelocloudRepository(
            nats_client=self._nats_client,
            config=config,
            notifications_repository=self._notifications_repository,
            utils_repository=self._utils_repository,
        )
        self._t7_repository = T7Repository(
            nats_client=self._nats_client,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._trouble_repository = TroubleRepository(config, self._utils_repository)
        self._customer_cache_repository = CustomerCacheRepository(
            nats_client=self._nats_client,
            config=config,
            notifications_repository=self._notifications_repository,
        )

        self._tnba_monitor = TNBAMonitor(
            self._nats_client,
            self._scheduler,
            config,
            self._metrics_repository,
            self._t7_repository,
            self._ticket_repo,
            self._customer_cache_repository,
            self._bruin_repository,
            self._velocloud_repository,
            self._prediction_repo,
            self._notifications_repository,
            self._utils_repository,
            self._trouble_repository,
        )

        self._server = HealthServer(HealthConfig(port=config.QUART_CONFIG["port"]))

    async def _init_nats_conn(self):
        conn = Connection(servers=config.NATS_CONFIG["servers"])

        try:
            await self._nats_client.connect(**asdict(conn))
        except NatsException as e:
            app_logger.exception(e)
            bail_out()

    async def start(self):
        # Setup prometheus
        self._start_prometheus_metrics_server()

        # Setup NATS
        await self._init_nats_conn()

        # Setup scheduler
        self._scheduler.start()

        await self._tnba_monitor.start_tnba_automated_process(exec_on_start=True)

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])

    async def start_server(self):
        await self._server.run()

    async def run(self):
        await self._start()


if __name__ == "__main__":
    container = Container()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(container.start())
    loop.run_until_complete(container.start_server())

    loop.run_forever()
