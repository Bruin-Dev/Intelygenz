import asyncio
from config import config
from igz.packages.nats.clients import NatsStreamingClient
from application.clients.email_client import EmailClient
from application.clients.slack_client import SlackClient
from application.clients.statistic_client import StatisticClient
from application.repositories.email_repository import EmailRepository
from application.repositories.slack_repository import SlackRepository
from application.repositories.statistic_repository import StatisticRepository
from application.actions.actions import Actions
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.server.api import QuartServer
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc


class Container:
    subscriber = None
    publisher = None
    email_client = None
    email_repo = None
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
    scheduler = None

    def setup(self):
        self.scheduler = AsyncIOScheduler(timezone=utc)
        self.subscriber_email = NatsStreamingClient(config, f'velocloud-notificator-subscriber-', logger=self.logger)
        self.subscriber = NatsStreamingClient(config, f'velocloud-notificator-subscriber-', logger=self.logger)
        self.publisher = NatsStreamingClient(config, f'velocloud-notificator-publisher-', logger=self.logger)

        self.email_client = EmailClient(config, self.logger)
        self.email_repo = EmailRepository(config, self.email_client, self.logger)

        self.slack_client = SlackClient(config, self.logger)
        self.slack_repo = SlackRepository(config, self.slack_client, self.logger)
        self.stats_client = StatisticClient(config)
        self.stats_repo = StatisticRepository(config, self.stats_client, self.logger)

        self.event_bus = EventBus(logger=self.logger)

        self.event_bus.add_consumer(consumer=self.subscriber_email, consumer_name="notification_email_request")
        self.event_bus.add_consumer(consumer=self.subscriber, consumer_name="KO_subscription")
        self.event_bus.set_producer(producer=self.publisher)

        self.actions = Actions(config, self.event_bus, self.slack_repo, self.stats_repo, self.logger, self.email_repo,
                               scheduler=self.scheduler)

        self.send_email_wrapper = ActionWrapper(self.actions, "send_to_email_job", is_async=True, logger=self.logger)
        self.store_stats_wrapper = ActionWrapper(self.actions, "store_stats", logger=self.logger)

        self.server = QuartServer(config)

    async def start(self):
        await self.event_bus.connect()
        await self.event_bus.subscribe_consumer(consumer_name="KO_subscription", topic="edge.status.ko",
                                                action_wrapper=self.store_stats_wrapper,
                                                durable_name="velocloud_notificator",
                                                queue="velocloud_notificator")

        await self.event_bus.subscribe_consumer(consumer_name="notification_email_request",
                                                topic="notification.email.request",
                                                action_wrapper=self.send_email_wrapper,
                                                durable_name="velocloud_notificator",
                                                queue="velocloud_notificator")
        self.actions.set_stats_to_slack_job()
        self.scheduler.start()

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
