import asyncio

import redis
from application.actions.new_emails_monitor import NewEmailsMonitor
from application.actions.new_tickets_monitor import NewTicketsMonitor
from application.repositories.bruin_repository import BruinRepository
from application.repositories.email_tagger_repository import EmailTaggerRepository
from application.repositories.new_emails_repository import NewEmailsRepository
from application.repositories.new_tickets_repository import NewTicketsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.predicted_tags_repository import PredictedTagsRepository
from application.repositories.storage_repository import StorageRepository
from application.repositories.utils_repository import UtilsRepository
from framework.storage.model import RepairParentEmailStorage, RepairReplyEmailStorage
from application.server.api_server import APIServer
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.nats.clients import NATSClient
from prometheus_client import start_http_server
from pytz import timezone


class Container:
    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Email Tagger Monitor starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()
        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        # Redis for data storage
        self._redis_cache_client = redis.Redis(host=config.REDIS_CACHE["host"], port=6379, decode_responses=True)
        self._redis_cache_client.ping()

        self._repair_parent_email_storage = RepairParentEmailStorage(self._redis_client, config.ENVIRONMENT_NAME)
        self._repair_reply_email_storage = RepairReplyEmailStorage(self._redis_client, config.ENVIRONMENT_NAME)

        self._scheduler = AsyncIOScheduler(timezone=timezone(config.TIMEZONE))

        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)

        self._utils_repository = UtilsRepository()
        self._storage_repository = StorageRepository(config, self._logger, self._redis_cache_client)
        self._notifications_repository = NotificationsRepository(self._event_bus)
        self._new_emails_repository = NewEmailsRepository(
            self._logger, config, self._notifications_repository, self._storage_repository
        )
        self._new_tickets_repository = NewTicketsRepository(
            self._logger, config, self._notifications_repository, self._storage_repository
        )
        self._email_tagger_repository = EmailTaggerRepository(
            self._event_bus, self._logger, config, self._notifications_repository
        )
        self._bruin_repository = BruinRepository(self._event_bus, self._logger, config, self._notifications_repository)
        self._predicted_tag_repository = PredictedTagsRepository(
            self._logger, config, self._notifications_repository, self._storage_repository
        )

        self._new_emails_monitor = NewEmailsMonitor(
            self._event_bus,
            self._logger,
            self._scheduler,
            config,
            self._predicted_tag_repository,
            self._new_emails_repository,
            self._repair_parent_email_storage,
            self._repair_reply_email_storage,
            self._email_tagger_repository,
            self._bruin_repository,
        )

        self._new_tickets_monitor = NewTicketsMonitor(
            self._event_bus,
            self._logger,
            self._scheduler,
            config,
            self._new_tickets_repository,
            self._email_tagger_repository,
            self._bruin_repository,
        )

        self._api_server = APIServer(
            self._logger,
            config,
            self._new_emails_repository,
            self._new_tickets_repository,
            self._notifications_repository,
            self._utils_repository,
        )

    async def _start(self):
        self._start_prometheus_metrics_server()

        await self._event_bus.connect()

        await self._new_emails_monitor.start_email_events_monitor(exec_on_start=True)
        await self._new_tickets_monitor.start_ticket_events_monitor(exec_on_start=True)

        self._scheduler.start()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])

    async def start_server(self):
        await self._api_server.run_server()

    async def run(self):
        await self._start()


if __name__ == "__main__":
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
