import asyncio

import redis

from igz.packages.eventbus.action import ActionWrapper
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer

from application.repositories.hawkeye_repository import HawkeyeRepository
from application.clients.hawkeye_client import HawkeyeClient
from application.actions.get_probes import GetProbes

from config import config


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Hawkeye bridge starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._hawkeye_client = HawkeyeClient(self._logger, config)
        self._hawkeye_repository = HawkeyeRepository(self._logger, self._hawkeye_client, config)

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        self._publisher = NATSClient(config, logger=self._logger)

        self._subscriber_probes = NATSClient(config, logger=self._logger)

        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)

        self._event_bus.add_consumer(self._subscriber_probes, consumer_name="probes")

        self._event_bus.set_producer(self._publisher)

        self._get_probes = GetProbes(self._logger, config.HAWKEYE_CONFIG, self._event_bus, self._hawkeye_repository)

        self._report_hawkeye_probe = ActionWrapper(self._get_probes, "get_probes", is_async=True, logger=self._logger)

        self._server = QuartServer(config)

    async def start(self):
        await self._event_bus.connect()
        await self._hawkeye_client.login()
        await self._event_bus.subscribe_consumer(consumer_name="probes", topic="hawkeye.probe.request",
                                                 action_wrapper=self._report_hawkeye_probe,
                                                 queue="hawkeye_bridge")

    async def start_server(self):
        await self._server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
