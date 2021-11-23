import copy
from unittest.mock import Mock

import pytest

from application.actions.edge_monitoring import EdgeMonitoring
from application.repositories.velocloud_repository import VelocloudRepository
from config import testconfig as config


# Scopes
# - function
# - module
# - session

@pytest.fixture(scope='function')
def instance_server():
    event_bus = Mock()
    logger = Mock()
    prometheus_repository = Mock()
    scheduler = Mock()
    notifications_repository = Mock()
    velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
    prometheus_repository.start_prometheus_metrics_server = Mock()
    prometheus_repository.set_cycle_total_edges = Mock()
    return EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository, config)


@pytest.fixture(scope='function')
def link():
    return {
        'enterpriseName': 'E1',
        'enterpriseId': 1,
        'enterpriseProxyId': None,
        'enterpriseProxyName': None,
        'edgeName': "EDGE2",
        'edgeState': None,
        'edgeSystemUpSince': None,
        'edgeServiceUpSince': None,
        'edgeLastContact': None,
        'edgeId': None,
        'edgeSerialNumber': None,
        'edgeHASerialNumber': None,
        'edgeModelNumber': None,
        'edgeLatitude': None,
        'edgeLongitude': None,
        'displayName': None,
        'isp': None,
        'interface': None,
        'internalId': None,
        'linkState': None,
        'linkLastActive': None,
        'linkVpnState': None,
        'linkId': None,
        'linkIpAddress': None,
        'host': 'mettel.velocloud.net'
    }


# host 1
# edge 1 - link 1 and 2 and link 4 (no state)
# edge 2 - link 3
# edge 3 - no status

# host 2
# edge 1 - link 1

# host 3
# edge 1 - link 1

# host 4
# edge 1 - link 1


@pytest.fixture(scope='function')
def serial_number_1_host_1():
    return 'VC1111111'


@pytest.fixture(scope='function')
def serial_number_2_host_1():
    return 'VC1222222'


@pytest.fixture(scope='function')
def serial_number_3_host_1():
    return 'VC1333333'


@pytest.fixture(scope='function')
def link_1_host_1(link, serial_number_1_host_1):
    updated_edge = copy.deepcopy(link)
    updated_edge['enterpriseName'] = 'E1'
    updated_edge['enterpriseId'] = 1
    updated_edge['edgeId'] = 1
    updated_edge['edgeState'] = 'CONNECTED'
    updated_edge['edgeSerialNumber'] = serial_number_1_host_1
    updated_edge['interface'] = 'GL1'
    updated_edge['linkState'] = 'CONNECTED'
    updated_edge['host'] = 'mettel.velocloud.net'
    return updated_edge


@pytest.fixture(scope='function')
def link_2_host_1(link, serial_number_1_host_1):
    updated_edge = copy.deepcopy(link)
    updated_edge['enterpriseName'] = 'E1'
    updated_edge['enterpriseId'] = 1
    updated_edge['edgeId'] = 1
    updated_edge['edgeState'] = 'CONNECTED'
    updated_edge['edgeSerialNumber'] = serial_number_1_host_1
    updated_edge['interface'] = 'GL2'
    updated_edge['linkState'] = 'CONNECTED'
    updated_edge['host'] = 'mettel.velocloud.net'
    return updated_edge


@pytest.fixture(scope='function')
def link_3_host_1(link, serial_number_2_host_1):
    updated_edge = copy.deepcopy(link)
    updated_edge['enterpriseName'] = 'E2'
    updated_edge['enterpriseId'] = 1
    updated_edge['edgeId'] = 2
    updated_edge['edgeState'] = 'CONNECTED'
    updated_edge['edgeSerialNumber'] = serial_number_2_host_1
    updated_edge['interface'] = 'GL1'
    updated_edge['linkState'] = 'CONNECTED'
    updated_edge['host'] = 'mettel.velocloud.net'
    return updated_edge


@pytest.fixture(scope='function')
def link_4_host_1(link, serial_number_3_host_1):
    updated_edge = copy.deepcopy(link)
    updated_edge['enterpriseName'] = 'E2'
    updated_edge['enterpriseId'] = 1
    updated_edge['edgeId'] = 1
    updated_edge['edgeState'] = 'CONNECTED'
    updated_edge['edgeSerialNumber'] = serial_number_3_host_1
    updated_edge['interface'] = 'GL1'
    updated_edge['linkState'] = 'CONNECTED'
    updated_edge['host'] = 'mettel.velocloud.net'
    return updated_edge


