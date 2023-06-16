import asyncio
import logging
import sys
from dataclasses import asdict

import redis
from application.actions.bandwidth_reports import BandwidthReports
from application.actions.handle_ticket_forward import HandleTicketForward
from application.actions.service_affecting_monitor import ServiceAffectingMonitor
from application.actions.service_affecting_monitor_reports import ServiceAffectingMonitorReports
from application.models import subscriptions
from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.email_repository import EmailRepository
from application.repositories.metrics_repository import MetricsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.template_repository import TemplateRepository
from application.repositories.ticket_repository import TicketRepository
from application.repositories.trouble_repository import TroubleRepository
from application.repositories.utils_repository import UtilsRepository
from application.repositories.velocloud_repository import VelocloudRepository
from application.repositories.s3_repository import S3Repository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from framework.http.server import Config as QuartConfig
from framework.http.server import Server as QuartServer
from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler
from framework.nats.client import Client
from framework.nats.exceptions import NatsException
from framework.nats.models import Connection
from framework.nats.temp_payload_storage import RedisLegacy as RedisStorage
from framework.storage.task_dispatcher_client import TaskDispatcherClient, TaskTypes
from prometheus_client import start_http_server
from pytz import timezone
import boto3

base_handler = StdoutHandler()
base_handler.setFormatter(StandardFormatter(environment_name=config.ENVIRONMENT_NAME))

app_logger = logging.getLogger("application")
app_logger.setLevel(logging.DEBUG)
app_logger.addHandler(base_handler)

framework_logger = logging.getLogger("framework")
framework_logger.setLevel(logging.DEBUG)
framework_logger.addHandler(base_handler)

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
    app_logger.addHandler(pt_handler)
    framework_logger.addHandler(pt_handler)


def bail_out():
    app_logger.critical("Stopping application...")
    sys.exit(1)


class Container:
    def __init__(self):
        # LOGGER
        app_logger.info(
            f"Service Affecting Monitor starting for host {config.VELOCLOUD_HOST} in {config.CURRENT_ENVIRONMENT}..."
        )

        # REDIS
        redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        redis_client.ping()

        tmp_redis_storage = RedisStorage(storage_client=redis_client)
        self._nats_client = Client(temp_payload_storage=tmp_redis_storage)

        self._task_dispatcher_client = TaskDispatcherClient(config, redis_client)

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=timezone(config.TIMEZONE))

        # METRICS
        self._metrics_repository = MetricsRepository(config=config)

        # REPOSITORIES
        self._utils_repository = UtilsRepository()
        self._template_repository = TemplateRepository(config=config)
        self._notifications_repository = NotificationsRepository(nats_client=self._nats_client, config=config)
        self._email_repository = EmailRepository(nats_client=self._nats_client)
        self._bruin_repository = BruinRepository(
            nats_client=self._nats_client,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._velocloud_repository = VelocloudRepository(
            nats_client=self._nats_client,
            config=config,
            utils_repository=self._utils_repository,
            notifications_repository=self._notifications_repository,
        )

        session = boto3.Session()

        self._s3_repository = S3Repository(
            s3_client=session.client('s3'),
            config=config,
        )

        self._customer_cache_repository = CustomerCacheRepository(
            nats_client=self._nats_client,
            config=config,
            notifications_repository=self._notifications_repository,
        )
        self._trouble_repository = TroubleRepository(config=config, utils_repository=self._utils_repository)
        self._ticket_repository = TicketRepository(
            config=config, trouble_repository=self._trouble_repository, utils_repository=self._utils_repository
        )

        # ACTIONS
        self._service_affecting_monitor = ServiceAffectingMonitor(
            scheduler=self._scheduler,
            task_dispatcher_client=self._task_dispatcher_client,
            config=config,
            metrics_repository=self._metrics_repository,
            bruin_repository=self._bruin_repository,
            velocloud_repository=self._velocloud_repository,
            customer_cache_repository=self._customer_cache_repository,
            notifications_repository=self._notifications_repository,
            ticket_repository=self._ticket_repository,
            trouble_repository=self._trouble_repository,
            utils_repository=self._utils_repository,
        )

        self._service_affecting_monitor_reports = ServiceAffectingMonitorReports(
            scheduler=self._scheduler,
            config=config,
            template_repository=self._template_repository,
            bruin_repository=self._bruin_repository,
            notifications_repository=self._notifications_repository,
            email_repository=self._email_repository,
            customer_cache_repository=self._customer_cache_repository,
        )

        self._bandwidth_reports = BandwidthReports(
            scheduler=self._scheduler,
            config=config,
            velocloud_repository=self._velocloud_repository,
            bruin_repository=self._bruin_repository,
            trouble_repository=self._trouble_repository,
            customer_cache_repository=self._customer_cache_repository,
            email_repository=self._email_repository,
            utils_repository=self._utils_repository,
            template_repository=self._template_repository,
            metrics_repository=self._metrics_repository,
            s3_repository=self._s3_repository,
        )
        self._server = QuartServer(QuartConfig(port=config.QUART_CONFIG["port"]))

    async def _init_subscriptions(self):
        try:
            # NOTE: Using dataclasses::asdict() throws a pickle error, so we need to use <dataclass>.__dict__ instead
            cb = HandleTicketForward(self._metrics_repository)
            await self._nats_client.subscribe(**subscriptions.HandleTicketForward(cb=cb.success).__dict__)
        except NatsException as e:
            app_logger.exception(e)
            bail_out()

    async def start(self):
        self._start_prometheus_metrics_server()

        await self._init_nats_conn()
        await self._init_subscriptions()

        # await self._service_affecting_monitor.start_service_affecting_monitor(exec_on_start=True)

        # if config.VELOCLOUD_HOST in config.MONITOR_REPORT_CONFIG["recipients_by_host_and_client_id"]:
        #     await self._service_affecting_monitor_reports.start_service_affecting_monitor_reports_job(
        #         exec_on_start=config.MONITOR_REPORT_CONFIG["exec_on_start"]
        #     )
        # else:
        #     app_logger.warning(
        #         f"Job for Reoccurring Affecting Trouble Reports will not be scheduled for {config.VELOCLOUD_HOST} "
        #         "as these reports are disabled for this host"
        #     )

        await self._bandwidth_reports.start_bandwidth_reports_job(
            exec_on_start=True  # config.BANDWIDTH_REPORT_CONFIG["exec_on_start"]
        )

        self._scheduler.start()

    async def _init_nats_conn(self):
        conn = Connection(servers=config.NATS_CONFIG["servers"])

        try:
            await self._nats_client.connect(**asdict(conn))
        except NatsException as e:
            app_logger.exception(e)
            bail_out()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])

    async def start_server(self):
        await self._server.run()


if __name__ == "__main__":
    container = Container()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(container.start())
    loop.run_until_complete(container.start_server())
    loop.run_forever()
