import base64
import json
import re
from collections import OrderedDict
from datetime import datetime, timedelta
from apscheduler.util import undefined
from pytz import timezone, utc
from shortuuid import uuid

from igz.packages.eventbus.eventbus import EventBus


class ServiceAffectingMonitor:

    def __init__(self, event_bus: EventBus, logger, scheduler, config, template_renderer):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._monitoring_minutes = config.MONITOR_CONFIG["monitoring_minutes"]
        self._template_renderer = template_renderer

    async def start_service_affecting_monitor_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: service affecting')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone('US/Eastern'))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._monitor_each_edge, 'interval', minutes=self._monitoring_minutes,
                                next_run_time=next_run_time, replace_existing=True,
                                id='_monitor_each_edge')

    async def _monitor_each_edge(self):
        monitored_edges = [await self._service_affecting_monitor_process(device) for device in
                           self._config.MONITOR_CONFIG['device_by_id']]

    async def _service_affecting_monitor_process(self, device):
        edge_id = {"host": device['host'], "enterprise_id": device['enterprise_id'], "edge_id": device['edge_id']}
        edge_status_request = {'request_id': uuid(),
                               'edge': edge_id,
                               'interval': {"end": datetime.now(utc),
                                            "start": (datetime.now(utc) - timedelta(minutes=self._monitoring_minutes))}}
        edge_status = await self._event_bus.rpc_request("edge.status.request", json.dumps(edge_status_request,
                                                                                          default=str), timeout=60)
        self._logger.info(f'Edge received from event bus')

        if edge_status is None or \
                ('edge_info' not in edge_status.keys() or 'links' not in edge_status['edge_info'].keys()):
            self._logger.error(f'Data received from Velocloud is incomplete')
            self._logger.error(f'{json.dumps(edge_status, indent=2)}')
            slack_message = {'request_id': uuid(),
                             'message': f'Error while monitoring edge for service affecting trouble, seems like data '
                                        f'is corrupted: \n {json.dumps(edge_status, indent=2)} \n'
                                        f'The environment is {self._config.MONITOR_CONFIG["environment"]}'}
            await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message),
                                              timeout=10)
            return

        self._logger.info(f'{edge_status}')

        for link in edge_status['edge_info']['links']:
            if 'serviceGroups' in link.keys():
                await self._latency_check(device, edge_status, link)
                await self._packet_loss_check(device, edge_status, link)
        self._logger.info("End of service affecting monitor job")

    async def _latency_check(self, device, edge_status, link):
        if 'PUBLIC_WIRELESS' in link['serviceGroups']:
            if link['bestLatencyMsRx'] > 120 or link['bestLatencyMsTx'] > 120:
                await self._notify_trouble(device, edge_status, link, link['bestLatencyMsRx'], link['bestLatencyMsTx'],
                                           'Latency', 120)
        elif 'PUBLIC_WIRED' in link['serviceGroups'] or 'PRIVATE_WIRED' in link['serviceGroups']:
            if link['bestLatencyMsRx'] > 50 or link['bestLatencyMsTx'] > 50:
                await self._notify_trouble(device, edge_status, link, link['bestLatencyMsRx'], link['bestLatencyMsTx'],
                                           'Latency', 50)

    async def _packet_loss_check(self, device, edge_status, link):
        if 'PUBLIC_WIRELESS' in link['serviceGroups']:
            if link['bestLossPctRx'] > 8 or link['bestLossPctTx'] > 8:
                await self._notify_trouble(device, edge_status, link, link['bestLossPctRx'], link['bestLossPctTx'],
                                           'Packet Loss', 8)
        elif 'PUBLIC_WIRED' in link['serviceGroups'] or 'PRIVATE_WIRED' in link['serviceGroups']:
            if link['bestLossPctRx'] > 5 or link['bestLossPctTx'] > 5:
                await self._notify_trouble(device, edge_status, link, link['bestLossPctRx'], link['bestLossPctTx'],
                                           'Packet Loss', 5)

    async def _notify_trouble(self, device, edge_status, link, input, output, trouble, threshold):
        ticket_dict = self._compose_ticket_dict(edge_status, link, input, output, trouble, threshold)

        if self._config.MONITOR_CONFIG['environment'] == 'dev':
            self._logger.info(f'Service affecting trouble {trouble} detected in edge with data {edge_status}')
        elif self._config.MONITOR_CONFIG['environment'] == 'production':
            client_id = edge_status['edge_info']['enterprise_name'].split('|')[1]
            ticket_exists = await self._ticket_existence(client_id, edge_status['edge_info']['edges']['serialNumber'],
                                                         trouble)
            if ticket_exists is False:
                # TODO contact is hardcoded. When Mettel provides us with a service to retrieve the contact change here
                ticket_note = self._ticket_object_to_string(ticket_dict)
                ticket_details = {
                    "request_id": uuid(),
                    "clientId": client_id,
                    "category": "VAS",
                    "services": [
                        {
                            "serviceNumber": device['serial']
                        }
                    ],
                    "contacts": [
                        {
                            "email": device['email'],
                            "phone": device['phone'],
                            "name": device['name'],
                            "type": "site"
                        },
                        {
                            "email": device['email'],
                            "phone": device['phone'],
                            "name": device['name'],
                            "type": "ticket"
                        }
                    ]
                }
                ticket_id = await self._event_bus.rpc_request("bruin.ticket.creation.request",
                                                              json.dumps(ticket_details), timeout=30)
                ticket_append_note_msg = {'request_id': uuid(),
                                          'ticket_id': ticket_id["ticketIds"]["ticketIds"][0],
                                          'note': ticket_note}
                await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                                  json.dumps(ticket_append_note_msg),
                                                  timeout=15)

                slack_message = {'request_id': uuid(),
                                 'message': f'Ticket created with ticket id: {ticket_id["ticketIds"]["ticketIds"][0]}\n'
                                            f'https://app.bruin.com/helpdesk?clientId={client_id}&'
                                            f'ticketId={ticket_id["ticketIds"]["ticketIds"][0]} , in '
                                            f'{self._config.MONITOR_CONFIG["environment"]}'}
                await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message),
                                                  timeout=10)

                self._logger.info(f'Ticket created with ticket id: {ticket_id["ticketIds"]["ticketIds"][0]}')

    async def _ticket_existence(self, client_id, serial, trouble):
        ticket_request_msg = {'request_id': uuid(), 'client_id': client_id,
                              'ticket_status': ['New', 'InProgress', 'Draft'],
                              'category': 'SD-WAN', 'ticket_topic': 'VAS'}
        all_tickets = await self._event_bus.rpc_request("bruin.ticket.request",
                                                        json.dumps(ticket_request_msg, default=str),
                                                        timeout=15)
        for ticket in all_tickets['tickets']:
            ticket_detail_msg = {'request_id': uuid(),
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
        edge_overview['Interval for Scan'] = f'{self._monitoring_minutes} Minutes'
        edge_overview['Scan Time'] = datetime.now(timezone('US/Eastern'))
        edge_overview["Input"] = input
        edge_overview["Output"] = output
        edge_overview["Links"] = \
            f'[Edge|https://{edges_status_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/] - ' \
            f'[QoE|https://{edges_status_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/qoe/] - ' \
            f'[Transport|https://{edges_status_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/links/] \n'

        return edge_overview

    def _ticket_object_to_string(self, ticket_dict):
        edge_triage_str = "#*Automation Engine*# \n"
        for key in ticket_dict.keys():
            parsed_key = re.sub(r" LABELMARK(.)*", "", key)
            edge_triage_str = edge_triage_str + f'{parsed_key}: {ticket_dict[key]} \n'
        return edge_triage_str
