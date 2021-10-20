import base64
import json
import re
import time
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from ipaddress import ip_address
from time import perf_counter
from typing import Callable
from typing import Coroutine

import asyncio
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone
from pytz import utc
from shortuuid import uuid

from application import Outages

TRIAGE_NOTE_REGEX = re.compile(r"^#\*(Automation Engine|MetTel's IPA)\*#\nTriage \(VeloCloud\)")
REOPEN_NOTE_REGEX = re.compile(r"^#\*(Automation Engine|MetTel's IPA)\*#\nRe-opening")


class OutageMonitor:
    def __init__(self, event_bus, logger, scheduler, config, outage_repository, bruin_repository, velocloud_repository,
                 notifications_repository, triage_repository, customer_cache_repository, metrics_repository,
                 digi_repository, ha_repository):
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
        self._metrics_repository.set_last_cycle_duration(round((stop - start) / 60, 2))

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
        self._metrics_repository.increment_edges_processed(amount=len(edges_full_info))
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
                self._logger.info(
                    f"{len(relevant_down_edges)} edges were detected in {outage_type.value} state. Scheduling "
                    "re-check job for all of them..."
                )
                self._schedule_recheck_job_for_edges(relevant_down_edges, outage_type)
            else:
                self._logger.info(
                    f"No edges were detected in {outage_type.value} state. Re-check job won't be scheduled"
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

        tz = timezone(self._config.MONITOR_CONFIG['timezone'])
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
        working_environment = self._config.MONITOR_CONFIG['environment']
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
            serial_number = edge['cached_info']['serial_number']
            self._logger.info(f'[ticket-autoresolve] Starting autoresolve for edge {serial_number}...')

            if serial_number not in self._autoresolve_serials_whitelist:
                self._logger.info(f'[ticket-autoresolve] Skipping autoresolve for edge {serial_number} because its '
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
                self._logger.info(f'[ticket-autoresolve] No outage ticket found for edge {serial_number}. '
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
            relevant_notes = [
                note
                for note in notes_from_outage_ticket
                if serial_number in note['serviceNumber']
                if note['noteValue'] is not None
            ]
            if not self._was_last_outage_detected_recently(relevant_notes, outage_ticket_creation_date):
                self._logger.info(
                    f'Edge {serial_number} has been in outage state for a long time, so detail {ticket_detail_id} '
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

            working_environment = self._config.MONITOR_CONFIG['environment']
            if working_environment != 'production':
                self._logger.info(f'[ticket-autoresolve] Skipping autoresolve for edge {serial_number} since the '
                                  f'current environment is {working_environment.upper()}.')
                return

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

            self._metrics_repository.increment_tickets_autoresolved()
            self._logger.info(
                f'Detail {ticket_detail_id} (serial {serial_number}) of ticket {outage_ticket_id} linked to '
                f'edge {serial_number} was autoresolved!'
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

    async def _recheck_edges_for_ticket_creation(self, outage_edges: list, outage_type: Outages):
        self._logger.info(
            f'[{outage_type.value}] Re-checking {len(outage_edges)} edges in outage state prior to ticket creation...'
        )
        self._logger.info(f"[{outage_type.value}] Edges in outage before quarantine recheck: {outage_edges}")

        # This method is never called with an empty outage_edges, so no IndexError should be raised
        host = outage_edges[0]['status']['host']

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

            working_environment = self._config.MONITOR_CONFIG['environment']
            if working_environment == 'production':
                for edge in edges_still_down:
                    cached_edge = edge['cached_info']
                    edge_full_id = cached_edge['edge']
                    edge_status = edge['status']
                    serial_number = edge['cached_info']['serial_number']
                    self._logger.info(
                        f'[{outage_type.value}] Attempting outage ticket creation for serial {serial_number}...'
                    )

                    bruin_client_id = edge['cached_info']['bruin_client_info']['client_id']
                    ticket_creation_response = await self._bruin_repository.create_outage_ticket(
                        bruin_client_id, serial_number
                    )
                    ticket_creation_response_body = ticket_creation_response['body']
                    ticket_creation_response_status = ticket_creation_response['status']
                    logical_id_list = edge['cached_info']['logical_ids']
                    self._logger.info(f"[{outage_type.value}] Bruin response for ticket creation for edge {edge}: "
                                      f"{ticket_creation_response}")
                    if ticket_creation_response_status in range(200, 300):
                        self._logger.info(f'[{outage_type.value}] Successfully created outage ticket for edge {edge}.')
                        self._metrics_repository.increment_tickets_created()
                        slack_message = (
                            f'Service Outage ticket created for edge {serial_number} in {outage_type.value} state: '
                            f'https://app.bruin.com/t/{ticket_creation_response_body}.'
                        )
                        await self._notifications_repository.send_slack_message(slack_message)
                        await self._append_triage_note(
                            ticket_creation_response_body, cached_edge, edge_status, outage_type
                        )
                        await self._change_ticket_severity(
                            ticket_id=ticket_creation_response_body,
                            edge_status=edge_status,
                            check_ticket_tasks=False,
                        )

                        self.schedule_forward_to_hnoc_queue(ticket_id=ticket_creation_response_body,
                                                            serial_number=serial_number,
                                                            edge_status=edge_status)
                        await self._check_for_digi_reboot(ticket_creation_response_body,
                                                          logical_id_list, serial_number, edge_status)
                    elif ticket_creation_response_status == 409:
                        self._logger.info(
                            f'[{outage_type.value}] Faulty edge {serial_number} already has an outage ticket in '
                            f'progress (ID = {ticket_creation_response_body}). Skipping outage ticket creation for '
                            'this edge...'
                        )
                        await self._change_ticket_severity(
                            ticket_id=ticket_creation_response_body,
                            edge_status=edge_status,
                            check_ticket_tasks=True,
                        )
                        await self._check_for_failed_digi_reboot(ticket_creation_response_body,
                                                                 logical_id_list, serial_number, edge_status)
                        await self._attempt_forward_to_asr(cached_edge, edge_status, ticket_creation_response_body)
                    elif ticket_creation_response_status == 471:
                        self._logger.info(
                            f'[{outage_type.value}] Faulty edge {serial_number} has a resolved outage ticket '
                            f'(ID = {ticket_creation_response_body}). Re-opening ticket...'
                        )
                        await self._reopen_outage_ticket(ticket_creation_response_body, edge_status)
                        await self._change_ticket_severity(
                            ticket_id=ticket_creation_response_body,
                            edge_status=edge_status,
                            check_ticket_tasks=True,
                        )

                        self.schedule_forward_to_hnoc_queue(ticket_id=ticket_creation_response_body,
                                                            serial_number=serial_number, edge_status=edge_status)
                        await self._check_for_digi_reboot(ticket_creation_response_body,
                                                          logical_id_list, serial_number, edge_status)
                    elif ticket_creation_response_status == 472:
                        self._logger.info(
                            f'[{outage_type.value}] Faulty edge {serial_number} has a resolved outage ticket '
                            f'(ID = {ticket_creation_response_body}). Its ticket detail was automatically unresolved '
                            f'by Bruin. Appending reopen note to ticket...'
                        )
                        self.schedule_forward_to_hnoc_queue(ticket_id=ticket_creation_response_body,
                                                            serial_number=serial_number, edge_status=edge_status)
                        await self._post_note_in_outage_ticket(ticket_creation_response_body, edge_status)
                        await self._change_ticket_severity(
                            ticket_id=ticket_creation_response_body,
                            edge_status=edge_status,
                            check_ticket_tasks=True,
                        )
                    elif ticket_creation_response_status == 473:
                        self._logger.info(
                            f'[{outage_type.value}] There is a resolve outage ticket for the same location of faulty '
                            f'edge {serial_number} (ticket ID = {ticket_creation_response_body}). The ticket was '
                            f'automatically unresolved by Bruin and a new ticket detail for serial {serial_number} was '
                            f'appended to it. Appending initial triage note for this service number...'
                        )
                        self.schedule_forward_to_hnoc_queue(ticket_id=ticket_creation_response_body,
                                                            serial_number=serial_number, edge_status=edge_status)
                        await self._append_triage_note(
                            ticket_creation_response_body, cached_edge, edge_status, outage_type
                        )
                        await self._change_ticket_severity(
                            ticket_id=ticket_creation_response_body,
                            edge_status=edge_status,
                            check_ticket_tasks=False,
                        )
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

    def schedule_forward_to_hnoc_queue(self, ticket_id, serial_number, edge_status):
        tz = timezone(self._config.MONITOR_CONFIG['timezone'])
        current_datetime = datetime.now(tz)
        forward_task_run_date = current_datetime + timedelta(
            seconds=self._config.MONITOR_CONFIG['jobs_intervals']['forward_to_hnoc'])

        self._scheduler.add_job(
            self.forward_ticket_to_hnoc_queue, 'date',
            kwargs={'ticket_id': ticket_id, 'serial_number': serial_number, 'edge_status': edge_status},
            run_date=forward_task_run_date,
            replace_existing=False,
            id=f'_forward_ticket_{ticket_id}_{serial_number}_to_hnoc',
        )

    async def forward_ticket_to_hnoc_queue(self, ticket_id, serial_number, edge_status):
        if self._outage_repository.is_faulty_edge(edge_status['edgeState']):
            self._logger.info(
                f'Edge with serial {serial_number} was detected to be DOWN. Ticket {ticket_id} will '
                'be forwarded to the HNOC Investigate queue.'
            )

            await self.change_detail_work_queue(ticket_id=ticket_id, serial_number=serial_number)
        elif self._outage_repository.is_any_link_disconnected(edge_status['links']):
            self._logger.info(f'At least one link of the edge with serial {serial_number} was DISCONNECTED.')

            ticket_data_response = await self._bruin_repository.get_ticket_overview(ticket_id=ticket_id)
            if ticket_data_response['status'] not in range(200, 300):
                return

            ticket_creation_date = ticket_data_response['body']['createDate']
            if not self._is_ticket_old_enough(ticket_creation_date):
                self._logger.info(
                    f'Ticket {ticket_id} is too recent, so detail related to serial {serial_number} will not be '
                    'forwarded to the HNOC Investigate queue'
                )
                return

            self._logger.info(
                f'Ticket {ticket_id} is old enough, so detail related to serial {serial_number} will be forwarded '
                'to the HNOC Investigate queue'
            )
            await self.change_detail_work_queue(ticket_id=ticket_id, serial_number=serial_number)

    async def change_detail_work_queue(self, ticket_id, serial_number):
        task_result = 'HNOC Investigate'
        change_detail_work_queue_response = await self._bruin_repository.change_detail_work_queue(
            serial_number=serial_number,
            ticket_id=ticket_id,
            task_result=task_result)

        if change_detail_work_queue_response['status'] in range(200, 300):
            slack_message = (
                f'Detail of ticket {ticket_id} related to serial {serial_number} was successfully forwarded '
                f'to {task_result} queue!'
            )
            await self._notifications_repository.send_slack_message(slack_message)

    async def _append_triage_note(self, ticket_id: int, cached_edge: dict, edge_status: dict, outage_type: Outages):
        edge_full_id = cached_edge['edge']
        serial_number = cached_edge['serial_number']

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
                f'No events were found for edge {serial_number} starting from {past_moment_for_events_lookup}. '
                f'Not appending any triage note to ticket {ticket_id}.'
            )
            return

        recent_events_response_body.sort(key=lambda event: event['eventTime'], reverse=True)

        ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
        if ticket_details_response['status'] not in range(200, 300):
            return

        ticket_detail: dict = ticket_details_response['body']['ticketDetails'][0]
        ticket_detail_id = ticket_detail['detailID']

        ticket_note = self._triage_repository.build_triage_note(
            cached_edge, edge_status, recent_events_response_body, outage_type
        )

        self._logger.info(
            f'Appending triage note to detail {ticket_detail_id} (serial {serial_number}) of recently created '
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

        ticket_creation_datetime = parse(ticket_creation_date).replace(tzinfo=utc)
        seconds_elapsed_since_last_outage = (current_datetime - ticket_creation_datetime).total_seconds()
        return seconds_elapsed_since_last_outage <= max_seconds_since_last_outage

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

    async def _check_for_failed_digi_reboot(self, ticket_id, logical_id_list, serial_number, edge_status):
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
                detail_for_ticket_resolution = self._get_first_element_matching(
                    details_from_ticket,
                    lambda detail: detail['detailValue'] == serial_number,
                )
                ticket_detail_id = detail_for_ticket_resolution['detailID']

                notes_from_outage_ticket = ticket_details_response_body['ticketNotes']
                self._logger.info(f'Notes of ticket {ticket_id}: {notes_from_outage_ticket}')

                relevant_notes = [
                    note
                    for note in notes_from_outage_ticket
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
                    task_result = "Wireless Repair Intervention Needed"
                    task_result_note = self._find_note(relevant_notes, 'Wireless Repair Intervention Needed')

                    if task_result_note is not None:
                        self._logger.info(f'Task results has already been changed to "{task_result}"')
                        return
                    self._logger.info(f'DiGi reboot attempt failed. Forwarding ticket {ticket_id} to Wireless team')
                    change_detail_work_queue_response = await self._bruin_repository.change_detail_work_queue(
                        ticket_id, task_result, serial_number=serial_number, detail_id=ticket_detail_id)
                    if change_detail_work_queue_response['status'] in range(200, 300):
                        await self._bruin_repository.append_task_result_change_note(ticket_id, task_result)
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

    async def _attempt_forward_to_asr(self, cached_edge, edge_status, ticket_id):
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
        detail_for_ticket_resolution = self._get_first_element_matching(
            details_from_ticket,
            lambda detail: detail['detailValue'] == serial_number,
        )
        ticket_detail_id = detail_for_ticket_resolution['detailID']

        notes_from_outage_ticket = ticket_details_response_body['ticketNotes']
        self._logger.info(f'Notes of ticket {ticket_id}: {notes_from_outage_ticket}')

        relevant_notes = [
            note
            for note in notes_from_outage_ticket
            if serial_number in note['serviceNumber']
            if note['noteValue'] is not None
        ]

        task_result = "No Trouble Found - Carrier Issue"
        task_result_note = self._find_note(relevant_notes, 'ASR Investigate')

        if task_result_note is not None:
            self._logger.info(
                f'Detail related to serial {serial_number} of ticket {ticket_id} has already been forwarded to '
                f'"{task_result}"'
            )
            return

        change_detail_work_queue_response = await self._bruin_repository.change_detail_work_queue(
            ticket_id, task_result, serial_number=serial_number, detail_id=ticket_detail_id)
        if change_detail_work_queue_response['status'] in range(200, 300):
            await self._bruin_repository.append_asr_forwarding_note(ticket_id, whitelisted_links, serial_number)
            slack_message = (
                f'Detail of ticket {ticket_id} related to serial {serial_number} was successfully forwarded '
                f'to {task_result} queue!'
            )
            await self._notifications_repository.send_slack_message(slack_message)

    def _is_link_label_an_ip(self, link_label):
        try:
            return bool(ip_address(link_label))
        except ValueError:
            return False

    def _is_link_label_black_listed(self, link_label):
        blacklisted_link_labels = self._config.MONITOR_CONFIG["blacklisted_link_labels_for_asr_forwards"]
        return any(label for label in blacklisted_link_labels if label in link_label)

    def _find_whitelisted_links_for_asr_forward(self, links: list) -> list:
        return [
            link
            for link in links
            if self._is_link_label_black_listed(link['displayName']) is False
            if self._is_link_label_an_ip(link['displayName']) is False
        ]

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

    async def _change_ticket_severity(self, ticket_id: int, edge_status: dict, *, check_ticket_tasks: bool):
        self._logger.info(f'Attempting to change severity level of ticket {ticket_id}...')

        serial_number = edge_status['edgeSerialNumber']

        change_severity_task: Coroutine = None
        target_severity_level = None

        if self._outage_repository.is_faulty_edge(edge_status['edgeState']):
            self._logger.info(
                f'Severity level of ticket {ticket_id} is about to be changed, as the root cause of the outage issue '
                f'is that edge {serial_number} is offline.'
            )
            change_severity_task = self._bruin_repository.change_ticket_severity_for_offline_edge(ticket_id)
            target_severity_level = self._config.MONITOR_CONFIG['severity_by_outage_type']['edge_down']
        else:
            if check_ticket_tasks:
                ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
                if ticket_details_response['status'] not in range(200, 300):
                    return

                ticket_tasks = ticket_details_response['body']['ticketDetails']
                if self._has_ticket_multiple_unresolved_tasks(ticket_tasks):
                    self._logger.info(
                        f'Severity level of ticket {ticket_id} will remain the same, as the root cause of the outage '
                        f'issue is that at least one link of edge {serial_number} is disconnected, and this ticket '
                        f'has multiple unresolved tasks.'
                    )
                    return

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
            target_severity_level = self._config.MONITOR_CONFIG['severity_by_outage_type']['link_down']

        get_ticket_response = await self._bruin_repository.get_ticket(ticket_id)
        if not get_ticket_response['status'] in range(200, 300):
            change_severity_task.close()
            return

        ticket_info = get_ticket_response['body']
        if self._is_ticket_already_in_severity_level(ticket_info, target_severity_level):
            self._logger.info(
                f'Ticket {ticket_id} is already in severity level {target_severity_level}, so there is no need '
                'to change it.'
            )
            change_severity_task.close()
            return

        await change_severity_task
        self._logger.info(f'Finished changing severity level of ticket {ticket_id} to {target_severity_level}!')

    def _has_ticket_multiple_unresolved_tasks(self, ticket_tasks: list) -> bool:
        unresolved_tasks = [task for task in ticket_tasks if not self._is_detail_resolved(task)]
        return len(unresolved_tasks) > 1

    @staticmethod
    def _is_ticket_already_in_severity_level(ticket_info: dict, severity_level: int) -> bool:
        return ticket_info['severity'] == severity_level
