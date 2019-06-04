from config import config
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
from application.actions.actions import Actions
from application.repositories.velocloud_repository import VelocloudRepository
from application.repositories.prometheus_repository import PrometheusRepository
from igz.packages.Logger.logger_client import LoggerClient
import asyncio
from igz.packages.server.api import QuartServer
from velocloud_client.client.velocloud_client import VelocloudClient


class Container:
    velocloud_client = None
    velocloud_repository = None
    prometheus_repository = None
    edge_status_gauge = None
    link_status_gauge = None
    edge_status_counter = None
    link_status_counter = None
    publisher = None
    subscriber = None
    event_bus = None
    actions = None
    report_edge_list = None
    report_edge_action = None
    logger = LoggerClient(config).get_logger()
    server = None

    def setup(self):
        self.velocloud_client = VelocloudClient(config, self.logger)
        self.velocloud_repository = VelocloudRepository(config, self.logger, self.velocloud_client)
        self.prometheus_repository = PrometheusRepository(config)

        self.publisher = NatsStreamingClient(config, f'velocloud-bridge-publisher-', logger=self.logger)
        self.subscriber = NatsStreamingClient(config, f'velocloud-bridge-subscriber-', logger=self.logger)

        self.event_bus = EventBus(logger=self.logger)
        self.event_bus.add_consumer(self.subscriber, consumer_name="list")
        self.event_bus.add_consumer(self.subscriber, consumer_name="status")
        self.event_bus.set_producer(self.publisher)

        self.actions = Actions(config, self.event_bus, self.velocloud_repository, self.logger,
                               self.prometheus_repository)
        self.report_edge_list = ActionWrapper(self.actions, "report_edge_list",
                                              is_async=True, logger=self.logger)
        self.report_edge_action = ActionWrapper(self.actions, "report_edge_status",
                                                is_async=True, logger=self.logger)
        self.server = QuartServer(config)

    async def start(self):
        self.actions.start_prometheus_metrics_server()
        self.velocloud_repository.connect_to_all_servers()
        await self.event_bus.connect()
        await self.event_bus.subscribe_consumer(consumer_name="list", topic="edge.list.request",
                                                action_wrapper=self.report_edge_list, durable_name="velocloud_bridge",
                                                queue="velocloud_bridge")
        await self.event_bus.subscribe_consumer(consumer_name="status", topic="edge.status.request",
                                                action_wrapper=self.report_edge_action, durable_name="velocloud_bridge",
                                                queue="velocloud_bridge")
        await self.actions.reset_counter()

    async def start_server(self):
        await self.server.run_server()

    async def run(self):
        self.setup()
        await self.start()


if __name__ == '__main__':
    container = Container()
    Container.logger.info("Velocloud bridge starting...")
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
