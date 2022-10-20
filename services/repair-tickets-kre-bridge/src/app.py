import logging
import sys
from dataclasses import asdict

import redis
from framework.http.server import Config as HealthConfig
from framework.http.server import Server as HealthServer
from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler
from framework.nats.client import Client
from framework.nats.exceptions import NatsException
from framework.nats.models import *
from framework.nats.temp_payload_storage import RedisLegacy as RedisStorage
from prometheus_client import start_http_server

from application.actions.get_email_inference import GetInference
from application.actions.save_closed_ticket_feedback import SaveClosedTicketFeedback
from application.actions.save_created_ticket_feedback import SaveCreatedTicketFeedback
from application.actions.save_outputs import SaveOutputs
from application.clients.repair_ticket_client import RepairTicketClient
from application.models import subscriptions
from application.repositories.repair_ticket_repository import RepairTicketRepository
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
        app_logger.info("KRE Repair Tickets bridge starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        tmp_redis_storage = RedisStorage(self._redis_client)
        self._nats_client = Client(temp_payload_storage=tmp_redis_storage)

        self._repair_ticket_client = RepairTicketClient(config)
        self._repair_ticket_repository = RepairTicketRepository(self._repair_ticket_client)

        self._server = HealthServer(HealthConfig(port=config.QUART_CONFIG["port"]))
        app_logger.info("KRE repair tickets bridge started!")

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
            cb = SaveOutputs(self._repair_ticket_repository)
            await self._nats_client.subscribe(**subscriptions.SaveOutputs(cb=cb).__dict__)

            cb = GetInference(self._repair_ticket_repository)
            await self._nats_client.subscribe(**subscriptions.GetInference(cb=cb).__dict__)

            cb = SaveCreatedTicketFeedback(self._repair_ticket_repository)
            await self._nats_client.subscribe(**subscriptions.SaveCreatedTicketFeedback(cb=cb).__dict__)

            cb = SaveClosedTicketFeedback(self._repair_ticket_repository)
            await self._nats_client.subscribe(**subscriptions.SaveClosedTicketFeedback(cb=cb).__dict__)
        except NatsException as e:
            app_logger.exception(e)
            bail_out()

    async def start(self):
        # Prometheus
        self._start_prometheus_metrics_server()

        # Setup NATS
        await self._init_nats_conn()
        await self._init_subscriptions()

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
