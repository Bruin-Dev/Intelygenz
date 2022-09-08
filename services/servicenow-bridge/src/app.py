import asyncio
import logging
import sys
from dataclasses import asdict

from framework.http.server import Config as HealthConfig
from framework.http.server import Server as HealthServer
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Stdout as StdoutHandler
from framework.nats.client import Client as NatsClient
from framework.nats.exceptions import NatsException
from framework.nats.models import Connection
from framework.nats.temp_payload_storage import RedisLegacy as RedisStorage
from prometheus_client import start_http_server
from redis import Redis

from application.actions.models import subscriptions
from application.actions.report_incident import ReportIncident
from application.clients.servicenow_client import ServiceNowClient
from application.repositories.servicenow_repository import ServiceNowRepository
from config import config

log = logging.getLogger("application")
log.setLevel(logging.DEBUG)
base_handler = StdoutHandler()
base_handler.setFormatter(StandardFormatter(environment_name=config.ENVIRONMENT_NAME))
log.addHandler(base_handler)


def bail_out():
    log.critical("Stopping application...")
    sys.exit(1)


class Container:
    def __init__(self):
        log.info("ServiceNow bridge starting...")

        self._redis_client = Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        # Build up singleton dependencies
        self._servicenow_client = ServiceNowClient(config)
        self._servicenow_repository = ServiceNowRepository(self._servicenow_client)
        self._message_storage_manager = RedisStorage(self._redis_client)

        # Add NATS clients as event bus consumers
        self._nats_client = NatsClient(temp_payload_storage=self._message_storage_manager)
        # self._nats_client.add_consumer(self._subscriber_report_incident, consumer_name="report_incident")
        # self._nats_client.set_producer(self._publisher)

        self._server = HealthServer(HealthConfig(port=config.QUART_CONFIG["port"]))

    async def _init_nats_conn(self):
        conn = Connection(servers=config.NATS_CONFIG["servers"])
        log.info(f"servers={config.NATS_CONFIG['servers']}")

        try:
            await self._nats_client.connect(**asdict(conn))
        except NatsException as e:
            log.exception(e)
            bail_out()

    async def _init_subscriptions(self):
        try:
            # NOTE: Using dataclasses::asdict() throws a pickle error, so we need to use <dataclass>.__dict__ instead
            cb = ReportIncident(self._nats_client, self._servicenow_repository)
            await self._nats_client.subscribe(**subscriptions.ReportIncident(cb=cb).__dict__)
        except NatsException as e:
            log.exception(e)
            bail_out()

    async def start(self):
        self._start_prometheus_metrics_server()

        # Setup NATS
        await self._init_nats_conn()
        await self._init_subscriptions()

    async def start_server(self):
        await self._server.run()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])


if __name__ == "__main__":
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
