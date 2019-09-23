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
        status_repository.set_current_cycle_request_id = Mock()
        statistic_repository = Mock()
        config = Mock()
        service_id = 123

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)
        await edge_monitoring._request_edges(1234)
        assert status_repository.set_current_cycle_request_id.called
        assert status_repository.set_current_cycle_request_id.call_args[0][0] == 1234
        assert event_bus.publish_message.called
        assert "edge.list.request" in event_bus.publish_message.call_args[0][0]

    @pytest.mark.asyncio
    async def receive_edge_list_no_redis_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        prometheus_repository = Mock()
        prometheus_repository.dec = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        edge_repository.get_last_edge_list = Mock(return_value=None)
        edge_repository.get_edge = Mock()
        status_repository = Mock()
        status_repository.set_edges_to_process = Mock()
        statistic_repository = Mock()
        config = Mock()
        service_id = 123

        edge_list = b'{"request_id":1234, "edges":["1", "2", "3"]}'

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)

        await edge_monitoring.receive_edge_list(edge_list)
        assert edge_repository.get_last_edge_list.called
        assert edge_repository.get_edge.called is False
        assert prometheus_repository.dec.called is False
        assert status_repository.set_edges_to_process.called
        assert event_bus.publish_message.called

    @pytest.mark.asyncio
    async def receive_edge_list_redis_data_test(self):

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        prometheus_repository = Mock()
        prometheus_repository.dec = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        redis_test_enterprise_name = 'Test'
        redis_edge_state = 'Edge_KO'
        redis_link_status = [{"link": {"state": "KO"}}]
        redis_edge = {"redis_edge": {"edges": {"edgeState": redis_edge_state},
                                     "enterprise_name": redis_test_enterprise_name,
                                     "links": redis_link_status}}
        edge_repository.get_edge = Mock(return_value=json.dumps(redis_edge))
        redis_list = b'[{"host": "some.host", "enterprise_id": 19, "edge_id": 99},' \
                     b'{"host": "some.host", "enterprise_id": 20, "edge_id": 100},' \
                     b'{"host": "some.host", "enterprise_id": 21, "edge_id": 101}]'
        edge_repository.get_last_edge_list = Mock(return_value=redis_list)
        status_repository = Mock()
        status_repository.set_edges_to_process = Mock()
        statistic_repository = Mock()
        config = Mock()
        service_id = 123

        edge_list = b'{"request_id":1234, "edges":[{"host": "some.host", "enterprise_id":19, "edge_id":99},' \
                    b'{"host": "some.host", "enterprise_id":20, "edge_id":100}]}'

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)

        await edge_monitoring.receive_edge_list(edge_list)

        assert prometheus_repository.dec.called
        assert edge_repository.get_last_edge_list.called
        assert edge_repository.get_edge.called
        assert status_repository.set_edges_to_process.called
        assert event_bus.publish_message.called

    @pytest.mark.asyncio
    async def receive_edge_list_redis_data_same_len_test(self):

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        prometheus_repository = Mock()
        prometheus_repository.dec = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        redis_test_enterprise_name = 'Test'
        redis_edge_state = 'Edge_KO'
        redis_link_status = [{"link": {"state": "KO"}}]
        redis_edge = {"redis_edge": {"edges": {"edgeState": redis_edge_state},
                                     "enterprise_name": redis_test_enterprise_name,
                                     "links": redis_link_status}}
        edge_repository.get_edge = Mock(return_value=json.dumps(redis_edge))
        redis_list = b'[{"host": "some.host", "enterprise_id": 19, "edge_id": 99},' \
                     b'{"host": "some.host", "enterprise_id": 20, "edge_id": 100}]'
        edge_repository.get_last_edge_list = Mock(return_value=redis_list)
        status_repository = Mock()
        status_repository.set_edges_to_process = Mock()
        statistic_repository = Mock()
        config = Mock()
        service_id = 123

        edge_list = b'{"request_id":1234, "edges":[{"host": "some.host", "enterprise_id":19, "edge_id":99},' \
                    b'{"host": "some.host", "enterprise_id":20, "edge_id":100}]}'

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)

        await edge_monitoring.receive_edge_list(edge_list)

        assert prometheus_repository.dec.called is False
        assert edge_repository.get_last_edge_list.called
        assert edge_repository.get_edge.called is False
        assert status_repository.set_edges_to_process.called
        assert event_bus.publish_message.called

    @pytest.mark.asyncio
    async def receive_edge_no_redis_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        prometheus_repository.inc = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        edge_repository.get_edge = Mock(return_value=None)
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
    async def receive_edge_redis_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        prometheus_repository.update_edge = Mock()
        prometheus_repository.update_link = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        redis_test_enterprise_name = 'Test'
        redis_edge_state = 'Edge_KO'
        redis_link_status = [{"link": {"state": "KO"}}]
        redis_edge = {"redis_edge": {"edges": {"edgeState": redis_edge_state},
                                     "enterprise_name": redis_test_enterprise_name,
                                     "links": redis_link_status}}
        edge_repository.get_edge = Mock(return_value=json.dumps(redis_edge))
        edge_repository.set_edge = Mock()
        status_repository = Mock()
        status_repository.set_edges_processed = Mock()
        status_repository.get_edges_to_process = Mock(return_value=3)
        status_repository.get_edges_processed = Mock(return_value=2)
        status_repository.set_status = Mock()
        statistic_repository = Mock()
        config = Mock()
        service_id = 123

        test_enterprise_name = 'Test'
        test_edge_state = 'Edge_OK'
        test_link_status = [{"link": {"state": "OK"}}]
        test_edge = {"edges": {"edgeState": test_edge_state}, "enterprise_name": test_enterprise_name,
                     "links": test_link_status}
        edge = {"request_id": 1234, 'edge_id': {'host': 'some_host'}, 'edge_info': test_edge}

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)
        edge_monitoring._edge_monitoring_process = CoroutineMock()

        await edge_monitoring.receive_edge(json.dumps(edge))
        assert prometheus_repository.update_edge.called
        assert prometheus_repository.update_link.called
        assert status_repository.get_edges_processed.called
        assert status_repository.set_edges_processed.called
        assert status_repository.set_edges_processed.call_args[0][0] == 3
        assert status_repository.get_edges_to_process.called
        assert status_repository.set_status.called
        assert "IDLE" in status_repository.set_status.call_args[0][0]
        assert edge_repository.set_edge.call_args[0][0] == edge['edge_id']
        assert edge_monitoring._edge_monitoring_process.called

    @pytest.mark.asyncio
    async def receive_edge_redis_same_edge_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        prometheus_repository.update_edge = Mock()
        prometheus_repository.update_link = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        redis_test_enterprise_name = 'Test'
        redis_edge_state = 'Edge_OK'
        redis_link_status = [{"link": {"state": "KO"}}]
        redis_edge = {"redis_edge": {"edges": {"edgeState": redis_edge_state},
                                     "enterprise_name": redis_test_enterprise_name,
                                     "links": redis_link_status}}
        edge_repository.get_edge = Mock(return_value=json.dumps(redis_edge))
        edge_repository.set_edge = Mock()
        status_repository = Mock()
        status_repository.set_edges_processed = Mock()
        status_repository.get_edges_to_process = Mock(return_value=3)
        status_repository.get_edges_processed = Mock(return_value=2)
        status_repository.set_status = Mock()
        statistic_repository = Mock()
        config = Mock()
        service_id = 123

        test_enterprise_name = 'Test'
        test_edge_state = 'Edge_OK'
        test_link_status = [{"link": {"state": "OK"}}]
        test_edge = {"edges": {"edgeState": test_edge_state}, "enterprise_name": test_enterprise_name,
                     "links": test_link_status}
        edge = {"request_id": 1234, 'edge_id': {'host': 'some_host'}, 'edge_info': test_edge}

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)
        edge_monitoring._edge_monitoring_process = CoroutineMock()

        await edge_monitoring.receive_edge(json.dumps(edge))
        assert prometheus_repository.update_edge.called is False
        assert prometheus_repository.update_link.called
        assert status_repository.get_edges_processed.called
        assert status_repository.set_edges_processed.called
        assert status_repository.set_edges_processed.call_args[0][0] == 3
        assert status_repository.get_edges_to_process.called
        assert status_repository.set_status.called
        assert "IDLE" in status_repository.set_status.call_args[0][0]
        assert edge_repository.set_edge.call_args[0][0] == edge['edge_id']
        assert edge_monitoring._edge_monitoring_process.called

    @pytest.mark.asyncio
    async def receive_edge_redis_same_link_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        prometheus_repository.update_edge = Mock()
        prometheus_repository.update_link = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        redis_test_enterprise_name = 'Test'
        redis_edge_state = 'Edge_OK'
        redis_link_status = [{"link": {"state": "OK"}}]
        redis_edge = {"redis_edge": {"edges": {"edgeState": redis_edge_state},
                                     "enterprise_name": redis_test_enterprise_name,
                                     "links": redis_link_status}}
        edge_repository.get_edge = Mock(return_value=json.dumps(redis_edge))
        edge_repository.set_edge = Mock()
        status_repository = Mock()
        status_repository.set_edges_processed = Mock()
        status_repository.get_edges_to_process = Mock(return_value=3)
        status_repository.get_edges_processed = Mock(return_value=2)
        status_repository.set_status = Mock()
        statistic_repository = Mock()
        config = Mock()
        service_id = 123

        test_enterprise_name = 'Test'
        test_edge_state = 'Edge_KO'
        test_link_status = [{"link": {"state": "OK"}}]
        test_edge = {"edges": {"edgeState": test_edge_state}, "enterprise_name": test_enterprise_name,
                     "links": test_link_status}
        edge = {"request_id": 1234, 'edge_id': {'host': 'some_host'}, 'edge_info': test_edge}

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)
        edge_monitoring._edge_monitoring_process = CoroutineMock()

        await edge_monitoring.receive_edge(json.dumps(edge))
        assert prometheus_repository.update_edge.called
        assert prometheus_repository.update_link.called is False
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
        status_repository.get_current_cycle_timestamp = Mock(return_value=datetime.timestamp(datetime.now()))
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
        assert status_repository.get_current_cycle_timestamp.called
        assert status_repository.set_status.called

    @pytest.mark.asyncio
    async def _edge_monitoring_process_idle_test(self):
        event_bus = Mock()
        logger = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()
        edge_repository = Mock()
        status_repository = Mock()
        status_repository.set_edges_processed = Mock()
        status_repository.set_current_cycle_timestamp = Mock()
        status_repository.get_status = Mock(return_value="IDLE")
        status_repository.set_status = Mock()
        status_repository.get_current_cycle_timestamp = Mock(return_value=datetime.timestamp(datetime.now()))
        statistic_repository = Mock()
        statistic_repository._statistic_client.clear_dictionaries = Mock()
        service_id = 123
        await asyncio.sleep(0.1)
        config = testconfig

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)
        edge_monitoring._request_edges = CoroutineMock()
        await edge_monitoring._edge_monitoring_process()
        assert statistic_repository._statistic_client.clear_dictionaries.called
        assert status_repository.set_edges_processed.called
        assert status_repository.set_current_cycle_timestamp.called
        assert status_repository.get_status.called
        assert status_repository.set_status.called
        assert edge_monitoring._request_edges.called

    @pytest.mark.asyncio
    async def _send_stats_to_notifier_ko_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()
        statistic_repository = Mock()
        statistic_repository._statistic_client.get_statistics = Mock(return_value="Failed Edges Status")
        statistic_repository.store_stats = Mock()
        edge_repository = Mock()
        edge_repository.get_keys = Mock(return_value=['host', 'fail', 'host 2'])
        edge_repository.get_edge = Mock(return_value=json.dumps({'request_id': 123, 'redis_edge': {'edges':
                                                                                                   {'edgeState':
                                                                                                    'DISCONNECTED'}}}))
        status_repository = Mock()
        status_repository.get_current_cycle_request_id = Mock(return_value=123)
        service_id = 123
        config = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)
        await edge_monitoring._send_stats_to_notifier()
        assert status_repository.get_current_cycle_request_id.called
        assert edge_repository.get_keys.called
        assert logger.info.called is False
        assert logger.error.called
        assert statistic_repository.store_stats.called
        assert statistic_repository._statistic_client.get_statistics.called
        assert event_bus.publish_message.call_args[0][0] == "notification.slack.request"
        assert event_bus.publish_message.call_args[0][1] == json.dumps(dict(request_id=123,
                                                                            response_topic=f'notification.'
                                                                            f'slack.request.{service_id}',
                                                                            message="Failed Edges Status"))

    @pytest.mark.asyncio
    async def _send_stats_to_notifier_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()
        prometheus_repository = Mock()
        scheduler = Mock()
        statistic_repository = Mock()
        statistic_repository._statistic_client.get_statistics = Mock(return_value=None)
        edge_repository = Mock()
        edge_repository.get_keys = Mock(return_value=['host', 'fail', 'host 2'])
        edge_repository.get_edge = Mock(return_value=json.dumps({'request_id': 123, 'redis_edge': {'edges':
                                                                                                   {'edgeState':
                                                                                                    'CONNECTED'}}}))
        status_repository = Mock()
        status_repository.get_current_cycle_request_id = Mock(return_value=123)
        service_id = 123
        config = Mock()

        edge_monitoring = EdgeMonitoring(event_bus, logger, prometheus_repository, scheduler, edge_repository,
                                         status_repository, statistic_repository, service_id, config)

        await edge_monitoring._send_stats_to_notifier()
        assert status_repository.get_current_cycle_request_id.called
        assert edge_repository.get_keys.called
        assert logger.info.called
        assert logger.error.called
        assert statistic_repository.store.called is False
        assert statistic_repository._statistic_client.get_statistics.called
        assert event_bus.publish_message.called is False
        statistic_repository._statistic_client.get_statistics = Mock(return_value="Failed Edge Report")
        status_repository.get_current_cycle_request_id = Mock(return_value=124)
        await edge_monitoring._send_stats_to_notifier()
        assert status_repository.get_current_cycle_request_id.called
        assert edge_repository.get_keys.called
        assert statistic_repository.send_to_stats_client.called is False
        assert statistic_repository._statistic_client.get_statistics.called
        assert event_bus.publish_message.called
