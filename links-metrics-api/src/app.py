import asyncio
import redis
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.nats.clients import NATSClient

from application.actions.get_link_metrics import GetLinkMetrics
from application.clients.mongo_client import MyMongoClient
from application.server.api_server import APIServer
from config import config


class Container:

    def __init__(self):
        # LOGGER
        self._logger = LoggerClient(config).get_logger()
        self._logger.info(f'Links metrics API starting in: {config.ENVIRONMENT_NAME}...')

        # REDIS
        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        # CLIENTS
        self._mongo_client = MyMongoClient(logger=self._logger, config=config)

        # API
        self._api_server = APIServer(self._logger, config)

        # MESSAGES STORAGE MANAGER
        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        # EVENT BUS
        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)

        self._get_links_metrics = GetLinkMetrics(self._logger, config, self._mongo_client)

    async def _start(self):
        await self._event_bus.connect()

    async def start_server(self):
        await self._api_server.run_server()

    async def run(self):
        await self._start()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
