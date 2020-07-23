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
                 notifications_repository, triage_repository, metrics_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._outage_repository = outage_repository
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository
        self._notifications_repository = notifications_repository
        self._triage_repository = triage_repository
        self._metrics_repository = metrics_repository

        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['semaphore'])
        self._process_semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['process_semaphore'])
        self._process_errors_semaphore = asyncio.BoundedSemaphore(
            self._config.MONITOR_CONFIG['process_errors_semaphore'])
        self._temp_monitoring_map = []
        self._monitoring_map_cache = []
        self._temp_autoresolve_serials_whitelist = set()
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

    async def _start_build_cache_job(self, exec_on_start):
        self._logger.info('Scheduling build_cache job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('Build_cache job is going to be executed immediately')

        try:
            self._scheduler.add_job(self._build_cache, 'interval',
                                    seconds=self._config.MONITOR_CONFIG['jobs_intervals']['build_cache'],
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_build_cache')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of build_cache job. Reason: {conflict}')

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
        if len(self._monitoring_map_cache) == 0:
            self._logger.info(f"[outage_monitoring_process] Starting initial build of cache and "
                              f"scheduling job to refresh cache every "
                              f"{self._config.MONITOR_CONFIG['jobs_intervals']['build_cache']/3600} hours")
            await self._build_cache()
            await self._start_build_cache_job(exec_on_start=False)

        total_start_time = time.time()
        self._logger.info(f"[outage_monitoring_process] Start with map cache!")

        split_cache = defaultdict(list)
        self._logger.info("[outage_monitoring_process] Splitting cache by host")

        for edge_info in self._monitoring_map_cache:
            split_cache[edge_info['edge_full_id']['host']].append(edge_info)
        self._logger.info('[outage_monitoring_process] Cache split')

        process_tasks = [
            self._process_host_with_cache(host, split_cache[host])
            for host in split_cache
        ]
        start = perf_counter()
        await asyncio.gather(*process_tasks, return_exceptions=True)
        stop = perf_counter()

        self._logger.info(f"[outage_monitoring_process] Elapsed time processing hosts with cache"
                          f": {(stop - start)/60} minutes")

        self._logger.info(f'[outage_monitoring_process] Outage monitoring process finished! Elapsed time:'
                          f'{(time.time() - total_start_time) // 60} minutes')
        self._metrics_repository.set_last_cycle_duration((time.time() - total_start_time) // 60)

    async def _build_cache(self):
        cache_start = perf_counter()
        self._temp_monitoring_map = []
        self._temp_autoresolve_serials_whitelist = set()

        self._logger.info('[build_cache] Building cache...')

        edges_to_monitor_response = await self._velocloud_repository.get_edges_for_outage_monitoring()
        edges_to_monitor_response_body = edges_to_monitor_response['body']
        edges_to_monitor_response_status = edges_to_monitor_response['status']
        if edges_to_monitor_response_status not in range(200, 300):
            return

        # Remove blacklisted
        edges_to_monitor_response_body = [
            edge_full_id
            for edge_full_id in edges_to_monitor_response_body
            if edge_full_id not in self._config.MONITOR_CONFIG['blacklisted_edges']
        ]

        tasks = [
            self._add_edge_to_temp_cache(edge)
            for edge in edges_to_monitor_response_body
        ]
        start = perf_counter()
        await asyncio.gather(*tasks, return_exceptions=True)
        stop = perf_counter()

        self._logger.info(f"[build_cache] Elapsed time building cache of edges for outage monitoring in minutes ....: "
                          f"{(stop - start)/60}")

        self._monitoring_map_cache = self._temp_monitoring_map
        self._autoresolve_serials_whitelist = self._temp_autoresolve_serials_whitelist

        cache_stop = perf_counter()
        self._logger.info(
            f'[build_cache] Create cache finished! Elapsed time: {(cache_stop - cache_start) // 60} minutes'
        )

    async def _process_host_with_cache(self, host, host_cache):
        self._logger.info(f"[process_host_with_cache] {host} starting '_process_edge' task for {len(host_cache)} edges")
        process_tasks = [
            self._process_edge(edge_info['edge_full_id'], edge_info['bruin_client_info'])
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

    async def _add_edge_to_temp_cache(self, edge_full_id):
        edge_identifier = EdgeIdentifier(**edge_full_id)

        @retry(wait=wait_exponential(multiplier=self._config.MONITOR_CONFIG['multiplier'],
                                     min=self._config.MONITOR_CONFIG['min']),
               stop=stop_after_delay(self._config.MONITOR_CONFIG['stop_delay']))
        async def _add_edge_to_temp_cache():
            async with self._semaphore:
                self._logger.info("[add_edge_to_temp_cache] Starting process_edges job")

                edge_status_response = await self._velocloud_repository.get_edge_status(edge_full_id)
                edge_status_response_body = edge_status_response['body']
                edge_status_response_status = edge_status_response['status']
                if edge_status_response_status not in range(200, 300):
                    return

                edge_data = edge_status_response_body["edge_info"]

                edge_serial = edge_data['edges'].get('serialNumber')
                if not edge_serial:
                    self._logger.info(f"[add_edge_to_temp_cache] Edge {edge_identifier} doesn't have "
                                      f"any serial associated. Skipping...")
                    return

                last_contact_moment: str = edge_data['edges']['lastContact']
                if not self._is_valid_last_contact_moment(last_contact_moment):
                    self._logger.info(f'[add_edge_to_temp_cache] Last moment that edge {edge_identifier} was '
                                      f'contacted could not be determined. Skipping...')
                    return

                if not self._was_edge_last_contacted_recently(last_contact_moment):
                    self._logger.info(f'[add_edge_to_temp_cache] Edge {edge_identifier} was contacted for the '
                                      f'last time long time ago. Skipping...')
                    return

                autoresolve_filter = self._config.MONITOR_CONFIG['velocloud_instances_filter'].keys()
                autoresolve_filter_enabled = len(autoresolve_filter) > 0
                if (autoresolve_filter_enabled and edge_full_id['host'] in autoresolve_filter) or \
                        not autoresolve_filter_enabled:
                    self._temp_autoresolve_serials_whitelist.add(edge_serial)

                self._logger.info(f'[add_edge_to_temp_cache] Claiming Bruin client info for serial {edge_serial}...')
                bruin_client_info_response = await self._bruin_repository.get_client_info(edge_serial)
                self._logger.info(f'[add_edge_to_temp_cache] Got Bruin client info for serial {edge_serial} -> '
                                  f'{bruin_client_info_response}')

                bruin_client_info_response_body = bruin_client_info_response['body']
                bruin_client_info_response_status = bruin_client_info_response['status']
                if bruin_client_info_response_status not in range(200, 300):
                    return

                bruin_client_id = bruin_client_info_response_body['client_id']
                if not bruin_client_id:
                    self._logger.info(
                        f"[add_edge_to_temp_cache] Edge {edge_identifier} doesn't have any Bruin client ID associated. "
                        'Skipping...')
                    return

                # Attach Bruin client info to edge_data
                edge_data['bruin_client_info'] = bruin_client_info_response_body

                management_status_response = await self._bruin_repository.get_management_status(
                    bruin_client_id, edge_serial)
                management_status_response_body = management_status_response['body']
                management_status_response_status = management_status_response['status']
                if management_status_response_status not in range(200, 300):
                    return

                if not self._bruin_repository.is_management_status_active(management_status_response_body):
                    self._logger.info(f'Management status is not active for {edge_identifier}. Skipping process...')
                    return
                else:
                    self._logger.info(f'Management status for {edge_identifier} seems active.')

                self._temp_monitoring_map.append({
                    'edge_full_id': edge_full_id,
                    'edge_data': edge_data,
                    'bruin_client_info': bruin_client_info_response_body
                })
        try:
            await _add_edge_to_temp_cache()
        except Exception as ex:
            self._metrics_repository.increment_temp_cache_errors()
            self._logger.error(f"[add_edge_to_temp_cache] Error: {edge_full_id} raised a {ex} exception")

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
            for edge in self._monitoring_map_cache:
                if edge['edge_full_id'] == edge_full_id:
                    serial_number = edge['edge_data']['edges'].get('serialNumber')
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

        working_environment = self._config.MONITOR_CONFIG['environment']
        if working_environment != 'production':
            self._logger.info(f'[ticket-autoresolve] Skipping autoresolve for edge {edge_identifier} since the current '
                              f'environment is {working_environment.upper()}.')
            return

        seconds_ago_for_down_events_lookup = self._config.MONITOR_CONFIG['autoresolve_down_events_seconds']
        timedelta_for_down_events_lookup = datetime.now(utc) - timedelta(seconds=seconds_ago_for_down_events_lookup)
        last_down_events_response = await self._velocloud_repository.get_last_down_edge_events(
            edge_full_id, timedelta_for_down_events_lookup
        )
        last_down_events_body = last_down_events_response['body']
        last_down_events_status = last_down_events_response['status']
        if last_down_events_status not in range(200, 300):
            return

        if not last_down_events_body:
            self._logger.info(f'[ticket-autoresolve] No DOWN events found for edge {edge_identifier} in the '
                              f'last {seconds_ago_for_down_events_lookup / 60} minutes. Skipping autoresolve...')
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

        self._logger.info(f'Autoresolving ticket {outage_ticket_id} linked to edge {edge_identifier} '
                          f' with serial number {serial_number}...')
        resolve_ticket_response = await self._bruin_repository.resolve_ticket(
            outage_ticket_id, detail_for_ticket_resolution['detailID']
        )
        if resolve_ticket_response['status'] not in range(200, 300):
            return

        await self._bruin_repository.append_autoresolve_note_to_ticket(outage_ticket_id, serial_number)

        bruin_client_id = edge_status['bruin_client_info']['client_id']
        await self._notify_successful_autoresolve(outage_ticket_id, bruin_client_id)

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

    async def _notify_successful_autoresolve(self, ticket_id, client_id):
        message = (
            f'Ticket {ticket_id} was autoresolved in {self._config.TRIAGE_CONFIG["environment"].upper()} '
            f'environment. Details at https://app.bruin.com/helpdesk?clientId={client_id}&ticketId={ticket_id}'
        )
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

                    bruin_client_id = bruin_client_info['client_id']
                    slack_message = (
                        f'Outage ticket created for faulty edge {edge_identifier}. Ticket '
                        f'details at https://app.bruin.com/helpdesk?clientId={bruin_client_id}&'
                        f'ticketId={ticket_creation_response_body}.'
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
        self._logger.info(f'Appending triage note to recently created ticket {ticket_id}...')

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

        ticket_note = self._triage_repository.build_triage_note(edge_full_id, edge_status, recent_events_response_body)

        if self._config.TRIAGE_CONFIG['environment'] == 'dev':
            serial_number = edge_status['edges']['serialNumber']
            triage_message = (
                f'Triage note would have been appended to ticket {ticket_id} (serial: {serial_number}).'
                f'Note: {ticket_note}. Details at app.bruin.com/t/{ticket_id}'
            )
            self._logger.info(triage_message)
            await self._notifications_repository.send_slack_message(triage_message)
        elif self._config.TRIAGE_CONFIG['environment'] == 'production':
            append_note_response = await self._bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

            if append_note_response['status'] == 503:
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
            bruin_client_id = edge_status['bruin_client_info']['client_id']
            slack_message = (
                f'Outage ticket {ticket_id} reopened. Ticket details at '
                f'https://app.bruin.com/helpdesk?clientId={bruin_client_id}&ticketId={ticket_id}.'
            )
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

    @staticmethod
    def _is_valid_last_contact_moment(last_contact_moment: str):
        return last_contact_moment != '0000-00-00 00:00:00'

    @staticmethod
    def _was_edge_last_contacted_recently(last_contact_moment: str):
        last_contact_datetime = parse(last_contact_moment).astimezone(utc)
        current_datetime = datetime.now(utc)

        return (current_datetime - last_contact_datetime) <= timedelta(days=7)
