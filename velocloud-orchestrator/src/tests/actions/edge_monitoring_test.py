import json
from datetime import datetime
from unittest.mock import Mock

import asyncio
import pytest
from application.actions.edge_monitoring import EdgeMonitoring
from asynctest import CoroutineMock

from config import testconfig


class TestEdgeMonitoring:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        statistic_repository = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        status_repository = Mock()
        config = Mock()
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)
        assert isinstance(edge_monitoring, EdgeMonitoring)
        assert edge_monitoring._event_bus is event_bus
        assert edge_monitoring._logger is logger
        assert edge_monitoring._prometheus_repository is prometheus_repository
        assert edge_monitoring._scheduler is scheduler
        assert edge_monitoring._edge_repository is edge_repository
        assert edge_monitoring._status_repository is status_repository
        assert edge_monitoring._statistic_repository is statistic_repository
        assert edge_monitoring._service_id == service_id
        assert edge_monitoring._config is config

    def start_metrics_server_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        prometheus_repository.start_prometheus_metrics_server = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        status_repository = Mock()
        statistic_repository = Mock()
        config = Mock()
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)
        edge_monitoring.start_prometheus_metrics_server()
        assert prometheus_repository.start_prometheus_metrics_server.called

    @pytest.mark.asyncio
    async def request_edges_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        prometheus_repository = Mock()
        prometheus_repository.start_prometheus_metrics_server = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        status_repository = Mock()
        status_repository.set_last_cycle_request_id = Mock()
        statistic_repository = Mock()
        config = Mock()
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)
        await edge_monitoring._request_edges(1234)
        assert status_repository.set_last_cycle_request_id.called
        assert status_repository.set_last_cycle_request_id.call_args[0][0] == 1234
        assert event_bus.publish_message.called
        assert "edge.list.request" in event_bus.publish_message.call_args[0][0]

    @pytest.mark.asyncio
    async def receive_edge_list_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        status_repository = Mock()
        status_repository.set_edges_to_process = Mock()
        statistic_repository = Mock()
        config = Mock()
        service_id = 123

        edge_list = b'{"request_id":1234, "edges":["1", "2", "3"]}'

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)

        await edge_monitoring.receive_edge_list(edge_list)
        assert status_repository.set_edges_to_process.called
        assert event_bus.publish_message.called

    @pytest.mark.asyncio
    async def receive_edge_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        prometheus_repository.inc = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        edge_repository.set_edge = Mock()
        status_repository = Mock()
        status_repository.set_edges_processed = Mock()
        status_repository.get_edges_to_process = Mock(return_value=3)
        status_repository.get_edges_processed = Mock(return_value=2)
        status_repository.set_status = Mock()
        statistic_repository = Mock()
        config = Mock()
        service_id = 123

        edge = {"request_id": 1234, 'edge_id': {'host': 'some_host'}, 'edge_info': 'Some edge data'}

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)
        edge_monitoring._edge_monitoring_process = CoroutineMock()

        await edge_monitoring.receive_edge(json.dumps(edge))
        assert prometheus_repository.inc.called
        assert status_repository.get_edges_processed.called
        assert status_repository.set_edges_processed.called
        assert status_repository.set_edges_processed.call_args[0][0] == 3
        assert status_repository.get_edges_to_process.called
        assert status_repository.set_status.called
        assert "IDLE" in status_repository.set_status.call_args[0][0]
        assert edge_repository.set_edge.call_args[0][0] == edge['edge_id']
        assert edge_monitoring._edge_monitoring_process.called

    @pytest.mark.asyncio
    async def start_edge_monitor_job_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        edge_repository = Mock()
        status_repository = Mock()
        statistic_repository = Mock()
        config = testconfig
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)
        edge_monitoring._edge_monitoring_process = CoroutineMock()
        await edge_monitoring.start_edge_monitor_job(exec_on_start=True)
        assert scheduler.add_job.called
        assert scheduler.add_job.call_args[0][0] is edge_monitoring._edge_monitoring_process
        assert "interval" in scheduler.add_job.call_args[0][1]
        assert scheduler.add_job.call_args[1]['seconds'] == testconfig.ORCHESTRATOR_CONFIG['monitoring_seconds']

    @pytest.mark.asyncio
    async def _edge_monitoring_process_processing_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        status_repository = Mock()
        status_repository.get_edges_processed = Mock()
        status_repository.get_edges_to_process = Mock()
        status_repository.get_status = Mock(return_value="PROCESSING_VELOCLOUD_EDGES")
        status_repository.set_status = Mock()
        status_repository.get_last_cycle_timestamp = Mock(return_value=datetime.timestamp(datetime.now()))
        statistic_repository = Mock()
        service_id = 123
        await asyncio.sleep(0.1)
        config = testconfig

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)
        await edge_monitoring._edge_monitoring_process()
        assert status_repository.get_edges_processed.called
        assert status_repository.get_edges_to_process.called
        assert status_repository.get_status.called
        assert status_repository.get_last_cycle_timestamp.called
        assert status_repository.set_status.called

    @pytest.mark.asyncio
    async def _edge_monitoring_process_idle_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        prometheus_repository.reset_counter = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        status_repository = Mock()
        status_repository.set_edges_processed = Mock()
        status_repository.set_last_cycle_timestamp = Mock()
        status_repository.get_status = Mock(return_value="IDLE")
        status_repository.set_status = Mock()
        status_repository.get_last_cycle_timestamp = Mock(return_value=datetime.timestamp(datetime.now()))
        statistic_repository = Mock()
        statistic_repository._statistic_client.clear_dictionaries = Mock()
        service_id = 123
        await asyncio.sleep(0.1)
        config = testconfig

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)
        edge_monitoring._request_edges = CoroutineMock()
        await edge_monitoring._edge_monitoring_process()
        assert edge_monitoring._send_stats_to_notifier.called
        assert prometheus_repository.reset_counter.called
        assert statistic_repository._statistic_client.clear_dictionaries.called
        assert status_repository.set_edges_processed.called
        assert status_repository.set_last_cycle_timestamp.called
        assert status_repository.get_status.called
        assert status_repository.set_status.called
        assert edge_monitoring._request_edges.called
