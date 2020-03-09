import json
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest
from application.actions.edge_monitoring import EdgeMonitoring
from apscheduler.util import undefined as apscheduler_undefined
from asynctest import CoroutineMock

from application.actions import edge_monitoring as edge_monitoring_module
from config import testconfig


class TestEdgeMonitoring:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        status_repository = Mock()
        config = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)
        assert isinstance(edge_monitoring, EdgeMonitoring)
        assert edge_monitoring._event_bus is event_bus
        assert edge_monitoring._logger is logger
        assert edge_monitoring._prometheus_repository is prometheus_repository
        assert edge_monitoring._scheduler is scheduler
        assert edge_monitoring._edge_repository is edge_repository
        assert edge_monitoring._status_repository is status_repository
        assert edge_monitoring._config is config

    def start_metrics_server_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        status_repository = Mock()
        config = Mock()

        prometheus_repository = Mock()
        prometheus_repository.start_prometheus_metrics_server = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)
        edge_monitoring.start_prometheus_metrics_server()
        prometheus_repository.start_prometheus_metrics_server.assert_called_once()

    @pytest.mark.asyncio
    async def process_all_edges_test(self):
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        request_id = 'random-uuid'

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[
            {'request_id': request_id, 'body': ["test_host1", "test_host2", "test_host3"]},
            {
                'request_id': request_id,
                'status': 200,
                'body': {
                    'edge_id': {'host': 'test_host1'},
                    'edge_info': {
                        'enterprise_name': 'evil-corp',
                        'edges': {'edgeState': 'DISCONNECTED'},
                        'links': [
                            {'link': {'state': 'DISCONNECTED'}},
                            {'link': {'state': 'DISCONNECTED'}},
                        ],
                    }
                }
            },
            {
                'request_id': request_id,
                'status': 200,
                'body':
                    {
                        'edge_id': {'host': 'test_host2'},
                        'edge_info': {
                            'enterprise_name': 'evil-corp',
                            'edges': {'edgeState': 'CONNECTED'},
                            'links': [
                                {'link': {'state': 'DISCONNECTED'}},
                                {'link': {'state': 'CONNECTED'}},
                            ],
                        }
                    }

            },
            {
                'request_id': request_id,
                'status': 500,
                'body': None
            }
        ])

        edge_repository = Mock()
        edge_repository.get_last_edge_list = Mock(
            return_value=json.dumps(["test_host1", "test_host2"])
        )
        edge_repository.set_current_edge_list = Mock()

        prometheus_repository = Mock()
        prometheus_repository.start_prometheus_metrics_server = Mock()
        prometheus_repository.set_cycle_total_edges = Mock()
        prometheus_repository.dec = Mock()

        status_repository = Mock()
        status_repository.set_edges_to_process = Mock()
        status_repository.set_current_cycle_request_id = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)
        edge_monitoring._process_edge = CoroutineMock()

        await edge_monitoring._process_all_edges(request_id=request_id)

        status_repository.set_current_cycle_request_id.assert_called_once_with(request_id)
        prometheus_repository.set_cycle_total_edges.assert_called_once()
        status_repository.set_edges_to_process.assert_called_once()
        edge_repository.get_edge.assert_not_called()
        prometheus_repository.dec.assert_not_called()
        edge_repository.set_current_edge_list.assert_called_once()

        event_bus.rpc_request.assert_has_awaits([
            call("edge.list.request", {'request_id': request_id, 'body': {'filter': {}}}, timeout=200),
            call("edge.status.request", {'request_id': request_id, 'body': "test_host1"}, timeout=10),
            call("edge.status.request", {'request_id': request_id, 'body': "test_host2"}, timeout=10),
        ], any_order=False)
        assert edge_monitoring._process_edge.await_count == 2

    @pytest.mark.asyncio
    async def process_all_edges_without_cache_data_test(self):
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        request_id = 'random-uuid'

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[
            {'request_id': request_id, 'body': ["test_host1", "test_host2"]},
            {
                'request_id': request_id,
                'status': 200,
                'body':
                    {
                        'edge_id': {'host': 'test_host1'},
                        'edge_info': {
                            'enterprise_name': 'evil-corp',
                            'edges': {'edgeState': 'DISCONNECTED'},
                            'links': [
                                {'link': {'state': 'DISCONNECTED'}},
                                {'link': {'state': 'CONNECTED'}},
                            ],
                        }
                    }
            },
            {
                'request_id': request_id,
                'status': 200,
                'body':
                    {
                        'edge_id': {'host': 'test_host2'},
                        'edge_info': {
                            'enterprise_name': 'evil-corp',
                            'edges': {'edgeState': 'CONNECTED'},
                            'links': [
                                {'link': {'state': 'DISCONNECTED'}},
                                {'link': {'state': 'DISCONNECTED'}},
                            ],
                        }
                    }
            },
        ])

        edge_repository = Mock()
        edge_repository.get_last_edge_list = Mock(return_value=None)
        edge_repository.set_current_edge_list = Mock()

        prometheus_repository = Mock()
        prometheus_repository.start_prometheus_metrics_server = Mock()
        prometheus_repository.set_cycle_total_edges = Mock()
        prometheus_repository.dec = Mock()

        status_repository = Mock()
        status_repository.set_edges_to_process = Mock()
        status_repository.set_current_cycle_request_id = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)
        edge_monitoring._process_edge = CoroutineMock()

        await edge_monitoring._process_all_edges(request_id=request_id)

        edge_repository.get_edge.assert_not_called()
        prometheus_repository.dec.assert_not_called()

    @pytest.mark.asyncio
    async def process_all_edges_with_cache_data_test(self):
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        request_id = 'random-uuid'

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

        cache_edge_5_info = {
            'enterprise_name': 'evil-corp',
            'edges': {'edgeState': 'CONNECTED'},
            'links': [
                {'link': {'state': 'CONNECTED'}},
                {'link': {'state': 'CONNECTED'}},
            ],
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[
            {'request_id': request_id, 'body': ["test_host1", "test_host2"]},
            {
                'request_id': request_id,
                'status': 200,
                'body':
                    {
                        'edge_id': {'host': 'test_host1'},
                        'edge_info': {
                            'enterprise_name': 'evil-corp',
                            'edges': {'edgeState': 'DISCONNECTED'},
                            'links': [
                                {'link': {'state': 'DISCONNECTED'}},
                                {'link': {'state': 'CONNECTED'}},
                            ],
                        },
                    }
            },
            {
                'request_id': request_id,
                'status': 200,
                'body':
                    {
                        'edge_id': {'host': 'test_host2'},
                        'edge_info': {
                            'enterprise_name': 'evil-corp',
                            'edges': {'edgeState': 'CONNECTED'},
                            'links': [
                                {'link': {'state': 'DISCONNECTED'}},
                                {'link': {'state': 'DISCONNECTED'}},
                            ],
                        }
                    }
            },
        ])

        edge_repository = Mock()
        # Let's simulate that the Cache has data that was not included within the
        # response to the RPC request targeting at edge.list.request topic
        edge_repository.get_last_edge_list = Mock(
            return_value=json.dumps(["edge-id-3", "edge-id-4", "edge-id-5"])
        )
        edge_repository.get_edge = Mock(side_effect=[
            json.dumps({'request_id': request_id, 'cache_edge': cache_edge_3_info}),
            json.dumps({'request_id': request_id, 'cache_edge': cache_edge_4_info}),
            json.dumps({'request_id': request_id, 'cache_edge': cache_edge_5_info}),
        ])
        edge_repository.set_current_edge_list = Mock()

        prometheus_repository = Mock()
        prometheus_repository.start_prometheus_metrics_server = Mock()
        prometheus_repository.set_cycle_total_edges = Mock()
        prometheus_repository.dec = Mock()

        status_repository = Mock()
        status_repository.set_edges_to_process = Mock()
        status_repository.set_current_cycle_request_id = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)
        edge_monitoring._process_edge = CoroutineMock()

        await edge_monitoring._process_all_edges(request_id=request_id)

        edge_repository.get_edge.assert_has_calls([
            call('edge-id-3'), call('edge-id-4'), call('edge-id-5')
        ], any_order=True)
        prometheus_repository.dec.assert_has_calls([
            call(cache_edge_3_info),
            call(cache_edge_4_info),
            call(cache_edge_5_info),
        ], any_order=True)

    @pytest.mark.asyncio
    async def process_all_edges_with_cache_data_equal_to_velocloud_data_test(self):
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        request_id = 'random-uuid'

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[
            {'request_id': request_id, 'body': ["test_host1", "test_host2"]},
            {
                'request_id': request_id,
                'status': 200,
                'body':
                    {
                        'edge_id': {'host': 'test_host1'},
                        'edge_info': {
                            'enterprise_name': 'evil-corp',
                            'edges': {'edgeState': 'CONNECTED'},
                            'links': [
                                {'link': {'state': 'DISCONNECTED'}},
                                {'link': {'state': 'CONNECTED'}},
                            ],
                        }
                    },
            },
            {
                'request_id': request_id,
                'status': 200,
                'body':
                    {
                        'edge_id': {'host': 'test_host2'},
                        'edge_info': {
                            'enterprise_name': 'evil-corp',
                            'edges': {'edgeState': 'DISCONNECTED'},
                            'links': [
                                {'link': {'state': 'DISCONNECTED'}},
                                {'link': {'state': 'DISCONNECTED'}},
                            ],
                        }
                    }
            },
        ])

        edge_repository = Mock()
        edge_repository.get_last_edge_list = Mock(
            return_value=json.dumps(["test_host1", "test_host2"])
        )
        edge_repository.set_current_edge_list = Mock()

        prometheus_repository = Mock()
        prometheus_repository.start_prometheus_metrics_server = Mock()
        prometheus_repository.set_cycle_total_edges = Mock()
        prometheus_repository.dec = Mock()

        status_repository = Mock()
        status_repository.set_edges_to_process = Mock()
        status_repository.set_current_cycle_request_id = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)
        edge_monitoring._process_edge = CoroutineMock()

        await edge_monitoring._process_all_edges(request_id=request_id)

        edge_repository.get_edge.assert_not_called()
        prometheus_repository.dec.assert_not_called()

    @pytest.mark.asyncio
    async def process_edge_test(self):
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        event_bus = Mock()

        edge_id = {'host': 'test_host1'}
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
        cache_edge = {
            'request_id': 1234,
            'cache_edge': edge_info,
        }

        edge_repository = Mock()
        edge_repository.get_edge = Mock(return_value=None)
        edge_repository.set_current_edge_list = Mock()
        edge_repository.set_edge = Mock()

        prometheus_repository = Mock()
        prometheus_repository.inc = Mock()

        status_repository = Mock()
        status_repository.get_edges_to_process = Mock(return_value=10)
        status_repository.get_edges_processed = Mock(return_value=5)
        status_repository.set_edges_processed = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)

        await edge_monitoring._process_edge(velocloud_edge)

        status_repository.get_edges_to_process.assert_called_once()
        status_repository.get_edges_processed.assert_called_once()
        status_repository.set_edges_processed.assert_called_once_with(
            status_repository.get_edges_processed.return_value + 1
        )
        edge_repository.set_edge.assert_called_once_with(
            edge_id, json.dumps(cache_edge)
        )

    @pytest.mark.asyncio
    async def process_edge_without_cache_data_test(self):
        logger = Mock()
        scheduler = Mock()
        config = Mock()
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
                'edge_id': {'host': 'test_host1'},
                'edge_info': edge_info
            }
        }

        edge_repository = Mock()
        edge_repository.get_edge = Mock(return_value=None)
        edge_repository.set_current_edge_list = Mock()
        edge_repository.set_edge = Mock()

        prometheus_repository = Mock()
        prometheus_repository.inc = Mock()

        status_repository = Mock()
        status_repository.get_edges_to_process = Mock(return_value=10)
        status_repository.get_edges_processed = Mock(return_value=5)
        status_repository.set_edges_processed = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)

        await edge_monitoring._process_edge(edge)

        prometheus_repository.inc.assert_called_once_with(edge_info)

    @pytest.mark.asyncio
    async def process_edge_with_cache_data_and_edge_state_changed_test(self):
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        event_bus = Mock()

        velocloud_edge_state = 'CONNECTED'
        cache_edge_state = 'DISCONNECTED'

        velocloud_edge = {
            'request_id': 1234,
            'status': 200,
            'body': {
                'edge_id': {'host': 'test_host1'},
                'edge_info': {
                    'enterprise_name': 'evil-corp',
                    'edges': {'edgeState': velocloud_edge_state},
                    'links': [
                        {'link': {'state': 'DISCONNECTED'}},
                        {'link': {'state': 'DISCONNECTED'}},
                    ],
                }
            }
        }

        cache_edge_info = {
            'enterprise_name': 'evil-corp',
            'edges': {'edgeState': cache_edge_state},
            'links': [
                {'link': {'state': 'DISCONNECTED'}},
                {'link': {'state': 'DISCONNECTED'}},
            ],
        }
        cache_edge = {
            'request_id': 1234,
            'cache_edge': cache_edge_info,
        }

        edge_repository = Mock()
        edge_repository.get_edge = Mock(return_value=json.dumps({
            'cache_edge': cache_edge_info,
        }))
        edge_repository.set_current_edge_list = Mock()
        edge_repository.set_edge = Mock()

        prometheus_repository = Mock()
        prometheus_repository.inc = Mock()

        status_repository = Mock()
        status_repository.get_edges_to_process = Mock(return_value=10)
        status_repository.get_edges_processed = Mock(return_value=5)
        status_repository.set_edges_processed = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)

        await edge_monitoring._process_edge(velocloud_edge)

        prometheus_repository.update_edge.assert_called_once_with(
            velocloud_edge['body']['edge_info'], cache_edge['cache_edge']
        )

    @pytest.mark.asyncio
    async def process_edge_with_cache_data_and_link_state_changed_test(self):
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        event_bus = Mock()

        velocloud_link_1_state = 'DISCONNECTED'
        velocloud_link_2_state = 'CONNECTED'
        cache_link_1_state = 'CONNECTED'
        cache_link_2_state = 'DISCONNECTED'

        velocloud_link_1 = {'link': {'state': velocloud_link_1_state}}
        velocloud_link_2 = {'link': {'state': velocloud_link_2_state}}
        cache_link_1 = {'link': {'state': cache_link_1_state}}
        cache_link_2 = {'link': {'state': cache_link_2_state}}

        velocloud_edge = {
            'request_id': 1234,
            'status': 200,
            'body':
                {
                    'edge_id': {'host': 'test_host1'},
                    'edge_info': {
                        'enterprise_name': 'evil-corp',
                        'edges': {'edgeState': 'CONNECTED'},
                        'links': [velocloud_link_1, velocloud_link_2],
                    }
                }
        }

        cache_edge_info = {
            'enterprise_name': 'evil-corp',
            'edges': {'edgeState': 'CONNECTED'},
            'links': [cache_link_1, cache_link_2],
        }
        cache_edge = {
            'request_id': 1234,
            'cache_edge': cache_edge_info,
        }

        edge_repository = Mock()
        edge_repository.get_edge = Mock(return_value=json.dumps({
            'cache_edge': cache_edge_info,
        }))
        edge_repository.set_current_edge_list = Mock()
        edge_repository.set_edge = Mock()

        prometheus_repository = Mock()
        prometheus_repository.update_link = Mock()

        status_repository = Mock()
        status_repository.get_edges_to_process = Mock(return_value=10)
        status_repository.get_edges_processed = Mock(return_value=5)
        status_repository.set_edges_processed = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)

        await edge_monitoring._process_edge(velocloud_edge)

        prometheus_repository.update_link.assert_has_calls([
            call(
                velocloud_edge['body']['edge_info'], velocloud_link_1,
                cache_edge['cache_edge'], cache_link_1,
            ),
            call(
                velocloud_edge['body']['edge_info'], velocloud_link_2,
                cache_edge['cache_edge'], cache_link_2,
            ),
        ])

    @pytest.mark.asyncio
    async def process_edge_with_no_remaining_edges_test(self):
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        event_bus = Mock()

        edge = {
            'request_id': 1234,
            'status': 200,
            'body':
                {
                    'edge_id': {'host': 'test_host1'},
                    'edge_info': {
                        'enterprise_name': 'evil-corp',
                        'edges': {'edgeState': 'DISCONNECTED'},
                        'links': [
                            {'link': {'state': 'DISCONNECTED'}},
                            {'link': {'state': 'DISCONNECTED'}},
                        ],
                    },
                }
        }

        edges_processed = 9  # We are processing the last remaining edge
        edges_to_process = 10

        edge_repository = Mock()
        edge_repository.get_edge = Mock(return_value=None)
        edge_repository.set_current_edge_list = Mock()
        edge_repository.set_edge = Mock()

        prometheus_repository = Mock()
        prometheus_repository.inc = Mock()

        status_repository = Mock()
        status_repository.get_edges_to_process = Mock(return_value=edges_to_process)
        status_repository.get_edges_processed = Mock(return_value=edges_processed)
        status_repository.set_edges_processed = Mock()
        status_repository.set_status = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)
        edge_monitoring._edge_monitoring_process = CoroutineMock()

        await edge_monitoring._process_edge(edge)

        status_repository.set_status.assert_called_once_with("IDLE")
        edge_monitoring._edge_monitoring_process.assert_awaited_once()

    @pytest.mark.asyncio
    async def start_edge_monitor_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        edge_repository = Mock()
        status_repository = Mock()
        config = testconfig

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)
        edge_monitoring._edge_monitoring_process = CoroutineMock()

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(edge_monitoring_module, 'datetime', new=datetime_mock) as _:
            with patch.object(edge_monitoring_module, 'timezone', new=Mock()) as _:
                await edge_monitoring.start_edge_monitor_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            edge_monitoring._edge_monitoring_process, 'interval',
            seconds=testconfig.SITES_MONITOR_CONFIG['monitoring_seconds'],
            next_run_time=next_run_time,
            replace_existing=True,
            id='_edge_monitoring_process',
        )

    @pytest.mark.asyncio
    async def start_edge_monitor_job_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        edge_repository = Mock()
        status_repository = Mock()
        config = testconfig

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)
        edge_monitoring._edge_monitoring_process = CoroutineMock()

        await edge_monitoring.start_edge_monitor_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            edge_monitoring._edge_monitoring_process, 'interval',
            seconds=testconfig.SITES_MONITOR_CONFIG['monitoring_seconds'],
            next_run_time=apscheduler_undefined,
            replace_existing=True,
            id='_edge_monitoring_process',
        )

    @pytest.mark.asyncio
    async def edge_monitoring_process_in_idle_status_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        config = testconfig

        edge_monitoring_status = "IDLE"

        status_repository = Mock()
        status_repository.get_status = Mock(return_value=edge_monitoring_status)
        status_repository.set_status = Mock()
        status_repository.set_edges_processed = Mock()
        status_repository.set_current_cycle_timestamp = Mock()

        statistic_repository = Mock()
        statistic_repository._statistic_client = Mock()
        statistic_repository._statistic_client.clear_dictionaries = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)
        edge_monitoring._process_all_edges = CoroutineMock()

        current_cycle_timestamp = 1000000
        datetime_mock = Mock()
        datetime_mock.timestamp = Mock(return_value=current_cycle_timestamp)
        with patch.object(edge_monitoring_module, 'datetime', new=datetime_mock) as _:
            with patch.object(edge_monitoring_module, 'timezone', new=Mock()) as _:
                await edge_monitoring._edge_monitoring_process()

        status_repository.get_status.assert_called()
        status_repository.set_edges_processed.assert_called_once_with(0)
        status_repository.set_current_cycle_timestamp.assert_called_once_with(
            current_cycle_timestamp
        )
        edge_monitoring._process_all_edges.assert_awaited_once()
        status_repository.set_status.assert_has_calls([
            call("REQUESTING_VELOCLOUD_EDGES"),
            call("PROCESSING_VELOCLOUD_EDGES"),
        ], any_order=False)

    @pytest.mark.asyncio
    async def edge_monitoring_process_in_processing_status_with_retriggering_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        config = testconfig

        current_timestamp = 100000
        current_cycle_timestamp = 50000

        status_repository = Mock()
        status_repository.get_status = Mock(side_effect=[
            "PROCESSING_VELOCLOUD_EDGES", "IDLE"
        ])
        status_repository.set_status = Mock()
        status_repository.get_edges_processed = Mock()
        status_repository.set_edges_processed = Mock()
        status_repository.get_edges_to_process = Mock()
        status_repository.get_current_cycle_timestamp = Mock(return_value=current_cycle_timestamp)
        status_repository.set_current_cycle_timestamp = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)
        edge_monitoring._process_all_edges = CoroutineMock()

        datetime_mock = Mock()
        datetime_mock.timestamp = Mock(return_value=current_timestamp)
        with patch.object(edge_monitoring_module, 'datetime', new=datetime_mock) as _:
            with patch.object(edge_monitoring_module, 'timezone', new=Mock()) as _:
                await edge_monitoring._edge_monitoring_process()

        status_repository.get_status.assert_called()
        status_repository.get_edges_processed.assert_called_once()
        status_repository.get_edges_to_process.assert_called_once()
        status_repository.get_current_cycle_timestamp.assert_called_once()
        edge_monitoring._process_all_edges.assert_awaited_once()
        status_repository.set_status.assert_has_calls([
            call("IDLE"),
            call("REQUESTING_VELOCLOUD_EDGES"),
            call("PROCESSING_VELOCLOUD_EDGES"),
        ], any_order=False)

    @pytest.mark.asyncio
    async def edge_monitoring_process_in_processing_status_with_no_retriggering_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        config = testconfig

        # We make these two values equal so the status is not set to IDLE
        current_timestamp = 50000
        current_cycle_timestamp = current_timestamp

        status_repository = Mock()
        status_repository.get_status = Mock(return_value="PROCESSING_VELOCLOUD_EDGES")
        status_repository.set_status = Mock()
        status_repository.get_edges_processed = Mock()
        status_repository.get_edges_to_process = Mock()
        status_repository.get_current_cycle_timestamp = Mock(return_value=current_cycle_timestamp)

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, config)
        edge_monitoring._process_all_edges = CoroutineMock()

        datetime_mock = Mock()
        datetime_mock.timestamp = Mock(return_value=current_timestamp)
        with patch.object(edge_monitoring_module, 'datetime', new=datetime_mock) as _:
            with patch.object(edge_monitoring_module, 'timezone', new=Mock()) as _:
                await edge_monitoring._edge_monitoring_process()

        status_repository.get_status.assert_called()
        status_repository.get_edges_processed.assert_called_once()
        status_repository.get_edges_to_process.assert_called_once()
        status_repository.get_current_cycle_timestamp.assert_called_once()
        edge_monitoring._process_all_edges.assert_not_awaited()
        status_repository.set_status.assert_not_called()
