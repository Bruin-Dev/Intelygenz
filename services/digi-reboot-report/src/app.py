import asyncio

import redis
from application.actions.digi_reboot_report import DiGiRebootReport
from application.repositories.bruin_repository import BruinRepository
from application.repositories.digi_repository import DiGiRepository
from application.repositories.email_repository import EmailRepository
from application.repositories.notifications_repository import NotificationsRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer
from prometheus_client import start_http_server
from pytz import timezone


class Container:
    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("DiGi reboot report starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._scheduler = AsyncIOScheduler(timezone=timezone("US/Eastern"))
        self._server = QuartServer(config)

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        self._publisher = NATSClient(config, logger=self._logger)
        self.subscriber_alert = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.add_consumer(self.subscriber_alert, consumer_name="sub-alert")
        self._event_bus.set_producer(self._publisher)
        self._notifications_repository = NotificationsRepository(event_bus=self._event_bus, config=config)
        self._email_repository = EmailRepository(event_bus=self._event_bus, config=config)
        self._bruin_repository = BruinRepository(self._event_bus, self._logger, config, self._notifications_repository)
        self._digi_repository = DiGiRepository(self._event_bus, self._logger, config, self._notifications_repository)

        self._digi_reboot_report = DiGiRebootReport(
            self._event_bus,
            self._scheduler,
            self._logger,
            config,
            self._bruin_repository,
            self._digi_repository,
            self._email_repository,
        )

    async def _start(self):
        self._start_prometheus_metrics_server()

        await self._event_bus.connect()

        await self._digi_reboot_report.start_digi_reboot_report_job(exec_on_start=True)

        self._scheduler.start()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])

    async def start_server(self):
        await self._server.run_server()

    async def run(self):
        await self._start()


if __name__ == "__main__":
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
