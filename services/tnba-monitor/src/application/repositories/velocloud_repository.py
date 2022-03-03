from collections import defaultdict
from datetime import datetime
from datetime import timedelta

from application.repositories import nats_error_response
from pytz import utc
from shortuuid import uuid

from application import AffectingTroubles


class VelocloudRepository:
    def __init__(self, event_bus, logger, config, notifications_repository, utils_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._utils_repository = utils_repository

    async def get_links_with_edge_info(self, velocloud_host: str):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                'host': velocloud_host,
            },
        }

        try:
            self._logger.info(f"Getting links with edge info from Velocloud for host {velocloud_host}...")
            response = await self._event_bus.rpc_request("get.links.with.edge.info", request, timeout=30)
        except Exception as e:
            err_msg = f'An error occurred when requesting edge list from Velocloud -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(f"Got links with edge info from Velocloud for host {velocloud_host}!")
            else:
                err_msg = (
                    f'Error while retrieving links with edge info in {self._config.ENVIRONMENT_NAME.upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_edges_for_tnba_monitoring(self):
        all_edges = []
        for host in self._config.MONITOR_CONFIG["velo_filter"]:
            response = await self.get_links_with_edge_info(velocloud_host=host)
            if response['status'] not in range(200, 300):
                self._logger.info(f"Error: could not retrieve edges links by host: {host}")
                continue
            all_edges += response['body']
        links_grouped_by_edge = self.group_links_by_serial(all_edges)
        return links_grouped_by_edge

    def group_links_by_serial(self, links_with_edge_info: list) -> list:
        edges_by_serial = {}

        for link in links_with_edge_info:
            velocloud_host = link['host']
            enterprise_name = link['enterpriseName']
            enterprise_id = link['enterpriseId']
            edge_name = link['edgeName']
            edge_state = link['edgeState']
            serial_number = link['edgeSerialNumber']

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

            edges_by_serial.setdefault(
                serial_number,
                {
                    'host': link['host'],
                    'enterpriseName': link['enterpriseName'],
                    'enterpriseId': link['enterpriseId'],
                    'enterpriseProxyId': link['enterpriseProxyId'],
                    'enterpriseProxyName': link['enterpriseProxyName'],
                    'edgeName': link['edgeName'],
                    'edgeState': link['edgeState'],
                    'edgeSystemUpSince': link['edgeSystemUpSince'],
                    'edgeServiceUpSince': link['edgeServiceUpSince'],
                    'edgeLastContact': link['edgeLastContact'],
                    'edgeId': link['edgeId'],
                    'edgeSerialNumber': link['edgeSerialNumber'],
                    'edgeHASerialNumber': link['edgeHASerialNumber'],
                    'edgeModelNumber': link['edgeModelNumber'],
                    'edgeLatitude': link['edgeLatitude'],
                    'edgeLongitude': link['edgeLongitude'],
                    "links": [],
                }
            )

            link_info = {
                'displayName': link['displayName'],
                'isp': link['isp'],
                'interface': link['interface'],
                'internalId': link['internalId'],
                'linkState': link['linkState'],
                'linkLastActive': link['linkLastActive'],
                'linkVpnState': link['linkVpnState'],
                'linkId': link['linkId'],
                'linkIpAddress': link['linkIpAddress'],
            }

            edges_by_serial[serial_number]["links"].append(link_info)

        edges = list(edges_by_serial.values())
        return edges

    async def get_links_metrics_for_autoresolve(self) -> dict:
        now = datetime.now(utc)
        past_moment = now - timedelta(
            minutes=self._config.MONITOR_CONFIG['service_affecting']['metrics_lookup_interval_minutes']
        )

        interval_for_metrics = {
            'start': past_moment,
            'end': now,
        }
        return await self.get_all_links_metrics(interval=interval_for_metrics)

    async def get_all_links_metrics(self, interval: dict) -> dict:
        all_links_metrics = []
        for host in self._config.MONITOR_CONFIG['velo_filter']:
            response = await self.get_links_metrics_by_host(host=host, interval=interval)
            if response['status'] not in range(200, 300):
                self._logger.info(f"Error: could not retrieve links metrics from Velocloud host {host}")
                continue
            all_links_metrics += response['body']

        return_response = {
            "request_id": uuid(),
            'body': all_links_metrics,
            'status': 200,
        }
        return return_response

    async def get_links_metrics_by_host(self, host: str, interval: dict) -> dict:
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                'host': host,
                'interval': interval,
            },
        }

        try:
            self._logger.info(
                f"Getting links metrics between {interval['start']} and {interval['end']} "
                f"from Velocloud host {host}..."
            )
            response = await self._event_bus.rpc_request("get.links.metric.info", request, timeout=30)
        except Exception as e:
            err_msg = f'An error occurred when requesting links metrics from Velocloud -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving links metrics in {self._config.ENVIRONMENT_NAME.upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )
            else:
                self._logger.info(f"Got links metrics from Velocloud host {host}!")

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_events_by_serial_and_interface(self, customer_cache):
        edges_by_host_and_enterprise = self._structure_edges_by_host_and_enterprise(customer_cache)
        events = defaultdict(lambda: defaultdict(list))

        for host in edges_by_host_and_enterprise:
            edges_by_enterprise = edges_by_host_and_enterprise[host]

            for enterprise_id in edges_by_enterprise:
                edges = edges_by_enterprise[enterprise_id]
                enterprise_events_response = await self.get_enterprise_events(host, enterprise_id)
                enterprise_events = enterprise_events_response['body']

                if enterprise_events_response['status'] not in range(200, 300):
                    continue

                for event in enterprise_events:
                    matching_edge = self._utils_repository.get_first_element_matching(
                        edges,
                        lambda edge: edge['edge_name'] == event['edgeName']
                    )
                    if not matching_edge:
                        self._logger.info(
                            f'No edge in the customer cache had edge name {event["edgeName"]}. Skipping...')
                        continue

                    serial = matching_edge['serial_number']
                    self._logger.info(f'Event with edge name {event["edgeName"]} matches edge from customer cache with'
                                      f'serial number {serial}')

                    interface = self._utils_repository.get_interface_from_event(event)
                    events[serial][interface].append(event)

        return events

    def _structure_edges_by_host_and_enterprise(self, customer_cache):
        self._logger.info('Organizing customer cache by host and enterprise_id')
        edges = defaultdict(lambda: defaultdict(list))

        for edge in customer_cache:
            host = edge['edge']['host']
            enterprise_id = edge['edge']['enterprise_id']
            edges[host][enterprise_id].append(edge)

        return edges

    async def get_enterprise_events(self, host, enterprise_id):
        err_msg = None
        now = datetime.now(utc)
        minutes = self._config.MONITOR_CONFIG['service_affecting']['monitoring_minutes_per_trouble'][
            AffectingTroubles.BOUNCING]
        past_moment = now - timedelta(minutes=minutes)
        event_types = ['LINK_DEAD']

        request = {
            'request_id': uuid(),
            'body': {
                'host': host,
                'enterprise_id': enterprise_id,
                'filter': event_types,
                'start_date': past_moment,
                'end_date': now,
            },
        }

        try:
            self._logger.info(
                f'Getting events of host {host} and enterprise id {enterprise_id} having any type of {event_types} '
                f'that took place between {past_moment} and {now} from Velocloud...'
            )
            response = await self._event_bus.rpc_request("alert.request.event.enterprise", request, timeout=180)
        except Exception as e:
            err_msg = f'An error occurred when requesting edge events from Velocloud for host {host} ' \
                      f'and enterprise id {enterprise_id} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(
                    f'Got events of host {host} and enterprise id {enterprise_id} having any type in {event_types} '
                    f'that took place between {past_moment} and {now} from Velocloud!'
                )
            else:
                err_msg = (
                    f'Error while retrieving events of host {host} and enterprise id {enterprise_id} having any type '
                    f'in {event_types} that took place between {past_moment} and {now} '
                    f'in {self._config.ENVIRONMENT_NAME.upper()}'
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    def _structure_link_and_event_metrics(self, links_metrics: list, events: dict = None):
        result = defaultdict(list)

        for link_info in links_metrics:
            serial = link_info['link']['edgeSerialNumber']
            interface = link_info['link']['interface']

            links_metric = {
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
            link_dict = {
                        'link_metrics': links_metric,
                        'link_events': events[serial][interface]
            }
            result[serial].append(link_dict)

        return result
