import asyncio
from asgiref.sync import async_to_sync
from config import config
from igz.packages.nats.clients import NatsStreamingClient
from application.clients.slack_client import SlackClient
from application.repositories.slack_repository import SlackRepository
from application.actions.actions import Actions
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper


class Container:
    subscriber = None
    publisher = None
    slack_client = None
    slack_repo = None
    actions = None
    base_notification_wrapper = None
    event_bus = None

    def setup(self):
        self.subscriber = NatsStreamingClient(config, "velocloud-notificator-subscriber")
        self.publisher = NatsStreamingClient(config, "velocloud-notificator-publisher")
        self.slack_client = SlackClient(config)
        self.slack_repo = SlackRepository(config, self.slack_client)
        self.actions = Actions(config, self.slack_repo)
        self.base_notification_wrapper = ActionWrapper(self.actions, "base_notification")
        self.event_bus = EventBus()
        self.event_bus.add_consumer(consumer=self.subscriber, consumer_name="KO_subscription")
        self.event_bus.set_producer(producer=self.publisher)

    async def start(self):
        await self.event_bus.connect()
        await self.event_bus.subscribe_consumer(consumer_name="KO_subscription", topic="edge.status.ko",
                                                action_wrapper=self.base_notification_wrapper,
                                                start_at='first')

    @async_to_sync
    async def run(self):
        self.setup()
        await self.start()


if __name__ == '__main__':
    print("Velocloud notificator starting...")
    container = Container()
    container.run()
    loop = asyncio.new_event_loop()
    loop.run_forever()
