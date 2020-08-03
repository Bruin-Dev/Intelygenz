from unittest.mock import Mock

import pytest
from shortuuid import uuid

from application.actions.edge_monitoring import EdgeMonitoring
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
    velocloud_repository = Mock()
    prometheus_repository.start_prometheus_metrics_server = Mock()
    prometheus_repository.set_cycle_total_edges = Mock()
    return EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository, config)


@pytest.fixture(scope='function')
def edge_full_id():
    edges_id = {
        "edge_1": {"host": "test_host1", "enterprise_id": 1, "edge_id": "edge-id-1"},
        "edge_2": {"host": "test_host2", "enterprise_id": 1, "edge_id": "edge-id-2"},
        "edge_3": {"host": "test_host3", "enterprise_id": 1, "edge_id": "edge-id-1"},
        "edge_4": {"host": "test_host4", "enterprise_id": 1, "edge_id": "edge-id-2"},
        "edge_5": {"host": "test_host5", "enterprise_id": 1, "edge_id": "edge-id-2"},
        "edge_6": {"host": "test_host6", "enterprise_id": 1, "edge_id": "edge-id-2"}
    }
    return edges_id


@pytest.fixture(scope='function')
def edge_response_status(edge_full_id):
    edges_status_response = {
        "edge_status_1": {
            'request_id': uuid(),
            'body': {
                'edge_id': edge_full_id['edge_1'],
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'DISCONNECTED', 'serialNumber': 'VC1234567'},
                    'links': [
                        {'linkId': 1, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                        {'linkId': 2, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                    ],
                },
            },
            'status': 200,
        },
        "edge_status_1_state_change": {
            'request_id': uuid(),
            'body': {
                'edge_id': edge_full_id['edge_1'],
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234567'},
                    'links': [
                        {'linkId': 1, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                        {'linkId': 2, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                    ],
                },
            },
            'status': 200,
        },
        "edge_status_2": {
            'request_id': uuid(),
            'body': {
                'edge_id': edge_full_id['edge_2'],
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234568'},
                    'links': [
                        {'linkId': 3, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                        {'linkId': 4, 'link': {'state': 'CONNECTED', 'interface': 'GE1'}},
                    ],
                },
            },
            'status': 200,
        },
        "edge_status_2_link_change": {
            'request_id': uuid(),
            'body': {
                'edge_id': edge_full_id['edge_2'],
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234568'},
                    'links': [
                        {'linkId': 3, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                        {'linkId': 4, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                    ],
                },
            },
            'status': 200,
        },
        "edge_status_3": {
            'request_id': uuid(),
            'body': {
                'edge_id': edge_full_id['edge_3'],
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234568'},
                    'links': [
                        {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                        {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
                    ],
                },
            },
            'status': 200,
        },
        "edge_status_4": {
            'request_id': uuid(),
            'body': {
                'edge_id': edge_full_id['edge_4'],
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234568'},
                    'links': [
                        {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                        {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
                    ],
                },
            },
            'status': 500,
        }, "edge_status_5": {
            'request_id': uuid(),
            'bod': {
                'edge_id': edge_full_id['edge_6'],
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234568'},
                    'links': [
                        {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                        {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
                    ],
                },
            },
            'status': 200,
        },
        "edge_status_6": {
            'reques_id': uuid(),
            'body': {
                'edge_id': edge_full_id['edge_5'],
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234568'},
                    'links': [
                        {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                        {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
                    ],
                },
            },
            'status': 200,
        }
    }

    return edges_status_response
