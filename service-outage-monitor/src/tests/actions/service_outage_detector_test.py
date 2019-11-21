import json
import pytest

from datetime import datetime
from datetime import timedelta
from unittest.mock import call
from unittest.mock import Mock
from unittest.mock import patch

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from asynctest import CoroutineMock
from shortuuid import uuid

from application.actions import service_outage_detector as service_outage_detector_module
from application.actions.service_outage_detector import ServiceOutageDetector
from application.repositories.edge_repository import EdgeIdentifier
from config import testconfig


class TestServiceOutageDetector:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)

        assert service_outage_detector._event_bus is event_bus
        assert service_outage_detector._logger is logger
        assert service_outage_detector._scheduler is scheduler
        assert service_outage_detector._quarantine_edge_repository is quarantine_edge_repository
        assert service_outage_detector._reporting_edge_repository is reporting_edge_repository
        assert service_outage_detector._config is config

    @pytest.mark.asyncio
    async def load_persisted_quarantine_test(self):
        edge_1_identifier = EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=1234, edge_id=5678)
        edge_2_identifier = EdgeIdentifier(host='mettel.velocloud.net', enterprise_id=4321, edge_id=8765)

        edge_1_full_id = edge_1_identifier._asdict()
        edge_2_full_id = edge_2_identifier._asdict()

        edge_1_addition_timestamp = 1234567890
        edge_2_addition_timestamp = 9876543210
        quarantine_edges = {
            edge_1_identifier: {
                'edge_status': {
                    'edges': {'edgeState': 'OFFLINE'},
                    'links': [
                        {'linkId': 1234, 'link': {'state': 'DISCONNECTED'}},
                        {'linkId': 5678, 'link': {'state': 'DISCONNECTED'}},
                    ],
                    'enterprise_name': 'EVIL-CORP|12345|',
                },
                'addition_timestamp': edge_1_addition_timestamp,
            },
            edge_2_identifier: {
                'edge_status': {
                    'edges': {'edgeState': 'CONNECTED'},
                    'links': [
                        {'linkId': 1234, 'link': {'state': 'DISCONNECTED'}},
                        {'linkId': 5678, 'link': {'state': 'DISCONNECTED'}},
                    ],
                    'enterprise_name': 'EVIL-CORP|12345|',
                },
                'addition_timestamp': edge_2_addition_timestamp,
            }
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        quarantine_edge_repository = Mock()
        quarantine_edge_repository.get_all_edges = Mock(return_value=quarantine_edges)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)
        service_outage_detector._start_quarantine_job = CoroutineMock()

        await service_outage_detector.load_persisted_quarantine()

        quarantine_edge_repository.get_all_edges.assert_called_once()

        quarantine_time = config.MONITOR_CONFIG['jobs_intervals']['quarantine']
        service_outage_detector._start_quarantine_job.assert_has_awaits([
            call(
                edge_1_full_id,
                run_date=datetime.fromtimestamp(edge_1_addition_timestamp + quarantine_time)
            ),
            call(
                edge_2_full_id,
                run_date=datetime.fromtimestamp(edge_2_addition_timestamp + quarantine_time)
            ),
        ])


