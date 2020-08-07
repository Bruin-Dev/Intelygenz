import asyncio
import sys
import redis
from application.actions.create_dispatch import CreateDispatch
from application.actions.get_dispatch import GetDispatch
from application.actions.update_dispatch import UpdateDispatch
from application.actions.upload_file import UploadFile
from application.clients.lit_client import LitClient
from application.repositories.lit_repository import LitRepository
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from application.actions.cancel_dispatch import CancelDispatch
from config import config


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("LIT bridge starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._scheduler = AsyncIOScheduler(timezone=config.LIT_CONFIG['timezone'])

        self._lit_client = LitClient(self._logger, config)
        self._lit_repository = LitRepository(
            self._lit_client, self._logger, self._scheduler, config, self._redis_client)

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        # NATS clients
        self._publisher = NATSClient(config, logger=self._logger)
        self._subscriber_create_dispatch = NATSClient(config, logger=self._logger)
        self._subscriber_cancel_dispatch = NATSClient(config, logger=self._logger)
        self._subscriber_get_dispatch = NATSClient(config, logger=self._logger)
        self._subscriber_update_dispatch = NATSClient(config, logger=self._logger)
        self._subscriber_upload_file = NATSClient(config, logger=self._logger)

        # event bus
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)
        self._event_bus.add_consumer(self._subscriber_create_dispatch, consumer_name="create_dispatch")
        self._event_bus.add_consumer(self._subscriber_cancel_dispatch, consumer_name="cancel_dispatch")
        self._event_bus.add_consumer(self._subscriber_get_dispatch, consumer_name="get_dispatch")
        self._event_bus.add_consumer(self._subscriber_update_dispatch, consumer_name="update_dispatch")
        self._event_bus.add_consumer(self._subscriber_upload_file, consumer_name="upload_file")

        # actions
        self._create_dispatch = CreateDispatch(self._logger, config.LIT_CONFIG, self._event_bus,
                                               self._lit_repository)
        self._cancel_dispatch = CancelDispatch(self._logger, config.LIT_CONFIG, self._event_bus,
                                               self._lit_repository)
        self._get_dispatch = GetDispatch(self._logger, config.LIT_CONFIG, self._event_bus,
                                         self._lit_repository)
        self._update_dispatch = UpdateDispatch(self._logger, config.LIT_CONFIG, self._event_bus,
                                               self._lit_repository)
        self._upload_file = UploadFile(self._logger, config.LIT_CONFIG, self._event_bus,
                                       self._lit_repository)

        # action wrappers
        self._action_create_dispatch = ActionWrapper(self._create_dispatch, "create_dispatch",
                                                     is_async=True, logger=self._logger)
        self._action_cancel_dispatch = ActionWrapper(self._cancel_dispatch, "cancel_dispatch",
                                                     is_async=True, logger=self._logger)
        self._action_get_dispatch = ActionWrapper(self._get_dispatch, "get_dispatch",
                                                  is_async=True, logger=self._logger)
        self._action_update_dispatch = ActionWrapper(self._update_dispatch, "update_dispatch",
                                                     is_async=True, logger=self._logger)
        self._action_upload_file = ActionWrapper(self._upload_file, "upload_file",
                                                 is_async=True, logger=self._logger)

        self._server = QuartServer(config)

    async def start(self):
        await self._event_bus.connect()
        self._lit_repository.login_job(exec_on_start=True)
        self._scheduler.start()

        await self._event_bus.subscribe_consumer(consumer_name="create_dispatch", topic="lit.dispatch.post",
                                                 action_wrapper=self._action_create_dispatch,
                                                 queue="lit_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="cancel_dispatch", topic="lit.dispatch.cancel",
                                                 action_wrapper=self._action_cancel_dispatch,
                                                 queue="lit_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="get_dispatch", topic="lit.dispatch.get",
                                                 action_wrapper=self._action_get_dispatch,
                                                 queue="lit_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="update_dispatch", topic="lit.dispatch.update",
                                                 action_wrapper=self._action_update_dispatch,
                                                 queue="lit_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="upload_file", topic="lit.dispatch.upload.file",
                                                 action_wrapper=self._action_upload_file,
                                                 queue="lit_bridge")

    async def start_server(self):
        await self._server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
