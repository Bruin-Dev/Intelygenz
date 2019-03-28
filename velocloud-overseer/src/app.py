from config import config
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.eventbus import EventBus
from application.actions.actions import Actions
from application.repositories.velocloud_repository import VelocloudRepository
from igz.packages.Logger.logger_client import LoggerClient
import asyncio
from application.server.api import quart_server
from hypercorn.asyncio import serve
from hypercorn.config import Config as CornConfig


class Container:
    logger = None
    velocloud_repository = None
    publisher = None
    event_bus = None
    report_edge_action = None
    actions = None
    logger = LoggerClient(config).get_logger()
    server = quart_server

    def setup(self):
        self.velocloud_repository = VelocloudRepository(config, self.logger)

        self.publisher = NatsStreamingClient(config, "velocloud-overseer-publisher", logger=self.logger)
        self.event_bus = EventBus(logger=self.logger)
        self.event_bus.set_producer(self.publisher)

        self.actions = Actions(self.event_bus, self.velocloud_repository, self.logger)

    async def start(self):
        await self.event_bus.connect()
        await self.actions.send_edge_status_task_interval(config.OVERSEER_CONFIG['interval_time'], exec_on_start=True)

    async def start_server(self):
        corn_config = CornConfig()
        corn_config.bind = ['0.0.0.0:5000']
        await serve(self.server, corn_config)

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
