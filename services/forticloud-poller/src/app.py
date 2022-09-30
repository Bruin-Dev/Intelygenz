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
from framework.nats.client import Client as NatsClient
from framework.nats.models import Connection
from framework.nats.temp_payload_storage import RedisLegacy as RedisStorage
from redis.client import Redis

from application.actions.forticloud_poller import ForticloudPoller
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.redis_repository import RedisRepository
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
        app_logger.info("Forticloud poller starting...")

        # HEALTHCHECK ENDPOINT
        self._server = HealthServer(HealthConfig(port=config.QUART_CONFIG["port"]))

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

        # REDIS FORTICLOUD CACHE
        redis_forticloud_cache = Redis(host=config.REDIS_FORTICLOUD_CACHE["host"], port=6379, decode_responses=True)
        redis_forticloud_cache.ping()

        # REDIS
        redis = Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        redis.ping()

        # NATS
        tmp_redis_storage = RedisStorage(storage_client=redis)
        self._nats_client = NatsClient(temp_payload_storage=tmp_redis_storage)

        # REPOSITORIES
        self._notifications_repository = NotificationsRepository(self._nats_client, config)
        self._redis_repository = RedisRepository(redis_forticloud_cache)

        # ACTIONS
        self._forticloud_poller = ForticloudPoller(
            self._nats_client,
            self._scheduler,
            config,
            self._redis_repository,
            self._notifications_repository,
        )

    async def run(self):
        # Start NATS connection
        conn = Connection(servers=config.NATS_CONFIG["servers"])
        await self._nats_client.connect(**asdict(conn))

        # Prepare scheduler jobs
        await self._forticloud_poller.start_forticloud_poller(exec_on_start=True)

        # Start scheduler
        self._scheduler.start()

    async def start_server(self):
        await self._server.run()


if __name__ == "__main__":
    container = Container()

    loop = asyncio.get_event_loop()

    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)

    loop.run_forever()
