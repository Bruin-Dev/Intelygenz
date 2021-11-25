import time
from collections import ChainMap
from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Optional

import asyncio
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone

from application import ALL_FIS_CLIENTS
from application import AffectingTroubles


class ServiceAffectingMonitor:

    def __init__(self, logger, scheduler, config, metrics_repository, bruin_repository, velocloud_repository,
                 customer_cache_repository, notifications_repository, ticket_repository, trouble_repository,
                 utils_repository):
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._metrics_repository = metrics_repository
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository
        self._customer_cache_repository = customer_cache_repository
        self._notifications_repository = notifications_repository
        self._ticket_repository = ticket_repository
        self._trouble_repository = trouble_repository
        self._utils_repository = utils_repository

        self.__autoresolve_semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['autoresolve']['semaphore'])

        self.__reset_state()

    def __reset_state(self):
        self._customer_cache = []

    async def start_service_affecting_monitor(self, exec_on_start=False):
        self._logger.info('Scheduling Service Affecting Monitor job...')
        next_run_time = undefined

        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))
            self._logger.info('Service Affecting Monitor job is going to be executed immediately')

        try:
            self._scheduler.add_job(self._service_affecting_monitor_process, 'interval',
                                    minutes=self._config.MONITOR_CONFIG["monitoring_minutes_interval"],
                                    next_run_time=next_run_time,
                                    replace_existing=False,
                                    id='_service_affecting_monitor_process')
        except ConflictingIdError as conflict:
            self._logger.error(f'Skipping start of Service Affecting Monitoring job. Reason: {conflict}')

    async def _service_affecting_monitor_process(self):
        self.__reset_state()

        self._logger.info(f"Starting Service Affecting Monitor process now...")
        start_time = time.time()

        customer_cache_response = await self._customer_cache_repository.get_cache_for_affecting_monitoring()
        if customer_cache_response['status'] not in range(200, 300) or customer_cache_response['status'] == 202:
            return

        self._customer_cache: list = customer_cache_response['body']
        if not self._customer_cache:
            self._logger.info('Got an empty customer cache. Process cannot keep going.')
            return
        self._default_contact_info_by_client = self._get_default_contact_info_by_client()
        self._customer_cache: list = [
            edge
            for edge in customer_cache_response['body']
            if edge['bruin_client_info']['client_id'] in self._default_contact_info_by_client.keys()
        ]

        await self._latency_check()
        await self._packet_loss_check()
        await self._jitter_check()
        await self._bandwidth_check()

        await self._run_autoresolve_process()

        self._logger.info(f"Finished processing all links! Took {round((time.time() - start_time) / 60, 2)} minutes")

    def _get_default_contact_info_by_client(self):

        contact_info_by_client = dict(ChainMap(*[
            default_contact_info_by_client_id
            for default_contact_info_by_client_id in
            self._config.MONITOR_CONFIG['contact_by_host_and_client_id'].values()]))

        if ALL_FIS_CLIENTS in contact_info_by_client.keys():
            fis_contact_info = contact_info_by_client.pop(ALL_FIS_CLIENTS)
            fis_contact_info_by_client = {
                edge['bruin_client_info']['client_id']: fis_contact_info
                for edge in self._customer_cache
                if edge['edge']['host'] == 'metvco04.mettel.net'
            }
            contact_info_by_client = {
                **contact_info_by_client,
                **fis_contact_info_by_client,
            }

        return contact_info_by_client

    def _structure_links_metrics(self, links_metrics: list) -> list:
        result = []

        for link_info in links_metrics:
            velocloud_host = link_info['link']['host']
            enterprise_name = link_info['link']['enterpriseName']
            enterprise_id = link_info['link']['enterpriseId']
            edge_name = link_info['link']['edgeName']
            edge_state = link_info['link']['edgeState']

            if edge_state is None:
                self._logger.info(
                    f"Edge in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
                    f"has an invalid state. Skipping..."
                )
                continue

            if edge_state == 'NEVER_ACTIVATED':
                self._logger.info(
                    f"Edge {edge_name} in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
                    f"has never been activated. Skipping..."
                )
                continue

            result.append({
                'edge_status': {
                    'enterpriseName': link_info['link']['enterpriseName'],
                    'enterpriseId': link_info['link']['enterpriseId'],
                    'enterpriseProxyId': link_info['link']['enterpriseProxyId'],
                    'enterpriseProxyName': link_info['link']['enterpriseProxyName'],
                    'edgeName': link_info['link']['edgeName'],
                    'edgeState': link_info['link']['edgeState'],
                    'edgeSystemUpSince': link_info['link']['edgeSystemUpSince'],
                    'edgeServiceUpSince': link_info['link']['edgeServiceUpSince'],
                    'edgeLastContact': link_info['link']['edgeLastContact'],
                    'edgeId': link_info['link']['edgeId'],
                    'edgeSerialNumber': link_info['link']['edgeSerialNumber'],
                    'edgeHASerialNumber': link_info['link']['edgeHASerialNumber'],
                    'edgeModelNumber': link_info['link']['edgeModelNumber'],
                    'edgeLatitude': link_info['link']['edgeLatitude'],
                    'edgeLongitude': link_info['link']['edgeLongitude'],
                    'host': link_info['link']['host'],
                },
                'link_status': {
                    'interface': link_info['link']['interface'],
                    'internalId': link_info['link']['internalId'],
                    'linkState': link_info['link']['linkState'],
                    'linkLastActive': link_info['link']['linkLastActive'],
                    'linkVpnState': link_info['link']['linkVpnState'],
                    'linkId': link_info['link']['linkId'],
                    'linkIpAddress': link_info['link']['linkIpAddress'],
                    'displayName': link_info['link']['displayName'],
                    'isp': link_info['link']['isp'],
                },
                'link_metrics': {
                    'bytesTx': link_info['bytesTx'],
                    'bytesRx': link_info['bytesRx'],
                    'packetsTx': link_info['packetsTx'],
                    'packetsRx': link_info['packetsRx'],
                    'totalBytes': link_info['totalBytes'],
                    'totalPackets': link_info['totalPackets'],
                    'p1BytesRx': link_info['p1BytesRx'],
                    'p1BytesTx': link_info['p1BytesTx'],
                    'p1PacketsRx': link_info['p1PacketsRx'],
                    'p1PacketsTx': link_info['p1PacketsTx'],
                    'p2BytesRx': link_info['p2BytesRx'],
                    'p2BytesTx': link_info['p2BytesTx'],
                    'p2PacketsRx': link_info['p2PacketsRx'],
                    'p2PacketsTx': link_info['p2PacketsTx'],
                    'p3BytesRx': link_info['p3BytesRx'],
                    'p3BytesTx': link_info['p3BytesTx'],
                    'p3PacketsRx': link_info['p3PacketsRx'],
                    'p3PacketsTx': link_info['p3PacketsTx'],
                    'controlBytesRx': link_info['controlBytesRx'],
                    'controlBytesTx': link_info['controlBytesTx'],
                    'controlPacketsRx': link_info['controlPacketsRx'],
                    'controlPacketsTx': link_info['controlPacketsTx'],
                    'bpsOfBestPathRx': link_info['bpsOfBestPathRx'],
                    'bpsOfBestPathTx': link_info['bpsOfBestPathTx'],
                    'bestJitterMsRx': link_info['bestJitterMsRx'],
                    'bestJitterMsTx': link_info['bestJitterMsTx'],
                    'bestLatencyMsRx': link_info['bestLatencyMsRx'],
                    'bestLatencyMsTx': link_info['bestLatencyMsTx'],
                    'bestLossPctRx': link_info['bestLossPctRx'],
                    'bestLossPctTx': link_info['bestLossPctTx'],
                    'scoreTx': link_info['scoreTx'],
                    'scoreRx': link_info['scoreRx'],
                    'signalStrength': link_info['signalStrength'],
                    'state': link_info['state'],
                }
            })

        return result

    async def _map_cached_edges_with_links_metrics_and_contact_info(self, links_metrics: list) -> list:
        result = []

        cached_edges_by_serial = {
            elem['serial_number']: elem
            for elem in self._customer_cache
        }

        for elem in links_metrics:
            serial_number = elem['edge_status']['edgeSerialNumber']
            cached_edge = cached_edges_by_serial.get(serial_number)
            if not cached_edge:
                self._logger.info(f'No cached info was found for edge {serial_number}. Skipping...')
                continue

            client_id = cached_edge['bruin_client_info']['client_id']
            site_details = cached_edge['site_details']

            default_contacts = self._default_contact_info_by_client.get(client_id)
            contacts = self._bruin_repository.get_contact_info_for_site(site_details) or default_contacts

            result.append({
                'cached_info': cached_edge,
                'contact_info': contacts,
                **elem,
            })

        return result

    async def _run_autoresolve_process(self):
        self._logger.info('Starting auto-resolve process...')

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_autoresolve()
        links_metrics: list = links_metrics_response['body']

        if not links_metrics:
            self._logger.info("List of links metrics arrived empty while running auto-resolve process. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache_and_contact_info = await self._map_cached_edges_with_links_metrics_and_contact_info(
            links_metrics)
        edges_with_links_info = self._group_links_by_edge(metrics_with_cache_and_contact_info)

        self._logger.info(f'Running auto-resolve for {len(edges_with_links_info)} edges')
        autoresolve_tasks = [self._run_autoresolve_for_edge(edge) for edge in edges_with_links_info]
        await asyncio.gather(*autoresolve_tasks)

        self._logger.info('Auto-resolve process finished!')

    async def _run_autoresolve_for_edge(self, edge: dict):
        async with self.__autoresolve_semaphore:
            serial_number = edge['cached_info']['serial_number']
            client_id = edge['cached_info']['bruin_client_info']['client_id']

            self._logger.info(f'Starting autoresolve for edge {serial_number}...')

            is_rep_services = self._is_rep_services_client_id(client_id)
            is_signet = self._is_signet_client_id(client_id)
            check_bandwidth_troubles = is_rep_services or is_signet
            metrics_lookup_interval = self._config.MONITOR_CONFIG['autoresolve']['metrics_lookup_interval_minutes']
            all_metrics_within_thresholds = self._trouble_repository.are_all_metrics_within_thresholds(
                edge,
                lookup_interval_minutes=metrics_lookup_interval,
                check_bandwidth_troubles=check_bandwidth_troubles,
            )
            if not all_metrics_within_thresholds:
                self._logger.info(
                    f'At least one metric of edge {serial_number} is not within the threshold. Skipping autoresolve...'
                )
                return

            affecting_ticket_response = await self._bruin_repository.get_open_affecting_tickets(
                client_id, service_number=serial_number
            )
            affecting_ticket_response_status = affecting_ticket_response['status']
            if affecting_ticket_response_status not in range(200, 300):
                return

            affecting_tickets: list = affecting_ticket_response['body']
            if not affecting_tickets:
                self._logger.info(
                    f'No affecting ticket found for edge with serial number {serial_number}. Skipping autoresolve...'
                )
                return

            for affecting_ticket in affecting_tickets:
                affecting_ticket_id = affecting_ticket['ticketID']
                affecting_ticket_creation_date = affecting_ticket['createDate']

                if not self._ticket_repository.was_ticket_created_by_automation_engine(affecting_ticket):
                    self._logger.info(
                        f'Ticket {affecting_ticket_id} was not created by Automation Engine. Skipping autoresolve...'
                    )
                    continue

                ticket_details_response = await self._bruin_repository.get_ticket_details(affecting_ticket_id)
                ticket_details_response_body = ticket_details_response['body']
                ticket_details_response_status = ticket_details_response['status']
                if ticket_details_response_status not in range(200, 300):
                    continue

                details_from_ticket = ticket_details_response_body['ticketDetails']
                detail_for_ticket_resolution = self._ticket_repository.find_task_by_serial_number(
                    details_from_ticket, serial_number
                )
                ticket_detail_id = detail_for_ticket_resolution['detailID']

                notes_from_affecting_ticket = ticket_details_response_body['ticketNotes']
                relevant_notes = [
                    note
                    for note in notes_from_affecting_ticket
                    if serial_number in note['serviceNumber']
                    if note['noteValue'] is not None
                ]

                max_seconds_since_last_trouble = self._config.MONITOR_CONFIG['autoresolve'][
                    'last_affecting_trouble_seconds']
                last_trouble_was_detected_recently = self._trouble_repository.was_last_trouble_detected_recently(
                    relevant_notes,
                    affecting_ticket_creation_date,
                    max_seconds_since_last_trouble=max_seconds_since_last_trouble,
                )
                if not last_trouble_was_detected_recently:
                    self._logger.info(
                        f'Edge with serial number {serial_number} has been under an affecting trouble for a long time, '
                        f'so the detail of ticket {affecting_ticket_id} related to it will not be autoresolved. '
                        'Skipping autoresolve...'
                    )
                    continue

                if self._ticket_repository.is_autoresolve_threshold_maxed_out(relevant_notes):
                    self._logger.info(
                        f'Limit to autoresolve detail of ticket {affecting_ticket_id} related to serial '
                        f'{serial_number} has been maxed out already. Skipping autoresolve...'
                    )
                    continue

                if self._ticket_repository.is_task_resolved(detail_for_ticket_resolution):
                    self._logger.info(
                        f'Detail of ticket {affecting_ticket_id} related to serial {serial_number} is already '
                        'resolved. Skipping autoresolve...'
                    )
                    continue

                working_environment = self._config.MONITOR_CONFIG['environment']
                if working_environment != 'production':
                    self._logger.info(
                        f'Skipping autoresolve for detail of ticket {affecting_ticket_id} related to serial number '
                        f'{serial_number} since the current environment is {working_environment.upper()}'
                    )
                    continue

                self._logger.info(
                    f'Autoresolving detail of ticket {affecting_ticket_id} related to serial number {serial_number}...'
                )
                await self._bruin_repository.unpause_ticket_detail(affecting_ticket_id, serial_number)
                resolve_ticket_response = await self._bruin_repository.resolve_ticket(
                    affecting_ticket_id, ticket_detail_id
                )
                if resolve_ticket_response['status'] not in range(200, 300):
                    continue

                await self._bruin_repository.append_autoresolve_note_to_ticket(affecting_ticket_id, serial_number)
                await self._notifications_repository.notify_successful_autoresolve(affecting_ticket_id, serial_number)

                self._logger.info(
                    f'Detail of ticket {affecting_ticket_id} related to serial number {serial_number} was autoresolved!'
                )

            self._logger.info(f'Finished autoresolve for edge {serial_number}!')

    @staticmethod
    def _group_links_by_edge(links: List[dict]) -> List[dict]:
        edge_info_by_serial = {}

        for link in links:
            serial_number = link['cached_info']['serial_number']

            edge_info = {
                'cached_info': link['cached_info'],
                'contact_info': link['contact_info'],
                'edge_status': link['edge_status'],
                'links': [],
            }
            edge_info_by_serial.setdefault(serial_number, edge_info)

            link_info = {
                'link_status': link['link_status'],
                'link_metrics': link['link_metrics'],
            }
            edge_info_by_serial[serial_number]['links'].append(link_info)

        return list(edge_info_by_serial.values())

    async def _latency_check(self):
        self._logger.info('Looking for latency issues...')

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_latency_checks()
        links_metrics: list = links_metrics_response['body']

        if not links_metrics:
            self._logger.info("List of links arrived empty while checking latency issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache_and_contact_info = await \
            self._map_cached_edges_with_links_metrics_and_contact_info(links_metrics)

        for elem in metrics_with_cache_and_contact_info:
            await asyncio.sleep(0)

            cached_info = elem['cached_info']
            link_status = elem['link_status']
            metrics = elem['link_metrics']

            serial_number = cached_info['serial_number']

            if self._trouble_repository.are_latency_metrics_within_threshold(metrics):
                self._logger.info(
                    f"Link {link_status['interface']} from {serial_number} didn't exceed latency thresholds"
                )
                continue

            await self._process_latency_trouble(elem)

        self._logger.info("Finished looking for latency issues!")

    async def _packet_loss_check(self):
        self._logger.info('Looking for packet loss issues...')

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_packet_loss_checks()
        links_metrics: list = links_metrics_response['body']

        if not links_metrics:
            self._logger.info("List of links arrived empty while checking packet loss issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache_and_contact_info = await \
            self._map_cached_edges_with_links_metrics_and_contact_info(links_metrics)

        for elem in metrics_with_cache_and_contact_info:
            await asyncio.sleep(0)

            cached_info = elem['cached_info']
            link_status = elem['link_status']
            metrics = elem['link_metrics']

            serial_number = cached_info['serial_number']

            if self._trouble_repository.are_packet_loss_metrics_within_threshold(metrics):
                self._logger.info(
                    f"Link {link_status['interface']} from {serial_number} didn't exceed packet loss thresholds"
                )
                continue

            await self._process_packet_loss_trouble(elem)

        self._logger.info("Finished looking for packet loss issues!")

    async def _jitter_check(self):
        self._logger.info('Looking for jitter issues...')

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_jitter_checks()
        links_metrics: list = links_metrics_response['body']

        if not links_metrics:
            self._logger.info("List of links arrived empty while checking jitter issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache_and_contact_info = await \
            self._map_cached_edges_with_links_metrics_and_contact_info(links_metrics)

        for elem in metrics_with_cache_and_contact_info:
            await asyncio.sleep(0)

            cached_info = elem['cached_info']
            link_status = elem['link_status']
            metrics = elem['link_metrics']

            serial_number = cached_info['serial_number']

            if self._trouble_repository.are_jitter_metrics_within_threshold(metrics):
                self._logger.info(
                    f"Link {link_status['interface']} from {serial_number} didn't exceed jitter thresholds"
                )
                continue

            await self._process_jitter_trouble(elem)

        self._logger.info("Finished looking for jitter issues!")

    async def _bandwidth_check(self):
        self._logger.info('Looking for bandwidth issues...')

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_bandwidth_checks()
        links_metrics: list = links_metrics_response['body']

        if not links_metrics:
            self._logger.info("List of links arrived empty while checking bandwidth issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache_and_contact_info = await \
            self._map_cached_edges_with_links_metrics_and_contact_info(links_metrics)

        for elem in metrics_with_cache_and_contact_info:
            await asyncio.sleep(0)

            cached_info = elem['cached_info']
            link_status = elem['link_status']
            metrics = elem['link_metrics']

            # TODO: Remove this check as soon as the customer asks to release Bandwidth check for all edges
            client_id = cached_info['bruin_client_info']['client_id']
            if not self._is_rep_services_client_id(client_id):
                continue

            tx_bandwidth = metrics['bpsOfBestPathTx']
            rx_bandwidth = metrics['bpsOfBestPathRx']

            if tx_bandwidth == 0 and rx_bandwidth == 0:
                continue

            serial_number = cached_info['serial_number']

            trouble = AffectingTroubles.BANDWIDTH_OVER_UTILIZATION
            scan_interval = self._config.MONITOR_CONFIG['monitoring_minutes_per_trouble'][trouble]
            bandwidth_metrics_are_within_threshold = (
                (rx_bandwidth == 0 or self._trouble_repository.is_bandwidth_rx_within_threshold(metrics,
                                                                                                scan_interval)) and (
                    tx_bandwidth == 0 or self._trouble_repository.is_bandwidth_tx_within_threshold(metrics,
                                                                                                   scan_interval))
            )

            if bandwidth_metrics_are_within_threshold:
                self._logger.info(
                    f"Link {link_status['interface']} from {serial_number} didn't exceed any bandwidth thresholds"
                )
                continue

            await self._process_bandwidth_trouble(elem)

        self._logger.info("Finished looking for bandwidth issues!")

    async def _process_latency_trouble(self, link_data: dict):
        trouble = AffectingTroubles.LATENCY
        await self._process_affecting_trouble(link_data, trouble)

    async def _process_packet_loss_trouble(self, link_data: dict):
        trouble = AffectingTroubles.PACKET_LOSS
        await self._process_affecting_trouble(link_data, trouble)

    async def _process_jitter_trouble(self, link_data: dict):
        trouble = AffectingTroubles.JITTER
        await self._process_affecting_trouble(link_data, trouble)

    async def _process_bandwidth_trouble(self, link_data: dict):
        trouble = AffectingTroubles.BANDWIDTH_OVER_UTILIZATION
        await self._process_affecting_trouble(link_data, trouble)

    async def _process_affecting_trouble(self, link_data: dict, trouble: AffectingTroubles):
        trouble_processed = False
        open_affecting_ticket = None
        resolved_affecting_ticket = None

        serial_number = link_data['cached_info']['serial_number']
        interface = link_data['link_status']['interface']
        client_id = link_data['cached_info']['bruin_client_info']['client_id']

        self._logger.info(
            f'Service Affecting trouble of type {trouble.value} detected in interface {interface} of edge '
            f'{serial_number}'
        )

        open_affecting_tickets_response = await self._bruin_repository.get_open_affecting_tickets(
            client_id, service_number=serial_number
        )
        if open_affecting_tickets_response['status'] not in range(200, 300):
            return

        # Get oldest open ticket related to Service Affecting Monitor (i.e. trouble must be latency, packet loss, jitter
        # or bandwidth)
        open_affecting_tickets = open_affecting_tickets_response['body']
        open_affecting_ticket = await self._get_oldest_affecting_ticket_for_serial_number(
            open_affecting_tickets, serial_number
        )

        if open_affecting_ticket:
            ticket_id = open_affecting_ticket['ticket_overview']['ticketID']
            self._logger.info(
                f'An open Service Affecting ticket was found for edge {serial_number}. Ticket ID: {ticket_id}'
            )

            # The task related to the serial we're checking can be in Resolved state, even if the ticket is returned as
            # open by Bruin. If that's the case, the task should be re-opened instead.
            if self._ticket_repository.is_task_resolved(open_affecting_ticket['ticket_task']):
                self._logger.info(
                    f'Service Affecting ticket with ID {ticket_id} is open, but the task related to edge '
                    f'{serial_number} is Resolved. Therefore, the ticket will be considered as Resolved.'
                )
                resolved_affecting_ticket = {**open_affecting_ticket}
                open_affecting_ticket = None
            else:
                await self._append_latest_trouble_to_ticket(open_affecting_ticket, trouble, link_data)
                trouble_processed = True
        else:
            self._logger.info(f'No open Service Affecting ticket was found for edge {serial_number}')

        # If we didn't get a Resolved ticket in the Open Tickets flow, we need to go look for it
        if not trouble_processed and not resolved_affecting_ticket:
            resolved_affecting_tickets_response = await self._bruin_repository.get_resolved_affecting_tickets(
                client_id, service_number=serial_number
            )
            if resolved_affecting_tickets_response['status'] not in range(200, 300):
                return

            resolved_affecting_tickets = resolved_affecting_tickets_response['body']
            resolved_affecting_ticket = await self._get_oldest_affecting_ticket_for_serial_number(
                resolved_affecting_tickets, serial_number
            )

        # If any of Open Ticket or Resolved Tickets flows returned a Resolved ticket task, keep going
        if not trouble_processed and resolved_affecting_ticket:
            ticket_id = resolved_affecting_ticket['ticket_overview']['ticketID']
            self._logger.info(
                f'A resolved Service Affecting ticket was found for edge {serial_number}. Ticket ID: {ticket_id}'
            )
            await self._unresolve_task_for_affecting_ticket(resolved_affecting_ticket, trouble, link_data)
            trouble_processed = True
        else:
            self._logger.info(f'No resolved Service Affecting ticket was found for edge {serial_number}')

        # If not a single ticket was found for the serial, create a new one
        if not trouble_processed and not open_affecting_ticket and not resolved_affecting_ticket:
            self._logger.info(f'No open or resolved Service Affecting ticket was found for edge {serial_number}')
            await self._create_affecting_ticket(trouble, link_data)

        self._logger.info(
            f'Service Affecting trouble of type {trouble.value} detected in interface {interface} of edge '
            f'{serial_number} has been processed'
        )

    async def _get_oldest_affecting_ticket_for_serial_number(self, tickets: List[dict],
                                                             serial_number: str) -> Optional[dict]:
        tickets = sorted(tickets, key=lambda item: parse(item["createDate"]))

        for ticket in tickets:
            ticket_id = ticket['ticketID']
            ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)

            if ticket_details_response['status'] not in range(200, 300):
                return

            ticket_notes = ticket_details_response['body']['ticketNotes']
            relevant_notes = [
                note
                for note in ticket_notes
                if serial_number in note['serviceNumber']
                if note['noteValue'] is not None
            ]

            ticket_tasks = ticket_details_response['body']['ticketDetails']
            relevant_task = self._ticket_repository.find_task_by_serial_number(ticket_tasks, serial_number)
            return {
                'ticket_overview': ticket,
                'ticket_task': relevant_task,
                'ticket_notes': relevant_notes,
            }

    async def _append_latest_trouble_to_ticket(self, ticket_info: dict, trouble: AffectingTroubles, link_data: dict):
        ticket_id = ticket_info['ticket_overview']['ticketID']
        serial_number = link_data['cached_info']['serial_number']
        interface = link_data['link_status']['interface']

        self._logger.info(
            f'Appending Service Affecting trouble note to ticket {ticket_id} for {trouble.value} trouble detected in '
            f'interface {interface} of edge {serial_number}...'
        )

        ticket_id = ticket_info['ticket_overview']['ticketID']
        ticket_notes = ticket_info['ticket_notes']

        # Get notes since latest re-open or ticket creation
        filtered_notes = self._ticket_repository.get_notes_appended_since_latest_reopen_or_ticket_creation(
            ticket_notes
        )

        # If there is a SA trouble note for the current trouble since the latest re-open note, skip
        # Otherwise, append SA trouble note to ticket using the callback passed as parameter
        if self._ticket_repository.is_there_any_note_for_trouble(filtered_notes, trouble):
            self._logger.info(
                f'No Service Affecting trouble note will be appended to ticket {ticket_id} for {trouble.value} trouble '
                f'detected in interface {interface} of edge {serial_number}. A note for this trouble was already '
                f'appended to the ticket after the latest re-open (or ticket creation)'
            )
            return

        build_note_fn = self._ticket_repository.get_build_note_fn_by_trouble(trouble)
        affecting_trouble_note = build_note_fn(link_data)

        working_environment = self._config.MONITOR_CONFIG['environment']
        if not working_environment == 'production':
            self._logger.info(
                f'No Service Affecting trouble note will be appended to ticket {ticket_id} for {trouble.value} trouble '
                f'detected in interface {interface} of edge {serial_number}, since the current environment is '
                f'{working_environment.upper()}'
            )
            return

        append_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, affecting_trouble_note,
            service_numbers=[serial_number],
        )
        if append_note_response['status'] not in range(200, 300):
            return

        self._logger.info(
            f'Service Affecting trouble note for {trouble.value} trouble detected in interface {interface} '
            f'of edge {serial_number} was successfully appended to ticket {ticket_id}!'
        )
        await self._notifications_repository.notify_successful_note_append(ticket_id, serial_number, trouble)

    async def _unresolve_task_for_affecting_ticket(self, ticket_info: dict, trouble: AffectingTroubles,
                                                   link_data: dict):
        ticket_id = ticket_info['ticket_overview']['ticketID']
        serial_number = link_data['cached_info']['serial_number']
        interface = link_data['link_status']['interface']

        self._logger.info(
            f'Unresolving task related to edge {serial_number} of Service Affecting ticket {ticket_id} due to a '
            f'{trouble.value} trouble detected in interface {interface}...'
        )

        ticket_id = ticket_info['ticket_overview']['ticketID']
        task_id = ticket_info['ticket_task']['detailID']

        working_environment = self._config.MONITOR_CONFIG['environment']
        if not working_environment == 'production':
            self._logger.info(
                f'Task related to edge {serial_number} of Service Affecting ticket {ticket_id} will not be unresolved '
                f'because of the {trouble.value} trouble detected in interface {interface}, since the current '
                f'environment is {working_environment.upper()}'
            )
            return

        unresolve_task_response = await self._bruin_repository.open_ticket(ticket_id, task_id)
        if unresolve_task_response['status'] not in range(200, 300):
            return

        self._logger.info(
            f'Task related to edge {serial_number} of Service Affecting ticket {ticket_id} was successfully '
            f'unresolved! The cause was a {trouble.value} trouble detected in interface {interface}'
        )
        await self._notifications_repository.notify_successful_reopen(ticket_id, serial_number, trouble)
        self._metrics_repository.increment_tickets_reopened()

        build_note_fn = self._ticket_repository.get_build_note_fn_by_trouble(trouble)
        reopen_trouble_note = build_note_fn(link_data, is_reopen_note=True)
        await self._bruin_repository.append_note_to_ticket(
            ticket_id, reopen_trouble_note,
            service_numbers=[serial_number],
        )

        self._logger.info(
            f'Forwarding reopened task for serial {serial_number} of ticket {ticket_id} to the HNOC queue...'
        )
        self._schedule_forward_to_hnoc_queue(ticket_id=ticket_id, serial_number=serial_number)

    async def _create_affecting_ticket(self, trouble: AffectingTroubles, link_data: dict):
        serial_number = link_data['cached_info']['serial_number']
        interface = link_data['link_status']['interface']
        client_id = link_data['cached_info']['bruin_client_info']['client_id']
        contact_info = link_data['contact_info']

        self._logger.info(
            f'Creating Service Affecting ticket to report a {trouble.value} trouble detected in interface {interface} '
            f'of edge {serial_number}...'
        )

        working_environment = self._config.MONITOR_CONFIG['environment']
        if not working_environment == 'production':
            self._logger.info(
                f'No Service Affecting ticket will be created to report a {trouble.value} trouble detected in '
                f'interface {interface} of edge {serial_number}, since the current environment is '
                f'{working_environment.upper()}'
            )
            return

        create_affecting_ticket_response = await self._bruin_repository.create_affecting_ticket(
            client_id, serial_number, contact_info
        )
        if create_affecting_ticket_response["status"] not in range(200, 300):
            return

        ticket_id = create_affecting_ticket_response["body"]["ticketIds"][0]
        self._logger.info(
            f'Service Affecting ticket to report {trouble.value} trouble detected in interface {interface} '
            f'of edge {serial_number} was successfully created! Ticket ID is {ticket_id}'
        )
        self._metrics_repository.increment_tickets_created()
        await self._notifications_repository.notify_successful_ticket_creation(ticket_id, serial_number, trouble)

        build_note_fn = self._ticket_repository.get_build_note_fn_by_trouble(trouble)
        affecting_trouble_note = build_note_fn(link_data)

        await self._bruin_repository.append_note_to_ticket(
            ticket_id, affecting_trouble_note,
            service_numbers=[serial_number],
        )

        self._logger.info(
            f'Task related to serial {serial_number} of ticket {ticket_id} will be forwarded to the '
            f'HNOC queue shortly'
        )
        self._schedule_forward_to_hnoc_queue(ticket_id=ticket_id, serial_number=serial_number)

    def _schedule_forward_to_hnoc_queue(self, ticket_id, serial_number):
        tz = timezone(self._config.MONITOR_CONFIG['timezone'])
        current_datetime = datetime.now(tz)
        forward_task_run_date = current_datetime + timedelta(seconds=self._config.MONITOR_CONFIG['forward_to_hnoc'])

        self._scheduler.add_job(
            self._forward_ticket_to_hnoc_queue, 'date',
            kwargs={'ticket_id': ticket_id, 'serial_number': serial_number},
            run_date=forward_task_run_date,
            replace_existing=False,
            id=f'_forward_ticket_{ticket_id}_{serial_number}_to_hnoc',
        )

    async def _forward_ticket_to_hnoc_queue(self, ticket_id, serial_number):
        change_work_queue_response = await self._bruin_repository.change_detail_work_queue_to_hnoc(
            ticket_id=ticket_id, service_number=serial_number
        )
        if change_work_queue_response['status'] not in range(200, 300):
            return

        await self._notifications_repository.notify_successful_ticket_forward(
            ticket_id=ticket_id, serial_number=serial_number
        )

    @staticmethod
    def _is_rep_services_client_id(client_id: int):
        return client_id == 83109 or client_id == 85940

    @staticmethod
    def _is_signet_client_id(client_id: int):
        return client_id == 86937
