import asyncio
from config import config
from igz.packages.nats.clients import NatsStreamingClient
from application.clients.slack_client import SlackClient
from application.clients.statistic_client import StatisticClient
from application.repositories.slack_repository import SlackRepository
from application.repositories.statistic_repository import StatisticRepository
from application.actions.actions import Actions
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.server.api import QuartServer


class Container:

    subscriber = None
    publisher = None
    slack_client = None
    slack_repo = None
    stats_client = None
    stats_repo = None
    actions = None
    store_stats_wrapper = None
    event_bus = None
    time = config.SLACK_CONFIG['time']
    logger = LoggerClient(config).get_logger()
    server = None

    def setup(self):
        self.subscriber = NatsStreamingClient(config, "velocloud-notificator-subscriber", logger=self.logger)
        self.publisher = NatsStreamingClient(config, "velocloud-notificator-publisher", logger=self.logger)
        self.slack_client = SlackClient(config, self.logger)
        self.slack_repo = SlackRepository(config, self.slack_client, self.logger)
        self.stats_client = StatisticClient(config)
        self.stats_repo = StatisticRepository(config, self.stats_client, self.logger)
        self.actions = Actions(config, self.slack_repo, self.stats_repo, self.logger)
        self.store_stats_wrapper = ActionWrapper(self.actions, "store_stats", logger=self.logger)
        self.event_bus = EventBus(logger=self.logger)
        self.event_bus.add_consumer(consumer=self.subscriber, consumer_name="KO_subscription")
        self.event_bus.set_producer(producer=self.publisher)
        self.server = QuartServer(config)

    async def start(self):
        await self.event_bus.connect()
        await self.event_bus.subscribe_consumer(consumer_name="KO_subscription", topic="edge.status.ko",
                                                action_wrapper=self.store_stats_wrapper,
                                                durable_name="velocloud_notificator",
                                                queue="velocloud_notificator")
        await self.actions.send_stats_to_slack_interval()

    async def start_server(self):
        await self.server.run_server()

    async def run(self):
        self.setup()
        await self.start()


if __name__ == '__main__':
    container = Container()
    container.logger.info("Velocloud notificator starting...")
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
