import re
import time
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from time import perf_counter
from typing import Callable

import asyncio
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone
from pytz import utc

from application.repositories import EdgeIdentifier

TRIAGE_NOTE_REGEX = re.compile(r'^#\*Automation Engine\*#\nTriage \(VeloCloud\)')
REOPEN_NOTE_REGEX = re.compile(r'^#\*Automation Engine\*#\nRe-opening')


class OutageMonitor:
    def __init__(self, event_bus, logger, scheduler, config, outage_repository, bruin_repository, velocloud_repository,
                 notifications_repository, triage_repository, customer_cache_repository, metrics_repository,
                 digi_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._outage_repository = outage_repository
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository
        self._notifications_repository = notifications_repository
        self._triage_repository = triage_repository
        self._customer_cache_repository = customer_cache_repository
        self._metrics_repository = metrics_repository
        self._digi_repository = digi_repository

        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['semaphore'])

        self.__reset_state()

    def __reset_state(self):
        self._customer_cache = []
        self._autoresolve_serials_whitelist = set()

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
        self.__reset_state()

        start = time.time()
        self._logger.info(f"[outage_monitoring_process] Start with map cache!")

        customer_cache_response = await self._customer_cache_repository.get_cache_for_outage_monitoring()
        if customer_cache_response['status'] not in range(200, 300) or customer_cache_response['status'] == 202:
            return

        self._logger.info('[outage_monitoring_process] Ignoring blacklisted edges...')
        self._customer_cache = [
            elem
            for elem in customer_cache_response['body']
            if elem['edge'] not in self._config.MONITOR_CONFIG['blacklisted_edges']
        ]

        self._logger.info("[outage_monitoring_process] Creating list of whitelisted serials for autoresolve...")
        autoresolve_filter = self._config.MONITOR_CONFIG['velocloud_instances_filter'].keys()
        autoresolve_filter_enabled = len(autoresolve_filter) > 0
        if not autoresolve_filter_enabled:
            self._autoresolve_serials_whitelist = set(elem['serial_number'] for elem in self._customer_cache)
        else:
            self._autoresolve_serials_whitelist = set(
                elem['serial_number']
                for elem in self._customer_cache
                if elem['edge']['host'] in autoresolve_filter
            )

        split_cache = defaultdict(list)
        self._logger.info("[outage_monitoring_process] Splitting cache by host")

        for edge_info in self._customer_cache:
            split_cache[edge_info['edge']['host']].append(edge_info)
        self._logger.info('[outage_monitoring_process] Cache split')

        process_tasks = [
            self._process_velocloud_host(host, split_cache[host])
            for host in split_cache
        ]
        await asyncio.gather(*process_tasks, return_exceptions=True)

        stop = time.time()
        self._logger.info(f'[outage_monitoring_process] Outage monitoring process finished! Elapsed time:'
                          f'{round((stop - start) / 60, 2)} minutes')
        self._metrics_repository.set_last_cycle_duration(round((stop - start) / 60, 2))

    async def _process_velocloud_host(self, host, host_cache):
        self._logger.info(f"Processing {len(host_cache)} edges in Velocloud {host}...")
        start = perf_counter()

        links_with_edge_info_response = await self._velocloud_repository.get_links_with_edge_info(velocloud_host=host)
        if links_with_edge_info_response['status'] not in range(200, 300):
            return

        links_with_edge_info: list = links_with_edge_info_response['body']

        links_grouped_by_edge = self._velocloud_repository.group_links_by_edge(links_with_edge_info)
        edges_full_info = self._map_cached_edges_with_edges_status(host_cache, links_grouped_by_edge)

        outage_edges = [edge for edge in edges_full_info if self._outage_repository.is_there_an_outage(edge['status'])]
        healthy_edges = [edge for edge in edges_full_info if edge not in outage_edges]

        if outage_edges:
            self._logger.info(
                f"{len(outage_edges)} edges were detected in outage state. Scheduling re-check job for all of them..."
            )
            self._schedule_recheck_job_for_edges(outage_edges)
        else:
            self._logger.info("No edges were detected in outage state. Re-check job won't be scheduled")

        if healthy_edges:
            self._logger.info(
                f"{len(healthy_edges)} edges were detected in healthy state. Running autoresolve for all of them..."
            )
            autoresolve_tasks = [self._run_ticket_autoresolve_for_edge(edge) for edge in healthy_edges]
            await asyncio.gather(*autoresolve_tasks)
        else:
            self._logger.info("No edges were detected in healthy state. Autoresolve won't be triggered")

        stop = perf_counter()
        self._logger.info(f"Elapsed time processing edges in host {host}: {round((stop - start) / 60, 2)} minutes")

        self._metrics_repository.increment_edges_processed(amount=len(edges_full_info))

    def _schedule_recheck_job_for_edges(self, edges: list):
        self._logger.info(f'Scheduling recheck job for {len(edges)} edges in outage state...')

        tz = timezone(self._config.MONITOR_CONFIG['timezone'])
        current_datetime = datetime.now(tz)
        run_date = current_datetime + timedelta(seconds=self._config.MONITOR_CONFIG['jobs_intervals']['quarantine'])

        self._scheduler.add_job(self._recheck_edges_for_ticket_creation, 'date',
                                args=[edges],
                                run_date=run_date,
                                replace_existing=False,
                                misfire_grace_time=9999,
                                id=f'_ticket_creation_recheck',
                                )

        self._logger.info(f'Edges scheduled for recheck successfully')

    def _map_cached_edges_with_edges_status(self, customer_cache: list, edges_status: list) -> list:
        result = []

        cached_edges_by_edge_identifier = {
            EdgeIdentifier(**elem['edge']): elem
            for elem in customer_cache
        }
        edge_statuses_by_edge_identifier = {
            EdgeIdentifier(host=elem['host'], enterprise_id=elem['enterpriseId'], edge_id=elem['edgeId']): elem
            for elem in edges_status
        }

        for edge_identifier, cached_edge in cached_edges_by_edge_identifier.items():
            edge_status = edge_statuses_by_edge_identifier.get(edge_identifier)
            if not edge_status:
                self._logger.info(f'No edge status was found for cached edge {edge_identifier}. Skipping...')
                continue

            result.append({
                'cached_info': cached_edge,
                'status': edge_status,
            })

        return result

    async def _run_ticket_autoresolve_for_edge(self, edge: dict):
        async with self._semaphore:
            edge_identifier = EdgeIdentifier(**edge['cached_info']['edge'])
            self._logger.info(f'[ticket-autoresolve] Starting autoresolve for edge {edge_identifier}...')

            serial_number = edge['cached_info']['serial_number']
            if serial_number not in self._autoresolve_serials_whitelist:
                self._logger.info(f'[ticket-autoresolve] Skipping autoresolve for edge {edge_identifier} because its '
                                  f'serial ({serial_number}) is not whitelisted.')
                return

            client_id = edge['cached_info']['bruin_client_info']['client_id']
            outage_ticket_response = await self._bruin_repository.get_open_outage_tickets(
                client_id, service_number=serial_number
            )
            outage_ticket_response_body = outage_ticket_response['body']
            outage_ticket_response_status = outage_ticket_response['status']
            if outage_ticket_response_status not in range(200, 300):
                return

            if not outage_ticket_response_body:
                self._logger.info(f'[ticket-autoresolve] No outage ticket found for edge {edge_identifier}. '
                                  f'Skipping autoresolve...')
                return

            outage_ticket: dict = outage_ticket_response_body[0]
            outage_ticket_id = outage_ticket['ticketID']
            outage_ticket_creation_date = outage_ticket['createDate']

            if not self._was_ticket_created_by_automation_engine(outage_ticket):
                self._logger.info(
                    f'Ticket {outage_ticket_id} was not created by Automation Engine. Skipping autoresolve...'
                )
                return

            ticket_details_response = await self._bruin_repository.get_ticket_details(outage_ticket_id)
            ticket_details_response_body = ticket_details_response['body']
            ticket_details_response_status = ticket_details_response['status']
            if ticket_details_response_status not in range(200, 300):
                return

            details_from_ticket = ticket_details_response_body['ticketDetails']
            detail_for_ticket_resolution = self._get_first_element_matching(
                details_from_ticket,
                lambda detail: detail['detailValue'] == serial_number,
            )
            ticket_detail_id = detail_for_ticket_resolution['detailID']

            notes_from_outage_ticket = ticket_details_response_body['ticketNotes']
            relevant_notes = [note for note in notes_from_outage_ticket if serial_number in note['serviceNumber']]
            if not self._was_last_outage_detected_recently(relevant_notes, outage_ticket_creation_date):
                self._logger.info(
                    f'Edge {edge_identifier} has been in outage state for a long time, so detail {ticket_detail_id} '
                    f'(serial {serial_number}) of ticket {outage_ticket_id} will not be autoresolved. Skipping '
                    f'autoresolve...'
                )
                return

            can_detail_be_autoresolved_one_more_time = self._outage_repository.is_outage_ticket_detail_auto_resolvable(
                notes_from_outage_ticket, serial_number, max_autoresolves=3
            )
            if not can_detail_be_autoresolved_one_more_time:
                self._logger.info(
                    f'[ticket-autoresolve] Limit to autoresolve detail {ticket_detail_id} (serial {serial_number}) '
                    f'of ticket {outage_ticket_id} linked to edge {edge_identifier} has been maxed out already. '
                    'Skipping autoresolve...'
                )
                return

            if self._is_detail_resolved(detail_for_ticket_resolution):
                self._logger.info(
                    f'Detail {ticket_detail_id} (serial {serial_number}) of ticket {outage_ticket_id} is already '
                    'resolved. Skipping autoresolve...'
                )
                return

            working_environment = self._config.MONITOR_CONFIG['environment']
            if working_environment != 'production':
                self._logger.info(f'[ticket-autoresolve] Skipping autoresolve for edge {edge_identifier} since the '
                                  f'current environment is {working_environment.upper()}.')
                return

            self._logger.info(
                f'Autoresolving detail {ticket_detail_id} of ticket {outage_ticket_id} linked to edge '
                f'{edge_identifier} with serial number {serial_number}...'
            )
            resolve_ticket_response = await self._bruin_repository.resolve_ticket(outage_ticket_id, ticket_detail_id)
            if resolve_ticket_response['status'] not in range(200, 300):
                return

            await self._bruin_repository.append_autoresolve_note_to_ticket(outage_ticket_id, serial_number)
            await self._notify_successful_autoresolve(outage_ticket_id)

            self._metrics_repository.increment_tickets_autoresolved()
            self._logger.info(
                f'Detail {ticket_detail_id} (serial {serial_number}) of ticket {outage_ticket_id} linked to '
                f'edge {edge_identifier} was autoresolved!'
            )

    @staticmethod
    def _was_ticket_created_by_automation_engine(ticket: dict) -> bool:
        return ticket['createdBy'] == 'Intelygenz Ai'

    @staticmethod
    def _is_detail_resolved(ticket_detail: dict):
        return ticket_detail['detailStatus'] == 'R'

    @staticmethod
    def _get_first_element_matching(iterable, condition: Callable, fallback=None):
        try:
            return next(elem for elem in iterable if condition(elem))
        except StopIteration:
            return fallback

    def _find_note(self, ticket_notes, watermark):
        return self._get_first_element_matching(
            iterable=ticket_notes,
            condition=lambda note: watermark in note.get('noteValue'),
            fallback=None
        )

    def _get_last_element_matching(self, iterable, condition: Callable, fallback=None):
        return self._get_first_element_matching(reversed(iterable), condition, fallback)

    async def _notify_successful_autoresolve(self, ticket_id):
        message = f'Outage ticket {ticket_id} was autoresolved. Details at https://app.bruin.com/t/{ticket_id}'
        await self._notifications_repository.send_slack_message(message)

    async def _recheck_edges_for_ticket_creation(self, outage_edges: list):
        self._logger.info(f'Re-checking {len(outage_edges)} edges in outage state prior to ticket creation...')

        # This method is never called with an empty outage_edges, so no IndexError should be raised
        host = outage_edges[0]['status']['host']

        links_with_edge_info_response = await self._velocloud_repository.get_links_with_edge_info(velocloud_host=host)
        if links_with_edge_info_response['status'] not in range(200, 300):
            return

        links_with_edge_info: list = links_with_edge_info_response['body']
        links_grouped_by_edge = self._velocloud_repository.group_links_by_edge(links_with_edge_info)

        customer_cache_for_outage_edges = [elem['cached_info'] for elem in outage_edges]
        edges_full_info = self._map_cached_edges_with_edges_status(
            customer_cache_for_outage_edges, links_grouped_by_edge
        )

        edges_still_in_outage = [
            edge
            for edge in edges_full_info
            if self._outage_repository.is_there_an_outage(edge['status'])
        ]
        healthy_edges = [edge for edge in edges_full_info if edge not in edges_still_in_outage]

        if edges_still_in_outage:
            self._logger.info(
                f"{len(edges_still_in_outage)} edges were detected as still in outage state after re-check. "
                f"Attempting outage ticket creation for all of them..."
            )

            working_environment = self._config.MONITOR_CONFIG['environment']
            if working_environment == 'production':
                for edge in edges_still_in_outage:
                    edge_full_id = edge['cached_info']['edge']
                    edge_status = edge['status']

                    edge_identifier = EdgeIdentifier(**edge_full_id)
                    self._logger.info(
                        f'[outage-recheck] Attempting outage ticket creation for faulty edge {edge_identifier}...'
                    )

                    serial_number = edge['cached_info']['serial_number']
                    bruin_client_id = edge['cached_info']['bruin_client_info']['client_id']
                    ticket_creation_response = await self._bruin_repository.create_outage_ticket(
                        bruin_client_id, serial_number
                    )
                    ticket_creation_response_body = ticket_creation_response['body']
                    ticket_creation_response_status = ticket_creation_response['status']
                    logical_id_list = edge['cached_info']['logical_ids']
                    if ticket_creation_response_status in range(200, 300):
                        self._logger.info(f'Successfully created outage ticket for edge {edge_identifier}.')
                        self._metrics_repository.increment_tickets_created()

                        slack_message = (
                            f'Outage ticket created for faulty edge {edge_identifier}. Ticket '
                            f'details at https://app.bruin.com/t/{ticket_creation_response_body}.'
                        )
                        await self._notifications_repository.send_slack_message(slack_message)
                        await self._append_triage_note(ticket_creation_response_body, edge_full_id, edge_status)
                        await self._check_for_digi_reboot(ticket_creation_response_body,
                                                          logical_id_list, serial_number, edge_status, edge_full_id)
                    elif ticket_creation_response_status == 409:
                        self._logger.info(
                            f'[outage-recheck] Faulty edge {edge_identifier} already has an outage ticket in progress '
                            f'(ID = {ticket_creation_response_body}). Skipping outage ticket creation for this edge...'
                        )
                        await self._check_for_failed_digi_reboot(ticket_creation_response_body,
                                                                 logical_id_list, serial_number, edge_status,
                                                                 edge_full_id)
                    elif ticket_creation_response_status == 471:
                        self._logger.info(
                            f'[outage-recheck] Faulty edge {edge_identifier} has a resolved outage ticket '
                            f'(ID = {ticket_creation_response_body}). Re-opening ticket...'
                        )
                        await self._reopen_outage_ticket(ticket_creation_response_body, edge_status)
                        await self._check_for_digi_reboot(ticket_creation_response_body,
                                                          logical_id_list, serial_number, edge_status, edge_full_id)
                    elif ticket_creation_response_status == 472:
                        self._logger.info(
                            f'[outage-recheck] Faulty edge {edge_identifier} has a resolved outage ticket '
                            f'(ID = {ticket_creation_response_body}). Its ticket detail was automatically unresolved '
                            f'by Bruin. Appending reopen note to ticket...'
                        )
                        await self._post_note_in_outage_ticket(ticket_creation_response_body, edge_status)
                    elif ticket_creation_response_status == 473:
                        self._logger.info(
                            f'[outage-recheck] There is a resolve outage ticket for the same location of faulty edge '
                            f'{edge_identifier} (ticket ID = {ticket_creation_response_body}). The ticket was'
                            f'automatically unresolved by Bruin and a new ticket detail for serial {serial_number} was '
                            f'appended to it. Appending initial triage note for this service number...'
                        )
                        await self._append_triage_note(ticket_creation_response_body, edge_full_id, edge_status)
            else:
                self._logger.info(
                    f'[outage-recheck] Not starting outage ticket creation for {len(edges_still_in_outage)} faulty '
                    f'edges because the current working environment is {working_environment.upper()}.'
                )
        else:
            self._logger.info("No edges were detected in outage state after re-check. Outage tickets won't be created")

        if healthy_edges:
            self._logger.info(
                f"{len(healthy_edges)} edges were detected in healthy state after re-check. '"
                "Running autoresolve for all of them..."
            )
            autoresolve_tasks = [self._run_ticket_autoresolve_for_edge(edge) for edge in healthy_edges]
            await asyncio.gather(*autoresolve_tasks)
        else:
            self._logger.info("No edges were detected in healthy state. Autoresolve won't be triggered")

        self._logger.info(f'Re-check process finished for {len(outage_edges)} edges')

    async def _append_triage_note(self, ticket_id, edge_full_id, edge_status):
        edge_identifier = EdgeIdentifier(**edge_full_id)

        past_moment_for_events_lookup = datetime.now(utc) - timedelta(days=7)

        recent_events_response = await self._velocloud_repository.get_last_edge_events(
            edge_full_id, since=past_moment_for_events_lookup
        )
        recent_events_response_body = recent_events_response['body']
        recent_events_response_status = recent_events_response['status']

        if recent_events_response_status not in range(200, 300):
            return

        if not recent_events_response_body:
            self._logger.info(
                f'No events were found for edge {edge_identifier} starting from {past_moment_for_events_lookup}. '
                f'Not appending any triage note to ticket {ticket_id}.'
            )
            return

        recent_events_response_body.sort(key=lambda event: event['eventTime'], reverse=True)

        ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
        if ticket_details_response['status'] not in range(200, 300):
            return

        ticket_detail: dict = ticket_details_response['body']['ticketDetails'][0]
        ticket_detail_id = ticket_detail['detailID']
        service_number = ticket_detail['detailValue']

        ticket_note = self._triage_repository.build_triage_note(edge_full_id, edge_status, recent_events_response_body)

        self._logger.info(
            f'Appending triage note to detail {ticket_detail_id} (serial {service_number}) of recently created '
            f'ticket {ticket_id}...'
        )
        detail_object = {
            'ticket_id': ticket_id,
            'ticket_detail': ticket_detail,
        }
        note_appended = await self._bruin_repository.append_triage_note(detail_object, ticket_note)

        if note_appended == 503:
            self._metrics_repository.increment_first_triage_errors()

    async def _reopen_outage_ticket(self, ticket_id, edge_status):
        serial_number = edge_status['edgeSerialNumber']
        self._logger.info(f'Reopening outage ticket {ticket_id} for serial {serial_number}...')

        ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
        ticket_details_response_body = ticket_details_response['body']
        ticket_details_response_status = ticket_details_response['status']
        if ticket_details_response_status not in range(200, 300):
            return

        ticket_detail_for_reopen = self._get_first_element_matching(
            ticket_details_response_body['ticketDetails'],
            lambda detail: detail['detailValue'] == serial_number,
        )
        detail_id_for_reopening = ticket_detail_for_reopen['detailID']

        ticket_reopening_response = await self._bruin_repository.open_ticket(ticket_id, detail_id_for_reopening)
        ticket_reopening_response_status = ticket_reopening_response['status']

        if ticket_reopening_response_status == 200:
            self._logger.info(f'Detail {detail_id_for_reopening} of outage ticket {ticket_id} reopened successfully.')
            slack_message = (
                f'Detail {detail_id_for_reopening} of outage ticket {ticket_id} reopened: '
                f'https://app.bruin.com/t/{ticket_id}'
            )
            await self._notifications_repository.send_slack_message(slack_message)
            await self._post_note_in_outage_ticket(ticket_id, edge_status)

            self._metrics_repository.increment_tickets_reopened()
        else:
            self._logger.error(f'Reopening for detail {detail_id_for_reopening} of outage ticket {ticket_id} failed.')

    async def _post_note_in_outage_ticket(self, ticket_id, edge_status):
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

        serial_number = edge_status['edgeSerialNumber']
        await self._bruin_repository.append_reopening_note_to_ticket(
            ticket_id, serial_number, ticket_note_outage_causes
        )

    def _get_outage_causes(self, edge_status):
        outage_causes = {}

        edge_state = edge_status["edgeState"]
        if self._outage_repository.is_faulty_edge(edge_state):
            outage_causes['edge'] = edge_state

        for link in edge_status['links']:
            link_state = link['linkState']

            if self._outage_repository.is_faulty_link(link_state):
                outage_links_states = outage_causes.setdefault('links', {})
                outage_links_states[link['interface']] = link_state

        return outage_causes or None

    def _was_last_outage_detected_recently(self, ticket_notes: list, ticket_creation_date: str) -> bool:
        current_datetime = datetime.now(utc)
        max_seconds_since_last_outage = self._config.MONITOR_CONFIG['autoresolve_last_outage_seconds']

        notes_sorted_by_date_asc = sorted(ticket_notes, key=lambda note: note['createdDate'])

        last_reopen_note = self._get_last_element_matching(
            notes_sorted_by_date_asc,
            lambda note: REOPEN_NOTE_REGEX.match(note['noteValue'])
        )
        if last_reopen_note:
            note_creation_date = parse(last_reopen_note['createdDate']).astimezone(utc)
            seconds_elapsed_since_last_outage = (current_datetime - note_creation_date).total_seconds()
            return seconds_elapsed_since_last_outage <= max_seconds_since_last_outage

        triage_note = self._get_first_element_matching(
            notes_sorted_by_date_asc,
            lambda note: TRIAGE_NOTE_REGEX.match(note['noteValue'])
        )
        if triage_note:
            note_creation_date = parse(triage_note['createdDate']).astimezone(utc)
            seconds_elapsed_since_last_outage = (current_datetime - note_creation_date).total_seconds()
            return seconds_elapsed_since_last_outage <= max_seconds_since_last_outage

        ticket_creation_datetime = parse(ticket_creation_date, ignoretz=True)
        seconds_elapsed_since_last_outage = (current_datetime - ticket_creation_datetime).total_seconds()
        return seconds_elapsed_since_last_outage <= max_seconds_since_last_outage

    async def _check_for_digi_reboot(self, ticket_id, logical_id_list, serial_number, edge_status, edge_full_id):
        edge_identifier = EdgeIdentifier(**edge_full_id)
        self._logger.info(f'Checking edge {edge_identifier} for DiGi Links')
        digi_links = self._digi_repository.get_digi_links(logical_id_list)

        for digi_link in digi_links:
            link_status = next((link for link in edge_status['links']
                                if link['interface'] == digi_link['interface_name']), None)
            if link_status is not None and self._outage_repository.is_faulty_link(link_status['linkState']):
                reboot = await self._digi_repository.reboot_link(serial_number, ticket_id, digi_link['logical_id'])
                if reboot['status'] in range(200, 300):
                    self._logger.info(f'Attempting DiGi reboot of link with MAC address of {digi_link["logical_id"]}'
                                      f'in edge {edge_identifier}')
                    await self._bruin_repository.append_digi_reboot_note(ticket_id, serial_number,
                                                                         digi_link['interface_name'])
                    slack_message = (
                        f'DiGi reboot started for faulty edge {edge_identifier}. Ticket '
                        f'details at https://app.bruin.com/t/{ticket_id}.'
                    )
                    await self._notifications_repository.send_slack_message(slack_message)

    async def _check_for_failed_digi_reboot(self, ticket_id, logical_id_list, serial_number, edge_status, edge_full_id):
        edge_identifier = EdgeIdentifier(**edge_full_id)
        self._logger.info(f'Checking edge {edge_identifier} for DiGi Links')
        digi_links = self._digi_repository.get_digi_links(logical_id_list)

        for digi_link in digi_links:
            link_status = next((link for link in edge_status['links']
                                if link['interface'] == digi_link['interface_name']), None)
            if link_status is not None and self._outage_repository.is_faulty_link(link_status['linkState']):

                ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
                ticket_details_response_body = ticket_details_response['body']
                ticket_details_response_status = ticket_details_response['status']
                if ticket_details_response_status not in range(200, 300):
                    return

                details_from_ticket = ticket_details_response_body['ticketDetails']
                detail_for_ticket_resolution = self._get_first_element_matching(
                    details_from_ticket,
                    lambda detail: detail['detailValue'] == serial_number,
                )
                ticket_detail_id = detail_for_ticket_resolution['detailID']

                notes_from_outage_ticket = ticket_details_response_body['ticketNotes']
                relevant_notes = [note for note in notes_from_outage_ticket if serial_number in note['serviceNumber']]
                digi_note = self._find_note(relevant_notes, 'DiGi')

                if digi_note is None:
                    self._logger.info(f'No DiGi note was found for ticket {ticket_id}')

                task_result = "Wireless Repair Intervention Needed"
                task_result_note = self._find_note(relevant_notes, 'Wireless Repair Intervention Needed')

                if task_result_note is None:
                    self._logger.info(f'Task results has already been changed to "{task_result}"')

                digi_note_interface_name = self._digi_repository.get_interface_name_from_digi_note(digi_note)

                if digi_note_interface_name == link_status['interface']:
                    self._logger.info(f'Changing task results of ticket_id {ticket_id} to "{task_result}"')
                    await self._bruin_repository.change_detail_work_queue(serial_number, ticket_id, ticket_detail_id,
                                                                          task_result)
                    await self._bruin_repository.append_task_result_change(ticket_id, task_result)
                    return
