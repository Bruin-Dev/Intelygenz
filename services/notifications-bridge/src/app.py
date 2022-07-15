import asyncio

import redis
from application.actions.send_to_slack import SendToSlack
from application.clients.slack_client import SlackClient
from application.repositories.slack_repository import SlackRepository
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
        self._logger.info("Notifications bridge starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        self._subscriber_slack = NATSClient(config, logger=self._logger)
        self._publisher = NATSClient(config, logger=self._logger)

        self._slack_client = SlackClient(config.SLACK_CONFIG, self._logger)
        self._slack_repo = SlackRepository(config, self._slack_client, self._logger)

        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)

        self._event_bus.add_consumer(consumer=self._subscriber_slack, consumer_name="notification_slack_request")
        self._event_bus.set_producer(producer=self._publisher)

        self._slack_notification = SendToSlack(config, self._event_bus, self._slack_repo, self._logger)

        self._send_slack_wrapper = ActionWrapper(
            self._slack_notification, "send_to_slack", is_async=True, logger=self._logger
        )
        self._server = QuartServer(config)

    async def start(self):
        self._start_prometheus_metrics_server()

        await self._event_bus.connect()

        await self._event_bus.subscribe_consumer(
            consumer_name="notification_slack_request",
            topic="notification.slack.request",
            action_wrapper=self._send_slack_wrapper,
            queue="notifications_bridge",
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
