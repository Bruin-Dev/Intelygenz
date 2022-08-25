import logging
import sys

import redis
from application.actions.edge_events_for_alert import EventEdgesForAlert
from application.actions.enterprise_edge_list import EnterpriseEdgeList
from application.actions.enterprise_events_for_alert import EventEnterpriseForAlert
from application.actions.enterprise_name_list_response import EnterpriseNameList
from application.actions.gateway_status_metrics import GatewayStatusMetrics
from application.actions.get_edge_links_series import GetEdgeLinksSeries
from application.actions.links_configuration import LinksConfiguration
from application.actions.links_metric_info import LinksMetricInfo
from application.actions.links_with_edge_info import LinksWithEdgeInfo
from application.actions.network_enterprise_edge_list import NetworkEnterpriseEdgeList
from application.actions.network_gateway_list import NetworkGatewayList
from application.clients.velocloud_client import VelocloudClient
from application.models import subscriptions
from application.repositories.velocloud_repository import VelocloudRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from dataclasses import asdict
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
        app_logger.info("Velocloud bridge starting...")

        redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        redis_client.ping()

        tmp_redis_storage = RedisStorage(storage_client=redis_client)
        self._nats_client = Client(temp_payload_storage=tmp_redis_storage)

        self._scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

        self._velocloud_client = VelocloudClient(config, self._scheduler)
        self._velocloud_repository = VelocloudRepository(config, self._velocloud_client)

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
            # NOTE: Using dataclasses::asdict() throws a pickle error, so we need to use <dataclass>.__dict__ instead
            cb = LinksWithEdgeInfo(self._velocloud_repository)
            await self._nats_client.subscribe(**subscriptions.GetLinksWithEdgeInfo(cb=cb).__dict__)

            cb = EventEdgesForAlert(self._velocloud_repository)
            await self._nats_client.subscribe(**subscriptions.EventEdgesForAlert(cb=cb).__dict__)

            cb = EnterpriseEdgeList(self._velocloud_repository)
            await self._nats_client.subscribe(**subscriptions.EnterpriseEdgeList(cb=cb).__dict__)

            cb = EventEnterpriseForAlert(self._velocloud_repository)
            await self._nats_client.subscribe(**subscriptions.EventEnterpriseForAlert(cb=cb).__dict__)

            cb = EnterpriseNameList(self._velocloud_repository)
            await self._nats_client.subscribe(**subscriptions.EnterpriseNameList(cb=cb).__dict__)

            cb = GetEdgeLinksSeries(self._velocloud_repository)
            await self._nats_client.subscribe(**subscriptions.GetEdgeLinksSeries(cb=cb).__dict__)

            cb = LinksConfiguration(self._velocloud_repository)
            await self._nats_client.subscribe(**subscriptions.LinksConfiguration(cb=cb).__dict__)

            cb = LinksMetricInfo(self._velocloud_repository)
            await self._nats_client.subscribe(**subscriptions.LinksMetricInfo(cb=cb).__dict__)

            cb = NetworkEnterpriseEdgeList(self._velocloud_repository)
            await self._nats_client.subscribe(**subscriptions.NetworkEnterpriseEdgeList(cb=cb).__dict__)

            cb = NetworkGatewayList(self._velocloud_repository)
            await self._nats_client.subscribe(**subscriptions.NetworkGatewayList(cb=cb).__dict__)

            cb = GatewayStatusMetrics(self._velocloud_repository)
            await self._nats_client.subscribe(**subscriptions.GatewayStatusMetrics(cb=cb).__dict__)
        except NatsException as e:
            app_logger.exception(e)
            bail_out()

    async def start(self):
        # Setup VeloCloud HTTP session
        await self._velocloud_client.create_session()
        await self._velocloud_repository.connect_to_all_servers()

        # Setup NATS
        await self._init_nats_conn()
        await self._init_subscriptions()

        # Setup scheduler
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
