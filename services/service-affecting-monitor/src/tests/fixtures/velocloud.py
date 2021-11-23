from datetime import datetime
from typing import List
from typing import Optional

import pytest

from tests.fixtures._helpers import _undefined
from tests.fixtures._helpers import velocloudize_date


# Factories
@pytest.fixture(scope='session')
def make_edge():
    def _inner(*, host: str = '', enterprise_name: str = '', enterprise_id: int = 0,
               enterprise_proxy_id: Optional[int] = _undefined, enterprise_proxy_name: Optional[str] = _undefined,
               name: str = '', edge_state: str = '', system_up_since: str = '', service_up_since: str = '',
               last_contact: str = '', id_: int = '', serial_number: str = '',
               ha_serial_number: Optional[str] = _undefined, model_number: str = '', latitude: float = 0.0,
               longitude: float = 0.0):
        enterprise_proxy_id = enterprise_proxy_id if enterprise_proxy_id is not _undefined else 0
        enterprise_proxy_name = enterprise_proxy_name if enterprise_proxy_name is not _undefined else ''
        system_up_since = system_up_since or velocloudize_date(datetime.now())
        service_up_since = service_up_since or velocloudize_date(datetime.now())
        last_contact = last_contact or velocloudize_date(datetime.now())
        ha_serial_number = ha_serial_number if ha_serial_number is not _undefined else ''

        return {
            'host': host,
            'enterpriseName': enterprise_name,
            'enterpriseId': enterprise_id,
            'enterpriseProxyId': enterprise_proxy_id,
            'enterpriseProxyName': enterprise_proxy_name,
            'edgeName': name,
            'edgeState': edge_state,
            'edgeSystemUpSince': system_up_since,
            'edgeServiceUpSince': service_up_since,
            'edgeLastContact': last_contact,
            'edgeId': id_,
            'edgeSerialNumber': serial_number,
            'edgeHASerialNumber': ha_serial_number,
            'edgeModelNumber': model_number,
            'edgeLatitude': latitude,
            'edgeLongitude': longitude,
        }

    return _inner


@pytest.fixture(scope='session')
def make_link():
    def _inner(*, display_name: str = '', isp: Optional[str] = _undefined, interface: str = '',
               internal_id: str = '', state: str = '', last_active: str = '', vpn_state: str = '',
               id_: int = 0, ip_address: str = ''):
        isp = isp if isp is not _undefined else ''
        last_active = last_active or velocloudize_date(datetime.now())

        return {
            'displayName': display_name,
            'isp': isp,
            'interface': interface,
            'internalId': internal_id,
            'linkState': state,
            'linkLastActive': last_active,
            'linkVpnState': vpn_state,
            'linkId': id_,
            'linkIpAddress': ip_address,
        }

    return _inner


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
def make_lookup_interval():
    def _inner(*, start: str = '', end: str = ''):
        start = start or datetime.now()
        end = end or datetime.now()

        return {
            'start': start,
            'end': end,
        }

    return _inner


# RPC requests
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


# RPC responses
@pytest.fixture(scope='session')
def velocloud_500_response(make_rpc_response):
    return make_rpc_response(
        body='Got internal error from Velocloud',
        status=500,
    )