class TestServiceOutageDetectorJob:
    @pytest.mark.asyncio
    async def start_service_outage_detector_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
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
            replace_existing=False,
            id='_service_outage_detector_process',
        )

    @pytest.mark.asyncio
    async def start_service_outage_detector_job_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)

        await service_outage_detector.start_service_outage_detector_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            service_outage_detector._service_outage_detector_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_detector'],
            next_run_time=undefined,
            replace_existing=False,
            id='_service_outage_detector_process',
        )

    @pytest.mark.asyncio
    async def start_service_outage_detector_job_with_job_id_already_executing_test(self):
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        event_bus = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)

        try:
            await service_outage_detector.start_service_outage_detector_job()
            pytest.fail('Call to function did not raise the expected exception')
        except:
            scheduler.add_job.assert_called_once_with(
                service_outage_detector._service_outage_detector_process, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_detector'],
                next_run_time=undefined,
                replace_existing=False,
                id='_service_outage_detector_process',
            )

    @pytest.mark.asyncio
    async def service_outage_detector_process_with_no_edges_found_test(self):
        edge_list = []

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)
        service_outage_detector._get_all_edges = CoroutineMock(return_value=edge_list)

        await service_outage_detector._service_outage_detector_process()

        service_outage_detector._get_all_edges.assert_awaited_once()

    @pytest.mark.asyncio
    async def service_outage_detector_process_with_edges_found_and_healthy_edges_test(self):
        edge_1_id = 5678
        edge_2_id = 8765
        edge_3_id = 3344
        edge_1_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': edge_1_id}
        edge_2_full_id = {'host': 'metvco03.mettel.net', 'enterprise_id': 4321, 'edge_id': edge_2_id}
        edge_3_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1122, 'edge_id': edge_3_id}
        edge_list = [edge_1_full_id, edge_2_full_id, edge_3_full_id]

        edge_1_status = {
            'edges': {'edgeState': 'CONNECTED'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE'}},
                {'linkId': 5678, 'link': {'state': 'STABLE'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE'}},
                {'linkId': 5678, 'link': {'state': 'STABLE'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE'}},
                {'linkId': 5678, 'link': {'state': 'STABLE'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_statuses = [edge_1_status, edge_2_status, edge_3_status]

        is_there_outage_side_effect = [False, False, False]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)
        service_outage_detector._get_all_edges = CoroutineMock(return_value=edge_list)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(side_effect=edge_statuses)
        service_outage_detector._is_there_an_outage = Mock(side_effect=is_there_outage_side_effect)
        service_outage_detector._start_quarantine_job = Mock()
        service_outage_detector._add_edge_to_quarantine = Mock()

        await service_outage_detector._service_outage_detector_process()

        service_outage_detector._get_all_edges.assert_awaited_once()
        service_outage_detector._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id), call(edge_2_full_id), call(edge_3_full_id)
        ])
        service_outage_detector._is_there_an_outage.assert_has_calls([
            call(edge_1_status), call(edge_2_status),
        ])
        service_outage_detector._start_quarantine_job.assert_not_called()
        service_outage_detector._add_edge_to_quarantine.assert_not_called()

    @pytest.mark.asyncio
    async def service_outage_detector_process_with_edges_found_and_edges_with_outages_test(self):
        edge_1_id = 5678
        edge_2_id = 8765
        edge_3_id = 3344
        edge_1_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': edge_1_id}
        edge_2_full_id = {'host': 'metvco03.mettel.net', 'enterprise_id': 4321, 'edge_id': edge_2_id}
        edge_3_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1122, 'edge_id': edge_3_id}
        edge_list = [edge_1_full_id, edge_2_full_id, edge_3_full_id]

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE'}},
                {'linkId': 5678, 'link': {'state': 'STABLE'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE'}},
                {'linkId': 5678, 'link': {'state': 'STABLE'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_statuses = [edge_1_status, edge_2_status, edge_3_status]

        is_there_outage_side_effect = [True, False, True]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)
        service_outage_detector._get_all_edges = CoroutineMock(return_value=edge_list)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(side_effect=edge_statuses)
        service_outage_detector._is_there_an_outage = Mock(side_effect=is_there_outage_side_effect)
        service_outage_detector._start_quarantine_job = CoroutineMock()
        service_outage_detector._add_edge_to_quarantine = Mock()

        await service_outage_detector._service_outage_detector_process()

        service_outage_detector._get_all_edges.assert_awaited_once()
        service_outage_detector._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id), call(edge_2_full_id), call(edge_3_full_id)
        ])
        service_outage_detector._start_quarantine_job.assert_has_awaits([
            call(edge_1_full_id), call(edge_3_full_id)
        ])
        service_outage_detector._add_edge_to_quarantine.assert_has_calls([
            call(edge_1_full_id, edge_1_status),
            call(edge_3_full_id, edge_3_status),
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
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=edge_list_response)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
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
            'edges': {'edgeState': 'CONNECTED'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE'}},
                {'linkId': 5678, 'link': {'state': 'STABLE'}},
            ],
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
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=edge_status_response)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
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

    def add_edge_to_quarantine_test(self):
        edge_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)

        service_outage_detector._add_edge_to_quarantine(edge_full_id, edge_status)

        quarantine_edge_repository.add_edge.assert_called_once_with(
            edge_full_id, edge_status,
            replace_existing=False,
            time_to_live=config.MONITOR_CONFIG['quarantine_key_ttl'],
        )

    def is_there_an_outage_edge_test(self):
        edge_status_1 = {
            'edges': {'edgeState': 'CONNECTED'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE'}},
                {'linkId': 5678, 'link': {'state': 'STABLE'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_status_2 = {
            'edges': {'edgeState': 'OFFLINE'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_status_3 = {
            'edges': {'edgeState': 'CONNECTED'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)

        result = service_outage_detector._is_there_an_outage(edge_status_1)
        assert result is False

        result = service_outage_detector._is_there_an_outage(edge_status_2)
        assert result is True

        result = service_outage_detector._is_there_an_outage(edge_status_3)
        assert result is True


class TestQuarantineJob:
    @pytest.mark.asyncio
    async def start_quarantine_job_with_run_date_undefined_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)

        current_datetime = datetime.now()
        current_timestamp = datetime.timestamp(current_datetime)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        datetime_mock.timestamp = Mock(return_value=current_timestamp)
        with patch.object(service_outage_detector_module, 'datetime', new=datetime_mock):
            with patch.object(service_outage_detector_module, 'timezone', new=Mock()):
                await service_outage_detector._start_quarantine_job(edge_full_id, run_date=None)

        job_run_date = current_datetime + timedelta(seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'])
        scheduler.add_job.assert_called_once_with(
            service_outage_detector._process_edge_from_quarantine, 'date',
            run_date=job_run_date,
            replace_existing=False,
            misfire_grace_time=9999,
            id=f'_quarantine_{json.dumps(edge_full_id)}',
            kwargs={'edge_full_id': edge_full_id},
        )

    @pytest.mark.asyncio
    async def start_quarantine_job_with_custom_run_date_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)

        job_run_date = datetime.fromtimestamp(999999)
        await service_outage_detector._start_quarantine_job(edge_full_id, run_date=job_run_date)

        scheduler.add_job.assert_called_once_with(
            service_outage_detector._process_edge_from_quarantine, 'date',
            run_date=job_run_date,
            replace_existing=False,
            misfire_grace_time=9999,
            id=f'_quarantine_{json.dumps(edge_full_id)}',
            kwargs={'edge_full_id': edge_full_id},
        )

    @pytest.mark.asyncio
    async def start_quarantine_job_with_job_id_already_executing_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        event_bus = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)

        current_datetime = datetime.now()
        current_timestamp = datetime.timestamp(current_datetime)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        datetime_mock.timestamp = Mock(return_value=current_timestamp)

        try:
            with patch.object(service_outage_detector_module, 'datetime', new=datetime_mock):
                with patch.object(service_outage_detector_module, 'timezone', new=Mock()):
                    await service_outage_detector._start_quarantine_job(edge_full_id)
            pytest.fail('Call to function did not raise the expected exception')
        except:
            job_run_date = current_datetime + timedelta(seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'])
            scheduler.add_job.assert_called_once_with(
                service_outage_detector._process_edge_from_quarantine, 'date',
                run_date=job_run_date,
                replace_existing=False,
                misfire_grace_time=9999,
                id=f'_quarantine_{json.dumps(edge_full_id)}',
                kwargs={'edge_full_id': edge_full_id},
            )

    @pytest.mark.asyncio
    async def process_edge_from_quarantine_with_no_outage_occurring_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)
        service_outage_detector._is_there_an_outage = Mock(return_value=False)
        service_outage_detector._get_outage_ticket_for_edge = CoroutineMock()
        service_outage_detector._add_edge_to_reporting = Mock()

        await service_outage_detector._process_edge_from_quarantine(edge_full_id)

        service_outage_detector._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        service_outage_detector._is_there_an_outage.assert_called_once_with(edge_status)
        service_outage_detector._get_outage_ticket_for_edge.assert_not_awaited()
        service_outage_detector._add_edge_to_reporting.assert_not_called()

    @pytest.mark.asyncio
    async def process_edge_from_quarantine_with_outage_occurring_and_existing_ticket_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        outage_ticket = {
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

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)
        service_outage_detector._is_there_an_outage = CoroutineMock(return_value=True)
        service_outage_detector._get_outage_ticket_for_edge = CoroutineMock(return_value=outage_ticket)
        service_outage_detector._add_edge_to_reporting = Mock()

        await service_outage_detector._process_edge_from_quarantine(edge_full_id)

        service_outage_detector._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        service_outage_detector._is_there_an_outage.assert_called_once_with(edge_status)
        service_outage_detector._get_outage_ticket_for_edge.assert_awaited_once_with(edge_full_id)
        service_outage_detector._add_edge_to_reporting.assert_not_called()

    @pytest.mark.asyncio
    async def process_edge_from_quarantine_with_outage_occurring_and_no_existing_ticket_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        outage_ticket = None

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)
        service_outage_detector._is_there_an_outage = CoroutineMock(return_value=True)
        service_outage_detector._get_outage_ticket_for_edge = CoroutineMock(return_value=outage_ticket)
        service_outage_detector._add_edge_to_reporting = Mock()

        await service_outage_detector._process_edge_from_quarantine(edge_full_id)

        service_outage_detector._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        service_outage_detector._is_there_an_outage.assert_called_once_with(edge_status)
        service_outage_detector._get_outage_ticket_for_edge.assert_awaited_once_with(edge_full_id)
        service_outage_detector._add_edge_to_reporting.assert_called_once_with(edge_full_id, edge_status)

    @pytest.mark.asyncio
    async def get_outage_ticket_for_edge_test(self):
        client_id = 12345
        enterprise_name = f'EVIL-CORP|{client_id}|'
        edge_serial_number = 'VC1234567'
        quarantine_edge_value = {
            'edge_status': {
                'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial_number},
                'links': [
                    {'linkId': 1234, 'link': {'state': 'STABLE'}},
                    {'linkId': 5678, 'link': {'state': 'STABLE'}},
                ],
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
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=outage_ticket)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)
        service_outage_detector._extract_client_id = Mock(return_value=client_id)

        uuid_ = uuid()
        with patch.object(service_outage_detector_module, 'uuid', return_value=uuid_):
            outage_ticket_result = await service_outage_detector._get_outage_ticket_for_edge(quarantine_edge_value)

        service_outage_detector._extract_client_id.assert_called_once_with(enterprise_name)
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
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)

        result_client_id = service_outage_detector._extract_client_id(enterprise_name)
        assert result_client_id == str(client_id)

    def add_edge_to_reporting_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}
        client_id = 12345
        edge_status = {
            'edges': {'edgeState': 'OFFLINE'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
        }

        addition_to_quarantine_timestamp = 123456789
        edge_status_in_quarantine = {
            'edge_status': {
                'edges': {'edgeState': 'CONNECTED'},
                'links': [
                    {'linkId': 1234, 'link': {'state': 'DISCONNECTED'}},
                    {'linkId': 5678, 'link': {'state': 'STABLE'}},
                ],
                'enterprise_name': 'EVIL-CORP|12345|',
            },
            'addition_timestamp': addition_to_quarantine_timestamp,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        quarantine_edge_repository = Mock()
        quarantine_edge_repository.get_edge = Mock(return_value=edge_status_in_quarantine)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)

        service_outage_detector._add_edge_to_reporting(edge_full_id, edge_status)

        quarantine_edge_repository.get_edge.assert_called_once_with(edge_full_id)
        reporting_edge_repository.add_edge.assert_called_once_with(
            edge_full_id,
            {
                'edge_status': edge_status,
                'detection_timestamp': addition_to_quarantine_timestamp,
            }
        )
        quarantine_edge_repository.remove_edge.assert_called_once_with(edge_full_id)

    def add_edge_to_reporting_with_edge_missing_in_quarantine_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}
        client_id = 12345
        edge_status = {
            'edges': {'edgeState': 'OFFLINE'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        quarantine_edge_repository = Mock()
        quarantine_edge_repository.get_edge = Mock(return_value=None)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)

        current_datetime = datetime.now()
        current_timestamp = datetime.timestamp(current_datetime)
        datetime_mock = Mock()
        datetime_mock.timestamp = Mock(return_value=current_timestamp)
        with patch.object(service_outage_detector_module, 'datetime', new=datetime_mock):
            with patch.object(service_outage_detector_module, 'timezone', new=Mock()):
                service_outage_detector._add_edge_to_reporting(edge_full_id, edge_status)

        assumed_detection_timestamp = current_timestamp - config.MONITOR_CONFIG['jobs_intervals']['quarantine']
        reporting_edge_repository.add_edge.assert_called_once_with(
            edge_full_id,
            {
                'edge_status': edge_status,
                'detection_timestamp': assumed_detection_timestamp,
            }
        )


class TestServiceOutageReporterJob:
    @pytest.mark.asyncio
    async def start_service_outage_reporter_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(service_outage_detector_module, 'datetime', new=datetime_mock):
            with patch.object(service_outage_detector_module, 'timezone', new=Mock()):
                await service_outage_detector.start_service_outage_reporter_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            service_outage_detector._service_outage_reporter_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_reporter'],
            next_run_time=next_run_time,
            replace_existing=True,
            id='_service_outage_reporter_process',
        )

    @pytest.mark.asyncio
    async def start_service_outage_reporter_job_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config)

        await service_outage_detector.start_service_outage_reporter_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            service_outage_detector._service_outage_reporter_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_reporter'],
            next_run_time=undefined,
            replace_existing=True,
            id='_service_outage_reporter_process',
        )
