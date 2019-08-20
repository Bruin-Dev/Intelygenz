import base64
import json
import re
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


class ServiceOutageMonitor:

    def __init__(self, event_bus: EventBus, logger, scheduler, service_id, config):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._service_id = service_id
        self._config = config

    async def start_service_outage_monitor_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: service outage')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone('US/Eastern'))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._service_outage_monitor_process, 'interval', seconds=900,
                                next_run_time=next_run_time, replace_existing=True,
                                id='_service_outage_monitor_process')

    async def _service_outage_monitor_process(self):
        edge_list_request = {'request_id': uuid(),
                             'response_topic': f'edge.list.response.{self._service_id}',
                             'filter': []}
        edge_list = await self._event_bus.rpc_request("edge.list.request", json.dumps(edge_list_request), timeout=30)
        self._logger.info(f'Edge list received from event bus')
        self._logger.info(f'Splitting and sending edges to the event bus')
        for edge in edge_list['edges']:
            edge_status_request = {'request_id': uuid(),
                                   'response_topic': f'edge.status.response.{self._service_id}',
                                   'edge': edge}
            edge_status = await self._event_bus.rpc_request("edge.status.request", json.dumps(edge_status_request))
            self._logger.info(f'Edge received from event bus')
            if edge_status["edge_info"]["edges"]["edgeState"] == 'CONNECTED':
                self._logger.info('Edge seems OK')
            elif edge_status["edge_info"]["edges"]["edgeState"] == 'OFFLINE':
                self._logger.error('Edge seems KO, failure!')
                # TODO remove production check here when production part gets implemented
                if self._config.MONITOR_CONFIG['environment'] == 'dev' or self._config.MONITOR_CONFIG['environment'] \
                                                              == 'production':
                    events_msg = {'request_id': uuid(),
                                  'response_topic': f'alert.response.event.edge.{self._service_id}',
                                  'edge': edge_status['edge_id'],
                                  'start_date': (datetime.now(utc) - timedelta(days=7)),
                                  'end_date': datetime.now(utc)}
                    edge_events = await self._event_bus.rpc_request("alert.request.event.edge",
                                                                    json.dumps(events_msg, default=str), timeout=10)
                    email_obj = self._compose_email_object(edge_status, edge_events)
                    await self._event_bus.rpc_request("notification.email.request", json.dumps(email_obj), timeout=10)
                # elif self._config.MONITOR_CONFIG['environment'] == 'production':
                #     TODO create repair tickets
                #     pass
        # Start up the next job
        self._logger.info("End of service outage monitor job")

    def _find_recent_occurence_of_event(self, event_list, event_type, message=None):
        for event_obj in event_list:
            if event_obj['event'] == event_type:
                if message is not None:
                    if event_obj['message'] == message:
                        return event_obj['eventTime']
                else:
                    return event_obj['eventTime']
        return None

    def _compose_email_object(self, edges_status_to_report, edges_events_to_report):
        with open('src/templates/service_outage_monitor.html') as template:
            email_html = "".join(template.readlines())
            email_html = email_html.replace('%%EDGE_COUNT%%', '1')
            email_html = email_html.replace('%%SERIAL_NUMBER%%',
                                            f'{edges_status_to_report["edge_info"]["edges"]["serialNumber"]}')

        edge_overview = OrderedDict()

        edge_overview["Orchestrator instance"] = edges_status_to_report['edge_id']['host']
        edge_overview["Edge Name"] = edges_status_to_report["edge_info"]["edges"]["name"]
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
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/links/'

        edge_overview["Edge Status"] = edges_status_to_report["edge_info"]["edges"]["edgeState"]

        edge_overview["Interface LABELMARK1"] = None
        edge_overview["Label LABELMARK2"] = None
        edge_overview["Line GE1 Status"] = "Line GE1 not available"

        edge_overview["Interface LABELMARK3"] = None
        edge_overview["Label LABELMARK4"] = None
        edge_overview["Line GE2 Status"] = "Line GE2 not available"

        link_data = dict()

        link_data["GE1"] = [link for link in edges_status_to_report["edge_info"]["links"]
                            if link["link"] is not None
                            if link["link"]["interface"] == "GE1"]
        link_data["GE2"] = [link for link in edges_status_to_report["edge_info"]["links"]
                            if link["link"] is not None
                            if link["link"]["interface"] == "GE2"]
        if len(link_data["GE1"]) > 0:
            edge_overview["Interface LABELMARK1"] = link_data["GE1"][0]["link"]["interface"]
            edge_overview["Line GE1 Status"] = link_data["GE1"][0]["link"]["state"]
            edge_overview["Label LABELMARK2"] = link_data["GE1"][0]["link"]['displayName']
        if len(link_data["GE2"]) > 0:
            edge_overview["Interface LABELMARK3"] = link_data["GE2"][0]["link"]["interface"]
            edge_overview["Line GE2 Status"] = link_data["GE2"][0]["link"]["state"]
            edge_overview["Label LABELMARK4"] = link_data["GE2"][0]["link"]['displayName']

        edge_events = OrderedDict()

        edge_events["Company Events URL"] = f'https://{edges_status_to_report["edge_id"]["host"]}/#!/' \
                                            f'operator/customer/{edges_status_to_report["edge_id"]["enterprise_id"]}' \
                                            f'/monitor/events/'
        edge_events["Last Edge Online"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]["data"],
                                                                               'EDGE_UP')
        edge_events["Last Edge Offline"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                ["data"], 'EDGE_DOWN')
        edge_events["Last GE1 Line Online"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                   ["data"], 'LINK_ALIVE',
                                                                                   'Link GE1 is no longer DEAD')
        edge_events["Last GE1 Line Offline"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                    ["data"], 'LINK_DEAD',
                                                                                    'Link GE1 is now DEAD')
        edge_events["Last GE2 Line Online"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                   ["data"], 'LINK_ALIVE',
                                                                                   'Link GE2 is no longer DEAD')
        edge_events["Last GE2 Line Offline"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                    ["data"], 'LINK_DEAD',
                                                                                    'Link GE2 is now DEAD')

        rows = []
        for idx, key in enumerate(edge_overview.keys()):
            row = EVEN_ROW if idx % 2 == 0 else ODD_ROW
            parsed_key = re.sub(r" LABELMARK(.)*", "", key)
            row = row.replace('%%KEY%%', parsed_key)
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
                'subject': f'Service outage monitor ({datetime.now().strftime("%Y-%m-%d")})',
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
