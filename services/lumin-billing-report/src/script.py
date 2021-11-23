import asyncio
import base64
import logging
import pathlib

from unittest.mock import Mock

from application.actions.billing_report import BillingReport
from application.clients.lumin_client import LuminBillingClient
from application.repositories.template_renderer import TemplateRenderer
from application.repositories.lumin_repository import LuminBillingRepository
from config import config


class ScriptContainer:

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        # init clients
        self._lumin_client = LuminBillingClient(config.LUMIN_CONFIG, logger=self._logger)

        # init repositories
        self._lumin_repository = LuminBillingRepository(self._logger, self._lumin_client)
        self._template_renderer = TemplateRenderer(config.BILLING_REPORT_CONFIG)

        # init actions
        self._billing_report = BillingReport(
            lumin_repo=self._lumin_repository,
            email_client=Mock(),
            template_renderer=self._template_renderer,
            scheduler=Mock(),
            logger=self._logger,
            config=config.BILLING_REPORT_CONFIG
        )

    async def run_report(self):
        data = await self._billing_report.generate_billing_report_data()
        html, csv = data["html"], base64.b64decode(data["attachments"][0]["data"].encode()).decode()

        p = pathlib.Path("report")
        p.mkdir(exist_ok=True)

        with open("report/report.html", "w") as f:
            f.write(html)

        with open("report/report.csv", "w") as f:
            f.write(csv)


if __name__ == "__main__":
    container = ScriptContainer()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(container.run_report())
