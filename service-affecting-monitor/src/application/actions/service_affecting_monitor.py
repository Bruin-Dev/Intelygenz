import re
import time

from collections import OrderedDict
from datetime import datetime

from apscheduler.util import undefined
from pytz import timezone
from shortuuid import uuid

from igz.packages.eventbus.eventbus import EventBus

from application.repositories import EdgeIdentifier
from application.repositories.bruin_repository import BruinRepository


class ServiceAffectingMonitor:

    def __init__(self, event_bus: EventBus, logger, scheduler, config, template_renderer, metrics_repository,
                 bruin_repository, velocloud_repository, customer_cache_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._template_renderer = template_renderer
        self._metrics_repository = metrics_repository
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository
        self._customer_cache_repository = customer_cache_repository

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
                ticket_details = {
                    "request_id": uuid(),
                    "body": {
                        "clientId": client_id,
                        "category": "VAS",
                        "services": [
                            {
                                "serviceNumber": edge_serial_number
                            }
                        ],
                        "contacts": [
                            {
                                "email": contact_info['site']['email'],
                                "phone": contact_info['site']['phone'],
                                "name": contact_info['site']['name'],
                                "type": "site"
                            },
                            {
                                "email": contact_info['ticket']['email'],
                                "phone": contact_info['ticket']['phone'],
                                "name": contact_info['ticket']['name'],
                                "type": "ticket"
                            }
                        ]
                    }
                }
                ticket_id = await self._event_bus.rpc_request("bruin.ticket.creation.request",
                                                              ticket_details, timeout=90)
                if ticket_id["status"] not in range(200, 300):
                    err_msg = (f'Outage ticket creation failed for edge {edge_identifier}. Reason: '
                               f'Error {ticket_id["status"]} - {ticket_id["body"]}')

                    self._logger.error(err_msg)
                    slack_message = {
                        'request_id': uuid(),
                        'message': err_msg
                    }
                    await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
                    return

                self._metrics_repository.increment_tickets_created()

                ticket_append_note_msg = {
                    'request_id': uuid(),
                    'body': {
                        'ticket_id': ticket_id["body"]["ticketIds"][0],
                        'note': ticket_note
                    }
                }
                await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                                  ticket_append_note_msg,
                                                  timeout=45)

                slack_message = {'request_id': uuid(),
                                 'message': f'Ticket created with ticket id: {ticket_id["body"]["ticketIds"][0]}\n'
                                            f'https://app.bruin.com/helpdesk?clientId={client_id}&'
                                            f'ticketId={ticket_id["body"]["ticketIds"][0]} , in '
                                            f'{self._config.MONITOR_CONFIG["environment"]}'}
                await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

                self._logger.info(f'Ticket created with ticket id: {ticket_id["body"]["ticketIds"][0]}')
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
                        await self._bruin_repository._notifications_repository.send_slack_message(err_msg)
                        return

                    ticket_note = self._ticket_object_to_string_without_watermark(ticket_dict)
                    slack_message = (
                        f'Affecting ticket {ticket_id} reopened. Details at https://app.bruin.com/t/{ticket_id}'
                    )
                    await self._bruin_repository._notifications_repository.send_slack_message(slack_message)
                    await self._bruin_repository.append_reopening_note_to_ticket(ticket_id, ticket_note)
                    self._metrics_repository.increment_tickets_reopened()
                else:
                    for ticket_note in ticket['ticketNotes']:
                        if ticket_note['noteValue'] and trouble in ticket_note['noteValue']:
                            return
                    ticket_id = ticket["ticketID"]
                    note = self._ticket_object_to_string(ticket_dict)
                    await self._bruin_repository.append_note_to_ticket(ticket_id, note)

                    slack_message = f'Posting {trouble} note to ticket id: {ticket_id}\n'\
                                    f'https://app.bruin.com/t/{ticket_id} , in '\
                                    f'{self._config.MONITOR_CONFIG["environment"]}'
                    await self._bruin_repository._notifications_repository.send_slack_message(slack_message)

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
        edge_triage_str = "#*Automation Engine*# \n"
        if watermark is not None:
            edge_triage_str = f"{watermark} \n"
        for key in ticket_dict.keys():
            parsed_key = re.sub(r" LABELMARK(.)*", "", key)
            edge_triage_str = edge_triage_str + f'{parsed_key}: {ticket_dict[key]} \n'
        return edge_triage_str

    def _ticket_object_to_string_without_watermark(self, ticket_dict):
        return self._ticket_object_to_string(ticket_dict, "")
