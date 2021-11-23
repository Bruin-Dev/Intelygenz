import asyncio
import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer

from application.actions.store_links_metrics import StoreLinkMetrics
from application.clients.mongo_client import MyMongoClient
from config import config


class Container:

    def __init__(self):
        # LOGGER
        self._logger = LoggerClient(config).get_logger()
        self._logger.info(f'Links metrics collector starting in: {config.CURRENT_ENVIRONMENT}...')

        # REDIS
        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        # CLIENTS
        self._mongo_client = MyMongoClient(logger=self._logger, config=config)

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=config.SCHEDULER_TIMEZONE)

        # HEALTHCHECK ENDPOINT
        self._server = QuartServer(config)

        # MESSAGES STORAGE MANAGER
        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        # EVENT BUS
        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)

        # # ACTIONS
        self._links_metrics_collector = StoreLinkMetrics(self._logger, config, self._event_bus, self._mongo_client,
                                                         self._scheduler)

    async def _start(self):
        await self._event_bus.connect()
        await self._links_metrics_collector.start_links_metrics_collector()
        self._scheduler.start()

    async def start_server(self):
        await self._server.run_server()

    async def run(self):
        await self._start()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
