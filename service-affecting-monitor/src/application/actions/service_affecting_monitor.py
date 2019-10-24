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
        edge_id = {"host": "mettel.velocloud.net", "enterprise_id": 137, "edge_id": 1651}
        edge_status_request = {'request_id': uuid(),
                               'response_topic': f'edge.status.response.{self._service_id}',
                               'edge': edge_id,
                               'interval': {"end": datetime.now(utc),
                                            "start": (datetime.now(utc) - timedelta(minutes=15))}}
        edge_status = await self._event_bus.rpc_request("edge.status.request", json.dumps(edge_status_request,
                                                                                          default=str), timeout=30)
        self._logger.info(f'Edge received from event bus')

        if edge_status and 'edge_info' not in edge_status.keys() or 'links' not in edge_status['edge_info'].keys():
            self._logger.error(f'Data received from Velocloud is incomplete')
            self._logger.error(f'{json.dumps(edge_status, indent=2)}')
            slack_message = {'request_id': uuid(),
                             'message': f'Error while monitoring edge for service affecting trouble, seems like data '
                                        f'is corrupted: \n {json.dumps(edge_status, indent=2)} \n'
                                        f'The environment is {self._config.MONITOR_CONFIG["environment"]}'}
            await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message),
                                              timeout=10)

        for link in edge_status['edge_info']['links']:
            await self._latency_check(edge_status, link)
            await self._packet_loss_check(edge_status, link)
        self._logger.info("End of service affecting monitor job")

    async def _latency_check(self, edge_status, link):
        if 'PUBLIC_WIRELESS' in link['serviceGroups']:
            if link['bestLatencyMsRx'] > 120 or link['bestLatencyMsTx'] > 120:
                await self._notify_trouble(edge_status, link, link['bestLatencyMsRx'], link['bestLatencyMsTx'],
                                           'Latency', 120)
        elif 'PUBLIC_WIRED' in link['serviceGroups'] or 'PRIVATE_WIRED' in link['serviceGroups']:
            if link['bestLatencyMsRx'] > 50 or link['bestLatencyMsTx'] > 50:
                await self._notify_trouble(edge_status, link, link['bestLatencyMsRx'], link['bestLatencyMsTx'],
                                           'Latency', 50)

    async def _packet_loss_check(self, edge_status, link):
        if 'PUBLIC_WIRELESS' in link['serviceGroups']:
            if link['bestLossPctRx'] > 8 or link['bestLossPctTx'] > 8:
                await self._notify_trouble(edge_status, link, link['bestLossPctRx'], link['bestLossPctTx'],
                                           'Packet Loss', 8)
        elif 'PUBLIC_WIRED' in link['serviceGroups'] or 'PRIVATE_WIRED' in link['serviceGroups']:
            if link['bestLossPctRx'] > 5 or link['bestLossPctTx'] > 5:
                await self._notify_trouble(edge_status, link, link['bestLossPctRx'], link['bestLossPctTx'],
                                           'Packet Loss', 5)

    async def _notify_trouble(self, edge_status, link, input, output, trouble, threshold):
        ticket_dict = self._compose_ticket_dict(edge_status, link, input, output, trouble, threshold)

        if self._config.MONITOR_CONFIG['environment'] == 'dev':
            email_obj = self._compose_email_object(edge_status, trouble, ticket_dict)
            await self._event_bus.rpc_request("notification.email.request", json.dumps(email_obj), timeout=10)
        elif self._config.MONITOR_CONFIG['environment'] == 'production':
            client_id = edge_status['edge_info']['enterprise_name'].split('|')[1]
            ticket_exists = await self._ticket_existence(client_id, edge_status['edge_info']['edges']['serialNumber'],
                                                         trouble)
            if ticket_exists is False:
                # TODO contact is hardcoded. When Mettel provides us with a service to retrieve the contact
                # TODO for each site, we should change this hardcode
                ticket_note = self._ticket_object_to_string(ticket_dict)
                ticket_details = {
                    "request_id": uuid(),
                    "response_topic": f'"bruin.ticket.creation..response.{self._service_id}',
                    "clientId": client_id,
                    "category": "VAS",
                    "services": [
                        {
                            "serviceNumber": edge_status['edge_info']['edges']['serialNumber']
                        }
                    ],
                    "notes": ticket_note,
                    "contacts": [
                        {
                            "email": "gclark@titanamerica.com",
                            "phone": "757-533-7151",
                            "name": "Gary Clark",
                            "type": "site"
                        },
                        {
                            "email": "gclark@titanamerica.com",
                            "phone": "757-342-9649",
                            "name": "Gary Clark",
                            "type": "ticket"
                        }
                    ]
                }
                ticket_id = await self._event_bus.rpc_request("bruin.ticket.creation.request",
                                                              json.dumps(ticket_details), timeout=30)

                slack_message = {'request_id': uuid(),
                                 'message': f'Ticket created with ticket id: {ticket_id["ticketIds"][0]}\n'
                                            f'https://app.bruin.com/helpdesk?clientId=85940&'
                                            f'ticketId={ticket_id["ticketIds"][0]} , in '
                                            f'{self._config.MONITOR_CONFIG["environment"]}',
                                 'response_topic': f'notification.slack.request.{self._service_id}'}
                await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message),
                                                  timeout=10)

                self._logger.info(f'Ticket created with ticket id: {ticket_id["ticketIds"][0]}')

    async def _ticket_existence(self, client_id, serial, trouble):
        ticket_request_msg = {'request_id': uuid(), 'response_topic': f'bruin.ticket.response.{self._service_id}',
                              'client_id': client_id, 'ticket_status': ['New', 'InProgress', 'Draft'],
                              'category': 'SD-WAN', 'ticket_topic': 'VAS'}
        all_tickets = await  self._event_bus.rpc_request("bruin.ticket.request",
                                                         json.dumps(ticket_request_msg, default=str),
                                                         timeout=15)
        for ticket in all_tickets['tickets']:
            ticket_detail_msg = {'request_id': uuid(),
                                 'response_topic': f'bruin.ticket.details.response.{self._service_id}',
                                 'ticket_id': ticket['ticketID']}
            ticket_details = await self._event_bus.rpc_request("bruin.ticket.details.request",
                                                               json.dumps(ticket_detail_msg, default=str),
                                                               timeout=15)
            for ticket_detail in ticket_details['ticket_details']['ticketDetails']:
                if 'detailValue' in ticket_detail.keys():
                    if ticket_detail['detailValue'] == serial:
                        for ticket_note in (ticket_details['ticket_details']['ticketNotes']):
                            if ticket_note['noteValue'] is not None:
                                if trouble in ticket_note['noteValue']:
                                    return True
        return False

    def _compose_ticket_dict(self, edges_status_to_report, link, input, output, trouble, threshold):
        edge_overview = OrderedDict()
        edge_overview["Edge Name"] = edges_status_to_report["edge_info"]["edges"]["name"]
        edge_overview["Trouble"] = trouble
        edge_overview["Interface"] = link['link']['interface']
        edge_overview["Name"] = link['link']['displayName']
        edge_overview["Threshold"] = threshold
        edge_overview['Interval for Scan'] = '15 Minutes'
        edge_overview['Scan Time'] = datetime.now(timezone('US/Eastern'))
        edge_overview["Input"] = input
        edge_overview["Output"] = output
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

        return edge_overview

    def _compose_email_object(self, edges_status_to_report, trouble, ticket_dict):
        with open('src/templates/service_affecting_monitor.html') as template:
            email_html = "".join(template.readlines())
            email_html = email_html.replace('%%TROUBLE%%', trouble)
            email_html = email_html.replace('%%SERIAL_NUMBER%%',
                                            f'{edges_status_to_report["edge_info"]["edges"]["serialNumber"]}')

        rows = []
        for idx, key in enumerate(ticket_dict.keys()):
            row = EVEN_ROW if idx % 2 == 0 else ODD_ROW
            row = row.replace('%%KEY%%', key)
            row = row.replace('%%VALUE%%', str(ticket_dict[key]))
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

    def _ticket_object_to_string(self, ticket_dict):
        edge_triage_str = "#*Automation Engine*# \n"
        for key in ticket_dict.keys():
            parsed_key = re.sub(r" LABELMARK(.)*", "", key)
            edge_triage_str = edge_triage_str + f'{parsed_key}: {ticket_dict[key]} \n'
        return edge_triage_str
