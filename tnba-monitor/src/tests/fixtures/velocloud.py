from typing import List

import pytest


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
def make_link_with_edge_info():
    def _inner(*, link_info: dict, edge_info: dict):
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
