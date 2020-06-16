import asyncio
import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer
from application.repositories.bruin_repository import BruinRepository
from application.repositories.velocloud_repository import VelocloudRepository
from application.repositories.storage_repository import StorageRepository
from application.actions.refresh_cache import RefreshCache
from application.actions.get_customers import GetCustomers

from config import config


class Container:

    def __init__(self):
        # LOGGER
        self._logger = LoggerClient(config).get_logger()
        self._logger.info(f'Customer cache starting in {config.ENVIRONMENT_NAME}...')

        # REDIS
        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=config.SCHEDULER_CONFIG['timezone'])

        # HEALTHCHECK ENDPOINT
        self._server = QuartServer(config)

        # MESSAGES STORAGE MANAGER
        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        # EVENT BUS
        self._publisher = NATSClient(config, logger=self._logger)
        self._subscriber_get_customers = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)
        self._event_bus.add_consumer(self._subscriber_get_customers, "get_customers")

        # REPOSITORIES
        self._bruin_repository = BruinRepository(config, self._logger, self._event_bus)
        self._velocloud_repository = VelocloudRepository(config, self._logger, self._event_bus)
        self._storage_repository = StorageRepository(config, self._logger, self._redis_client)

        # ACTIONS
        self._refresh_cache = RefreshCache(config, self._event_bus, self._logger, self._scheduler,
                                           self._storage_repository, self._bruin_repository, self._velocloud_repository)
        self._get_customers = GetCustomers(config, self._logger, self._storage_repository, self._event_bus)

        # ACTION WRAPPER
        self._get_customers_w = ActionWrapper(self._get_customers, "get_customers",
                                              is_async=True, logger=self._logger)

    async def _start(self):
        await self._event_bus.connect()

        await self._event_bus.subscribe_consumer(consumer_name="get_customers", topic="customer.cache.get",
                                                 action_wrapper=self._get_customers_w,
                                                 queue="customer_cache")

        self._scheduler.start()
        await self._refresh_cache.schedule_cache_refresh()

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
