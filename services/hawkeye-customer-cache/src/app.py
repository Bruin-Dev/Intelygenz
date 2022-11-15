import asyncio
import logging
import sys
from dataclasses import asdict

from application.actions.get_customers import GetCustomers
from application.actions.refresh_cache import RefreshCache
from application.models import subscriptions
from application.repositories.bruin_repository import BruinRepository
from application.repositories.email_repository import EmailRepository
from application.repositories.hawkeye_repository import HawkeyeRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.storage_repository import StorageRepository
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
from framework.nats.models import Connection
from framework.nats.temp_payload_storage import RedisLegacy as RedisStorage
from prometheus_client import start_http_server
from redis import Redis

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
        app_logger.info(f"Hawkeye customer cache starting in {config.ENVIRONMENT_NAME}...")

        # HEALTHCHECK ENDPOINT
        self._server = HealthServer(HealthConfig(port=config.QUART_CONFIG["port"]))

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

        # REDIS
        redis = Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        redis.ping()

        self._redis_customer_cache_client = Redis(
            host=config.REDIS_CUSTOMER_CACHE["host"], port=6379, decode_responses=True
        )
        self._redis_customer_cache_client.ping()

        # NATS
        tmp_redis_storage = RedisStorage(storage_client=redis)
        self._nats_client = Client(temp_payload_storage=tmp_redis_storage)

        # REPOSITORIES
        self._notifications_repository = NotificationsRepository(nats_client=self._nats_client, config=config)
        self._email_repository = EmailRepository(nats_client=self._nats_client)
        self._bruin_repository = BruinRepository(
            nats_client=self._nats_client,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._hawkeye_repository = HawkeyeRepository(
            config=config,
            nats_client=self._nats_client,
            notifications_repository=self._notifications_repository,
        )
        self._storage_repository = StorageRepository(config=config, redis=self._redis_customer_cache_client)

        # ACTIONS
        self._refresh_cache = RefreshCache(
            config,
            self._scheduler,
            self._storage_repository,
            self._bruin_repository,
            self._hawkeye_repository,
            self._notifications_repository,
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
            # NOTE: Using dataclasses::asdict() throws a pickle error, so we need to use <dataclass>.__dict__ instead
            cb = GetCustomers(config, self._storage_repository)
            await self._nats_client.subscribe(**subscriptions.GetCustomers(cb=cb).__dict__)
        except NatsException as e:
            app_logger.exception(e)
            bail_out()

    async def start(self):
        # Start NATS connection
        await self._init_nats_conn()
        await self._init_subscriptions()

        # Prepare scheduler jobs
        await self._refresh_cache.schedule_cache_refresh()

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

    loop.run_until_complete(container.start())
    loop.run_until_complete(container.start_server())
    loop.run_forever()
