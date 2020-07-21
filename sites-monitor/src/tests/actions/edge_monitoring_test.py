import json
from shortuuid import uuid

import pytest
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

from application.actions.edge_monitoring import EdgeMonitoring
from apscheduler.util import undefined as apscheduler_undefined
from asynctest import CoroutineMock
from application.repositories import EdgeIdentifier

from application.actions import edge_monitoring as edge_monitoring_module
from config import testconfig as config


class TestEdgeMonitoring:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()
        velocloud_repository = Mock()
        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler,
                                         velocloud_repository, config)
        assert isinstance(edge_monitoring, EdgeMonitoring)
        assert edge_monitoring._event_bus is event_bus
        assert edge_monitoring._logger is logger
        assert edge_monitoring._prometheus_repository is prometheus_repository
        assert edge_monitoring._scheduler is scheduler
        assert edge_monitoring._config is config

    def start_metrics_server_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()

        prometheus_repository = Mock()
        prometheus_repository.start_prometheus_metrics_server = Mock()
        velocloud_repository = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)
        edge_monitoring.start_prometheus_metrics_server()
        prometheus_repository.start_prometheus_metrics_server.assert_called_once()

    @pytest.mark.asyncio
    async def process_all_edges_test(self):
        logger = Mock()
        scheduler = Mock()
        request_id = 'random-uuid'
        uuid_1 = uuid()
        uuid_2 = uuid()
        uuid_3 = uuid()

        edge_full_id_1 = {"host": "test_host1", "enterprise_id": 1, "edge_id": "edge-id-1"}
        edge_full_id_2 = {"host": "test_host2", "enterprise_id": 1, "edge_id": "edge-id-2"}
        edge_list_response = {
            'request_id': uuid_3,
            'body': [edge_full_id_1, edge_full_id_2],
            'status': 200
        }

        edge_1_status_response = {
            'request_id': uuid_1,
            'body': {
                'edge_id': edge_full_id_1,
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'DISCONNECTED'},
                    'links': [
                        {'link': {'state': 'DISCONNECTED'}},
                        {'link': {'state': 'DISCONNECTED'}},
                    ],
                },
            },
            'status': 200,
        }

        edge_2_status_response = {
            'request_id': uuid_2,
            'body': {
                'edge_id': edge_full_id_1,
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'CONNECTED'},
                    'links': [
                        {'link': {'state': 'DISCONNECTED'}},
                        {'link': {'state': 'CONNECTED'}},
                    ],
                },
            },
            'status': 200,
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(
            return_value={'request_id': request_id, 'body': [edge_full_id_1, edge_full_id_2]})

        prometheus_repository = Mock()
        prometheus_repository.start_prometheus_metrics_server = Mock()
        prometheus_repository.set_cycle_total_edges = Mock()
        prometheus_repository.dec = Mock()
        velocloud_repository = Mock()
        velocloud_repository.get_edges = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response,
            edge_2_status_response,
        ])

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)
        edge_monitoring._process_edge = CoroutineMock()

        await edge_monitoring._process_all_edges()

        assert edge_monitoring._process_edge.await_count == 2

    @pytest.mark.asyncio
    async def process_all_edges_bad_status_test(self):
        logger = Mock()
        scheduler = Mock()
        request_id = 'random-uuid'
        uuid_1 = uuid()
        uuid_2 = uuid()
        uuid_3 = uuid()

        edge_full_id_1 = {"host": "test_host1", "enterprise_id": 1, "edge_id": "edge-id-1"}
        edge_full_id_2 = {"host": "test_host2", "enterprise_id": 1, "edge_id": "edge-id-2"}
        edge_list_response = {
            'request_id': uuid_3,
            'body': [edge_full_id_1, edge_full_id_2],
            'status': 500
        }

        edge_1_status_response = {
            'request_id': uuid_1,
            'body': {
                'edge_id': edge_full_id_1,
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'DISCONNECTED'},
                    'links': [
                        {'link': {'state': 'DISCONNECTED'}},
                        {'link': {'state': 'DISCONNECTED'}},
                    ],
                },
            },
            'status': 200,
        }

        edge_2_status_response = {
            'request_id': uuid_2,
            'body': {
                'edge_id': edge_full_id_1,
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'CONNECTED'},
                    'links': [
                        {'link': {'state': 'DISCONNECTED'}},
                        {'link': {'state': 'CONNECTED'}},
                    ],
                },
            },
            'status': 200,
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(
            return_value={'request_id': request_id, 'body': [edge_full_id_1, edge_full_id_2]})

        prometheus_repository = Mock()
        prometheus_repository.start_prometheus_metrics_server = Mock()
        prometheus_repository.set_cycle_total_edges = Mock()
        prometheus_repository.dec = Mock()
        velocloud_repository = Mock()
        velocloud_repository.get_edges = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response,
            edge_2_status_response,
        ])

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)
        edge_monitoring._process_edge = CoroutineMock()

        await edge_monitoring._process_all_edges()

        assert edge_monitoring._process_edge.await_count == 0

    @pytest.mark.asyncio
    async def process_all_edges_wrong_id_test(self):
        logger = Mock()
        scheduler = Mock()
        request_id = 'random-uuid'
        uuid_1 = uuid()
        uuid_2 = uuid()
        uuid_3 = uuid()

        edge_full_id_1 = {"host": "test_host1", "enterprise_id": 1, "edge_id": "edge-id-1"}
        edge_full_id_2 = {"host": "test_host2", "enterprise_id": 1, "edge_id": "edge-id-2"}

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(
            return_value={'reques_id': request_id, 'body': [edge_full_id_1, edge_full_id_2]})

        edge_list_response = {
            'reques_id': uuid_3,
            'body': [edge_full_id_1, edge_full_id_2],
            'status': 200
        }

        edge_1_status_response = {
            'request_id': uuid_1,
            'body': {
                'edge_id': edge_full_id_1,
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'DISCONNECTED'},
                    'links': [
                        {'link': {'state': 'DISCONNECTED'}},
                        {'link': {'state': 'DISCONNECTED'}},
                    ],
                },
            },
            'status': 200,
        }

        edge_2_status_response = {
            'request_id': uuid_2,
            'body': {
                'edge_id': edge_full_id_1,
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'CONNECTED'},
                    'links': [
                        {'link': {'state': 'DISCONNECTED'}},
                        {'link': {'state': 'CONNECTED'}},
                    ],
                },
            },
            'status': 200,
        }

        prometheus_repository = Mock()
        prometheus_repository.start_prometheus_metrics_server = Mock()
        prometheus_repository.set_cycle_total_edges = Mock()
        prometheus_repository.dec = Mock()
        velocloud_repository = Mock()
        velocloud_repository.get_edges = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response,
            edge_2_status_response,
        ])

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)
        edge_monitoring._process_edge = CoroutineMock()

        await edge_monitoring._process_all_edges()

        assert edge_monitoring._process_edge.await_count == 0

    @pytest.mark.asyncio
    async def process_all_edges_without_cache_data_test(self):
        logger = Mock()
        scheduler = Mock()
        request_id = 'random-uuid'
        uuid_1 = uuid()
        uuid_2 = uuid()
        uuid_3 = uuid()

        event_bus = Mock()
        edge_full_id_1 = {"host": "test_host1", "enterprise_id": 1, "edge_id": "edge-id-1"}
        edge_full_id_2 = {"host": "test_host2", "enterprise_id": 1, "edge_id": "edge-id-2"}
        edge_list_response = {
            'request_id': uuid_3,
            'body': [edge_full_id_1, edge_full_id_2],
            'status': 200
        }
        cache_edge_3_info = {
            'enterprise_name': 'evil-corp',
            'edges': {'edgeState': 'DISCONNECTED'},
            'links': [
                {'link': {'state': 'DISCONNECTED'}},
                {'link': {'state': 'DISCONNECTED'}},
            ],
        }

        cache_edge_4_info = {
            'enterprise_name': 'evil-corp',
            'edges': {'edgeState': 'CONNECTED'},
            'links': [
                {'link': {'state': 'DISCONNECTED'}},
                {'link': {'state': 'CONNECTED'}},
            ],
        }

        edge_1_status_response = {
            'request_id': uuid_1,
            'body': {
                'edge_id': edge_full_id_1,
                'edge_info': cache_edge_3_info,
            },
            'status': 200,
        }

        edge_2_status_response = {
            'request_id': uuid_2,
            'body': {
                'edge_id': edge_full_id_1,
                'edge_info': cache_edge_4_info,
            },
            'status': 200,
        }

        event_bus.rpc_request = CoroutineMock(side_effect=[
            {'request_id': request_id, 'body': [edge_full_id_1, edge_full_id_2]},
        ])

        prometheus_repository = Mock()
        prometheus_repository.start_prometheus_metrics_server = Mock()
        prometheus_repository.set_cycle_total_edges = Mock()
        prometheus_repository.dec = Mock()
        velocloud_repository = Mock()
        velocloud_repository.get_edges = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response,
            edge_2_status_response,
        ])

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)
        edge_monitoring._process_edge = CoroutineMock()

        await edge_monitoring._process_all_edges()

        prometheus_repository.dec.assert_not_called()

    @pytest.mark.asyncio
    async def process_all_edges_with_cache_data_and_no_differences_in_edge_list_test(self):
        logger = Mock()
        scheduler = Mock()
        request_id = 'random-uuid'

        edge_full_id_1 = {"host": "test_host1", "enterprise_id": 1, "edge_id": "edge-id-3"}
        edge_full_id_2 = {"host": "test_host2", "enterprise_id": 1, "edge_id": "edge-id-4"}

        uuid_1 = uuid()
        uuid_2 = uuid()
        uuid_3 = uuid()

        edge_list_response = {
            'request_id': uuid_3,
            'body': [edge_full_id_1, edge_full_id_2],
            'status': 200
        }
        cache_edge_3_info = {
            'enterprise_name': 'evil-corp',
            'edges': {'edgeState': 'DISCONNECTED'},
            'links': [
                {'link': {'state': 'DISCONNECTED'}},
                {'link': {'state': 'DISCONNECTED'}},
            ],
        }

        cache_edge_4_info = {
            'enterprise_name': 'evil-corp',
            'edges': {'edgeState': 'CONNECTED'},
            'links': [
                {'link': {'state': 'DISCONNECTED'}},
                {'link': {'state': 'CONNECTED'}},
            ],
        }

        edge_1_status_response = {
            'request_id': uuid_1,
            'body': {
                'edge_id': edge_full_id_1,
                'edge_info': cache_edge_3_info,
            },
            'status': 200,
        }

        edge_2_status_response = {
            'request_id': uuid_2,
            'body': {
                'edge_id': edge_full_id_1,
                'edge_info': cache_edge_4_info,
            },
            'status': 200,
        }
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value={
            'request_id': request_id, 'body': [edge_full_id_1, edge_full_id_2]
        })

        prometheus_repository = Mock()
        prometheus_repository.start_prometheus_metrics_server = Mock()
        prometheus_repository.set_cycle_total_edges = Mock()
        prometheus_repository.dec = Mock()
        velocloud_repository = Mock()
        velocloud_repository.get_edges = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response,
            edge_2_status_response,
        ])

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)
        edge_monitoring._edges_cache = [
            edge_full_id_1, edge_full_id_2
        ]

        edge_monitoring._status_cache = {
            EdgeIdentifier(**edge_full_id_1): {'request_id': request_id, 'cache_edge': cache_edge_3_info},
            EdgeIdentifier(**edge_full_id_2): {'request_id': request_id, 'cache_edge': cache_edge_4_info}
        }
        edge_monitoring._process_edge = CoroutineMock()

        await edge_monitoring._process_all_edges()

        prometheus_repository.dec.assert_not_called()

    @pytest.mark.asyncio
    async def process_all_edges_with_cache_data_and_differences_in_edge_list_test(self):
        logger = Mock()
        scheduler = Mock()
        request_id = 'random-uuid'
        bruin_client_1 = 12345
        bruin_client_2 = 54321
        uuid_1 = uuid()
        uuid_2 = uuid()
        uuid_3 = uuid()
        edge_1_serial = 'VC1234567'
        edge_full_id_1 = {"host": "test_host1", "enterprise_id": 1, "edge_id": "edge-id-1"}
        edge_full_id_2 = {"host": "test_host2", "enterprise_id": 1, "edge_id": "edge-id-1"}
        edge_full_id_3 = {"host": "test_host3", "enterprise_id": 1, "edge_id": "edge-id-1"}
        edge_full_id_4 = {"host": "test_host4", "enterprise_id": 1, "edge_id": "edge-id-1"}

        edge_list_response = {
            'request_id': uuid_1,
            'body': [edge_full_id_1, edge_full_id_3, edge_full_id_4],
            'status': 200
        }
        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_1_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_1}|',
        }
        edge_1_status_response = {
            'request_id': uuid_2,
            'body': {
                'edge_id': edge_full_id_1,
                'edge_info': edge_1_status,
            },
            'status': 200,
        }

        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_full_id_3},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_2}|',
        }
        edge_3_status_response = {
            'request_id': uuid_3,
            'body': {
                'edge_id': edge_full_id_3,
                'edge_info': edge_3_status,
            },
            'status': 200,
        }

        edge_4_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_full_id_2},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_2}|',
        }

        edge_4_status_response = {
            'request_id': uuid_3,
            'body': {
                'edge_id': edge_full_id_4,
                'edge_info': edge_4_status,
            },
            'status': 200,
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value={
            'request_id': request_id, 'body': [edge_full_id_1, edge_full_id_3, edge_full_id_4]
        })

        prometheus_repository = Mock()
        prometheus_repository.start_prometheus_metrics_server = Mock()
        prometheus_repository.set_cycle_total_edges = Mock()
        prometheus_repository.dec = Mock()
        velocloud_repository = Mock()
        velocloud_repository.get_edges = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response,
            edge_3_status_response,
            edge_4_status_response
        ])

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)
        edge_monitoring._edges_cache = {
            EdgeIdentifier(**edge_full_id_1),
            EdgeIdentifier(**edge_full_id_2)
        }

        edge_monitoring._status_cache = {
            EdgeIdentifier(**edge_full_id_1): {'request_id': request_id, 'cache_edge': edge_full_id_1},
            EdgeIdentifier(**edge_full_id_2): {'request_id': request_id, 'cache_edge': edge_full_id_2}
        }
        edge_monitoring._process_edge = CoroutineMock()

        await edge_monitoring._process_all_edges()

        prometheus_repository.dec.assert_called_once()

    @pytest.mark.asyncio
    async def process_edge_test(self):
        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        edge_id = {"host": "test_host1", "enterprise_id": 1, "edge_id": "edge-id-3"}

        edge_info = {
            'enterprise_name': 'evil-corp',
            'edges': {'edgeState': 'DISCONNECTED'},
            'links': [
                {'link': {'state': 'DISCONNECTED'}},
                {'link': {'state': 'DISCONNECTED'}},
            ],
        }
        velocloud_edge = {
            'request_id': 1234,
            'status': 200,
            'body': {
                'edge_id': edge_id,
                'edge_info': edge_info
            }
        }

        event_bus.rpc_request = CoroutineMock(side_effect=[
            velocloud_edge
        ])

        edge_repository = Mock()
        edge_repository.get_edge = Mock(return_value=None)
        edge_repository.set_current_edge_list = Mock()
        edge_repository.set_edge = Mock()

        prometheus_repository = Mock()
        prometheus_repository.inc = Mock()
        velocloud_repository = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)

        await edge_monitoring._process_edge(velocloud_edge)

    @pytest.mark.asyncio
    async def process_edge_corrupted_body_test(self):
        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()

        edge_id = {"host": "test_host1", "enterprise_id": 1, "edge_id": 1}
        edge_info = {
            'enterprise_name': 'evil-corp',
            'edges': {'edgeState': 'DISCONNECTED'},
            'links': [
                {'link': {'state': 'DISCONNECTED'}},
                {'link': {'state': 'DISCONNECTED'}},
            ],
        }
        velocloud_edge = {
            'request_id': 1234,
            'status': 200,
            'boy': {
                'edge_id': edge_id,
                'edge_info': edge_info
            }
        }

        event_bus.rpc_request = CoroutineMock(side_effect=[
            velocloud_edge
        ])

        prometheus_repository = Mock()
        prometheus_repository.inc = Mock()
        velocloud_repository = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)

        await edge_monitoring._process_edge(velocloud_edge)

    @pytest.mark.asyncio
    async def process_edge_wrong_status_test(self):
        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()

        edge_id = {"host": "test_host1", "enterprise_id": 1, "edge_id": 1}
        edge_info = {
            'enterprise_name': 'evil-corp',
            'edges': {'edgeState': 'DISCONNECTED'},
            'links': [
                {'link': {'state': 'DISCONNECTED'}},
                {'link': {'state': 'DISCONNECTED'}},
            ],
        }
        velocloud_edge = {
            'request_id': 1234,
            'status': 500,
            'body': {
                'edge_id': edge_id,
                'edge_info': edge_info
            }
        }

        event_bus.rpc_request = CoroutineMock(side_effect=[
            velocloud_edge
        ])

        prometheus_repository = Mock()
        prometheus_repository.inc = Mock()
        velocloud_repository = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)

        await edge_monitoring._process_edge(velocloud_edge)

    @pytest.mark.asyncio
    async def process_edge_without_cache_data_test(self):
        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()

        edge_info = {
            'enterprise_name': 'evil-corp',
            'edges': {'edgeState': 'DISCONNECTED'},
            'links': [
                {'link': {'state': 'DISCONNECTED'}},
                {'link': {'state': 'DISCONNECTED'}},
            ],
        }
        edge = {
            'request_id': 1234,
            'status': 200,
            'body': {
                'edge_id': {"host": "test_host1", "enterprise_id": 1, "edge_id": 1},
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'DISCONNECTED'},
                    'links': [
                        {'link': {'state': 'DISCONNECTED'}},
                        {'link': {'state': 'DISCONNECTED'}},
                    ],
                }
            }
        }

        event_bus.rpc_request = CoroutineMock(side_effect=[
            edge
        ])

        prometheus_repository = Mock()
        prometheus_repository.inc = Mock()
        velocloud_repository = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)

        await edge_monitoring._process_edge(edge)

        prometheus_repository.inc.assert_called_once_with(edge_info)

    @pytest.mark.asyncio
    async def process_edge_with_cache_data_and_edge_state_changed_test(self):
        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()

        edge_full_id_1 = {"host": "test_host1", "enterprise_id": 1, "edge_id": "edge-id-3"}
        edge_full_id_2 = {"host": "test_host2", "enterprise_id": 1, "edge_id": "edge-id-4"}

        velocloud_edge = {
            'request_id': 1234,
            'status': 200,
            'body': {
                'edge_id': edge_full_id_1,
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'CONNECTED'},
                    'links': [
                        {'link': {'state': 'DISCONNECTED'}},
                        {'link': {'state': 'DISCONNECTED'}},
                    ],
                }
            }
        }

        cache_edge_info = {
            'enterprise_name': 'evil-corp',
            'edges': {'edgeState': 'DISCONNECTED'},
            'links': [
                {'link': {'state': 'DISCONNECTED'}},
                {'link': {'state': 'DISCONNECTED'}},
            ],
        }
        cache_edge = {
            'request_id': 1234,
            'cache_edge': cache_edge_info,
        }

        event_bus.rpc_request = CoroutineMock(side_effect=[
            velocloud_edge
        ])

        prometheus_repository = Mock()
        prometheus_repository.inc = Mock()
        velocloud_repository = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)
        edge_monitoring._edges_cache = [
            edge_full_id_1
        ]

        edge_monitoring._status_cache = {
            EdgeIdentifier(**edge_full_id_1): {'request_id': 1234, 'cache_edge': cache_edge_info},
            EdgeIdentifier(**edge_full_id_2): {'request_id': 1234, 'cache_edge': cache_edge_info}
        }

        await edge_monitoring._process_edge(velocloud_edge)

        prometheus_repository.update_edge.assert_called_once_with(
            velocloud_edge['body']['edge_info'], cache_edge['cache_edge']
        )

    @pytest.mark.asyncio
    async def process_edge_with_cache_data_and_link_state_changed_test(self):
        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()

        edge_full_id_1 = {"host": "test_host1", "enterprise_id": 1, "edge_id": "edge-id-3"}
        edge_full_id_2 = {"host": "test_host2", "enterprise_id": 1, "edge_id": "edge-id-4"}

        velocloud_edge = {
            'request_id': 1234,
            'status': 200,
            'body': {
                'edge_id': edge_full_id_1,
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': 'CONNECTED'},
                    'links': [
                        {'link': {'state': 'DISCONNECTED'}},
                        {'link': {'state': 'DISCONNECTED'}},
                    ],
                }
            }
        }

        cache_edge_info = {
            'enterprise_name': 'evil-corp',
            'edges': {'edgeState': 'CONNECTED'},
            'links': [
                {'link': {'state': 'CONNECTED'}},
                {'link': {'state': 'DISCONNECTED'}},
            ],
        }

        event_bus.rpc_request = CoroutineMock(side_effect=[
            velocloud_edge
        ])

        prometheus_repository = Mock()
        prometheus_repository.inc = Mock()
        velocloud_repository = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)
        edge_monitoring._edges_cache = [
            edge_full_id_1
        ]

        edge_monitoring._status_cache = {
            EdgeIdentifier(**edge_full_id_1): {'request_id': 1234, 'cache_edge': cache_edge_info},
            EdgeIdentifier(**edge_full_id_2): {'request_id': 1234, 'cache_edge': cache_edge_info}
        }

        await edge_monitoring._process_edge(velocloud_edge)

        prometheus_repository.update_link.assert_called()

    @pytest.mark.asyncio
    async def process_edge_with_no_remaining_edges_test(self):
        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()

        edge_info = {
            'enterprise_name': 'evil-corp',
            'edges': {'edgeState': 'DISCONNECTED'},
            'links': [
                {'link': {'state': 'DISCONNECTED'}},
                {'link': {'state': 'DISCONNECTED'}},
            ],
        }
        edge = {
            'request_id': 1234,
            'status': 200,
            'body':
                {
                    'edge_id': {"host": "test_host1", "enterprise_id": 1, "edge_id": 1},
                    'edge_info': edge_info
                }
        }

        event_bus.rpc_request = CoroutineMock(side_effect=[
            edge
        ])

        prometheus_repository = Mock()
        prometheus_repository.inc = Mock()
        velocloud_repository = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)
        edge_monitoring._edge_monitoring_process = CoroutineMock()

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)

        with patch.object(edge_monitoring_module, 'datetime', new=datetime_mock) as _:
            with patch.object(edge_monitoring_module, 'timezone', new=Mock()) as _:
                await edge_monitoring.start_edge_monitor_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            edge_monitoring._edge_monitoring_process, 'interval',
            seconds=config.SITES_MONITOR_CONFIG['jobs_intervals']['edge_monitor'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_edge_monitoring_process',
        )

    @pytest.mark.asyncio
    async def start_edge_monitor_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        velocloud_repository = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)
        edge_monitoring._edge_monitoring_process = CoroutineMock()

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(edge_monitoring_module, 'datetime', new=datetime_mock) as _:
            with patch.object(edge_monitoring_module, 'timezone', new=Mock()) as _:
                await edge_monitoring.start_edge_monitor_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            edge_monitoring._edge_monitoring_process, 'interval',
            seconds=config.SITES_MONITOR_CONFIG['monitoring_seconds'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_edge_monitoring_process',
        )

    @pytest.mark.asyncio
    async def start_edge_monitor_job_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        velocloud_repository = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)
        edge_monitoring._edge_monitoring_process = CoroutineMock()

        await edge_monitoring.start_edge_monitor_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            edge_monitoring._edge_monitoring_process, 'interval',
            seconds=config.SITES_MONITOR_CONFIG['monitoring_seconds'],
            next_run_time=apscheduler_undefined,
            replace_existing=False,
            id='_edge_monitoring_process',
        )

    @pytest.mark.asyncio
    async def edge_monitoring_process_in_idle_status_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()

        statistic_repository = Mock()
        statistic_repository._statistic_client = Mock()
        statistic_repository._statistic_client.clear_dictionaries = Mock()
        velocloud_repository = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)
        edge_monitoring._process_all_edges = CoroutineMock()

        current_cycle_timestamp = 1000000
        datetime_mock = Mock()
        datetime_mock.timestamp = Mock(return_value=current_cycle_timestamp)
        with patch.object(edge_monitoring_module, 'datetime', new=datetime_mock) as _:
            with patch.object(edge_monitoring_module, 'timezone', new=Mock()) as _:
                await edge_monitoring._edge_monitoring_process()

        edge_monitoring._process_all_edges.assert_awaited_once()

    @pytest.mark.asyncio
    async def edge_monitoring_process_in_processing_status_with_retriggering_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()

        current_timestamp = 100000
        velocloud_repository = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)
        edge_monitoring._process_all_edges = CoroutineMock()

        datetime_mock = Mock()
        datetime_mock.timestamp = Mock(return_value=current_timestamp)
        with patch.object(edge_monitoring_module, 'datetime', new=datetime_mock) as _:
            with patch.object(edge_monitoring_module, 'timezone', new=Mock()) as _:
                await edge_monitoring._edge_monitoring_process()

    @pytest.mark.asyncio
    async def edge_monitoring_process_in_processing_status_with_no_retriggering_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()

        # We make these two values equal so the status is not set to IDLE
        current_timestamp = 50000
        velocloud_repository = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, velocloud_repository,
                                         config)
        edge_monitoring._process_all_edges = CoroutineMock()
        datetime_mock = Mock()
        datetime_mock.timestamp = Mock(return_value=current_timestamp)
        with patch.object(edge_monitoring_module, 'datetime', new=datetime_mock) as _:
            with patch.object(edge_monitoring_module, 'timezone', new=Mock()) as _:
                await edge_monitoring._edge_monitoring_process()

        edge_monitoring._process_all_edges.assert_awaited_once()
