import asyncio
import logging
import sys
from dataclasses import asdict

import redis
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

from application.actions.digi_reboot import DiGiReboot
from application.actions.get_digi_recovery_logs import DiGiRecoveryLogs
from application.clients.digi_client import DiGiClient
from application.models import subscriptions
from application.repositories.digi_repository import DiGiRepository
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
        app_logger.info("DiGi bridge starting...")

        redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        redis_client.ping()

        tmp_redis_storage = RedisStorage(storage_client=redis_client)
        self._nats_client = Client(temp_payload_storage=tmp_redis_storage)

        self._scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

        self._digi_client = DiGiClient(config)
        self._digi_repository = DiGiRepository(config, self._scheduler, self._digi_client)

        self._server = QuartServer(QuartConfig(port=config.QUART_CONFIG["port"]))

    async def _init_nats_conn(self):
        conn = Connection(servers=config.NATS_CONFIG["servers"])

        try:
            await self._nats_client.connect(**asdict(conn))
        except NatsException as e:
            app_logger.exception(e)
            bail_out()

    async def _init_subscriptions(self):
        try:
            cb = DiGiReboot(self._digi_repository)
            await self._nats_client.subscribe(**subscriptions.DigiReboot(cb=cb).__dict__)
            cb = DiGiRecoveryLogs(self._digi_repository)
            await self._nats_client.subscribe(**subscriptions.GetDigiRecoveryLogs(cb=cb).__dict__)

        except NatsException as e:
            app_logger.exception(e)
            bail_out()

    async def start(self):
        self._start_prometheus_metrics_server()

        await self._init_nats_conn()
        await self._init_subscriptions()
        await self._digi_client.create_session()
        await self._digi_repository.login_job()
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
