import asyncio
import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from igz.packages.eventbus.storage_managers import RedisStorageManager
from pytz import timezone

from application.repositories.bruin_repository import BruinRepository
from application.repositories.lit_repository import LitRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.server.api_server import DispatchServer
from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.nats.clients import NATSClient


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Dispatch portal backend starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        self._client1 = NATSClient(config, logger=self._logger)
        self._client2 = NATSClient(config, logger=self._logger)

        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)

        self._event_bus.set_producer(self._client1)

        self._event_bus.add_consumer(consumer=self._client2, consumer_name="consumer2")

        self._notifications_repository = NotificationsRepository(self._event_bus)
        self._bruin_repository = BruinRepository(self._event_bus, self._logger, config, self._notifications_repository)
        self._lit_repository = LitRepository(self._logger, config, self._event_bus, self._notifications_repository,
                                             self._bruin_repository)
        self._dispatch_api_server = DispatchServer(config, self._redis_client, self._event_bus, self._logger,
                                                   self._bruin_repository, self._lit_repository,
                                                   self._notifications_repository)

    self._logger.info("Container created")

    async def start(self):
        await self._event_bus.connect()

    async def run(self):
        await self.start()

    async def start_dispatch_server(self):
        await self._dispatch_api_server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_dispatch_server(), loop=loop)
    loop.run_forever()
