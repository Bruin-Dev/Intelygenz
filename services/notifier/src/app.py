import asyncio

import redis
from application.actions.get_emails import GetEmails
from application.actions.mark_email_as_read import MarkEmailAsRead
from application.actions.send_to_email import SendToEmail
from application.actions.send_to_slack import SendToSlack
from application.clients.email_client import EmailClient
from application.clients.email_reader_client import EmailReaderClient
from application.clients.slack_client import SlackClient
from application.repositories.email_reader_repository import EmailReaderRepository
from application.repositories.email_repository import EmailRepository
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
        self._logger.info("Notifier starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        self._subscriber_email_reader = NATSClient(config, logger=self._logger)
        self._subscriber_email_mark_read = NATSClient(config, logger=self._logger)
        self._subscriber_email = NATSClient(config, logger=self._logger)
        self._subscriber_slack = NATSClient(config, logger=self._logger)
        self._publisher = NATSClient(config, logger=self._logger)

        self._email_reader_client = EmailReaderClient(config, self._logger)
        self._email_reader_repo = EmailReaderRepository(config, self._email_reader_client, self._logger)

        self._email_client = EmailClient(config, self._logger)
        self._email_repo = EmailRepository(config, self._email_client, self._logger)

        self._slack_client = SlackClient(config, self._logger)
        self._slack_repo = SlackRepository(config, self._slack_client, self._logger)

        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)

        self._event_bus.add_consumer(consumer=self._subscriber_email_reader, consumer_name="email_reader_request")
        self._event_bus.add_consumer(consumer=self._subscriber_email_mark_read, consumer_name="mark_email_read_request")
        self._event_bus.add_consumer(consumer=self._subscriber_email, consumer_name="notification_email_request")
        self._event_bus.add_consumer(consumer=self._subscriber_slack, consumer_name="notification_slack_request")
        self._event_bus.set_producer(producer=self._publisher)

        self._get_emails = GetEmails(config, self._event_bus, self._logger, self._email_reader_repo)
        self._mark_email_as_read = MarkEmailAsRead(config, self._event_bus, self._logger, self._email_reader_repo)
        self._email_notification = SendToEmail(config, self._event_bus, self._logger, self._email_repo)
        self._slack_notification = SendToSlack(config, self._event_bus, self._slack_repo, self._logger)

        self._get_email_wrapper = ActionWrapper(
            self._get_emails, "get_unread_emails", is_async=True, logger=self._logger
        )
        self._mark_email_read_wrapper = ActionWrapper(
            self._mark_email_as_read, "mark_email_as_read", is_async=True, logger=self._logger
        )
        self._send_email_wrapper = ActionWrapper(
            self._email_notification, "send_to_email", is_async=True, logger=self._logger
        )
        self._send_slack_wrapper = ActionWrapper(
            self._slack_notification, "send_to_slack", is_async=True, logger=self._logger
        )
        self._server = QuartServer(config)

    async def start(self):
        self._start_prometheus_metrics_server()

        await self._event_bus.connect()

        await self._event_bus.subscribe_consumer(
            consumer_name="email_reader_request",
            topic="get.email.request",
            action_wrapper=self._get_email_wrapper,
            queue="notifier",
        )

        await self._event_bus.subscribe_consumer(
            consumer_name="mark_email_read_request",
            topic="mark.email.read.request",
            action_wrapper=self._mark_email_read_wrapper,
            queue="notifier",
        )

        await self._event_bus.subscribe_consumer(
            consumer_name="notification_email_request",
            topic="notification.email.request",
            action_wrapper=self._send_email_wrapper,
            queue="notifier",
        )

        await self._event_bus.subscribe_consumer(
            consumer_name="notification_slack_request",
            topic="notification.slack.request",
            action_wrapper=self._send_slack_wrapper,
            queue="notifier",
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
