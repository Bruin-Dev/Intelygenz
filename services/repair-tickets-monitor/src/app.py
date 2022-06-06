import logging
import socket

import asyncio
import redis
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer
from prometheus_client import start_http_server
from pytz import timezone

from application.actions.new_closed_tickets_feedback import NewClosedTicketsFeedback
from application.actions.new_created_tickets_feedback import NewCreatedTicketsFeedback
from application.actions.repair_tickets_monitor import RepairTicketsMonitor
from application.repositories.bruin_repository import BruinRepository
from application.repositories.new_created_tickets_repository import NewCreatedTicketsRepository
from application.repositories.new_tagged_emails_repository import NewTaggedEmailsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.repair_ticket_kre_repository import RepairTicketKreRepository
from application.repositories.storage_repository import StorageRepository
from application.rpc.append_note_to_ticket_rpc import AppendNoteToTicketRpc
from application.rpc.get_asset_topics_rpc import GetAssetTopicsRpc
from application.rpc.subscribe_user_rpc import SubscribeUserRpc
from application.rpc.upsert_outage_ticket_rpc import UpsertOutageTicketRpc
from config import config
from config.configuration import config as conf
from middleware.logging import JsonFormatter, ContextFilter

json_formatter = JsonFormatter(fields={
    "timestamp": "asctime",
    "name": "name",
    "module": "module",
    "line": "lineno",
    "log_level": "levelname",
    "message": "message",
}, always_extra={
    "environment": conf.environment,
    "hostname": socket.gethostname()
})
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(json_formatter)
console_handler.addFilter(ContextFilter())

logger = logging.getLogger('middleware')
logger.addHandler(console_handler)
logger.setLevel(conf.logging.level)


class Container:

    def __init__(self):
        # LOGGER
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Repair Ticket Monitor starting...")

        # REDIS
        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()
        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        # HEALTH CHECK ENDPOINT
        self._server = QuartServer(config)

        # REDIS DATA STORAGE
        self._redis_cache_client = redis.Redis(host=config.REDIS_CACHE["host"],
                                               port=6379,
                                               decode_responses=True)
        self._redis_cache_client.ping()

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=timezone(config.TIMEZONE))

        # EVENT BUS
        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)

        # REPOSITORIES
        self._storage_repository = StorageRepository(config, self._logger, self._redis_cache_client)
        self._notifications_repository = NotificationsRepository(self._event_bus)
        self._bruin_repository = BruinRepository(self._event_bus, self._logger, config, self._notifications_repository)
        self._new_tagged_emails_repository = NewTaggedEmailsRepository(
            self._logger,
            config,
            self._storage_repository,
        )
        self._new_tickets_repository = NewCreatedTicketsRepository(
            self._logger,
            config,
            self._storage_repository,
        )
        self._repair_ticket_repository = RepairTicketKreRepository(self._event_bus, self._logger, config,
                                                                   self._notifications_repository)
        # RPCs
        append_note_to_ticket_rpc = AppendNoteToTicketRpc(
            event_bus=self._event_bus,
            logger=self._logger,
            timeout=config.MONITOR_CONFIG["nats_request_timeout"]["bruin_request_seconds"]
        )
        get_asset_topics_rpc = GetAssetTopicsRpc(
            event_bus=self._event_bus,
            logger=self._logger,
            timeout=config.MONITOR_CONFIG["nats_request_timeout"]["bruin_request_seconds"],
        )
        upsert_outage_ticket_rpc = UpsertOutageTicketRpc(
            event_bus=self._event_bus,
            logger=self._logger,
            timeout=config.MONITOR_CONFIG["nats_request_timeout"]["bruin_request_seconds"],
        )
        subscribe_user_rpc = SubscribeUserRpc(
            event_bus=self._event_bus,
            logger=self._logger,
            timeout=config.MONITOR_CONFIG["nats_request_timeout"]["bruin_request_seconds"],
        )

        # ACTIONS
        self._new_created_tickets_feedback = NewCreatedTicketsFeedback(
            self._event_bus,
            self._logger,
            self._scheduler,
            config,
            self._new_tickets_repository,
            self._repair_ticket_repository,
            self._bruin_repository
        )
        self._new_closed_tickets_feedback = NewClosedTicketsFeedback(
            self._event_bus,
            self._logger,
            self._scheduler,
            config,
            self._repair_ticket_repository,
            self._bruin_repository
        )
        self._repair_tickets_monitor = RepairTicketsMonitor(
            self._event_bus,
            self._logger,
            self._scheduler,
            config,
            self._bruin_repository,
            self._new_tagged_emails_repository,
            self._repair_ticket_repository,
            append_note_to_ticket_rpc,
            get_asset_topics_rpc,
            upsert_outage_ticket_rpc,
            subscribe_user_rpc
        )

    async def start_server(self):
        await self._server.run_server()

    async def _start(self):
        self._start_prometheus_metrics_server()

        await self._event_bus.connect()
        await self._new_created_tickets_feedback.start_created_ticket_feedback(exec_on_start=True)
        await self._new_closed_tickets_feedback.start_closed_ticket_feedback(exec_on_start=True)
        await self._repair_tickets_monitor.start_repair_tickets_monitor(exec_on_start=True)
        self._scheduler.start()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG['port'])

    async def run(self):
        await self._start()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
