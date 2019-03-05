import asyncio
from asgiref.sync import async_to_sync
from config import config
from igz.packages.nats.clients import NatsStreamingClient
from application.clients.slack_client import SlackClient
from application.repositories.slack_repository import SlackRepository
from application.actions.actions import Actions


class Container:
    nats_client = None
    slack_client = None
    slack_repo = None
    actions = None

    def setup(self):
        self.nats_client = NatsStreamingClient(config, "velocloud-notificator-subscriber")
        self.slack_client = SlackClient(config)
        self.slack_repo = SlackRepository(config, self.slack_client)
        self.actions = Actions(config, self.slack_repo)

    async def start(self):
        await self.nats_client.connect_to_nats()
        await self.nats_client.subscribe(topic="edge.status.ko", callback=Actions.base_notification,
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
