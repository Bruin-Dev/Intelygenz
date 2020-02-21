import json
import re

from datetime import datetime
from datetime import timedelta

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone
from shortuuid import uuid

from igz.packages.repositories.edge_repository import EdgeIdentifier


class OutageMonitor:
    __client_id_regex = re.compile(r'^.*\|(?P<client_id>\d+)\|$')

    def __init__(self, event_bus, logger, scheduler, config, outage_utils):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._outage_utils = outage_utils

    async def start_service_outage_monitoring(self, exec_on_start):
        self._logger.info('Scheduling Service Outage Monitor job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('Service Outage Monitor job is going to be executed immediately')

        try:
            self._scheduler.add_job(self._outage_monitoring_process, 'interval',
                                    seconds=self._config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_service_outage_monitor_process')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of Service Outage Monitoring job. Reason: {conflict}')

    async def _outage_monitoring_process(self):
        edges_to_monitor = self._get_edges_for_monitoring()

        for edge_full_id in edges_to_monitor:
            edge_identifier = EdgeIdentifier(**edge_full_id)

            self._logger.info(f'[outage-monitoring] Checking status of {edge_identifier}.')
            full_edge_status = await self._get_edge_status_by_id(edge_full_id)
            self._logger.info(f'[outage-monitoring] Got status for edge: {edge_identifier}.')
            self._logger.info(f'[outage-monitoring] Getting management status for {edge_identifier}.')
            edge_status = {}
            if full_edge_status["status"] in range(200, 300):
                edge_status = full_edge_status["body"]["edge_info"]
                management_status = await self._get_management_status(edge_status)
            else:
                management_status = {"status": 500, "body": None}

            if management_status["status"] not in range(200, 300):
                self._logger.error(f"Management status is unknown for {edge_identifier}")
                message = (
                    f"[outage-monitoring] Management status is unknown for {edge_identifier}. "
                    f"Cause: {management_status['body']}"
                )
                slack_message = {'request_id': uuid(),
                                 'message': message}
                await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=30)
                continue

            if not self._is_management_status_active(management_status["body"]):
                self._logger.info(
                    f'Management status is not active for {edge_identifier}. Skipping process...')
                continue
            else:
                self._logger.info(f'Management status for {edge_identifier} seems active.')

            outage_happened = self._outage_utils.is_there_an_outage(edge_status)
            if outage_happened:
                self._logger.info(
                    f'[outage-monitoring] Outage detected for {edge_identifier}. '
                    'Scheduling edge to re-check it in a few moments.'
                )

                try:
                    tz = timezone(self._config.MONITOR_CONFIG['timezone'])
                    current_datetime = datetime.now(tz)
                    run_date = current_datetime + timedelta(
                        seconds=self._config.MONITOR_CONFIG['jobs_intervals']['quarantine'])
                    self._scheduler.add_job(self._recheck_edge_for_ticket_creation, 'date',
                                            run_date=run_date,
                                            replace_existing=False,
                                            misfire_grace_time=9999,
                                            id=f'_ticket_creation_recheck_{json.dumps(edge_full_id)}',
                                            kwargs={'edge_full_id': edge_full_id})
                    self._logger.info(f'[outage-monitoring] {edge_identifier} successfully scheduled for re-check.')
                except ConflictingIdError:
                    self._logger.info(f'There is a recheck job scheduled for {edge_identifier} already. No new job '
                                      'is going to be scheduled.')
            else:
                self._logger.info(f'[outage-monitoring] {edge_identifier} is in healthy state. Skipping...')

    def _get_edges_for_monitoring(self):
        return list(self._config.MONITORING_EDGES.values())

    async def _recheck_edge_for_ticket_creation(self, edge_full_id):
        edge_identifier = EdgeIdentifier(**edge_full_id)

        self._logger.info(
            f"[outage-recheck] Checking status of {edge_identifier} to ensure it's still in outage state...")
        full_edge_status = await self._get_edge_status_by_id(edge_full_id)
        self._logger.info(f'[outage-recheck] Got status for edge {edge_identifier}.')
        edge_status = {}
        is_outage = None
        if full_edge_status["status"] in range(200, 300):
            edge_status = full_edge_status["body"]["edge_info"]
            is_outage = self._outage_utils.is_there_an_outage(edge_status)
        if is_outage:
            self._logger.info(f'[outage-recheck] Edge {edge_identifier} is still in outage state.')

            working_environment = self._config.MONITOR_CONFIG['environment']
            if working_environment == 'production':
                self._logger.info(
                    f'[outage-recheck] Attempting outage ticket creation for faulty edge {edge_identifier}...'
                )

                ticket_creation_response = await self._create_outage_ticket(edge_status)
                ticket_creation_response_body = ticket_creation_response['body']
                ticket_creation_response_status = ticket_creation_response['status']
                if ticket_creation_response_status in range(200, 300):
                    self._logger.info(f'Successfully created outage ticket for edge {edge_identifier}.')

                    enterprise_name = edge_status['enterprise_name']
                    bruin_client_id = self._extract_client_id(enterprise_name)
                    slack_message = {
                        'request_id': uuid(),
                        'message': f'Outage ticket created for faulty edge {edge_identifier}. Ticket '
                                   f'details at https://app.bruin.com/helpdesk?clientId={bruin_client_id}&'
                                   f'ticketId={ticket_creation_response_body}.'
                    }
                    await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
                elif ticket_creation_response_status == 409:
                    self._logger.info(
                        f'[outage-recheck] Faulty edge {edge_identifier} already has an outage ticket in progress '
                        f'(ID = {ticket_creation_response_body}). Skipping outage ticket creation for this edge...'
                    )
                elif ticket_creation_response_status == 471:
                    self._logger.info(
                        f'[outage-recheck] Faulty edge {edge_identifier} has a resolved outage ticket '
                        f'(ID = {ticket_creation_response_body}). Re-opening ticket...'
                    )
                    await self._reopen_outage_ticket(ticket_creation_response_body, edge_status)
                else:
                    slack_message = {
                        'request_id': uuid(),
                        'message': f'Outage ticket creation failed for edge {edge_identifier}. Reason: '
                                   f'Error {ticket_creation_response_status} - {ticket_creation_response_body}'
                    }
                    await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
            else:
                self._logger.info(
                    f'[outage-recheck] Not starting outage ticket creation for faulty edge {edge_identifier} because '
                    f'the current working environment is {working_environment.upper()}.'
                )
        else:
            self._logger.info(
                f'[outage-recheck] {edge_identifier} seems to be healthy again! No ticket will be created.')

    async def _create_outage_ticket(self, edge_status):
        ticket_data = self._generate_outage_ticket(edge_status)
        ticket_creation_response = await self._event_bus.rpc_request(
            "bruin.ticket.creation.outage.request", {'request_id': uuid(), 'body': ticket_data}, timeout=30
        )

        return ticket_creation_response

    async def _reopen_outage_ticket(self, ticket_id, edge_status):
        self._logger.info(f'[outage-ticket-reopening] Reopening outage ticket {ticket_id}...')

        ticket_details_request_msg = {'request_id': uuid(), 'body': {'ticket_id': ticket_id}}
        ticket_details = await self._event_bus.rpc_request(
            "bruin.ticket.details.request", ticket_details_request_msg, timeout=15
        )
        detail_id_for_reopening = ticket_details['body']['ticketDetails'][0]['detailID']

        ticket_reopening_msg = {'request_id': uuid(), 'body': {'ticket_id': ticket_id,
                                                               'detail_id': detail_id_for_reopening}}
        ticket_reopening_response = await self._event_bus.rpc_request(
            "bruin.ticket.status.open", ticket_reopening_msg, timeout=30
        )

        if ticket_reopening_response['status'] == 200:
            self._logger.info(
                f'[outage-ticket-reopening] Outage ticket {ticket_id} reopening succeeded.'
            )
            enterprise_name = edge_status['enterprise_name']
            bruin_client_id = self._extract_client_id(enterprise_name)
            slack_message = {
                'request_id': uuid(),
                'message': f'Outage ticket {ticket_id} reopened. Ticket details at '
                           f'https://app.bruin.com/helpdesk?clientId={bruin_client_id}&ticketId={ticket_id}.'
            }
            await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
            await self._post_note_in_outage_ticket(ticket_id, edge_status)
        else:
            self._logger.error(
                f'[outage-ticket-creation] Outage ticket {ticket_id} reopening failed.'
            )

    async def _post_note_in_outage_ticket(self, ticket_id, edge_status):
        ticket_note_timestamp = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))

        outage_causes = self._get_outage_causes(edge_status)
        ticket_note_outage_causes = 'Outage causes:'
        if outage_causes is not None:
            edge_state = outage_causes.get('edge')
            if edge_state is not None:
                ticket_note_outage_causes += f' Edge was {edge_state}.'

            links_states = outage_causes.get('links')
            if links_states is not None:
                for interface, state in links_states.items():
                    ticket_note_outage_causes += f' Link {interface} was {state}.'
        else:
            ticket_note_outage_causes += ' Could not determine causes.'

        ticket_note = (
            f'#*Automation Engine*#\n'
            f'Re-opening ticket.\n'
            f'{ticket_note_outage_causes}\n'
            f'TimeStamp: {str(ticket_note_timestamp)}'
        )

        ticket_append_note_msg = {'request_id': uuid(), 'body': {'ticket_id': ticket_id, 'note': ticket_note}}

        self._logger.info(f'[outage-ticket-reopening] Posting reopening note in ticket {ticket_id}...')
        await self._event_bus.rpc_request("bruin.ticket.note.append.request", ticket_append_note_msg, timeout=15)

    def _generate_outage_ticket(self, edge_status):
        serial_number = edge_status['edges']['serialNumber']
        enterprise_name = edge_status['enterprise_name']
        bruin_client_id = self._extract_client_id(enterprise_name)

        return {
            "client_id": bruin_client_id,
            "service_number": serial_number,
        }

    def _get_outage_causes(self, edge_status):
        outage_causes = {}

        edge_state = edge_status["edges"]["edgeState"]
        if self._outage_utils.is_faulty_edge(edge_state):
            outage_causes['edge'] = edge_state

        for link in edge_status['links']:
            link_data = link['link']
            link_state = link_data['state']

            if self._outage_utils.is_faulty_link(link_state):
                outage_links_states = outage_causes.setdefault('links', {})
                outage_links_states[link_data['interface']] = link_state

        return outage_causes or None

    async def _get_edge_status_by_id(self, edge_full_id):
        edge_status_request_dict = {
            'request_id': uuid(),
            'body': edge_full_id,
        }
        edge_status_response = await self._event_bus.rpc_request(
            'edge.status.request', edge_status_request_dict, timeout=120,
        )

        return edge_status_response

    def _extract_client_id(self, enterprise_name):
        client_id_match = self.__client_id_regex.match(enterprise_name)

        if client_id_match:
            client_id = client_id_match.group('client_id')
            return int(client_id)
        else:
            return 9994

    async def _get_management_status(self, edge_status):
        enterprise_name = edge_status['enterprise_name']
        bruin_client_id = self._extract_client_id(enterprise_name)
        serial_number = edge_status['edges']['serialNumber']
        management_request = {
            "request_id": uuid(),
            "body": {
                "client_id": bruin_client_id,
                "status": "A",
                "service_number": serial_number
            }
        }

        management_status = await self._event_bus.rpc_request("bruin.inventory.management.status",
                                                              management_request, timeout=30)

        return management_status

    def _is_management_status_active(self, management_status) -> bool:
        return management_status in {"Pending", "Active – Gold Monitoring", "Active – Platinum Monitoring"}
