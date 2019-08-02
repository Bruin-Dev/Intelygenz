from config import config
from application.clients.bruin_client import BruinClient
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
        self._bruin_client = BruinClient(self._logger, config.BRUIN_CONFIG)
        self._publisher = NatsStreamingClient(config, f'bruin-bridge-publisher-', logger=self._logger)

        self._event_bus = EventBus(logger=self._logger)
        self._event_bus.set_producer(self._publisher)
        self._server = QuartServer(config)

    async def start(self):
        await self._event_bus.connect()
        self._bruin_client.login()

    async def start_server(self):
        await self._server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
