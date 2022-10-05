import logging
import sys
from dataclasses import asdict

import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from forticloud_client.client import ForticloudClient as ForticloudClientLibrary
from framework.http.server import Config as QuartConfig
from framework.http.server import Server as QuartServer
from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler
from framework.nats.client import Client
from framework.nats.exceptions import NatsException
from framework.nats.models import *
from framework.nats.temp_payload_storage import RedisLegacy as RedisStorage
from prometheus_client import start_http_server

from application.actions.refresh_cache import RefreshCache
from application.clients.bruin_client import BruinClient
from application.clients.forticloud_client import ForticloudClient
from application.repositories.bruin_repository import BruinRepository
from application.repositories.cache_repository import CacheRepository
from application.repositories.forticloud_repository import ForticloudRepository
from application.repositories.redis_repository import RedisRepository
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
        app_logger.info("Forticloud cache starting...")

        redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)

        tmp_redis_storage = RedisStorage(storage_client=redis_client)
        self._nats_client = Client(temp_payload_storage=tmp_redis_storage)

        redis_forticloud_cache = redis.Redis(
            host=config.REDIS_FORTICLOUD_CACHE["host"], port=6379, decode_responses=True
        )

        self._scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

        self._forticloud_client_library = ForticloudClientLibrary(config=config.FORTICLOUD_CONFIG)
        self._forticloud_client = ForticloudClient(forticloud_client=self._forticloud_client_library)
        self._forticloud_repository = ForticloudRepository(forticloud_client=self._forticloud_client)

        self._bruin_client = BruinClient(nats_client=self._nats_client)
        self._bruin_repository = BruinRepository(bruin_client=self._bruin_client)

        self._redis_repository = RedisRepository(redis_client=redis_forticloud_cache)

        self._cache_repository = CacheRepository(
            config=config,
            scheduler=self._scheduler,
            forticloud_repository=self._forticloud_repository,
            redis_repository=self._redis_repository,
            bruin_repository=self._bruin_repository,
        )
        self._refresh_cache = RefreshCache(self._cache_repository)

        self._server = QuartServer(QuartConfig(port=config.QUART_CONFIG["port"]))

    async def _init_nats_conn(self):
        conn = Connection(servers=config.NATS_CONFIG["servers"])

        try:
            await self._nats_client.connect(**asdict(conn))
        except NatsException as e:
            app_logger.exception(e)
            bail_out()

    async def start(self):
        # Setup NATS

        await self._init_nats_conn()
        await self._forticloud_client_library.login()
        await self._refresh_cache.refresh_cache()

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

    loop.run_until_complete(container.start())
    loop.run_until_complete(container.start_server())
    loop.run_forever()
