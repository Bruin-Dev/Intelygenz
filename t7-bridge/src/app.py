from config import config
from application.clients.t7_client import T7Client
from application.repositories.t7_repository import T7Repository
from application.actions.get_predication import GetPredication
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper

from igz.packages.Logger.logger_client import LoggerClient
import asyncio
from igz.packages.server.api import QuartServer


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Bruin bridge starting...")
        self._t7_client = T7Client(self._logger, config)
        self._t7_repository = T7Repository(self._logger, self._t7_client)
        self._publisher = NatsStreamingClient(config, f't7-bridge-publisher-', logger=self._logger)
        self._subscriber_predication = NatsStreamingClient(config, f't7-bridge-subscriber-', logger=self._logger)

        self._event_bus = EventBus(logger=self._logger)
        self._event_bus.add_consumer(self._subscriber_predication, consumer_name="predication")
        self._event_bus.set_producer(self._publisher)

        self._get_predication = GetPredication(self._logger, config.BRUIN_CONFIG, self._event_bus,
                                               self._t7_repository)

        self._action_get_predication = ActionWrapper(self._get_predication, "get_predication",
                                                     is_async=True, logger=self._logger)

        self._server = QuartServer(config)

    async def start(self):
        await self._event_bus.connect()
        await self._event_bus.subscribe_consumer(consumer_name="predication", topic="t7.predication.request",
                                                 action_wrapper=self._get_predication,
                                                 durable_name="t7_bridge",
                                                 queue="t7_bridge",
                                                 ack_wait=480)

    async def start_server(self):
        await self._server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
