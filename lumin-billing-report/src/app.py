import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from application.actions.billing_report import BillingReport
from application.clients.email_client import EmailClient
from application.clients.lumin_client import LuminBillingClient
from application.repositories.template_renderer import TemplateRenderer
from application.repositories.lumin_repository import LuminBillingRepository
from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.server.api import QuartServer


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("FCI Lumin.AI billing report starting...")

        self._scheduler = AsyncIOScheduler(timezone=timezone('US/Eastern'))
        self._server = QuartServer(config)

        # init clients
        self._email_client = EmailClient(config.EMAIL_CONFIG, logger=self._logger)
        self._lumin_client = LuminBillingClient(config.LUMIN_CONFIG, logger=self._logger)

        # init repositories
        self._lumin_repository = LuminBillingRepository(self._logger, self._lumin_client)
        self._template_renderer = TemplateRenderer(config.BILLING_REPORT_CONFIG)

        # init actions
        self._billing_report = BillingReport(
            lumin_repo=self._lumin_repository,
            email_client=self._email_client,
            template_renderer=self._template_renderer,
            scheduler=self._scheduler,
            logger=self._logger,
            config=config.BILLING_REPORT_CONFIG
        )

    async def start(self):
        self._billing_report.start_billing_report_job(exec_on_start=False)
        self._billing_report.register_error_handler()
        self._scheduler.start()

    async def start_server(self):
        await self._server.run_server()

    async def run(self):
        await self.start()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
