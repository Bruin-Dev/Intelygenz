import asyncio
import logging
import sys
from dataclasses import asdict

import redis
from application.actions.task_dispatcher import TaskDispatcher
from application.repositories.bruin_repository import BruinRepository
from application.repositories.notifications_repository import NotificationsRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from framework.http.server import Config as HealthConfig
from framework.http.server import Server as HealthServer
from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler
from framework.nats.client import Client
from framework.nats.models import Connection
from framework.nats.temp_payload_storage import RedisLegacy as RedisStorage
from framework.storage.task_dispatcher_client import TaskDispatcherClient
from prometheus_client import start_http_server

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
        app_logger.info(f"Task dispatcher starting in {config.CURRENT_ENVIRONMENT}...")

        # HEALTHCHECK ENDPOINT
        self._server = HealthServer(HealthConfig(port=config.QUART_CONFIG["port"]))

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

        # REDIS
        redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        redis_client.ping()
        self._task_dispatcher_client = TaskDispatcherClient(config, redis_client)

        # NATS
        tmp_redis_storage = RedisStorage(storage_client=redis_client)
        self._nats_client = Client(temp_payload_storage=tmp_redis_storage)

        # REPOSITORIES
        self._notifications_repository = NotificationsRepository(self._nats_client, config)
        self._bruin_repository = BruinRepository(self._nats_client, config, self._notifications_repository)

        # ACTIONS
        self._task_dispatcher = TaskDispatcher(
            self._nats_client,
            self._scheduler,
            self._task_dispatcher_client,
            config,
            self._bruin_repository,
        )

    async def run(self):
        # Prometheus
        self._start_prometheus_metrics_server()

        # Start NATS connection
        conn = Connection(servers=config.NATS_CONFIG["servers"])
        await self._nats_client.connect(**asdict(conn))

        # Prepare scheduler jobs
        await self._task_dispatcher.start_dispatching()

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