@pytest.fixture(scope='function')
def link_5_host_1(link, serial_number_3_host_1):
    updated_edge = copy.deepcopy(link)
    updated_edge['enterpriseName'] = 'E2'
    updated_edge['enterpriseId'] = 1
    updated_edge['edgeId'] = 1
    updated_edge['edgeState'] = 'CONNECTED'
    updated_edge['edgeSerialNumber'] = serial_number_3_host_1
    updated_edge['interface'] = 'GL1'
    updated_edge['linkState'] = 'CONNECTED'
    updated_edge['host'] = 'mettel.velocloud.net'
    return updated_edge


@pytest.fixture(scope='function')
def edge_1_host_1(link_1_host_1, link_2_host_1):
    return {
        'enterpriseName': link_1_host_1['enterpriseName'],
        'enterpriseId': link_1_host_1['enterpriseId'],
        'enterpriseProxyId': link_1_host_1['enterpriseProxyId'],
        'enterpriseProxyName': link_1_host_1['enterpriseProxyName'],
        'edgeName': link_1_host_1['edgeName'],
        'edgeState': link_1_host_1['edgeState'],
        'edgeSystemUpSince': link_1_host_1['edgeSystemUpSince'],
        'edgeServiceUpSince': link_1_host_1['edgeServiceUpSince'],
        'edgeLastContact': link_1_host_1['edgeLastContact'],
        'edgeId': link_1_host_1['edgeId'],
        'edgeSerialNumber': link_1_host_1['edgeSerialNumber'],
        'edgeHASerialNumber': link_1_host_1['edgeHASerialNumber'],
        'edgeModelNumber': link_1_host_1['edgeModelNumber'],
        'edgeLatitude': link_1_host_1['edgeLatitude'],
        'edgeLongitude': link_1_host_1['edgeLongitude'],
        'host': link_1_host_1['host'],
        "links": [
            {
                'interface': link_1_host_1['interface'],
                'internalId': link_1_host_1['internalId'],
                'linkState': link_1_host_1['linkState'],
                'linkLastActive': link_1_host_1['linkLastActive'],
                'linkVpnState': link_1_host_1['linkVpnState'],
                'linkId': link_1_host_1['linkId'],
                'linkIpAddress': link_1_host_1['linkIpAddress'],
                'displayName': link_1_host_1['displayName'],
                'isp': link_1_host_1['isp'],
            },
            {
                'interface': link_2_host_1['interface'],
                'internalId': link_2_host_1['internalId'],
                'linkState': link_2_host_1['linkState'],
                'linkLastActive': link_2_host_1['linkLastActive'],
                'linkVpnState': link_2_host_1['linkVpnState'],
                'linkId': link_2_host_1['linkId'],
                'linkIpAddress': link_2_host_1['linkIpAddress'],
                'displayName': link_2_host_1['displayName'],
                'isp': link_2_host_1['isp'],
            }
        ]
    }


@pytest.fixture(scope='function')
def edge_1_host_1_offline(edge_1_host_1):
    edge_offline = copy.deepcopy(edge_1_host_1)
    edge_offline['edgeState'] = 'OFFLINE'
    return edge_offline


@pytest.fixture(scope='function')
def edge_1_host_1_offline_link(edge_1_host_1):
    edge_offline = copy.deepcopy(edge_1_host_1)
    edge_offline['links'][0]['linkState'] = 'OFFLINE'
    return edge_offline


@pytest.fixture(scope='function')
def edge_2_host_1(link_3_host_1):
    return {
        'enterpriseName': link_3_host_1['enterpriseName'],
        'enterpriseId': link_3_host_1['enterpriseId'],
        'enterpriseProxyId': link_3_host_1['enterpriseProxyId'],
        'enterpriseProxyName': link_3_host_1['enterpriseProxyName'],
        'edgeName': link_3_host_1['edgeName'],
        'edgeState': link_3_host_1['edgeState'],
        'edgeSystemUpSince': link_3_host_1['edgeSystemUpSince'],
        'edgeServiceUpSince': link_3_host_1['edgeServiceUpSince'],
        'edgeLastContact': link_3_host_1['edgeLastContact'],
        'edgeId': link_3_host_1['edgeId'],
        'edgeSerialNumber': link_3_host_1['edgeSerialNumber'],
        'edgeHASerialNumber': link_3_host_1['edgeHASerialNumber'],
        'edgeModelNumber': link_3_host_1['edgeModelNumber'],
        'edgeLatitude': link_3_host_1['edgeLatitude'],
        'edgeLongitude': link_3_host_1['edgeLongitude'],
        'host': link_3_host_1['host'],
        "links": [
            {
                'interface': link_3_host_1['interface'],
                'internalId': link_3_host_1['internalId'],
                'linkState': link_3_host_1['linkState'],
                'linkLastActive': link_3_host_1['linkLastActive'],
                'linkVpnState': link_3_host_1['linkVpnState'],
                'linkId': link_3_host_1['linkId'],
                'linkIpAddress': link_3_host_1['linkIpAddress'],
                'displayName': link_3_host_1['displayName'],
                'isp': link_3_host_1['isp'],
            }
        ]
    }


