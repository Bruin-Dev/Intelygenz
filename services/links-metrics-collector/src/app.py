import asyncio
import logging
import sys
from dataclasses import asdict

import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
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

from application.actions.store_links_metrics import StoreLinkMetrics
from application.clients.mongo_client import MyMongoClient
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
        app_logger.info(f"Links metrics collector starting in: {config.CURRENT_ENVIRONMENT}...")

        # REDIS
        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        # NATS
        tmp_redis_storage = RedisStorage(self._redis_client)
        self._nats_client = Client(temp_payload_storage=tmp_redis_storage)

        # CLIENTS
        self._mongo_client = MyMongoClient(config=config)

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=config.SCHEDULER_TIMEZONE)

        # ACTIONS
        self._links_metrics_collector = StoreLinkMetrics(config, self._nats_client, self._mongo_client, self._scheduler)

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

        await self._links_metrics_collector.start_links_metrics_collector()

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

    loop.run_until_complete(container.run())
    loop.run_until_complete(container.start_server())

    loop.run_forever()
