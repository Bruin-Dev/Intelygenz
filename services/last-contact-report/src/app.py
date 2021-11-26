import asyncio
import redis
from application.actions.alert import Alert
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer
from application.repositories.template_management import TemplateRenderer
from application.repositories.velocloud_repository import VelocloudRepository
from application.repositories.notifications_repository import NotificationsRepository


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Last contact report starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._scheduler = AsyncIOScheduler(timezone=timezone('US/Eastern'))
        self._server = QuartServer(config)

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        self._publisher = NATSClient(config, logger=self._logger)
        self.subscriber_alert = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.add_consumer(self.subscriber_alert, consumer_name="sub-alert")
        self._event_bus.set_producer(self._publisher)
        self._notifications_repository = NotificationsRepository(event_bus=self._event_bus, config=config)
        self._velocloud_repository = VelocloudRepository(self._event_bus, self._logger, config,
                                                         self._notifications_repository)
        self._template_renderer = TemplateRenderer(config.ALERTS_CONFIG)

        self._alert = Alert(self._event_bus, self._scheduler, self._logger,
                            config, self._velocloud_repository, self._template_renderer, self._notifications_repository)

    async def _start(self):
        await self._event_bus.connect()

        await self._alert.start_alert_job(exec_on_start=False)
        self._scheduler.start()

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