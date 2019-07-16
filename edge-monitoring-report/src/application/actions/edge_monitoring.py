import base64
import json
from collections import OrderedDict
from datetime import datetime

from apscheduler.util import undefined
from pytz import timezone
from shortuuid import uuid

from igz.packages.eventbus.eventbus import EventBus

ODD_ROW = '<tr>' \
          '<td class="odd" bgcolor="#EDEFF0" style="background-color: #EDEFF0; color: #596872; font-weight: normal; ' \
          'font-size: 14px; line-height: 20px; padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD; ' \
          'white-space: nowrap">%%KEY%%</td>' \
          '<td class="odd" bgcolor="#EDEFF0" style="background-color: #EDEFF0; color: #596872; font-weight: normal; ' \
          'font-size: 14px; line-height: 20px; padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD; ' \
          'white-space: nowrap">%%VALUE%%</td>' \
          ' </tr>'

EVEN_ROW = ' <tr>' \
           '<td class="even" bgcolor="#FFFFFF" style="background-color: #FFFFFF; ' \
           'color: #596872; font-weight: normal; ' \
           'font-size: 14px; line-height: 20px; padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD; ' \
           'white-space: nowrap">%%KEY%%</td>' \
           '<td class="even" bgcolor="#FFFFFF" style="background-color: #FFFFFF; ' \
           'color: #596872; font-weight: normal; ' \
           'font-size: 14px; line-height: 20px; padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD; ' \
           'white-space: nowrap">%%VALUE%%</td>' \
           '</tr>'


class EdgeMonitoring:

    def __init__(self, event_bus: EventBus, logger, scheduler, service_id, config):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._service_id = service_id
        self._config = config

    async def start_edge_monitor_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: edge monitoring process configured to run each first hour each day')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone('US/Eastern'))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._request_edges, 'cron', hour=0, next_run_time=next_run_time,
                                replace_existing=True, id='_edge_monitoring_process')

    async def _request_edges(self):
        request_id = uuid()
        self._logger.info("Requesting edges for edge monitoring report")
        edge_id = {"host": "mettel.velocloud.net", "enterprise_id": 137, "edge_id": 1602}
        msg = dict(request_id=request_id, response_topic=f'edge.status.response.{self._service_id}', edge=edge_id)
        await self._event_bus.publish_message("edge.status.request", json.dumps(msg))

    async def receive_edge(self, msg):
        self._logger.info(f'Edge received from event bus')
        edge = json.loads(msg)
        self._logger.info(f'Edge data: {json.dumps(edge, indent=2)}')
        email_obj = self._compose_email_object(edge)
        await self._event_bus.publish_message("notification.email.request", json.dumps(email_obj))

    def _compose_email_object(self, edges_to_report):
        with open('src/templates/edge_monitoring.html') as template:
            email_html = "".join(template.readlines())
            email_html = email_html.replace('%%EDGE_COUNT%%', '1')
            email_html = email_html.replace('%%SERIAL_NUMBER%%',
                                            f'{edges_to_report["edge_info"]["edges"]["serialNumber"]}')

        edge_overview = OrderedDict()

        edge_overview["Orchestrator instance"] = edges_to_report['edge_id']['host']
        edge_overview["Device URL"] = \
            f'https://{edges_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_to_report["edge_id"]["edge_id"]}/'
        edge_overview["Edge Status"] = edges_to_report["edge_info"]["edges"]["edgeState"]

        edge_overview["Interface Line1"] = None
        edge_overview["GE1 Label"] = None
        edge_overview["Line GE1 Status"] = "Line GE1 not available"

        edge_overview["Interface Line2"] = None
        edge_overview["GE2 Label"] = None
        edge_overview["Line GE2 Status"] = "Line GE2 not available"

        link_data = dict()

        link_data["GE1"] = [link for link in edges_to_report["edge_info"]["links"]
                            if link["link"] is not None
                            if link["link"]["interface"] == "GE1"]
        link_data["GE2"] = [link for link in edges_to_report["edge_info"]["links"]
                            if link["link"] is not None
                            if link["link"]["interface"] == "GE2"]
        if len(link_data["GE1"]) > 0:
            edge_overview["Interface Line1"] = link_data["GE1"][0]["link"]["interface"]
            edge_overview["Line GE1 Status"] = link_data["GE1"][0]["link"]["state"]
            edge_overview["GE1 Label"] = link_data["GE1"][0]["link"]['displayName']
        if len(link_data["GE2"]) > 0:
            edge_overview["Interface Line2"] = link_data["GE2"][0]["link"]["interface"]
            edge_overview["Line GE2 Status"] = link_data["GE2"][0]["link"]["state"]
            edge_overview["GE2 Label"] = link_data["GE2"][0]["link"]['displayName']

        edge_events = OrderedDict()

        edge_events["Company Events URL"] = f'https://{edges_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_to_report["edge_id"]["enterprise_id"]}/monitor/events/'
        edge_events["Last Edge Online"] = ""
        edge_events["Last Edge Offline"] = ""
        edge_events["Last GE1 Line Online"] = ""
        edge_events["Last GE1 Line Offline"] = ""
        edge_events["Last GE2 Line Online"] = ""
        edge_events["Last GE2 Line Offline"] = ""

        rows = []
        for idx, key in enumerate(edge_overview.keys()):
            row = EVEN_ROW if idx % 2 == 0 else ODD_ROW
            row = row.replace('%%KEY%%', key)
            row = row.replace('%%VALUE%%', str(edge_overview[key]))
            rows.append(row)
        email_html = email_html.replace('%%OVERVIEW_ROWS%%', "".join(rows))

        rows = []
        for idx, key in enumerate(edge_events.keys()):
            row = EVEN_ROW if idx % 2 == 0 else ODD_ROW
            row = row.replace('%%KEY%%', key)
            row = row.replace('%%VALUE%%', str(edge_events[key]))
            rows.append(row)
        email_html = email_html.replace('%%EVENT_ROWS%%', "".join(rows))

        return {
            'request_id': uuid(),
            'response_topic': f"notification.email.response.{self._service_id}",
            'email_data': {
                'subject': f'Edge Monitoring ({datetime.now().strftime("%Y-%m-%d")})',
                'recipient': self._config["edge_monitoring"]["recipient"],
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
                'attachments': []
            }
        }
