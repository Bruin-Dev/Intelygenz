from datetime import datetime
from shortuuid import uuid

from dateutil import relativedelta
from collections import OrderedDict
from apscheduler.util import undefined
from pytz import timezone
from application import EdgeIdentifier

from igz.packages.eventbus.eventbus import EventBus


class Alert:

    def __init__(self, event_bus: EventBus, scheduler, logger, config, velocloud_repository, template_renderer,
                 notifications_repository):
        self._event_bus = event_bus
        self._scheduler = scheduler
        self._logger = logger
        self._config = config
        self._velocloud_repository = velocloud_repository
        self._notifications_repository = notifications_repository
        self._template_renderer = template_renderer

    async def start_alert_job(self, exec_on_start=False):
        self._logger.info("Scheduled task: alert report process configured to run first day of each month")
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.ALERTS_CONFIG['timezone']))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._alert_process, 'cron', day=1, misfire_grace_time=86400, replace_existing=True,
                                next_run_time=next_run_time,
                                id='_alert_process')

    async def _alert_process(self):
        self._logger.info("Requesting all edges with details for alert report")
        list_edges = await self._velocloud_repository.get_edges()
        if len(list_edges) == 0:
            return
        edges_to_report = []
        for edge in list_edges:
            edge_full_id = {
                'host': edge['host'],
                'enterprise_id': edge['enterpriseId'],
                'edge_id': edge['edgeId']
            }
            edge_identifier = EdgeIdentifier(**edge_full_id)
            raw_last_contact = edge["edgeLastContact"]

            if '0000-00-00 00:00:00' in raw_last_contact:
                self._logger.info(f'Missing last contact timestamp for edge {edge_identifier}. Skipping...')
                continue

            last_contact = datetime.strptime(raw_last_contact, "%Y-%m-%dT%H:%M:%S.%fZ")
            time_elapsed = datetime.now() - last_contact
            relative_time_elapsed = relativedelta.relativedelta(datetime.now(), last_contact)
            total_months_elapsed = relative_time_elapsed.years * 12 + relative_time_elapsed.months

            if time_elapsed.days < 30:
                self._logger.info(f'Time elapsed is less than 30 days for {edge_identifier}')
                continue

            edge_for_alert = OrderedDict()
            edge_for_alert['edge_name'] = edge['edgeName']
            edge_for_alert['enterprise'] = edge["enterpriseName"]
            edge_for_alert['serial_number'] = edge["edgeSerialNumber"]
            edge_for_alert['model number'] = edge['edgeModelNumber']
            edge_for_alert['last_contact'] = edge["edgeLastContact"]
            edge_for_alert['months in SVC'] = total_months_elapsed
            edge_for_alert['balance of the 36 months'] = 36 - total_months_elapsed
            edge_for_alert['url'] = f'https://{edge["host"]}/#!/operator/customer/' \
                                    f'{edge["enterpriseId"]}' \
                                    f'/monitor/edge/{edge["edgeId"]}/'
            edges_to_report.append(edge_for_alert)

        email_obj = self._template_renderer.compose_email_object(edges_to_report)
        await self._notifications_repository.send_email(email_obj)
        self._logger.info("Last Contact Report sent")
