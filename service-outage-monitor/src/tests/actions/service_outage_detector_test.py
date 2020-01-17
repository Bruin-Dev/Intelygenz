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
from pytz import timezone
from shortuuid import uuid

from application.actions import service_outage_detector as service_outage_detector_module
from application.actions.service_outage_detector import ServiceOutageDetector
from igz.packages.repositories.edge_repository import EdgeIdentifier
from config import testconfig


class TestServiceOutageDetector:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = Mock()
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        assert service_outage_detector._event_bus is event_bus
        assert service_outage_detector._logger is logger
        assert service_outage_detector._scheduler is scheduler
        assert service_outage_detector._quarantine_edge_repository is quarantine_edge_repository
        assert service_outage_detector._reporting_edge_repository is reporting_edge_repository
        assert service_outage_detector._config is config
        assert service_outage_detector._outage_utils is outage_utils

    @pytest.mark.asyncio
    async def report_persisted_edges_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector.start_service_outage_reporter_job = CoroutineMock()

        await service_outage_detector.report_persisted_edges()

        service_outage_detector.start_service_outage_reporter_job.assert_awaited_once_with(exec_on_start=True)

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
                    'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
                    'links': [
                        {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                        {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                    ],
                    'enterprise_name': 'EVIL-CORP|12345|',
                },
                'addition_timestamp': edge_1_addition_timestamp,
            },
            edge_2_identifier: {
                'edge_status': {
                    'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC7654321'},
                    'links': [
                        {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                        {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
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
        template_renderer = Mock()
        outage_utils = Mock()

        quarantine_edge_repository = Mock()
        quarantine_edge_repository.get_all_edges = Mock(return_value=quarantine_edges)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
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
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

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
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

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
        template_renderer = Mock()
        outage_utils = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        try:
            await service_outage_detector.start_service_outage_detector_job()
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
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
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_all_edges = CoroutineMock(return_value=edge_list)

        await service_outage_detector._service_outage_detector_process()

        service_outage_detector._get_all_edges.assert_awaited_once()

    @pytest.mark.asyncio
    async def service_outage_detector_process_with_edges_found_and_edges_for_testing_test(self):
        edge_1_id = 5678
        edge_2_id = 8765
        edge_3_id = 3344
        edge_1_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': edge_1_id}
        edge_2_full_id = {'host': 'metvco03.mettel.net', 'enterprise_id': 4321, 'edge_id': edge_2_id}
        edge_3_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1122, 'edge_id': edge_3_id}
        edge_list = [edge_1_full_id, edge_2_full_id, edge_3_full_id]

        edge_1_enterprise_name = 'EVIL-CORP|12345|'
        edge_2_enterprise_name = 'EVIL-CORP-TEST'
        edge_3_enterprise_name = 'EVIL-CORP-TEST-2'

        edge_1_state = 'CONNECTED'
        edge_1_link_ge1_state = edge_1_link_ge2_state = 'STABLE'
        edge_1_status = {
            'edges': {'edgeState': edge_1_state, 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': edge_1_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_1_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': edge_1_enterprise_name,
        }

        edge_2_state = 'CONNECTED'
        edge_2_link_ge1_state = edge_2_link_ge2_state = 'STABLE'
        edge_2_status = {
            'edges': {'edgeState': edge_2_state, 'serialNumber': 'VC7654321'},
            'links': [
                {'linkId': 1234, 'link': {'state': edge_2_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_2_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': edge_2_enterprise_name,
        }

        edge_3_state = 'CONNECTED'
        edge_3_link_ge1_state = edge_3_link_ge2_state = 'STABLE'
        edge_3_status = {
            'edges': {'edgeState': edge_3_state, 'serialNumber': 'VC1112223'},
            'links': [
                {'linkId': 1234, 'link': {'state': edge_3_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_3_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': edge_3_enterprise_name,
        }
        edge_statuses = [edge_1_status, edge_2_status, edge_3_status]

        is_edge_for_testing_side_effect = [False, True, True]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(return_value=False)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_all_edges = CoroutineMock(return_value=edge_list)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(side_effect=edge_statuses)
        service_outage_detector._is_edge_for_testing_purposes = Mock(side_effect=is_edge_for_testing_side_effect)
        service_outage_detector._start_quarantine_job = Mock()
        service_outage_detector._add_edge_to_quarantine = Mock()

        await service_outage_detector._service_outage_detector_process()

        service_outage_detector._get_all_edges.assert_awaited_once()
        service_outage_detector._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id), call(edge_2_full_id), call(edge_3_full_id)
        ])
        service_outage_detector._is_edge_for_testing_purposes.assert_has_calls([
            call(edge_1_enterprise_name),
            call(edge_2_enterprise_name),
            call(edge_3_enterprise_name),
        ])
        service_outage_detector._start_quarantine_job.assert_not_called()
        service_outage_detector._add_edge_to_quarantine.assert_not_called()

    @pytest.mark.asyncio
    async def service_outage_detector_process_with_edges_found_and_no_edges_for_testing_and_healthy_edges_test(self):
        edge_1_id = 5678
        edge_2_id = 8765
        edge_3_id = 3344
        edge_1_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': edge_1_id}
        edge_2_full_id = {'host': 'metvco03.mettel.net', 'enterprise_id': 4321, 'edge_id': edge_2_id}
        edge_3_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1122, 'edge_id': edge_3_id}
        edge_list = [edge_1_full_id, edge_2_full_id, edge_3_full_id]

        edge_1_enterprise_name = edge_2_enterprise_name = edge_3_enterprise_name = 'EVIL-CORP|12345|'

        edge_1_state = 'CONNECTED'
        edge_1_link_ge1_state = edge_1_link_ge2_state = 'STABLE'
        edge_1_status = {
            'edges': {'edgeState': edge_1_state, 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': edge_1_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_1_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': edge_1_enterprise_name,
        }

        edge_2_state = 'CONNECTED'
        edge_2_link_ge1_state = edge_2_link_ge2_state = 'STABLE'
        edge_2_status = {
            'edges': {'edgeState': edge_2_state, 'serialNumber': 'VC7654321'},
            'links': [
                {'linkId': 1234, 'link': {'state': edge_2_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_2_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': edge_2_enterprise_name,
        }

        edge_3_state = 'CONNECTED'
        edge_3_link_ge1_state = edge_3_link_ge2_state = 'STABLE'
        edge_3_status = {
            'edges': {'edgeState': edge_3_state, 'serialNumber': 'VC1112223'},
            'links': [
                {'linkId': 1234, 'link': {'state': edge_3_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_3_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': edge_3_enterprise_name,
        }
        edge_statuses = [edge_1_status, edge_2_status, edge_3_status]

        is_there_outage_side_effect = [False, False, False]
        is_edge_for_testing_side_effect = [False, False, False]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(side_effect=is_there_outage_side_effect)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_all_edges = CoroutineMock(return_value=edge_list)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(side_effect=edge_statuses)
        service_outage_detector._is_edge_for_testing_purposes = Mock(side_effect=is_edge_for_testing_side_effect)

        service_outage_detector._start_quarantine_job = Mock()
        service_outage_detector._add_edge_to_quarantine = Mock()

        await service_outage_detector._service_outage_detector_process()

        service_outage_detector._get_all_edges.assert_awaited_once()
        service_outage_detector._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id), call(edge_2_full_id), call(edge_3_full_id)
        ])
        service_outage_detector._is_edge_for_testing_purposes.assert_has_calls([
            call(edge_1_enterprise_name), call(edge_2_enterprise_name), call(edge_3_enterprise_name),
        ])
        service_outage_detector._start_quarantine_job.assert_not_called()
        service_outage_detector._add_edge_to_quarantine.assert_not_called()

    @pytest.mark.asyncio
    async def service_outage_detector_process_with_edges_found_and_no_edges_for_testing_and_edges_with_outages_test(
            self):
        edge_1_id = 5678
        edge_2_id = 8765
        edge_3_id = 3344
        edge_1_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': edge_1_id}
        edge_2_full_id = {'host': 'metvco03.mettel.net', 'enterprise_id': 4321, 'edge_id': edge_2_id}
        edge_3_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1122, 'edge_id': edge_3_id}
        edge_list = [edge_1_full_id, edge_2_full_id, edge_3_full_id]

        edge_1_enterprise_name = edge_2_enterprise_name = edge_3_enterprise_name = 'EVIL-CORP|12345|'

        edge_1_state = 'OFFLINE'
        edge_1_link_ge1_state = edge_1_link_ge2_state = 'STABLE'
        edge_1_status = {
            'edges': {'edgeState': edge_1_state, 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': edge_1_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_1_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': edge_1_enterprise_name,
        }

        edge_2_state = 'CONNECTED'
        edge_2_link_ge1_state = edge_2_link_ge2_state = 'STABLE'
        edge_2_status = {
            'edges': {'edgeState': edge_2_state, 'serialNumber': 'VC7654321'},
            'links': [
                {'linkId': 1234, 'link': {'state': edge_2_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_2_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': edge_2_enterprise_name,
        }

        edge_3_state = 'OFFLINE'
        edge_3_link_ge1_state = 'STABLE'
        edge_3_link_ge2_state = 'DISCONNECTED'
        edge_3_status = {
            'edges': {'edgeState': edge_3_state, 'serialNumber': 'VC1112223'},
            'links': [
                {'linkId': 1234, 'link': {'state': edge_3_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_3_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': edge_3_enterprise_name,
        }
        edge_statuses = [edge_1_status, edge_2_status, edge_3_status]

        is_there_outage_side_effect = [True, False, True]
        is_edge_for_testing_side_effect = [False, False, False]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(side_effect=is_there_outage_side_effect)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_all_edges = CoroutineMock(return_value=edge_list)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(side_effect=edge_statuses)
        service_outage_detector._is_edge_for_testing_purposes = Mock(side_effect=is_edge_for_testing_side_effect)
        service_outage_detector._start_quarantine_job = CoroutineMock()
        service_outage_detector._add_edge_to_quarantine = Mock()

        await service_outage_detector._service_outage_detector_process()

        service_outage_detector._get_all_edges.assert_awaited_once()
        service_outage_detector._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id), call(edge_2_full_id), call(edge_3_full_id)
        ])
        service_outage_detector._is_edge_for_testing_purposes.assert_has_calls([
            call(edge_1_enterprise_name), call(edge_2_enterprise_name), call(edge_3_enterprise_name),
        ])
        service_outage_detector._start_quarantine_job.assert_has_awaits([
            call(edge_1_full_id), call(edge_3_full_id)
        ])
        service_outage_detector._add_edge_to_quarantine.assert_has_calls([
            call(edge_1_full_id, edge_1_status),
            call(edge_3_full_id, edge_3_status),
        ])

    def is_edge_for_testing_purposes_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        enterprise_name = 'EVIL-CORP|12345|'
        result = service_outage_detector._is_edge_for_testing_purposes(enterprise_name)
        assert result is False

        enterprise_name = 'EVIL-CORP'
        result = service_outage_detector._is_edge_for_testing_purposes(enterprise_name)
        assert result is False

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
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        with patch.object(service_outage_detector_module, 'uuid', return_value=uuid_):
            result = await service_outage_detector._get_all_edges()

        event_bus.rpc_request.assert_awaited_once_with(
            'edge.list.request',
            {'request_id': uuid_, 'filter': []},
            timeout=600,
        )
        assert result == edge_list

    @pytest.mark.asyncio
    async def get_edge_status_by_id_test(self):
        uuid_ = uuid()
        edge_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
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
        template_renderer = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=edge_status_response)
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        with patch.object(service_outage_detector_module, 'uuid', return_value=uuid_):
            result = await service_outage_detector._get_edge_status_by_id(edge_full_id)

        event_bus.rpc_request.assert_awaited_once_with(
            'edge.status.request',
            {'request_id': uuid_, 'edge': edge_full_id},
            timeout=120,
        )
        assert result == edge_status

    def add_edge_to_quarantine_test(self):
        edge_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        service_outage_detector._add_edge_to_quarantine(edge_full_id, edge_status)

        quarantine_edge_repository.add_edge.assert_called_once_with(
            edge_full_id, {'edge_status': edge_status},
            update_existing=False,
            time_to_live=config.MONITOR_CONFIG['quarantine_key_ttl'],
        )

    def get_outage_cases_test(self):
        edge_1_state = 'CONNECTED'
        edge_1_link_ge1_state = edge_1_link_ge2_state = 'STABLE'
        edge_status_1 = {
            'edges': {'edgeState': edge_1_state, 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': edge_1_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_1_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        edge_2_state = 'OFFLINE'
        edge_2_link_ge1_state = edge_2_link_ge2_state = 'DISCONNECTED'
        edge_status_2 = {
            'edges': {'edgeState': edge_2_state, 'serialNumber': 'VC7654321'},
            'links': [
                {'linkId': 1234, 'link': {'state': edge_2_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_2_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        edge_3_state = 'OFFLINE'
        edge_3_link_ge1_state = 'STABLE'
        edge_3_link_ge2_state = 'DISCONNECTED'
        edge_status_3 = {
            'edges': {'edgeState': edge_3_state, 'serialNumber': 'VC1112223'},
            'links': [
                {'linkId': 1234, 'link': {'state': edge_3_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_3_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()
        outage_utils.is_faulty_edge = Mock(side_effect=[False, True, True])
        outage_utils.is_faulty_link = Mock(side_effect=[False, False, True, True, False, True])

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        result = service_outage_detector._get_outage_causes(edge_status_1)
        assert result is None

        result = service_outage_detector._get_outage_causes(edge_status_2)
        assert result == {'edge': 'OFFLINE', 'links': {'GE1': edge_2_link_ge1_state, 'GE2': edge_2_link_ge2_state}}

        result = service_outage_detector._get_outage_causes(edge_status_3)
        assert result == {'edge': 'OFFLINE', 'links': {'GE2': edge_2_link_ge2_state}}


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
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

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
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

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
        template_renderer = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        current_datetime = datetime.now()
        current_timestamp = datetime.timestamp(current_datetime)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        datetime_mock.timestamp = Mock(return_value=current_timestamp)

        try:
            with patch.object(service_outage_detector_module, 'datetime', new=datetime_mock):
                with patch.object(service_outage_detector_module, 'timezone', new=Mock()):
                    await service_outage_detector._start_quarantine_job(edge_full_id)
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
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
    async def process_edge_from_quarantine_with_no_reportable_edge_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)
        service_outage_detector._is_reportable_edge = CoroutineMock(return_value=False)
        service_outage_detector._add_edge_to_reporting = Mock()

        await service_outage_detector._process_edge_from_quarantine(edge_full_id)

        service_outage_detector._add_edge_to_reporting.assert_not_called()

    @pytest.mark.asyncio
    async def process_edge_from_quarantine_with_reportable_edge_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)
        service_outage_detector._is_reportable_edge = CoroutineMock(return_value=True)
        service_outage_detector._add_edge_to_reporting = Mock()

        await service_outage_detector._process_edge_from_quarantine(edge_full_id)

        service_outage_detector._add_edge_to_reporting.assert_called_once_with(edge_full_id, edge_status)

    @pytest.mark.asyncio
    async def process_edge_from_quarantine_with_exception_raised_while_determining_reportability_of_edge_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)
        service_outage_detector._is_reportable_edge = CoroutineMock(side_effect=ValueError)
        service_outage_detector._add_edge_to_reporting = Mock()

        await service_outage_detector._process_edge_from_quarantine(edge_full_id)

        service_outage_detector._add_edge_to_reporting.assert_not_called()

    @pytest.mark.asyncio
    async def is_reportable_edge_with_healthy_status_test(self):
        edge_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(return_value=False)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_outage_ticket_for_edge = CoroutineMock()

        result = await service_outage_detector._is_reportable_edge(edge_status)

        service_outage_detector._get_outage_ticket_for_edge.assert_not_awaited()
        assert result is False

    @pytest.mark.asyncio
    async def is_reportable_edge_with_faulty_status_and_outage_ticket_found_test(self):
        edge_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        outage_ticket = {
            'request_id': uuid(),
            'ticket_details': {
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
            },
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        outage_utils.is_there_an_outage = Mock(wraps=outage_utils.is_there_an_outage)
        service_outage_detector._get_outage_ticket_for_edge = CoroutineMock(return_value=outage_ticket)

        result = await service_outage_detector._is_reportable_edge(edge_status)

        # service_outage_detector._is_there_an_outage.assert_called_once_with(edge_status)
        service_outage_detector._get_outage_ticket_for_edge.assert_awaited_once_with(edge_status)
        assert result is False

    @pytest.mark.asyncio
    async def is_reportable_edge_with_faulty_status_and_outage_ticket_not_found_test(self):
        edge_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        outage_ticket = {
            'request_id': uuid(),
            'ticket_details': None,
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        outage_utils.is_there_an_outage = Mock(wraps=outage_utils.is_there_an_outage)
        service_outage_detector._get_outage_ticket_for_edge = CoroutineMock(return_value=outage_ticket)

        result = await service_outage_detector._is_reportable_edge(edge_status)

        # service_outage_detector._is_there_an_outage.assert_called_once_with(edge_status)
        service_outage_detector._get_outage_ticket_for_edge.assert_awaited_once_with(edge_status)
        assert result is True

    @pytest.mark.asyncio
    async def is_reportable_edge_with_faulty_status_and_unexpected_outage_ticket_format_test(self):
        edge_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
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
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_outage_ticket_for_edge = CoroutineMock(return_value=outage_ticket)

        with pytest.raises(ValueError):
            await service_outage_detector._is_reportable_edge(edge_status)

    @pytest.mark.asyncio
    async def get_outage_ticket_for_edge_test(self):
        client_id = 12345
        enterprise_name = f'EVIL-CORP|{client_id}|'
        edge_serial_number = 'VC1234567'
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE'}},
                {'linkId': 5678, 'link': {'state': 'STABLE'}},
            ],
            'enterprise_name': enterprise_name,
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
        template_renderer = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=outage_ticket)
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._extract_client_id = Mock(return_value=client_id)

        uuid_ = uuid()
        with patch.object(service_outage_detector_module, 'uuid', return_value=uuid_):
            outage_ticket_result = await service_outage_detector._get_outage_ticket_for_edge(edge_status)

        service_outage_detector._extract_client_id.assert_called_once_with(enterprise_name)
        event_bus.rpc_request.assert_awaited_once_with(
            'bruin.ticket.outage.details.by_edge_serial.request',
            {
                'request_id': uuid_,
                'edge_serial': edge_serial_number,
                'client_id': client_id,
            },
            timeout=180,
        )
        assert outage_ticket_result == outage_ticket

    def extract_client_id_with_match_found_test(self):
        client_id = 12345
        enterprise_name = f'EVIL-CORP|{client_id}|'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        result_client_id = service_outage_detector._extract_client_id(enterprise_name)
        assert result_client_id == client_id

    def extract_client_id_with_no_match_found_test(self):
        enterprise_name = f'EVIL-CORP'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        result_client_id = service_outage_detector._extract_client_id(enterprise_name)
        assert result_client_id == 9994

    def add_edge_to_reporting_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}
        client_id = 12345
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
        }

        addition_to_quarantine_timestamp = 123456789
        edge_status_in_quarantine = {
            'edge_status': {
                'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC7654321'},
                'links': [
                    {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                    {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
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
        template_renderer = Mock()

        quarantine_edge_repository = Mock()
        quarantine_edge_repository.get_edge = Mock(return_value=edge_status_in_quarantine)
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        service_outage_detector._add_edge_to_reporting(edge_full_id, edge_status)

        quarantine_edge_repository.get_edge.assert_called_once_with(edge_full_id)
        reporting_edge_repository.add_edge.assert_called_once_with(
            edge_full_id,
            {
                'edge_status': edge_status,
                'detection_timestamp': addition_to_quarantine_timestamp,
            },
            time_to_live=None,
        )
        quarantine_edge_repository.remove_edge.assert_called_once_with(edge_full_id)

    def add_edge_to_reporting_with_edge_missing_in_quarantine_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}
        client_id = 12345
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        quarantine_edge_repository = Mock()
        quarantine_edge_repository.get_edge = Mock(return_value=None)
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

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
            },
            time_to_live=None,
        )
        quarantine_edge_repository.remove_edge.assert_called_once_with(edge_full_id)


class TestServiceOutageReporterJob:
    @pytest.mark.asyncio
    async def start_service_outage_reporter_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

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
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        await service_outage_detector.start_service_outage_reporter_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            service_outage_detector._service_outage_reporter_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_reporter'],
            next_run_time=undefined,
            replace_existing=True,
            id='_service_outage_reporter_process',
        )

    @pytest.mark.asyncio
    async def service_outage_reporter_process_with_edges_to_report_test(self):
        edge_1_host = edge_2_host = 'mettel.velocloud.net'
        edge_1_enterprise_id = 1234
        edge_2_enterprise_id = 4321
        edge_1_id = 5678
        edge_2_id = 8765

        edge_1_identifier = EdgeIdentifier(host=edge_1_host, enterprise_id=edge_1_enterprise_id, edge_id=edge_1_id)
        edge_2_identifier = EdgeIdentifier(host=edge_2_host, enterprise_id=edge_2_enterprise_id, edge_id=edge_2_id)

        edge_1_detection_timestamp = 1234567890
        edge_2_detection_timestamp = 9876543210
        edge_1_serial_number = 'V123456789'
        edge_2_serial_number = 'V987654321'
        edge_1_enterprise_name = edge_2_enterprise_name = 'EVIL-CORP|12345|'

        edge_1_value = {
            'edge_status': {
                'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_1_serial_number},
                'links': [
                    {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                    {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                ],
                'enterprise_name': edge_1_enterprise_name,
            },
            'detection_timestamp': edge_1_detection_timestamp,
            'addition_timestamp': 11112222,
        }
        edge_2_value = {
            'edge_status': {
                'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial_number},
                'links': [
                    {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                    {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                ],
                'enterprise_name': edge_2_enterprise_name,
            },
            'detection_timestamp': edge_2_detection_timestamp,
            'addition_timestamp': 22223333,
        }

        edge_to_report_1 = {edge_1_identifier: edge_1_value}
        edge_to_report_2 = {edge_2_identifier: edge_2_value}
        edges_to_report = {**edge_to_report_1, **edge_to_report_2}

        edge_1_detection_datetime = datetime.fromtimestamp(edge_1_detection_timestamp)
        edge_2_detection_datetime = datetime.fromtimestamp(edge_2_detection_timestamp)
        edge_1_url = f'https://{edge_1_host}/#!/operator/customer/{edge_1_enterprise_id}/monitor/edge/{edge_1_id}/'
        edge_2_url = f'https://{edge_2_host}/#!/operator/customer/{edge_2_enterprise_id}/monitor/edge/{edge_2_id}/'
        unmarshalling_result = [
            {
                'detection_time': edge_1_detection_datetime,
                'serial_number': edge_1_serial_number,
                'enterprise': edge_1_enterprise_name,
                'links': edge_1_url,
            },
            {
                'detection_time': edge_2_detection_datetime,
                'serial_number': edge_2_serial_number,
                'enterprise': edge_2_enterprise_name,
                'links': edge_2_url,
            },
        ]

        email_object = {
            'request_id': uuid(),
            'email_data': {
                'subject': 'Serious outage report',
                'recipient': 'evil@corp.net',
                'html': '<div>Some important data</div>'
            }
        }

        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        reporting_edge_repository = Mock()
        reporting_edge_repository.get_all_edges = Mock(return_value=edges_to_report)

        template_renderer = Mock()
        template_renderer.compose_email_object = Mock(return_value=email_object)
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._refresh_reporting_queue = CoroutineMock()
        service_outage_detector._attach_outage_causes_to_edges = Mock()
        service_outage_detector._unmarshall_edge_to_report = Mock(side_effect=unmarshalling_result)

        await service_outage_detector._service_outage_reporter_process()

        # service_outage_detector._refresh_reporting_queue.assert_awaited_once()
        service_outage_detector._attach_outage_causes_to_edges.assert_called_once_with(edges_to_report)
        reporting_edge_repository.get_all_edges.assert_called_once()
        service_outage_detector._unmarshall_edge_to_report.assert_has_calls([
            call(edge_1_identifier, edge_1_value),
            call(edge_2_identifier, edge_2_value),
        ])
        template_renderer.compose_email_object.assert_called_once_with(
            unmarshalling_result,
            fields=["Date of detection", "Serial Number", "Company", "Edge URL", "Outage causes"],
            fields_edge=["detection_time", "serial_number", "enterprise", "edge_url", "outage_causes"],
        )
        event_bus.rpc_request.assert_awaited_once_with(
            "notification.email.request",
            email_object,
            timeout=10,
        )
        reporting_edge_repository.remove_all_stored_elements.assert_called_once()

    @pytest.mark.asyncio
    async def service_outage_reporter_process_with_no_edges_to_report_test(self):
        edges_to_report = {}

        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        reporting_edge_repository = Mock()
        reporting_edge_repository.get_all_edges = Mock(return_value=edges_to_report)
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._refresh_reporting_queue = CoroutineMock()
        service_outage_detector._attach_outage_causes_to_edges = Mock()
        service_outage_detector._unmarshall_edge_to_report = Mock()

        await service_outage_detector._service_outage_reporter_process()

        # service_outage_detector._refresh_reporting_queue.assert_awaited_once()
        service_outage_detector._attach_outage_causes_to_edges.assert_not_called()
        reporting_edge_repository.get_all_edges.assert_called_once()
        service_outage_detector._unmarshall_edge_to_report.assert_not_called()
        template_renderer.compose_email_object.assert_not_called()
        event_bus.rpc_request.assert_not_called()
        reporting_edge_repository.remove_all_stored_elements.assert_not_called()

    @pytest.mark.asyncio
    async def refresh_reporting_queue_test(self):
        edge_1_full_id = {'host': 'metvc04.mettel.net', 'enterprise_id': 12345, 'edge_id': 67890}
        edge_2_full_id = {'host': 'metvc04.mettel.net', 'enterprise_id': 54321, 'edge_id': 98765}
        edge_3_full_id = {'host': 'metvc04.mettel.net', 'enterprise_id': 11111, 'edge_id': 22222}
        edge_4_full_id = {'host': 'metvc04.mettel.net', 'enterprise_id': 33333, 'edge_id': 44444}

        edge_1_identifier = EdgeIdentifier(**edge_1_full_id)
        edge_2_identifier = EdgeIdentifier(**edge_2_full_id)
        edge_3_identifier = EdgeIdentifier(**edge_3_full_id)
        edge_4_identifier = EdgeIdentifier(**edge_4_full_id)

        edge_1_value = {
            'edge_status': {
                'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC123456789'},
                'links': [
                    {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                    {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                ],
                'enterprise_name': 'EVIL-CORP|12345|',
            },
            'detection_timestamp': 123456789,
            'addition_timestamp': 11112222,
        }
        edge_2_value = {
            'edge_status': {
                'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC987654321'},
                'links': [
                    {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                    {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                ],
                'enterprise_name': 'EVIL-CORP|12345|',
            },
            'detection_timestamp': 987654321,
            'addition_timestamp': 22223333,
        }
        edge_3_value = {
            'edge_status': {
                'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC111122223'},
                'links': [
                    {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                    {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                ],
                'enterprise_name': 'EVIL-CORP|12345|',
            },
            'detection_timestamp': 123459876,
            'addition_timestamp': 22223333,
        }
        edge_4_value = {
            'edge_status': {
                'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC111122223'},
                'links': [
                    {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                    {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                ],
                'enterprise_name': 'EVIL-CORP|12345|',
            },
            'detection_timestamp': 123459876,
            'addition_timestamp': 22223333,
        }

        edges_to_report = {
            edge_1_identifier: edge_1_value,
            edge_2_identifier: edge_2_value,
            edge_3_identifier: edge_3_value,
            edge_4_identifier: edge_4_value,
        }

        edge_1_new_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC123456789'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_2_new_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC987654321'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_3_new_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC111122223'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_4_new_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC111122223'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        edge_2_outage_ticket = {
            'request_id': uuid(),
            'ticket_details': None,
            'status': 500,
        }
        edge_3_outage_ticket = {
            'request_id': uuid(),
            'ticket_details': {
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
            },
            'status': 200,
        }
        edge_4_outage_ticket = None

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        quarantine_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(side_effect=[False, True, True, True])

        reporting_edge_repository = Mock()
        reporting_edge_repository.get_all_edges = Mock(return_value=edges_to_report)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(side_effect=[
            edge_1_new_status, edge_2_new_status, edge_3_new_status, edge_4_new_status
        ])
        service_outage_detector._get_outage_ticket_for_edge = CoroutineMock(side_effect=[
            edge_2_outage_ticket, edge_3_outage_ticket, edge_4_outage_ticket
        ])

        await service_outage_detector._refresh_reporting_queue()

        edge_2_new_value = {**edge_2_value, **{'edge_status': edge_2_new_status}}
        reporting_edge_repository.add_edge.assert_called_once_with(
            edge_2_full_id,
            edge_2_new_value,
            update_existing=True, time_to_live=None,
        )
        reporting_edge_repository.remove_edge.assert_has_calls([
            call(edge_1_full_id), call(edge_3_full_id)
        ])

    def attach_outage_causes_to_edges_test(self):
        edge_1_full_id = {'host': 'metvc04.mettel.net', 'enterprise_id': 12345, 'edge_id': 67890}
        edge_2_full_id = {'host': 'metvc04.mettel.net', 'enterprise_id': 54321, 'edge_id': 98765}
        edge_3_full_id = {'host': 'metvc04.mettel.net', 'enterprise_id': 11111, 'edge_id': 22222}

        edge_1_identifier = EdgeIdentifier(**edge_1_full_id)
        edge_2_identifier = EdgeIdentifier(**edge_2_full_id)
        edge_3_identifier = EdgeIdentifier(**edge_3_full_id)

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC123456789'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC987654321'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC111122223'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        edge_1_value = {
            'edge_status': edge_1_status,
            'detection_timestamp': 123456789,
            'addition_timestamp': 11112222,
        }
        edge_2_value = {
            'edge_status': edge_2_status,
            'detection_timestamp': 987654321,
            'addition_timestamp': 22223333,
        }
        edge_3_value = {
            'edge_status': edge_3_status,
            'detection_timestamp': 123459876,
            'addition_timestamp': 22223333,
        }

        edges_to_report = {
            edge_1_identifier: edge_1_value,
            edge_2_identifier: edge_2_value,
            edge_3_identifier: edge_3_value,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        is_faulty_edge_side_effect = [True, False, True]
        is_faulty_link_side_effect = [True, True, True, True, False, False]
        outage_utils = Mock()
        outage_utils.is_faulty_edge = Mock(side_effect=is_faulty_edge_side_effect)
        outage_utils.is_faulty_link = Mock(side_effect=is_faulty_link_side_effect)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        service_outage_detector._attach_outage_causes_to_edges(edges_to_report)

        assert edges_to_report[edge_1_identifier] == {
            **edge_1_value,
            'outage_causes': {'edge': 'OFFLINE', 'links': {'GE1': 'DISCONNECTED', 'GE2': 'DISCONNECTED'}}
        }
        assert edges_to_report[edge_2_identifier] == {
            **edge_2_value,
            'outage_causes': {'links': {'GE1': 'DISCONNECTED', 'GE2': 'DISCONNECTED'}}
        }
        assert edges_to_report[edge_3_identifier] == {
            **edge_3_value,
            'outage_causes': {'edge': 'OFFLINE'}
        }

    def generate_edge_url_test(self):
        host = 'metvco04.mettel.net'
        enterprise_id = 12345
        edge_id = 67890
        edge_full_id = {'host': host, 'enterprise_id': enterprise_id, 'edge_id': edge_id}

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        result_url = service_outage_detector._generate_edge_url(edge_full_id)

        expected_url = f'https://{host}/#!/operator/customer/{enterprise_id}/monitor/edge/{edge_id}/'
        assert result_url == expected_url

    def unmarshall_edge_to_report_test(self):
        host = 'metvco04.mettel.net'
        enterprise_id = 12345
        edge_id = 67890
        edge_identifier = EdgeIdentifier(host=host, enterprise_id=enterprise_id, edge_id=edge_id)

        detection_timestamp = 123456789
        edge_serial_number = 'V123456789'
        enterprise_name = 'EVIL-CORP|12345|'
        edge_1_value = {
            'edge_status': {
                'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial_number},
                'links': [
                    {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                    {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                ],
                'enterprise_name': enterprise_name,
            },
            'detection_timestamp': detection_timestamp,
            'addition_timestamp': 987654321,
            'outage_causes': {'edge': 'OFFLINE', 'links': {'GE1': 'DISCONNECTED', 'GE2': 'DISCONNECTED'}}
        }
        edge_2_value = {
            'edge_status': {
                'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial_number},
                'links': [
                    {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                    {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                ],
                'enterprise_name': enterprise_name,
            },
            'detection_timestamp': detection_timestamp,
            'addition_timestamp': 987654321,
            'outage_causes': {'links': {'GE2': 'DISCONNECTED'}}
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        tz = timezone(config.MONITOR_CONFIG['timezone'])
        expected_detection_time = datetime.fromtimestamp(detection_timestamp, tz=tz)
        expected_edge_url = f'https://{host}/#!/operator/customer/{enterprise_id}/monitor/edge/{edge_id}/'

        result = service_outage_detector._unmarshall_edge_to_report(edge_identifier, edge_1_value)
        expected = {
            'detection_time': expected_detection_time,
            'serial_number': edge_serial_number,
            'enterprise': enterprise_name,
            'edge_url': expected_edge_url,
            'outage_causes': [
                'Edge was OFFLINE',
                'Link GE1 was DISCONNECTED',
                'Link GE2 was DISCONNECTED',
            ]
        }
        assert result == expected

        result = service_outage_detector._unmarshall_edge_to_report(edge_identifier, edge_2_value)
        expected = {
            'detection_time': expected_detection_time,
            'serial_number': edge_serial_number,
            'enterprise': enterprise_name,
            'edge_url': expected_edge_url,
            'outage_causes': [
                'Link GE2 was DISCONNECTED',
            ]
        }
        assert result == expected


class TestServiceOutageMonitor:
    @pytest.mark.asyncio
    async def start_service_outage_monitoring_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(service_outage_detector_module, 'datetime', new=datetime_mock):
            with patch.object(service_outage_detector_module, 'timezone', new=Mock()):
                await service_outage_detector.start_service_outage_monitoring(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            service_outage_detector._outage_monitoring_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_service_outage_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_service_outage_monitoring_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        await service_outage_detector.start_service_outage_monitoring(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            service_outage_detector._outage_monitoring_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
            next_run_time=undefined,
            replace_existing=False,
            id='_service_outage_monitor_process',
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
        template_renderer = Mock()
        outage_utils = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        try:
            await service_outage_detector.start_service_outage_monitoring(exec_on_start=False)
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                service_outage_detector._outage_monitoring_process, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
                next_run_time=undefined,
                replace_existing=False,
                id='_service_outage_monitor_process',
            )

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_no_edges_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edges_for_monitoring = Mock(return_value=[])
        service_outage_detector._get_edge_status_by_id = CoroutineMock()

        await service_outage_detector._outage_monitoring_process()

        service_outage_detector._get_edges_for_monitoring.assert_called_once()
        service_outage_detector._get_edge_status_by_id.assert_not_awaited()
        outage_utils.is_there_an_outage.assert_not_called()
        scheduler.add_job.assert_not_called()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_edges_and_no_outages_detected_test(self):
        edge_1_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_2_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 5678}
        edge_3_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 9012}
        edges_for_monitoring = [edge_1_full_id, edge_2_full_id, edge_3_full_id]

        edge_1_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC7654321'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1122334'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edges_statuses = [edge_1_status, edge_2_status, edge_3_status]

        is_there_an_outage_side_effect = [
            False,   # Edge 1
            False,   # Edge 2
            False,   # Edge 3
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(side_effect=is_there_an_outage_side_effect)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edges_for_monitoring = Mock(return_value=edges_for_monitoring)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(side_effect=edges_statuses)

        await service_outage_detector._outage_monitoring_process()

        service_outage_detector._get_edges_for_monitoring.assert_called_once()
        service_outage_detector._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id), call(edge_2_full_id), call(edge_3_full_id)
        ])
        outage_utils.is_there_an_outage.assert_has_calls([
            call(edge_1_status), call(edge_2_status), call(edge_3_status)
        ])
        scheduler.add_job.assert_not_called()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_edges_and_some_outages_detected_and_recheck_job_not_scheduled_test(self):
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        is_there_an_outage = True

        event_bus = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(return_value=is_there_an_outage)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edges_for_monitoring = Mock(return_value=[edge_full_id])
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)

        try:
            await service_outage_detector._outage_monitoring_process()
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                service_outage_detector._recheck_edge_for_ticket_creation, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'],
                replace_existing=False,
                id=f'_ticket_creation_recheck_{json.dumps(edge_full_id)}',
                kwargs={'edge_full_id': edge_full_id}
            )

        service_outage_detector._get_edges_for_monitoring.assert_called_once()
        service_outage_detector._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_utils.is_there_an_outage.assert_called_once_with(edge_status)

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_edges_and_some_outages_detected_and_recheck_job_scheduled_test(self):
        edge_1_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_2_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 5678}
        edge_3_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 9012}
        edges_for_monitoring = [edge_1_full_id, edge_2_full_id, edge_3_full_id]

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC7654321'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1122334'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edges_statuses = [edge_1_status, edge_2_status, edge_3_status]

        is_there_an_outage_side_effect = [
            True,   # Edge 1
            False,  # Edge 2
            True,   # Edge 3
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(side_effect=is_there_an_outage_side_effect)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edges_for_monitoring = Mock(return_value=edges_for_monitoring)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(side_effect=edges_statuses)

        await service_outage_detector._outage_monitoring_process()

        service_outage_detector._get_edges_for_monitoring.assert_called_once()
        service_outage_detector._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id), call(edge_2_full_id), call(edge_3_full_id)
        ])
        outage_utils.is_there_an_outage.assert_has_calls([
            call(edge_1_status), call(edge_2_status), call(edge_3_status)
        ])
        scheduler.add_job.assert_has_calls([
            call(
                service_outage_detector._recheck_edge_for_ticket_creation, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'],
                replace_existing=False,
                id=f'_ticket_creation_recheck_{json.dumps(edge_1_full_id)}',
                kwargs={'edge_full_id': edge_1_full_id}
            ),
            call(
                service_outage_detector._recheck_edge_for_ticket_creation, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'],
                replace_existing=False,
                id=f'_ticket_creation_recheck_{json.dumps(edge_3_full_id)}',
                kwargs={'edge_full_id': edge_3_full_id}
            ),
        ])

    def get_edges_for_monitoring_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        edges = service_outage_detector._get_edges_for_monitoring()

        expected = list(config.MONITORING_EDGES.values())
        assert edges == expected

    @pytest.mark.asyncio
    async def recheck_edge_for_ticket_creation_with_no_outage_detected_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        outage_happened = False

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(return_value=outage_happened)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)
        service_outage_detector._create_outage_ticket = CoroutineMock()

        await service_outage_detector._recheck_edge_for_ticket_creation(edge_full_id)

        service_outage_detector._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_utils.is_there_an_outage.assert_called_once_with(edge_status)
        service_outage_detector._create_outage_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edge_for_ticket_creation_with_outage_detected_and_no_production_environment_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        outage_happened = True

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        template_renderer = Mock()

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)
        service_outage_detector._create_outage_ticket = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_outage_detector._recheck_edge_for_ticket_creation(edge_full_id)

        service_outage_detector._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_utils.is_there_an_outage.assert_called_once_with(edge_status)
        service_outage_detector._create_outage_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edge_for_ticket_creation_with_outage_detected_and_production_env_and_no_existing_ticket_test(
            self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        outage_happened = True

        outage_ticket = {
            'request_id': uuid(),
            'ticket_details': None,
            'status': 500,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        template_renderer = Mock()

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)
        service_outage_detector._get_outage_ticket_for_edge = CoroutineMock(return_value=outage_ticket)
        service_outage_detector._create_outage_ticket = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_outage_detector._recheck_edge_for_ticket_creation(edge_full_id)

        service_outage_detector._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_utils.is_there_an_outage.assert_called_once_with(edge_status)
        service_outage_detector._get_outage_ticket_for_edge.assert_awaited_once_with(edge_status)
        service_outage_detector._create_outage_ticket.assert_awaited_once_with(edge_full_id, edge_status)

    @pytest.mark.asyncio
    async def recheck_edge_for_ticket_creation_with_outage_detected_and_production_env_and_existing_ticket_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        outage_happened = True

        outage_ticket = {
            'request_id': uuid(),
            'ticket_details': {
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
            },
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        template_renderer = Mock()

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)
        service_outage_detector._get_outage_ticket_for_edge = CoroutineMock(return_value=outage_ticket)
        service_outage_detector._create_outage_ticket = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_outage_detector._recheck_edge_for_ticket_creation(edge_full_id)

        service_outage_detector._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_utils.is_there_an_outage.assert_called_once_with(edge_status)
        service_outage_detector._get_outage_ticket_for_edge.assert_awaited_once_with(edge_status)
        service_outage_detector._create_outage_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def create_outage_ticket_with_failing_creation_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        serial_number = 'VC1234567'
        bruin_client_id = 12345
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_id}|',
        }

        uuid_ = uuid()

        ticket_creation_details = {
            "request_id": uuid_,
            "clientId": bruin_client_id,
            "category": "VOO",
            "services": [
                {"serviceNumber": serial_number}
            ],
            "contacts": [
                {
                    "email": "some@contact.com",
                    "phone": "123-456-7890",
                    "name": "Saturos",
                    "type": "site"
                },
            ]
        }

        post_ticket_result = {
            'request_id': uuid_,
            'ticketIds': None,
            'status': 500,
        }

        slack_message_post_result = None

        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[post_ticket_result, slack_message_post_result])

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._generate_outage_ticket = Mock(return_value=ticket_creation_details)

        with patch.object(service_outage_detector_module, 'uuid', return_value=uuid_):
            await service_outage_detector._create_outage_ticket(edge_full_id, edge_status)

        service_outage_detector._generate_outage_ticket.assert_called_once_with(edge_status)
        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.creation.request",
            ticket_creation_details,
            timeout=30
        )
        logger.error.assert_called()

    @pytest.mark.asyncio
    async def create_outage_ticket_with_successful_creation_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_identifier = EdgeIdentifier(**edge_full_id)

        serial_number = 'VC1234567'
        bruin_client_id = 12345
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_id}|',
        }

        uuid_ = uuid()

        ticket_creation_details = {
            "request_id": uuid_,
            "clientId": bruin_client_id,
            "category": "VOO",
            "services": [
                {"serviceNumber": serial_number}
            ],
            "contacts": [
                {
                    "email": "some@contact.com",
                    "phone": "123-456-7890",
                    "name": "Saturos",
                    "type": "site"
                },
            ]
        }

        ticket_id = 54321
        post_ticket_result = {
            'request_id': uuid_,
            'ticketIds': {
                'ticketIds': [ticket_id]
            },
            'status': 200,
        }

        slack_message_post_result = None

        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[post_ticket_result, slack_message_post_result])

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._generate_outage_ticket = Mock(return_value=ticket_creation_details)

        with patch.object(service_outage_detector_module, 'uuid', return_value=uuid_):
            await service_outage_detector._create_outage_ticket(edge_full_id, edge_status)

        service_outage_detector._generate_outage_ticket.assert_called_once_with(edge_status)
        event_bus.rpc_request.assert_has_awaits([
            call(
                "bruin.ticket.creation.request",
                ticket_creation_details,
                timeout=30
            ),
            call(
                "notification.slack.request",
                {
                    'request_id': uuid_,
                    'message': (
                        f'Outage ticket created for faulty edge {edge_identifier}. Ticket details at '
                        f'https://app.bruin.com/helpdesk?clientId={bruin_client_id}&ticketId={ticket_id}.')
                },
                timeout=10
            )
        ])

    @pytest.mark.asyncio
    async def generate_outage_ticket_test(self):
        bruin_client_id = 12345
        serial_number = 'VC1234567'
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_id}|',
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        outage_ticket_data = service_outage_detector._generate_outage_ticket(edge_status)

        assert outage_ticket_data == {
            "clientId": bruin_client_id,
            "category": "VOO",
            "services": [
                {"serviceNumber": serial_number}
            ],
            "contacts": config.OUTAGE_CONTACTS
        }


class TestServiceOutageMonitor:
    @pytest.mark.asyncio
    async def start_service_outage_monitoring_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(service_outage_detector_module, 'datetime', new=datetime_mock):
            with patch.object(service_outage_detector_module, 'timezone', new=Mock()):
                await service_outage_detector.start_service_outage_monitoring(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            service_outage_detector._outage_monitoring_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_service_outage_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_service_outage_monitoring_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        await service_outage_detector.start_service_outage_monitoring(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            service_outage_detector._outage_monitoring_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
            next_run_time=undefined,
            replace_existing=False,
            id='_service_outage_monitor_process',
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
        template_renderer = Mock()
        outage_utils = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        try:
            await service_outage_detector.start_service_outage_monitoring(exec_on_start=False)
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                service_outage_detector._outage_monitoring_process, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
                next_run_time=undefined,
                replace_existing=False,
                id='_service_outage_monitor_process',
            )

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_no_edges_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edges_for_monitoring = Mock(return_value=[])
        service_outage_detector._get_edge_status_by_id = CoroutineMock()

        await service_outage_detector._outage_monitoring_process()

        service_outage_detector._get_edges_for_monitoring.assert_called_once()
        service_outage_detector._get_edge_status_by_id.assert_not_awaited()
        outage_utils.is_there_an_outage.assert_not_called()
        scheduler.add_job.assert_not_called()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_edges_and_no_outages_detected_test(self):
        edge_1_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_2_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 5678}
        edge_3_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 9012}
        edges_for_monitoring = [edge_1_full_id, edge_2_full_id, edge_3_full_id]

        edge_1_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC7654321'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1122334'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edges_statuses = [edge_1_status, edge_2_status, edge_3_status]

        is_there_an_outage_side_effect = [
            False,   # Edge 1
            False,   # Edge 2
            False,   # Edge 3
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(side_effect=is_there_an_outage_side_effect)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edges_for_monitoring = Mock(return_value=edges_for_monitoring)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(side_effect=edges_statuses)

        await service_outage_detector._outage_monitoring_process()

        service_outage_detector._get_edges_for_monitoring.assert_called_once()
        service_outage_detector._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id), call(edge_2_full_id), call(edge_3_full_id)
        ])
        outage_utils.is_there_an_outage.assert_has_calls([
            call(edge_1_status), call(edge_2_status), call(edge_3_status)
        ])
        scheduler.add_job.assert_not_called()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_edges_and_some_outages_detected_and_recheck_job_not_scheduled_test(self):
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        is_there_an_outage = True

        event_bus = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(return_value=is_there_an_outage)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edges_for_monitoring = Mock(return_value=[edge_full_id])
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)

        try:
            await service_outage_detector._outage_monitoring_process()
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                service_outage_detector._recheck_edge_for_ticket_creation, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'],
                replace_existing=False,
                id=f'_ticket_creation_recheck_{json.dumps(edge_full_id)}',
                kwargs={'edge_full_id': edge_full_id}
            )

        service_outage_detector._get_edges_for_monitoring.assert_called_once()
        service_outage_detector._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_utils.is_there_an_outage.assert_called_once_with(edge_status)

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_edges_and_some_outages_detected_and_recheck_job_scheduled_test(self):
        edge_1_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_2_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 5678}
        edge_3_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 9012}
        edges_for_monitoring = [edge_1_full_id, edge_2_full_id, edge_3_full_id]

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC7654321'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1122334'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edges_statuses = [edge_1_status, edge_2_status, edge_3_status]

        is_there_an_outage_side_effect = [
            True,   # Edge 1
            False,  # Edge 2
            True,   # Edge 3
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(side_effect=is_there_an_outage_side_effect)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edges_for_monitoring = Mock(return_value=edges_for_monitoring)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(side_effect=edges_statuses)

        await service_outage_detector._outage_monitoring_process()

        service_outage_detector._get_edges_for_monitoring.assert_called_once()
        service_outage_detector._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id), call(edge_2_full_id), call(edge_3_full_id)
        ])
        outage_utils.is_there_an_outage.assert_has_calls([
            call(edge_1_status), call(edge_2_status), call(edge_3_status)
        ])
        scheduler.add_job.assert_has_calls([
            call(
                service_outage_detector._recheck_edge_for_ticket_creation, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'],
                replace_existing=False,
                id=f'_ticket_creation_recheck_{json.dumps(edge_1_full_id)}',
                kwargs={'edge_full_id': edge_1_full_id}
            ),
            call(
                service_outage_detector._recheck_edge_for_ticket_creation, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'],
                replace_existing=False,
                id=f'_ticket_creation_recheck_{json.dumps(edge_3_full_id)}',
                kwargs={'edge_full_id': edge_3_full_id}
            ),
        ])

    def get_edges_for_monitoring_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        edges = service_outage_detector._get_edges_for_monitoring()

        expected = list(config.MONITORING_EDGES.values())
        assert edges == expected

    @pytest.mark.asyncio
    async def recheck_edge_for_ticket_creation_with_no_outage_detected_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        outage_happened = False

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(return_value=outage_happened)

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)
        service_outage_detector._create_outage_ticket = CoroutineMock()

        await service_outage_detector._recheck_edge_for_ticket_creation(edge_full_id)

        service_outage_detector._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_utils.is_there_an_outage.assert_called_once_with(edge_status)
        service_outage_detector._create_outage_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edge_for_ticket_creation_with_outage_detected_and_no_production_environment_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        outage_happened = True

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        template_renderer = Mock()

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)
        service_outage_detector._create_outage_ticket = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_outage_detector._recheck_edge_for_ticket_creation(edge_full_id)

        service_outage_detector._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_utils.is_there_an_outage.assert_called_once_with(edge_status)
        service_outage_detector._create_outage_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edge_for_ticket_creation_with_outage_detected_and_production_env_and_no_existing_ticket_test(
            self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        outage_happened = True

        outage_ticket = {
            'request_id': uuid(),
            'ticket_details': None,
            'status': 500,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        template_renderer = Mock()

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)
        service_outage_detector._get_outage_ticket_for_edge = CoroutineMock(return_value=outage_ticket)
        service_outage_detector._create_outage_ticket = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_outage_detector._recheck_edge_for_ticket_creation(edge_full_id)

        # service_outage_detector._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        # outage_utils.is_there_an_outage.assert_called_once_with(edge_status)
        # service_outage_detector._get_outage_ticket_for_edge.assert_awaited_once_with(
        # edge_status, ticket_statuses=None)
        # service_outage_detector._create_outage_ticket.assert_awaited_once_with(edge_full_id, edge_status)

    @pytest.mark.asyncio
    async def recheck_edge_for_ticket_creation_with_outage_detected_and_production_env_and_existing_ticket_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        outage_happened = True

        outage_ticket = {
            'request_id': uuid(),
            'ticket_details': {
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
            },
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        template_renderer = Mock()

        outage_utils = Mock()
        outage_utils.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._get_edge_status_by_id = CoroutineMock(return_value=edge_status)
        service_outage_detector._get_outage_ticket_for_edge = CoroutineMock(return_value=outage_ticket)
        service_outage_detector._create_outage_ticket = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_outage_detector._recheck_edge_for_ticket_creation(edge_full_id)

        service_outage_detector._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_utils.is_there_an_outage.assert_called_once_with(edge_status)
        service_outage_detector._get_outage_ticket_for_edge.assert_awaited_once_with(edge_status, ticket_statuses=None)
        service_outage_detector._create_outage_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def create_outage_ticket_with_failing_creation_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        serial_number = 'VC1234567'
        bruin_client_id = 12345
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_id}|',
        }

        uuid_ = uuid()

        ticket_creation_details = {
            "request_id": uuid_,
            "clientId": bruin_client_id,
            "category": "VOO",
            "services": [
                {"serviceNumber": serial_number}
            ],
            "contacts": [
                {
                    "email": "some@contact.com",
                    "phone": "123-456-7890",
                    "name": "Saturos",
                    "type": "site"
                },
            ]
        }

        post_ticket_result = {
            'request_id': uuid_,
            'ticketIds': None,
            'status': 500,
        }

        slack_message_post_result = None

        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[post_ticket_result, slack_message_post_result])

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._generate_outage_ticket = Mock(return_value=ticket_creation_details)

        with patch.object(service_outage_detector_module, 'uuid', return_value=uuid_):
            await service_outage_detector._create_outage_ticket(edge_full_id, edge_status)

        service_outage_detector._generate_outage_ticket.assert_called_once_with(edge_status)
        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.creation.request",
            ticket_creation_details,
            timeout=30
        )
        logger.error.assert_called()

    @pytest.mark.asyncio
    async def create_outage_ticket_with_successful_creation_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_identifier = EdgeIdentifier(**edge_full_id)

        serial_number = 'VC1234567'
        bruin_client_id = 12345
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_id}|',
        }

        uuid_ = uuid()

        ticket_creation_details = {
            "request_id": uuid_,
            "clientId": bruin_client_id,
            "category": "VOO",
            "services": [
                {"serviceNumber": serial_number}
            ],
            "contacts": [
                {
                    "email": "some@contact.com",
                    "phone": "123-456-7890",
                    "name": "Saturos",
                    "type": "site"
                },
            ]
        }

        ticket_id = 54321
        post_ticket_result = {
            'request_id': uuid_,
            'ticketIds': {
                'ticketIds': [ticket_id]
            },
            'status': 200,
        }

        slack_message_post_result = None

        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[post_ticket_result, slack_message_post_result])

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)
        service_outage_detector._generate_outage_ticket = Mock(return_value=ticket_creation_details)

        with patch.object(service_outage_detector_module, 'uuid', return_value=uuid_):
            await service_outage_detector._create_outage_ticket(edge_full_id, edge_status)

        service_outage_detector._generate_outage_ticket.assert_called_once_with(edge_status)
        event_bus.rpc_request.assert_has_awaits([
            call(
                "bruin.ticket.creation.request",
                ticket_creation_details,
                timeout=30
            ),
            call(
                "notification.slack.request",
                {
                    'request_id': uuid_,
                    'message': (
                        f'Outage ticket created for faulty edge {edge_identifier}. Ticket details at '
                        f'https://app.bruin.com/helpdesk?clientId={bruin_client_id}&ticketId={ticket_id}.')
                },
                timeout=10
            )
        ])

    @pytest.mark.asyncio
    async def generate_outage_ticket_test(self):
        bruin_client_id = 12345
        serial_number = 'VC1234567'
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_id}|',
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_utils = Mock()

        service_outage_detector = ServiceOutageDetector(event_bus, logger, scheduler,
                                                        quarantine_edge_repository, reporting_edge_repository,
                                                        config, template_renderer, outage_utils)

        outage_ticket_data = service_outage_detector._generate_outage_ticket(edge_status)

        assert outage_ticket_data == {
            "clientId": bruin_client_id,
            "category": "VOO",
            "services": [
                {"serviceNumber": serial_number}
            ],
            "contacts": config.OUTAGE_CONTACTS
        }
