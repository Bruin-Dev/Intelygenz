from collections import defaultdict
from typing import List
from typing import Optional

import pytest
from tests.fixtures._constants import CURRENT_DATETIME
from tests.fixtures._helpers import velocloudize_date


# Model-as-dict generators
def __generate_edge_full_id(*, host: str, enterprise_id: int, edge_id: int):
    return {
        "host": host,
        "enterprise_id": enterprise_id,
        "edge_id": edge_id,
    }


def __generate_link(*, interface_name: str, is_stable: bool):
    link_state = 'STABLE' if is_stable else 'DISCONNECTED'

    return {
        'displayName': '70.59.5.185',
        'isp': None,
        'interface': interface_name,
        'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
        'linkState': link_state,
        'linkLastActive': '2020-09-29T04:45:15.000Z',
        'linkVpnState': link_state,
        'linkId': 5293,
        'linkIpAddress': '70.59.5.185',
    }


def __generate_edge(*, edge_name: str, is_connected: bool, host: str, enterprise_id: int, edge_id: int,
                    serial_number: str):
    edge_state = 'CONNECTED' if is_connected else 'OFFLINE'

    return {
        'host': host,
        'enterpriseName': 'Militaires Sans Frontières',
        'enterpriseId': enterprise_id,
        'enterpriseProxyId': None,
        'enterpriseProxyName': None,
        'edgeName': edge_name,
        'edgeState': edge_state,
        'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
        'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
        'edgeLastContact': '2020-09-29T04:48:55.000Z',
        'edgeId': edge_id,
        'edgeSerialNumber': serial_number,
        'edgeHASerialNumber': None,
        'edgeModelNumber': 'edge520',
        'edgeLatitude': None,
        'edgeLongitude': None,
    }


# Factories
@pytest.fixture(scope='session')
def make_link_with_edge_info(make_link, make_edge):
    def _inner(*, link_info: dict = None, edge_info: dict = None):
        link_info = link_info or make_link()
        edge_info = edge_info or make_edge()
        return {
            **edge_info,
            **link_info,
        }

    return _inner


@pytest.fixture(scope='session')
def make_edge_with_links_info():
    def _inner(*, edge_info: dict, links_info: List[dict]):
        return {
            **edge_info,
            'links': links_info,
        }

    return _inner


# Common
@pytest.fixture(scope='session')
def host_1():
    return 'mettel.velocloud.net'


@pytest.fixture(scope='session')
def enterprise_id_1():
    return 1


@pytest.fixture(scope='session')
def edge_id_1():
    return 1


@pytest.fixture(scope='session')
def edge_id_2():
    return 2


@pytest.fixture(scope='session')
def edge_id_3():
    return 3


# Edge full IDs
@pytest.fixture(scope='session')
def edge_full_id_1(host_1, enterprise_id_1, edge_id_1):
    return __generate_edge_full_id(host=host_1, enterprise_id=enterprise_id_1, edge_id=edge_id_1)


@pytest.fixture(scope='session')
def edge_full_id_2(host_1, enterprise_id_1, edge_id_2):
    return __generate_edge_full_id(host=host_1, enterprise_id=enterprise_id_1, edge_id=edge_id_2)


@pytest.fixture(scope='session')
def edge_full_id_3(host_1, enterprise_id_1, edge_id_3):
    return __generate_edge_full_id(host=host_1, enterprise_id=enterprise_id_1, edge_id=edge_id_3)


@pytest.fixture(scope='session')
def make_edge_full_id():
    def _inner(*, host: str = '', enterprise_id: int = 0, edge_id: int = 0):
        return __generate_edge_full_id(
            host=host,
            enterprise_id=enterprise_id,
            edge_id=edge_id,
        )

    return _inner


# Edges statuses
@pytest.fixture(scope='session')
def edge_1_connected(host_1, enterprise_id_1, edge_id_1, serial_number_1):
    return __generate_edge(edge_name='Big Boss', is_connected=True, host=host_1, enterprise_id=enterprise_id_1,
                           edge_id=edge_id_1, serial_number=serial_number_1)


