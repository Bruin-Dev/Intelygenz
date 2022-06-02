import asyncio

import redis
from application.actions.digi_reboot import DiGiReboot
from application.actions.get_digi_recovery_logs import DiGiRecoveryLogs
from application.clients.digi_client import DiGiClient
from application.repositories.digi_repository import DiGiRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
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
        self._logger.info("DiGi bridge starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

        self._digi_client = DiGiClient(config, self._logger)
        self._digi_repository = DiGiRepository(config, self._logger, self._scheduler, self._digi_client)

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        # NATS client
        self._publisher = NATSClient(config, logger=self._logger)
        self._subscriber_digi_reboot = NATSClient(config, logger=self._logger)
        self._subscriber_digi_recovery_logs = NATSClient(config, logger=self._logger)

        # event bus
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)
        self._event_bus.add_consumer(self._subscriber_digi_reboot, consumer_name="digi_reboot")
        self._event_bus.add_consumer(self._subscriber_digi_recovery_logs, consumer_name="digi_recovery_logs")

        # actions
        self._digi_reboot = DiGiReboot(self._logger, self._event_bus, self._digi_repository)
        self._digi_recovery_logs = DiGiRecoveryLogs(self._logger, self._event_bus, self._digi_repository)

        # action wrappers
        self._action_digi_reboot = ActionWrapper(self._digi_reboot, "digi_reboot", is_async=True, logger=self._logger)
        self._action_digi_recovery_logs = ActionWrapper(
            self._digi_recovery_logs, "get_digi_recovery_logs", is_async=True, logger=self._logger
        )
        self._server = QuartServer(config)

    async def start(self):
        self._start_prometheus_metrics_server()

        await self._event_bus.connect()
        await self._digi_repository.login_job(exec_on_start=True)
        self._scheduler.start()

        await self._event_bus.subscribe_consumer(
            consumer_name="digi_reboot",
            topic="digi.reboot",
            action_wrapper=self._action_digi_reboot,
            queue="digi_bridge",
        )
        await self._event_bus.subscribe_consumer(
            consumer_name="digi_recovery_logs",
            topic="get.digi.recovery.logs",
            action_wrapper=self._action_digi_recovery_logs,
            queue="digi_bridge",
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
