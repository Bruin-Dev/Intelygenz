from config import config
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
from application.actions.actions import Actions
from application.repositories.velocloud_repository import VelocloudRepository
from igz.packages.Logger.logger_client import LoggerClient
import asyncio
from igz.packages.server.api import QuartServer
from prometheus_client import start_http_server, Gauge


class Container:
    velocloud_repository = None
    edge_status_gauge = None
    link_status_gauge = None
    publisher = None
    subscriber = None
    event_bus = None
    actions = None
    report_edge_action = None
    logger = LoggerClient(config).get_logger()
    server = None

    def setup(self):
        self.velocloud_repository = VelocloudRepository(config, self.logger)

        self.edge_status_gauge = Gauge('edge_state', 'Edge States', ['state'])
        self.link_status_gauge = Gauge('link_state', 'Link States', ['state'])

        self.publisher = NatsStreamingClient(config, "velocloud-drone-publisher", logger=self.logger)
        self.subscriber = NatsStreamingClient(config, "velocloud-drone-subscriber", logger=self.logger)

        self.event_bus = EventBus(logger=self.logger)
        self.event_bus.add_consumer(self.subscriber, consumer_name="tasks")
        self.event_bus.set_producer(self.publisher)

        self.actions = Actions(config, self.event_bus, self.velocloud_repository, self.logger, self.edge_status_gauge,
                               self.link_status_gauge)

        self.report_edge_action = ActionWrapper(self.actions, "report_edge_status",
                                                is_async=True, logger=self.logger)
        self.server = QuartServer(config)

    async def start(self):
        start_http_server(9200)
        await self.event_bus.connect()
        await self.event_bus.subscribe_consumer(consumer_name="tasks", topic="edge.status.task",
                                                action_wrapper=self.report_edge_action, durable_name="velocloud_drones",
                                                queue="velocloud_drones")
        await self.actions.reset_counter()

    async def start_server(self):
        await self.server.run_server()

    async def run(self):
        self.setup()
        await self.start()


if __name__ == '__main__':
    container = Container()
    Container.logger.info("Velocloud drone starting...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(container.run())
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