@pytest.fixture(scope='session')
def edge_2_connected(host_1, enterprise_id_1, edge_id_2, serial_number_2):
    return __generate_edge(edge_name='Otacon', is_connected=True, host=host_1, enterprise_id=enterprise_id_1,
                           edge_id=edge_id_2, serial_number=serial_number_2)


@pytest.fixture(scope='session')
def edge_1_offline(host_1, enterprise_id_1, edge_id_1, serial_number_1):
    return __generate_edge(edge_name='Sniper Wolf', is_connected=False, host=host_1, enterprise_id=enterprise_id_1,
                           edge_id=edge_id_1, serial_number=serial_number_1)


@pytest.fixture(scope='session')
def edge_2_offline(host_1, enterprise_id_1, edge_id_2, serial_number_2):
    return __generate_edge(edge_name='Psycho Mantis', is_connected=False, host=host_1, enterprise_id=enterprise_id_1,
                           edge_id=edge_id_2, serial_number=serial_number_2)


# Links statuses
@pytest.fixture(scope='session')
def link_1_stable():
    return __generate_link(interface_name='REX', is_stable=True)


@pytest.fixture(scope='session')
def link_2_stable():
    return __generate_link(interface_name='RAY', is_stable=True)


@pytest.fixture(scope='session')
def link_1_disconnected():
    return __generate_link(interface_name='REX', is_stable=False)


@pytest.fixture(scope='session')
def link_2_disconnected():
    return __generate_link(interface_name='RAY', is_stable=False)


# RPC responses
@pytest.fixture(scope='session')
def velocloud_500_response():
    return {
        'body': 'Got internal error from Velocloud',
        'status': 500,
    }


@pytest.fixture(scope='session')
def make_metrics():
    def _inner(*, bytes_tx: int = 0, bytes_rx: int = 0,
               packets_tx: int = 0, packets_rx: int = 0,
               total_bytes: int = 0, total_packets: int = 0,
               p1_bytes_tx: int = 0, p1_bytes_rx: int = 0, p1_packets_tx: int = 0, p1_packets_rx: int = 0,
               p2_bytes_tx: int = 0, p2_bytes_rx: int = 0, p2_packets_tx: int = 0, p2_packets_rx: int = 0,
               p3_bytes_tx: int = 0, p3_bytes_rx: int = 0, p3_packets_tx: int = 0, p3_packets_rx: int = 0,
               control_bytes_tx: int = 0, control_bytes_rx: int = 0,
               control_packets_tx: int = 0, control_packets_rx: int = 0,
               bps_of_best_path_tx: int = 0, bps_of_best_path_rx: int = 0,
               best_jitter_ms_tx: int = 0, best_jitter_ms_rx: int = 0,
               best_latency_ms_tx: int = 0, best_latency_ms_rx: int = 0,
               best_packet_loss_tx: int = 0, best_packet_loss_rx: int = 0,
               score_tx: float = 0.0, score_rx: int = 0.0,
               signal_strength: int = 0, state: int = 0):
        return {
            'bytesTx': bytes_tx,
            'bytesRx': bytes_rx,
            'packetsTx': packets_tx,
            'packetsRx': packets_rx,
            'totalBytes': total_bytes,
            'totalPackets': total_packets,
            'p1BytesRx': p1_bytes_rx,
            'p1BytesTx': p1_bytes_tx,
            'p1PacketsRx': p1_packets_rx,
            'p1PacketsTx': p1_packets_tx,
            'p2BytesRx': p2_bytes_rx,
            'p2BytesTx': p2_bytes_tx,
            'p2PacketsRx': p2_packets_rx,
            'p2PacketsTx': p2_packets_tx,
            'p3BytesRx': p3_bytes_rx,
            'p3BytesTx': p3_bytes_tx,
            'p3PacketsRx': p3_packets_rx,
            'p3PacketsTx': p3_packets_tx,
            'controlBytesRx': control_bytes_rx,
            'controlBytesTx': control_bytes_tx,
            'controlPacketsRx': control_packets_rx,
            'controlPacketsTx': control_packets_tx,
            'bpsOfBestPathRx': bps_of_best_path_rx,
            'bpsOfBestPathTx': bps_of_best_path_tx,
            'bestJitterMsRx': best_jitter_ms_rx,
            'bestJitterMsTx': best_jitter_ms_tx,
            'bestLatencyMsRx': best_latency_ms_rx,
            'bestLatencyMsTx': best_latency_ms_tx,
            'bestLossPctRx': best_packet_loss_rx,
            'bestLossPctTx': best_packet_loss_tx,
            'scoreTx': score_tx,
            'scoreRx': score_rx,
            'signalStrength': signal_strength,
            'state': state,
        }

    return _inner


