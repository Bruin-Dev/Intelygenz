import json
import re

from datetime import datetime
from datetime import timedelta
from typing import Callable

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone
from shortuuid import uuid

from igz.packages.repositories.edge_repository import EdgeIdentifier


class OutageMonitor:
    def __init__(self, event_bus, logger, scheduler, config, outage_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._outage_repository = outage_repository

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
        try:
            self._logger.info('[outage-monitoring] Claiming edges under monitoring...')
            edges_to_monitor_response = await self._get_edges_for_monitoring()
            self._logger.info('[outage-monitoring] Got edges under monitoring from Velocloud')
        except Exception as e:
            self._logger.error(f'[outage-monitoring] An error occurred while claiming edges for outage monitoring: {e}')
            raise

        edges_to_monitor_response_body = edges_to_monitor_response['body']
        edges_to_monitor_response_status = edges_to_monitor_response['status']
        if edges_to_monitor_response_status not in range(200, 300):
            err_msg = ('[outage-monitoring] Something happened while retrieving edges under monitoring from Velocloud. '
                       f'Reason: Error {edges_to_monitor_response_status} - {edges_to_monitor_response_body}')
            self._logger.error(err_msg)

            slack_message = {'request_id': uuid(), 'message': err_msg}
            await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
            return

        for edge_full_id in edges_to_monitor_response_body:
            edge_identifier = EdgeIdentifier(**edge_full_id)

            if edge_full_id in self._config.MONITOR_CONFIG['blacklisted_edges']:
                self._logger.info(f'[outage-monitoring] Edge {edge_identifier} is blacklisted at this moment. '
                                  'Skipping...')
                continue

            self._logger.info(f'[outage-monitoring] Checking status of {edge_identifier}...')
            edge_status_response = await self._get_edge_status_by_id(edge_full_id)
            self._logger.info(f'[outage-monitoring] Got status for edge {edge_identifier} -> {edge_status_response}')

            edge_status_response_body = edge_status_response['body']
            edge_status_response_status = edge_status_response['status']
            if edge_status_response_status not in range(200, 300):
                err_msg = (
                    f"[outage-monitoring] An error occurred while trying to retrieve edge status for edge "
                    f"{edge_identifier}: Error {edge_status_response_status} - {edge_status_response_body}"
                )

                self._logger.error(err_msg)
                slack_message = {'request_id': uuid(),
                                 'message': err_msg}
                await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=30)
                continue

            edge_data = edge_status_response_body["edge_info"]

            edge_serial = edge_data['edges']['serialNumber']
            if not edge_serial:
                self._logger.info(f"[outage-monitoring] Edge {edge_identifier} doesn't have any serial associated. "
                                  'Skipping...')
                continue

            self._logger.info(f'[outage-monitoring] Claiming Bruin client info for serial {edge_serial}...')
            bruin_client_info_response = await self._get_bruin_client_info_by_serial(edge_serial)
            self._logger.info(f'[outage-monitoring] Got Bruin client info for serial {edge_serial} -> '
                              f'{bruin_client_info_response}')

            bruin_client_info_response_body = bruin_client_info_response['body']
            bruin_client_info_response_status = bruin_client_info_response['status']
            if bruin_client_info_response_status not in range(200, 300):
                err_msg = (f'Error trying to get Bruin client info from Bruin for serial {edge_serial}: '
                           f'Error {bruin_client_info_response_status} - {bruin_client_info_response_body}')
                self._logger.error(err_msg)

                slack_message = {'request_id': uuid(), 'message': err_msg}
                await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
                continue

            if not bruin_client_info_response_body.get('client_id'):
                self._logger.info(
                    f"[outage-monitoring] Edge {edge_identifier} doesn't have any Bruin client ID associated. "
                    'Skipping...')
                continue

            # Attach Bruin client info to edge_data
            edge_data['bruin_client_info'] = bruin_client_info_response_body

            self._logger.info(f'[outage-monitoring] Getting management status for edge {edge_identifier}...')
            management_status_response = await self._get_management_status(edge_data)
            self._logger.info(f'[outage-monitoring] Got management status for edge {edge_identifier} -> '
                              f'{management_status_response}')

            management_status_response_body = management_status_response['body']
            management_status_response_status = management_status_response['status']
            if management_status_response_status not in range(200, 300):
                self._logger.error(f"Management status is unknown for {edge_identifier}")
                message = (
                    f"[outage-monitoring] Management status is unknown for {edge_identifier}. "
                    f"Cause: {management_status_response_body}"
                )
                slack_message = {'request_id': uuid(),
                                 'message': message}
                await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=30)
                continue

            if not self._is_management_status_active(management_status_response_body):
                self._logger.info(
                    f'Management status is not active for {edge_identifier}. Skipping process...')
                continue
            else:
                self._logger.info(f'Management status for {edge_identifier} seems active.')

            outage_happened = self._outage_repository.is_there_an_outage(edge_data)
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
                                            kwargs={
                                                'edge_full_id': edge_full_id,
                                                'bruin_client_info': bruin_client_info_response_body
                                            })
                    self._logger.info(f'[outage-monitoring] {edge_identifier} successfully scheduled for re-check.')
                except ConflictingIdError:
                    self._logger.info(f'There is a recheck job scheduled for {edge_identifier} already. No new job '
                                      'is going to be scheduled.')
            else:
                self._logger.info(f'[outage-monitoring] {edge_identifier} is in healthy state.')
                await self._run_ticket_autoresolve_for_edge(edge_full_id, edge_data)

    async def _run_ticket_autoresolve_for_edge(self, edge_full_id, edge_status):
        edge_identifier = EdgeIdentifier(**edge_full_id)
        self._logger.info(f'[ticket-autoresolve] Starting autoresolve for edge {edge_identifier}...')

        serial_number = edge_status['edges']['serialNumber']
        if serial_number not in self._config.MONITOR_CONFIG['autoresolve_serials_whitelist']:
            self._logger.info(f'[ticket-autoresolve] Skipping autoresolve for edge {edge_identifier} because its '
                              f'serial ({serial_number}) is not whitelisted.')
            return

        working_environment = self._config.MONITOR_CONFIG['environment']
        if working_environment != 'production':
            self._logger.info(f'[ticket-autoresolve] Skipping autoresolve for edge {edge_identifier} since the current '
                              f'environment is {working_environment.upper()}.')
            return

        seconds_ago_for_down_events_lookup = self._config.MONITOR_CONFIG['autoresolve_down_events_seconds']
        timedelta_for_down_events_lookup = timedelta(seconds=seconds_ago_for_down_events_lookup)
        last_down_events_response = await self._get_last_down_events_for_edge(
            edge_full_id, timedelta_for_down_events_lookup
        )

        last_down_events_body = last_down_events_response['body']
        last_down_events_status = last_down_events_response['status']
        if last_down_events_status not in range(200, 300):
            err_msg = (f'Error while retrieving down events for edge {edge_identifier}. '
                       f'Reason: Error {last_down_events_status} - {last_down_events_body}')

            self._logger.error(f'[ticket-autoresolve] {err_msg}')
            slack_message = {
                'request_id': uuid(),
                'message': err_msg
            }
            await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
            return

        if not last_down_events_body:
            self._logger.info(f'[ticket-autoresolve] No DOWN events found for edge {edge_identifier} in the '
                              f'last {seconds_ago_for_down_events_lookup / 60} minutes. Skipping autoresolve...')
            return

        outage_ticket_response = await self._get_outage_ticket_for_edge(edge_status)

        outage_ticket_response_body = outage_ticket_response['body']
        outage_ticket_response_status = outage_ticket_response['status']
        if outage_ticket_response_status not in range(200, 300):
            err_msg = (f'Error while retrieving outage ticket for edge {edge_identifier}. '
                       f'Reason: Error {outage_ticket_response_status} - {outage_ticket_response_body}')

            self._logger.error(f'[ticket-autoresolve] {err_msg}')
            slack_message = {
                'request_id': uuid(),
                'message': err_msg
            }
            await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
            return

        if not outage_ticket_response_body:
            self._logger.info(f'[ticket-autoresolve] No outage ticket found for edge {edge_identifier}. '
                              f'Skipping autoresolve...')
            return

        outage_ticket_id = outage_ticket_response_body['ticketID']
        notes_from_outage_ticket = outage_ticket_response_body['ticketNotes']
        if not self._outage_repository.is_outage_ticket_auto_resolvable(notes_from_outage_ticket, max_autoresolves=3):
            self._logger.info(f'[ticket-autoresolve] Limit to autoresolve ticket {outage_ticket_id} linked to edge '
                              f'{edge_identifier} has been maxed out already. Skipping autoresolve...')
            return

        details_from_ticket = outage_ticket_response_body['ticketDetails']
        detail_for_ticket_resolution = self._get_first_element_matching(
            details_from_ticket,
            lambda detail: detail['detailValue'] == serial_number,
         )

        self._logger.info(f'Autoresolving ticket {outage_ticket_id} linked to edge {edge_identifier}...')
        await self._resolve_outage_ticket(outage_ticket_id, detail_for_ticket_resolution['detailID'])
        await self._append_autoresolve_note_to_ticket(outage_ticket_id)

        bruin_client_id = edge_status['bruin_client_info']['client_id']
        await self._notify_successful_autoresolve(outage_ticket_id, bruin_client_id)

        self._logger.info(f'Ticket {outage_ticket_id} linked to edge {edge_identifier} was autoresolved!')

    @staticmethod
    def _get_first_element_matching(iterable, condition: Callable, fallback=None):
        try:
            return next(elem for elem in iterable if condition(elem))
        except StopIteration:
            return fallback

    async def _get_last_down_events_for_edge(self, edge_full_id, since: timedelta):
        current_datetime = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))

        last_down_events_request = {
            'request_id': uuid(),
            'body': {
                'edge': edge_full_id,
                'start_date': current_datetime - since,
                'end_date': current_datetime,
                'filter': ['EDGE_DOWN', 'LINK_DEAD'],
            }
        }
        down_events = await self._event_bus.rpc_request(
            "alert.request.event.edge", last_down_events_request, timeout=180
        )
        return down_events

    async def _resolve_outage_ticket(self, ticket_id, detail_id):
        resolve_ticket_request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
            }
        }
        await self._event_bus.rpc_request("bruin.ticket.status.resolve", resolve_ticket_request, timeout=15)

    async def _append_autoresolve_note_to_ticket(self, ticket_id):
        current_datetime = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))
        autoresolve_note = (
            f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: '
            f'{current_datetime + timedelta(seconds=1)}'
        )

        append_autoresolve_note_request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'note': autoresolve_note,
            }
        }
        await self._event_bus.rpc_request(
            "bruin.ticket.note.append.request", append_autoresolve_note_request, timeout=15
        )

    async def _notify_successful_autoresolve(self, ticket_id, client_id):
        notify_slack_message_request = {
            'request_id': uuid(),
            'message': (
                f'Ticket {ticket_id} was autoresolved in {self._config.TRIAGE_CONFIG["environment"].upper()} '
                f'environment. Details at https://app.bruin.com/helpdesk?clientId={client_id}&ticketId={ticket_id}'
            )
        }
        await self._event_bus.rpc_request("notification.slack.request", notify_slack_message_request, timeout=10)

    async def _get_outage_ticket_for_edge(self, edge_status: dict, ticket_statuses=None):
        edge_serial = edge_status['edges']['serialNumber']
        client_id = edge_status['bruin_client_info']['client_id']

        outage_ticket_request = {
            'request_id': uuid(),
            'body': {
                'edge_serial': edge_serial,
                'client_id': client_id,
            },
        }

        if ticket_statuses is not None:
            outage_ticket_request['body']['ticket_statuses'] = ticket_statuses

        outage_ticket = await self._event_bus.rpc_request(
            'bruin.ticket.outage.details.by_edge_serial.request', outage_ticket_request, timeout=180,
        )
        return outage_ticket

    async def _get_edges_for_monitoring(self):
        edge_list_request = {
            'request_id': uuid(),
            'body': {
                'filter': self._config.MONITOR_CONFIG['velocloud_instances_filter']
            },
        }

        edge_list = await self._event_bus.rpc_request("edge.list.request", edge_list_request, timeout=600)
        return edge_list

    async def _recheck_edge_for_ticket_creation(self, edge_full_id, bruin_client_info):
        edge_identifier = EdgeIdentifier(**edge_full_id)

        self._logger.info(
            f"[outage-recheck] Checking status of {edge_identifier} to ensure it's still in outage state...")
        full_edge_status = await self._get_edge_status_by_id(edge_full_id)
        self._logger.info(f'[outage-recheck] Got status for edge {edge_identifier}.')
        edge_status = {}
        is_outage = None
        if full_edge_status["status"] in range(200, 300):
            edge_status = full_edge_status["body"]["edge_info"]
            edge_status['bruin_client_info'] = bruin_client_info

            is_outage = self._outage_repository.is_there_an_outage(edge_status)
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

                    bruin_client_id = bruin_client_info['client_id']
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
                    err_msg = (f'Outage ticket creation failed for edge {edge_identifier}. Reason: '
                               f'Error {ticket_creation_response_status} - {ticket_creation_response_body}')

                    self._logger.error(f'[outage-recheck] {err_msg}')
                    slack_message = {
                        'request_id': uuid(),
                        'message': err_msg
                    }
                    await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
            else:
                self._logger.info(
                    f'[outage-recheck] Not starting outage ticket creation for faulty edge {edge_identifier} because '
                    f'the current working environment is {working_environment.upper()}.'
                )
        else:
            self._logger.info(
                f'[outage-recheck] {edge_identifier} seems to be healthy again! No ticket will be created.'
            )
            await self._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

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
            bruin_client_id = edge_status['bruin_client_info']['client_id']
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
        bruin_client_id = edge_status['bruin_client_info']['client_id']

        return {
            "client_id": bruin_client_id,
            "service_number": serial_number,
        }

    def _get_outage_causes(self, edge_status):
        outage_causes = {}

        edge_state = edge_status["edges"]["edgeState"]
        if self._outage_repository.is_faulty_edge(edge_state):
            outage_causes['edge'] = edge_state

        for link in edge_status['links']:
            link_data = link['link']
            link_state = link_data['state']

            if self._outage_repository.is_faulty_link(link_state):
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

    async def _get_management_status(self, edge_status):
        bruin_client_id = edge_status['bruin_client_info']['client_id']
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
        return management_status in {"Pending", "Active – Gold Monitoring", "Active – Platinum Monitoring"}
