import json
from typing import Dict
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


uuid_ = uuid()
uuid_mock = patch.object(edge_monitoring_module, 'uuid', return_value=uuid_)


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
    async def process_all_edges_test(self, instance_server, links_host_1_response, links_host_2_response,
                                     links_host_3_response, links_host_4_response, edge_1_host_1,
                                     edge_2_host_1, edge_identifier_1_host_1, edge_identifier_2_host_1,
                                     edge_identifier_1_host_2, edge_1_host_2, edge_identifier_1_host_3,
                                     edge_1_host_3, edge_identifier_1_host_4, edge_1_host_4
                                     ):
        all_links = links_host_1_response['body'] + links_host_2_response['body'] + \
                    links_host_3_response['body'] + links_host_4_response['body']
        response = {
            'request_id': uuid_,
            'status': 200,
            'body': all_links
        }

        instance_server._velocloud_repository.get_all_links_with_edge_info = CoroutineMock(side_effect=[response])
        instance_server._prometheus_repository.set_cycle_total_edges = Mock()
        instance_server._process_edge = CoroutineMock()
        with uuid_mock:
            await instance_server._process_all_edges()

        instance_server._velocloud_repository.get_all_links_with_edge_info.assert_awaited_once()
        instance_server._prometheus_repository.set_cycle_total_edges.assert_called_once_with(5)
        instance_server._process_edge.assert_has_awaits([
            call(edge_identifier_1_host_1, edge_1_host_1),
            call(edge_identifier_2_host_1, edge_2_host_1),
            call(edge_identifier_1_host_2, edge_1_host_2),
            call(edge_identifier_1_host_3, edge_1_host_3),
            call(edge_identifier_1_host_4, edge_1_host_4),
        ], any_order=True)

    @pytest.mark.asyncio
    async def process_all_edges_with_error_test(self, instance_server, links_host_1_response, links_host_2_response,
                                                links_host_3_response, links_host_4_response):
        all_links = links_host_1_response['body'] + links_host_2_response['body'] + \
                    links_host_3_response['body'] + links_host_4_response['body']
        response = {
            'request_id': uuid_,
            'status': 400,
            'body': []
        }

        instance_server._velocloud_repository.get_all_links_with_edge_info = CoroutineMock(side_effect=[response])
        instance_server._prometheus_repository.set_cycle_total_edges = Mock()
        with uuid_mock:
            await instance_server._process_all_edges()

        instance_server._velocloud_repository.get_all_links_with_edge_info.assert_awaited_once()
        instance_server._prometheus_repository.set_cycle_total_edges.assert_not_called()

    @pytest.mark.asyncio
    async def process_all_edges_with_exception_test(self, instance_server, links_host_1_response,
                                                    links_host_2_response, links_host_3_response,
                                                    links_host_4_response, edge_1_host_1, edge_2_host_1,
                                                    edge_identifier_1_host_1, edge_identifier_2_host_1,
                                                    edge_identifier_1_host_2, edge_1_host_2, edge_identifier_1_host_3,
                                                    edge_1_host_3, edge_identifier_1_host_4, edge_1_host_4):
        all_links = links_host_1_response['body'] + links_host_2_response['body'] + \
                    links_host_3_response['body'] + links_host_4_response['body']
        response = {
            'request_id': uuid_,
            'status': 200,
            'body': all_links
        }

        instance_server._velocloud_repository.get_all_links_with_edge_info = CoroutineMock(side_effect=[
            Exception('Failed!')])
        instance_server._prometheus_repository.set_cycle_total_edges = Mock()
        instance_server._process_edge = CoroutineMock()
        instance_server._logger.error = Mock()
        with uuid_mock:
            await instance_server._process_all_edges()

        instance_server._velocloud_repository.get_all_links_with_edge_info.assert_awaited_once()
        instance_server._prometheus_repository.set_cycle_total_edges.assert_not_called()
        instance_server._process_edge.assert_not_called()
        instance_server._logger.error.assert_called_once_with("Error: Exception in process all edges: Failed!")

    @pytest.mark.asyncio
    async def process_all_edges_with_cache_test(self, instance_server, links_host_1_response, links_host_2_response,
                                                links_host_3_response, links_host_4_response, edge_1_host_1,
                                                edge_2_host_1, edge_identifier_1_host_1, edge_identifier_2_host_1,
                                                edge_identifier_1_host_2, edge_1_host_2, edge_identifier_1_host_3,
                                                edge_1_host_3, edge_identifier_1_host_4, edge_1_host_4):
        # removed links_host_4_response for testing
        all_links = links_host_1_response['body'] + links_host_2_response['body'] + \
                    links_host_3_response['body']
        response = {
            'request_id': uuid_,
            'status': 200,
            'body': all_links
        }
        cache_some_edge_identifiers: Dict[EdgeIdentifier, dict] = {
            edge_identifier_1_host_1: edge_1_host_1,
            edge_identifier_2_host_1: edge_2_host_1,
            edge_identifier_1_host_2: edge_1_host_2,
            edge_identifier_1_host_3: edge_1_host_3,
            edge_identifier_1_host_4: edge_1_host_4
        }
        instance_server._edges_cache = set(cache_some_edge_identifiers)
        instance_server._status_cache = {
            edge_identifier_1_host_1: {
                'cache_edge': edge_1_host_1
            },
            edge_identifier_2_host_1: {
                'cache_edge': edge_2_host_1
            },
            edge_identifier_1_host_2: {
                'cache_edge': edge_1_host_2
            },
            edge_identifier_1_host_3: {
                'cache_edge': edge_1_host_3
            },
            edge_identifier_1_host_4: {
                'cache_edge': edge_1_host_4
            }
        }
        instance_server._velocloud_repository.get_all_links_with_edge_info = CoroutineMock(side_effect=[response])
        instance_server._prometheus_repository.set_cycle_total_edges = Mock()
        instance_server._prometheus_repository.dec = Mock()
        instance_server._process_edge = CoroutineMock()
        with uuid_mock:
            await instance_server._process_all_edges()

        instance_server._velocloud_repository.get_all_links_with_edge_info.assert_awaited_once()
        instance_server._prometheus_repository.set_cycle_total_edges.assert_called_once_with(4)
        instance_server._prometheus_repository.dec.assert_called_once_with(edge_1_host_4)
        instance_server._process_edge.assert_has_awaits([
            call(edge_identifier_1_host_3, edge_1_host_3)
        ], any_order=True)

    @pytest.mark.asyncio
    async def process_edge_without_cache_test(self, instance_server, edge_identifier_1_host_1, edge_1_host_1):
        expected_cache = {
            edge_identifier_1_host_1: {'cache_edge': edge_1_host_1}
        }
        instance_server._prometheus_repository.inc = Mock()
        await instance_server._process_edge(edge_identifier_1_host_1, edge_1_host_1)
        instance_server._prometheus_repository.inc.assert_called_once_with(edge_1_host_1)
        assert instance_server._status_cache == expected_cache

    @pytest.mark.asyncio
    async def process_edge_with_exception_test(self, instance_server, edge_identifier_1_host_1, edge_1_host_1):
        expected_cache = {}
        instance_server._prometheus_repository.inc = Mock(side_effect=Exception("Failed!"))
        instance_server._logger.error = Mock()
        await instance_server._process_edge(edge_identifier_1_host_1, edge_1_host_1)
        instance_server._prometheus_repository.inc.assert_called_once_with(edge_1_host_1)
        assert instance_server._status_cache == expected_cache
        instance_server._logger.error.assert_called_once_with('Error: Exception in process one edge link: Failed!')

    @pytest.mark.asyncio
    async def process_edge_with_cache_test(self, instance_server, edge_identifier_1_host_1, edge_1_host_1):
        instance_server._status_cache = {
            edge_identifier_1_host_1: {'cache_edge': edge_1_host_1}
        }
        instance_server._prometheus_repository.inc = Mock()
        await instance_server._process_edge(edge_identifier_1_host_1, edge_1_host_1)
        instance_server._prometheus_repository.inc.assert_not_called()

    @pytest.mark.asyncio
    async def process_edge_without_cache_edge_no_links_test(self, instance_server, edge_identifier_1_host_1,
                                                            edge_4_host_1):
        instance_server._status_cache = {
            edge_identifier_1_host_1: {'cache_edge': edge_4_host_1}
        }
        instance_server._prometheus_repository.inc = Mock()
        await instance_server._process_edge(edge_identifier_1_host_1, edge_4_host_1)
        instance_server._prometheus_repository.inc.assert_not_called()

    @pytest.mark.asyncio
    async def process_edge_with_cache_and_edge_offline_status_test(self, instance_server, edge_identifier_1_host_1,
                                                                   edge_1_host_1, edge_1_host_1_offline):
        instance_server._status_cache = {
            edge_identifier_1_host_1: {'cache_edge': edge_1_host_1_offline}
        }
        instance_server._prometheus_repository.inc = Mock()
        instance_server._prometheus_repository.update_edge = Mock()

        await instance_server._process_edge(edge_identifier_1_host_1, edge_1_host_1)

        instance_server._prometheus_repository.inc.assert_not_called()
        instance_server._prometheus_repository.update_edge.assert_called_once_with(edge_1_host_1,
                                                                                   edge_1_host_1_offline)

    @pytest.mark.asyncio
    async def process_edge_with_cache_and_link_offline_status_test(self, instance_server, edge_identifier_1_host_1,
                                                                   edge_1_host_1, edge_1_host_1_offline_link):
        instance_server._status_cache = {
            edge_identifier_1_host_1: {'cache_edge': edge_1_host_1_offline_link}
        }
        instance_server._prometheus_repository.inc = Mock()
        instance_server._prometheus_repository.update_link = Mock()
        link_offline = edge_1_host_1_offline_link['links'][0]
        cache_link = edge_1_host_1['links'][0]

        await instance_server._process_edge(edge_identifier_1_host_1, edge_1_host_1)

        instance_server._prometheus_repository.inc.assert_not_called()
        instance_server._prometheus_repository.update_link.assert_called_once_with(
            edge_1_host_1, cache_link, edge_1_host_1_offline_link, link_offline
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