@pytest.fixture(scope='session')
def make_metrics_for_link(make_metrics, make_link_with_edge_info):
    def _inner(*, link_id: int = 0, link_name: str = '', link_with_edge_info: dict = None, metrics: dict = None):
        link_with_edge_info = link_with_edge_info or make_link_with_edge_info()
        metrics = metrics or make_metrics()

        return {
            'linkId': link_id,
            'name': link_name,
            **metrics,
            'link': link_with_edge_info,
        }

    return _inner


@pytest.fixture(scope='session')
def make_list_of_link_metrics():
    def _inner(*link_metrics: List[dict]):
        return list(link_metrics)

    return _inner


@pytest.fixture(scope='session')
def make_event():
    def _inner(*, id_: int = 0, event_time: str = velocloudize_date(CURRENT_DATETIME), event_type: str = 'LINK_DEAD',
               category: str = '', severity: str = '', message: str = '', edge_name: str = '',
               enterprise_username: Optional[str] = '', segment_name: Optional[str] = '', detail: Optional[str] = ''):
        return {
            'id': id_,
            'eventTime': event_time,
            'event': event_type,
            'category': category,
            'severity': severity,
            'message': message,
            'edgeName': edge_name,
            'enterpriseUsername': enterprise_username,
            'segmentName': segment_name,
            'detail': detail,
        }

    return _inner


@pytest.fixture(scope='session')
def make_lookup_interval():
    def _inner(*, start: str = '', end: str = ''):
        start = start or CURRENT_DATETIME
        end = end or CURRENT_DATETIME

        return {
            'start': start,
            'end': end,
        }

    return _inner


@pytest.fixture(scope='session')
def make_get_links_metrics_request(make_rpc_request, make_lookup_interval):
    def _inner(*, request_id: str = '', velocloud_host: str = '', interval: dict = None):
        interval = interval or make_lookup_interval()

        payload = {
            'host': velocloud_host,
            'interval': interval,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope='session')
def make_get_enterprise_events_request(make_rpc_request):
    def _inner(*, request_id: str = '', host: str = '', enterprise_id: int = 0, filter_: list = None,
               start_date: str = velocloudize_date(CURRENT_DATETIME),
               end_date: str = velocloudize_date(CURRENT_DATETIME)):
        payload = {
            'host': host,
            'enterprise_id': enterprise_id,
            'filter': filter_,
            'start_date': start_date,
            'end_date': end_date,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope='session')
def make_edge():
    def _inner(*, edge_name: str = '', is_connected: bool = True, host: str = '', enterprise_id: int = 0,
               edge_id: int = 0, serial_number: str = ''):
        return __generate_edge(edge_name=edge_name, is_connected=is_connected, host=host, enterprise_id=enterprise_id,
                               edge_id=edge_id, serial_number=serial_number)

    return _inner


@pytest.fixture(scope='session')
def make_link():
    def _inner(*, interface_name: str = '', is_stable: bool = True):

        return __generate_link(interface_name=interface_name, is_stable=is_stable)

    return _inner


@pytest.fixture(scope='session')
def make_events_by_serial_and_interface():
    def _inner(*, serials: list = None, interfaces: list = None):
        serials = serials or []
        interfaces = interfaces or []
        events = defaultdict(lambda: defaultdict(list))

        for serial in serials:
            for interface in interfaces:
                events[serial][interface] = []

        return events

    return _inner