@pytest.fixture(scope='function')
def edge_3_host_1(link_4_host_1, link_5_host_1):
    return {
       'enterpriseName': link_5_host_1['enterpriseName'],
       'enterpriseId': link_5_host_1['enterpriseId'],
       'enterpriseProxyId': link_5_host_1['enterpriseProxyId'],
       'enterpriseProxyName': link_5_host_1['enterpriseProxyName'],
       'edgeName': link_5_host_1['edgeName'],
       'edgeState': link_5_host_1['edgeState'],
       'edgeSystemUpSince': link_5_host_1['edgeSystemUpSince'],
       'edgeServiceUpSince': link_5_host_1['edgeServiceUpSince'],
       'edgeLastContact': link_5_host_1['edgeLastContact'],
       'edgeId': link_5_host_1['edgeId'],
       'edgeSerialNumber': link_5_host_1['edgeSerialNumber'],
       'edgeHASerialNumber': link_5_host_1['edgeHASerialNumber'],
       'edgeModelNumber': link_5_host_1['edgeModelNumber'],
       'edgeLatitude': link_5_host_1['edgeLatitude'],
       'edgeLongitude': link_5_host_1['edgeLongitude'],
       'host': link_5_host_1['host'],
       "links": [
           {
               'interface': link_4_host_1['interface'],
               'internalId': link_4_host_1['internalId'],
               'linkState': link_4_host_1['linkState'],
               'linkLastActive': link_4_host_1['linkLastActive'],
               'linkVpnState': link_4_host_1['linkVpnState'],
               'linkId': link_4_host_1['linkId'],
               'linkIpAddress': link_4_host_1['linkIpAddress'],
               'displayName': link_4_host_1['displayName'],
               'isp': link_4_host_1['isp'],
           },
           {
               'interface': link_5_host_1['interface'],
               'internalId': link_5_host_1['internalId'],
               'linkState': link_5_host_1['linkState'],
               'linkLastActive': link_5_host_1['linkLastActive'],
               'linkVpnState': link_5_host_1['linkVpnState'],
               'linkId': link_5_host_1['linkId'],
               'linkIpAddress': link_5_host_1['linkIpAddress'],
               'displayName': link_5_host_1['displayName'],
               'isp': link_5_host_1['isp'],
           }
       ]
    }


@pytest.fixture(scope='function')
def edge_4_host_1(link_4_host_1):
    return {
       'enterpriseName': link_4_host_1['enterpriseName'],
       'enterpriseId': link_4_host_1['enterpriseId'],
       'enterpriseProxyId': link_4_host_1['enterpriseProxyId'],
       'enterpriseProxyName': link_4_host_1['enterpriseProxyName'],
       'edgeName': link_4_host_1['edgeName'],
       'edgeState': link_4_host_1['edgeState'],
       'edgeSystemUpSince': link_4_host_1['edgeSystemUpSince'],
       'edgeServiceUpSince': link_4_host_1['edgeServiceUpSince'],
       'edgeLastContact': link_4_host_1['edgeLastContact'],
       'edgeId': link_4_host_1['edgeId'],
       'edgeSerialNumber': link_4_host_1['edgeSerialNumber'],
       'edgeHASerialNumber': link_4_host_1['edgeHASerialNumber'],
       'edgeModelNumber': link_4_host_1['edgeModelNumber'],
       'edgeLatitude': link_4_host_1['edgeLatitude'],
       'edgeLongitude': link_4_host_1['edgeLongitude'],
       'host': link_4_host_1['host'],
       "links": [],
    }


@pytest.fixture(scope='function')
def serial_number_1_host_2():
    return 'VC2111111'


