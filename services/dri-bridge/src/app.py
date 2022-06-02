import asyncio

import redis
from application.actions.get_dri_parameters import GetDRIParameters
from application.clients.dri_client import DRIClient
from application.repositories.dri_repository import DRIRepository
from application.repositories.endpoints_usage_repository import EndpointsUsageRepository
from application.repositories.storage_repository import StorageRepository
from config import config
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer
from prometheus_client import start_http_server


class Container:
    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info(f"DRI bridge starting in {config.ENVIRONMENT_NAME}...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()
        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        self._storage_repository = StorageRepository(config, self._logger, self._redis_client)

        self._endpoints_usage_repository = EndpointsUsageRepository()
        config.generate_aio_tracers(
            endpoints_usage_repository=self._endpoints_usage_repository,
        )

        self._dri_client = DRIClient(config, self._logger)
        self._dri_repository = DRIRepository(self._logger, self._storage_repository, self._dri_client)

        self._publisher = NATSClient(config, logger=self._logger)

        self._subscriber_get_dri_parameters = NATSClient(config, logger=self._logger)

        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.add_consumer(self._subscriber_get_dri_parameters, consumer_name="get_dri_parameters")

        self._event_bus.set_producer(self._publisher)

        self._get_dri_parameters = GetDRIParameters(self._logger, self._event_bus, self._dri_repository)

        self._action_get_dri_parameters = ActionWrapper(
            self._get_dri_parameters, "get_dri_parameters", is_async=True, logger=self._logger
        )
        self._server = QuartServer(config)

    async def start(self):
        self._start_prometheus_metrics_server()
        await self._event_bus.connect()
        await self._dri_client.login()
        await self._event_bus.subscribe_consumer(
            consumer_name="get_dri_parameters",
            topic="dri.parameters.request",
            action_wrapper=self._action_get_dri_parameters,
            queue="dri_bridge",
        )

    async def start_server(self):
        await self._server.run_server()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])


if __name__ == "__main__":
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
