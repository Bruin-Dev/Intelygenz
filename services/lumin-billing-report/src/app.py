import asyncio
import logging
import sys

from application.actions.billing_report import BillingReport
from application.clients.email_client import EmailClient
from application.clients.lumin_client import LuminBillingClient
from application.repositories.lumin_repository import LuminBillingRepository
from application.repositories.template_renderer import TemplateRenderer
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from framework.http.server import Config as HealthConfig
from framework.http.server import Server as HealthServer
from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler
from prometheus_client import start_http_server
from pytz import timezone

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
        app_logger.info("FCI Lumin.AI billing report starting...")

        self._scheduler = AsyncIOScheduler(timezone=timezone("US/Eastern"))

        # init clients
        self._email_client = EmailClient(config)
        self._lumin_client = LuminBillingClient(config.LUMIN_CONFIG)

        # init repositories
        self._lumin_repository = LuminBillingRepository(self._lumin_client)
        self._template_renderer = TemplateRenderer(config.BILLING_REPORT_CONFIG)

        # init actions
        self._billing_report = BillingReport(
            lumin_repo=self._lumin_repository,
            email_client=self._email_client,
            template_renderer=self._template_renderer,
            scheduler=self._scheduler,
            config=config.BILLING_REPORT_CONFIG,
        )

        self._server = HealthServer(HealthConfig(port=config.QUART_CONFIG["port"]))

    async def start(self):
        self._start_prometheus_metrics_server()
        self._billing_report.start_billing_report_job(exec_on_start=False)
        self._billing_report.register_error_handler()
        self._scheduler.start()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])

    async def start_server(self):
        await self._server.run()

    async def run(self):
        await self.start()


if __name__ == "__main__":
    container = Container()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(container.start())
    loop.run_until_complete(container.start_server())
    loop.run_forever()
