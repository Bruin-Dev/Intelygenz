from config import config
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
from application.actions.actions import Actions
from application.repositories.velocloud_repository import VelocloudRepository
from igz.packages.Logger.logger_client import LoggerClient
import asyncio


class Container:
    velocloud_repository = None
    publisher = None
    subscriber = None
    event_bus = None
    actions = None
    report_edge_action = None
    logger = LoggerClient(config).get_logger()

    def setup(self):
        self.velocloud_repository = VelocloudRepository(config, self.logger)

        self.publisher = NatsStreamingClient(config, "velocloud-drone-publisher", logger=self.logger)
        self.subscriber = NatsStreamingClient(config, "velocloud-drone-subscriber", logger=self.logger)

        self.event_bus = EventBus(logger=self.logger)
        self.event_bus.add_consumer(self.subscriber, consumer_name="tasks")
        self.event_bus.set_producer(self.publisher)

        self.actions = Actions(self.event_bus, self.velocloud_repository, self.logger)
        self.report_edge_action = ActionWrapper(self.actions, "report_edge_status",
                                                is_async=True, logger=self.logger)

    async def start(self):
        await self.event_bus.connect()
        await self.event_bus.subscribe_consumer(consumer_name="tasks", topic="edge.status.task",
                                                action_wrapper=self.report_edge_action, durable_name="velocloud_drones",
                                                queue="velocloud_drones")

    async def run(self):
        self.setup()
        await self.start()


if __name__ == '__main__':
    container = Container()
    Container.logger.info("Velocloud drone starting...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(container.run())
    loop.run_forever()
