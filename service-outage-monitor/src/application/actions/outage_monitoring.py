import asyncio
import json
import time

from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from time import perf_counter
from typing import Callable

from application.repositories import EdgeIdentifier
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone
from pytz import utc
from tenacity import retry
from tenacity import stop_after_delay
from tenacity import wait_exponential


class OutageMonitor:
    def __init__(self, event_bus, logger, scheduler, config, outage_repository, bruin_repository, velocloud_repository,
                 notifications_repository, triage_repository, customer_cache_repository, metrics_repository):
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

        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['semaphore'])
        self._process_semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['process_semaphore'])
        self._process_errors_semaphore = asyncio.BoundedSemaphore(
            self._config.MONITOR_CONFIG['process_errors_semaphore'])

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

    async def _start_edge_after_error_process(self, edge_full_id, bruin_client_info, run_date: datetime = None):
        self._logger.info('Scheduling process_edge_after_error job...')
        edge_identifier = EdgeIdentifier(**edge_full_id)
        if run_date is None:
            tz = timezone(self._config.MONITOR_CONFIG['timezone'])
            run_date = datetime.now(tz)
        try:
            params = {
                'edge_full_id': edge_full_id,
                'bruin_client_info': bruin_client_info
            }
            self._scheduler.add_job(self._process_edge_after_error, 'date', run_date=run_date,
                                    replace_existing=False, misfire_grace_time=9999,
                                    id=f'_error_process_{json.dumps(edge_full_id)}',
                                    kwargs=params)
        except ConflictingIdError as conflict:
            self._logger.error(f'Job: process_edge_after_error for edge "{edge_identifier}" '
                               f'will not be scheduled. Reason: {conflict}')

    async def _outage_monitoring_process(self):
        self.__reset_state()

        total_start_time = time.time()
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
            self._process_host_with_cache(host, split_cache[host])
            for host in split_cache
        ]
        start = perf_counter()
        await asyncio.gather(*process_tasks, return_exceptions=True)
        stop = perf_counter()

        self._logger.info(f"[outage_monitoring_process] Elapsed time processing hosts with cache"
                          f": {(stop - start) / 60} minutes")

        self._logger.info(f'[outage_monitoring_process] Outage monitoring process finished! Elapsed time:'
                          f'{(time.time() - total_start_time) // 60} minutes')
        self._metrics_repository.set_last_cycle_duration((time.time() - total_start_time) // 60)

    async def _process_host_with_cache(self, host, host_cache):
        self._logger.info(f"[process_host_with_cache] {host} starting '_process_edge' task for {len(host_cache)} edges")
        process_tasks = [
            self._process_edge(edge_info['edge'], edge_info['bruin_client_info'])
            for edge_info in host_cache
        ]
        start = perf_counter()
        await asyncio.gather(*process_tasks, return_exceptions=True)
        stop = perf_counter()

        self._logger.info(f"[process_host_with_cache] Elapsed time processing host - {host} edges in minutes: "
                          f"{(stop - start) // 60}")

    async def _process_edge(self, edge_full_id, bruin_client_info):
        async with self._process_semaphore:
            try:
                edge_identifier = EdgeIdentifier(**edge_full_id)

                edge_status_response = await self._velocloud_repository.get_edge_status(edge_full_id)
                edge_status_response_body = edge_status_response['body']
                edge_status_response_status = edge_status_response['status']
                if edge_status_response_status not in range(200, 300):
                    return

                edge_data = edge_status_response_body["edge_info"]
                # Attach Bruin client info to edge_data
                edge_data['bruin_client_info'] = bruin_client_info

                outage_happened = self._outage_repository.is_there_an_outage(edge_data)
                if outage_happened:
                    self._logger.info(
                        f'[process_edge] Outage detected for {edge_identifier}. '
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
                                                    'bruin_client_info': bruin_client_info
                                                })
                        self._logger.info(f'[process_edge] {edge_identifier} successfully scheduled for re-check.')
                    except ConflictingIdError:
                        self._logger.info(f'There is a recheck job scheduled for {edge_identifier} already. No new job '
                                          'is going to be scheduled.')
                else:
                    self._logger.info(f'[process_edge] {edge_identifier} is in healthy state.')
                    await self._run_ticket_autoresolve_for_edge(edge_full_id, edge_data)

                self._metrics_repository.increment_edges_processed()
            except Exception as ex:
                self._logger.error(f"[process_edge] Error: {ex} processing edge: {edge_full_id}. "
                                   f"Scheduling retries in a separated process...")
                await self._start_edge_after_error_process(edge_full_id, bruin_client_info)

    async def _process_edge_after_error(self, edge_full_id, bruin_client_info):
        @retry(wait=wait_exponential(multiplier=self._config.MONITOR_CONFIG['multiplier'],
                                     min=self._config.MONITOR_CONFIG['min']),
               stop=stop_after_delay(self._config.MONITOR_CONFIG['stop_delay']),
               reraise=True)
        async def _process_edge_after_error():
            async with self._process_errors_semaphore:
                edge_identifier = EdgeIdentifier(**edge_full_id)

                edge_status_response = await self._velocloud_repository.get_edge_status(edge_full_id)
                edge_status_response_body = edge_status_response['body']
                edge_status_response_status = edge_status_response['status']
                if edge_status_response_status not in range(200, 300):
                    return

                edge_data = edge_status_response_body["edge_info"]
                # Attach Bruin client info to edge_data
                edge_data['bruin_client_info'] = bruin_client_info

                outage_happened = self._outage_repository.is_there_an_outage(edge_data)
                if outage_happened:
                    self._logger.info(
                        f'[process_edge_after_error] Outage detected for {edge_identifier}. '
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
                                                    'bruin_client_info': bruin_client_info
                                                })
                        self._logger.info(f'[process_edge_after_error] {edge_identifier} successfully '
                                          f'scheduled for re-check.')
                    except ConflictingIdError:
                        self._logger.info(f'[process_edge_after_error] There is a recheck job scheduled for '
                                          f'{edge_identifier} already. No new job is going to be scheduled.')
                else:
                    self._logger.info(f'[process_edge_after_error] {edge_identifier} is in healthy state.')
                    await self._run_ticket_autoresolve_for_edge(edge_full_id, edge_data)

        try:
            await _process_edge_after_error()
        except Exception as ex:
            self._metrics_repository.increment_retry_errors()

            serial_number = None
            for edge in self._customer_cache:
                if edge['edge'] == edge_full_id:
                    serial_number = edge['serial_number']
            self._logger.error(f"[process_edge_after_error] Maximum retries in process_edge_after_error "
                               f"for edge: ({edge_full_id, bruin_client_info}). Error: {ex}")
            slack_message = f"Maximum retries happened while trying to process edge {edge_full_id} with " \
                            f"serial {serial_number}"
            await self._notifications_repository.send_slack_message(slack_message)

    async def _run_ticket_autoresolve_for_edge(self, edge_full_id, edge_status):
        edge_identifier = EdgeIdentifier(**edge_full_id)
        self._logger.info(f'[ticket-autoresolve] Starting autoresolve for edge {edge_identifier}...')

        serial_number = edge_status['edges']['serialNumber']
        if serial_number not in self._autoresolve_serials_whitelist:
            self._logger.info(f'[ticket-autoresolve] Skipping autoresolve for edge {edge_identifier} because its '
                              f'serial ({serial_number}) is not whitelisted.')
            return

        client_id = edge_status['bruin_client_info']['client_id']
        outage_ticket_response = await self._bruin_repository.get_outage_ticket_details_by_service_number(
            client_id, serial_number
        )
        outage_ticket_response_body = outage_ticket_response['body']
        outage_ticket_response_status = outage_ticket_response['status']
        if outage_ticket_response_status not in range(200, 300):
            return

        if not outage_ticket_response_body:
            self._logger.info(f'[ticket-autoresolve] No outage ticket found for edge {edge_identifier}. '
                              f'Skipping autoresolve...')
            return

        outage_ticket_id = outage_ticket_response_body['ticketID']
        outage_ticket_info = await self._bruin_repository.get_ticket_info(client_id, outage_ticket_id)
        if not outage_ticket_info:
            self._logger.error(f"Can't get creation date for outage ticket {outage_ticket_id}. "
                               f"Can't proceed with autoresolve")
            return

        if not self._can_autoresolve_ticket_by_age(outage_ticket_info):
            return

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

        if self._is_detail_resolved(detail_for_ticket_resolution):
            self._logger.info(f'Ticket {outage_ticket_id} is already resolved. Skipping autoresolve...')
            return

        working_environment = self._config.MONITOR_CONFIG['environment']
        if working_environment != 'production':
            self._logger.info(f'[ticket-autoresolve] Skipping autoresolve for edge {edge_identifier} since the current '
                              f'environment is {working_environment.upper()}.')
            return

        self._logger.info(f'Autoresolving ticket {outage_ticket_id} linked to edge {edge_identifier} '
                          f' with serial number {serial_number}...')
        resolve_ticket_response = await self._bruin_repository.resolve_ticket(
            outage_ticket_id, detail_for_ticket_resolution['detailID']
        )
        if resolve_ticket_response['status'] not in range(200, 300):
            return

        await self._bruin_repository.append_autoresolve_note_to_ticket(outage_ticket_id, serial_number)
        await self._notify_successful_autoresolve(outage_ticket_id)

        self._metrics_repository.increment_tickets_autoresolved()
        self._logger.info(f'Ticket {outage_ticket_id} linked to edge {edge_identifier} was autoresolved!')

    @staticmethod
    def _is_detail_resolved(ticket_detail: dict):
        return ticket_detail['detailStatus'] == 'R'

    @staticmethod
    def _get_first_element_matching(iterable, condition: Callable, fallback=None):
        try:
            return next(elem for elem in iterable if condition(elem))
        except StopIteration:
            return fallback

    async def _notify_successful_autoresolve(self, ticket_id):
        message = f'Outage ticket {ticket_id} was autoresolved. Details at https://app.bruin.com/t/{ticket_id}'
        await self._notifications_repository.send_slack_message(message)

    async def _recheck_edge_for_ticket_creation(self, edge_full_id, bruin_client_info):
        edge_identifier = EdgeIdentifier(**edge_full_id)

        edge_status_response = await self._velocloud_repository.get_edge_status(edge_full_id)
        edge_status_response_body = edge_status_response['body']
        edge_status_response_status = edge_status_response['status']
        if edge_status_response_status not in range(200, 300):
            return

        edge_data = edge_status_response_body["edge_info"]
        edge_data['bruin_client_info'] = bruin_client_info

        is_outage = self._outage_repository.is_there_an_outage(edge_data)
        if is_outage:
            self._logger.info(f'[outage-recheck] Edge {edge_identifier} is still in outage state.')

            working_environment = self._config.MONITOR_CONFIG['environment']
            if working_environment == 'production':
                self._logger.info(
                    f'[outage-recheck] Attempting outage ticket creation for faulty edge {edge_identifier}...'
                )

                serial_number = edge_data['edges']['serialNumber']
                bruin_client_id = bruin_client_info['client_id']
                ticket_creation_response = await self._bruin_repository.create_outage_ticket(
                    bruin_client_id, serial_number
                )
                ticket_creation_response_body = ticket_creation_response['body']
                ticket_creation_response_status = ticket_creation_response['status']
                if ticket_creation_response_status in range(200, 300):
                    self._logger.info(f'Successfully created outage ticket for edge {edge_identifier}.')
                    self._metrics_repository.increment_tickets_created()

                    slack_message = (
                        f'Outage ticket created for faulty edge {edge_identifier}. Ticket '
                        f'details at https://app.bruin.com/t/{ticket_creation_response_body}.'
                    )
                    await self._notifications_repository.send_slack_message(slack_message)
                    await self._append_triage_note(ticket_creation_response_body, edge_full_id, edge_data)
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
                    await self._reopen_outage_ticket(ticket_creation_response_body, edge_data)
            else:
                self._logger.info(
                    f'[outage-recheck] Not starting outage ticket creation for faulty edge {edge_identifier} because '
                    f'the current working environment is {working_environment.upper()}.'
                )
        else:
            self._logger.info(
                f'[outage-recheck] {edge_identifier} seems to be healthy again! No ticket will be created.'
            )
            await self._run_ticket_autoresolve_for_edge(edge_full_id, edge_data)

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
        self._logger.info(f'[outage-ticket-reopening] Reopening outage ticket {ticket_id}...')

        ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
        ticket_details_response_body = ticket_details_response['body']
        ticket_details_response_status = ticket_details_response['status']
        if ticket_details_response_status not in range(200, 300):
            return

        detail_id_for_reopening = ticket_details_response_body['ticketDetails'][0]['detailID']
        ticket_reopening_response = await self._bruin_repository.open_ticket(ticket_id, detail_id_for_reopening)
        ticket_reopening_response_status = ticket_reopening_response['status']

        if ticket_reopening_response_status == 200:
            self._logger.info(f'[outage-ticket-reopening] Outage ticket {ticket_id} reopening succeeded.')
            slack_message = f'Outage ticket {ticket_id} reopened. Ticket details at https://app.bruin.com/t/{ticket_id}'
            await self._notifications_repository.send_slack_message(slack_message)
            await self._post_note_in_outage_ticket(ticket_id, edge_status)

            self._metrics_repository.increment_tickets_reopened()
        else:
            self._logger.error(
                f'[outage-ticket-creation] Outage ticket {ticket_id} reopening failed.'
            )

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

        await self._bruin_repository.append_reopening_note_to_ticket(ticket_id, ticket_note_outage_causes)

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

    def _can_autoresolve_ticket_by_age(self, outage_ticket_info):
        ticket_id = outage_ticket_info["ticketID"]
        outage_ticket_creation_date_utc = datetime.strptime(outage_ticket_info["createDate"], "%m/%d/%Y %I:%M:%S %p")
        now = datetime.utcnow()
        seconds_from_creation = (now - outage_ticket_creation_date_utc).total_seconds()
        max_ticket_age_seconds = self._config.MONITOR_CONFIG['autoresolve_ticket_creation_seconds']
        self._logger.info(f'It has been {int(seconds_from_creation / 60)} minutes '
                          f'since ticket creation for ticket {ticket_id}')

        if seconds_from_creation > max_ticket_age_seconds:
            self._logger.info(f"Ticket age is greater than {int(max_ticket_age_seconds / 60)} minutes "
                              f"for ticket {ticket_id}. Skipping autoresolve...")
            return False
        return True
