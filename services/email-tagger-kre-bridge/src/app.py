import asyncio

import redis
from application.actions.get_prediction import GetPrediction
from application.actions.save_metrics import SaveMetrics
from application.clients.email_tagger_client import EmailTaggerClient
from application.repositories.email_tagger_repository import EmailTaggerRepository
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
        self._logger.info("KRE Email Tagger bridge starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._email_tagger_client = EmailTaggerClient(self._logger, config)
        self._email_tagger_repository = EmailTaggerRepository(self._logger, self._email_tagger_client)

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        self._publisher = NATSClient(config, logger=self._logger)
        self._subscriber_get_prediction = NATSClient(config, logger=self._logger)
        self._subscriber_save_metrics = NATSClient(config, logger=self._logger)

        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.add_consumer(self._subscriber_get_prediction, consumer_name="prediction")
        self._event_bus.add_consumer(self._subscriber_save_metrics, consumer_name="metrics")
        self._event_bus.set_producer(self._publisher)

        self._get_prediction = GetPrediction(
            self._logger,
            config,
            self._event_bus,
            self._email_tagger_repository,
        )

        self._save_metrics = SaveMetrics(
            self._logger,
            config,
            self._event_bus,
            self._email_tagger_repository,
        )

        self._action_get_prediction = ActionWrapper(
            self._get_prediction, "get_prediction", is_async=True, logger=self._logger
        )
        self._action_save_metrics = ActionWrapper(
            self._save_metrics, "save_metrics", is_async=True, logger=self._logger
        )

        self._server = QuartServer(config)
        self._logger.info("KRE Email Tagger bridge started!")

    async def start(self):
        self._start_prometheus_metrics_server()

        await self._event_bus.connect()

        await self._event_bus.subscribe_consumer(
            consumer_name="metrics",
            topic="email_tagger.metrics.request",
            action_wrapper=self._action_save_metrics,
            queue="email_tagger_kre_bridge",
        )

        await self._event_bus.subscribe_consumer(
            consumer_name="prediction",
            topic="email_tagger.prediction.request",
            action_wrapper=self._action_get_prediction,
            queue="email_tagger_kre_bridge",
        )

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])

    async def start_server(self):
        await self._server.run_server()


if __name__ == "__main__":
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