@pytest.fixture(scope='function')
def edge_1_host_2(link_1_host_2):
    return {
        'enterpriseName': link_1_host_2['enterpriseName'],
        'enterpriseId': link_1_host_2['enterpriseId'],
        'enterpriseProxyId': link_1_host_2['enterpriseProxyId'],
        'enterpriseProxyName': link_1_host_2['enterpriseProxyName'],
        'edgeName': link_1_host_2['edgeName'],
        'edgeState': link_1_host_2['edgeState'],
        'edgeSystemUpSince': link_1_host_2['edgeSystemUpSince'],
        'edgeServiceUpSince': link_1_host_2['edgeServiceUpSince'],
        'edgeLastContact': link_1_host_2['edgeLastContact'],
        'edgeId': link_1_host_2['edgeId'],
        'edgeSerialNumber': link_1_host_2['edgeSerialNumber'],
        'edgeHASerialNumber': link_1_host_2['edgeHASerialNumber'],
        'edgeModelNumber': link_1_host_2['edgeModelNumber'],
        'edgeLatitude': link_1_host_2['edgeLatitude'],
        'edgeLongitude': link_1_host_2['edgeLongitude'],
        'host': link_1_host_2['host'],
        "links": [
            {
                'interface': link_1_host_2['interface'],
                'internalId': link_1_host_2['internalId'],
                'linkState': link_1_host_2['linkState'],
                'linkLastActive': link_1_host_2['linkLastActive'],
                'linkVpnState': link_1_host_2['linkVpnState'],
                'linkId': link_1_host_2['linkId'],
                'linkIpAddress': link_1_host_2['linkIpAddress'],
                'displayName': link_1_host_2['displayName'],
                'isp': link_1_host_2['isp'],
            }
        ]
    }


@pytest.fixture(scope='function')
def link_1_host_2(link, serial_number_1_host_2):
    updated_edge = copy.deepcopy(link)
    updated_edge['enterpriseName'] = 'E1'
    updated_edge['enterpriseId'] = 2
    updated_edge['edgeId'] = 1
    updated_edge['edgeState'] = 'CONNECTED'
    updated_edge['edgeSerialNumber'] = serial_number_1_host_2
    updated_edge['interface'] = 'GL1'
    updated_edge['linkState'] = 'CONNECTED'
    updated_edge['host'] = 'metvco02.mettel.net'
    return updated_edge


@pytest.fixture(scope='function')
def serial_number_1_host_3():
    return 'VC3111111'


@pytest.fixture(scope='function')
def edge_1_host_3(link_1_host_3):
    return {
        'enterpriseName': link_1_host_3['enterpriseName'],
        'enterpriseId': link_1_host_3['enterpriseId'],
        'enterpriseProxyId': link_1_host_3['enterpriseProxyId'],
        'enterpriseProxyName': link_1_host_3['enterpriseProxyName'],
        'edgeName': link_1_host_3['edgeName'],
        'edgeState': link_1_host_3['edgeState'],
        'edgeSystemUpSince': link_1_host_3['edgeSystemUpSince'],
        'edgeServiceUpSince': link_1_host_3['edgeServiceUpSince'],
        'edgeLastContact': link_1_host_3['edgeLastContact'],
        'edgeId': link_1_host_3['edgeId'],
        'edgeSerialNumber': link_1_host_3['edgeSerialNumber'],
        'edgeHASerialNumber': link_1_host_3['edgeHASerialNumber'],
        'edgeModelNumber': link_1_host_3['edgeModelNumber'],
        'edgeLatitude': link_1_host_3['edgeLatitude'],
        'edgeLongitude': link_1_host_3['edgeLongitude'],
        'host': link_1_host_3['host'],
        "links": [
            {
                'interface': link_1_host_3['interface'],
                'internalId': link_1_host_3['internalId'],
                'linkState': link_1_host_3['linkState'],
                'linkLastActive': link_1_host_3['linkLastActive'],
                'linkVpnState': link_1_host_3['linkVpnState'],
                'linkId': link_1_host_3['linkId'],
                'linkIpAddress': link_1_host_3['linkIpAddress'],
                'displayName': link_1_host_3['displayName'],
                'isp': link_1_host_3['isp'],
            }
        ]
    }


@pytest.fixture(scope='function')
def link_1_host_3(link, serial_number_1_host_3):
    updated_edge = copy.deepcopy(link)
    updated_edge['enterpriseName'] = 'E1'
    updated_edge['enterpriseId'] = 3
    updated_edge['edgeId'] = 1
    updated_edge['edgeState'] = 'CONNECTED'
    updated_edge['edgeSerialNumber'] = serial_number_1_host_3
    updated_edge['interface'] = 'GL1'
    updated_edge['linkState'] = 'CONNECTED'
    updated_edge['host'] = 'metvco03.mettel.net'
    return updated_edge


