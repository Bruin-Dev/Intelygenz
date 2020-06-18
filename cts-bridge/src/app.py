import asyncio
import redis
from application.actions.create_dispatch import CreateDispatch
from application.actions.get_dispatch import GetDispatch
from application.actions.update_dispatch import UpdateDispatch
from application.clients.cts_client import CtsClient
from application.repositories.cts_repository import CtsRepository
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import config


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("CTS bridge starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._scheduler = AsyncIOScheduler(timezone=config.CTS_CONFIG['timezone'])

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        # NATS clients
        self._publisher = NATSClient(config, logger=self._logger)
        self._subscriber_create_dispatch = NATSClient(config, logger=self._logger)
        self._subscriber_get_dispatch = NATSClient(config, logger=self._logger)
        self._subscriber_update_dispatch = NATSClient(config, logger=self._logger)
        self._subscriber_upload_file = NATSClient(config, logger=self._logger)

        # event bus
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)
        self._event_bus.add_consumer(self._subscriber_create_dispatch, consumer_name="create_dispatch")
        self._event_bus.add_consumer(self._subscriber_get_dispatch, consumer_name="get_dispatch")
        self._event_bus.add_consumer(self._subscriber_update_dispatch, consumer_name="update_dispatch")
        self._event_bus.add_consumer(self._subscriber_upload_file, consumer_name="upload_file")

        self._cts_client = CtsClient(self._logger, config)
        self._cts_repository = CtsRepository(self._cts_client, self._logger, self._scheduler, config)

        # actions
        self._create_dispatch = CreateDispatch(self._logger, config.CTS_CONFIG, self._event_bus, self._cts_repository)
        self._get_dispatch = GetDispatch(self._logger, config.CTS_CONFIG, self._event_bus, self._cts_repository)
        self._update_dispatch = UpdateDispatch(self._logger, config.CTS_CONFIG, self._event_bus, self._cts_repository)

        # action wrappers
        self._action_create_disptch = ActionWrapper(self._create_dispatch, "create_dispatch",
                                                    is_async=True, logger=self._logger)
        self._action_get_dispatch = ActionWrapper(self._get_dispatch, "get_dispatch",
                                                  is_async=True, logger=self._logger)
        self._action_update_dispatch = ActionWrapper(self._update_dispatch, "update_dispatch",
                                                     is_async=True, logger=self._logger)

        self._server = QuartServer(config)

    async def start(self):
        await self._event_bus.connect()
        self._cts_repository.login_job(exec_on_start=True)
        self._scheduler.start()

        await self._event_bus.subscribe_consumer(consumer_name="create_dispatch", topic="cts.dispatch.post",
                                                 action_wrapper=self._action_create_disptch,
                                                 queue="cts_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="get_dispatch", topic="cts.dispatch.get",
                                                 action_wrapper=self._action_get_dispatch,
                                                 queue="cts_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="update_dispatch", topic="cts.dispatch.update",
                                                 action_wrapper=self._action_update_dispatch,
                                                 queue="cts_bridge")

    async def start_server(self):
        await self._server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
