import json

from datetime import datetime
from datetime import timedelta
from unittest.mock import call
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from asynctest import CoroutineMock
from igz.packages.repositories.edge_repository import EdgeIdentifier
from pytz import timezone
from shortuuid import uuid

from application.actions import comparison_report as comparison_report_module
from application.actions.comparison_report import ComparisonReport
from config import testconfig


class TestComparisonReport:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = Mock()
        template_renderer = Mock()
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        assert comparison_report._event_bus is event_bus
        assert comparison_report._logger is logger
        assert comparison_report._scheduler is scheduler
        assert comparison_report._quarantine_edge_repository is quarantine_edge_repository
        assert comparison_report._reporting_edge_repository is reporting_edge_repository
        assert comparison_report._config is config
        assert comparison_report._outage_repository is outage_repository

    @pytest.mark.asyncio
    async def report_persisted_edges_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report.start_service_outage_reporter_job = CoroutineMock()

        await comparison_report.report_persisted_edges()

        comparison_report.start_service_outage_reporter_job.assert_awaited_once_with(exec_on_start=True)

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
                    'edges': {
                        'edgeState': 'OFFLINE',
                        'serialNumber': 'VC1234567',
                        'name': 'Saturos',
                        'lastContact': '2020-01-16T14:59:56.245Z'
                    },
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
                    'edges': {
                        'edgeState': 'CONNECTED',
                        'serialNumber': 'VC7654321',
                        'name': 'Menardi',
                        'lastContact': '2020-01-16T14:59:56.245Z'
                    },
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
        outage_repository = Mock()

        quarantine_edge_repository = Mock()
        quarantine_edge_repository.get_all_edges = Mock(return_value=quarantine_edges)

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._start_quarantine_job = CoroutineMock()

        await comparison_report.load_persisted_quarantine()

        quarantine_edge_repository.get_all_edges.assert_called_once()

        quarantine_time = config.MONITOR_CONFIG['jobs_intervals']['quarantine']
        comparison_report._start_quarantine_job.assert_has_awaits([
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
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(comparison_report_module, 'datetime', new=datetime_mock):
            with patch.object(comparison_report_module, 'timezone', new=Mock()):
                await comparison_report.start_service_outage_detector_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            comparison_report._service_outage_detector_process, 'interval',
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
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        await comparison_report.start_service_outage_detector_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            comparison_report._service_outage_detector_process, 'interval',
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
        outage_repository = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        try:
            await comparison_report.start_service_outage_detector_job()
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                comparison_report._service_outage_detector_process, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_detector'],
                next_run_time=undefined,
                replace_existing=False,
                id='_service_outage_detector_process',
            )

    @pytest.mark.asyncio
    async def comparison_report_process_with_no_edges_found_test(self):
        edge_list = []

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_all_edges = CoroutineMock(return_value=edge_list)

        await comparison_report._service_outage_detector_process()

        comparison_report._get_all_edges.assert_awaited_once()

    @pytest.mark.asyncio
    async def comparison_report_process_with_edge_having_null_serial_test(self):
        edge_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_list = [edge_full_id]

        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': None},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|12345|',
        }
        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': edge_status_data,
            },
            'status': 200,
        }

        logger = Mock()
        event_bus = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_all_edges = CoroutineMock(return_value=edge_list)
        comparison_report._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        comparison_report._get_management_status = CoroutineMock()

        await comparison_report._service_outage_detector_process()

        comparison_report._get_all_edges.assert_awaited_once()
        comparison_report._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        comparison_report._get_management_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def comparison_report_process_with_retrieval_of_bruin_client_info_returning_non_2XX_status_test(self):
        uuid_ = uuid()

        edge_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_list = [edge_full_id]

        serial_number = 'VC1234567'
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|12345|',
        }
        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': edge_status_data,
            },
            'status': 200,
        }

        bruin_client_info_response_body = 'Got internal error from Bruin'
        bruin_client_info_response_status = 500
        bruin_client_info_response = {
            'body': bruin_client_info_response_body,
            'status': bruin_client_info_response_status,
        }

        message = (
            f'[outage-report] Error trying to get Bruin client info from Bruin for serial '
            f'{serial_number}: Error {bruin_client_info_response_status} - '
            f'{bruin_client_info_response_body}'
        )
        slack_message = {
            'request_id': uuid_,
            'message': message,
        }

        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_all_edges = CoroutineMock(return_value=edge_list)
        comparison_report._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        comparison_report._get_bruin_client_info_by_serial = CoroutineMock(return_value=bruin_client_info_response)
        comparison_report._get_management_status = CoroutineMock()

        with patch.object(comparison_report_module, 'uuid', return_value=uuid_):
            await comparison_report._service_outage_detector_process()

        comparison_report._get_all_edges.assert_awaited_once()
        comparison_report._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        event_bus.rpc_request.assert_awaited_once_with("notification.slack.request", slack_message, timeout=10)
        comparison_report._get_management_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def comparison_report_process_with_bruin_client_info_having_null_client_id_test(self):
        edge_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_list = [edge_full_id]

        serial_number = 'VC1234567'
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|12345|',
        }
        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': edge_status_data,
            },
            'status': 200,
        }

        bruin_client_info_response = {
            'body': {
                'client_id': None,
                'client_name': None,
            },
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_all_edges = CoroutineMock(return_value=edge_list)
        comparison_report._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        comparison_report._get_bruin_client_info_by_serial = CoroutineMock(return_value=bruin_client_info_response)
        comparison_report._get_management_status = CoroutineMock()

        await comparison_report._service_outage_detector_process()

        comparison_report._get_all_edges.assert_awaited_once()
        comparison_report._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        comparison_report._get_management_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def comparison_report_process_with_retrieval_of_management_status_returning_non_2XX_status_test(self):
        edge_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_identifier = EdgeIdentifier(**edge_full_id)
        edge_list = [edge_full_id]

        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|12345|',
        }
        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': edge_status_data,
            },
            'status': 200,
        }

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_response = {
            'body': bruin_client_info_response_body,
            'status': 200,
        }

        edge_status_data_with_bruin_info = {
            **edge_status_data,
            'bruin_client_info': bruin_client_info_response_body,
        }

        management_status_response_body = "Got internal error from Bruin"
        management_status_response_status = 500
        management_status_response = {
            "body": management_status_response_body,
            "status": management_status_response_status,
        }

        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        uuid_ = uuid()

        message = (
            f'[outage-report] Error trying to get management status from Bruin for edge '
            f'{edge_identifier}: Error {management_status_response_status} - '
            f'{management_status_response_body}'
        )
        slack_message = {'request_id': uuid_,
                         'message': message}

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_all_edges = CoroutineMock(return_value=edge_list)
        comparison_report._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        comparison_report._get_bruin_client_info_by_serial = CoroutineMock(return_value=bruin_client_info_response)
        comparison_report._get_management_status = CoroutineMock(return_value=management_status_response)

        with patch.object(comparison_report_module, 'uuid', return_value=uuid_):
            await comparison_report._service_outage_detector_process()

        comparison_report._get_all_edges.assert_awaited_once()
        comparison_report._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        comparison_report._get_management_status.assert_awaited_once_with(edge_status_data_with_bruin_info)
        event_bus.rpc_request.assert_awaited_with("notification.slack.request", slack_message, timeout=30)
        outage_repository.is_there_an_outage.assert_not_called()

    @pytest.mark.asyncio
    async def comparison_report_process_with_management_status_inactive_test(self):
        edge_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_list = [edge_full_id]

        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|12345|',
        }
        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': edge_status_data,
            },
            'status': 200,
        }

        bruin_client_info_response = {
            'body': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            },
            'status': 200,
        }

        management_status_response = {
            "body": "Fake status",
            "status": 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=False)

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_all_edges = CoroutineMock(return_value=edge_list)
        comparison_report._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        comparison_report._get_bruin_client_info_by_serial = CoroutineMock(return_value=bruin_client_info_response)
        comparison_report._get_management_status = CoroutineMock(return_value=management_status_response)
        comparison_report._is_management_status_active = Mock(return_value=False)
        comparison_report._start_quarantine_job = CoroutineMock()

        await comparison_report._service_outage_detector_process()

        comparison_report._get_all_edges.assert_awaited_once()
        comparison_report._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_not_called()
        comparison_report._start_quarantine_job.assert_not_awaited()

    @pytest.mark.asyncio
    async def comparison_report_process_with_edges_found_and_healthy_edges_test(self):
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
            'edges': {
                'edgeState': edge_1_state,
                'serialNumber': 'VC1234567',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': edge_1_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_1_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': edge_1_enterprise_name,
        }
        edge_1_status_response = {
            'body': {
                'edge_id': edge_1_full_id,
                'edge_info': edge_1_status,
            },
            'status': 200,
        }

        edge_2_state = 'CONNECTED'
        edge_2_link_ge1_state = edge_2_link_ge2_state = 'STABLE'
        edge_2_status = {
            'edges': {
                'edgeState': edge_2_state,
                'serialNumber': 'VC7654321',
                'name': 'Menardi',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': edge_2_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_2_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': edge_2_enterprise_name,
        }
        edge_2_status_response = {
            'body': {
                'edge_id': edge_2_full_id,
                'edge_info': edge_2_status,
            },
            'status': 200,
        }

        edge_3_state = 'CONNECTED'
        edge_3_link_ge1_state = edge_3_link_ge2_state = 'STABLE'
        edge_3_status = {
            'edges': {
                'edgeState': edge_3_state,
                'serialNumber': 'VC1112223',
                'name': 'Isaac',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': edge_3_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_3_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': edge_3_enterprise_name,
        }
        edge_3_status_response = {
            'body': {
                'edge_id': edge_3_full_id,
                'edge_info': edge_3_status,
            },
            'status': 200,
        }
        edge_status_responses = [edge_1_status_response, edge_2_status_response, edge_3_status_response]

        bruin_client_info_response = {
            'body': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            },
            'status': 200,
        }

        management_status_response = {
            "body": "Active – Gold Monitoring",
            "status": 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=False)

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_all_edges = CoroutineMock(return_value=edge_list)
        comparison_report._get_edge_status_by_id = CoroutineMock(side_effect=edge_status_responses)
        comparison_report._get_bruin_client_info_by_serial = CoroutineMock(return_value=bruin_client_info_response)
        comparison_report._get_management_status = CoroutineMock(return_value=management_status_response)
        comparison_report._is_management_status_active = CoroutineMock(return_value=True)
        comparison_report._start_quarantine_job = CoroutineMock()
        comparison_report._add_edge_to_quarantine = Mock()

        await comparison_report._service_outage_detector_process()

        comparison_report._get_all_edges.assert_awaited_once()
        comparison_report._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id), call(edge_2_full_id), call(edge_3_full_id)
        ])
        comparison_report._start_quarantine_job.assert_not_awaited()
        comparison_report._add_edge_to_quarantine.assert_not_called()

    @pytest.mark.asyncio
    async def comparison_report_process_with_edges_found_and_edges_with_outages_test(self):
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
            'edges': {
                'edgeState': edge_1_state,
                'serialNumber': 'VC1234567',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': edge_1_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_1_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': edge_1_enterprise_name,
        }
        edge_1_status_response = {
            'body': {
                'edge_id': edge_1_full_id,
                'edge_info': edge_1_status,
            },
            'status': 200,
        }

        edge_2_state = 'CONNECTED'
        edge_2_link_ge1_state = edge_2_link_ge2_state = 'STABLE'
        edge_2_status = {
            'edges': {
                'edgeState': edge_2_state,
                'serialNumber': 'VC7654321',
                'name': 'Menardi',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': edge_2_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_2_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': edge_2_enterprise_name,
        }
        edge_2_status_response = {
            'body': {
                'edge_id': edge_2_full_id,
                'edge_info': edge_2_status,
            },
            'status': 200,
        }

        edge_3_state = 'OFFLINE'
        edge_3_link_ge1_state = 'STABLE'
        edge_3_link_ge2_state = 'DISCONNECTED'
        edge_3_status = {
            'edges': {
                'edgeState': edge_3_state,
                'serialNumber': 'VC1112223',
                'name': 'Isaac',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': edge_3_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_3_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': edge_3_enterprise_name,
        }
        edge_3_status_response = {
            'body': {
                'edge_id': edge_3_full_id,
                'edge_info': edge_3_status,
            },
            'status': 200,
        }
        edge_status_responses = [edge_1_status_response, edge_2_status_response, edge_3_status_response]

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_response = {
            'body': bruin_client_info_response_body,
            'status': 200,
        }

        management_status_response = {
            "body": "Active – Gold Monitoring",
            "status": 200,
        }

        edge_1_status_with_bruin_client_info = {
            **edge_1_status,
            'bruin_client_info': bruin_client_info_response_body,
        }
        edge_3_status_with_bruin_client_info = {
            **edge_3_status,
            'bruin_client_info': bruin_client_info_response_body,
        }

        is_there_outage_side_effect = [True, False, True]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(side_effect=is_there_outage_side_effect)

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_all_edges = CoroutineMock(return_value=edge_list)
        comparison_report._get_edge_status_by_id = CoroutineMock(side_effect=edge_status_responses)
        comparison_report._get_bruin_client_info_by_serial = CoroutineMock(return_value=bruin_client_info_response)
        comparison_report._get_management_status = CoroutineMock(return_value=management_status_response)
        comparison_report._is_management_status_active = CoroutineMock(return_value=True)
        comparison_report._start_quarantine_job = CoroutineMock()
        comparison_report._add_edge_to_quarantine = Mock()

        await comparison_report._service_outage_detector_process()

        comparison_report._get_all_edges.assert_awaited_once()
        comparison_report._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id), call(edge_2_full_id), call(edge_3_full_id)
        ])
        comparison_report._start_quarantine_job.assert_has_awaits([
            call(edge_1_full_id, bruin_client_info_response_body),
            call(edge_3_full_id, bruin_client_info_response_body),
        ])
        comparison_report._add_edge_to_quarantine.assert_has_calls([
            call(edge_1_full_id, edge_1_status_with_bruin_client_info),
            call(edge_3_full_id, edge_3_status_with_bruin_client_info),
        ])

    @pytest.mark.asyncio
    async def comparison_report_process_throws_exception_test(self):
        edge_id = 5678
        edge_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': edge_id}
        edge_list = [edge_full_id] * 3

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_all_edges = CoroutineMock(return_value=edge_list)
        comparison_report._start_quarantine_job = CoroutineMock()
        comparison_report._get_edge_status_by_id = CoroutineMock(side_effect=ValueError)
        await comparison_report._service_outage_detector_process()
        outage_repository.is_there_an_outage.assert_not_called()

        comparison_report._get_edge_status_by_id = CoroutineMock(side_effect=Exception)
        comparison_report._is_management_status_active = CoroutineMock()
        await comparison_report._service_outage_detector_process()

        logger.exception.assert_called()

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
            'body': edge_list,
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
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        with patch.object(comparison_report_module, 'uuid', return_value=uuid_):
            result = await comparison_report._get_all_edges()

        event_bus.rpc_request.assert_awaited_once_with(
            'edge.list.request',
            {'request_id': uuid_, 'body': {'filter': {}}},
            timeout=600,
        )
        assert result == edge_list

    @pytest.mark.asyncio
    async def get_edge_status_by_id_test(self):
        uuid_ = uuid()
        edge_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_status = {
            'edges': {
                'edgeState': 'CONNECTED',
                'serialNumber': 'VC1234567',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_data = {
            'edge_id': edge_full_id,
            'edge_info': edge_status,
        }
        edge_status_response = {
            'request_id': uuid_,
            'body': edge_data,
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
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        with patch.object(comparison_report_module, 'uuid', return_value=uuid_):
            result = await comparison_report._get_edge_status_by_id(edge_full_id)

        event_bus.rpc_request.assert_awaited_once_with(
            'edge.status.request',
            {'request_id': uuid_, 'body': edge_full_id},
            timeout=120,
        )
        assert result == edge_status_response

    def add_edge_to_quarantine_test(self):
        edge_full_id = {'host': 'mettel.velocloud.net', 'enterprise_id': 1234, 'edge_id': 5678}
        edge_status = {
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': 'VC1234567',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
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
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        comparison_report._add_edge_to_quarantine(edge_full_id, edge_status)

        quarantine_edge_repository.add_edge.assert_called_once_with(
            edge_full_id, {'edge_status': edge_status},
            update_existing=False,
            time_to_live=config.MONITOR_CONFIG['quarantine_key_ttl'],
        )

    def get_outage_causes_test(self):
        edge_1_state = 'CONNECTED'
        edge_1_link_ge1_state = edge_1_link_ge2_state = 'STABLE'
        edge_status_1 = {
            'edges': {
                'edgeState': edge_1_state,
                'serialNumber': 'VC1234567',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': edge_1_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_1_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        edge_2_state = 'OFFLINE'
        edge_2_link_ge1_state = edge_2_link_ge2_state = 'DISCONNECTED'
        edge_status_2 = {
            'edges': {
                'edgeState': edge_2_state,
                'serialNumber': 'VC7654321',
                'name': 'Menardi',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
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
            'edges': {
                'edgeState': edge_3_state,
                'serialNumber': 'VC1112223',
                'name': 'Isaac',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
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

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(side_effect=[False, True, True])
        outage_repository.is_faulty_link = Mock(side_effect=[False, False, True, True, False, True])

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        result = comparison_report._get_outage_causes(edge_status_1)
        assert result is None

        result = comparison_report._get_outage_causes(edge_status_2)
        assert result == {'edge': 'OFFLINE', 'links': {'GE1': edge_2_link_ge1_state, 'GE2': edge_2_link_ge2_state}}

        result = comparison_report._get_outage_causes(edge_status_3)
        assert result == {'edge': 'OFFLINE', 'links': {'GE2': edge_2_link_ge2_state}}

    @pytest.mark.asyncio
    async def get_management_status_test(self):
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC9876'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            }
        }

        uuid_ = uuid()
        management_status_request = {
            "request_id": uuid_,
            "body": {
                "client_id": 12345,
                "status": "A",
                "service_number": 'VC9876'
            }
        }

        management_status_response = {
            "body": "Some info",
            "status": 200,
        }

        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=management_status_response)

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        with patch.object(comparison_report_module, 'uuid', return_value=uuid_):
            management_status = await comparison_report._get_management_status(edge_status)

        event_bus.rpc_request.assert_awaited_once_with("bruin.inventory.management.status",
                                                       management_status_request, timeout=30)
        assert management_status == management_status_response

    @pytest.mark.asyncio
    async def is_management_status_active_ok_test(self):
        management_status_str = "Pending"
        uuid_ = uuid()

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        with patch.object(comparison_report_module, 'uuid', return_value=uuid_):
            is_management_status_active = comparison_report._is_management_status_active(management_status_str)

        assert is_management_status_active is True

    @pytest.mark.asyncio
    async def is_management_status_active_false_test(self):
        management_status_str = "Inactive"
        uuid_ = uuid()

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        with patch.object(comparison_report_module, 'uuid', return_value=uuid_):
            is_management_status_active = comparison_report._is_management_status_active(management_status_str)

        assert is_management_status_active is False


class TestQuarantineJob:
    @pytest.mark.asyncio
    async def start_quarantine_job_with_run_date_undefined_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}
        bruin_client_info = {
            'client_id': 12345,
            'client_name': 'METTEL/NEW YORK',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        current_datetime = datetime.now()
        current_timestamp = datetime.timestamp(current_datetime)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        datetime_mock.timestamp = Mock(return_value=current_timestamp)
        with patch.object(comparison_report_module, 'datetime', new=datetime_mock):
            with patch.object(comparison_report_module, 'timezone', new=Mock()):
                await comparison_report._start_quarantine_job(edge_full_id, bruin_client_info, run_date=None)

        job_run_date = current_datetime + timedelta(seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'])
        scheduler.add_job.assert_called_once_with(
            comparison_report._process_edge_from_quarantine, 'date',
            run_date=job_run_date,
            replace_existing=False,
            misfire_grace_time=9999,
            id=f'_quarantine_{json.dumps(edge_full_id)}',
            kwargs={'edge_full_id': edge_full_id, 'bruin_client_info': bruin_client_info},
        )

    @pytest.mark.asyncio
    async def start_quarantine_job_with_custom_run_date_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}
        bruin_client_info = {
            'client_id': 12345,
            'client_name': 'METTEL/NEW YORK',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        job_run_date = datetime.fromtimestamp(999999)
        await comparison_report._start_quarantine_job(edge_full_id, bruin_client_info, run_date=job_run_date)

        scheduler.add_job.assert_called_once_with(
            comparison_report._process_edge_from_quarantine, 'date',
            run_date=job_run_date,
            replace_existing=False,
            misfire_grace_time=9999,
            id=f'_quarantine_{json.dumps(edge_full_id)}',
            kwargs={'edge_full_id': edge_full_id, 'bruin_client_info': bruin_client_info},
        )

    @pytest.mark.asyncio
    async def start_quarantine_job_with_job_id_already_executing_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}
        bruin_client_info = {
            'client_id': 12345,
            'client_name': 'METTEL/NEW YORK',
        }

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
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        current_datetime = datetime.now()
        current_timestamp = datetime.timestamp(current_datetime)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        datetime_mock.timestamp = Mock(return_value=current_timestamp)

        try:
            with patch.object(comparison_report_module, 'datetime', new=datetime_mock):
                with patch.object(comparison_report_module, 'timezone', new=Mock()):
                    await comparison_report._start_quarantine_job(edge_full_id, bruin_client_info)
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
            job_run_date = current_datetime + timedelta(seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'])
            scheduler.add_job.assert_called_once_with(
                comparison_report._process_edge_from_quarantine, 'date',
                run_date=job_run_date,
                replace_existing=False,
                misfire_grace_time=9999,
                id=f'_quarantine_{json.dumps(edge_full_id)}',
                kwargs={'edge_full_id': edge_full_id, 'bruin_client_info': bruin_client_info},
            )

    @pytest.mark.asyncio
    async def process_edge_from_quarantine_with_no_reportable_edge_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}

        edge_status_data = {
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': 'VC1234567',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': edge_status_data,
            },
            'status': 200,
        }

        bruin_client_info = {
            'client_id': 12345,
            'client_name': 'METTEL/NEW YORK',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        comparison_report._is_reportable_edge = CoroutineMock(return_value=False)
        comparison_report._add_edge_to_reporting = Mock()

        await comparison_report._process_edge_from_quarantine(edge_full_id, bruin_client_info)

        quarantine_edge_repository.remove_edge.assert_called_once_with(edge_full_id)

    @pytest.mark.asyncio
    async def process_edge_from_quarantine_with_reportable_edge_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}

        edge_status_data = {
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': 'VC1234567',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': edge_status_data,
            },
            'status': 200,
        }

        bruin_client_info = {
            'client_id': 12345,
            'client_name': 'METTEL/NEW YORK',
        }

        edge_status_data_with_bruin_client_info = {
            **edge_status_data,
            'bruin_client_info': bruin_client_info,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        comparison_report._is_reportable_edge = CoroutineMock(return_value=True)
        comparison_report._add_edge_to_reporting = Mock()

        await comparison_report._process_edge_from_quarantine(edge_full_id, bruin_client_info)

        comparison_report._add_edge_to_reporting.assert_called_once_with(
            edge_full_id, edge_status_data_with_bruin_client_info
        )

    @pytest.mark.asyncio
    async def process_edge_from_quarantine_with_exception_raised_while_determining_reportability_of_edge_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}

        edge_status_data = {
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': 'VC1234567',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': edge_status_data,
            },
            'status': 200,
        }

        bruin_client_info = {
            'client_id': 12345,
            'client_name': 'METTEL/NEW YORK',
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        comparison_report._is_reportable_edge = CoroutineMock(side_effect=ValueError)
        comparison_report._add_edge_to_reporting = Mock()

        await comparison_report._process_edge_from_quarantine(edge_full_id, bruin_client_info)

        comparison_report._add_edge_to_reporting.assert_not_called()

    @pytest.mark.asyncio
    async def is_reportable_edge_with_healthy_status_test(self):
        edge_status = {
            'edges': {
                'edgeState': 'CONNECTED',
                'serialNumber': 'VC1234567',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=False)

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_outage_ticket_for_edge = CoroutineMock()

        result = await comparison_report._is_reportable_edge(edge_status)

        comparison_report._get_outage_ticket_for_edge.assert_not_awaited()
        assert result is False

    @pytest.mark.asyncio
    async def is_reportable_edge_with_faulty_status_and_outage_ticket_found_test(self):
        edge_status = {
            'edges': {
                'edgeState': 'CONNECTED',
                'serialNumber': 'VC1234567',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        outage_ticket = {
            'request_id': uuid(),
            'body': {
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
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        outage_repository.is_there_an_outage = Mock(wraps=outage_repository.is_there_an_outage)
        comparison_report._get_outage_ticket_for_edge = CoroutineMock(return_value=outage_ticket)

        result = await comparison_report._is_reportable_edge(edge_status)

        # comparison_report._is_there_an_outage.assert_called_once_with(edge_status)
        comparison_report._get_outage_ticket_for_edge.assert_awaited_once_with(edge_status)
        assert result is False

    @pytest.mark.asyncio
    async def is_reportable_edge_with_faulty_status_and_outage_ticket_not_found_test(self):
        edge_status = {
            'edges': {
                'edgeState': 'CONNECTED',
                'serialNumber': 'VC1234567',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        outage_ticket = {
            'request_id': uuid(),
            'body': None,
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        outage_repository.is_there_an_outage = Mock(wraps=outage_repository.is_there_an_outage)
        comparison_report._get_outage_ticket_for_edge = CoroutineMock(return_value=outage_ticket)

        result = await comparison_report._is_reportable_edge(edge_status)

        # comparison_report._is_there_an_outage.assert_called_once_with(edge_status)
        comparison_report._get_outage_ticket_for_edge.assert_awaited_once_with(edge_status)
        assert result is True

    @pytest.mark.asyncio
    async def is_reportable_edge_with_faulty_status_and_unexpected_outage_ticket_format_test(self):
        edge_status = {
            'edges': {
                'edgeState': 'CONNECTED',
                'serialNumber': 'VC1234567',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        outage_ticket = None

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_outage_ticket_for_edge = CoroutineMock(return_value=outage_ticket)

        with pytest.raises(ValueError):
            await comparison_report._is_reportable_edge(edge_status)

    @pytest.mark.asyncio
    async def get_outage_ticket_for_edge_with_default_ticket_statuses_test(self):
        client_id = 12345
        enterprise_name = f'EVIL-CORP|{client_id}|'
        edge_serial_number = 'VC1234567'
        edge_status = {
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': edge_serial_number,
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE'}},
                {'linkId': 5678, 'link': {'state': 'STABLE'}},
            ],
            'enterprise_name': enterprise_name,
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        outage_ticket = {
            'body': {
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
            },
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=outage_ticket)
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        uuid_ = uuid()
        with patch.object(comparison_report_module, 'uuid', return_value=uuid_):
            outage_ticket_result = await comparison_report._get_outage_ticket_for_edge(edge_status)

        event_bus.rpc_request.assert_awaited_once_with(
            'bruin.ticket.outage.details.by_edge_serial.request',
            {
                'request_id': uuid_,
                'body': {
                    'edge_serial': edge_serial_number,
                    'client_id': client_id,
                },
            },
            timeout=180,
        )
        assert outage_ticket_result == outage_ticket

    @pytest.mark.asyncio
    async def get_outage_ticket_for_edge_with_custom_ticket_statuses_test(self):
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
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        outage_ticket = {
            'body': {
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
            },
            'status': 200,
        }

        ticket_statuses = ['Resolved', 'New', 'InProgress', 'Draft']

        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=outage_ticket)
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        uuid_ = uuid()
        with patch.object(comparison_report_module, 'uuid', return_value=uuid_):
            outage_ticket_result = await comparison_report._get_outage_ticket_for_edge(
                edge_status, ticket_statuses=ticket_statuses
            )

        event_bus.rpc_request.assert_awaited_once_with(
            'bruin.ticket.outage.details.by_edge_serial.request',
            {
                'request_id': uuid_,
                'body': {
                    'edge_serial': edge_serial_number,
                    'client_id': client_id,
                    'ticket_statuses': ticket_statuses,
                },
            },
            timeout=180,
        )
        assert outage_ticket_result == outage_ticket

    def add_edge_to_reporting_test(self):
        edge_full_id = {'host': 'metvco04.mettel.net', 'enterprise_id': 1234, 'edge_id': 5678}
        client_id = 12345
        edge_status = {
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': 'VC1234567',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
        }

        addition_to_quarantine_timestamp = 123456789
        edge_status_in_quarantine = {
            'edge_status': {
                'edges': {
                    'edgeState': 'CONNECTED',
                    'serialNumber': 'VC7654321',
                    'name': 'Saturos',
                    'lastContact': '2020-01-16T14:59:56.245Z'
                },
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
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        comparison_report._add_edge_to_reporting(edge_full_id, edge_status)

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
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': 'VC1234567',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
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
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        current_datetime = datetime.now()
        current_timestamp = datetime.timestamp(current_datetime)
        datetime_mock = Mock()
        datetime_mock.timestamp = Mock(return_value=current_timestamp)
        with patch.object(comparison_report_module, 'datetime', new=datetime_mock):
            with patch.object(comparison_report_module, 'timezone', new=Mock()):
                comparison_report._add_edge_to_reporting(edge_full_id, edge_status)

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
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(comparison_report_module, 'datetime', new=datetime_mock):
            with patch.object(comparison_report_module, 'timezone', new=Mock()):
                await comparison_report.start_service_outage_reporter_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            comparison_report._service_outage_reporter_process, 'interval',
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
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        await comparison_report.start_service_outage_reporter_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            comparison_report._service_outage_reporter_process, 'interval',
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
                'edges': {
                    'edgeState': 'OFFLINE',
                    'serialNumber': edge_1_serial_number,
                    'name': 'Saturos',
                    'lastContact': '2020-01-16T14:59:56.245Z'
                },
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
                'edges': {
                    'edgeState': 'CONNECTED',
                    'serialNumber': edge_2_serial_number,
                    'name': 'Menardi',
                    'lastContact': '2020-01-16T14:59:56.245Z'
                },
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
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._refresh_reporting_queue = CoroutineMock()
        comparison_report._attach_outage_causes_to_edges = Mock()
        comparison_report._unmarshall_edge_to_report = Mock(side_effect=unmarshalling_result)

        await comparison_report._service_outage_reporter_process()

        # comparison_report._refresh_reporting_queue.assert_awaited_once()
        comparison_report._attach_outage_causes_to_edges.assert_called_once_with(edges_to_report)
        reporting_edge_repository.get_all_edges.assert_called_once()
        comparison_report._unmarshall_edge_to_report.assert_has_calls([
            call(edge_1_identifier, edge_1_value),
            call(edge_2_identifier, edge_2_value),
        ])
        template_renderer.compose_email_object.assert_called_once_with(
            unmarshalling_result,
            fields=["Date of detection", "Company", "Edge name", "Last contact", "Serial Number", "Edge URL",
                    "Outage causes"],
            fields_edge=["detection_time", "enterprise", "edge_name", "last_contact", "serial_number", "edge_url",
                         "outage_causes"],
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
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._refresh_reporting_queue = CoroutineMock()
        comparison_report._attach_outage_causes_to_edges = Mock()
        comparison_report._unmarshall_edge_to_report = Mock()

        await comparison_report._service_outage_reporter_process()

        # comparison_report._refresh_reporting_queue.assert_awaited_once()
        comparison_report._attach_outage_causes_to_edges.assert_not_called()
        reporting_edge_repository.get_all_edges.assert_called_once()
        comparison_report._unmarshall_edge_to_report.assert_not_called()
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
                'edges': {
                    'edgeState': 'OFFLINE',
                    'serialNumber': 'VC123456789',
                    'name': 'Saturos',
                    'lastContact': '2020-01-16T14:59:56.245Z'
                },
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
                'edges': {
                    'edgeState': 'CONNECTED',
                    'serialNumber': 'VC987654321',
                    'name': 'Menardi',
                    'lastContact': '2020-01-16T14:59:56.245Z'
                },
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
                'edges': {
                    'edgeState': 'CONNECTED',
                    'serialNumber': 'VC111122223',
                    'name': 'Isaac',
                    'lastContact': '2020-01-16T14:59:56.245Z'
                },
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
                'edges': {
                    'edgeState': 'OFFLINE',
                    'serialNumber': 'VC111122223',
                    'name': 'Nadia',
                    'lastContact': '2020-01-16T14:59:56.245Z'
                },
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

        edge_1_data = {
            'edges': {
                'edgeState': 'CONNECTED',
                'serialNumber': 'VC123456789',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_1_new_status_response = {
            'body': {
                'edge_id': edge_1_full_id,
                'edge_info': edge_1_data,
            },
            'status': 200,
        }

        edge_2_data = {
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': 'VC987654321',
                'name': 'Menardi',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_2_new_status_response = {
            'body': {
                'edge_id': edge_2_full_id,
                'edge_info': edge_2_data,
            },
            'status': 200,
        }

        edge_3_data = {
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': 'VC111122223',
                'name': 'Isaac',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_3_new_status_response = {
            'body': {
                'edge_id': edge_3_full_id,
                'edge_info': edge_3_data,
            },
            'status': 200,
        }

        edge_4_data = {
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': 'VC111122223',
                'name': 'Nadia',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_4_new_status_response = {
            'body': {
                'edge_id': edge_4_full_id,
                'edge_info': edge_4_data,
            },
            'status': 200,
        }

        edge_2_outage_ticket = {
            'request_id': uuid(),
            'body': None,
            'status': 500,
        }
        edge_3_outage_ticket = {
            'request_id': uuid(),
            'body': {
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
        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(side_effect=[False, True, True, True])

        reporting_edge_repository = Mock()
        reporting_edge_repository.get_all_edges = Mock(return_value=edges_to_report)

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_edge_status_by_id = CoroutineMock(side_effect=[
            edge_1_new_status_response,
            edge_2_new_status_response,
            edge_3_new_status_response,
            edge_4_new_status_response,
        ])
        comparison_report._get_outage_ticket_for_edge = CoroutineMock(side_effect=[
            edge_2_outage_ticket, edge_3_outage_ticket, edge_4_outage_ticket
        ])

        await comparison_report._refresh_reporting_queue()

        edge_2_new_value = {**edge_2_value, **{'edge_status': edge_2_data}}
        reporting_edge_repository.add_edge.assert_called_once_with(
            edge_2_full_id,
            edge_2_new_value,
            update_existing=True, time_to_live=None,
        )
        reporting_edge_repository.remove_edge.assert_has_calls([
            call(edge_1_full_id), call(edge_3_full_id)
        ])

    @pytest.mark.asyncio
    async def refresh_reporting_queue_throws_exception_test(self):
        edge_1_full_id = {'host': 'metvc04.mettel.net', 'enterprise_id': 12345, 'edge_id': 67890}

        edge_1_identifier = EdgeIdentifier(**edge_1_full_id)

        edge_1_value = {
            'edge_status': {
                'edges': {
                    'edgeState': 'OFFLINE',
                    'serialNumber': 'VC123456789',
                    'name': 'Saturos',
                    'lastContact': '2020-01-16T14:59:56.245Z'
                },
                'links': [
                    {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                    {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                ],
                'enterprise_name': 'EVIL-CORP|12345|',
            },
            'detection_timestamp': 123456789,
            'addition_timestamp': 11112222,
        }

        edges_to_report = {
            edge_1_identifier: edge_1_value,
        }

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        quarantine_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(side_effect=[False, True, True, True])

        reporting_edge_repository = Mock()
        reporting_edge_repository.get_all_edges = Mock(return_value=edges_to_report)

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)
        comparison_report._get_edge_status_by_id = CoroutineMock(side_effect=Exception)

        await comparison_report._refresh_reporting_queue()

        logger.exception.assert_called()

    def attach_outage_causes_to_edges_test(self):
        edge_1_full_id = {'host': 'metvc04.mettel.net', 'enterprise_id': 12345, 'edge_id': 67890}
        edge_2_full_id = {'host': 'metvc04.mettel.net', 'enterprise_id': 54321, 'edge_id': 98765}
        edge_3_full_id = {'host': 'metvc04.mettel.net', 'enterprise_id': 11111, 'edge_id': 22222}

        edge_1_identifier = EdgeIdentifier(**edge_1_full_id)
        edge_2_identifier = EdgeIdentifier(**edge_2_full_id)
        edge_3_identifier = EdgeIdentifier(**edge_3_full_id)

        edge_1_status = {
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': 'VC123456789',
                'name': 'Saturos',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_2_status = {
            'edges': {
                'edgeState': 'CONNECTED',
                'serialNumber': 'VC987654321',
                'name': 'Menardi',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_3_status = {
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': 'VC111122223',
                'name': 'Isaac',
                'lastContact': '2020-01-16T14:59:56.245Z'
            },
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
        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(side_effect=is_faulty_edge_side_effect)
        outage_repository.is_faulty_link = Mock(side_effect=is_faulty_link_side_effect)

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        comparison_report._attach_outage_causes_to_edges(edges_to_report)

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
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        result_url = comparison_report._generate_edge_url(edge_full_id)

        expected_url = f'https://{host}/#!/operator/customer/{enterprise_id}/monitor/edge/{edge_id}/'
        assert result_url == expected_url

    def unmarshall_edge_to_report_test(self):
        host = 'metvco04.mettel.net'
        enterprise_id = 12345
        edge_id = 67890
        edge_identifier = EdgeIdentifier(host=host, enterprise_id=enterprise_id, edge_id=edge_id)

        detection_timestamp = 123456789
        edge_name = 'Saturos'
        last_contact = '2020-01-16T14:59:56.245Z'
        edge_serial_number = 'V123456789'
        enterprise_name = 'EVIL-CORP'
        edge_1_value = {
            'edge_status': {
                'edges': {
                    'edgeState': 'OFFLINE',
                    'serialNumber': edge_serial_number,
                    'name': edge_name,
                    'lastContact': last_contact,
                },
                'links': [
                    {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                    {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                ],
                'enterprise_name': 'EVIL-CORP|12345|',
                'bruin_client_info': {
                    'client_id': 12345,
                    'client_name': enterprise_name,
                },
            },
            'detection_timestamp': detection_timestamp,
            'addition_timestamp': 987654321,
            'outage_causes': {'edge': 'OFFLINE', 'links': {'GE1': 'DISCONNECTED', 'GE2': 'DISCONNECTED'}}
        }
        edge_2_value = {
            'edge_status': {
                'edges': {
                    'edgeState': 'OFFLINE',
                    'serialNumber': edge_serial_number,
                    'name': edge_name,
                    'lastContact': last_contact,
                    'bruin_client_info': {
                        'client_id': 12345,
                        'client_name': enterprise_name,
                    },
                },
                'links': [
                    {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                    {'linkId': 5678, 'link': {'state': 'DISCONNECTED', 'interface': 'GE2'}},
                ],
                'enterprise_name': 'EVIL-CORP|12345|',
                'bruin_client_info': {
                    'client_id': 12345,
                    'client_name': enterprise_name,
                },
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
        outage_repository = Mock()

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        tz = timezone(config.MONITOR_CONFIG['timezone'])
        expected_detection_time = datetime.fromtimestamp(detection_timestamp, tz=tz)
        expected_edge_url = f'https://{host}/#!/operator/customer/{enterprise_id}/monitor/edge/{edge_id}/'

        result = comparison_report._unmarshall_edge_to_report(edge_identifier, edge_1_value)
        expected = {
            'detection_time': expected_detection_time,
            'edge_name': edge_name,
            'last_contact': last_contact,
            'serial_number': edge_serial_number,
            'enterprise': enterprise_name,
            'edge_url': expected_edge_url,
            'outage_causes': [
                'Edge was OFFLINE',
                'Link GE1 was DISCONNECTED',
                'Link GE2 was DISCONNECTED',
            ],
        }
        assert result == expected

        result = comparison_report._unmarshall_edge_to_report(edge_identifier, edge_2_value)
        expected = {
            'detection_time': expected_detection_time,
            'edge_name': edge_name,
            'last_contact': last_contact,
            'serial_number': edge_serial_number,
            'enterprise': enterprise_name,
            'edge_url': expected_edge_url,
            'outage_causes': [
                'Link GE2 was DISCONNECTED',
            ],
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_bruin_client_info_by_serial_test(self):
        uuid_ = uuid()

        serial_number = 'VC1234567'
        bruin_client_info_response = {
            'request_id': uuid_,
            'body': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            },
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        quarantine_edge_repository = Mock()
        reporting_edge_repository = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=bruin_client_info_response)

        comparison_report = ComparisonReport(event_bus, logger, scheduler,
                                             quarantine_edge_repository, reporting_edge_repository,
                                             config, template_renderer, outage_repository)

        with patch.object(comparison_report_module, 'uuid', return_value=uuid_):
            result = await comparison_report._get_bruin_client_info_by_serial(serial_number)

        event_bus.rpc_request.assert_awaited_once_with(
            'bruin.customer.get.info',
            {'request_id': uuid_, 'body': {'service_number': serial_number}},
            timeout=30,
        )
        assert result == bruin_client_info_response
