import asyncio
import logging
from dataclasses import asdict

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from framework.http.server import Config as HealthConfig
from framework.http.server import Server as HealthServer
from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler
from framework.nats.client import Client
from framework.nats.models import Connection
from framework.nats.temp_payload_storage import RedisLegacy as RedisStorage
from framework.storage.model import RepairParentEmailStorage
from prometheus_client import start_http_server
from pytz import timezone
from redis.client import Redis

from application.actions.new_closed_tickets_feedback import NewClosedTicketsFeedback
from application.actions.new_created_tickets_feedback import NewCreatedTicketsFeedback
from application.actions.repair_tickets_monitor import RepairTicketsMonitor
from application.actions.reprocess_old_parent_emails import ReprocessOldParentEmails
from application.repositories.bruin_repository import BruinRepository
from application.repositories.new_created_tickets_repository import NewCreatedTicketsRepository
from application.repositories.new_tagged_emails_repository import NewTaggedEmailsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.repair_ticket_kre_repository import RepairTicketKreRepository
from application.repositories.storage_repository import StorageRepository
from application.rpc.append_note_to_ticket_rpc import AppendNoteToTicketRpc
from application.rpc.get_asset_topics_rpc import GetAssetTopicsRpc
from application.rpc.send_email_reply_rpc import SendEmailReplyRpc
from application.rpc.set_email_status_rpc import SetEmailStatusRpc
from application.rpc.subscribe_user_rpc import SubscribeUserRpc
from application.rpc.upsert_outage_ticket_rpc import UpsertOutageTicketRpc
from config import config

# json_formatter = JsonFormatter(
#     fields={
#         "timestamp": "asctime",
#         "name": "name",
#         "module": "module",
#         "line": "lineno",
#         "log_level": "levelname",
#         "message": "message",
#     },
#     always_extra={"environment": conf.environment, "hostname": socket.gethostname()},
# )
# console_handler = logging.StreamHandler(sys.stdout)
# console_handler.setFormatter(json_formatter)
# console_handler.addFilter(ContextFilter())
#
# logger = logging.getLogger("middleware")
# logger.addHandler(console_handler)
# logger.setLevel(conf.logging.level)

log = logging.getLogger("application")
log.setLevel(logging.DEBUG)
base_handler = StdoutHandler()
base_handler.setFormatter(StandardFormatter(environment_name=config.ENVIRONMENT_NAME))
log.addHandler(base_handler)

if config.LOG_CONFIG["papertrail"]["active"]:
    pt_handler = PapertrailHandler(
        host=config.LOG_CONFIG["papertrail"]["host"],
        port=config.LOG_CONFIG["papertrail"]["port"],
    )
    pt_handler.setFormatter(
        PapertrailFormatter(
            environment_name=config.ENVIRONMENT_NAME,
            papertrail_prefix=config.LOG_CONFIG["papertrail"]["prefix"],
        )
    )
    log.addHandler(pt_handler)


class Container:
    def __init__(self):
        # LOGGER
        log.info("Repair Ticket Monitor starting...")

        # HEALTH CHECK ENDPOINT
        self._server = HealthServer(HealthConfig(port=config.QUART_CONFIG["port"]))

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=timezone(config.TIMEZONE))

        # EVENT BUS
        redis = Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        redis.ping()
        tmp_redis_storage = RedisStorage(storage_client=redis)
        self._nats_client = Client(temp_payload_storage=tmp_redis_storage)

        # REPOSITORIES
        redis_cache = Redis(host=config.REDIS_CACHE["host"], port=6379, decode_responses=True)
        redis_cache.ping()
        self._storage_repository = StorageRepository(config, redis_cache)
        self._notifications_repository = NotificationsRepository(self._nats_client)
        self._bruin_repository = BruinRepository(self._nats_client, config, self._notifications_repository)
        self._repair_parent_email_storage = RepairParentEmailStorage(redis_cache, config.ENVIRONMENT_NAME)
        self._new_tagged_emails_repository = NewTaggedEmailsRepository(
            config, self._storage_repository, self._repair_parent_email_storage
        )
        self._new_tickets_repository = NewCreatedTicketsRepository(config, self._storage_repository)
        self._repair_ticket_repository = RepairTicketKreRepository(
            self._nats_client, config, self._notifications_repository
        )
        # EMAIL STORAGE
        self._repair_parent_email_storage = RepairParentEmailStorage(redis_cache, config.ENVIRONMENT_NAME)
        # RPCs
        append_note_to_ticket_rpc = AppendNoteToTicketRpc(
            _nats_client=self._nats_client,
            _timeout=config.MONITOR_CONFIG["nats_request_timeout"]["bruin_request_seconds"],
        )
        get_asset_topics_rpc = GetAssetTopicsRpc(
            _nats_client=self._nats_client,
            _timeout=config.MONITOR_CONFIG["nats_request_timeout"]["bruin_request_seconds"],
        )
        upsert_outage_ticket_rpc = UpsertOutageTicketRpc(
            _nats_client=self._nats_client,
            _timeout=config.MONITOR_CONFIG["nats_request_timeout"]["bruin_request_seconds"],
        )
        subscribe_user_rpc = SubscribeUserRpc(
            _nats_client=self._nats_client,
            _timeout=config.MONITOR_CONFIG["nats_request_timeout"]["bruin_request_seconds"],
        )
        set_email_status_rpc = SetEmailStatusRpc(
            _nats_client=self._nats_client,
            _timeout=config.MONITOR_CONFIG["nats_request_timeout"]["bruin_request_seconds"],
        )
        send_email_reply_rpc = SendEmailReplyRpc(
            _nats_client=self._nats_client,
            _timeout=config.MONITOR_CONFIG["nats_request_timeout"]["bruin_request_seconds"],
        )

        # ACTIONS
        self._new_created_tickets_feedback = NewCreatedTicketsFeedback(
            self._nats_client,
            self._scheduler,
            config,
            self._new_tickets_repository,
            self._repair_ticket_repository,
            self._bruin_repository,
        )
        self._new_closed_tickets_feedback = NewClosedTicketsFeedback(
            self._nats_client,
            self._scheduler,
            config,
            self._repair_ticket_repository,
            self._bruin_repository,
        )
        self._repair_tickets_monitor = RepairTicketsMonitor(
            self._nats_client,
            self._scheduler,
            config,
            self._bruin_repository,
            self._new_tagged_emails_repository,
            self._repair_ticket_repository,
            append_note_to_ticket_rpc,
            get_asset_topics_rpc,
            upsert_outage_ticket_rpc,
            subscribe_user_rpc,
            set_email_status_rpc,
            send_email_reply_rpc,
        )
        self._reprocess_old_parent_emails = ReprocessOldParentEmails(
            self._nats_client,
            self._scheduler,
            config,
            self._repair_parent_email_storage,
            self._bruin_repository,
        )

    async def start_server(self):
        await self._server.run()

    async def _start(self):
        self._start_prometheus_metrics_server()

        conn = Connection(servers=config.NATS_CONFIG["servers"])
        await self._nats_client.connect(**asdict(conn))

        await self._new_created_tickets_feedback.start_created_ticket_feedback(exec_on_start=True)
        await self._new_closed_tickets_feedback.start_closed_ticket_feedback(exec_on_start=True)
        await self._repair_tickets_monitor.start_repair_tickets_monitor(exec_on_start=True)
        await self._reprocess_old_parent_emails.start_old_parent_email_reprocess(exec_on_start=True)
        self._scheduler.start()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])

    async def run(self):
        await self._start()


if __name__ == "__main__":
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
