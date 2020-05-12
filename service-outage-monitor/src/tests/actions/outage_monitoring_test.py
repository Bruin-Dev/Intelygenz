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
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        assert outage_monitor._event_bus is event_bus
        assert outage_monitor._logger is logger
        assert outage_monitor._scheduler is scheduler
        assert outage_monitor._config is config
        assert outage_monitor._outage_repository is outage_repository

        assert outage_monitor._autoresolve_serials_whitelist == set()

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
    async def start_build_cache_job_with_exec_on_start_test(self):
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
                await outage_monitor._start_build_cache_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            outage_monitor._build_cache, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['build_cache'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_build_cache',
        )

    @pytest.mark.asyncio
    async def start_build_cache_job_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        await outage_monitor._start_build_cache_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            outage_monitor._build_cache, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['build_cache'],
            next_run_time=undefined,
            replace_existing=False,
            id='_build_cache',
        )

    @pytest.mark.asyncio
    async def start_build_cache_job_with_job_id_already_executing_test(self):
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
            await outage_monitor._start_build_cache_job(exec_on_start=False)
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                outage_monitor._build_cache, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['build_cache'],
                next_run_time=undefined,
                replace_existing=False,
                id='_build_cache',
            )

    @pytest.mark.asyncio
    async def start_edge_after_error_process_with_no_run_date_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        config = testconfig
        outage_repository = Mock()

        edge_full_id = {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        params = {
            'edge_full_id': edge_full_id,
            'bruin_client_info': bruin_client_info_response_body
        }
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                await outage_monitor._start_edge_after_error_process(edge_full_id, bruin_client_info_response_body)

        scheduler.add_job.assert_called_once_with(
                                    outage_monitor._process_edge_after_error,
                                    'date',
                                    run_date=next_run_time,
                                    replace_existing=False, misfire_grace_time=9999,
                                    id=f'_error_process_{json.dumps(edge_full_id)}',
                                    kwargs=params)

    @pytest.mark.asyncio
    async def start_edge_after_error_process_with_run_date_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        config = testconfig
        outage_repository = Mock()

        edge_full_id = {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        params = {
            'edge_full_id': edge_full_id,
            'bruin_client_info': bruin_client_info_response_body
        }
        job_run_date = datetime.fromtimestamp(999999)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                await outage_monitor._start_edge_after_error_process(edge_full_id, bruin_client_info_response_body,
                                                                     run_date=job_run_date)

        scheduler.add_job.assert_called_once_with(
            outage_monitor._process_edge_after_error,
            'date',
            run_date=job_run_date,
            replace_existing=False, misfire_grace_time=9999,
            id=f'_error_process_{json.dumps(edge_full_id)}',
            kwargs=params)

    @pytest.mark.asyncio
    async def start_edge_after_error_process_with_conflict_test(self):
        event_bus = Mock()
        logger = Mock()
        logger.error = Mock()
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=['ok', exception_instance])

        config = testconfig
        outage_repository = Mock()

        edge_full_id = {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        params = {
            'edge_full_id': edge_full_id,
            'bruin_client_info': bruin_client_info_response_body
        }
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                await outage_monitor._start_edge_after_error_process(edge_full_id, bruin_client_info_response_body)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                await outage_monitor._start_edge_after_error_process(edge_full_id, bruin_client_info_response_body)

        logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def outage_monitoring_process_no_rebuild_cache_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        fake_response = {'body': [], 'status': 200}

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edges_for_monitoring = CoroutineMock(return_value=fake_response)
        outage_monitor._start_build_cache_job = CoroutineMock()
        outage_monitor._monitoring_map_cache = [
            {'edge_full_id': {'host': 'mettel.velocloud.net', 'enterprise_id': 6, 'edge_id': 315}}
        ]

        await outage_monitor._outage_monitoring_process()

        outage_monitor._get_edges_for_monitoring.assert_not_awaited()
        outage_monitor._start_build_cache_job.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_host_with_cache_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        fake_response = {
            'request_id': 's8ixRY7ShDpYpZzJ34zk5P',
            'body': [{'host': 'mettel.velocloud.net', 'enterprise_id': 6, 'edge_id': 315}],
            'status': 200
        }

        fake_events_response = {
            'request_id': 's8ixRY7ShDpYpZzJ34zk5P',
            'body': [],
            'status': 200
        }

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edges_for_monitoring = CoroutineMock(return_value=fake_response)
        outage_monitor._get_last_events_for_edge = CoroutineMock(return_value=fake_events_response)
        outage_monitor._start_build_cache_job = CoroutineMock()
        outage_monitor._process_edge = CoroutineMock()

        outage_monitor._monitoring_map_cache = [
            {
                'edge_full_id': {'host': 'mettel.velocloud.net', 'enterprise_id': 6, 'edge_id': 315},
                'bruin_client_info': {
                    'client_id': 'AAAA', 'client_name': 'TESTNAME'
                }
            }
        ]

        await outage_monitor._outage_monitoring_process()

        outage_monitor._get_edges_for_monitoring.assert_not_awaited()
        outage_monitor._get_last_events_for_edge.assert_not_awaited()
        outage_monitor._start_build_cache_job.assert_not_awaited()
        outage_monitor._process_edge.assert_awaited_once()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_exception_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        fake_response = {
            'request_id': 's8ixRY7ShDpYpZzJ34zk5P',
            'body': [{'host': 'mettel.velocloud.net', 'enterprise_id': 6, 'edge_id': 315}],
            'status': 200
        }

        fake_events_response = {
            'request_id': 's8ixRY7ShDpYpZzJ34zk5P',
            'body': {'edges': {'serialNumber': 'testSN'}},
            'status': 200
        }

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edges_for_monitoring = CoroutineMock(return_value=fake_response)
        outage_monitor._get_last_events_for_edge = CoroutineMock(return_value=fake_events_response)
        outage_monitor._start_build_cache_job = CoroutineMock()

        await outage_monitor._outage_monitoring_process()

        outage_monitor._get_edges_for_monitoring.assert_awaited_once()
        outage_monitor._get_last_events_for_edge.assert_awaited_once()
        outage_monitor._start_build_cache_job.assert_awaited_once()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_failure_in_rpc_request_for_retrieval_of_edges_under_monitoring_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edges_for_monitoring = CoroutineMock(side_effect=Exception)
        outage_monitor._start_build_cache_job = CoroutineMock()

        with pytest.raises(Exception):
            await outage_monitor._outage_monitoring_process()

        outage_monitor._get_edges_for_monitoring.assert_awaited_once()
        logger.error.assert_called_once()
        outage_monitor._start_build_cache_job.assert_not_awaited()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_retrieval_of_edges_under_monitoring_returning_non_2XX_status_test(self):
        uuid_ = uuid()

        edge_list_response_body = "Got internal error from Velocloud"
        edge_list_response_status = 500
        edge_list_response = {
            'request_id': uuid(),
            'body': edge_list_response_body,
            'status': edge_list_response_status,
        }

        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edges_for_monitoring = CoroutineMock(return_value=edge_list_response)
        outage_monitor._get_last_events_for_edge = CoroutineMock()
        outage_monitor._add_edge_to_temp_cache = CoroutineMock()
        outage_monitor._start_build_cache_job = CoroutineMock()

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            await outage_monitor._outage_monitoring_process()

        outage_monitor._get_edges_for_monitoring.assert_awaited_once()
        logger.error.assert_called_once()
        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'[build_cache] Something happened while retrieving edges under monitoring from '
                           f'Velocloud. Reason: Error {edge_list_response_status} - {edge_list_response_body}',
            },
            timeout=10,
        )
        outage_monitor._get_last_events_for_edge.assert_not_awaited()
        outage_monitor._add_edge_to_temp_cache.assert_not_awaited()
        outage_monitor._start_build_cache_job.assert_awaited_once()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_no_edges_test(self):
        edge_list_response = {
            'request_id': uuid(),
            'body': [],
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edges_for_monitoring = CoroutineMock(return_value=edge_list_response)
        outage_monitor._get_last_events_for_edge = CoroutineMock()
        outage_monitor._add_edge_to_temp_cache = CoroutineMock()
        outage_monitor._start_build_cache_job = CoroutineMock()

        await outage_monitor._outage_monitoring_process()

        outage_monitor._get_edges_for_monitoring.assert_awaited_once()
        outage_monitor._get_last_events_for_edge.assert_not_awaited()
        outage_monitor._add_edge_to_temp_cache.assert_not_awaited()
        outage_repository.is_there_an_outage.assert_not_called()
        outage_monitor._start_build_cache_job.assert_awaited_once()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_edge_list_not_empty_and_edge_in_blacklist_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edges_for_monitoring = [edge_full_id]

        edge_list_response = {
            'request_id': uuid(),
            'body': edges_for_monitoring,
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['blacklisted_edges'] = [edge_full_id]

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edges_for_monitoring = CoroutineMock(return_value=edge_list_response)
        outage_monitor._get_last_events_for_edge = CoroutineMock()
        outage_monitor._add_edge_to_temp_cache = CoroutineMock()
        outage_monitor._start_build_cache_job = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._outage_monitoring_process()

        outage_monitor._get_edges_for_monitoring.assert_awaited_once()
        outage_monitor._get_last_events_for_edge.assert_not_awaited()
        outage_monitor._add_edge_to_temp_cache.assert_not_awaited()
        outage_monitor._start_build_cache_job.assert_awaited_once()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_retrieval_of_last_edge_events_returning_non_2XX_status_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edges_for_monitoring = [edge_full_id]

        edge_list_response = {
            'request_id': uuid(),
            'body': edges_for_monitoring,
            'status': 200,
        }

        edge_events_response = {
            'request_id': uuid(),
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edges_for_monitoring = CoroutineMock(return_value=edge_list_response)
        outage_monitor._get_last_events_for_edge = CoroutineMock(return_value=edge_events_response)
        outage_monitor._add_edge_to_temp_cache = CoroutineMock()
        outage_monitor._start_build_cache_job = CoroutineMock()

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._outage_monitoring_process()

        outage_monitor._get_edges_for_monitoring.assert_awaited_once()
        outage_monitor._get_last_events_for_edge.assert_awaited_once_with(
            edge_full_id,
            since=current_time - timedelta(days=7),
        )
        outage_monitor._add_edge_to_temp_cache.assert_not_awaited()
        outage_monitor._start_build_cache_job.assert_awaited_once()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_no_edge_events_during_last_week_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edges_for_monitoring = [edge_full_id]

        edge_list_response = {
            'request_id': uuid(),
            'body': edges_for_monitoring,
            'status': 200,
        }

        edge_events_response = {
            'request_id': uuid(),
            'body': [],
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edges_for_monitoring = CoroutineMock(return_value=edge_list_response)
        outage_monitor._get_last_events_for_edge = CoroutineMock(return_value=edge_events_response)
        outage_monitor._add_edge_to_temp_cache = CoroutineMock()
        outage_monitor._start_build_cache_job = CoroutineMock()

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._outage_monitoring_process()

        outage_monitor._get_edges_for_monitoring.assert_awaited_once()
        outage_monitor._get_last_events_for_edge.assert_awaited_once_with(
            edge_full_id,
            since=current_time - timedelta(days=7),
        )
        outage_monitor._add_edge_to_temp_cache.assert_not_awaited()
        outage_monitor._start_build_cache_job.assert_awaited_once()

    @pytest.mark.asyncio
    async def outage_monitoring_process_ok_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edges_for_monitoring = [edge_full_id]

        edge_list_response = {
            'request_id': uuid(),
            'body': edges_for_monitoring,
            'status': 200,
        }

        edge_events_response = {
            'request_id': uuid(),
            'body': [
                {
                    'event': 'EDGE_NEW_DEVICE',
                    'category': 'EDGE',
                    'eventTime': '2019-07-30 07:38:00+00:00',
                    'message': 'New or updated client device'
                },
                {
                    'event': 'EDGE_INTERFACE_UP',
                    'category': 'SYSTEM',
                    'eventTime': '2019-07-29 07:38:00+00:00',
                    'message': 'Interface GE1 is up'
                }
            ],
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edges_for_monitoring = CoroutineMock(return_value=edge_list_response)
        outage_monitor._get_last_events_for_edge = CoroutineMock(return_value=edge_events_response)
        outage_monitor._add_edge_to_temp_cache = CoroutineMock()
        outage_monitor._start_build_cache_job = CoroutineMock()

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._outage_monitoring_process()

        outage_monitor._get_edges_for_monitoring.assert_awaited_once()
        outage_monitor._get_last_events_for_edge.assert_awaited_once_with(
            edge_full_id,
            since=current_time - timedelta(days=7),
        )
        outage_monitor._add_edge_to_temp_cache.assert_awaited_with(edge_full_id)
        outage_monitor._start_build_cache_job.assert_awaited_once()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_having_a_null_serial_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': {
                    'edges': {'edgeState': 'OFFLINE', 'serialNumber': None},
                    'links': [
                        {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                        {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
                    ],
                    'enterprise_name': 'EVIL-CORP|12345|',
                },
            },
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        scheduler = Mock()
        event_bus = Mock()
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        outage_monitor._get_management_status = CoroutineMock()

        await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_monitor._get_management_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_retrieval_of_edge_status_returning_non_2XX_status_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_identifier = EdgeIdentifier(**edge_full_id)

        edge_status_response_body = 'Got internal error from Velocloud'
        edge_status_response_status = 500
        edge_status_response = {
            'body': edge_status_response_body,
            'status': edge_status_response_status,
        }
        uuid_ = uuid()
        message = (
            f"[outage-monitoring] An error occurred while trying to retrieve edge status for edge "
            f"{edge_identifier}: Error {edge_status_response_status} - {edge_status_response_body}"
        )
        slack_message = {
            'request_id': uuid_,
            'message': message
        }

        logger = Mock()
        config = testconfig
        scheduler = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        outage_monitor._get_management_status = CoroutineMock()

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        event_bus.rpc_request.assert_awaited_with("notification.slack.request", slack_message, timeout=30)
        outage_monitor._get_management_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_retrieval_of_bruin_client_info_returning_non_2XX_status_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_status_data = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_serial},
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

        bruin_client_info_response_body = 'Got internal error from Bruin'
        bruin_client_info_response_status = 500
        bruin_client_info_response = {
            "body": bruin_client_info_response_body,
            'status': bruin_client_info_response_status,
        }

        uuid_ = uuid()
        message = (
            f'Error trying to get Bruin client info from Bruin for serial {edge_serial}: '
            f'Error {bruin_client_info_response_status} - {bruin_client_info_response_body}'
        )
        slack_message = {
            'request_id': uuid_,
            'message': message
        }

        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        outage_monitor._get_bruin_client_info_by_serial = CoroutineMock(return_value=bruin_client_info_response)
        outage_monitor._get_management_status = CoroutineMock()

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_monitor._get_bruin_client_info_by_serial.assert_awaited_once_with(edge_serial)
        event_bus.rpc_request.assert_awaited_with("notification.slack.request", slack_message, timeout=10)
        outage_monitor._get_management_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_bruin_client_info_having_null_client_id_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_status_data = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_serial},
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

        bruin_client_info_response = {
            "body": {
                'client_id': None,
                'client_name': None,
            },
            'status': 200,
        }

        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        outage_monitor._get_bruin_client_info_by_serial = CoroutineMock(return_value=bruin_client_info_response)
        outage_monitor._get_management_status = CoroutineMock()

        await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_monitor._get_bruin_client_info_by_serial.assert_awaited_once_with(edge_serial)
        outage_monitor._get_management_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_retrieval_of_management_status_returning_non_2XX_status_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': edge_data,
            },
            'status': 200,
        }

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_response = {
            "body": bruin_client_info_response_body,
            'status': 200,
        }

        management_status_response = {
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        edge_data_with_bruin_info = {
            **edge_data,
            'bruin_client_info': bruin_client_info_response_body,
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

        logger = Mock()
        config = testconfig
        scheduler = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        outage_monitor._get_bruin_client_info_by_serial = CoroutineMock(return_value=bruin_client_info_response)
        outage_monitor._get_management_status = CoroutineMock(return_value=management_status_response)
        outage_monitor._is_management_status_active = Mock()

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_monitor._get_bruin_client_info_by_serial.assert_awaited_once_with(edge_serial)
        outage_monitor._get_management_status.assert_awaited_once_with(edge_data_with_bruin_info)
        event_bus.rpc_request.assert_awaited_with("notification.slack.request", slack_message, timeout=30)
        outage_monitor._is_management_status_active.assert_not_called()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_management_status_inactive_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': edge_data,
            },
            'status': 200,
        }

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_response = {
            "body": bruin_client_info_response_body,
            'status': 200,
        }

        management_status_response_body = 'Fake status'
        management_status_response = {
            "body": management_status_response_body,
            "status": 200,
        }

        edge_data_with_bruin_info = {
            **edge_data,
            'bruin_client_info': bruin_client_info_response_body,
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        scheduler = Mock()
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        outage_monitor._get_bruin_client_info_by_serial = CoroutineMock(return_value=bruin_client_info_response)
        outage_monitor._get_management_status = CoroutineMock(return_value=management_status_response)
        outage_monitor._is_management_status_active = Mock(return_value=False)

        await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_monitor._get_bruin_client_info_by_serial.assert_awaited_once_with(edge_serial)
        outage_monitor._get_management_status.assert_awaited_once_with(edge_data_with_bruin_info)
        outage_monitor._is_management_status_active.assert_called_once_with(management_status_response_body)

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_management_status_active_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': edge_data,
            },
            'status': 200,
        }

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_response = {
            "body": bruin_client_info_response_body,
            'status': 200,
        }

        management_status_response_body = 'Fake status'
        management_status_response = {
            "body": management_status_response_body,
            "status": 200,
        }

        edge_data_with_bruin_info = {
            **edge_data,
            'bruin_client_info': bruin_client_info_response_body,
        }

        expected_outcome = {
                            'edge_full_id': edge_full_id,
                            'edge_data': edge_data,
                            'bruin_client_info': bruin_client_info_response_body
        }
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        scheduler = Mock()
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        outage_monitor._get_bruin_client_info_by_serial = CoroutineMock(return_value=bruin_client_info_response)
        outage_monitor._get_management_status = CoroutineMock(return_value=management_status_response)
        outage_monitor._is_management_status_active = Mock(return_value=True)

        await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_monitor._get_bruin_client_info_by_serial.assert_awaited_once_with(edge_serial)
        outage_monitor._get_management_status.assert_awaited_once_with(edge_data_with_bruin_info)
        outage_monitor._is_management_status_active.assert_called_once_with(management_status_response_body)
        assert expected_outcome in outage_monitor._temp_monitoring_map

    @pytest.mark.asyncio
    async def process_edge_with_retrieval_of_edge_status_returning_non_2XX_status_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        edge_identifier = EdgeIdentifier(**edge_full_id)

        edge_status_response_body = 'Got internal error from Velocloud'
        edge_status_response_status = 500
        edge_status_response = {
            'body': edge_status_response_body,
            'status': edge_status_response_status,
        }
        uuid_ = uuid()
        message = (
            f"[outage-monitoring] An error occurred while trying to retrieve edge status for edge "
            f"{edge_identifier}: Error {edge_status_response_status} - {edge_status_response_body}"
        )
        slack_message = {
            'request_id': uuid_,
            'message': message
        }

        logger = Mock()
        config = testconfig
        scheduler = Mock()
        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=False)

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            await outage_monitor._process_edge(edge_full_id, bruin_client_info_response_body)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        event_bus.rpc_request.assert_awaited_with("notification.slack.request", slack_message, timeout=30)
        outage_repository.is_there_an_outage.assert_not_called()

    @pytest.mark.asyncio
    async def process_edge_no_outages_detected_test(self):
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

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        edge_data_with_bruin_info = {
            **edge_status_data,
            'bruin_client_info': bruin_client_info_response_body,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=False)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)

        await outage_monitor._process_edge(edge_full_id, bruin_client_info_response_body)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        outage_monitor._run_ticket_autoresolve_for_edge.assert_awaited_once_with(edge_full_id,
                                                                                 edge_data_with_bruin_info)

    @pytest.mark.asyncio
    async def process_edge_with_outages_detected_and_recheck_job_not_scheduled_test(self):
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

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
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
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)

        try:
            await outage_monitor._process_edge(edge_full_id, bruin_client_info_response_body)
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                outage_monitor._recheck_edge_for_ticket_creation, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'],
                replace_existing=False,
                id=f'_ticket_creation_recheck_{json.dumps(edge_full_id)}',
                kwargs={'edge_full_id': edge_full_id}
            )

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)

    @pytest.mark.asyncio
    async def process_edge_outages_detected_and_recheck_job_scheduled_test(self):
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

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._process_edge(edge_full_id, bruin_client_info_response_body)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        run_date = current_time + timedelta(
            seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'])
        scheduler.add_job.assert_called_once_with(
                outage_monitor._recheck_edge_for_ticket_creation, 'date',
                run_date=run_date,
                replace_existing=False,
                misfire_grace_time=9999,
                id=f'_ticket_creation_recheck_{json.dumps(edge_full_id)}',
                kwargs={'edge_full_id': edge_full_id, 'bruin_client_info': bruin_client_info_response_body}
            )
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_edge_with_side_effects_over_autoresolve_whitelist_with_autoresolve_filter_test(self):
        edge_full_id = {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial},
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

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['velocloud_instances_filter'] = {
            "mettel.velocloud.net": [],
            "metvco02.mettel.net": [],
        }
        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._process_edge(edge_full_id, bruin_client_info_response_body)

        assert outage_monitor._autoresolve_serials_whitelist == {edge_serial}

    @pytest.mark.asyncio
    async def process_edge_with_side_effects_over_autoresolve_whitelist_without_autoresolve_filter_test(self):
        edge_full_id = {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial},
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

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['velocloud_instances_filter'] = {}
        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._process_edge(edge_full_id, bruin_client_info_response_body)

        assert outage_monitor._autoresolve_serials_whitelist == {edge_serial}

    @pytest.mark.asyncio
    async def process_edge_exception_test(self):
        edge_full_id = {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial},
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

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=Exception)
        outage_monitor._start_edge_after_error_process = CoroutineMock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['velocloud_instances_filter'] = {}
        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._process_edge(edge_full_id, bruin_client_info_response_body)

        outage_monitor._start_edge_after_error_process.assert_awaited_once()

    @pytest.mark.asyncio
    async def process_edge_after_error_retrieval_of_edge_status_returning_non_2XX_status_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        edge_identifier = EdgeIdentifier(**edge_full_id)

        edge_status_response_body = 'Got internal error from Velocloud'
        edge_status_response_status = 500
        edge_status_response = {
            'body': edge_status_response_body,
            'status': edge_status_response_status,
        }
        uuid_ = uuid()
        message = (
            f"[process_edge_after_error] An error occurred while trying to retrieve edge status for edge "
            f"{edge_identifier}: Error {edge_status_response_status} - {edge_status_response_body}"
        )
        slack_message = {
            'request_id': uuid_,
            'message': message
        }

        logger = Mock()
        config = testconfig
        scheduler = Mock()
        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=False)

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)
        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            await outage_monitor._process_edge_after_error(edge_full_id, bruin_client_info_response_body)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        event_bus.rpc_request.assert_awaited_with("notification.slack.request", slack_message, timeout=30)
        outage_repository.is_there_an_outage.assert_not_called()

    @pytest.mark.asyncio
    async def process_edge_after_error_and_no_outages_detected_test(self):
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

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        edge_data_with_bruin_info = {
            **edge_status_data,
            'bruin_client_info': bruin_client_info_response_body,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=False)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)

        await outage_monitor._process_edge_after_error(edge_full_id, bruin_client_info_response_body)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        outage_monitor._run_ticket_autoresolve_for_edge.assert_awaited_once_with(edge_full_id,
                                                                                 edge_data_with_bruin_info)

    @pytest.mark.asyncio
    async def process_with_edge_after_error_outages_detected_and_recheck_job_not_scheduled_test(self):
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

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
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
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)

        try:
            await outage_monitor._process_edge_after_error(edge_full_id, bruin_client_info_response_body)
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                outage_monitor._recheck_edge_for_ticket_creation, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'],
                replace_existing=False,
                id=f'_ticket_creation_recheck_{json.dumps(edge_full_id)}',
                kwargs={'edge_full_id': edge_full_id}
            )

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)

    @pytest.mark.asyncio
    async def process_edge_after_error_outages_detected_and_recheck_job_scheduled_test(self):
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

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._process_edge_after_error(edge_full_id, bruin_client_info_response_body)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        run_date = current_time + timedelta(
            seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'])
        scheduler.add_job.assert_called_once_with(
                outage_monitor._recheck_edge_for_ticket_creation, 'date',
                run_date=run_date,
                replace_existing=False,
                misfire_grace_time=9999,
                id=f'_ticket_creation_recheck_{json.dumps(edge_full_id)}',
                kwargs={'edge_full_id': edge_full_id, 'bruin_client_info': bruin_client_info_response_body}
            )
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_edge_after_error_side_effects_over_autoresolve_whitelist_with_autoresolve_filter_test(self):
        edge_full_id = {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial},
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

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['velocloud_instances_filter'] = {
            "mettel.velocloud.net": [],
            "metvco02.mettel.net": [],
        }
        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._process_edge_after_error(edge_full_id, bruin_client_info_response_body)

        assert outage_monitor._autoresolve_serials_whitelist == {edge_serial}

    @pytest.mark.asyncio
    async def process_edge_after_error_side_effects_over_autoresolve_whitelist_without_autoresolve_filter_test(self):
        edge_full_id = {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial},
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

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=edge_status_response)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['velocloud_instances_filter'] = {}
        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._process_edge_after_error(edge_full_id, bruin_client_info_response_body)

        assert outage_monitor._autoresolve_serials_whitelist == {edge_serial}

    @pytest.mark.asyncio
    async def process_edge_after_error_exception_test(self):
        edge_full_id = {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        uuid_ = uuid()

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        expected_slack_message = {
            'request_id': uuid_,
            'message': f"Maximum retries happened while trying to process edge {edge_full_id} with "
                       f"serial {edge_serial}"
        }
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=Exception)
        outage_monitor._start_edge_after_error_process = CoroutineMock()
        outage_monitor._monitoring_map_cache = [
            {'edge_full_id': edge_full_id,
             'edge_data': edge_status_data}
        ]

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['velocloud_instances_filter'] = {}
        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
                await outage_monitor._process_edge_after_error(edge_full_id, bruin_client_info_response_body)

        event_bus.rpc_request.assert_awaited_once_with("notification.slack.request", expected_slack_message, timeout=30)

    @pytest.mark.asyncio
    async def process_edge_after_error_exception_no_serial_test(self):
        edge_full_id = {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        uuid_ = uuid()

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        expected_slack_message = {
            'request_id': uuid_,
            'message': f"Maximum retries happened while trying to process edge {edge_full_id} with "
                       f"serial {None}"
        }
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._get_edge_status_by_id = CoroutineMock(return_value=Exception)
        outage_monitor._start_edge_after_error_process = CoroutineMock()
        outage_monitor._monitoring_map_cache = [
            {'edge_full_id': {'host': 'mettel.velocloud.net', 'enterprise_id': 6, 'edge_id': 315}}
        ]

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['velocloud_instances_filter'] = {}
        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
                await outage_monitor._process_edge_after_error(edge_full_id, bruin_client_info_response_body)

        event_bus.rpc_request.assert_awaited_once_with("notification.slack.request", expected_slack_message, timeout=30)

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_non_whitelisted_edge_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._autoresolve_serials_whitelist = set()
        outage_monitor._get_last_down_events_for_edge = CoroutineMock()

        await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        outage_monitor._get_last_down_events_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_environment_different_from_production_test(self):
        serial_number = 'VC1234567'

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._get_last_down_events_for_edge = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        outage_monitor._get_last_down_events_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_prod_and_request_for_down_events_failed_test(self):
        serial_number = 'VC1234567'

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        edge_identifier = EdgeIdentifier(**edge_full_id)
        uuid_ = uuid()

        last_down_events_response_body = "Invalid parameters"
        last_down_events_response_status = 400

        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._get_last_down_events_for_edge = CoroutineMock(return_value={
            'body': last_down_events_response_body, 'status': last_down_events_response_status
        })

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
                await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        down_events_since = timedelta(seconds=config.MONITOR_CONFIG['autoresolve_down_events_seconds'])
        outage_monitor._get_last_down_events_for_edge.assert_awaited_once_with(edge_full_id, down_events_since)
        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'Error while retrieving down events for edge {edge_identifier}. '
                           f'Reason: Error {last_down_events_response_status} - {last_down_events_response_body}'
            },
            timeout=10
        )

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_prod_and_no_down_events_test(self):
        serial_number = 'VC1234567'

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            }
        }

        last_down_events_response_body = []
        last_down_events_response_status = 200

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._get_last_down_events_for_edge = CoroutineMock(return_value={
            'body': last_down_events_response_body, 'status': last_down_events_response_status
        })
        outage_monitor._get_outage_ticket_for_edge = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        down_events_since = timedelta(seconds=config.MONITOR_CONFIG['autoresolve_down_events_seconds'])
        outage_monitor._get_last_down_events_for_edge.assert_awaited_once_with(edge_full_id, down_events_since)
        outage_monitor._get_outage_ticket_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_prod_and_down_events_and_ticket_request_failed_test(self):
        serial_number = 'VC1234567'

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        edge_identifier = EdgeIdentifier(**edge_full_id)
        uuid_ = uuid()

        last_down_events_response_body = [
            {
                'event': 'LINK_ALIVE',
                'category': 'NETWORK',
                'eventTime': '2019-07-30 07:38:00+00:00',
                'message': 'GE2 alive'
            }
        ]
        last_down_events_response_status = 200

        outage_ticket_response_body = "Invalid parameters"
        outage_ticket_response_status = 400

        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._get_last_down_events_for_edge = CoroutineMock(return_value={
            'body': last_down_events_response_body, 'status': last_down_events_response_status
        })
        outage_monitor._get_outage_ticket_for_edge = CoroutineMock(return_value={
            'body': outage_ticket_response_body, 'status': outage_ticket_response_status
        })

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
                await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        down_events_since = timedelta(seconds=config.MONITOR_CONFIG['autoresolve_down_events_seconds'])
        outage_monitor._get_last_down_events_for_edge.assert_awaited_once_with(edge_full_id, down_events_since)
        outage_monitor._get_outage_ticket_for_edge.assert_awaited_once_with(edge_status)
        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'Error while retrieving outage ticket for edge {edge_identifier}. '
                           f'Reason: Error {outage_ticket_response_status} - {outage_ticket_response_body}'
            },
            timeout=10
        )

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_prod_and_and_down_events_and_no_ticket_found_test(self):
        serial_number = 'VC1234567'

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        uuid_ = uuid()

        last_down_events_response_body = [
            {
                'event': 'LINK_ALIVE',
                'category': 'NETWORK',
                'eventTime': '2019-07-30 07:38:00+00:00',
                'message': 'GE2 alive'
            }
        ]
        last_down_events_response_status = 200

        outage_ticket_response_body = None
        outage_ticket_response_status = 200

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._get_last_down_events_for_edge = CoroutineMock(return_value={
            'body': last_down_events_response_body, 'status': last_down_events_response_status
        })
        outage_monitor._get_outage_ticket_for_edge = CoroutineMock(return_value={
            'body': outage_ticket_response_body, 'status': outage_ticket_response_status
        })

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
                await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        down_events_since = timedelta(seconds=config.MONITOR_CONFIG['autoresolve_down_events_seconds'])
        outage_monitor._get_last_down_events_for_edge.assert_awaited_once_with(edge_full_id, down_events_since)

        outage_monitor._get_outage_ticket_for_edge.assert_awaited_once_with(edge_status)
        outage_repository._is_outage_ticket_auto_resolvable.assert_not_called()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_down_events_and_ticket_and_resolve_limit_exceeded_test(self):
        serial_number = 'VC1234567'

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        uuid_ = uuid()

        last_down_events_response_body = [
            {
                'event': 'LINK_ALIVE',
                'category': 'NETWORK',
                'eventTime': '2019-07-30 07:38:00+00:00',
                'message': 'GE2 alive'
            }
        ]
        last_down_events_response_status = 200

        outage_ticket_notes = [
            {
                "noteId": 68246614,
                "noteValue": "#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2021-01-02 10:18:16-05:00",
            },
            {
                "noteId": 68246615,
                "noteValue": "#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            },
            {
                "noteId": 68246616,
                "noteValue": "#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            },
        ]
        outage_ticket_response_body = {
            'ticketID': 12345,
            'ticketDetails': [
                {
                    "detailID": 2746937,
                    "detailValue": serial_number,
                    "detailStatus": "I",
                },
            ],
            'ticketNotes': outage_ticket_notes
        }
        outage_ticket_response_status = 200

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()

        outage_repository = Mock()
        outage_repository.is_outage_ticket_auto_resolvable = Mock(return_value=False)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._get_last_down_events_for_edge = CoroutineMock(return_value={
            'body': last_down_events_response_body, 'status': last_down_events_response_status
        })
        outage_monitor._get_outage_ticket_for_edge = CoroutineMock(return_value={
            'body': outage_ticket_response_body, 'status': outage_ticket_response_status
        })

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
                await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        down_events_since = timedelta(seconds=config.MONITOR_CONFIG['autoresolve_down_events_seconds'])
        outage_monitor._get_last_down_events_for_edge.assert_awaited_once_with(edge_full_id, down_events_since)

        outage_monitor._get_outage_ticket_for_edge.assert_awaited_once_with(edge_status)
        outage_repository.is_outage_ticket_auto_resolvable.assert_called_once_with(
            outage_ticket_notes, max_autoresolves=3
        )

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_ticket_already_resolved_test(self):
        serial_number = 'VC1234567'
        client_id = 12345

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        uuid_ = uuid()

        last_down_events_response_body = [
            {
                'event': 'LINK_ALIVE',
                'category': 'NETWORK',
                'eventTime': '2019-07-30 07:38:00+00:00',
                'message': 'GE2 alive'
            }
        ]
        last_down_events_response_status = 200

        outage_ticket_id = 12345
        outage_ticket_detail_id = 2746937
        outage_ticket_detail = {
            "detailID": outage_ticket_detail_id,
            "detailValue": serial_number,
            "detailStatus": "R",
        }
        outage_ticket_notes = [
            {
                "noteId": 68246614,
                "noteValue": "#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2021-01-02 10:18:16-05:00",
            },
            {
                "noteId": 68246615,
                "noteValue": "#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            },
        ]
        outage_ticket_response_body = {
            'ticketID': outage_ticket_id,
            'ticketDetails': [outage_ticket_detail],
            'ticketNotes': outage_ticket_notes,
        }
        outage_ticket_response_status = 200

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()

        outage_repository = Mock()
        outage_repository.is_outage_ticket_auto_resolvable = Mock(return_value=True)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._get_last_down_events_for_edge = CoroutineMock(return_value={
            'body': last_down_events_response_body, 'status': last_down_events_response_status
        })
        outage_monitor._get_outage_ticket_for_edge = CoroutineMock(return_value={
            'body': outage_ticket_response_body, 'status': outage_ticket_response_status
        })
        outage_monitor._is_detail_resolved = Mock(return_value=True)
        outage_monitor._resolve_outage_ticket = CoroutineMock()
        outage_monitor._append_autoresolve_note_to_ticket = CoroutineMock()
        outage_monitor._notify_successful_autoresolve = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
                await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        outage_monitor._resolve_outage_ticket.assert_not_awaited()
        outage_monitor._append_autoresolve_note_to_ticket.assert_not_awaited()
        outage_monitor._notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_all_conditions_met_test(self):
        serial_number = 'VC1234567'
        client_id = 12345

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        uuid_ = uuid()

        last_down_events_response_body = [
            {
                'event': 'LINK_ALIVE',
                'category': 'NETWORK',
                'eventTime': '2019-07-30 07:38:00+00:00',
                'message': 'GE2 alive'
            }
        ]
        last_down_events_response_status = 200

        outage_ticket_id = 12345
        outage_ticket_detail_id = 2746937
        outage_ticket_detail = {
            "detailID": outage_ticket_detail_id,
            "detailValue": serial_number,
            "detailStatus": "I",
        }
        outage_ticket_notes = [
            {
                "noteId": 68246614,
                "noteValue": "#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2021-01-02 10:18:16-05:00",
            },
            {
                "noteId": 68246615,
                "noteValue": "#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            },
        ]
        outage_ticket_response_body = {
            'ticketID': outage_ticket_id,
            'ticketDetails': [outage_ticket_detail],
            'ticketNotes': outage_ticket_notes,
        }
        outage_ticket_response_status = 200

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()

        outage_repository = Mock()
        outage_repository.is_outage_ticket_auto_resolvable = Mock(return_value=True)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._get_last_down_events_for_edge = CoroutineMock(return_value={
            'body': last_down_events_response_body, 'status': last_down_events_response_status
        })
        outage_monitor._get_outage_ticket_for_edge = CoroutineMock(return_value={
            'body': outage_ticket_response_body, 'status': outage_ticket_response_status
        })
        outage_monitor._is_detail_resolved = Mock(return_value=False)
        outage_monitor._resolve_outage_ticket = CoroutineMock()
        outage_monitor._append_autoresolve_note_to_ticket = CoroutineMock()
        outage_monitor._notify_successful_autoresolve = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
                await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        down_events_since = timedelta(seconds=config.MONITOR_CONFIG['autoresolve_down_events_seconds'])
        outage_monitor._get_last_down_events_for_edge.assert_awaited_once_with(edge_full_id, down_events_since)

        outage_monitor._get_outage_ticket_for_edge.assert_awaited_once_with(edge_status)
        outage_repository.is_outage_ticket_auto_resolvable.assert_called_once_with(
            outage_ticket_notes, max_autoresolves=3
        )

        outage_monitor._resolve_outage_ticket.assert_awaited_once_with(outage_ticket_id, outage_ticket_detail_id)
        outage_monitor._append_autoresolve_note_to_ticket.assert_awaited_once_with(outage_ticket_id, serial_number)
        outage_monitor._notify_successful_autoresolve.assert_awaited_once_with(outage_ticket_id, client_id)

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
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=outage_ticket)
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        uuid_ = uuid()
        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            outage_ticket_result = await outage_monitor._get_outage_ticket_for_edge(edge_status)

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
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=outage_ticket)
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        uuid_ = uuid()
        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            outage_ticket_result = await outage_monitor._get_outage_ticket_for_edge(
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

    @pytest.mark.asyncio
    async def get_last_down_events_for_edge_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_events = [
            {
                'event': 'LINK_ALIVE',
                'category': 'NETWORK',
                'eventTime': '2019-07-30 07:38:00+00:00',
                'message': 'GE2 alive'
            }
        ]
        rpc_response = {'body': edge_events, 'status': 200}

        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=rpc_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        seconds_ago_for_down_events_lookup = timedelta(config.MONITOR_CONFIG['autoresolve_down_events_seconds'])

        uuid_ = uuid()
        current_datetime = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
                    result = await outage_monitor._get_last_down_events_for_edge(
                        edge_full_id, since=seconds_ago_for_down_events_lookup
                    )

        event_bus.rpc_request.assert_awaited_once_with(
            "alert.request.event.edge",
            {
                'request_id': uuid_,
                'body': {
                    'edge': edge_full_id,
                    'start_date': current_datetime - seconds_ago_for_down_events_lookup,
                    'end_date': current_datetime,
                    'filter': ['EDGE_DOWN', 'LINK_DEAD'],
                },
            },
            timeout=180,
        )
        assert result == rpc_response

    @pytest.mark.asyncio
    async def resolve_outage_ticket_test(self):
        ticket_id = 12345
        detail_id = 67890

        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        uuid_ = uuid()
        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            await outage_monitor._resolve_outage_ticket(ticket_id, detail_id)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.status.resolve",
            {
                'request_id': uuid_,
                'body': {
                    'ticket_id': ticket_id,
                    'detail_id': detail_id,
                },
            },
            timeout=15,
        )

    @pytest.mark.asyncio
    async def append_autoresolve_note_to_ticket_test(self):
        ticket_id = 12345
        serial_number = 'VC1234567'

        current_datetime = datetime.now()
        autoresolve_note = (
            f'#*Automation Engine*#\nAuto-resolving detail for serial: {serial_number}\nTimeStamp: '
            f'{current_datetime + timedelta(seconds=1)}'
        )

        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        uuid_ = uuid()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
                    await outage_monitor._append_autoresolve_note_to_ticket(ticket_id, serial_number)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.note.append.request",
            {
                'request_id': uuid_,
                'body': {
                    'ticket_id': ticket_id,
                    'note': autoresolve_note,
                },
            },
            timeout=15,
        )

    @pytest.mark.asyncio
    async def notify_successful_autoresolve_test(self):
        ticket_id = 12345
        bruin_client_id = 67890

        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        uuid_ = uuid()
        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            await outage_monitor._notify_successful_autoresolve(ticket_id, bruin_client_id)

        autoresolve_slack_message = (
            f'Ticket {ticket_id} was autoresolved in {config.TRIAGE_CONFIG["environment"].upper()} environment. '
            f'Details at https://app.bruin.com/helpdesk?clientId={bruin_client_id}&ticketId={ticket_id}'
        )

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': autoresolve_slack_message,
            },
            timeout=10,
        )

    def get_first_element_matching_with_match_test(self):
        payload = range(0, 11)

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = OutageMonitor._get_first_element_matching(iterable=payload, condition=cond)
        expected = 5

        assert result == expected

    def get_first_element_matching_with_no_match_test(self):
        payload = [0] * 10
        fallback_value = 42

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = OutageMonitor._get_first_element_matching(iterable=payload, condition=cond, fallback=fallback_value)

        assert result == fallback_value

    @pytest.mark.asyncio
    async def get_edges_for_monitoring_test(self):
        uuid_ = uuid()
        edge_list_response = {
            'request_id': uuid_,
            'body': [
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1},
            ],
            'status': 200,
        }

        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=edge_list_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            result = await outage_monitor._get_edges_for_monitoring()

        event_bus.rpc_request.assert_awaited_once_with(
            "edge.list.request",
            {
                'request_id': uuid_,
                'body': {
                    'filter': config.MONITOR_CONFIG['velocloud_instances_filter']
                }
            },
            timeout=300,
        )
        assert result == edge_list_response

    @pytest.mark.asyncio
    async def recheck_edge_for_ticket_creation_with_no_outage_detected_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

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
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id, bruin_client_info)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        outage_monitor._run_ticket_autoresolve_for_edge.assert_awaited_once_with(edge_full_id, edge_status_data)

    @pytest.mark.asyncio
    async def recheck_edge_for_ticket_creation_with_outage_detected_and_no_production_environment_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

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
            await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id, bruin_client_info)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        outage_monitor._create_outage_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edge_for_ticket_creation_with_status_200_response_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

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
            await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id, bruin_client_info)

        outage_monitor._get_edge_status_by_id.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        outage_monitor._create_outage_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edge_with_outage_detected_and_production_env_and_failing_ticket_creation_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_identifier = EdgeIdentifier(**edge_full_id)
        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

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
                await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id, bruin_client_info)

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
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

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

        edge_status_data_with_bruin_client_info = {
            **edge_status_data,
            'bruin_client_info': bruin_client_info,
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
        outage_monitor._append_triage_note_to_new_ticket = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
                await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id, bruin_client_info)

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
        outage_monitor._append_triage_note_to_new_ticket.assert_awaited_once_with(
            outage_ticket_creation_body, edge_full_id, edge_status_data_with_bruin_client_info
        )

    @pytest.mark.asyncio
    async def recheck_edge_with_outage_detected_and_production_env_and_ticket_creation_returning_status_409_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        client_id = 12345
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

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
                await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id, bruin_client_info)

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
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

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
                await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id, bruin_client_info)

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
    async def append_triage_note_to_new_ticket_test(self):
        ticket_id = 12345

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        serial_number = 'VC1234567'
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            }
        }

        tickets = [
            {
                'ticket_id': ticket_id,
                'ticket_detail': {
                    'detailValue': serial_number,
                }
            }
        ]

        edges_data_by_serial = {
            serial_number: {
                'edge_id': edge_full_id,
                'edge_status': edge_status,
            }
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        outage_monitor._process_tickets_without_triage = CoroutineMock()

        await outage_monitor._append_triage_note_to_new_ticket(ticket_id, edge_full_id, edge_status)

        outage_monitor._process_tickets_without_triage.assert_awaited_once_with(tickets, edges_data_by_serial)

    @pytest.mark.asyncio
    async def append_triage_note_to_new_ticket_with_response_status_error_test(self):
        ticket_id = 12345

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        serial_number = 'VC1234567'
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            }
        }

        tickets = [
            {
                'ticket_id': ticket_id,
                'ticket_detail': {
                    'detailValue': serial_number,
                }
            }
        ]

        edges_data_by_serial = {
            serial_number: {
                'edge_id': edge_full_id,
                'edge_status': edge_status,
            }
        }

        bruin_client_id = 9994

        uuid_ = uuid()
        config = testconfig
        slack_message = \
            (f'Triage appended to ticket {ticket_id} in '
             f'{config.TRIAGE_CONFIG["environment"].upper()} environment. Details at '
             f'https://app.bruin.com/helpdesk?clientId={bruin_client_id}&ticketId={ticket_id}')
        slack_msg = {
            'request_id': uuid_,
            'body': (
                f'Outage ticket {ticket_id} reopened. Ticket details at '
                f'https://app.bruin.com/helpdesk?clientId={bruin_client_id}&ticketId={ticket_id}.')
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[
            slack_msg
        ])
        scheduler = Mock()
        logger = Mock()

        outage_repository = Mock()

        config.TRIAGE_CONFIG['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)
        # outage_monitor._process_tickets_without_triage = CoroutineMock()
        outage_monitor._get_last_events_for_edge = CoroutineMock(return_value={
            'status': 200,
            'body': [{'eventTime': '2020-01-01 00:00:000'}]
        })
        outage_monitor._gather_relevant_data_for_first_triage_note = CoroutineMock(return_value=None)
        outage_monitor._append_note_to_ticket = CoroutineMock(return_value={'status': 400, 'body': 'error'})
        outage_monitor._transform_relevant_data_into_ticket_note = Mock()
        # outage_monitor._notify_http_error_when_appending_note_to_ticket = CoroutineMock()
        outage_monitor._notify_failing_rpc_request_for_appending_ticket_note = CoroutineMock()

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            await outage_monitor._append_triage_note_to_new_ticket(ticket_id, edge_full_id, edge_status)

        # outage_monitor._process_tickets_without_triage.assert_awaited_once_with(tickets, edges_data_by_serial)
        # outage_monitor._notify_http_error_when_appending_note_to_ticket.assert_called_once()
        event_bus.rpc_request.assert_has_awaits([
            call(
                "notification.slack.request",
                {
                    'request_id': uuid_,
                    'message': (
                        f'Error while appending note to ticket {ticket_id} in '
                        f'{config.TRIAGE_CONFIG["environment"].upper()} environment: Error 400 - error')
                },
                timeout=10
            )
        ])

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
            'enterprise_name': f'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            },
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
            'bruin_client_info': {
                'client_id': bruin_client_id,
                'client_name': 'METTEL/NEW YORK',
            },
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
            'enterprise_name': f'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            },
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
            'enterprise_name': f'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            },
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
            'enterprise_name': f'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            },
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
            'bruin_client_info': {
                'client_id': bruin_client_id,
                'client_name': 'METTEL/NEW YORK',
            },
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
        bruin_client_id = 12345
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC9876'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_id}|',
            'bruin_client_info': {
                'client_id': bruin_client_id,
                'client_name': 'METTEL/NEW YORK',
            },
        }
        management_status_rpc = {"body": "balblaba",
                                 "status": 200}
        uuid_ = uuid()
        management_request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "status": "A",
                "service_number": 'VC9876'
            }}
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        event_bus.rpc_request = CoroutineMock(return_value=management_status_rpc)

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            management_status = await outage_monitor._get_management_status(edge_status)

        event_bus.rpc_request.assert_awaited_once_with("bruin.inventory.management.status",
                                                       management_request, timeout=30)
        assert management_status == management_status_rpc

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
        config = testconfig
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=bruin_client_info_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository)

        with patch.object(outage_monitoring_module, 'uuid', return_value=uuid_):
            result = await outage_monitor._get_bruin_client_info_by_serial(serial_number)

        event_bus.rpc_request.assert_awaited_once_with(
            'bruin.customer.get.info',
            {'request_id': uuid_, 'body': {'service_number': serial_number}},
            timeout=30,
        )
        assert result == bruin_client_info_response

    def is_detail_resolved_test(self):
        ticket_detail = {
            "detailID": 12345,
            "detailValue": 'VC1234567',
            "detailStatus": "I",
        }
        result = OutageMonitor._is_detail_resolved(ticket_detail)
        assert result is False

        ticket_detail = {
            "detailID": 12345,
            "detailValue": 'VC1234567',
            "detailStatus": "R",
        }
        result = OutageMonitor._is_detail_resolved(ticket_detail)
        assert result is True
