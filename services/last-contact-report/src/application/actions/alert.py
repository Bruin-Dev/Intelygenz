import logging
from collections import OrderedDict
from datetime import datetime

from apscheduler.util import undefined
from dateutil import relativedelta
from pytz import timezone

logger = logging.getLogger(__name__)


class Alert:
    def __init__(
        self,
        scheduler,
        config,
        velocloud_repository,
        template_renderer,
        email_repository,
    ):
        self._scheduler = scheduler
        self._config = config
        self._velocloud_repository = velocloud_repository
        self._email_repository = email_repository
        self._template_renderer = template_renderer

    async def start_alert_job(self, exec_on_start=False):
        logger.info("Scheduled task: alert report process configured to run first day of each month")
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.TIMEZONE))
            logger.info(f"It will be executed now")
        self._scheduler.add_job(
            self._alert_process,
            "cron",
            day=1,
            misfire_grace_time=86400,
            replace_existing=True,
            next_run_time=next_run_time,
            id="_alert_process",
        )

    async def _alert_process(self):
        logger.info("Requesting all edges with details for alert report")
        list_edges = await self._velocloud_repository.get_edges()
        if len(list_edges) == 0:
            return
        edges_to_report = []
        for edge in list_edges:
            serial_number = edge["edgeSerialNumber"]
            raw_last_contact = edge["edgeLastContact"]
            last_contact = datetime.strptime(raw_last_contact, "%Y-%m-%dT%H:%M:%S.%fZ")
            time_elapsed = datetime.now() - last_contact
            relative_time_elapsed = relativedelta.relativedelta(datetime.now(), last_contact)
            total_months_elapsed = relative_time_elapsed.years * 12 + relative_time_elapsed.months

            if time_elapsed.days < 30:
                logger.info(f"Time elapsed is less than 30 days for {serial_number}")
                continue

            edge_for_alert = OrderedDict()
            edge_for_alert["edge_name"] = edge["edgeName"]
            edge_for_alert["enterprise"] = edge["enterpriseName"]
            edge_for_alert["serial_number"] = serial_number
            edge_for_alert["model number"] = edge["edgeModelNumber"]
            edge_for_alert["last_contact"] = edge["edgeLastContact"]
            edge_for_alert["months in SVC"] = total_months_elapsed
            edge_for_alert["balance of the 36 months"] = 36 - total_months_elapsed
            edge_for_alert["url"] = (
                f'https://{edge["host"]}/#!/operator/customer/'
                f'{edge["enterpriseId"]}'
                f'/monitor/edge/{edge["edgeId"]}/'
            )
            edges_to_report.append(edge_for_alert)

        email_obj = self._template_renderer.compose_email_object(edges_to_report)
        await self._email_repository.send_email(email_obj)
        logger.info("Last Contact Report sent")
