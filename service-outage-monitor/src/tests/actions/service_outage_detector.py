import json
import pytest

from datetime import datetime
from unittest.mock import call
from unittest.mock import Mock
from unittest.mock import patch

from apscheduler.util import undefined
from asynctest import CoroutineMock
from shortuuid import uuid

from application.actions import service_outage_detector as service_outage_detector_module
from application.actions.service_outage_detector import ServiceOutageDetector
from config import testconfig


class TestServiceOutageDetector:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        config = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        online_edge_repository, quarantine_edge_repository,
                                                        config)

        assert service_outage_detector._event_bus is event_bus
        assert service_outage_detector._logger is logger
        assert service_outage_detector._scheduler is scheduler
        assert service_outage_detector._config is config

    @pytest.mark.asyncio
    async def start_service_outage_detector_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        online_edge_repository, quarantine_edge_repository,
                                                        config)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(service_outage_detector_module, 'datetime', new=datetime_mock):
            with patch.object(service_outage_detector_module, 'timezone', new=Mock()):
                await service_outage_detector.start_service_outage_detector_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            service_outage_detector._service_outage_detector_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_detector'],
            next_run_time=next_run_time,
            replace_existing=True,
            id='_service_outage_detector_process',
        )

    @pytest.mark.asyncio
    async def start_service_outage_monitor_job_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        online_edge_repository, quarantine_edge_repository,
                                                        config)

        await service_outage_detector.start_service_outage_detector_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            service_outage_detector._service_outage_detector_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_detector'],
            next_run_time=undefined,
            replace_existing=True,
            id='_service_outage_detector_process',
        )

    @pytest.mark.asyncio
    async def service_outage_detector_process_with_no_edges_found_test(self):
        edge_list = []

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        online_edge_repository, quarantine_edge_repository,
                                                        config)
        service_outage_detector._get_all_edges = CoroutineMock(return_value=edge_list)

        await service_outage_detector._service_outage_detector_process()

        service_outage_detector._get_all_edges.assert_awaited_once()

    @pytest.mark.asyncio
    async def service_outage_detector_process_with_edges_found_and_online_edges_test(self):
        edge_1_id = 5678
        edge_2_id = 8765
        edge_3_id = 3344
        edge_1_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': edge_1_id}
        edge_2_full_id = {'host': 'metvco03.mettel.net', 'enterprise_id': 4321, 'edge_id': edge_2_id}
        edge_3_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1122, 'edge_id': edge_3_id}
        edge_list = [edge_1_full_id, edge_2_full_id, edge_3_full_id]

        edge_1_status = {'edges': {'edgeState': 'CONNECTED'}}
        edge_2_status = {'edges': {'edgeState': 'OFFLINE'}}
        edge_3_status = {'edges': {'edgeState': 'CONNECTED'}}
        edge_statuses = [edge_1_status, edge_2_status, edge_3_status]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        online_edge_repository, quarantine_edge_repository,
                                                        config)
        service_outage_detector._get_all_edges = CoroutineMock(return_value=edge_list)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(side_effect=edge_statuses)

        await service_outage_detector._service_outage_detector_process()

        service_outage_detector._get_all_edges.assert_awaited_once()
        service_outage_detector._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id), call(edge_2_full_id), call(edge_3_full_id)
        ])
        service_outage_detector._online_edge_repository.add_edge.assert_has_calls([
            call(full_id=edge_1_full_id, status=edge_1_status),
            call(full_id=edge_3_full_id, status=edge_3_status),
        ])

    @pytest.mark.asyncio
    async def service_outage_detector_process_with_edges_found_and_offline_edges_test(self):
        edge_1_id = 5678
        edge_2_id = 8765
        edge_3_id = 3344
        edge_1_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': edge_1_id}
        edge_2_full_id = {'host': 'metvco03.mettel.net', 'enterprise_id': 4321, 'edge_id': edge_2_id}
        edge_3_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1122, 'edge_id': edge_3_id}
        edge_list = [edge_1_full_id, edge_2_full_id, edge_3_full_id]

        edge_1_status = {'edges': {'edgeState': 'OFFLINE'}}
        edge_2_status = {'edges': {'edgeState': 'CONNECTED'}}
        edge_3_status = {'edges': {'edgeState': 'OFFLINE'}}
        edge_statuses = [edge_1_status, edge_2_status, edge_3_status]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        online_edge_repository, quarantine_edge_repository,
                                                        config)
        service_outage_detector._get_all_edges = CoroutineMock(return_value=edge_list)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(side_effect=edge_statuses)

        await service_outage_detector._service_outage_detector_process()

        service_outage_detector._get_all_edges.assert_awaited_once()
        service_outage_detector._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id), call(edge_2_full_id), call(edge_3_full_id)
        ])
        service_outage_detector._quarantine_edge_repository.add_edge.assert_has_calls([
            call(full_id=edge_1_full_id, status=edge_1_status),
            call(full_id=edge_3_full_id, status=edge_3_status),
        ])

    @pytest.mark.asyncio
    async def get_all_edges_test(self):
        uuid_ = uuid()
        edge_list = [
            {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': 5678},
            {'host': 'metvco03.mettel.net', 'enterprise_id': 4321, 'edge_id': 8765},
            {'host': 'metvco04.mettel.net', 'enterprise_id': 1122, 'edge_id': 3344},
        ]
        edge_list_response = {
            'request_id': uuid_,
            'edges': edge_list,
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=edge_list_response)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        online_edge_repository, quarantine_edge_repository,
                                                        config)

        with patch.object(service_outage_detector_module, 'uuid', return_value=uuid_):
            result = await service_outage_detector._get_all_edges()

        event_bus.rpc_request.assert_awaited_once_with(
            'edge.list.request',
            json.dumps({
                'request_id': uuid_,
                'filter': [
                    {'host': 'mettel.velocloud.net', 'enterprise_ids': []},
                    {'host': 'metvco03.mettel.net', 'enterprise_ids': []},
                    {'host': 'metvco04.mettel.net', 'enterprise_ids': []},
                ]
            }),
            timeout=60,
        )
        assert result == edge_list

    @pytest.mark.asyncio
    async def get_edge_status_by_id_test(self):
        uuid_ = uuid()
        edge_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_status = {
            'edges': {
                'edgeState': 'CONNECTED'
            }
        }
        edge_status_response = {
            'request_id': uuid_,
            'edge_id': edge_full_id,
            'edge_info': edge_status,
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=edge_status_response)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        online_edge_repository, quarantine_edge_repository,
                                                        config)

        with patch.object(service_outage_detector_module, 'uuid', return_value=uuid_):
            result = await service_outage_detector._get_edge_status_by_id(edge_full_id)

        event_bus.rpc_request.assert_awaited_once_with(
            'edge.status.request',
            json.dumps({
                'request_id': uuid_,
                'edge': edge_full_id,
            }),
            timeout=45,
        )
        assert result == edge_status

    def is_offline_edge_test(self):
        edge_status_1 = {
            'edges': {
                'edgeState': 'CONNECTED'
            }
        }
        edge_status_2 = {
            'edges': {
                'edgeState': 'OFFLINE'
            }
        }

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        online_edge_repository, quarantine_edge_repository,
                                                        config)

        result = service_outage_detector._is_offline(edge_status_1)
        assert result is False

        result = service_outage_detector._is_offline(edge_status_2)
        assert result is True
