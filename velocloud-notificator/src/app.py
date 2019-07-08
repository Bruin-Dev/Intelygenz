import asyncio
from config import config
from igz.packages.nats.clients import NatsStreamingClient
from application.clients.email_client import EmailClient
from application.clients.slack_client import SlackClient
from application.repositories.email_repository import EmailRepository
from application.repositories.slack_repository import SlackRepository
from application.actions.email_notifier import SendToEmail
from application.actions.slack_notifier import SendToSlack
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.server.api import QuartServer


class Container:

    def __init__(self):

        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Velocloud notificator starting...")
        self._subscriber_email = NatsStreamingClient(config, f'velocloud-notificator-mail-subscriber-',
                                                     logger=self._logger)
        self._subscriber_slack = NatsStreamingClient(config, f'velocloud-notificator-slack-subscriber-',
                                                     logger=self._logger)
        self._publisher = NatsStreamingClient(config, f'velocloud-notificator-publisher-', logger=self._logger)

        self._email_client = EmailClient(config, self._logger)
        self._email_repo = EmailRepository(config, self._email_client, self._logger)

        self._slack_client = SlackClient(config, self._logger)
        self._slack_repo = SlackRepository(config, self._slack_client, self._logger)

        self._event_bus = EventBus(logger=self._logger)

        self._event_bus.add_consumer(consumer=self._subscriber_email, consumer_name="notification_email_request")
        self._event_bus.add_consumer(consumer=self._subscriber_slack, consumer_name="notification_slack_request")
        self._event_bus.set_producer(producer=self._publisher)

        self._slack_notification = SendToSlack(config, self._event_bus, self._slack_repo, self._logger)
        self._email_notification = SendToEmail(config, self._event_bus, self._logger, self._email_repo)

        self._send_slack_wrapper = ActionWrapper(self._slack_notification, "send_to_slack", is_async=True,
                                                 logger=self._logger)
        self._send_email_wrapper = ActionWrapper(self._email_notification, "send_to_email", is_async=True,
                                                 logger=self._logger)
        self._server = QuartServer(config)

    async def start(self):
        await self._event_bus.connect()

        await self._event_bus.subscribe_consumer(consumer_name="notification_email_request",
                                                 topic="notification.email.request",
                                                 action_wrapper=self._send_email_wrapper,
                                                 durable_name="velocloud_notificator",
                                                 queue="velocloud_notificator")

        await self._event_bus.subscribe_consumer(consumer_name="notification_slack_request",
                                                 topic="notification.slack.request",
                                                 action_wrapper=self._send_slack_wrapper,
                                                 durable_name="velocloud_notificator",
                                                 queue="velocloud_notificator")

    async def start_server(self):
        await self._server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
