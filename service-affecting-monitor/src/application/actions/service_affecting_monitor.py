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
            next_run_time = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._monitor_each_edge, 'interval', minutes=self._monitoring_minutes,
                                next_run_time=next_run_time, replace_existing=True,
                                id='_monitor_each_edge')

    async def _monitor_each_edge(self):
        monitored_edges = [await self._service_affecting_monitor_process(device) for device in
                           self._config.MONITOR_CONFIG['device_by_id']]

    async def _service_affecting_monitor_process(self, device):
        edge_id = {"host": device['host'], "enterprise_id": device['enterprise_id'], "edge_id": device['edge_id']}
        interval = {
            "end": datetime.now(utc),
            "start": (datetime.now(utc) - timedelta(minutes=self._monitoring_minutes))}
        edge_status_request = {'request_id': uuid(),
                               'body': {**edge_id, "interval": interval}
                               }
        edge_status = await self._event_bus.rpc_request("edge.status.request", edge_status_request, timeout=60)
        self._logger.info(f'Edge received from event bus')

        if edge_status is None or \
                ('edge_info' not in edge_status.keys() or 'links' not in edge_status['edge_info'].keys()):
            self._logger.error(f'Data received from Velocloud is incomplete')
            self._logger.error(f'{json.dumps(edge_status, indent=2)}')
            slack_message = {'request_id': uuid(),
                             'message': f'Error while monitoring edge for service affecting trouble, seems like data '
                                        f'is corrupted: \n {json.dumps(edge_status, indent=2)} \n'
                                        f'The environment is {self._config.MONITOR_CONFIG["environment"]}'}
            await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
            return

        self._logger.info(f'{edge_status}')

        for link in edge_status['edge_info']['links']:
            if 'serviceGroups' in link.keys():
                await self._latency_check(device, edge_status, link)
                await self._packet_loss_check(device, edge_status, link)
                await self._jitter_check(device, edge_status, link)
        self._logger.info("End of service affecting monitor job")

    async def _latency_check(self, device, edge_status, link):
        if 'PUBLIC_WIRELESS' in link['serviceGroups']:
            if link['bestLatencyMsRx'] > self._config.MONITOR_CONFIG["latency_wireless"] or \
               link['bestLatencyMsTx'] > self._config.MONITOR_CONFIG["latency_wireless"]:
                await self._notify_trouble(device, edge_status, link, link['bestLatencyMsRx'], link['bestLatencyMsTx'],
                                           'Latency', self._config.MONITOR_CONFIG["latency_wireless"])
        elif 'PUBLIC_WIRED' in link['serviceGroups'] or 'PRIVATE_WIRED' in link['serviceGroups']:
            if link['bestLatencyMsRx'] > self._config.MONITOR_CONFIG["latency_wired"] or \
               link['bestLatencyMsTx'] > self._config.MONITOR_CONFIG["latency_wired"]:
                await self._notify_trouble(device, edge_status, link, link['bestLatencyMsRx'], link['bestLatencyMsTx'],
                                           'Latency', self._config.MONITOR_CONFIG["latency_wired"])

    async def _packet_loss_check(self, device, edge_status, link):
        if 'PUBLIC_WIRELESS' in link['serviceGroups']:
            if link['bestLossPctRx'] > self._config.MONITOR_CONFIG["packet_loss_wireless"] or \
               link['bestLossPctTx'] > self._config.MONITOR_CONFIG["packet_loss_wireless"]:
                await self._notify_trouble(device, edge_status, link, link['bestLossPctRx'], link['bestLossPctTx'],
                                           'Packet Loss', self._config.MONITOR_CONFIG["packet_loss_wireless"])
        elif 'PUBLIC_WIRED' in link['serviceGroups'] or 'PRIVATE_WIRED' in link['serviceGroups']:
            if link['bestLossPctRx'] > self._config.MONITOR_CONFIG["packet_loss_wired"] or \
               link['bestLossPctTx'] > self._config.MONITOR_CONFIG["packet_loss_wired"]:
                await self._notify_trouble(device, edge_status, link, link['bestLossPctRx'], link['bestLossPctTx'],
                                           'Packet Loss', self._config.MONITOR_CONFIG["packet_loss_wired"])

    async def _jitter_check(self, device, edge_status, link):
        if link['bestJitterMsRx'] > self._config.MONITOR_CONFIG["jitter"] or \
           link['bestJitterMsTx'] > self._config.MONITOR_CONFIG["jitter"]:
            await self._notify_trouble(device, edge_status, link, link['bestJitterMsRx'], link['bestJitterMsTx'],
                                       'Jitter', 30)

    async def _notify_trouble(self, device, edge_status, link, input, output, trouble, threshold):
        ticket_dict = self._compose_ticket_dict(edge_status, link, input, output, trouble, threshold)
        self._logger.info(f'Service affecting trouble {trouble} detected in edge with data {edge_status}')

        if self._config.MONITOR_CONFIG['environment'] == 'production':
            client_id = edge_status['edge_info']['enterprise_name'].split('|')[1]
            ticket_exists = await self._ticket_existence(client_id, edge_status['edge_info']['edges']['serialNumber'],
                                                         trouble)
            if ticket_exists is False:
                # TODO contact is hardcoded. When Mettel provides us with a service to retrieve the contact change here
                ticket_note = self._ticket_object_to_string(ticket_dict)
                ticket_details = {
                    "request_id": uuid(),
                    "payload": {
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
                }
                ticket_id = await self._event_bus.rpc_request("bruin.ticket.creation.request",
                                                              ticket_details, timeout=30)
                ticket_append_note_msg = {'request_id': uuid(),
                                          'ticket_id': ticket_id["ticketIds"]["ticketIds"][0],
                                          'note': ticket_note}
                await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                                  ticket_append_note_msg,
                                                  timeout=15)

                slack_message = {'request_id': uuid(),
                                 'message': f'Ticket created with ticket id: {ticket_id["ticketIds"]["ticketIds"][0]}\n'
                                            f'https://app.bruin.com/helpdesk?clientId={client_id}&'
                                            f'ticketId={ticket_id["ticketIds"]["ticketIds"][0]} , in '
                                            f'{self._config.MONITOR_CONFIG["environment"]}'}
                await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

                self._logger.info(f'Ticket created with ticket id: {ticket_id["ticketIds"]["ticketIds"][0]}')

    async def _ticket_existence(self, client_id, serial, trouble):
        ticket_request_msg = {'request_id': uuid(),
                              'params': {
                                          'client_id': client_id,
                                          'category': 'SD-WAN',
                                          'ticket_topic': 'VAS',
                              },
                              'ticket_status': ['New', 'InProgress', 'Draft']}
        all_tickets = await self._event_bus.rpc_request("bruin.ticket.request", ticket_request_msg, timeout=200)
        for ticket in all_tickets['tickets']:
            ticket_detail_msg = {'request_id': uuid(),
                                 'ticket_id': ticket['ticketID']}
            ticket_details = await self._event_bus.rpc_request("bruin.ticket.details.request", ticket_detail_msg,
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
        edge_overview['Scan Time'] = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))
        if input > threshold:
            edge_overview["Receive"] = input
        if output > threshold:
            edge_overview["Transfer"] = output
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
