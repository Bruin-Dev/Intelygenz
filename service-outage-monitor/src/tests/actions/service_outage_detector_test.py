import json
import pytest

from datetime import datetime
from datetime import timedelta
from unittest.mock import call
from unittest.mock import Mock
from unittest.mock import patch

from apscheduler.util import undefined
from asynctest import CoroutineMock
from shortuuid import uuid

from application.actions import service_outage_detector as service_outage_detector_module
from application.actions.service_outage_detector import ServiceOutageDetector
from application.actions.service_outage_detector import DetectedOutagesObserver
from application.repositories.edge_repository import EdgeIdentifier
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
        assert service_outage_detector._online_edge_repository is online_edge_repository
        assert service_outage_detector._quarantine_edge_repository is quarantine_edge_repository
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

        edge_1_status = {'edges': {'edgeState': 'CONNECTED'}, 'enterprise_name': 'EVIL-CORP|12345|'}
        edge_2_status = {'edges': {'edgeState': 'OFFLINE'}, 'enterprise_name': 'EVIL-CORP|12345|'}
        edge_3_status = {'edges': {'edgeState': 'CONNECTED'}, 'enterprise_name': 'EVIL-CORP|12345|'}
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
            call(full_id=edge_1_full_id, status=edge_1_status, time_to_live=600),
            call(full_id=edge_3_full_id, status=edge_3_status, time_to_live=600),
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

        edge_1_status = {'edges': {'edgeState': 'OFFLINE'}, 'enterprise_name': 'EVIL-CORP|12345|'}
        edge_2_status = {'edges': {'edgeState': 'CONNECTED'}, 'enterprise_name': 'EVIL-CORP|12345|'}
        edge_3_status = {'edges': {'edgeState': 'OFFLINE'}, 'enterprise_name': 'EVIL-CORP|12345|'}
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
            call(full_id=edge_1_full_id, status=edge_1_status, time_to_live=600),
            call(full_id=edge_3_full_id, status=edge_3_status, time_to_live=600),
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
            },
            'enterprise_name': 'EVIL-CORP|12345|',
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
            },
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_status_2 = {
            'edges': {
                'edgeState': 'OFFLINE'
            },
            'enterprise_name': 'EVIL-CORP|12345|',
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


class TestDetectedOutagesObserver:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = Mock()

        detected_outages_observer = DetectedOutagesObserver(event_bus, logger, scheduler,
                                                            online_edge_repository, quarantine_edge_repository,
                                                            reporting_edge_repository, config)

        assert detected_outages_observer._event_bus is event_bus
        assert detected_outages_observer._logger is logger
        assert detected_outages_observer._scheduler is scheduler
        assert detected_outages_observer._online_edge_repository is online_edge_repository
        assert detected_outages_observer._quarantine_edge_repository is quarantine_edge_repository
        assert detected_outages_observer._reporting_edge_repository is reporting_edge_repository
        assert detected_outages_observer._config is config

    @pytest.mark.asyncio
    async def start_detected_outages_observer_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        detected_outages_observer = DetectedOutagesObserver(event_bus, logger, scheduler,
                                                            online_edge_repository, quarantine_edge_repository,
                                                            reporting_edge_repository, config)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(service_outage_detector_module, 'datetime', new=datetime_mock):
            with patch.object(service_outage_detector_module, 'timezone', new=Mock()):
                await detected_outages_observer.start_detected_outages_observer_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            detected_outages_observer._observe_detected_outages, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_observer'],
            next_run_time=next_run_time,
            replace_existing=True,
            id='_detected_outages_observer_process',
        )

    @pytest.mark.asyncio
    async def start_detected_outages_observer_job_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        detected_outages_observer = DetectedOutagesObserver(event_bus, logger, scheduler,
                                                            online_edge_repository, quarantine_edge_repository,
                                                            reporting_edge_repository, config)

        await detected_outages_observer.start_detected_outages_observer_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            detected_outages_observer._observe_detected_outages, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_observer'],
            next_run_time=undefined,
            replace_existing=True,
            id='_detected_outages_observer_process',
        )

    @pytest.mark.asyncio
    async def observe_detected_outages_test(self):
        quarantine_edges = {}
        online_edges = {
            EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=123, edge_id=456): {
                'edge_status': {'edges': {'edgeState': 'CONNECTED'}, 'enterprise_name': 'EVIL-CORP|12345|'},
                'addition_timestamp': 123456789,
            },
            EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=789, edge_id=321): {
                'edge_status': {'edges': {'edgeState': 'CONNECTED'}, 'enterprise_name': 'EVIL-CORP|12345|'},
                'addition_timestamp': 987654321,
            },
            EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=654, edge_id=987): {
                'edge_status': {'edges': {'edgeState': 'CONNECTED'}, 'enterprise_name': 'EVIL-CORP|12345|'},
                'addition_timestamp': 789123456,
            },
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        quarantine_edge_repository = Mock()
        quarantine_edge_repository.get_all_edges = Mock(return_value=quarantine_edges)

        online_edge_repository = Mock()
        online_edge_repository.get_all_edges = Mock(return_value=online_edges)

        detected_outages_observer = DetectedOutagesObserver(event_bus, logger, scheduler,
                                                            online_edge_repository, quarantine_edge_repository,
                                                            reporting_edge_repository, config)
        detected_outages_observer._purge_edge_stores = Mock()
        detected_outages_observer._process_quarantine = CoroutineMock()

        await detected_outages_observer._observe_detected_outages()

        detected_outages_observer._purge_edge_stores.assert_called_once()
        detected_outages_observer._process_quarantine.assert_called_once()

    def purge_edge_stores_test(self):
        online_edges = {
            EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=123, edge_id=456): {
                'edge_status': {'edges': {'edgeState': 'CONNECTED'}, 'enterprise_name': 'EVIL-CORP|12345|'},
                'addition_timestamp': 123456789,
            },
            EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=789, edge_id=321): {
                'edge_status': {'edges': {'edgeState': 'CONNECTED'}, 'enterprise_name': 'EVIL-CORP|12345|'},
                'addition_timestamp': 987654321,
            },
            EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=654, edge_id=987): {
                'edge_status': {'edges': {'edgeState': 'CONNECTED'}, 'enterprise_name': 'EVIL-CORP|12345|'},
                'addition_timestamp': 789123456,
            },
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        online_edge_repository = Mock()
        online_edge_repository.get_all_edges = Mock(return_value=online_edges)

        detected_outages_observer = DetectedOutagesObserver(event_bus, logger, scheduler,
                                                            online_edge_repository, quarantine_edge_repository,
                                                            reporting_edge_repository, config)
        detected_outages_observer._remove_online_edges_from_quarantine = Mock()
        detected_outages_observer._remove_online_edges_from_edges_to_report = Mock()
        detected_outages_observer._clear_online_edges_store = Mock()

        detected_outages_observer._purge_edge_stores()

        online_edge_repository.get_all_edges.assert_called_once()
        detected_outages_observer._remove_online_edges_from_quarantine.assert_called_once_with(online_edges.keys())
        detected_outages_observer._remove_online_edges_from_edges_to_report.assert_called_once_with(online_edges.keys())
        detected_outages_observer._clear_online_edges_store.assert_called_once()

    def remove_online_edges_from_quarantine_test(self):
        online_edges = {
            EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=123, edge_id=456): {
                'edge_status': {'edges': {'edgeState': 'CONNECTED'}, 'enterprise_name': 'EVIL-CORP|12345|'},
                'addition_timestamp': 123456789,
            },
            EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=789, edge_id=321): {
                'edge_status': {'edges': {'edgeState': 'CONNECTED'}, 'enterprise_name': 'EVIL-CORP|12345|'},
                'addition_timestamp': 987654321,
            },
            EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=654, edge_id=987): {
                'edge_status': {'edges': {'edgeState': 'CONNECTED'}, 'enterprise_name': 'EVIL-CORP|12345|'},
                'addition_timestamp': 789123456,
            },
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        detected_outages_observer = DetectedOutagesObserver(event_bus, logger, scheduler,
                                                            online_edge_repository, quarantine_edge_repository,
                                                            reporting_edge_repository, config)

        detected_outages_observer._remove_online_edges_from_quarantine(online_edges.keys())

        quarantine_edge_repository.remove_edge_set.assert_called_once_with(*online_edges.keys())

    def remove_online_edges_from_edges_to_report_test(self):
        online_edges = {
            EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=123, edge_id=456): {
                'edge_status': {'edges': {'edgeState': 'CONNECTED'}, 'enterprise_name': 'EVIL-CORP|12345|'},
                'addition_timestamp': 123456789,
            },
            EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=789, edge_id=321): {
                'edge_status': {'edges': {'edgeState': 'CONNECTED'}, 'enterprise_name': 'EVIL-CORP|12345|'},
                'addition_timestamp': 987654321,
            },
            EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=654, edge_id=987): {
                'edge_status': {'edges': {'edgeState': 'CONNECTED'}, 'enterprise_name': 'EVIL-CORP|12345|'},
                'addition_timestamp': 789123456,
            },
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        detected_outages_observer = DetectedOutagesObserver(event_bus, logger, scheduler,
                                                            online_edge_repository, quarantine_edge_repository,
                                                            reporting_edge_repository, config)

        detected_outages_observer._remove_online_edges_from_edges_to_report(online_edges.keys())

        reporting_edge_repository.remove_edge_set.assert_called_once_with(*online_edges.keys())

    def clear_online_edges_store_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        detected_outages_observer = DetectedOutagesObserver(event_bus, logger, scheduler,
                                                            online_edge_repository, quarantine_edge_repository,
                                                            reporting_edge_repository, config)

        detected_outages_observer._clear_online_edges_store()

        online_edge_repository.reset_root_key.assert_called_once()

    @pytest.mark.asyncio
    async def process_quarantine_with_no_outages_yet_test(self):
        quarantine_edge_1_value = {
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}, 'enterprise_name': 'EVIL-CORP|12345|'},
            'addition_timestamp': 123456789,
        }
        quarantine_edge_2_value = {
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}, 'enterprise_name': 'EVIL-CORP|12345|'},
            'addition_timestamp': 987654321,
        }
        quarantine_edge_3_value = {
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}, 'enterprise_name': 'EVIL-CORP|12345|'},
            'addition_timestamp': 789123456,
        }
        quarantine_edges = {
            EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=123, edge_id=456): quarantine_edge_1_value,
            EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=789, edge_id=321): quarantine_edge_2_value,
            EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=654, edge_id=987): quarantine_edge_3_value,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        quarantine_edge_repository = Mock()
        quarantine_edge_repository.get_all_edges = Mock(return_value=quarantine_edges)

        detected_outages_observer = DetectedOutagesObserver(event_bus, logger, scheduler,
                                                            online_edge_repository, quarantine_edge_repository,
                                                            reporting_edge_repository, config)
        detected_outages_observer._is_there_an_outage = Mock(return_value=False)
        detected_outages_observer._get_outage_ticket_for_edge = CoroutineMock()

        await detected_outages_observer._process_quarantine()

        quarantine_edge_repository.get_all_edges.assert_called_once()
        detected_outages_observer._is_there_an_outage.assert_has_calls([
            call(quarantine_edge_1_value),
            call(quarantine_edge_2_value),
            call(quarantine_edge_3_value),
        ])
        detected_outages_observer._get_outage_ticket_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_quarantine_with_some_outages_and_some_missing_outage_tickets_test(self):
        quarantine_edge_1_identifier = EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=123, edge_id=456)
        quarantine_edge_2_identifier = EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=789, edge_id=321)
        quarantine_edge_3_identifier = EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=654, edge_id=987)
        quarantine_edge_1_value = {
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}},
            'addition_timestamp': 123456789,
        }
        quarantine_edge_2_value = {
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}},
            'addition_timestamp': 987654321,
        }
        quarantine_edge_3_value = {
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}},
            'addition_timestamp': 789123456,
        }
        quarantine_edges = {
            quarantine_edge_1_identifier: quarantine_edge_1_value,
            quarantine_edge_2_identifier: quarantine_edge_2_value,
            quarantine_edge_3_identifier: quarantine_edge_3_value,
        }

        has_edge_1_outage = True
        has_edge_2_outage = False
        has_edge_3_outage = True
        has_edge_outage_side_effect = [has_edge_1_outage, has_edge_2_outage, has_edge_3_outage]

        edge_1_outage_ticket_id = 12345
        edge_3_outage_ticket_id = None
        edge_1_outage_ticket = {
            'ticketID': 12345,
            'ticketDetails': [
                {
                    "detailID": 2746937,
                    "detailValue": 'VC1234567',
                },
            ],
            'ticketNotes': [
                {
                    "noteId": 41894041,
                    "noteValue": f'#*Automation Engine*# \n TimeStamp: 2019-07-30 06:38:00+00:00',
                }
            ],
        }
        edge_3_outage_ticket = None
        edge_outage_ticket_side_effect = [edge_1_outage_ticket, edge_3_outage_ticket]

        dict_for_edge_1_reporting = {
            **quarantine_edge_1_value,
            'ticketID': edge_1_outage_ticket_id,
        }
        dict_for_edge_3_reporting = {
            **quarantine_edge_3_value,
            'ticketID': edge_3_outage_ticket_id,
        }

        edges_to_report = {
            quarantine_edge_1_identifier: dict_for_edge_1_reporting,
            quarantine_edge_3_identifier: dict_for_edge_3_reporting,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        quarantine_edge_repository = Mock()
        quarantine_edge_repository.get_all_edges = Mock(return_value=quarantine_edges)

        detected_outages_observer = DetectedOutagesObserver(event_bus, logger, scheduler,
                                                            online_edge_repository, quarantine_edge_repository,
                                                            reporting_edge_repository, config)
        detected_outages_observer._is_there_an_outage = Mock(side_effect=has_edge_outage_side_effect)
        detected_outages_observer._get_outage_ticket_for_edge = CoroutineMock(
            side_effect=edge_outage_ticket_side_effect)
        detected_outages_observer._move_edges_to_reporting = Mock()

        await detected_outages_observer._process_quarantine()

        quarantine_edge_repository.get_all_edges.assert_called_once()
        detected_outages_observer._is_there_an_outage.assert_has_calls([
            call(quarantine_edge_1_value),
            call(quarantine_edge_2_value),
            call(quarantine_edge_3_value),
        ])
        detected_outages_observer._get_outage_ticket_for_edge.assert_has_awaits([
            call(quarantine_edge_1_value),
            call(quarantine_edge_3_value),
        ])
        detected_outages_observer._move_edges_to_reporting.assert_called_once_with(edges_to_report)

    def is_there_an_outage_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        detected_outages_observer = DetectedOutagesObserver(event_bus, logger, scheduler,
                                                            online_edge_repository, quarantine_edge_repository,
                                                            reporting_edge_repository, config)

        current_datetime = datetime.now()
        datetime_mock = Mock()
        datetime_mock.fromtimestamp = datetime.fromtimestamp

        edge_value = {
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}, 'enterprise_name': 'EVIL-CORP|12345|'},
            'addition_timestamp': datetime.timestamp(current_datetime - timedelta(minutes=39, seconds=59)),
        }
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(service_outage_detector_module, 'datetime', new=datetime_mock):
            is_there_outage = detected_outages_observer._is_there_an_outage(edge_value)
            assert is_there_outage is False

        edge_value = {
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}, 'enterprise_name': 'EVIL-CORP|12345|'},
            'addition_timestamp': datetime.timestamp(current_datetime - timedelta(minutes=40)),
        }
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(service_outage_detector_module, 'datetime', new=datetime_mock):
            is_there_outage = detected_outages_observer._is_there_an_outage(edge_value)
            assert is_there_outage is False

        edge_value = {
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}, 'enterprise_name': 'EVIL-CORP|12345|'},
            'addition_timestamp': datetime.timestamp(current_datetime - timedelta(minutes=40, seconds=1)),
        }
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(service_outage_detector_module, 'datetime', new=datetime_mock):
            is_there_outage = detected_outages_observer._is_there_an_outage(edge_value)
            assert is_there_outage is True

    @pytest.mark.asyncio
    async def get_outage_ticket_for_edge_test(self):
        client_id = 12345
        enterprise_name = f'EVIL-CORP|{client_id}|'
        edge_serial_number = 'VC1234567'
        quarantine_edge_value = {
            'edge_status': {
                'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial_number},
                'enterprise_name': enterprise_name,
            },
            'addition_timestamp': 123456789,
        }

        outage_ticket = {
            'ticketID': 12345,
            'ticketDetails': [
                {
                    "detailID": 2746937,
                    "detailValue": edge_serial_number,
                },
            ],
            'ticketNotes': [
                {
                    "noteId": 41894041,
                    "noteValue": f'#*Automation Engine*# \n TimeStamp: 2019-07-30 06:38:00+00:00',
                }
            ],
        }

        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=outage_ticket)

        detected_outages_observer = DetectedOutagesObserver(event_bus, logger, scheduler,
                                                            online_edge_repository, quarantine_edge_repository,
                                                            reporting_edge_repository, config)
        detected_outages_observer._extract_client_id = Mock(return_value=client_id)

        uuid_ = uuid()
        with patch.object(service_outage_detector_module, 'uuid', return_value=uuid_):
            outage_ticket_result = await detected_outages_observer._get_outage_ticket_for_edge(quarantine_edge_value)

        detected_outages_observer._extract_client_id.assert_called_once_with(enterprise_name)
        event_bus.rpc_request.assert_awaited_once_with(
            'bruin.ticket.outage.details.by_edge_serial.request',
            json.dumps({
                'request_id': uuid_,
                'edge_serial': edge_serial_number,
                'client_id': client_id,
            })
        )
        assert outage_ticket_result == outage_ticket

    def extract_client_id_test(self):
        client_id = 12345
        enterprise_name = f'EVIL-CORP|{client_id}|'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        detected_outages_observer = DetectedOutagesObserver(event_bus, logger, scheduler,
                                                            online_edge_repository, quarantine_edge_repository,
                                                            reporting_edge_repository, config)

        result_client_id = detected_outages_observer._extract_client_id(enterprise_name)
        assert result_client_id == str(client_id)

    def move_edges_to_reporting_test(self):
        edge_1_identifier = EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=123, edge_id=456)
        edge_2_identifier = EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=789, edge_id=321)
        edge_1_value = {
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}},
            'addition_timestamp': 123456789,
            'ticketID': 12345,
        }
        edge_2_value = {
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}},
            'addition_timestamp': 123456789,
            'ticketID': 67890,
        }

        edges_to_report = [
            {edge_1_identifier: edge_1_value},
            {edge_2_identifier: edge_2_value},
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        online_edge_repository = Mock()
        config = testconfig

        quarantine_edge_repository = Mock()
        quarantine_edge_repository.reset_root_key = Mock()

        reporting_edge_repository = Mock()
        reporting_edge_repository.add_edge_set = Mock()

        detected_outages_observer = DetectedOutagesObserver(event_bus, logger, scheduler,
                                                            online_edge_repository, quarantine_edge_repository,
                                                            reporting_edge_repository, config)

        detected_outages_observer._move_edges_to_reporting(edges_to_report)

        quarantine_edge_repository.reset_root_key.assert_called_once()
        reporting_edge_repository.add_edge_set.assert_called_once_with(edges_to_report)
