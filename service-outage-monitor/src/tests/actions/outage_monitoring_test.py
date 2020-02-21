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

from application.actions import outage_monitoring as outage_monitoring_module
from application.actions.outage_monitoring import OutageMonitor
from config import testconfig


class TestServiceOutageMonitor:
    @pytest.mark.asyncio
    async def start_service_outage_monitoring_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                await outage_monitor.start_service_outage_monitoring(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            outage_monitor._outage_monitoring_process, 'interval',
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
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        await outage_monitor.start_service_outage_monitoring(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            outage_monitor._outage_monitoring_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
            next_run_time=undefined,
            replace_existing=False,
            id='_service_outage_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_outage_monitor_job_with_job_id_already_executing_test(self):
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        try:
            await outage_monitor.start_service_outage_monitoring(exec_on_start=False)
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                outage_monitor._outage_monitoring_process, 'interval',
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
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edges_for_monitoring = Mock(return_value=[])
        outage_monitor._get_edge_status_by_id = CoroutineMock()

        await outage_monitor._outage_monitoring_process()

        outage_monitor._get_edges_for_monitoring.assert_called_once()
        outage_monitor._get_edge_status_by_id.assert_not_awaited()
        outage_repository.is_there_an_outage.assert_not_called()
        scheduler.add_job.assert_not_called()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_status_in_management_500_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': {
                    'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
                    'links': [
                        {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                        {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
                    ],
                    'enterprise_name': 'EVIL-CORP|12345|',
                },
            },
            'status': 200,
        }
        management_status_response = {
            "body": "None",
            "status": 500,
        }
        uuid_ = uuid()
        message = (
            f"[outage-monitoring] Management status is unknown for {EdgeIdentifier(**edge_full_id)}. "
            f"Cause: {management_status_response['body']}"
        )
        slack_message = {
            'request_id': uuid_,
            'message': message
        }
        is_there_an_outage = True

        logger = Mock()
        config = testconfig
        scheduler = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=is_there_an_outage)

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
            outage_monitor._get_edges_for_monitoring = Mock(return_value=[edge_full_id])
            outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
            outage_monitor._get_management_status = CoroutineMock(return_value=management_status_response)
            outage_monitor._is_management_status_active = Mock(return_value=True)

            await outage_monitor._outage_monitoring_process()

            event_bus.rpc_request.assert_awaited_with("notification.slack.request", slack_message, timeout=30)

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_status_in_management_inactive_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': {
                    'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
                    'links': [
                        {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                        {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
                    ],
                    'enterprise_name': 'EVIL-CORP|12345|',
                },
            },
            'status': 200,
        }
        management_status_response = {
            "body": "None",
            "status": 200,
        }
        is_there_an_outage = True

        event_bus = Mock()
        logger = Mock()
        config = testconfig

        scheduler = Mock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=is_there_an_outage)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edges_for_monitoring = Mock(return_value=[edge_full_id])
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        outage_monitor._get_management_status = CoroutineMock(return_value=management_status_response)
        outage_monitor._is_management_status_active = Mock(return_value=False)

        await outage_monitor._outage_monitoring_process()

        outage_repository.is_there_an_outage.assert_not_called()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_edges_and_no_outages_detected_test(self):
        edge_1_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_2_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 5678}
        edge_3_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 9012}
        edges_for_monitoring = [edge_1_full_id, edge_2_full_id, edge_3_full_id]

        edge_1_status_data = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_1_status_response = {
            'body': {
                'edge_id': edge_1_full_id,
                'edge_info': edge_1_status_data,
            },
            'status': 200,
        }

        edge_2_status_data = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC7654321'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_2_status_response = {
            'body': {
                'edge_id': edge_2_full_id,
                'edge_info': edge_2_status_data,
            },
            'status': 200,
        }

        edge_3_status_data = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1122334'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_3_status_response = {
            'body': {
                'edge_id': edge_3_full_id,
                'edge_info': edge_3_status_data,
            },
            'status': 200,
        }
        edges_statuses_responses = [edge_1_status_response, edge_2_status_response, edge_3_status_response]

        is_there_an_outage_side_effect = [
            False,  # Edge 1
            False,  # Edge 2
            False,  # Edge 3
        ]

        management_status = {"body": "Active – Gold Monitoring",
                             "status": 200}

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(side_effect=is_there_an_outage_side_effect)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edges_for_monitoring = Mock(return_value=edges_for_monitoring)
        outage_monitor._get_edge_status_by_id = CoroutineMock(side_effect=edges_statuses_responses)
        outage_monitor._get_management_status = CoroutineMock(return_value=management_status)
        outage_monitor._is_management_status_active = Mock(return_value=True)

        await outage_monitor._outage_monitoring_process()

        outage_monitor._get_edges_for_monitoring.assert_called_once()

        outage_monitor._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id), call(edge_2_full_id), call(edge_3_full_id)
        ])
        outage_repository.is_there_an_outage.assert_has_calls([
            call(edge_1_status_data), call(edge_2_status_data), call(edge_3_status_data)
        ])
        scheduler.add_job.assert_not_called()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_edges_and_some_outages_detected_and_recheck_job_not_scheduled_test(self):
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
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

        management_status_response = {
            "body": "Active – Gold Monitoring",
            "status": 200,
        }

        is_there_an_outage = True

        event_bus = Mock()
        logger = Mock()
        config = testconfig

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=is_there_an_outage)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edges_for_monitoring = Mock(return_value=[edge_full_id])
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        outage_monitor._get_management_status = CoroutineMock(return_value=management_status_response)
        outage_monitor._is_management_status_active = Mock()

        try:
            await outage_monitor._outage_monitoring_process()
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                outage_monitor._recheck_edge_for_ticket_creation, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'],
                replace_existing=False,
                id=f'_ticket_creation_recheck_{json.dumps(edge_full_id)}',
                kwargs={'edge_full_id': edge_full_id}
            )

        outage_monitor._get_edges_for_monitoring.assert_called_once()
        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_edges_and_some_outages_detected_and_recheck_job_scheduled_test(self):
        edge_1_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_2_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 5678}
        edge_3_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 9012}
        edges_for_monitoring = [edge_1_full_id, edge_2_full_id, edge_3_full_id]

        edge_1_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_1_status_response = {
            'body': {
                'edge_id': edge_1_full_id,
                'edge_info': edge_1_status_data,
            },
            'status': 200,
        }

        edge_2_status_data = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC7654321'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_2_status_response = {
            'body': {
                'edge_id': edge_2_full_id,
                'edge_info': edge_2_status_data,
            },
            'status': 200,
        }

        edge_3_status_data = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1122334'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_3_status_response = {
            'body': {
                'edge_id': edge_3_full_id,
                'edge_info': edge_3_status_data,
            },
            'status': 200,
        }

        edges_statuses_responses = [edge_1_status_response, edge_2_status_response, edge_3_status_response]

        management_status_response = {
            "body": "Active – Gold Monitoring",
            "status": 200,
        }

        is_there_an_outage_side_effect = [
            True,  # Edge 1
            False,  # Edge 2
            True,  # Edge 3
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(side_effect=is_there_an_outage_side_effect)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edges_for_monitoring = Mock(return_value=edges_for_monitoring)
        outage_monitor._get_edge_status_by_id = CoroutineMock(side_effect=edges_statuses_responses)
        outage_monitor._get_management_status = CoroutineMock(return_value=management_status_response)
        outage_monitor._is_management_status_active = Mock(return_value=True)

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._outage_monitoring_process()

        outage_monitor._get_edges_for_monitoring.assert_called_once()
        outage_monitor._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id), call(edge_2_full_id), call(edge_3_full_id)
        ])
        outage_repository.is_there_an_outage.assert_has_calls([
            call(edge_1_status_data), call(edge_2_status_data), call(edge_3_status_data)
        ])
        run_date = current_time + timedelta(
            seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'])
        scheduler.add_job.assert_has_calls([
            call(
                outage_monitor._recheck_edge_for_ticket_creation, 'date',
                run_date=run_date,
                replace_existing=False,
                misfire_grace_time=9999,
                id=f'_ticket_creation_recheck_{json.dumps(edge_1_full_id)}',
                kwargs={'edge_full_id': edge_1_full_id}
            ),
            call(
                outage_monitor._recheck_edge_for_ticket_creation, 'date',
                run_date=run_date,
                replace_existing=False,
                misfire_grace_time=9999,
                id=f'_ticket_creation_recheck_{json.dumps(edge_3_full_id)}',
                kwargs={'edge_full_id': edge_3_full_id}
            ),
        ])

    def get_edges_for_monitoring_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        edges = outage_monitor._get_edges_for_monitoring()

        expected = list(config.MONITORING_EDGES.values())
        assert edges == expected

    @pytest.mark.asyncio
    async def recheck_edge_for_ticket_creation_with_no_outage_detected_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status_data = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
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

        outage_happened = False

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=outage_happened)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        outage_monitor._create_outage_ticket = CoroutineMock()

        await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        outage_monitor._create_outage_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edge_for_ticket_creation_with_outage_detected_and_no_production_environment_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
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

        outage_happened = True

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        outage_monitor._create_outage_ticket = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        outage_monitor._create_outage_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edge_with_outage_detected_and_production_env_and_failing_ticket_creation_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_identifier = EdgeIdentifier(**edge_full_id)

        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
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

        outage_happened = True

        outage_ticket_creation_body = "Got internal error from Bruin"
        outage_ticket_creation_status = 500
        outage_ticket_creation_response = {
            'request_id': uuid(),
            'body': outage_ticket_creation_body,
            'status': outage_ticket_creation_status,
        }

        uuid_ = uuid()

        scheduler = Mock()
        logger = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        outage_monitor._create_outage_ticket = CoroutineMock(return_value=outage_ticket_creation_response)

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
                await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        outage_monitor._create_outage_ticket.assert_awaited_once_with(edge_status_data)
        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'Outage ticket creation failed for edge {edge_identifier}. Reason: '
                           f'Error {outage_ticket_creation_status} - {outage_ticket_creation_body}'
            },
            timeout=10
        )

    @pytest.mark.asyncio
    async def recheck_edge_with_outage_detected_and_production_env_and_ticket_creation_returning_status_200_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_identifier = EdgeIdentifier(**edge_full_id)

        client_id = 12345
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
        }
        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': edge_status_data,
            },
            'status': 200,
        }

        outage_happened = True

        outage_ticket_creation_body = 12345  # Ticket ID
        outage_ticket_creation_status = 200
        outage_ticket_creation_response = {
            'request_id': uuid(),
            'body': outage_ticket_creation_body,
            'status': outage_ticket_creation_status,
        }

        uuid_ = uuid()

        scheduler = Mock()
        logger = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        outage_monitor._create_outage_ticket = CoroutineMock(return_value=outage_ticket_creation_response)

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
                await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        outage_monitor._create_outage_ticket.assert_awaited_once_with(edge_status_data)
        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'Outage ticket created for faulty edge {edge_identifier}. Ticket '
                           f'details at https://app.bruin.com/helpdesk?clientId={client_id}&'
                           f'ticketId={outage_ticket_creation_body}.'
            },
            timeout=10
        )

    @pytest.mark.asyncio
    async def recheck_edge_with_outage_detected_and_production_env_and_ticket_creation_returning_status_409_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        client_id = 12345
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
        }
        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': edge_status_data,
            },
            'status': 200,
        }

        outage_happened = True

        outage_ticket_creation_body = 12345  # Ticket ID
        outage_ticket_creation_status = 409
        outage_ticket_creation_response = {
            'request_id': uuid(),
            'body': outage_ticket_creation_body,
            'status': outage_ticket_creation_status,
        }

        uuid_ = uuid()

        scheduler = Mock()
        logger = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        outage_monitor._create_outage_ticket = CoroutineMock(return_value=outage_ticket_creation_response)

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
                await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        outage_monitor._create_outage_ticket.assert_awaited_once_with(edge_status_data)
        assert call(
            "notification.slack.request",
            {'request_id': 'some-uuid', 'message': 'some-message'},
            timeout=10
        ) not in event_bus.rpc_request.mock_calls

    @pytest.mark.asyncio
    async def recheck_edge_with_outage_detected_and_production_env_and_ticket_creation_returning_status_471_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        client_id = 12345
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
        }
        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': edge_status_data,
            },
            'status': 200,
        }

        outage_happened = True

        outage_ticket_creation_body = 12345  # Ticket ID
        outage_ticket_creation_status = 471
        outage_ticket_creation_response = {
            'request_id': uuid(),
            'body': outage_ticket_creation_body,
            'status': outage_ticket_creation_status,
        }

        uuid_ = uuid()

        scheduler = Mock()
        logger = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        outage_monitor._create_outage_ticket = CoroutineMock(return_value=outage_ticket_creation_response)
        outage_monitor._reopen_outage_ticket = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
                await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        outage_monitor._create_outage_ticket.assert_awaited_once_with(edge_status_data)
        outage_monitor._reopen_outage_ticket.assert_awaited_once_with(
            outage_ticket_creation_body, edge_status_data
        )

    @pytest.mark.asyncio
    async def create_outage_ticket_test(self):
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
            "client_id": bruin_client_id,
            "service_number": serial_number,
        }

        post_ticket_result = {
            'request_id': uuid_,
            'body': 123456,  # Ticket ID
            'status': 200,
        }

        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=post_ticket_result)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._generate_outage_ticket = Mock(return_value=ticket_creation_details)

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            result = await outage_monitor._create_outage_ticket(edge_status)

        outage_monitor._generate_outage_ticket.assert_called_once_with(edge_status)
        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.creation.outage.request",
            {'request_id': uuid_, 'body': ticket_creation_details},
            timeout=30
        )
        assert result == post_ticket_result

    @pytest.mark.asyncio
    async def reopen_outage_ticket_with_failing_reopening_test(self):
        ticket_id = 1234567
        detail_id = 9876543
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 1},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|00001|',
        }
        uuid_ = uuid()

        ticket_details_msg = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
            },
        }

        ticket_reopening_msg = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
            },
        }

        ticket_details_result = {
            'request_id': uuid_,
            'body': {
                'ticketDetails': [
                    {
                        "detailID": detail_id,
                        "detailType": "Repair_WTN",
                        "detailStatus": "R",
                        "detailValue": "VC05400002265",
                        "assignedToName": "0",
                        "currentTaskID": None,
                        "currentTaskName": None,
                        "lastUpdatedBy": 0,
                        "lastUpdatedAt": "2020-02-14T12:40:04.69-05:00"
                    }
                ]
            },
            'status': 200,
        }

        reopen_ticket_result = {
            'request_id': uuid_,
            'status': 500,
        }

        slack_message_post_result = None

        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[
            ticket_details_result,
            reopen_ticket_result,
            slack_message_post_result,
        ])

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            await outage_monitor._reopen_outage_ticket(ticket_id, edge_status)

        event_bus.rpc_request.assert_has_awaits([
            call("bruin.ticket.details.request", ticket_details_msg, timeout=15),
            call("bruin.ticket.status.open", ticket_reopening_msg, timeout=30),
        ])
        logger.error.assert_called()

    @pytest.mark.asyncio
    async def reopen_outage_ticket_with_successful_reopening_test(self):
        ticket_id = 1234567
        detail_id = 9876543
        bruin_client_id = 12345
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 1},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_id}|',
        }
        uuid_ = uuid()

        ticket_details_msg = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
            },
        }

        ticket_reopening_msg = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
            },
        }

        ticket_details_result = {
            'request_id': uuid_,
            'body': {
                'ticketDetails': [
                    {
                        "detailID": detail_id,
                        "detailType": "Repair_WTN",
                        "detailStatus": "R",
                        "detailValue": "VC05400002265",
                        "assignedToName": "0",
                        "currentTaskID": None,
                        "currentTaskName": None,
                        "lastUpdatedBy": 0,
                        "lastUpdatedAt": "2020-02-14T12:40:04.69-05:00"
                    }
                ]
            },
            'status': 200,
        }

        reopen_ticket_result = {
            'request_id': uuid_,
            'status': 200,
        }

        slack_message_post_result = None

        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[
            ticket_details_result,
            reopen_ticket_result,
            slack_message_post_result
        ])

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        outage_monitor._post_note_in_outage_ticket = CoroutineMock()

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            await outage_monitor._reopen_outage_ticket(ticket_id, edge_status)

        outage_monitor._post_note_in_outage_ticket.assert_called_once_with(ticket_id, edge_status)
        event_bus.rpc_request.assert_has_awaits([
            call("bruin.ticket.details.request", ticket_details_msg, timeout=15),
            call("bruin.ticket.status.open", ticket_reopening_msg, timeout=30),
            call(
                "notification.slack.request",
                {
                    'request_id': uuid_,
                    'message': (
                        f'Outage ticket {ticket_id} reopened. Ticket details at '
                        f'https://app.bruin.com/helpdesk?clientId={bruin_client_id}&ticketId={ticket_id}.')
                },
                timeout=10
            )
        ])

    @pytest.mark.asyncio
    async def _post_note_in_outage_ticket_with_no_outage_causes_test(self):
        ticket_id = 1234567
        edge_status = {
            'edges': {'edgeState': 'FAKE STATE', 'serialNumber': 1},
            'links': [
                {'linkId': 1234, 'link': {'state': 'FAKE STATE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'FAKE STATE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|00001|',
        }

        outage_causes = None

        config = testconfig

        ticket_note_timestamp = str(datetime.now(timezone(config.MONITOR_CONFIG['timezone'])))
        ticket_note_outage_causes = 'Outage causes: Could not determine causes.'

        ticket_note = (
            f'#*Automation Engine*#\n'
            f'Re-opening ticket.\n'
            f'{ticket_note_outage_causes}\n'
            f'TimeStamp: {ticket_note_timestamp}'
        )

        uuid_ = uuid()
        ticket_append_note_msg = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'note': ticket_note,
            },
        }

        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_outage_causes = Mock(return_value=outage_causes)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=ticket_note_timestamp)

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
                await outage_monitor._post_note_in_outage_ticket(ticket_id, edge_status)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.note.append.request",
            ticket_append_note_msg,
            timeout=15
        )

    @pytest.mark.asyncio
    async def _post_note_in_outage_ticket_with_outage_causes_and_only_faulty_edge_test(self):
        ticket_id = 1234567
        edge_state = 'OFFLINE'
        edge_status = {
            'edges': {'edgeState': edge_state, 'serialNumber': 1},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|00001|',
        }

        outage_causes = {'edge': edge_state}

        config = testconfig

        ticket_note_timestamp = str(datetime.now(timezone(config.MONITOR_CONFIG['timezone'])))
        ticket_note_outage_causes = f'Outage causes: Edge was {edge_state}.'

        ticket_note = (
            f'#*Automation Engine*#\n'
            f'Re-opening ticket.\n'
            f'{ticket_note_outage_causes}\n'
            f'TimeStamp: {ticket_note_timestamp}'
        )

        uuid_ = uuid()
        ticket_append_note_msg = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'note': ticket_note,
            },
        }

        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_outage_causes = Mock(return_value=outage_causes)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=ticket_note_timestamp)

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
                await outage_monitor._post_note_in_outage_ticket(ticket_id, edge_status)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.note.append.request",
            ticket_append_note_msg,
            timeout=15
        )

    @pytest.mark.asyncio
    async def _post_note_in_outage_ticket_with_outage_causes_and_only_faulty_links_test(self):
        ticket_id = 1234567
        link_1_interface = 'GE1'
        link_2_interface = 'GE2'
        links_state = 'DISCONNECTED'
        edge_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': 1},
            'links': [
                {'linkId': 1234, 'link': {'state': links_state, 'interface': link_1_interface}},
                {'linkId': 5678, 'link': {'state': links_state, 'interface': link_2_interface}},
            ],
            'enterprise_name': f'EVIL-CORP|00001|',
        }

        outage_causes = {'links': {link_1_interface: links_state, link_2_interface: links_state}}

        config = testconfig

        ticket_note_timestamp = str(datetime.now(timezone(config.MONITOR_CONFIG['timezone'])))
        ticket_note_outage_causes = (
            f'Outage causes: Link {link_1_interface} was {links_state}. Link {link_2_interface} was {links_state}.'
        )

        ticket_note = (
            f'#*Automation Engine*#\n'
            f'Re-opening ticket.\n'
            f'{ticket_note_outage_causes}\n'
            f'TimeStamp: {ticket_note_timestamp}'
        )

        uuid_ = uuid()
        ticket_append_note_msg = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'note': ticket_note,
            },
        }

        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_outage_causes = Mock(return_value=outage_causes)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=ticket_note_timestamp)

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
                await outage_monitor._post_note_in_outage_ticket(ticket_id, edge_status)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.note.append.request",
            ticket_append_note_msg,
            timeout=15
        )

    @pytest.mark.asyncio
    async def _post_note_in_outage_ticket_with_outage_causes_and_faulty_edge_and_faulty_links_test(self):
        ticket_id = 1234567
        edge_state = 'OFFLINE'
        link_1_interface = 'GE1'
        link_2_interface = 'GE2'
        links_state = 'DISCONNECTED'
        edge_status = {
            'edges': {'edgeState': edge_state, 'serialNumber': 1},
            'links': [
                {'linkId': 1234, 'link': {'state': links_state, 'interface': link_1_interface}},
                {'linkId': 5678, 'link': {'state': links_state, 'interface': link_2_interface}},
            ],
            'enterprise_name': f'EVIL-CORP|00001|',
        }

        outage_causes = {
            'edge': edge_state,
            'links': {link_1_interface: links_state, link_2_interface: links_state}
        }

        config = testconfig

        ticket_note_timestamp = str(datetime.now(timezone(config.MONITOR_CONFIG['timezone'])))
        ticket_note_outage_causes = (
            f'Outage causes: Edge was {edge_state}. '
            f'Link {link_1_interface} was {links_state}. Link {link_2_interface} was {links_state}.'
        )

        ticket_note = (
            f'#*Automation Engine*#\n'
            f'Re-opening ticket.\n'
            f'{ticket_note_outage_causes}\n'
            f'TimeStamp: {ticket_note_timestamp}'
        )

        uuid_ = uuid()
        ticket_append_note_msg = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'note': ticket_note,
            },
        }

        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_outage_causes = Mock(return_value=outage_causes)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=ticket_note_timestamp)

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
                await outage_monitor._post_note_in_outage_ticket(ticket_id, edge_status)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.note.append.request",
            ticket_append_note_msg,
            timeout=15
        )

    @pytest.mark.asyncio
    async def generate_outage_ticket_test(self):
        bruin_client_id = 12345
        serial_number = 'VC0123456789'
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
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        outage_ticket_data = outage_monitor._generate_outage_ticket(edge_status)

        assert outage_ticket_data == {
            "client_id": bruin_client_id,
            "service_number": serial_number,
        }

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
        edge_status_response = {
            'request_id': uuid_,
            'body': {
                'edge_id': edge_full_id,
                'edge_info': edge_status,
            },
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=edge_status_response)
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            result = await outage_monitor._get_edge_status_by_id(edge_full_id)

        event_bus.rpc_request.assert_awaited_once_with(
            'edge.status.request',
            {'request_id': uuid_, 'body': edge_full_id},
            timeout=120,
        )
        assert result == edge_status_response

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
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(side_effect=[False, True, True])
        outage_repository.is_faulty_link = Mock(side_effect=[False, False, True, True, False, True])

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        result = outage_monitor._get_outage_causes(edge_status_1)
        assert result is None

        result = outage_monitor._get_outage_causes(edge_status_2)
        assert result == {'edge': 'OFFLINE', 'links': {'GE1': edge_2_link_ge1_state, 'GE2': edge_2_link_ge2_state}}

        result = outage_monitor._get_outage_causes(edge_status_3)
        assert result == {'edge': 'OFFLINE', 'links': {'GE2': edge_2_link_ge2_state}}

    def extract_client_id_with_match_found_test(self):
        client_id = 12345
        enterprise_name = f'EVIL-CORP|{client_id}|'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        result_client_id = outage_monitor._extract_client_id(enterprise_name)
        assert result_client_id == client_id

    def extract_client_id_with_no_match_found_test(self):
        enterprise_name = f'EVIL-CORP'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        result_client_id = outage_monitor._extract_client_id(enterprise_name)
        assert result_client_id == 9994

    @pytest.mark.asyncio
    async def is_management_status_active_ok_test(self):
        management_status_str = "Pending"
        uuid_ = uuid()

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            is_management_status_active = outage_monitor._is_management_status_active(management_status_str)

        assert is_management_status_active is True

    @pytest.mark.asyncio
    async def is_management_status_active_false_test(self):
        management_status_str = "Inactive"
        uuid_ = uuid()

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            is_management_status_active = outage_monitor._is_management_status_active(management_status_str)

        assert is_management_status_active is False

    @pytest.mark.asyncio
    async def get_management_status_test(self):
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC9876'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|12345|',
        }
        management_status_rpc = {"body": "balblaba",
                                 "status": 200}
        uuid_ = uuid()
        management_request = {
            "request_id": uuid_,
            "body": {
                "client_id": 12345,
                "status": "A",
                "service_number": 'VC9876'
            }}
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        outage_monitor._extract_client_id = Mock(return_value=12345)
        event_bus.rpc_request = CoroutineMock(return_value=management_status_rpc)

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            management_status = await outage_monitor._get_management_status(edge_status)

        event_bus.rpc_request.assert_awaited_once_with("bruin.inventory.management.status",
                                                       management_request, timeout=30)
        assert management_status == management_status_rpc
