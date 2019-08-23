import base64
import json
from collections import OrderedDict
from datetime import datetime, timedelta
from apscheduler.util import undefined
from pytz import timezone, utc
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


class ServiceAffectingMonitor:

    def __init__(self, event_bus: EventBus, logger, scheduler, service_id, config):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._service_id = service_id
        self._config = config

    async def start_service_affecting_monitor_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: service affecting')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone('US/Eastern'))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._service_affecting_monitor_process, 'interval', seconds=60,
                                next_run_time=next_run_time, replace_existing=True,
                                id='_service_affecting_monitor_process')

    async def _service_affecting_monitor_process(self):
        edge_id = {"host": "mettel.velocloud.net", "enterprise_id": 137, "edge_id": 1602}
        edge_status_request = {'request_id': uuid(),
                               'response_topic': f'edge.status.response.{self._service_id}',
                               'edge': edge_id,
                               'interval': {"end": datetime.now(utc),
                                            "start": (datetime.now(utc) - timedelta(minutes=15))}}
        edge_status = await self._event_bus.rpc_request("edge.status.request", json.dumps(edge_status_request,
                                                                                          default=str), timeout=30)
        self._logger.info(f'Edge received from event bus')
        for link in edge_status['edge_info']['links']:
            await self._latency_check(edge_status, link)

        self._logger.info("End of service affecting monitor job")

    async def _latency_check(self, edge_status, link):
        if 'PUBLIC_WIRELESS' in link['serviceGroups']:
            if link['bestLatencyMsRx'] > 120 or link['bestLatencyMsTx'] > 120:
                await self._notify_trouble(edge_status, link, 'Latency', 120)
        elif 'PUBLIC_WIRED' in link['serviceGroups'] or 'PRIVATE_WIRED' in link['serviceGroups']:
            if link['bestLatencyMsRx'] > 50 or link['bestLatencyMsTx'] > 50:
                await self._notify_trouble(edge_status, link, 'Latency', 50)

    async def _notify_trouble(self, edge_status, link, trouble, threshold):
        # TODO remove production check here when production part gets implemented
        if self._config.MONITOR_CONFIG['environment'] == 'dev' or self._config.MONITOR_CONFIG['environment'] \
                == 'production':
            email_obj = self._compose_email_object(edge_status, link, trouble, threshold)
            await self._event_bus.rpc_request("notification.email.request", json.dumps(email_obj), timeout=10)
        # elif self._config.MONITOR_CONFIG['environment'] == 'production':
        #     TODO create repair tickets
        #     pass

    def _compose_email_object(self, edges_status_to_report, link, trouble, threshold):
        with open('src/templates/service_affecting_monitor.html') as template:
            email_html = "".join(template.readlines())
            email_html = email_html.replace('%%TROUBLE%%', trouble)
            email_html = email_html.replace('%%SERIAL_NUMBER%%',
                                            f'{edges_status_to_report["edge_info"]["edges"]["serialNumber"]}')

        edge_overview = OrderedDict()

        edge_overview["Trouble"] = trouble
        edge_overview["Threshold"] = threshold
        edge_overview['Interval for Scan'] = '15 Minutes'
        edge_overview['Scan Time'] = datetime.now(timezone('US/Eastern'))
        edge_overview["Input"] = link['bestLatencyMsRx']
        edge_overview["Output"] = link['bestLatencyMsTx']
        edge_overview["Edge URL"] = \
            f'https://{edges_status_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/'
        edge_overview["QoE URL"] = \
            f'https://{edges_status_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/qoe/'

        edge_overview["Transport URL"] = \
            f'https://{edges_status_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/links/ \n'
        rows = []
        for idx, key in enumerate(edge_overview.keys()):
            row = EVEN_ROW if idx % 2 == 0 else ODD_ROW
            row = row.replace('%%KEY%%', key)
            row = row.replace('%%VALUE%%', str(edge_overview[key]))
            rows.append(row)
        email_html = email_html.replace('%%OVERVIEW_ROWS%%', "".join(rows))

        return {
            'request_id': uuid(),
            'response_topic': f"notification.email.response.{self._service_id}",
            'email_data': {
                'subject': f'Service affecting trouble detected: {trouble}',
                'recipient': self._config.MONITOR_CONFIG["recipient"],
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
