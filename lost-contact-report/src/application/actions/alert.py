import base64
import json
from datetime import datetime

import pandas as pd
from apscheduler.util import undefined
from pytz import timezone
from shortuuid import uuid

from igz.packages.eventbus.eventbus import EventBus

ODD_ROW = '<tr>' \
          '<td class="odd" bgcolor="#EDEFF0" style="background-color: #EDEFF0; color: #596872; font-weight: normal; ' \
          'font-size: 14px; line-height: 20px; padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD; ' \
          'white-space: nowrap">%%ENTERPRISE%%</td>' \
          '<td class="odd" bgcolor="#EDEFF0" style="background-color: #EDEFF0; color: #596872; font-weight: normal; ' \
          'font-size: 14px; line-height: 20px; padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD; ' \
          'white-space: nowrap">%%COUNT%%</td>' \
          ' </tr>'

EVEN_ROW = ' <tr>' \
           '<td class="even" bgcolor="#FFFFFF" style="background-color: #FFFFFF; ' \
           'color: #596872; font-weight: normal; ' \
           'font-size: 14px; line-height: 20px; padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD; ' \
           'white-space: nowrap">%%ENTERPRISE%%</td>' \
           '<td class="even" bgcolor="#FFFFFF" style="background-color: #FFFFFF; ' \
           'color: #596872; font-weight: normal; ' \
           'font-size: 14px; line-height: 20px; padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD; ' \
           'white-space: nowrap">%%COUNT%%</td>' \
           '</tr>'


class Alert:

    def __init__(self, event_bus: EventBus, scheduler, logger, config, service_id):
        self._event_bus = event_bus
        self._scheduler = scheduler
        self._logger = logger
        self._config = config
        self._service_id = service_id

    async def start_alert_job(self, exec_on_start=False):
        self._logger.info("Scheduled task: alert report process configured to run first day of each month")
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone('US/Eastern'))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._alert_process, 'interval', seconds=60, misfire_grace_time=86400,
                                replace_existing=True, next_run_time=next_run_time, id='_alert_process')

    async def _alert_process(self):
        await self._request_all_edges()

    async def _request_all_edges(self):
        self._logger.info("Requesting all edges with details for alert report")
        request = dict(request_id=uuid(), response_topic=f"alert.response.all.edges.{self._service_id}", filter=[])
        await self._event_bus.publish_message("alert.request.all.edges", json.dumps(request))

    async def receive_all_edges(self, msg):
        self._logger.info("Processing all edges with details for alert report")
        all_edges = json.loads(msg)["edges"]
        edges_to_report = []
        for edge_info in all_edges:
            raw_last_contact = edge_info["edge"]["lastContact"]
            if '0000-00-00 00:00:00' not in raw_last_contact:
                last_contact = datetime.strptime(raw_last_contact, "%Y-%m-%dT%H:%M:%S.%fZ")
                time_elapsed = datetime.now() - last_contact
                if time_elapsed.days >= 30:
                    edge_for_alert = {
                        'serial_number': edge_info["edge"]["serialNumber"],
                        'enterprise': edge_info["enterprise"],
                        'last_contact': edge_info["edge"]["lastContact"]
                    }
                    edges_to_report.append(edge_for_alert)
        email_obj = self._compose_email_object(edges_to_report)
        await self._event_bus.publish_message("notification.email.request", json.dumps(email_obj))

    def _compose_email_object(self, edges_to_report):
        with open('src/templates/lost_contact.html') as template:
            email_html = "".join(template.readlines())
            email_html = email_html.replace('%%EDGE_COUNT%%', str(len(edges_to_report)))

        enterprises = {}
        for edge in edges_to_report:
            if edge['enterprise'] not in enterprises.keys():
                enterprises[edge['enterprise']] = 0
            enterprises[edge['enterprise']] += 1

        rows = []
        for idx, enterprise in enumerate(enterprises.keys()):
            row = EVEN_ROW if idx % 2 == 0 else ODD_ROW
            row = row.replace('%%ENTERPRISE%%', enterprise)
            row = row.replace('%%COUNT%%', str(enterprises[enterprise]))
            rows.append(row)
        email_html = email_html.replace('%%ROWS%%', "".join(rows))

        edges_dataframe = pd.DataFrame(edges_to_report)
        edges_dataframe.index.name = 'idx'
        edges_dataframe.to_csv('lost_contact.csv')

        return {
            'request_id': uuid(),
            'response_topic': f"notification.email.response.{self._service_id}",
            'email_data': {
                'subject': f'Lost contact edges ({datetime.now().strftime("%Y-%m-%d")})',
                'recipient': self._config["lost_contact"]["recipient"],
                'text': 'this is the accessible text for the email',
                'html': email_html,
                'images': [
                    {
                        'name': 'logo',
                        'data': base64.b64encode(open('src/templates/images/logo.png', 'rb').read()).decode('utf-8')
                    },
                    {
                        'name': 'header',
                        'data': base64.b64encode(open('src/templates/images/header.jpg', 'rb').read()).decode('utf-8')
                    },
                ],
                'attachments': [
                    {
                        'name': 'lost_contact.csv',
                        'data': base64.b64encode(open('lost_contact.csv', 'rb').read()).decode('utf-8')
                    }
                ]
            }
        }
