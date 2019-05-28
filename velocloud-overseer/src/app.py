from config import config
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.eventbus import EventBus
from application.actions.actions import Actions
from application.repositories.velocloud_repository import VelocloudRepository
from igz.packages.Logger.logger_client import LoggerClient
import asyncio
from igz.packages.server.api import QuartServer
from application.repositories.prometheus_repository import PrometheusRepository
from velocloud_client.client.velocloud_client import VelocloudClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc


class Container:
    velocloud_client = None
    velocloud_repository = None
    publisher = None
    event_bus = None
    prometheus_repository = None
    report_edge_action = None
    actions = None
    logger = LoggerClient(config).get_logger()
    server = QuartServer(config)
    scheduler = None

    def setup(self):
        self.scheduler = AsyncIOScheduler(timezone=utc)
        self.velocloud_client = VelocloudClient(config)
        self.velocloud_repository = VelocloudRepository(config, self.logger, self.velocloud_client)

        self.publisher = NatsStreamingClient(config, f'velocloud-overseer-publisher-', logger=self.logger)
        self.event_bus = EventBus(logger=self.logger)
        self.prometheus_repository = PrometheusRepository(config)
        self.event_bus.set_producer(self.publisher)

        self.actions = Actions(self.event_bus, self.velocloud_repository, self.logger, self.prometheus_repository,
                               self.scheduler)

    async def start(self):
        self.actions.start_prometheus_metrics_server()
        self.velocloud_repository.connect_to_all_servers()
        await self.event_bus.connect()
        await self.actions.set_edge_status_job(config.OVERSEER_CONFIG['interval_time'], exec_on_start=True)
        self.scheduler.start()

    async def start_server(self):
        await self.server.run_server()

    async def run(self):
        self.setup()
        await self.start()


if __name__ == '__main__':
    container = Container()
    container.logger.info("Velocloud overseer starting...")
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
