import asyncio
import re
import time

from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from typing import Callable
from typing import List

from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone
from pytz import utc

from igz.packages.eventbus.eventbus import EventBus

from application.repositories import EdgeIdentifier
from application.repositories.bruin_repository import BruinRepository


INITIAL_AFFECTING_NOTE_REGEX = re.compile(
    r"^#\*(Automation Engine|MetTel's IPA)\*#\n.*Trouble:",
    re.DOTALL | re.MULTILINE
)
REOPEN_NOTE_REGEX = re.compile(r"^#\*(Automation Engine|MetTel's IPA)\*#\nRe-opening")


class ServiceAffectingMonitor:

    def __init__(self, event_bus: EventBus, logger, scheduler, config, template_renderer, metrics_repository,
                 bruin_repository, velocloud_repository, customer_cache_repository, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._template_renderer = template_renderer
        self._metrics_repository = metrics_repository
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository
        self._customer_cache_repository = customer_cache_repository
        self._notifications_repository = notifications_repository

        self.__autoresolve_semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['autoresolve']['semaphore'])

        self.__reset_state()

    async def start_service_affecting_monitor_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: service affecting')
        next_run_time = undefined

        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))
            self._logger.info(f'It will be executed now')

        self._scheduler.add_job(self._service_affecting_monitor_process, 'interval',
                                minutes=self._config.MONITOR_CONFIG["monitoring_minutes_interval"],
                                next_run_time=next_run_time,
                                replace_existing=True,
                                id='_monitor_each_edge')

    def _is_ticket_resolved(self, ticket_detail: dict) -> bool:
        return ticket_detail['detailStatus'] == 'R'

    def __reset_state(self):
        self._customer_cache = []

    async def _service_affecting_monitor_process(self):
        self.__reset_state()

        self._logger.info(f"Processing all links of {len(self._config.MONITOR_CONFIG['device_by_id'])} edges...")
        start_time = time.time()

        customer_cache_response = await self._customer_cache_repository.get_cache_for_affecting_monitoring()
        if customer_cache_response['status'] not in range(200, 300) or customer_cache_response['status'] == 202:
            return

        self._customer_cache: list = customer_cache_response['body']
        if not self._customer_cache:
            self._logger.info('Got an empty customer cache. Process cannot keep going.')
            return

        await self._latency_check()
        await self._packet_loss_check()
        await self._jitter_check()
        await self._bandwidth_check()

        await self._run_autoresolve_process()

        self._logger.info(f"Finished processing all links! Took {round((time.time() - start_time) / 60, 2)} minutes")

    def _structure_links_metrics(self, links_metrics: list) -> list:
        result = []

        for link_info in links_metrics:
            edge_identifier = EdgeIdentifier(
                host=link_info['link'].get('host'),
                enterprise_id=link_info['link'].get('enterpriseId'),
                edge_id=link_info['link'].get('edgeId'),
            )

            if not link_info['link'].get('edgeId'):
                self._logger.info(f"Edge {edge_identifier} doesn't have any ID. Skipping...")
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

    def _map_cached_edges_with_links_metrics_and_contact_info(self, links_metrics: list) -> list:
        result = []

        cached_edges_by_edge_identifier = {
            EdgeIdentifier(**elem['edge']): elem
            for elem in self._customer_cache
        }

        links_metrics_by_edge_identifier = {}
        for elem in links_metrics:
            edge_identifier = EdgeIdentifier(
                host=elem['edge_status']['host'],
                enterprise_id=elem['edge_status']['enterpriseId'],
                edge_id=elem['edge_status']['edgeId']
            )

            links_metrics_by_edge_identifier.setdefault(edge_identifier, [])
            links_metrics_by_edge_identifier[edge_identifier].append(elem)

        for contact_info in self._config.MONITOR_CONFIG['device_by_id']:
            edge_identifier = EdgeIdentifier(
                host=contact_info['host'],
                enterprise_id=contact_info['enterprise_id'],
                edge_id=contact_info['edge_id']
            )

            cached_edge = cached_edges_by_edge_identifier.get(edge_identifier)
            if not cached_edge:
                self._logger.info(f'No cached info was found for edge {edge_identifier}. Skipping...')
                continue

            links_metrics_for_current_edge = links_metrics_by_edge_identifier.get(edge_identifier)
            if not links_metrics_for_current_edge:
                self._logger.info(f'No links metrics were found for edge {edge_identifier}. Skipping...')
                continue

            for metric in links_metrics_for_current_edge:
                result.append({
                    'cached_info': cached_edge,
                    'contact_info': contact_info['contacts'],
                    **metric,
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
        metrics_with_cache_and_contact_info = self._map_cached_edges_with_links_metrics_and_contact_info(links_metrics)
        edges_with_links_info = self._group_links_by_edge(metrics_with_cache_and_contact_info)

        self._logger.info(f'Running auto-resolve for {len(edges_with_links_info)} edges')
        autoresolve_tasks = [self._run_autoresolve_for_edge(edge) for edge in edges_with_links_info]
        await asyncio.gather(*autoresolve_tasks)

        self._logger.info('Auto-resolve process finished!')

    async def _run_autoresolve_for_edge(self, edge: dict):
        async with self.__autoresolve_semaphore:
            serial_number = edge['cached_info']['serial_number']

            self._logger.info(f'Starting autoresolve for edge {serial_number}...')

            if not self._are_all_metrics_within_thresholds(edge):
                self._logger.info(
                    f'At least one metric of edge {serial_number} is not within the threshold. Skipping autoresolve...'
                )
                return

            client_id = edge['cached_info']['bruin_client_info']['client_id']
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

                if not self._was_ticket_created_by_automation_engine(affecting_ticket):
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
                detail_for_ticket_resolution = self._get_first_element_matching(
                    details_from_ticket,
                    lambda detail: detail['detailValue'] == serial_number,
                )
                ticket_detail_id = detail_for_ticket_resolution['detailID']

                notes_from_affecting_ticket = ticket_details_response_body['ticketNotes']
                relevant_notes = [
                    note
                    for note in notes_from_affecting_ticket
                    if serial_number in note['serviceNumber']
                    if note['noteValue'] is not None
                ]
                if not self._was_last_affecting_trouble_detected_recently(relevant_notes,
                                                                          affecting_ticket_creation_date):
                    self._logger.info(
                        f'Edge with serial number {serial_number} has been under an affecting trouble for a long time, '
                        f'so the detail of ticket {affecting_ticket_id} related to it will not be autoresolved. '
                        'Skipping autoresolve...'
                    )
                    continue

                can_detail_be_autoresolved_one_more_time = self._is_affecting_ticket_detail_auto_resolvable(
                    relevant_notes
                )
                if not can_detail_be_autoresolved_one_more_time:
                    self._logger.info(
                        f'Limit to autoresolve detail of ticket {affecting_ticket_id} related to serial '
                        f'{serial_number}) has been maxed out already. Skipping autoresolve...'
                    )
                    continue

                if self._is_ticket_resolved(detail_for_ticket_resolution):
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
                await self._notify_successful_autoresolve(affecting_ticket_id, serial_number)

                self._logger.info(
                    f'Detail of ticket {affecting_ticket_id} related to serial number {serial_number} was autoresolved!'
                )

    def _are_all_metrics_within_thresholds(self, edge: dict) -> bool:
        client_id = edge['cached_info']['bruin_client_info']['client_id']

        all_metrics_within_thresholds = True

        for link in edge['links']:
            metrics = link['link_metrics']

            is_rx_latency_below_threshold = metrics['bestLatencyMsRx'] < self._config.MONITOR_CONFIG["latency"]
            is_tx_latency_below_threshold = metrics['bestLatencyMsTx'] < self._config.MONITOR_CONFIG["latency"]
            are_latency_metrics_below_threshold = is_rx_latency_below_threshold and is_tx_latency_below_threshold

            is_rx_packet_loss_below_threshold = metrics['bestLossPctRx'] < self._config.MONITOR_CONFIG["packet_loss"]
            is_tx_packet_loss_below_threshold = metrics['bestLossPctTx'] < self._config.MONITOR_CONFIG["packet_loss"]
            are_packet_loss_metrics_below_threshold = \
                is_rx_packet_loss_below_threshold and is_tx_packet_loss_below_threshold

            is_rx_jitter_below_threshold = metrics['bestJitterMsRx'] < self._config.MONITOR_CONFIG["jitter"]
            is_tx_jitter_below_threshold = metrics['bestJitterMsTx'] < self._config.MONITOR_CONFIG["jitter"]
            are_jitter_metrics_below_threshold = is_rx_jitter_below_threshold and is_tx_jitter_below_threshold

            are_bandwidth_metrics_below_threshold = True
            if self._is_rep_services_client_id(client_id):
                metrics_lookup_interval = self._config.MONITOR_CONFIG['autoresolve']['metrics_lookup_interval_minutes']
                bandwidth_threshold = self._config.MONITOR_CONFIG['bandwidth_percentage']
                tx_bandwidth = metrics['bpsOfBestPathTx']
                rx_bandwidth = metrics['bpsOfBestPathRx']
                rx_throughput = (metrics['bytesRx'] * 8) / (metrics_lookup_interval * 60)
                tx_throughput = (metrics['bytesTx'] * 8) / (metrics_lookup_interval * 60)
                is_rx_bandwidth_below_threshold = (rx_throughput / rx_bandwidth) * 100 < bandwidth_threshold
                is_tx_bandwidth_below_threshold = (tx_throughput / tx_bandwidth) * 100 < bandwidth_threshold
                are_bandwidth_metrics_below_threshold = \
                    is_rx_bandwidth_below_threshold and is_tx_bandwidth_below_threshold

            all_metrics_within_thresholds &= all([
                are_latency_metrics_below_threshold,
                are_packet_loss_metrics_below_threshold,
                are_jitter_metrics_below_threshold,
                are_bandwidth_metrics_below_threshold,
            ])

        return all_metrics_within_thresholds

    @staticmethod
    def _was_ticket_created_by_automation_engine(ticket: dict) -> bool:
        return ticket['createdBy'] == 'Intelygenz Ai'

    def _was_last_affecting_trouble_detected_recently(self, ticket_notes: list, ticket_creation_date: str) -> bool:
        current_datetime = datetime.now(utc)
        max_seconds_since_last_affecting_trouble = self._config.MONITOR_CONFIG['autoresolve'][
            'last_affecting_trouble_seconds']

        notes_sorted_by_date_asc = sorted(ticket_notes, key=lambda note: note['createdDate'])

        last_reopen_note = self._get_last_element_matching(
            notes_sorted_by_date_asc,
            lambda note: REOPEN_NOTE_REGEX.match(note['noteValue'])
        )
        if last_reopen_note:
            note_creation_date = parse(last_reopen_note['createdDate']).astimezone(utc)
            seconds_elapsed_since_last_affecting_trouble = (current_datetime - note_creation_date).total_seconds()
            return seconds_elapsed_since_last_affecting_trouble <= max_seconds_since_last_affecting_trouble

        initial_affecting_note = self._get_first_element_matching(
            notes_sorted_by_date_asc,
            lambda note: INITIAL_AFFECTING_NOTE_REGEX.search(note['noteValue'])
        )
        if initial_affecting_note:
            note_creation_date = parse(initial_affecting_note['createdDate']).astimezone(utc)
            seconds_elapsed_since_last_affecting_trouble = (current_datetime - note_creation_date).total_seconds()
            return seconds_elapsed_since_last_affecting_trouble <= max_seconds_since_last_affecting_trouble

        ticket_creation_datetime = parse(ticket_creation_date).replace(tzinfo=utc)
        seconds_elapsed_since_last_affecting_trouble = (current_datetime - ticket_creation_datetime).total_seconds()
        return seconds_elapsed_since_last_affecting_trouble <= max_seconds_since_last_affecting_trouble

    def _is_affecting_ticket_detail_auto_resolvable(self, ticket_notes: list) -> bool:
        regex = re.compile(r"^#\*(Automation Engine|MetTel's IPA)\*#\nAuto-resolving task for serial")
        max_autoresolves = self._config.MONITOR_CONFIG['autoresolve']['max_autoresolves']
        times_autoresolved = 0

        for ticket_note in ticket_notes:
            note_value = ticket_note['noteValue']
            is_autoresolve_note = bool(regex.match(note_value))
            times_autoresolved += int(is_autoresolve_note)

            if times_autoresolved >= max_autoresolves:
                return False

        return True

    @staticmethod
    def _get_first_element_matching(iterable, condition: Callable, fallback=None):
        try:
            return next(elem for elem in iterable if condition(elem))
        except StopIteration:
            return fallback

    def _get_last_element_matching(self, iterable, condition: Callable, fallback=None):
        return self._get_first_element_matching(reversed(iterable), condition, fallback)

    async def _notify_successful_autoresolve(self, ticket_id, serial_number):
        message = (
            f'Task related to serial number {serial_number} in Service Affecting ticket {ticket_id} was autoresolved. '
            f'Details at https://app.bruin.com/t/{ticket_id}'
        )
        await self._notifications_repository.send_slack_message(message)

    @staticmethod
    def _group_links_by_edge(links: List[dict]) -> List[dict]:
        edge_info_by_edge_identifier = {}

        for link in links:
            edge_identifier = EdgeIdentifier(**link['cached_info']['edge'])

            edge_info = {
                'cached_info': link['cached_info'],
                'contact_info': link['contact_info'],
                'edge_status': link['edge_status'],
                'links': [],
            }
            edge_info_by_edge_identifier.setdefault(edge_identifier, edge_info)

            link_info = {
                'link_status': link['link_status'],
                'link_metrics': link['link_metrics'],
            }
            edge_info_by_edge_identifier[edge_identifier]['links'].append(link_info)

        return list(edge_info_by_edge_identifier.values())

    async def _latency_check(self):
        self._logger.info('Looking for latency issues...')

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_latency_checks()
        links_metrics: list = links_metrics_response['body']

        if not links_metrics:
            self._logger.info("List of links arrived empty while checking latency issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache_and_contact_info = self._map_cached_edges_with_links_metrics_and_contact_info(links_metrics)

        for elem in metrics_with_cache_and_contact_info:
            cached_info = elem['cached_info']
            link_status = elem['link_status']
            metrics = elem['link_metrics']

            edge_identifier = EdgeIdentifier(**cached_info['edge'])

            is_rx_latency_below_threshold = metrics['bestLatencyMsRx'] < self._config.MONITOR_CONFIG["latency"]
            is_tx_latency_below_threshold = metrics['bestLatencyMsTx'] < self._config.MONITOR_CONFIG["latency"]

            if is_rx_latency_below_threshold and is_tx_latency_below_threshold:
                self._logger.info(
                    f"Link {link_status['interface']} from {edge_identifier} didn't exceed latency thresholds"
                )
                continue

            ticket_dict = self._compose_ticket_dict(
                link_info=elem,
                input=metrics['bestLatencyMsRx'],
                output=metrics['bestLatencyMsTx'],
                trouble='Latency',
                threshold=self._config.MONITOR_CONFIG["latency"]
            )
            await self._notify_trouble(link_info=elem, trouble='Latency', ticket_dict=ticket_dict)

        self._logger.info("Finished looking for latency issues!")

    async def _packet_loss_check(self):
        self._logger.info('Looking for packet loss issues...')

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_packet_loss_checks()
        links_metrics: list = links_metrics_response['body']

        if not links_metrics:
            self._logger.info("List of links arrived empty while checking packet loss issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache_and_contact_info = self._map_cached_edges_with_links_metrics_and_contact_info(links_metrics)

        for elem in metrics_with_cache_and_contact_info:
            cached_info = elem['cached_info']
            link_status = elem['link_status']
            metrics = elem['link_metrics']

            edge_identifier = EdgeIdentifier(**cached_info['edge'])

            is_rx_packet_loss_below_threshold = metrics['bestLossPctRx'] < self._config.MONITOR_CONFIG["packet_loss"]
            is_tx_packet_loss_below_threshold = metrics['bestLossPctTx'] < self._config.MONITOR_CONFIG["packet_loss"]

            if is_rx_packet_loss_below_threshold and is_tx_packet_loss_below_threshold:
                self._logger.info(
                    f"Link {link_status['interface']} from {edge_identifier} didn't exceed packet loss thresholds"
                )
                continue

            ticket_dict = self._compose_ticket_dict(
                link_info=elem,
                input=metrics['bestLossPctRx'],
                output=metrics['bestLossPctTx'],
                trouble='Packet Loss',
                threshold=self._config.MONITOR_CONFIG["packet_loss"]
            )
            await self._notify_trouble(link_info=elem, trouble='Packet Loss', ticket_dict=ticket_dict)

        self._logger.info("Finished looking for packet loss issues!")

    async def _jitter_check(self):
        self._logger.info('Looking for jitter issues...')

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_jitter_checks()
        links_metrics: list = links_metrics_response['body']

        if not links_metrics:
            self._logger.info("List of links arrived empty while checking jitter issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache_and_contact_info = self._map_cached_edges_with_links_metrics_and_contact_info(links_metrics)

        for elem in metrics_with_cache_and_contact_info:
            cached_info = elem['cached_info']
            link_status = elem['link_status']
            metrics = elem['link_metrics']

            edge_identifier = EdgeIdentifier(**cached_info['edge'])

            is_rx_jitter_below_threshold = metrics['bestJitterMsRx'] < self._config.MONITOR_CONFIG["jitter"]
            is_tx_jitter_below_threshold = metrics['bestJitterMsTx'] < self._config.MONITOR_CONFIG["jitter"]

            if is_rx_jitter_below_threshold and is_tx_jitter_below_threshold:
                self._logger.info(
                    f"Link {link_status['interface']} from {edge_identifier} didn't exceed jitter thresholds"
                )
                continue

            ticket_dict = self._compose_ticket_dict(
                link_info=elem,
                input=metrics['bestJitterMsRx'],
                output=metrics['bestJitterMsTx'],
                trouble='Jitter',
                threshold=self._config.MONITOR_CONFIG["jitter"]
            )
            await self._notify_trouble(link_info=elem, trouble='Jitter', ticket_dict=ticket_dict)

        self._logger.info("Finished looking for jitter issues!")

    async def _bandwidth_check(self):
        self._logger.info('Looking for bandwidth issues...')

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_bandwidth_checks()
        links_metrics: list = links_metrics_response['body']

        if not links_metrics:
            self._logger.info("List of links arrived empty while checking bandwidth issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache_and_contact_info = self._map_cached_edges_with_links_metrics_and_contact_info(links_metrics)

        for elem in metrics_with_cache_and_contact_info:
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

            edge_identifier = EdgeIdentifier(**cached_info['edge'])

            minutes_to_check = self._config.MONITOR_CONFIG['monitoring_minutes_per_trouble']['bandwidth']
            threshold = self._config.MONITOR_CONFIG['bandwidth_percentage']

            rx_throughput = (metrics['bytesRx'] * 8) / (minutes_to_check * 60)
            tx_throughput = (metrics['bytesTx'] * 8) / (minutes_to_check * 60)

            bandwidth_dict = {}

            if rx_bandwidth > 0 and (rx_throughput / rx_bandwidth) * 100 > threshold:
                bandwidth_dict['rx_throughput'] = rx_throughput
                bandwidth_dict['rx_bandwidth'] = rx_bandwidth
                bandwidth_dict['rx_threshold'] = (threshold / 100) * rx_bandwidth

            if tx_bandwidth > 0 and (tx_throughput / tx_bandwidth) * 100 > threshold:
                bandwidth_dict['tx_throughput'] = tx_throughput
                bandwidth_dict['tx_bandwidth'] = tx_bandwidth
                bandwidth_dict['tx_threshold'] = (threshold / 100) * tx_bandwidth

            if not bandwidth_dict:
                self._logger.info(
                    f"Link {link_status['interface']} from {edge_identifier} didn't exceed any bandwidth thresholds"
                )
                continue

            ticket_dict = self._compose_bandwidth_ticket_dict(link_info=elem, bandwidth_metrics=bandwidth_dict)
            await self._notify_trouble(link_info=elem, trouble='Bandwidth Over Utilization', ticket_dict=ticket_dict)

        self._logger.info("Finished looking for bandwidth issues!")

    async def _notify_trouble(self, link_info, trouble, ticket_dict):
        cached_info = link_info['cached_info']
        contact_info = link_info['contact_info']
        edge_identifier = EdgeIdentifier(**cached_info['edge'])

        self._logger.info(f'Service affecting trouble {trouble} detected in edge {edge_identifier}')
        if self._config.MONITOR_CONFIG['environment'] == 'production':
            client_id = cached_info['bruin_client_info']['client_id']

            edge_serial_number = cached_info['serial_number']
            ticket = await self._bruin_repository.get_affecting_ticket(client_id, edge_serial_number)
            if ticket is None:
                return
            if len(ticket) == 0:
                # TODO contact is hardcoded. When Mettel provides us with a service to retrieve the contact change here
                ticket_note = self._ticket_object_to_string(ticket_dict)
                response = await self._bruin_repository.create_affecting_ticket(client_id, edge_serial_number,
                                                                                contact_info)
                if response["status"] not in range(200, 300):
                    return
                ticket_id = response["body"]["ticketIds"][0]
                self._metrics_repository.increment_tickets_created()

                await self._bruin_repository.append_note_to_ticket(ticket_id=ticket_id,
                                                                   note=ticket_note)

                slack_message = f'Ticket created with ticket id: {ticket_id}\n' \
                                f'https://app.bruin.com/helpdesk?clientId={client_id}&' \
                                f'ticketId={ticket_id} , in ' \
                                f'{self._config.MONITOR_CONFIG["environment"]}'
                await self._notifications_repository.send_slack_message(slack_message)

                self._logger.info(f'Ticket created with ticket id: {ticket_id}')

                self._logger.info(
                    f'Detail related to serial {edge_serial_number} of ticket {ticket_id} will be forwarded to the '
                    f'HNOC queue shortly'
                )
                self._schedule_forward_to_hnoc_queue(ticket_id=ticket_id, serial_number=edge_serial_number)
                return
            else:
                ticket_details = BruinRepository.find_detail_by_serial(ticket, edge_serial_number)
                if not ticket_details:
                    self._logger.error(f"No ticket details matching the serial number {edge_serial_number}")
                    return
                if self._is_ticket_resolved(ticket_details):
                    self._logger.info(f'[service-affecting-monitor] ticket with trouble {trouble} '
                                      f'detected in edge with data {edge_identifier}. '
                                      f'Ticket: {ticket}. Re-opening ticket..')
                    ticket_id = ticket['ticketID']
                    detail_id = ticket_details['detailID']
                    open_ticket_response = await self._bruin_repository.open_ticket(ticket_id, detail_id)
                    if open_ticket_response['status'] not in range(200, 300):
                        err_msg = f'[service-affecting-monitor] Error: Could not reopen ticket: {ticket}'
                        self._logger.error(err_msg)
                        await self._notifications_repository.send_slack_message(err_msg)
                        return

                    ticket_note = self._ticket_object_to_string_without_watermark(ticket_dict)
                    slack_message = (
                        f'Affecting ticket {ticket_id} reopened. Details at https://app.bruin.com/t/{ticket_id}'
                    )
                    await self._notifications_repository.send_slack_message(slack_message)
                    await self._bruin_repository.append_reopening_note_to_ticket(ticket_id, ticket_note)
                    self._metrics_repository.increment_tickets_reopened()

                    self._logger.info(
                        f'Forwarding reopened detail {detail_id} (serial {edge_serial_number}) of ticket {ticket_id} '
                        'to the HNOC queue...'
                    )
                    self._schedule_forward_to_hnoc_queue(ticket_id=ticket_id, serial_number=edge_serial_number)
                else:
                    for ticket_note in ticket['ticketNotes']:
                        if ticket_note['noteValue'] and trouble in ticket_note['noteValue']:
                            return
                    ticket_id = ticket["ticketID"]
                    note = self._ticket_object_to_string(ticket_dict)
                    await self._bruin_repository.append_note_to_ticket(ticket_id, note)

                    slack_message = f'Posting {trouble} note to ticket id: {ticket_id}\n' \
                                    f'https://app.bruin.com/t/{ticket_id} , in ' \
                                    f'{self._config.MONITOR_CONFIG["environment"]}'
                    await self._notifications_repository.send_slack_message(slack_message)

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

    def _compose_ticket_dict(self, link_info, input, output, trouble, threshold):
        edge_overview = OrderedDict()
        edge_overview["Edge Name"] = link_info["edge_status"]["edgeName"]
        edge_overview["Trouble"] = trouble
        edge_overview["Interface"] = link_info['link_status']['interface']
        edge_overview["Name"] = link_info['link_status']['displayName']
        edge_overview["Threshold"] = threshold
        edge_overview['Interval for Scan'] = self._config.MONITOR_CONFIG['monitoring_minutes_per_trouble'][
            trouble.lower().replace(' ', '_')]
        edge_overview['Scan Time'] = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))
        if input >= threshold:
            edge_overview["Receive"] = input
        if output >= threshold:
            edge_overview["Transfer"] = output
        edge_overview["Links"] = \
            f'[Edge|https://{link_info["edge_status"]["host"]}/#!/operator/customer/' \
            f'{link_info["edge_status"]["enterpriseId"]}' \
            f'/monitor/edge/{link_info["edge_status"]["edgeId"]}/] - ' \
            f'[QoE|https://{link_info["edge_status"]["host"]}/#!/operator/customer/' \
            f'{link_info["edge_status"]["enterpriseId"]}' \
            f'/monitor/edge/{link_info["edge_status"]["edgeId"]}/qoe/] - ' \
            f'[Transport|https://{link_info["edge_status"]["host"]}/#!/operator/customer/' \
            f'{link_info["edge_status"]["enterpriseId"]}' \
            f'/monitor/edge/{link_info["edge_status"]["edgeId"]}/links/] \n'

        return edge_overview

    def _compose_bandwidth_ticket_dict(self, link_info: dict, bandwidth_metrics: dict) -> dict:
        edge_overview = OrderedDict()

        edge_overview["Edge Name"] = link_info["edge_status"]["edgeName"]
        edge_overview["Trouble"] = 'Bandwidth Over Utilization'
        edge_overview["Interface"] = link_info['link_status']['interface']
        edge_overview["Name"] = link_info['link_status']['displayName']
        edge_overview['Interval for Scan'] = self._config.MONITOR_CONFIG['monitoring_minutes_per_trouble']['bandwidth']
        edge_overview['Scan Time'] = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))

        if 'rx_throughput' in bandwidth_metrics:
            edge_overview['Throughput (Receive)'] = self._humanize_bps(bandwidth_metrics['rx_throughput'])
            edge_overview['Bandwidth (Receive)'] = self._humanize_bps(bandwidth_metrics['rx_bandwidth'])
            edge_overview['Threshold (Receive)'] = f"{self._config.MONITOR_CONFIG['bandwidth_percentage']}% " \
                                                   f"({self._humanize_bps(bandwidth_metrics['rx_threshold'])})"
        if 'tx_throughput' in bandwidth_metrics:
            edge_overview['Throughput (Transfer)'] = self._humanize_bps(bandwidth_metrics['tx_throughput'])
            edge_overview['Bandwidth (Transfer)'] = self._humanize_bps(bandwidth_metrics['tx_bandwidth'])
            edge_overview['Threshold (Transfer)'] = f"{self._config.MONITOR_CONFIG['bandwidth_percentage']}% " \
                                                    f"({self._humanize_bps(bandwidth_metrics['tx_threshold'])})"

        edge_overview["Links"] = \
            f'[Edge|https://{link_info["edge_status"]["host"]}/#!/operator/customer/' \
            f'{link_info["edge_status"]["enterpriseId"]}' \
            f'/monitor/edge/{link_info["edge_status"]["edgeId"]}/] - ' \
            f'[QoE|https://{link_info["edge_status"]["host"]}/#!/operator/customer/' \
            f'{link_info["edge_status"]["enterpriseId"]}' \
            f'/monitor/edge/{link_info["edge_status"]["edgeId"]}/qoe/] - ' \
            f'[Transport|https://{link_info["edge_status"]["host"]}/#!/operator/customer/' \
            f'{link_info["edge_status"]["enterpriseId"]}' \
            f'/monitor/edge/{link_info["edge_status"]["edgeId"]}/links/] \n'

        return edge_overview

    @staticmethod
    def _humanize_bps(bps: int) -> str:
        if 0 <= bps < 1000:
            return f'{round(bps, 3)} bps'
        if 1000 <= bps < 100000000:
            return f'{round((bps / 1000), 3)} Kbps'
        if 100000000 <= bps < 100000000000:
            return f'{round((bps / 1000000), 3)} Mbps'
        if bps >= 100000000000:
            return f'{round((bps / 1000000000), 3)} Gbps'

    def _ticket_object_to_string(self, ticket_dict, watermark=None):
        edge_triage_str = "#*MetTel's IPA*# \n"
        if watermark is not None:
            edge_triage_str = f"{watermark} \n"
        for key in ticket_dict.keys():
            parsed_key = re.sub(r" LABELMARK(.)*", "", key)
            edge_triage_str = edge_triage_str + f'{parsed_key}: {ticket_dict[key]} \n'
        return edge_triage_str

    def _ticket_object_to_string_without_watermark(self, ticket_dict):
        return self._ticket_object_to_string(ticket_dict, "")
