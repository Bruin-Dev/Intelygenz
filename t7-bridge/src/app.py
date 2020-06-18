import redis

from config import config
from application.clients.t7_client import T7Client
from application.repositories.t7_repository import T7Repository
from application.actions.get_prediction import GetPrediction
from application.actions.post_automation_metrics import PostAutomationMetrics
from igz.packages.nats.clients import NATSClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.eventbus.action import ActionWrapper

from igz.packages.Logger.logger_client import LoggerClient
import asyncio
from igz.packages.server.api import QuartServer


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("T7 bridge starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._t7_client = T7Client(self._logger, config)
        self._t7_repository = T7Repository(self._logger, self._t7_client)

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        self._publisher = NATSClient(config, logger=self._logger)
        self._subscriber_prediction = NATSClient(config, logger=self._logger)
        self._subscriber_automation_metrics = NATSClient(config, logger=self._logger)

        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.add_consumer(self._subscriber_prediction, consumer_name="prediction")
        self._event_bus.add_consumer(self._subscriber_automation_metrics, consumer_name="automation_metrics")
        self._event_bus.set_producer(self._publisher)

        self._get_prediction = GetPrediction(self._logger, config, self._event_bus,
                                             self._t7_repository)
        self._post_automation_metrics = PostAutomationMetrics(self._logger, config, self._event_bus,
                                                              self._t7_repository)

        self._action_get_prediction = ActionWrapper(self._get_prediction, "get_prediction",
                                                    is_async=True, logger=self._logger)
        self._action_automation_metrics = ActionWrapper(self._post_automation_metrics, "post_automation_metrics",
                                                        is_async=True, logger=self._logger)

        self._server = QuartServer(config)

    async def start(self):
        await self._event_bus.connect()
        await self._event_bus.subscribe_consumer(consumer_name="prediction", topic="t7.prediction.request",
                                                 action_wrapper=self._action_get_prediction,
                                                 queue="t7_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="automation_metrics", topic="t7.automation.metrics",
                                                 action_wrapper=self._action_automation_metrics,
                                                 queue="t7_bridge")

    async def start_server(self):
        await self._server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
