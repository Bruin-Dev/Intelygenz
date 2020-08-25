import json
import re
import time

from collections import OrderedDict
from datetime import datetime, timedelta

from apscheduler.util import undefined
from pytz import timezone, utc
from shortuuid import uuid

from igz.packages.eventbus.eventbus import EventBus


class ServiceAffectingMonitor:

    def __init__(self, event_bus: EventBus, logger, scheduler, config, template_renderer, metrics_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._monitoring_minutes = config.MONITOR_CONFIG["monitoring_minutes"]
        self._template_renderer = template_renderer
        self._metrics_repository = metrics_repository

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
        start_time = time.time()
        self._logger.info(f"[service-affecting-monitor] Processing "
                          f"{len(self._config.MONITOR_CONFIG['device_by_id'])} edges")
        monitored_edges = [await self._service_affecting_monitor_process(device) for device in
                           self._config.MONITOR_CONFIG['device_by_id']]
        self._logger.info(f"[service-affecting-monitor] Processing "
                          f"{len(self._config.MONITOR_CONFIG['device_by_id'])} edges. Took "
                          f"{time.time() - start_time} seconds")

    async def _get_management_status(self, enterprise_id, serial_number):
        management_request = {
            "request_id": uuid(),
            "body": {
                "client_id": enterprise_id,
                "status": "A",
                "service_number": serial_number
            }
        }
        management_status = await self._event_bus.rpc_request("bruin.inventory.management.status",
                                                              management_request, timeout=30)
        return management_status

    async def _get_bruin_client_info_by_serial(self, serial_number):
        client_info_request = {
            "request_id": uuid(),
            "body": {
                "service_number": serial_number,
            },
        }

        client_info = await self._event_bus.rpc_request("bruin.customer.get.info", client_info_request, timeout=30)
        return client_info

    def _is_management_status_active(self, management_status) -> bool:
        return management_status in self._config.MONITOR_CONFIG["management_status_filter"]

    async def _service_affecting_monitor_process(self, device):
        edge_id = {"host": device['host'], "enterprise_id": device['enterprise_id'], "edge_id": device['edge_id']}
        edge_identifier = device['edge_id']
        interval = {
            "end": datetime.now(utc),
            "start": (datetime.now(utc) - timedelta(minutes=self._monitoring_minutes))}
        edge_status_request = {'request_id': uuid(),
                               'body': {**edge_id, "interval": interval}
                               }
        edge_status = await self._event_bus.rpc_request("edge.status.request", edge_status_request, timeout=60)
        self._logger.info(f'Edge received from event bus')
        self._logger.info(f'{edge_status}')

        if edge_status is None or 'edge_info' not in edge_status['body'].keys() \
                or 'links' not in edge_status['body']['edge_info'].keys() \
                or 'edges' not in edge_status['body']['edge_info'].keys() \
                or 'serialNumber' not in edge_status['body']['edge_info']['edges'].keys():
            self._logger.error(f'Data received from Velocloud is incomplete')
            self._logger.error(f'{json.dumps(edge_status, indent=2)}')
            slack_message = {'request_id': uuid(),
                             'message': f'Error while monitoring edge for service affecting trouble, seems like data '
                                        f'is corrupted: \n {json.dumps(edge_status, indent=2)} \n'
                                        f'The environment is {self._config.MONITOR_CONFIG["environment"]}'}
            await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
            return

        serial_number = edge_status['body']['edge_info']['edges']['serialNumber']

        self._logger.info(f'[service-affecting-monitoring] Claiming Bruin client info for serial {serial_number}...')
        bruin_client_info_response = await self._get_bruin_client_info_by_serial(serial_number)
        self._logger.info(f'[service-affecting-monitoring] Got Bruin client info for serial {serial_number} -> '
                          f'{bruin_client_info_response}')
        bruin_client_info_response_body = bruin_client_info_response['body']
        bruin_client_info_response_status = bruin_client_info_response['status']
        if bruin_client_info_response_status not in range(200, 300):
            err_msg = (f'Error trying to get Bruin client info from Bruin for serial {serial_number}: '
                       f'Error {bruin_client_info_response_status} - {bruin_client_info_response_body}')
            self._logger.error(err_msg)

            slack_message = {'request_id': uuid(), 'message': err_msg}
            await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
            return

        if not bruin_client_info_response_body.get('client_id'):
            self._logger.info(
                f"[service-affecting-monitoring] Edge {device} doesn't have any Bruin client ID associated. "
                'Skipping...')
            return

        self._logger.info(f'[service-affecting-monitoring] Getting management status for edge {edge_identifier}...')
        management_status_response = await self._get_management_status(
            bruin_client_info_response_body.get('client_id'), serial_number)
        self._logger.info(f'[service-affecting-monitoring] Got management status for edge {edge_identifier} -> '
                          f'{management_status_response}')

        management_status_response_body = management_status_response['body']
        management_status_response_status = management_status_response['status']
        if management_status_response_status not in range(200, 300):
            self._logger.error(f"Management status is unknown for {edge_identifier}")
            message = (
                f"[service-affecting-monitoring] Management status is unknown for {edge_identifier}. "
                f"Cause: {management_status_response_body}"
            )
            slack_message = {'request_id': uuid(),
                             'message': message}
            await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=30)
            return

        if not self._is_management_status_active(management_status_response_body):
            self._logger.info(
                f'Management status is not active for {edge_identifier}. Skipping process...')
            return
        else:
            self._logger.info(f'Management status for {edge_identifier} seems active.')

        for link in edge_status['body']['edge_info']['links']:
            if 'serviceGroups' in link.keys():
                await self._latency_check(device, edge_status['body'], link)
                await self._packet_loss_check(device, edge_status['body'], link)
                await self._jitter_check(device, edge_status['body'], link)
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
        self._logger.info(f'Service affecting trouble {trouble} detected in edge with data {edge_status}')
        if self._config.MONITOR_CONFIG['environment'] == 'production':
            client_id = edge_status['edge_info']['enterprise_name'].split('|')[1]
            ticket_exists = await self._ticket_existence(client_id, edge_status['edge_info']['edges']['serialNumber'],
                                                         trouble)
            if ticket_exists is False:
                # TODO contact is hardcoded. When Mettel provides us with a service to retrieve the contact change here
                ticket_dict = self._compose_ticket_dict(edge_status, link, input, output, trouble, threshold)
                ticket_note = self._ticket_object_to_string(ticket_dict)
                ticket_details = {
                    "request_id": uuid(),
                    "body": {
                                "clientId": client_id,
                                "category": "VAS",
                                "services": [
                                    {
                                        "serviceNumber": edge_status['edge_info']['edges']['serialNumber']
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
                if ticket_id["status"] not in range(200, 300):
                    err_msg = (f'Outage ticket creation failed for edge {edge_status["edge_id"]}. Reason: '
                               f'Error {ticket_id["status"]} - {ticket_id["body"]}')

                    self._logger.error(err_msg)
                    slack_message = {
                        'request_id': uuid(),
                        'message': err_msg
                    }
                    await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
                    return

                self._metrics_repository.increment_tickets_created()

                ticket_append_note_msg = {'request_id': uuid(),
                                          'body': {
                                          'ticket_id': ticket_id["body"]["ticketIds"][0],
                                          'note': ticket_note}}
                await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                                  ticket_append_note_msg,
                                                  timeout=15)

                slack_message = {'request_id': uuid(),
                                 'message': f'Ticket created with ticket id: {ticket_id["body"]["ticketIds"][0]}\n'
                                            f'https://app.bruin.com/helpdesk?clientId={client_id}&'
                                            f'ticketId={ticket_id["body"]["ticketIds"][0]} , in '
                                            f'{self._config.MONITOR_CONFIG["environment"]}'}
                await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

                self._logger.info(f'Ticket created with ticket id: {ticket_id["body"]["ticketIds"][0]}')

    async def _ticket_existence(self, client_id, serial, trouble):
        ticket_request_msg = {'request_id': uuid(),
                              'body': {
                                          'client_id': client_id,
                                          'category': 'SD-WAN',
                                          'ticket_topic': 'VAS',
                                          'ticket_status': ['New', 'InProgress', 'Draft']}}
        all_tickets = await self._event_bus.rpc_request("bruin.ticket.request", ticket_request_msg, timeout=200)
        for ticket in all_tickets['body']:
            ticket_detail_msg = {'request_id': uuid(),
                                 'body': {'ticket_id': ticket['ticketID']}}
            ticket_details = await self._event_bus.rpc_request("bruin.ticket.details.request", ticket_detail_msg,
                                                               timeout=15)
            for ticket_detail in ticket_details['body']['ticketDetails']:
                if 'detailValue' in ticket_detail.keys():
                    if ticket_detail['detailValue'] == serial:
                        for ticket_note in (ticket_details['body']['ticketNotes']):
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
