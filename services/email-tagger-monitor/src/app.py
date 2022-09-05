import asyncio
import logging
from dataclasses import asdict

import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Stdout as StdoutHandler
from framework.nats.client import Client
from framework.nats.models import Connection
from framework.nats.temp_payload_storage import RedisLegacy as RedisStorage
from prometheus_client import start_http_server
from pytz import timezone

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
from application.server.api_server import APIServer
from config import config
from framework.storage.model import RepairParentEmailStorage

log = logging.getLogger("application")
log.setLevel(logging.DEBUG)
base_handler = StdoutHandler()
base_handler.setFormatter(StandardFormatter(environment_name=config.ENVIRONMENT_NAME))
log.addHandler(base_handler)


class Container:
    def __init__(self):
        log.info("Email Tagger Monitor starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()
        self._message_storage_manager = RedisStorage(self._redis_client)

        # Redis for data storage
        self._redis_cache_client = redis.Redis(host=config.REDIS_CACHE["host"], port=6379, decode_responses=True)
        self._redis_cache_client.ping()

        self._repair_parent_email_storage = RepairParentEmailStorage(self._redis_cache_client, config.ENVIRONMENT_NAME)

        self._scheduler = AsyncIOScheduler(timezone=timezone(config.TIMEZONE))

        self._event_bus = Client(temp_payload_storage=self._message_storage_manager)

        self._utils_repository = UtilsRepository()
        self._storage_repository = StorageRepository(config, self._redis_cache_client)
        self._notifications_repository = NotificationsRepository(self._event_bus)
        self._new_emails_repository = NewEmailsRepository(
            config, self._notifications_repository, self._storage_repository
        )
        self._new_tickets_repository = NewTicketsRepository(
            config, self._notifications_repository, self._storage_repository
        )
        self._email_tagger_repository = EmailTaggerRepository(self._event_bus, config, self._notifications_repository)
        self._bruin_repository = BruinRepository(self._event_bus, config, self._notifications_repository)
        self._predicted_tag_repository = PredictedTagsRepository(
            config, self._notifications_repository, self._storage_repository
        )

        self._new_emails_monitor = NewEmailsMonitor(
            self._event_bus,
            self._scheduler,
            config,
            self._predicted_tag_repository,
            self._new_emails_repository,
            self._repair_parent_email_storage,
            self._email_tagger_repository,
            self._bruin_repository,
        )

        self._new_tickets_monitor = NewTicketsMonitor(
            self._event_bus,
            self._scheduler,
            config,
            self._new_tickets_repository,
            self._email_tagger_repository,
            self._bruin_repository,
        )

        self._api_server = APIServer(
            config,
            self._new_emails_repository,
            self._new_tickets_repository,
            self._notifications_repository,
            self._utils_repository,
        )

    async def _start(self):
        self._start_prometheus_metrics_server()

        conn = Connection(servers=config.NATS_CONFIG["servers"])
        await self._event_bus.connect(**asdict(conn))

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
