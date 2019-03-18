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
from threading import Timer
from igz.packages.Logger.logger_client import LoggerClient
from application.server.api import quart_server


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
        self.server = quart_server

    async def start(self):
        await self.event_bus.connect()
        await self.event_bus.subscribe_consumer(consumer_name="KO_subscription", topic="edge.status.ko",
                                                action_wrapper=self.store_stats_wrapper,
                                                durable_name="velocloud_notificator",
                                                queue="velocloud_notificator")
        self.timer_completion()

    def start_server(self):
        self.server.run(host="0.0.0.0", debug=True)

    def timer_completion(self):
        sec_to_min = self.time / 60
        msg = self.stats_client.get_statistics(sec_to_min)
        if msg is not None:
            self.actions.send_to_slack(msg)
        self.stats_client.clear_dictionaries()
        self.logger.info("Time has passed")
        Timer(self.time, self.timer_completion).start()

    async def run(self):
        self.setup()
        await self.start()


if __name__ == '__main__':
    container = Container()
    container.logger.info("Velocloud notificator starting...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(container.run())
    container.start_server()
    loop.run_forever()
