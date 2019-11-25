import base64
import json
from collections import OrderedDict
from datetime import datetime

import pandas as pd
from apscheduler.util import undefined
from dateutil import relativedelta
from pytz import timezone
from shortuuid import uuid

from igz.packages.eventbus.eventbus import EventBus


class Alert:

    def __init__(self, event_bus: EventBus, scheduler, logger, config, template_renderer):
        self._event_bus = event_bus
        self._scheduler = scheduler
        self._logger = logger
        self._config = config
        self._template_renderer = template_renderer

    async def start_alert_job(self, exec_on_start=False):
        self._logger.info("Scheduled task: alert report process configured to run first day of each month")
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone('US/Eastern'))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._alert_process, 'cron', day=1, misfire_grace_time=86400, replace_existing=True,
                                next_run_time=next_run_time,
                                id='_alert_process')

    async def _alert_process(self):
        self._logger.info("Requesting all edges with details for alert report")
        request = dict(request_id=uuid(), filter=[])
        all_edges = await self._event_bus.rpc_request("alert.request.all.edges", json.dumps(request), timeout=200)
        self._logger.info("Processing all edges with details for alert report")
        edges_to_report = []
        for edge_info in all_edges["edges"]:
            raw_last_contact = edge_info["edge"]["lastContact"]
            if '0000-00-00 00:00:00' not in raw_last_contact:
                last_contact = datetime.strptime(raw_last_contact, "%Y-%m-%dT%H:%M:%S.%fZ")
                time_elapsed = datetime.now() - last_contact
                relative_time_elapsed = relativedelta.relativedelta(datetime.now(), last_contact)
                total_months_elapsed = relative_time_elapsed.years * 12 + relative_time_elapsed.months
                if time_elapsed.days >= 30:
                    edge_for_alert = OrderedDict()
                    edge_for_alert['enterprise'] = edge_info["enterprise"]
                    edge_for_alert['serial_number'] = edge_info["edge"]["serialNumber"]
                    edge_for_alert['model number'] = edge_info["edge"]['modelNumber']
                    edge_for_alert['last_contact'] = edge_info["edge"]["lastContact"]
                    edge_for_alert['months in SVC'] = total_months_elapsed
                    edge_for_alert['balance of the 36 months'] = 36 - total_months_elapsed
                    edge_for_alert['url'] = f'https://{edge_info["edge_id"]["host"]}/#!/operator/customer/'\
                                            f'{edge_info["edge_id"]["enterprise_id"]}' \
                                            f'/monitor/edge/{edge_info["edge_id"]["edge_id"]}/'

                    edges_to_report.append(edge_for_alert)
        email_obj = self._template_renderer.compose_email_object(edges_to_report)
        await self._event_bus.publish_message("notification.email.request", json.dumps(email_obj))
