import asyncio
import base64
import json
import time
import os
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from ipaddress import ip_address
from time import perf_counter
from typing import List, Pattern, Optional

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone
from pytz import utc
from shortuuid import uuid
from tenacity import retry, wait_exponential, stop_after_delay

from application import Outages, ForwardQueues, ChangeTicketSeverityStatus
from application import TRIAGE_NOTE_REGEX, REOPEN_NOTE_REGEX, REMINDER_NOTE_REGEX, DIGI_NOTE_REGEX
from application import OUTAGE_TYPE_REGEX, LINK_INFO_REGEX


class OutageMonitor:
    def __init__(self, event_bus, logger, scheduler, config, utils_repository, outage_repository, bruin_repository,
                 velocloud_repository, notifications_repository, triage_repository, customer_cache_repository,
                 metrics_repository, digi_repository, ha_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._utils_repository = utils_repository
        self._outage_repository = outage_repository
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository
        self._notifications_repository = notifications_repository
        self._triage_repository = triage_repository
        self._customer_cache_repository = customer_cache_repository
        self._metrics_repository = metrics_repository
        self._digi_repository = digi_repository
        self._ha_repository = ha_repository
        self._cached_edges_without_status = []

        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['semaphore'])

        self.__reset_state()

    def __reset_state(self):
        self._customer_cache = []
        self._autoresolve_serials_whitelist = set()
        self._velocloud_links_by_host = {}

    async def start_service_outage_monitoring(self, exec_on_start):
        self._logger.info('Scheduling Service Outage Monitor job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.TIMEZONE)
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
        serials_for_monitoring = [edge["serial_number"] for edge in self._customer_cache]
        self._logger.info(f"List of serials from customer cache: {serials_for_monitoring}")
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

    async def _process_velocloud_host(self, host, host_cache):
        self._logger.info(f"Processing {len(host_cache)} edges in Velocloud {host}...")
        start = perf_counter()

        links_with_edge_info_response = await self._velocloud_repository.get_links_with_edge_info(velocloud_host=host)
        if links_with_edge_info_response['status'] not in range(200, 300):
            return

        network_enterprises_response = await self._velocloud_repository.get_network_enterprises(velocloud_host=host)
        if network_enterprises_response['status'] not in range(200, 300):
            return

        links_with_edge_info: list = links_with_edge_info_response['body']
        edges_network_enterprises: list = network_enterprises_response['body']

        self._velocloud_links_by_host[host] = links_with_edge_info
        self._logger.info(f"Link status with edge info from Velocloud: {links_with_edge_info}")
        links_grouped_by_edge = self._velocloud_repository.group_links_by_edge(links_with_edge_info)

        self._logger.info(
            'Adding HA info to existing edges, and putting standby edges under monitoring as if they were '
            'standalone edges...'
        )
        edges_with_ha_info = self._ha_repository.map_edges_with_ha_info(
            links_grouped_by_edge, edges_network_enterprises
        )
        all_edges = self._ha_repository.get_edges_with_standbys_as_standalone_edges(edges_with_ha_info)

        serials_with_ha_disabled = [
            edge['edgeSerialNumber']
            for edge in all_edges
            if not self._ha_repository.is_ha_enabled(edge)
        ]
        serials_with_ha_enabled = [
            edge['edgeSerialNumber']
            for edge in all_edges
            if self._ha_repository.is_ha_enabled(edge)
        ]
        primary_serials = [
            edge['edgeSerialNumber']
            for edge in all_edges
            if self._ha_repository.is_ha_primary(edge)
        ]
        standby_serials = [
            edge['edgeSerialNumber']
            for edge in all_edges
            if self._ha_repository.is_ha_standby(edge)
        ]
        self._logger.info(f'Service Outage monitoring is about to check {len(all_edges)} edges')
        self._logger.info(f'{len(serials_with_ha_disabled)} edges have HA disabled: {serials_with_ha_disabled}')
        self._logger.info(f'{len(serials_with_ha_enabled)} edges have HA enabled: {serials_with_ha_enabled}')
        self._logger.info(f'{len(primary_serials)} edges are the primary of a HA pair: {primary_serials}')
        self._logger.info(f'{len(standby_serials)} edges are the standby of a HA pair: {standby_serials}')

        edges_full_info = self._map_cached_edges_with_edges_status(host_cache, all_edges)
        mapped_serials_w_status = [edge["cached_info"]["serial_number"] for edge in edges_full_info]
        self._logger.info(f"Mapped cache serials with status: {mapped_serials_w_status}")

        for outage_type in Outages:
            down_edges = self._outage_repository.filter_edges_by_outage_type(edges_full_info, outage_type)
            self._logger.info(f'{outage_type.value} serials: {[e["status"]["edgeSerialNumber"] for e in down_edges]}')

            relevant_down_edges = [
                edge
                for edge in down_edges
                if self._outage_repository.should_document_outage(edge['status'])
            ]
            self._logger.info(
                f'{outage_type.value} serials that should be documented: '
                f'{[e["status"]["edgeSerialNumber"] for e in relevant_down_edges]}'
            )

            if relevant_down_edges:
                self._logger.info(f"{len(relevant_down_edges)} edges were detected in {outage_type.value} state.")
                edges_with_business_grade_links_down = [
                    edge
                    for edge in relevant_down_edges
                    if outage_type in [Outages.LINK_DOWN, Outages.HA_LINK_DOWN]
                    if self._config.VELOCLOUD_HOST == 'metvco04.mettel.net'
                    if self._has_business_grade_link_down(edge['status']['links'])
                ]
                business_grade_tasks = [
                    self._attempt_ticket_creation(edge, outage_type) for edge in edges_with_business_grade_links_down
                ]
                out = await asyncio.gather(*business_grade_tasks, return_exceptions=True)
                for ex in filter(None, out):
                    self._logger.error(
                        f'[{outage_type.value}] Error while attempting ticket creation(s) for edge '
                        f'with Business Grade Link(s): {ex}')

                regular_edges = [
                    edge
                    for edge in relevant_down_edges
                    if edge not in edges_with_business_grade_links_down
                ]
                self._schedule_recheck_job_for_edges(regular_edges, outage_type)
            else:
                self._logger.info(
                    f"No edges were detected in {outage_type.value} state. "
                    f"No ticket creations will trigger for this outage type"
                )

        healthy_edges = [edge for edge in edges_full_info if self._outage_repository.is_edge_up(edge['status'])]
        self._logger.info(f'Healthy serials: {[e["status"]["edgeSerialNumber"] for e in healthy_edges]}')
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

    def _schedule_recheck_job_for_edges(self, edges: list, outage_type: Outages):
        self._logger.info(f'Scheduling recheck job for {len(edges)} edges in {outage_type.value} state...')

        tz = timezone(self._config.TIMEZONE)
        current_datetime = datetime.now(tz)
        quarantine_time = self._config.MONITOR_CONFIG['quarantine'][outage_type]
        run_date = current_datetime + timedelta(seconds=quarantine_time)

        self._scheduler.add_job(self._recheck_edges_for_ticket_creation, 'date',
                                args=[edges, outage_type],
                                run_date=run_date,
                                replace_existing=False,
                                misfire_grace_time=9999,
                                id=f'{outage_type.value}_ticket_creation_recheck',
                                )

        self._logger.info(f'Edges in {outage_type.value} state scheduled for recheck successfully')

    def _map_cached_edges_with_edges_status(self, customer_cache: list, edges_status: list) -> list:
        result = []
        self._cached_edges_without_status = []

        cached_edges_by_serial = {
            elem['serial_number']: elem
            for elem in customer_cache
        }
        edge_statuses_by_serial = {
            elem['edgeSerialNumber']: elem
            for elem in edges_status
        }

        for serial_number, cached_edge in cached_edges_by_serial.items():
            edge_status = edge_statuses_by_serial.get(serial_number)
            if not edge_status:
                self._logger.info(f'No edge status was found for cached edge {cached_edge["serial_number"]}. '
                                  'Skipping...')
                edge = cached_edge["edge"]
                if edge["host"] == "metvco03.mettel.net" and edge["enterprise_id"] == 124:
                    self._cached_edges_without_status.append(
                        f"<br>https://{edge['host']}/#!/operator/customer/"
                        f"{edge['enterprise_id']}/monitor/edge/{edge['edge_id']}/<br>")
                    self._logger.info(f"Edge {edge} was appended to the list of edges that have no status but"
                                      f"are in the customer cache.")
                continue

            result.append({
                'cached_info': cached_edge,
                'status': edge_status,
            })

        return result

    async def _report_cached_edges_without_status(self):
        working_environment = self._config.CURRENT_ENVIRONMENT
        if len(self._cached_edges_without_status) == 0:
            self._logger.info('No RSI edges were found in customer cache but not in Velocloud response'
                              '. Skipping report...')
            return
        if working_environment != 'production':
            self._logger.info(f'[outage-monitoring] Skipping sending email with edges that are in customer-cache'
                              f'but not in Velocloud response. Current environment is {working_environment}')
            return
        self._logger.info("Sending email with cached edges without status...")
        email_obj = self._format_edges_to_report_for_email()
        response = await self._event_bus.rpc_request("notification.email.request", email_obj, timeout=60)
        self._logger.info(f"Response from sending email: {json.dumps(response)}")

    def _format_edges_to_report_for_email(self):
        string_edges_without_status = "".join(self._cached_edges_without_status)

        # Attachment with VCO03's raw JSON response
        now = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
        host = 'metvco03.mettel.net'
        attachment_filename = f'raw_response_{host}_{now} (UTC).json'
        raw_response = self._velocloud_links_by_host[host]

        return {
            'request_id': uuid(),
            'email_data': {
                'subject': f'Edges present in customer cache that are not returned from velocloud endpoint',
                'recipient': (
                    "ndimuro@mettel.net, bsullivan@mettel.net, mettel.team@intelygenz.com, jsidney@vmware.com, "
                    "webform@vmware.com, jigeshd@vmware.com"
                ),
                'text': 'this is the accessible text for the email',
                'html': f"<br>These are the edges that are present in the customer cache but are not returned from "
                        f"Velocloud's API endpoint: <br>"
                        f"{string_edges_without_status} <br>"
                        "The attachment included in this e-mail is a JSON file with the raw response returned by "
                        f"endpoint https://{host}/portal/rest/monitoring/getEnterpriseEdgeLinkStatus",
                'images': [],
                'attachments': [
                    {
                        'name': attachment_filename,
                        'data': base64.b64encode(json.dumps(raw_response, indent=4).encode('utf-8')).decode('utf-8')
                    },
                ]
            }
        }

    async def _run_ticket_autoresolve_for_edge(self, edge: dict):
        async with self._semaphore:
            cached_edge = edge['cached_info']
            serial_number = cached_edge['serial_number']
            client_id = cached_edge['bruin_client_info']['client_id']
            client_name = cached_edge['bruin_client_info']['client_name']

            self._logger.info(f'[ticket-autoresolve] Starting autoresolve for edge {serial_number}...')

            if serial_number not in self._autoresolve_serials_whitelist:
                self._logger.info(f'[ticket-autoresolve] Skipping autoresolve for edge {serial_number} because its '
                                  f'serial ({serial_number}) is not whitelisted.')
                return

            outage_ticket_response = await self._bruin_repository.get_open_outage_tickets(
                client_id=client_id, service_number=serial_number
            )
            outage_ticket_response_body = outage_ticket_response['body']
            outage_ticket_response_status = outage_ticket_response['status']
            if outage_ticket_response_status not in range(200, 300):
                return

            if not outage_ticket_response_body:
                self._logger.info(f'[ticket-autoresolve] No outage ticket found for edge {serial_number}. '
                                  f'Skipping autoresolve...')
                return

            outage_ticket: dict = outage_ticket_response_body[0]
            outage_ticket_id = outage_ticket['ticketID']
            outage_ticket_creation_date = outage_ticket['createDate']
            outage_ticket_severity = outage_ticket['severity']

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
            detail_for_ticket_resolution = self._utils_repository.get_first_element_matching(
                details_from_ticket,
                lambda detail: detail['detailValue'] == serial_number,
            )
            ticket_detail_id = detail_for_ticket_resolution['detailID']

            notes_from_outage_ticket = ticket_details_response_body['ticketNotes']
            relevant_notes = [
                note
                for note in notes_from_outage_ticket
                if note['serviceNumber'] is not None
                if serial_number in note['serviceNumber']
                if note['noteValue'] is not None
            ]
            if self._is_ticket_task_in_ipa_queue(detail_for_ticket_resolution):
                self._logger.info(
                    f'Task for serial {serial_number} in ticket {outage_ticket_id} is in the IPA Investigate queue. '
                    f'Skipping checks for max auto-resolves and grace period to auto-resolve after last documented '
                    f'outage...'
                )

            else:
                max_seconds_since_last_outage = self._get_max_seconds_since_last_outage(edge)
                was_last_outage_detected_recently = self._has_last_event_happened_recently(
                    ticket_notes=relevant_notes,
                    documentation_cycle_start_date=outage_ticket_creation_date,
                    max_seconds_since_last_event=max_seconds_since_last_outage,
                    note_regex=REOPEN_NOTE_REGEX
                )
                if not was_last_outage_detected_recently:
                    self._logger.info(
                        f'Edge {serial_number} has been in outage state for a long time, so detail {ticket_detail_id} '
                        f'(serial {serial_number}) of ticket {outage_ticket_id} will not be autoresolved. Skipping '
                        f'autoresolve...'
                    )
                    return

                can_detail_be_autoresolved_one_more_time = \
                    self._outage_repository.is_outage_ticket_detail_auto_resolvable(
                        notes_from_outage_ticket,
                        serial_number,
                        max_autoresolves=self._config.MONITOR_CONFIG['autoresolve']['max_autoresolves'],)
                if not can_detail_be_autoresolved_one_more_time:
                    self._logger.info(
                        f'[ticket-autoresolve] Limit to autoresolve detail {ticket_detail_id} (serial {serial_number}) '
                        f'of ticket {outage_ticket_id} linked to edge {serial_number} has been maxed out already. '
                        'Skipping autoresolve...'
                    )
                    return

            if self._is_detail_resolved(detail_for_ticket_resolution):
                self._logger.info(
                    f'Detail {ticket_detail_id} (serial {serial_number}) of ticket {outage_ticket_id} is already '
                    'resolved. Skipping autoresolve...'
                )
                return

            working_environment = self._config.CURRENT_ENVIRONMENT
            if working_environment != 'production':
                self._logger.info(f'[ticket-autoresolve] Skipping autoresolve for edge {serial_number} since the '
                                  f'current environment is {working_environment.upper()}.')
                return

            last_cycle_notes = self._get_notes_appended_since_latest_reopen_or_ticket_creation(relevant_notes)
            triage_note = self._get_triage_or_reopen_note(last_cycle_notes)
            outage_type = self._get_outage_type_from_ticket_notes(last_cycle_notes)
            has_faulty_digi_link = self._get_has_faulty_digi_link_from_ticket_notes(last_cycle_notes, triage_note)
            has_faulty_byob_link = self._get_has_faulty_byob_link_from_triage_note(triage_note)
            faulty_link_types = self._get_faulty_link_types_from_triage_note(triage_note)

            self._logger.info(
                f'Autoresolving detail {ticket_detail_id} of ticket {outage_ticket_id} linked to edge '
                f'{serial_number} with serial number {serial_number}...'
            )
            await self._bruin_repository.unpause_ticket_detail(
                outage_ticket_id,
                service_number=serial_number, detail_id=ticket_detail_id
            )
            resolve_ticket_response = await self._bruin_repository.resolve_ticket(outage_ticket_id, ticket_detail_id)
            if resolve_ticket_response['status'] not in range(200, 300):
                return

            await self._bruin_repository.append_autoresolve_note_to_ticket(outage_ticket_id, serial_number)
            await self._notify_successful_autoresolve(outage_ticket_id)

            self._metrics_repository.increment_tasks_autoresolved(
                client=client_name, outage_type=outage_type, severity=outage_ticket_severity,
                has_digi=has_faulty_digi_link, has_byob=has_faulty_byob_link, link_types=faulty_link_types
            )
            self._logger.info(
                f'Detail {ticket_detail_id} (serial {serial_number}) of ticket {outage_ticket_id} linked to '
                f'edge {serial_number} was autoresolved!'
            )

    def _was_ticket_created_by_automation_engine(self, ticket: dict) -> bool:
        return ticket['createdBy'] == self._config.IPA_SYSTEM_USERNAME_IN_BRUIN

    @staticmethod
    def _is_detail_resolved(ticket_detail: dict):
        return ticket_detail['detailStatus'] == 'R'

    def _find_note(self, ticket_notes, watermark):
        return self._utils_repository.get_first_element_matching(
            iterable=ticket_notes,
            condition=lambda note: watermark in note.get('noteValue'),
            fallback=None
        )

    async def _notify_successful_autoresolve(self, ticket_id):
        message = f'Outage ticket {ticket_id} was autoresolved. Details at https://app.bruin.com/t/{ticket_id}'
        await self._notifications_repository.send_slack_message(message)

    async def _recheck_edges_for_ticket_creation(self, outage_edges: list, outage_type: Outages):
        self._logger.info(
            f'[{outage_type.value}] Re-checking {len(outage_edges)} edges in outage state prior to ticket creation...'
        )
        self._logger.info(f"[{outage_type.value}] Edges in outage before quarantine recheck: {outage_edges}")

        host = self._config.VELOCLOUD_HOST

        links_with_edge_info_response = await self._velocloud_repository.get_links_with_edge_info(velocloud_host=host)
        if links_with_edge_info_response['status'] not in range(200, 300):
            return

        network_enterprises_response = await self._velocloud_repository.get_network_enterprises(velocloud_host=host)
        if network_enterprises_response['status'] not in range(200, 300):
            return

        self._logger.info(f"[{outage_type.value}] Velocloud edge status response in quarantine recheck: "
                          f"{links_with_edge_info_response}")
        links_with_edge_info: list = links_with_edge_info_response['body']
        edges_network_enterprises: list = network_enterprises_response['body']

        links_grouped_by_edge = self._velocloud_repository.group_links_by_edge(links_with_edge_info)

        self._logger.info(
            f'[{outage_type.value}] Adding HA info to existing edges, and putting standby edges under monitoring as if '
            'they were standalone edges...'
        )
        edges_with_ha_info = self._ha_repository.map_edges_with_ha_info(
            links_grouped_by_edge, edges_network_enterprises
        )
        all_edges = self._ha_repository.get_edges_with_standbys_as_standalone_edges(edges_with_ha_info)

        customer_cache_for_outage_edges = [elem['cached_info'] for elem in outage_edges]
        edges_full_info = self._map_cached_edges_with_edges_status(customer_cache_for_outage_edges, all_edges)
        self._logger.info(f"[{outage_type.value}] Current status of edges that were in outage state: {edges_full_info}")

        edges_still_down = self._outage_repository.filter_edges_by_outage_type(edges_full_info, outage_type)
        serials_still_down = [edge['status']['edgeSerialNumber'] for edge in edges_still_down]
        self._logger.info(f"[{outage_type.value}] Edges still in outage state after recheck: {edges_still_down}")
        self._logger.info(f"[{outage_type.value}] Serials still in outage state after recheck: {serials_still_down}")

        healthy_edges = [edge for edge in edges_full_info if self._outage_repository.is_edge_up(edge['status'])]
        healthy_serials = [edge['status']['edgeSerialNumber'] for edge in healthy_edges]
        self._logger.info(f"[{outage_type.value}] Edges that are healthy after recheck: {healthy_edges}")
        self._logger.info(f"[{outage_type.value}] Serials that are healthy after recheck: {healthy_serials}")

        if edges_still_down:
            self._logger.info(
                f"[{outage_type.value}] {len(edges_still_down)} edges are still in outage state after re-check. "
                "Attempting outage ticket creation for all of them..."
            )

            working_environment = self._config.CURRENT_ENVIRONMENT
            if working_environment == 'production':
                tasks = [
                    self._attempt_ticket_creation(edge, outage_type)
                    for edge in edges_still_down
                ]
                out = await asyncio.gather(*tasks, return_exceptions=True)
                for ex in filter(None, out):
                    self._logger.error(
                        f'[{outage_type.value}] Error while attempting ticket creation(s) for edge in '
                        f'the quarantine: {ex}')
            else:
                self._logger.info(
                    f'[{outage_type.value}] Not starting outage ticket creation for {len(edges_still_down)} faulty '
                    f'edges because the current working environment is {working_environment.upper()}.'
                )
        else:
            self._logger.info(f"[{outage_type.value}] No edges were detected in outage state after re-check. "
                              "Outage tickets won't be created")

        if healthy_edges:
            self._logger.info(
                f"[{outage_type.value}] {len(healthy_edges)} edges were detected in healthy state after re-check. '"
                "Running autoresolve for all of them..."
            )
            self._logger.info(
                f"[{outage_type.value}] Edges that are going to be attempted to autoresolve: {healthy_edges}"
            )
            autoresolve_tasks = [self._run_ticket_autoresolve_for_edge(edge) for edge in healthy_edges]
            await asyncio.gather(*autoresolve_tasks)
        else:
            self._logger.info(f"[{outage_type.value}] No edges were detected in healthy state. "
                              "Autoresolve won't be triggered")

        self._logger.info(f'[{outage_type.value}] Re-check process finished for {len(outage_edges)} edges')

    def _get_hnoc_forward_time_by_outage_type(self, outage_type: Outages, edge: dict) -> float:
        if outage_type in [Outages.LINK_DOWN, Outages.HA_LINK_DOWN]:
            max_seconds_since_last_outage = self._get_max_seconds_since_last_outage(edge)
            return max_seconds_since_last_outage / 60
        else:
            return self._config.MONITOR_CONFIG['jobs_intervals']['forward_to_hnoc_edge_down']

    def _should_always_stay_in_ipa_queue(self, link_data: list) -> bool:
        if self._config.VELOCLOUD_HOST == 'metvco04.mettel.net':
            return False
        return self._has_faulty_blacklisted_link(link_data)

    def schedule_forward_to_hnoc_queue(self, forward_time, ticket_id, serial_number, client_name, outage_type, severity,
                                       has_faulty_digi_link, has_faulty_byob_link, faulty_link_types):
        tz = timezone(self._config.TIMEZONE)
        current_datetime = datetime.now(tz)
        forward_task_run_date = current_datetime + timedelta(minutes=forward_time)

        self._logger.info(f"Scheduling HNOC forwarding for ticket_id {ticket_id} and serial {serial_number}"
                          f" to happen at timestamp: {forward_task_run_date}")

        self._scheduler.add_job(
            self.forward_ticket_to_hnoc_queue, 'date',
            kwargs={'ticket_id': ticket_id, 'serial_number': serial_number, 'client_name': client_name,
                    'outage_type': outage_type, 'severity': severity, 'has_faulty_digi_link': has_faulty_digi_link,
                    'has_faulty_byob_link': has_faulty_byob_link, 'faulty_link_types': faulty_link_types},
            run_date=forward_task_run_date,
            replace_existing=True,
            misfire_grace_time=9999,
            coalesce=True,
            id=f'_forward_ticket_{ticket_id}_{serial_number}_to_hnoc',
        )

    async def forward_ticket_to_hnoc_queue(self, ticket_id, serial_number, client_name, outage_type, severity,
                                           has_faulty_digi_link, has_faulty_byob_link, faulty_link_types):
        @retry(wait=wait_exponential(multiplier=self._config.NATS_CONFIG['multiplier'],
                                     min=self._config.NATS_CONFIG['min']),
               stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay']))
        async def forward_ticket_to_hnoc_queue():
            self._logger.info(f'Checking if ticket_id {ticket_id} for serial {serial_number} is resolved before '
                              f'attempting to forward to HNOC...')
            ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)

            if ticket_details_response['status'] not in range(200, 300):
                self._logger.error(f'Getting ticket details of ticket_id {ticket_id} and serial {serial_number} '
                                   f'from Bruin failed: {ticket_details_response}. '
                                   f'Retrying forward to HNOC...')
                raise Exception

            ticket_details = ticket_details_response['body']['ticketDetails']
            most_recent_detail = self._utils_repository.get_first_element_matching(
                ticket_details,
                lambda detail: detail['detailValue'] == serial_number,
            )
            if self._is_detail_resolved(most_recent_detail):
                self._logger.info(f"Ticket id {ticket_id} for serial {serial_number} is resolved. "
                                  f"Skipping forward to HNOC...")
                return
            self._logger.info(f"Ticket id {ticket_id} for serial {serial_number} is not resolved. "
                              f"Forwarding to HNOC...")

            await self.change_detail_work_queue_to_hnoc(
                ticket_id=ticket_id, serial_number=serial_number, client_name=client_name, outage_type=outage_type,
                severity=severity, has_faulty_digi_link=has_faulty_digi_link, has_faulty_byob_link=has_faulty_byob_link,
                faulty_link_types=faulty_link_types
            )

        try:
            await forward_ticket_to_hnoc_queue()
        except Exception as e:
            self._logger.error(
                f"An error occurred while trying to forward ticket_id {ticket_id} for serial {serial_number} to HNOC"
                f" -> {e}"
            )

    async def change_detail_work_queue_to_hnoc(self, ticket_id, serial_number, client_name, outage_type, severity,
                                               has_faulty_digi_link, has_faulty_byob_link, faulty_link_types):
        target_queue = ForwardQueues.HNOC.value
        change_detail_work_queue_response = await self._bruin_repository.change_detail_work_queue(
            serial_number=serial_number,
            ticket_id=ticket_id,
            task_result=target_queue)

        if change_detail_work_queue_response['status'] in range(200, 300):
            self._metrics_repository.increment_tasks_forwarded(
                client=client_name, outage_type=outage_type.value, severity=severity, target_queue=target_queue,
                has_digi=has_faulty_digi_link, has_byob=has_faulty_byob_link, link_types=faulty_link_types
            )
            slack_message = (
                f'Detail of ticket {ticket_id} related to serial {serial_number} was successfully forwarded '
                f'to {target_queue} queue!'
            )
            await self._notifications_repository.send_slack_message(slack_message)
            self._logger.info(f'Successfully forwarded ticket_id {ticket_id} and '
                              f'serial {serial_number} to {target_queue}.')
        else:
            self._logger.error(f'Failed to forward ticket_id {ticket_id} and '
                               f'serial {serial_number} to {target_queue} due to bruin '
                               f'returning {change_detail_work_queue_response} when attempting to forward to HNOC.')

    async def _append_triage_note(self, ticket_id: int, cached_edge: dict, edge_status: dict, outage_type: Outages, *,
                                  is_reopen_note=False):
        edge_full_id = cached_edge['edge']
        serial_number = cached_edge['serial_number']

        past_moment_for_events_lookup = datetime.now(utc) - timedelta(days=7)

        recent_events_response = await self._velocloud_repository.get_last_edge_events(
            edge_full_id, since=past_moment_for_events_lookup
        )

        if recent_events_response['status'] not in range(200, 300):
            return

        recent_events = recent_events_response['body']
        recent_events.sort(key=lambda event: event['eventTime'], reverse=True)

        ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
        if ticket_details_response['status'] not in range(200, 300):
            return

        ticket_detail: dict = ticket_details_response['body']['ticketDetails'][0]
        ticket_detail_id = ticket_detail['detailID']

        ticket_note = self._triage_repository.build_triage_note(
            cached_edge, edge_status, recent_events, outage_type, is_reopen_note=is_reopen_note
        )

        self._logger.info(
            f'Appending triage note to detail {ticket_detail_id} (serial {serial_number}) of ticket {ticket_id}...'
        )
        detail_object = {
            'ticket_id': ticket_id,
            'ticket_detail': ticket_detail,
        }
        await self._bruin_repository.append_triage_note(detail_object, ticket_note)

    async def _reopen_outage_ticket(self, ticket_id: int, edge_status: dict, cached_edge: dict, outage_type: Outages):
        serial_number = edge_status['edgeSerialNumber']
        self._logger.info(f'Reopening outage ticket {ticket_id} for serial {serial_number}...')

        ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
        ticket_details_response_body = ticket_details_response['body']
        ticket_details_response_status = ticket_details_response['status']
        if ticket_details_response_status not in range(200, 300):
            return

        ticket_detail_for_reopen = self._utils_repository.get_first_element_matching(
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
            await self._append_triage_note(ticket_id, cached_edge, edge_status, outage_type, is_reopen_note=True)
            return True
        else:
            self._logger.error(f'Reopening for detail {detail_id_for_reopening} of outage ticket {ticket_id} failed.')
            return False

    async def _check_for_digi_reboot(self, ticket_id, logical_id_list, serial_number, edge_status):
        self._logger.info(f'Checking edge {serial_number} for DiGi Links')
        digi_links = self._digi_repository.get_digi_links(logical_id_list)

        for digi_link in digi_links:
            link_status = next((link for link in edge_status['links']
                                if link['interface'] == digi_link['interface_name']), None)
            if link_status is not None and self._outage_repository.is_faulty_link(link_status['linkState']):
                reboot = await self._digi_repository.reboot_link(serial_number, ticket_id, digi_link['logical_id'])
                if reboot['status'] in range(200, 300):
                    self._logger.info(f'Attempting DiGi reboot of link with MAC address of {digi_link["logical_id"]}'
                                      f'in edge {serial_number}')
                    await self._bruin_repository.append_digi_reboot_note(ticket_id, serial_number,
                                                                         digi_link['interface_name'])
                    slack_message = (
                        f'DiGi reboot started for faulty edge {serial_number}. Ticket '
                        f'details at https://app.bruin.com/t/{ticket_id}.'
                    )
                    await self._notifications_repository.send_slack_message(slack_message)

    async def _check_for_failed_digi_reboot(self, ticket_id, logical_id_list, serial_number, edge_status, client_name,
                                            outage_type, severity, has_faulty_digi_link, has_faulty_byob_link,
                                            faulty_link_types):
        if self._outage_repository.is_faulty_edge(edge_status["edgeState"]):
            return
        self._logger.info(f'Checking edge {serial_number} for DiGi Links')
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
                detail_for_ticket_resolution = self._utils_repository.get_first_element_matching(
                    details_from_ticket,
                    lambda detail: detail['detailValue'] == serial_number,
                )
                ticket_detail_id = detail_for_ticket_resolution['detailID']

                notes_from_outage_ticket = ticket_details_response_body['ticketNotes']
                self._logger.info(f'Notes of ticket {ticket_id}: {notes_from_outage_ticket}')

                relevant_notes = [
                    note
                    for note in notes_from_outage_ticket
                    if note['serviceNumber'] is not None
                    if serial_number in note['serviceNumber']
                    if note['noteValue'] is not None
                ]
                digi_note = self._find_note(relevant_notes, 'DiGi')

                if digi_note is None:
                    self._logger.info(f'No DiGi note was found for ticket {ticket_id}')
                    return
                if self._was_digi_rebooted_recently(digi_note):
                    self._logger.info(
                        f'The last DiGi reboot attempt for Edge {serial_number} did not occur '
                        f'{self._config.MONITOR_CONFIG["last_digi_reboot_seconds"] / 60} or more mins ago.'
                    )
                    return

                digi_note_interface_name = self._digi_repository.get_interface_name_from_digi_note(digi_note)

                if digi_note_interface_name == link_status['interface']:
                    target_queue = ForwardQueues.WIRELESS.value
                    task_result_note = self._find_note(relevant_notes, target_queue)

                    if task_result_note is not None:
                        self._logger.info(f'Task results has already been changed to "{target_queue}"')
                        return
                    self._logger.info(f'DiGi reboot attempt failed. Forwarding ticket {ticket_id} to Wireless team')
                    change_detail_work_queue_response = await self._bruin_repository.change_detail_work_queue(
                        ticket_id, target_queue, serial_number=serial_number, detail_id=ticket_detail_id)
                    if change_detail_work_queue_response['status'] in range(200, 300):
                        self._metrics_repository.increment_tasks_forwarded(
                            client=client_name, outage_type=outage_type.value, severity=severity,
                            target_queue=target_queue, has_digi=has_faulty_digi_link, has_byob=has_faulty_byob_link,
                            link_types=faulty_link_types
                        )
                        await self._bruin_repository.append_task_result_change_note(ticket_id, target_queue)
                        slack_message = f'Forwarding ticket {ticket_id} to Wireless team'
                        await self._notifications_repository.send_slack_message(slack_message)
                        return
                else:
                    reboot = await self._digi_repository.reboot_link(serial_number, ticket_id, digi_link['logical_id'])
                    if reboot['status'] in range(200, 300):
                        self._logger.info(
                            f'Attempting DiGi reboot of link with MAC address of {digi_link["logical_id"]}'
                            f'in edge {serial_number}')
                        await self._bruin_repository.append_digi_reboot_note(ticket_id, serial_number,
                                                                             digi_link['interface_name'])
                        slack_message = (
                            f'DiGi reboot started for faulty edge {serial_number}. Ticket '
                            f'details at https://app.bruin.com/t/{ticket_id}.'
                        )
                        await self._notifications_repository.send_slack_message(slack_message)
                        return

    async def _attempt_forward_to_asr(self, cached_edge, edge_status, ticket_id, client_name, outage_type, severity,
                                      has_faulty_digi_link, has_faulty_byob_link, faulty_link_types):
        serial_number = cached_edge['serial_number']
        self._logger.info(
            f'Attempting to forward task of ticket {ticket_id} related to serial {serial_number} to ASR Investigate...'
        )

        links_configuration = cached_edge['links_configuration']
        if self._outage_repository.is_faulty_edge(edge_status["edgeState"]):
            self._logger.info(
                f'Outage of serial {serial_number} is caused by a faulty edge. Related detail of ticket {ticket_id} '
                'will not be forwarded to ASR Investigate.'
            )
            return

        self._logger.info(f'Searching serial {serial_number} for any wired links')
        links_wired = self._outage_repository.find_disconnected_wired_links(edge_status, links_configuration)
        if not links_wired:
            self._logger.info(
                f'No wired links are disconnected for serial {serial_number}. Related detail of ticket {ticket_id} '
                'will not be forwarded to ASR Investigate.'
            )
            return

        self._logger.info(f'Filtering out any of the wired links of serial {serial_number} that contains any of the '
                          f'following: {self._config.MONITOR_CONFIG["blacklisted_link_labels_for_asr_forwards"]} '
                          f'in the link label')
        whitelisted_links = self._find_whitelisted_links_for_asr_forward(links_wired)
        if not whitelisted_links:
            self._logger.info(
                f'No links with whitelisted labels were found for serial {serial_number}. '
                f'Related detail of ticket {ticket_id} will not be forwarded to ASR Investigate.'
            )
            return

        ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
        ticket_details_response_body = ticket_details_response['body']
        ticket_details_response_status = ticket_details_response['status']
        if ticket_details_response_status not in range(200, 300):
            return

        details_from_ticket = ticket_details_response_body['ticketDetails']
        detail_for_ticket_resolution = self._utils_repository.get_first_element_matching(
            details_from_ticket,
            lambda detail: detail['detailValue'] == serial_number,
        )
        ticket_detail_id = detail_for_ticket_resolution['detailID']

        notes_from_outage_ticket = ticket_details_response_body['ticketNotes']
        self._logger.info(f'Notes of ticket {ticket_id}: {notes_from_outage_ticket}')

        relevant_notes = [
            note
            for note in notes_from_outage_ticket
            if note['serviceNumber'] is not None
            if serial_number in note['serviceNumber']
            if note['noteValue'] is not None
        ]

        target_queue = "No Trouble Found - Carrier Issue"
        task_result_note = self._find_note(relevant_notes, ForwardQueues.ASR.value)

        if task_result_note is not None:
            self._logger.info(
                f'Detail related to serial {serial_number} of ticket {ticket_id} has already been forwarded to '
                f'"{target_queue}"'
            )
            return

        change_detail_work_queue_response = await self._bruin_repository.change_detail_work_queue(
            ticket_id, target_queue, serial_number=serial_number, detail_id=ticket_detail_id)
        if change_detail_work_queue_response['status'] in range(200, 300):
            self._metrics_repository.increment_tasks_forwarded(
                client=client_name, outage_type=outage_type.value, severity=severity,
                target_queue=ForwardQueues.ASR.value, has_digi=has_faulty_digi_link, has_byob=has_faulty_byob_link,
                link_types=faulty_link_types
            )
            await self._bruin_repository.append_asr_forwarding_note(ticket_id, whitelisted_links, serial_number)
            slack_message = (
                f'Detail of ticket {ticket_id} related to serial {serial_number} was successfully forwarded '
                f'to {target_queue} queue!'
            )
            await self._notifications_repository.send_slack_message(slack_message)

    def _is_link_label_an_ip(self, link_label: str):
        try:
            return bool(ip_address(link_label))
        except ValueError:
            return False

    def _is_link_label_black_listed(self, link_label: str):
        blacklisted_link_labels = self._config.MONITOR_CONFIG["blacklisted_link_labels_for_asr_forwards"]
        return any(label for label in blacklisted_link_labels if label in link_label)

    def _is_link_label_black_listed_from_hnoc(self, link_label: str):
        blacklisted_link_labels = self._config.MONITOR_CONFIG["blacklisted_link_labels_for_hnoc_forwards"]
        return any(label for label in blacklisted_link_labels if label.lower() in link_label)

    def _find_whitelisted_links_for_asr_forward(self, links: list) -> list:
        return [
            link
            for link in links
            if self._is_link_label_black_listed(link['displayName']) is False
            if self._is_link_label_an_ip(link['displayName']) is False
        ]

    def _has_faulty_digi_link(self, links: List[dict], logical_id_list: List[dict]) -> bool:
        digi_links = self._digi_repository.get_digi_links(logical_id_list)
        digi_interfaces = [link['interface_name'] for link in digi_links]

        return any(
            link for link in links
            if link['interface'] in digi_interfaces
            if self._outage_repository.is_faulty_link(link['linkState'])
        )

    def _has_faulty_blacklisted_link(self, links: List[dict]) -> bool:
        return any(
            link for link in links
            if link['displayName'] and self._is_link_label_black_listed_from_hnoc(link['displayName'].lower())
            if self._outage_repository.is_faulty_link(link['linkState'])
        )

    def _get_faulty_link_types(self, links: List[dict], links_configuration: List[dict]) -> List[str]:
        return list({
            self._outage_repository.get_link_type(link, links_configuration) for link in links
            if self._outage_repository.is_faulty_link(link['linkState'])
        })

    def _was_digi_rebooted_recently(self, ticket_note) -> bool:
        current_datetime = datetime.now(utc)
        max_seconds_since_last_outage = self._config.MONITOR_CONFIG['last_digi_reboot_seconds']

        note_creation_date = parse(ticket_note['createdDate']).astimezone(utc)
        seconds_elapsed_since_last_outage = (current_datetime - note_creation_date).total_seconds()
        return seconds_elapsed_since_last_outage < max_seconds_since_last_outage

    def _is_ticket_old_enough(self, ticket_creation_date: str) -> bool:
        current_datetime = datetime.now().astimezone(utc)
        max_seconds_since_creation = self._config.MONITOR_CONFIG['forward_link_outage_seconds']

        ticket_creation_datetime = parse(ticket_creation_date).replace(tzinfo=utc)
        seconds_elapsed_since_creation = (current_datetime - ticket_creation_datetime).total_seconds()

        return seconds_elapsed_since_creation >= max_seconds_since_creation

    def _get_target_severity(self, edge_status: dict):
        if self._outage_repository.is_faulty_edge(edge_status['edgeState']):
            return self._config.MONITOR_CONFIG['severity_by_outage_type']['edge_down']
        else:
            return self._config.MONITOR_CONFIG['severity_by_outage_type']['link_down']

    async def _change_ticket_severity(self, ticket_id: int, edge_status: dict, target_severity: int, *,
                                      check_ticket_tasks: bool) -> ChangeTicketSeverityStatus:
        self._logger.info(f'Attempting to change severity level of ticket {ticket_id}...')

        serial_number = edge_status['edgeSerialNumber']

        if self._outage_repository.is_faulty_edge(edge_status['edgeState']):
            self._logger.info(
                f'Severity level of ticket {ticket_id} is about to be changed, as the root cause of the outage issue '
                f'is that edge {serial_number} is offline.'
            )
            change_severity_task = self._bruin_repository.change_ticket_severity_for_offline_edge(ticket_id)
        else:
            if check_ticket_tasks:
                ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
                if ticket_details_response['status'] not in range(200, 300):
                    return ChangeTicketSeverityStatus.NOT_CHANGED

                ticket_tasks = ticket_details_response['body']['ticketDetails']
                if self._has_ticket_multiple_unresolved_tasks(ticket_tasks):
                    self._logger.info(
                        f'Severity level of ticket {ticket_id} will remain the same, as the root cause of the outage '
                        f'issue is that at least one link of edge {serial_number} is disconnected, and this ticket '
                        f'has multiple unresolved tasks.'
                    )
                    return ChangeTicketSeverityStatus.NOT_CHANGED

            self._logger.info(
                f'Severity level of ticket {ticket_id} is about to be changed, as the root cause of the outage issue '
                f'is that at least one link of edge {serial_number} is disconnected, and this ticket has a single '
                'unresolved task.'
            )
            disconnected_links = self._outage_repository.find_disconnected_links(edge_status['links'])
            disconnected_interfaces = [link['interface'] for link in disconnected_links]

            change_severity_task = self._bruin_repository.change_ticket_severity_for_disconnected_links(
                ticket_id, disconnected_interfaces
            )

        get_ticket_response = await self._bruin_repository.get_ticket(ticket_id)
        if not get_ticket_response['status'] in range(200, 300):
            change_severity_task.close()
            return ChangeTicketSeverityStatus.NOT_CHANGED

        ticket_info = get_ticket_response['body']
        if self._is_ticket_already_in_severity_level(ticket_info, target_severity):
            self._logger.info(
                f'Ticket {ticket_id} is already in severity level {target_severity}, so there is no need '
                'to change it.'
            )
            change_severity_task.close()
            return ChangeTicketSeverityStatus.NOT_CHANGED

        result = await change_severity_task
        if result['status'] not in range(200, 300):
            return ChangeTicketSeverityStatus.NOT_CHANGED

        if target_severity == self._config.MONITOR_CONFIG['severity_by_outage_type']['link_down']:
            change_severity_status = ChangeTicketSeverityStatus.CHANGED_TO_LINK_DOWN_SEVERITY
        else:
            change_severity_status = ChangeTicketSeverityStatus.CHANGED_TO_EDGE_DOWN_SEVERITY

        self._logger.info(f'Finished changing severity level of ticket {ticket_id} to {target_severity}!')
        return change_severity_status

    def _has_ticket_multiple_unresolved_tasks(self, ticket_tasks: list) -> bool:
        unresolved_tasks = [task for task in ticket_tasks if not self._is_detail_resolved(task)]
        return len(unresolved_tasks) > 1

    @staticmethod
    def _is_ticket_already_in_severity_level(ticket_info: dict, severity_level: int) -> bool:
        return ticket_info['severity'] == severity_level

    @staticmethod
    def _is_ticket_task_in_ipa_queue(ticket_task: dict) -> bool:
        return ticket_task['currentTaskName'] == 'IPA Investigate'

    def _get_max_seconds_since_last_outage(self, edge: dict) -> int:
        from datetime import timezone

        tz_offset = edge['cached_info']['site_details']['tzOffset']
        tz = timezone(timedelta(hours=tz_offset))
        now = datetime.now(tz=tz)

        last_outage_seconds = self._config.MONITOR_CONFIG['autoresolve']['last_outage_seconds']
        day_schedule = self._config.MONITOR_CONFIG['autoresolve']['day_schedule']
        day_start_hour = day_schedule['start_hour']
        day_end_hour = day_schedule['end_hour']

        if day_start_hour >= day_end_hour:
            day_end_hour += 24

        if day_start_hour <= now.hour < day_end_hour:
            return last_outage_seconds['day']
        else:
            return last_outage_seconds['night']

    def _get_notes_appended_since_latest_reopen_or_ticket_creation(self, ticket_notes: List[dict]) -> List[dict]:
        sorted_ticket_notes = sorted(ticket_notes, key=lambda note: note['createdDate'])
        latest_reopen = self._utils_repository.get_last_element_matching(
            sorted_ticket_notes,
            lambda note: REOPEN_NOTE_REGEX.search(note['noteValue'])
        )

        if not latest_reopen:
            # If there's no re-open, all notes in the ticket are the ones posted since the last outage
            return ticket_notes

        latest_reopen_position = ticket_notes.index(latest_reopen)
        return ticket_notes[latest_reopen_position:]

    def _get_triage_or_reopen_note(self, ticket_notes: List[dict]) -> Optional[dict]:
        return self._utils_repository.get_first_element_matching(
            ticket_notes,
            lambda note: TRIAGE_NOTE_REGEX.match(note['noteValue']) or REOPEN_NOTE_REGEX.match(note['noteValue'])
        )

    @staticmethod
    def _get_outage_type_from_ticket_notes(ticket_notes: List[dict]) -> Optional[str]:
        for note in ticket_notes:
            match = OUTAGE_TYPE_REGEX.search(note['noteValue'])
            if match:
                return match.group('outage_type')

    def _get_has_faulty_digi_link_from_ticket_notes(self, ticket_notes: List[dict],
                                                    triage_note: Optional[dict]) -> Optional[bool]:
        if not triage_note:
            return None

        digi_interfaces = set()

        for note in ticket_notes:
            match = DIGI_NOTE_REGEX.search(note['noteValue'])
            if match:
                interface = match.group('interface')
                digi_interfaces.add(interface)

        matches = LINK_INFO_REGEX.finditer(triage_note['noteValue'])

        for match in matches:
            link_interface = match.group('interface')
            link_status = match.group('status')

            if self._outage_repository.is_faulty_link(link_status):
                if link_interface in digi_interfaces:
                    return True

        return False

    def _get_has_faulty_byob_link_from_triage_note(self, triage_note: Optional[dict]) -> Optional[bool]:
        if not triage_note:
            return None

        matches = LINK_INFO_REGEX.finditer(triage_note['noteValue'])

        for match in matches:
            link_label = match.group('label')
            link_status = match.group('status')

            if self._outage_repository.is_faulty_link(link_status):
                if self._is_link_label_black_listed_from_hnoc(link_label):
                    return True

        return False

    def _get_faulty_link_types_from_triage_note(self, triage_note: Optional[dict]) -> List[str]:
        if not triage_note:
            return []

        link_types = set()
        matches = LINK_INFO_REGEX.finditer(triage_note['noteValue'])

        for match in matches:
            link_type = match.group('type')
            link_status = match.group('status')

            if self._outage_repository.is_faulty_link(link_status):
                link_types.add(link_type)

        return list(link_types)

    def _has_last_event_happened_recently(self, ticket_notes: list, documentation_cycle_start_date: str,
                                          max_seconds_since_last_event: int, note_regex: Pattern[str]) -> bool:
        current_datetime = datetime.now(utc)

        notes_sorted_by_date_asc = sorted(ticket_notes, key=lambda note: note['createdDate'])
        last_event_note = self._utils_repository.get_last_element_matching(
            notes_sorted_by_date_asc,
            lambda note: note_regex.match(note['noteValue'])
        )
        if last_event_note:
            note_creation_date = parse(last_event_note['createdDate']).astimezone(utc)
            seconds_elapsed_since_last_event = (current_datetime - note_creation_date).total_seconds()
            return seconds_elapsed_since_last_event <= max_seconds_since_last_event

        documentation_cycle_start_datetime = parse(documentation_cycle_start_date).replace(tzinfo=utc)
        seconds_elapsed_since_last_event = (current_datetime - documentation_cycle_start_datetime).total_seconds()
        return seconds_elapsed_since_last_event <= max_seconds_since_last_event

    async def _send_reminder(self, ticket_id: str, service_number: str, ticket_notes: list):
        self._logger.info(
            f'Attempting to send reminder for service number {service_number} to ticket {ticket_id}'
        )

        filtered_notes = self._get_notes_appended_since_latest_reopen_or_ticket_creation(ticket_notes)
        last_documentation_cycle_start_date = filtered_notes[0]['createdDate']

        max_seconds_since_last_reminder = self._config.MONITOR_CONFIG['wait_time_before_sending_new_milestone_reminder']
        should_send_reminder_notification = not self._has_last_event_happened_recently(
            ticket_notes=filtered_notes,
            documentation_cycle_start_date=last_documentation_cycle_start_date,
            max_seconds_since_last_event=max_seconds_since_last_reminder,
            note_regex=REMINDER_NOTE_REGEX,
        )
        if not should_send_reminder_notification:
            self._logger.info(
                f'No Reminder note will be appended for service number {service_number} to ticket {ticket_id},'
                f' since either the last documentation cycle started or the last reminder'
                f' was sent too recently'
            )
            return

        working_environment = self._config.CURRENT_ENVIRONMENT
        if not working_environment == 'production':
            self._logger.info(
                f'No Reminder note will be appended for service number {service_number} to ticket {ticket_id} since '
                f'the current environment is {working_environment.upper()}'
            )
            return

        email_response = await self._bruin_repository.send_reminder_email_milestone_notification(
            ticket_id,
            service_number
        )
        if email_response['status'] not in range(200, 300):
            self._logger.error(
                f'Reminder email of edge {service_number} could not be sent for ticket'
                f' {ticket_id}!'
            )
            return

        append_note_response = await self._append_reminder_note(ticket_id, service_number)
        if append_note_response['status'] not in range(200, 300):
            self._logger.error(
                f'Reminder note of edge {service_number} could not be appended to ticket'
                f' {ticket_id}!'
            )
            return

        self._logger.info(
            f'Reminder note of edge {service_number} was successfully appended to ticket'
            f' {ticket_id}!'
        )
        await self._notifications_repository.notify_successful_reminder_note_append(
            ticket_id,
            service_number
        )

    async def _append_reminder_note(self, ticket_id: int, service_number: str):
        note_lines = [
            "#*MetTel's IPA*#",
            'Client Reminder'
        ]
        reminder_note = os.linesep.join(note_lines)

        return await self._bruin_repository.append_note_to_ticket(
            ticket_id,
            reminder_note,
            service_numbers=[service_number],
        )

    async def _attempt_ticket_creation(self, edge: dict, outage_type: Outages):
        edge_status = edge['status']
        edge_links = edge_status['links']
        cached_edge = edge['cached_info']
        serial_number = cached_edge['serial_number']
        logical_id_list = cached_edge['logical_ids']
        links_configuration = cached_edge['links_configuration']
        client_id = cached_edge['bruin_client_info']['client_id']
        client_name = cached_edge['bruin_client_info']['client_name']
        target_severity = self._get_target_severity(edge_status)
        has_faulty_digi_link = self._has_faulty_digi_link(edge_links, logical_id_list)
        has_faulty_byob_link = self._has_faulty_blacklisted_link(edge_links)
        faulty_link_types = self._get_faulty_link_types(edge_links, links_configuration)

        self._logger.info(
            f'[{outage_type.value}] Attempting outage ticket creation for serial {serial_number}...'
        )

        try:
            ticket_creation_response = await self._bruin_repository.create_outage_ticket(
                client_id, serial_number
            )
            ticket_id = ticket_creation_response['body']
            ticket_creation_response_status = ticket_creation_response['status']
            self._logger.info(f"[{outage_type.value}] Bruin response for ticket creation for edge {edge}: "
                              f"{ticket_creation_response}")
            if ticket_creation_response_status in range(200, 300):
                self._logger.info(f'[{outage_type.value}] Successfully created outage ticket for edge {edge}.')
                self._metrics_repository.increment_tasks_created(
                    client=client_name, outage_type=outage_type.value, severity=target_severity,
                    has_digi=has_faulty_digi_link, has_byob=has_faulty_byob_link, link_types=faulty_link_types
                )
                slack_message = (
                    f'Service Outage ticket created for edge {serial_number} in {outage_type.value} state: '
                    f'https://app.bruin.com/t/{ticket_id}.'
                )
                await self._notifications_repository.send_slack_message(slack_message)
                await self._append_triage_note(
                    ticket_id, cached_edge, edge_status, outage_type
                )
                await self._change_ticket_severity(
                    ticket_id=ticket_id,
                    edge_status=edge_status,
                    target_severity=target_severity,
                    check_ticket_tasks=False,
                )

                should_schedule_hnoc_forwarding = not self._should_always_stay_in_ipa_queue(edge_links)
                forward_time = self._get_hnoc_forward_time_by_outage_type(outage_type, edge)

                if should_schedule_hnoc_forwarding:
                    self.schedule_forward_to_hnoc_queue(
                        forward_time, ticket_id, serial_number, client_name, outage_type,
                        target_severity, has_faulty_digi_link, has_faulty_byob_link, faulty_link_types
                    )
                else:
                    self._logger.info(f"Ticket_id: {ticket_id} for serial: {serial_number} "
                                      f"with link_data: {edge_links} has a blacklisted link and "
                                      f"should not be forwarded to HNOC. Skipping forward to HNOC...")

                    self._logger.info(f"Sending an email for ticket_id: {ticket_id} "
                                      f"with serial: {serial_number} instead of scheduling forward to HNOC...")
                    email_response = await self._bruin_repository.send_initial_email_milestone_notification(
                        ticket_id,
                        serial_number
                    )
                    if email_response['status'] not in range(200, 300):
                        self._logger.error(
                            f'Reminder email of edge {serial_number} could not be sent for ticket'
                            f' {ticket_id}!'
                        )
                    else:
                        append_note_response = await self._append_reminder_note(ticket_id, serial_number)
                        if append_note_response['status'] not in range(200, 300):
                            self._logger.error(
                                f'Reminder note of edge {serial_number} could not be appended to ticket'
                                f' {ticket_id}!'
                            )

                await self._check_for_digi_reboot(ticket_id, logical_id_list, serial_number, edge_status)
            elif ticket_creation_response_status == 409:
                self._logger.info(
                    f'[{outage_type.value}] Faulty edge {serial_number} already has an outage ticket in '
                    f'progress (ID = {ticket_id}). Skipping outage ticket creation for '
                    'this edge...'
                )
                change_severity_result = await self._change_ticket_severity(
                    ticket_id=ticket_id,
                    edge_status=edge_status,
                    target_severity=target_severity,
                    check_ticket_tasks=True,
                )

                should_schedule_hnoc_forwarding = not self._should_always_stay_in_ipa_queue(edge_links)

                if change_severity_result is not ChangeTicketSeverityStatus.NOT_CHANGED:
                    if should_schedule_hnoc_forwarding:
                        forward_time = self._get_hnoc_forward_time_by_outage_type(outage_type, edge)
                        self.schedule_forward_to_hnoc_queue(
                            forward_time, ticket_id, serial_number, client_name,
                            outage_type, target_severity, has_faulty_digi_link, has_faulty_byob_link,
                            faulty_link_types
                        )
                    else:
                        self._logger.info(
                            f"Ticket_id: {ticket_id} for serial: {serial_number} "
                            f"with link_data: {edge_links} has a blacklisted link and "
                            f"should not be forwarded to HNOC. Skipping forward to HNOC...")
                        ticket_details = await self._bruin_repository.get_ticket_details(ticket_id)
                        ticket_notes = ticket_details['body']['ticketNotes']
                        await self._send_reminder(
                            ticket_id=ticket_id,
                            service_number=serial_number,
                            ticket_notes=ticket_notes
                        )
                await self._check_for_failed_digi_reboot(
                    ticket_id, logical_id_list, serial_number, edge_status, client_name,
                    outage_type, target_severity, has_faulty_digi_link, has_faulty_byob_link, faulty_link_types
                )
                await self._attempt_forward_to_asr(
                    cached_edge, edge_status, ticket_id, client_name, outage_type,
                    target_severity, has_faulty_digi_link, has_faulty_byob_link, faulty_link_types
                )
            elif ticket_creation_response_status == 471:
                self._logger.info(
                    f'[{outage_type.value}] Faulty edge {serial_number} has a resolved outage ticket '
                    f'(ID = {ticket_id}). Re-opening ticket...'
                )
                was_ticket_reopened = await self._reopen_outage_ticket(
                    ticket_id, edge_status, cached_edge, outage_type
                )
                if was_ticket_reopened:
                    self._metrics_repository.increment_tasks_reopened(
                        client=client_name, outage_type=outage_type.value, severity=target_severity,
                        has_digi=has_faulty_digi_link, has_byob=has_faulty_byob_link,
                        link_types=faulty_link_types
                    )

                await self._change_ticket_severity(
                    ticket_id=ticket_id,
                    edge_status=edge_status,
                    target_severity=target_severity,
                    check_ticket_tasks=True,
                )

                should_schedule_hnoc_forwarding = not self._should_always_stay_in_ipa_queue(edge_links)
                forward_time = self._get_hnoc_forward_time_by_outage_type(outage_type, edge)

                if should_schedule_hnoc_forwarding:
                    self.schedule_forward_to_hnoc_queue(
                        forward_time, ticket_id, serial_number, client_name, outage_type,
                        target_severity, has_faulty_digi_link, has_faulty_byob_link, faulty_link_types
                    )
                else:
                    self._logger.info(f"Ticket_id: {ticket_id} for serial: {serial_number} "
                                      f"with link_data: {edge_links} has a blacklisted link and "
                                      f"should not be forwarded to HNOC. Skipping forward to HNOC...")

                    self._logger.info(f"Sending an email for ticket_id: {ticket_id} "
                                      f"with serial: {serial_number} instead of scheduling forward to HNOC...")
                    email_response = await self._bruin_repository.send_initial_email_milestone_notification(
                        ticket_id,
                        serial_number
                    )
                    if email_response['status'] not in range(200, 300):
                        self._logger.error(
                            f'Reminder email of edge {serial_number} could not be sent for ticket'
                            f' {ticket_id}!'
                        )
                    else:
                        append_note_response = await self._append_reminder_note(ticket_id, serial_number)
                        if append_note_response['status'] not in range(200, 300):
                            self._logger.error(
                                f'Reminder note of edge {serial_number} could not be appended to ticket'
                                f' {ticket_id}!'
                            )

                await self._check_for_digi_reboot(ticket_id, logical_id_list, serial_number, edge_status)
            elif ticket_creation_response_status == 472:
                self._logger.info(
                    f'[{outage_type.value}] Faulty edge {serial_number} has a resolved outage ticket '
                    f'(ID = {ticket_id}). Its ticket detail was automatically unresolved '
                    f'by Bruin. Appending reopen note to ticket...'
                )
                self._metrics_repository.increment_tasks_reopened(
                    client=client_name, outage_type=outage_type.value, severity=target_severity,
                    has_digi=has_faulty_digi_link, has_byob=has_faulty_byob_link, link_types=faulty_link_types
                )

                await self._append_triage_note(
                    ticket_id,
                    cached_edge,
                    edge_status,
                    outage_type,
                    is_reopen_note=True,
                )
                await self._change_ticket_severity(
                    ticket_id=ticket_id,
                    edge_status=edge_status,
                    target_severity=target_severity,
                    check_ticket_tasks=True,
                )

                should_schedule_hnoc_forwarding = not self._should_always_stay_in_ipa_queue(edge_links)
                forward_time = self._get_hnoc_forward_time_by_outage_type(outage_type, edge)

                if should_schedule_hnoc_forwarding:
                    self.schedule_forward_to_hnoc_queue(
                        forward_time, ticket_id, serial_number, client_name, outage_type,
                        target_severity, has_faulty_digi_link, has_faulty_byob_link, faulty_link_types
                    )
                else:
                    self._logger.info(f"Ticket_id: {ticket_id} for serial: {serial_number} "
                                      f"with link_data: {edge_links} has a blacklisted link and "
                                      f"should not be forwarded to HNOC. Skipping forward to HNOC...")

                    self._logger.info(f"Sending an email for ticket_id: {ticket_id} "
                                      f"with serial: {serial_number} instead of scheduling forward to HNOC...")
                    email_response = await self._bruin_repository.send_initial_email_milestone_notification(
                        ticket_id,
                        serial_number
                    )
                    if email_response['status'] not in range(200, 300):
                        self._logger.error(
                            f'Reminder email of edge {serial_number} could not be sent for ticket'
                            f' {ticket_id}!'
                        )
                    else:
                        append_note_response = await self._append_reminder_note(ticket_id, serial_number)
                        if append_note_response['status'] not in range(200, 300):
                            self._logger.error(
                                f'Reminder note of edge {serial_number} could not be appended to ticket'
                                f' {ticket_id}!'
                            )

            elif ticket_creation_response_status == 473:
                self._logger.info(
                    f'[{outage_type.value}] There is a resolve outage ticket for the same location of faulty '
                    f'edge {serial_number} (ticket ID = {ticket_id}). The ticket was '
                    f'automatically unresolved by Bruin and a new ticket detail for serial {serial_number} was '
                    f'appended to it. Appending initial triage note for this service number...'
                )
                self._metrics_repository.increment_tasks_reopened(
                    client=client_name, outage_type=outage_type.value, severity=target_severity,
                    has_digi=has_faulty_digi_link, has_byob=has_faulty_byob_link, link_types=faulty_link_types
                )

                await self._append_triage_note(ticket_id, cached_edge, edge_status, outage_type)
                await self._change_ticket_severity(
                    ticket_id=ticket_id,
                    edge_status=edge_status,
                    target_severity=target_severity,
                    check_ticket_tasks=False,
                )

                should_schedule_hnoc_forwarding = not self._should_always_stay_in_ipa_queue(edge_links)
                forward_time = self._get_hnoc_forward_time_by_outage_type(outage_type, edge)

                if should_schedule_hnoc_forwarding:
                    self.schedule_forward_to_hnoc_queue(
                        forward_time, ticket_id, serial_number, client_name, outage_type,
                        target_severity, has_faulty_digi_link, has_faulty_byob_link, faulty_link_types
                    )
                else:
                    self._logger.info(f"Ticket_id: {ticket_id} for serial: {serial_number} "
                                      f"with link_data: {edge_links} has a blacklisted link and "
                                      f"should not be forwarded to HNOC. Skipping forward to HNOC...")

                    self._logger.info(f"Sending an email for ticket_id: {ticket_id} "
                                      f"with serial: {serial_number} instead of scheduling forward to HNOC...")
                    email_response = await self._bruin_repository.send_initial_email_milestone_notification(
                        ticket_id,
                        serial_number
                    )
                    if email_response['status'] not in range(200, 300):
                        self._logger.error(
                            f'Reminder email of edge {serial_number} could not be sent for ticket'
                            f' {ticket_id}!'
                        )
                    else:
                        append_note_response = await self._append_reminder_note(ticket_id, serial_number)
                        if append_note_response['status'] not in range(200, 300):
                            self._logger.error(
                                f'Reminder note of edge {serial_number} could not be appended to ticket'
                                f' {ticket_id}!'
                            )
        except Exception as ex:
            msg = (
                f"Error while attempting ticket creation for edge {serial_number}: {ex}"
            )
            raise Exception(msg)

    def _has_business_grade_link_down(self, links: List[dict]) -> bool:
        return any(
            link
            for link in links
            if link['displayName'] and self._is_business_grade_link_label(link['displayName'])
            if self._outage_repository.is_faulty_link(link['linkState'])
        )

    def _is_business_grade_link_label(self, label: str) -> bool:
        business_grade_link_labels = self._config.MONITOR_CONFIG["business_grade_link_labels"]
        return any(bg_label for bg_label in business_grade_link_labels if bg_label in label)
