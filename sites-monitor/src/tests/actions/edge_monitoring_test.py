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

    def start_metrics_server_test(self, instance_server):
        instance_server._prometheus_repository.start_prometheus_metrics_server = Mock()

        instance_server.start_prometheus_metrics_server()
        instance_server._prometheus_repository.start_prometheus_metrics_server.assert_called_once()

    @pytest.mark.asyncio
    async def process_all_edges_test(self, instance_server, edge_full_id, edge_response_status):
        request_id = 'random-uuid'

        edge_full_id_1 = edge_full_id['edge_1']
        edge_full_id_2 = edge_full_id['edge_2']

        edge_list_response = {
            'request_id': uuid(),
            'body': [edge_full_id_1, edge_full_id_2],
            'status': 200
        }

        instance_server._event_bus.rpc_request = CoroutineMock(
            return_value={'request_id': request_id, 'body': [edge_full_id_1, edge_full_id_2]})

        instance_server._velocloud_repository.get_edges = CoroutineMock(return_value=edge_list_response)
        instance_server._velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_response_status["edge_status_1"],
            edge_response_status["edge_status_1"],
        ])

        instance_server._process_edge = CoroutineMock()

        await instance_server._process_all_edges()

        assert instance_server._process_edge.await_count == 2

    @pytest.mark.asyncio
    async def process_all_edges_bad_status_test(self, instance_server, edge_full_id,
                                                edge_response_status):
        edge_full_id_1 = edge_full_id['edge_1']
        edge_full_id_2 = edge_full_id['edge_2']

        edge_list_response = {
            'request_id': uuid(),
            'body': [edge_full_id_1, edge_full_id_2],
            'status': 500
        }

        instance_server._event_bus.rpc_request = CoroutineMock(
            return_value={'request_id': 'random-uuid', 'body': [edge_full_id_1, edge_full_id_2]})

        instance_server._velocloud_repository.get_edges = CoroutineMock(return_value=edge_list_response)
        instance_server._velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_response_status["edge_status_1"],
            edge_response_status["edge_status_2"],
        ])

        instance_server._process_edge = CoroutineMock()

        await instance_server._process_all_edges()

        assert instance_server._process_edge.await_count == 0

    @pytest.mark.asyncio
    async def process_all_edges_wrong_id_test(self, instance_server, edge_full_id,
                                              edge_response_status):
        edge_full_id_1 = edge_full_id['edge_1']
        edge_full_id_2 = edge_full_id['edge_2']

        instance_server._event_bus.rpc_request = CoroutineMock(
            return_value={'reques_id': 'random-uuid', 'body': [edge_full_id_1, edge_full_id_2]})

        edge_list_response = {
            'reques_id': uuid(),
            'body': [edge_full_id_1, edge_full_id_2],
            'status': 200
        }

        instance_server._velocloud_repository.get_edges = CoroutineMock(return_value=edge_list_response)
        instance_server._velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_response_status["edge_status_1"],
            edge_response_status["edge_status_2"],
        ])

        instance_server._logger.error = Mock()
        instance_server._process_edge = CoroutineMock()

        await instance_server._process_all_edges()

        instance_server._logger.error.assert_called_once()
        assert instance_server._process_edge.await_count == 0

    @pytest.mark.asyncio
    async def process_all_edges_without_cache_data_test(self, instance_server, edge_full_id,
                                                        edge_response_status):
        edge_full_id_1 = edge_full_id['edge_1']
        edge_full_id_2 = edge_full_id['edge_2']
        edge_list_response = {
            'request_id': uuid(),
            'body': [edge_full_id_1, edge_full_id_2],
            'status': 200
        }

        instance_server._event_bus.rpc_request = CoroutineMock(side_effect=[
            {'request_id': 'random-uuid', 'body': [edge_full_id_1, edge_full_id_2]},
        ])

        instance_server._velocloud_repository.get_edges = CoroutineMock(return_value=edge_list_response)
        instance_server._velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_response_status["edge_status_1"],
            edge_response_status["edge_status_2"],
        ])

        instance_server._process_edge = CoroutineMock()

        await instance_server._process_all_edges()

        instance_server._prometheus_repository.dec.assert_not_called()

    @pytest.mark.asyncio
    async def process_all_edges_with_cache_data_and_no_differences_in_edge_list_test(self, instance_server,
                                                                                     edge_full_id,
                                                                                     edge_response_status):
        edge_full_id_1 = edge_full_id['edge_1']
        edge_full_id_2 = edge_full_id['edge_2']
        request_id = uuid()

        edge_list_response = {
            'request_id': request_id,
            'body': [edge_full_id_1, edge_full_id_2],
            'status': 200
        }
        instance_server._event_bus.rpc_request = CoroutineMock(return_value={
            'request_id': 'random-uuid', 'body': [edge_full_id_1, edge_full_id_2]
        })

        instance_server._velocloud_repository.get_edges = CoroutineMock(return_value=edge_list_response)
        instance_server._velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_response_status["edge_status_1"],
            edge_response_status["edge_status_2"],
        ])

        instance_server._edges_cache = [
            edge_full_id_1, edge_full_id_2
        ]

        instance_server._status_cache = {
            EdgeIdentifier(**edge_full_id_1): {'request_id': request_id,
                                               'cache_edge': edge_response_status["edge_status_1"]['body'][
                                                   'edge_info']},
            EdgeIdentifier(**edge_full_id_2): {'request_id': request_id,
                                               'cache_edge': edge_response_status["edge_status_2"]['body'][
                                                   'edge_info']}
        }
        instance_server._process_edge = CoroutineMock()

        await instance_server._process_all_edges()

        instance_server._prometheus_repository.dec.assert_not_called()

    @pytest.mark.asyncio
    async def process_all_edges_with_cache_data_and_differences_in_edge_list_test(self, instance_server,
                                                                                  edge_full_id,
                                                                                  edge_response_status):
        uuid_1 = uuid()
        edge_full_id_1 = edge_full_id['edge_1']
        edge_full_id_2 = edge_full_id['edge_2']
        edge_full_id_3 = edge_full_id['edge_3']

        edge_list_response = {
            'request_id': uuid_1,
            'body': [edge_full_id_1, edge_full_id_3, edge_full_id_3],
            'status': 200
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value={
            'request_id': 'random-uuid', 'body': [edge_full_id_1, edge_full_id_3, edge_full_id_3]
        })

        instance_server._velocloud_repository.get_edges = CoroutineMock(
            return_value=edge_list_response)
        instance_server._velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_response_status["edge_status_1"],
            edge_response_status["edge_status_2"],
            edge_response_status["edge_status_3"],
        ])

        instance_server._edges_cache = {
            EdgeIdentifier(**edge_full_id_1),
            EdgeIdentifier(**edge_full_id_2),
            EdgeIdentifier(**edge_full_id_3)
        }

        instance_server._status_cache = {
            EdgeIdentifier(**edge_full_id_1): {'request_id': 'random-uuid',
                                               'cache_edge': edge_response_status["edge_status_1"]['body'][
                                                   'edge_info']},
            EdgeIdentifier(**edge_full_id_2): {'request_id': 'random-uuid',
                                               'cache_edge': edge_response_status["edge_status_2"]['body'][
                                                   'edge_info']}
        }
        instance_server._process_edge = CoroutineMock()

        await instance_server._process_all_edges()

        instance_server._prometheus_repository.dec.assert_called_once()

    @pytest.mark.asyncio
    async def process_edge_test(self, instance_server, edge_response_status):
        instance_server._event_bus.rpc_request = CoroutineMock(side_effect=[
            edge_response_status["edge_status_1"]
        ])

        await instance_server._process_edge(edge_response_status["edge_status_1"])

        instance_server._prometheus_repository.inc.assert_called_once()

    @pytest.mark.asyncio
    async def process_edge_corrupted_body_test(self, instance_server, edge_response_status):
        instance_server._event_bus.rpc_request = CoroutineMock(side_effect=[
            edge_response_status["edge_status_5"]
        ])

        await instance_server._process_edge(edge_response_status["edge_status_5"])

        instance_server._logger.error.assert_called_once()
        assert instance_server._logger.error.called

    @pytest.mark.asyncio
    async def process_edge_wrong_status_test(self, instance_server, edge_response_status):
        instance_server._event_bus.rpc_request = CoroutineMock(side_effect=[
            edge_response_status["edge_status_4"]
        ])

        await instance_server._process_edge(edge_response_status["edge_status_4"])

        instance_server._prometheus_repository.dec.assert_not_called()
        instance_server._prometheus_repository.inc.assert_not_called()
        instance_server._prometheus_repository.update_edge.assert_not_called()
        instance_server._prometheus_repository.update_link.assert_not_called()

    @pytest.mark.asyncio
    async def process_edge_without_cache_data_test(self, instance_server, edge_response_status):
        instance_server._event_bus.rpc_request = CoroutineMock(side_effect=[
            edge_response_status["edge_status_2"]
        ])

        await instance_server._process_edge(edge_response_status["edge_status_2"])

        instance_server._prometheus_repository.inc.assert_called_once_with(
            edge_response_status["edge_status_2"]["body"]["edge_info"])

    @pytest.mark.asyncio
    async def process_edge_with_cache_data_and_edge_state_changed_test(self, instance_server, edge_full_id,
                                                                       edge_response_status):
        edge_full_id_1 = edge_full_id['edge_1']
        edge_full_id_2 = edge_full_id['edge_2']

        instance_server._event_bus.rpc_request = CoroutineMock(side_effect=[
            edge_response_status["edge_status_1"]
        ])

        instance_server._edges_cache = [
            edge_full_id_1
        ]

        instance_server._status_cache = {
            EdgeIdentifier(**edge_full_id_1): {'request_id': 'random-uuid',
                                               'cache_edge':
                                                   edge_response_status["edge_status_1_state_change"]['body'][
                                                       'edge_info']},
            EdgeIdentifier(**edge_full_id_2): {'request_id': 'random-uuid',
                                               'cache_edge': edge_response_status["edge_status_2"]['body'][
                                                   'edge_info']}
        }

        await instance_server._process_edge(edge_response_status["edge_status_1"])

        instance_server._prometheus_repository.update_edge.assert_called_once_with(
            edge_response_status["edge_status_1"]['body']['edge_info'],
            edge_response_status["edge_status_1_state_change"]['body']['edge_info']
        )

    @pytest.mark.asyncio
    async def process_edge_with_cache_data_and_edge_state_no_changed_test(self, instance_server, edge_full_id,
                                                                          edge_response_status):
        edge_full_id_1 = edge_full_id['edge_1']
        edge_full_id_2 = edge_full_id['edge_2']

        instance_server._event_bus.rpc_request = CoroutineMock(side_effect=[
            edge_response_status["edge_status_1"]
        ])

        instance_server._edges_cache = [
            edge_full_id_1
        ]

        instance_server._status_cache = {
            EdgeIdentifier(**edge_full_id_1): {'request_id': 'random-uuid',
                                               'cache_edge':
                                                   edge_response_status["edge_status_1"]['body'][
                                                       'edge_info']},
            EdgeIdentifier(**edge_full_id_2): {'request_id': 'random-uuid',
                                               'cache_edge': edge_response_status["edge_status_2"]['body'][
                                                   'edge_info']}
        }

        await instance_server._process_edge(edge_response_status["edge_status_1"])

        instance_server._prometheus_repository.update_edge.assert_not_called()

    @pytest.mark.asyncio
    async def process_edge_with_cache_data_and_link_state_changed_test(self, instance_server, edge_full_id,
                                                                       edge_response_status):
        edge_full_id_1 = edge_full_id['edge_1']
        edge_full_id_2 = edge_full_id['edge_2']

        instance_server._event_bus.rpc_request = CoroutineMock(side_effect=[
            edge_response_status["edge_status_2"]
        ])

        instance_server._edges_cache = [
            edge_full_id_2
        ]

        instance_server._status_cache = {
            EdgeIdentifier(**edge_full_id_1): {'request_id': 'random-uuid',
                                               'cache_edge':
                                                   edge_response_status["edge_status_2_link_change"]['body'][
                                                       'edge_info']},
            EdgeIdentifier(**edge_full_id_2): {'request_id': 'random-uuid',
                                               'cache_edge': edge_response_status["edge_status_1"]['body'][
                                                   'edge_info']}
        }

        await instance_server._process_edge(edge_response_status["edge_status_2"])

        instance_server._prometheus_repository.update_link.assert_called()

    @pytest.mark.asyncio
    async def process_edge_with_no_remaining_edges_test(self, instance_server, edge_response_status):
        instance_server._event_bus.rpc_request = CoroutineMock(side_effect=[
            edge_response_status["edge_status_1"]
        ])

        instance_server._edge_monitoring_process = CoroutineMock()

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)

        with patch.object(edge_monitoring_module, 'datetime', new=datetime_mock) as _:
            with patch.object(edge_monitoring_module, 'timezone', new=Mock()) as _:
                await instance_server.start_edge_monitor_job(exec_on_start=True)

        instance_server._scheduler.add_job.assert_called_once_with(
            instance_server._edge_monitoring_process, 'interval',
            seconds=config.SITES_MONITOR_CONFIG['jobs_intervals']['edge_monitor'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_edge_monitoring_process',
        )

    @pytest.mark.asyncio
    async def start_edge_monitor_job_with_exec_on_start_test(self, instance_server):
        instance_server._edge_monitoring_process = CoroutineMock()

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(edge_monitoring_module, 'datetime', new=datetime_mock) as _:
            with patch.object(edge_monitoring_module, 'timezone', new=Mock()) as _:
                await instance_server.start_edge_monitor_job(exec_on_start=True)

        instance_server._scheduler.add_job.assert_called_once_with(
            instance_server._edge_monitoring_process, 'interval',
            seconds=config.SITES_MONITOR_CONFIG['monitoring_seconds'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_edge_monitoring_process',
        )

    @pytest.mark.asyncio
    async def start_edge_monitor_job_with_no_exec_on_start_test(self, instance_server):
        instance_server._edge_monitoring_process = CoroutineMock()

        await instance_server.start_edge_monitor_job(exec_on_start=False)

        instance_server._scheduler.add_job.assert_called_once_with(
            instance_server._edge_monitoring_process, 'interval',
            seconds=config.SITES_MONITOR_CONFIG['monitoring_seconds'],
            next_run_time=apscheduler_undefined,
            replace_existing=False,
            id='_edge_monitoring_process',
        )

    @pytest.mark.asyncio
    async def edge_monitoring_process_in_idle_status_test(self, instance_server):
        instance_server._process_all_edges = CoroutineMock()

        current_cycle_timestamp = 1000000
        datetime_mock = Mock()
        datetime_mock.timestamp = Mock(return_value=current_cycle_timestamp)
        with patch.object(edge_monitoring_module, 'datetime', new=datetime_mock) as _:
            with patch.object(edge_monitoring_module, 'timezone', new=Mock()) as _:
                await instance_server._edge_monitoring_process()

        instance_server._process_all_edges.assert_awaited_once()

    @pytest.mark.asyncio
    async def edge_monitoring_process_in_processing_status_with_retriggering_test(self, instance_server):
        instance_server._process_all_edges = CoroutineMock()

        datetime_mock = Mock()
        datetime_mock.timestamp = Mock(return_value=100000)
        with patch.object(edge_monitoring_module, 'datetime', new=datetime_mock) as _:
            with patch.object(edge_monitoring_module, 'timezone', new=Mock()) as _:
                await instance_server._edge_monitoring_process()

    @pytest.mark.asyncio
    async def edge_monitoring_process_in_processing_status_with_no_retriggering_test(self, instance_server):
        instance_server._process_all_edges = CoroutineMock()
        datetime_mock = Mock()
        datetime_mock.timestamp = Mock(return_value=50000)
        with patch.object(edge_monitoring_module, 'datetime', new=datetime_mock) as _:
            with patch.object(edge_monitoring_module, 'timezone', new=Mock()) as _:
                await instance_server._edge_monitoring_process()

        instance_server._process_all_edges.assert_awaited_once()