@pytest.fixture(scope='function')
def serial_number_1_host_4():
    return 'VC4111111'


@pytest.fixture(scope='function')
def link_1_host_4(link, serial_number_1_host_4):
    updated_edge = copy.deepcopy(link)
    updated_edge['enterpriseName'] = 'E1'
    updated_edge['enterpriseId'] = 4
    updated_edge['edgeId'] = 1
    updated_edge['edgeState'] = 'CONNECTED'
    updated_edge['edgeSerialNumber'] = serial_number_1_host_4
    updated_edge['interface'] = 'GL1'
    updated_edge['linkState'] = 'CONNECTED'
    updated_edge['host'] = 'metvco04.mettel.net'
    return updated_edge


@pytest.fixture(scope='function')
def edge_1_host_4(link_1_host_4):
    return {
        'enterpriseName': link_1_host_4['enterpriseName'],
        'enterpriseId': link_1_host_4['enterpriseId'],
        'enterpriseProxyId': link_1_host_4['enterpriseProxyId'],
        'enterpriseProxyName': link_1_host_4['enterpriseProxyName'],
        'edgeName': link_1_host_4['edgeName'],
        'edgeState': link_1_host_4['edgeState'],
        'edgeSystemUpSince': link_1_host_4['edgeSystemUpSince'],
        'edgeServiceUpSince': link_1_host_4['edgeServiceUpSince'],
        'edgeLastContact': link_1_host_4['edgeLastContact'],
        'edgeId': link_1_host_4['edgeId'],
        'edgeSerialNumber': link_1_host_4['edgeSerialNumber'],
        'edgeHASerialNumber': link_1_host_4['edgeHASerialNumber'],
        'edgeModelNumber': link_1_host_4['edgeModelNumber'],
        'edgeLatitude': link_1_host_4['edgeLatitude'],
        'edgeLongitude': link_1_host_4['edgeLongitude'],
        'host': link_1_host_4['host'],
        "links": [
            {
                'interface': link_1_host_4['interface'],
                'internalId': link_1_host_4['internalId'],
                'linkState': link_1_host_4['linkState'],
                'linkLastActive': link_1_host_4['linkLastActive'],
                'linkVpnState': link_1_host_4['linkVpnState'],
                'linkId': link_1_host_4['linkId'],
                'linkIpAddress': link_1_host_4['linkIpAddress'],
                'displayName': link_1_host_4['displayName'],
                'isp': link_1_host_4['isp'],
            }
        ]
    }


@pytest.fixture(scope='function')
def list_all_links_with_edge_info(link_1_host_1, link_2_host_1, link_3_host_1, link_4_host_1, link_5_host_1,
                                  link_1_host_2, link_1_host_3, link_1_host_4):
    return {
        'request_id': '12345',
        'status': 200,
        'body': [
            link_1_host_1,
            link_2_host_1,
            link_3_host_1,
            link_4_host_1,
            link_5_host_1,
            link_1_host_2,
            link_1_host_3,
            link_1_host_4
        ]
    }


@pytest.fixture(scope='function')
def links_host_1_response(link_1_host_1, link_2_host_1, link_3_host_1, link_4_host_1, link_5_host_1):
    return {
        'request_id': '1',
        'status': 200,
        'body': [
            link_1_host_1,
            link_2_host_1,
            link_3_host_1,
            link_4_host_1,
            link_5_host_1
        ]
    }


@pytest.fixture(scope='function')
def links_host_2_response(link_1_host_2):
    return {
        'request_id': '2',
        'status': 200,
        'body': [
            link_1_host_2
        ]
    }


@pytest.fixture(scope='function')
def links_host_3_response(link_1_host_3):
    return {
        'request_id': '2',
        'status': 200,
        'body': [
            link_1_host_3
        ]
    }


@pytest.fixture(scope='function')
def links_host_4_response(link_1_host_4):
    return {
        'request_id': '4',
        'status': 200,
        'body': [
            link_1_host_4
        ]
    }


@pytest.fixture(scope='function')
def links_host_4_response_error(link_1_host_4):
    return {
        'request_id': '4',
        'status': 300,
        'body': [
            link_1_host_4
        ]
    }
