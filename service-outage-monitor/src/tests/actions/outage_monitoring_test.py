import json

from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from asynctest import CoroutineMock
from dateutil.parser import parse
from shortuuid import uuid

from application.actions import outage_monitoring as outage_monitoring_module
from application.actions.outage_monitoring import OutageMonitor
from application.repositories import EdgeIdentifier
from config import testconfig


class TestServiceOutageMonitor:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        assert outage_monitor._event_bus is event_bus
        assert outage_monitor._logger is logger
        assert outage_monitor._scheduler is scheduler
        assert outage_monitor._config is config
        assert outage_monitor._outage_repository is outage_repository
        assert outage_monitor._bruin_repository is bruin_repository
        assert outage_monitor._velocloud_repository is velocloud_repository
        assert outage_monitor._notifications_repository is notifications_repository
        assert outage_monitor._triage_repository is triage_repository
        assert outage_monitor._metrics_repository is metrics_repository

        assert outage_monitor._autoresolve_serials_whitelist == set()

    @pytest.mark.asyncio
    async def start_service_outage_monitoring_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

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
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

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
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

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
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

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
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

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
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

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
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_outage_monitoring = CoroutineMock()

        edge_full_id = {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

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
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        velocloud_repository = Mock()
        metrics_repository = Mock()

        edge_full_id = {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

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
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        velocloud_repository = Mock()
        metrics_repository = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        edge_full_id = {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
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
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_outage_monitoring = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._start_build_cache_job = CoroutineMock()
        outage_monitor._monitoring_map_cache = [
            {'edge_full_id': {'host': 'mettel.velocloud.net', 'enterprise_id': 6, 'edge_id': 315}}
        ]

        await outage_monitor._outage_monitoring_process()

        velocloud_repository.get_edges_for_outage_monitoring.assert_not_awaited()
        outage_monitor._start_build_cache_job.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_host_with_cache_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_outage_monitoring = CoroutineMock()
        velocloud_repository.get_last_edge_events = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
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

        velocloud_repository.get_edges_for_outage_monitoring.assert_not_awaited()
        velocloud_repository.get_last_edge_events.assert_not_awaited()
        outage_monitor._start_build_cache_job.assert_not_awaited()
        outage_monitor._process_edge.assert_awaited_once()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_exception_test(self):
        edges_to_monitor_response = {
            'request_id': 's8ixRY7ShDpYpZzJ34zk5P',
            'body': [{'host': 'mettel.velocloud.net', 'enterprise_id': 6, 'edge_id': 315}],
            'status': 200
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_outage_monitoring = CoroutineMock(return_value=edges_to_monitor_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._start_build_cache_job = CoroutineMock()

        await outage_monitor._outage_monitoring_process()

        velocloud_repository.get_edges_for_outage_monitoring.assert_awaited_once()
        outage_monitor._start_build_cache_job.assert_awaited_once()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_failure_in_rpc_request_for_retrieval_of_edges_under_monitoring_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_outage_monitoring = CoroutineMock(side_effect=Exception)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._start_build_cache_job = CoroutineMock()

        with pytest.raises(Exception):
            await outage_monitor._outage_monitoring_process()

        velocloud_repository.get_edges_for_outage_monitoring.assert_awaited_once()
        outage_monitor._start_build_cache_job.assert_not_awaited()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_retrieval_of_edges_under_monitoring_returning_non_2xx_status_test(self):
        edge_list_response_body = "Got internal error from Velocloud"
        edge_list_response_status = 500
        edge_list_response = {
            'request_id': uuid(),
            'body': edge_list_response_body,
            'status': edge_list_response_status,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_outage_monitoring = CoroutineMock(return_value=edge_list_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._add_edge_to_temp_cache = CoroutineMock()
        outage_monitor._start_build_cache_job = CoroutineMock()

        await outage_monitor._outage_monitoring_process()

        velocloud_repository.get_edges_for_outage_monitoring.assert_awaited_once()
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
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_outage_monitoring = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._add_edge_to_temp_cache = CoroutineMock()
        outage_monitor._start_build_cache_job = CoroutineMock()

        await outage_monitor._outage_monitoring_process()

        velocloud_repository.get_edges_for_outage_monitoring.assert_awaited_once()
        velocloud_repository.get_edge_status.assert_not_awaited()
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
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_outage_monitoring = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['blacklisted_edges'] = [edge_full_id]

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._add_edge_to_temp_cache = CoroutineMock()
        outage_monitor._start_build_cache_job = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._outage_monitoring_process()

        velocloud_repository.get_edges_for_outage_monitoring.assert_awaited_once()
        velocloud_repository.get_edge_status.assert_not_awaited()
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
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_outage_monitoring = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._add_edge_to_temp_cache = CoroutineMock()
        outage_monitor._start_build_cache_job = CoroutineMock()

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._outage_monitoring_process()

        velocloud_repository.get_edges_for_outage_monitoring.assert_awaited_once()
        velocloud_repository.get_edge_status.assert_not_awaited()
        outage_monitor._add_edge_to_temp_cache.assert_awaited_once()
        outage_monitor._start_build_cache_job.assert_awaited_once()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_retrieval_of_edge_status_returning_non_2XX_status_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status_response_body = 'Got internal error from Velocloud'
        edge_status_response_status = 500
        edge_status_response = {
            'body': edge_status_response_body,
            'status': edge_status_response_status,
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        scheduler = Mock()
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_management_status = CoroutineMock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        bruin_repository.get_management_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_null_serial_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': {
                    'edges': {
                        'edgeState': 'CONNECTED',
                        'serialNumber': None,
                        'lastContact': '2020-07-05T10:13:06.000Z',
                    },
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
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_management_status = CoroutineMock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        bruin_repository.get_management_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_invalid_last_contact_moment_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': {
                    'edges': {
                        'edgeState': 'CONNECTED',
                        'serialNumber': 'VC1234567',
                        'lastContact': '0000-00-00 00:00:00',
                    },
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
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_management_status = CoroutineMock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._is_valid_last_contact_moment = Mock(return_value=False)

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        bruin_repository.get_management_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_edge_last_contacted_long_time_ago_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_status_response = {
            'body': {
                'edge_id': edge_full_id,
                'edge_info': {
                    'edges': {
                        'edgeState': 'CONNECTED',
                        'serialNumber': 'VC1234567',
                        'lastContact': '2020-07-05T10:13:06.000Z',
                    },
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
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_management_status = CoroutineMock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._is_valid_last_contact_moment = Mock(return_value=True)
        outage_monitor._was_edge_last_contacted_recently = Mock(return_value=False)

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        bruin_repository.get_management_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_retrieval_of_bruin_client_info_returning_non_2xx_status_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_status_data = {
            'edges': {
                'edgeState': 'CONNECTED',
                'serialNumber': edge_serial,
                'lastContact': '2020-07-05T10:13:06.000Z',
            },
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

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_client_info = CoroutineMock(return_value=bruin_client_info_response)
        bruin_repository.get_management_status = CoroutineMock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._is_valid_last_contact_moment = Mock(return_value=True)
        outage_monitor._was_edge_last_contacted_recently = Mock(return_value=True)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        bruin_repository.get_client_info.assert_awaited_once_with(edge_serial)
        bruin_repository.get_management_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_bruin_client_info_having_null_client_id_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_status_data = {
            'edges': {
                'edgeState': 'CONNECTED',
                'serialNumber': edge_serial,
                'lastContact': '2020-07-05T10:13:06.000Z',
            },
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

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_client_info = CoroutineMock(return_value=bruin_client_info_response)
        bruin_repository.get_management_status = CoroutineMock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._is_valid_last_contact_moment = Mock(return_value=True)
        outage_monitor._was_edge_last_contacted_recently = Mock(return_value=True)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        bruin_repository.get_client_info.assert_awaited_once_with(edge_serial)
        bruin_repository.get_management_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_retrieval_of_management_status_returning_non_2XX_status_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_data = {
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': edge_serial,
                'lastContact': '2020-07-05T10:13:06.000Z',
            },
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

        client_id = 9994
        bruin_client_info_response_body = {
            'client_id': client_id,
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

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        scheduler = Mock()
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_client_info = CoroutineMock(return_value=bruin_client_info_response)
        bruin_repository.get_management_status = CoroutineMock(return_value=management_status_response)
        bruin_repository.is_management_status_active = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._is_valid_last_contact_moment = Mock(return_value=True)
        outage_monitor._was_edge_last_contacted_recently = Mock(return_value=True)

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        bruin_repository.get_client_info.assert_awaited_once_with(edge_serial)
        bruin_repository.get_management_status.assert_awaited_once_with(client_id, edge_serial)
        bruin_repository.is_management_status_active.assert_not_called()

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_management_status_inactive_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_data = {
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': edge_serial,
                'lastContact': '2020-07-05T10:13:06.000Z',
            },
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

        client_id = 9994
        bruin_client_info_response_body = {
            'client_id': client_id,
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

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        scheduler = Mock()
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_client_info = CoroutineMock(return_value=bruin_client_info_response)
        bruin_repository.get_management_status = CoroutineMock(return_value=management_status_response)
        bruin_repository.is_management_status_active = Mock(return_value=False)

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._is_valid_last_contact_moment = Mock(return_value=True)
        outage_monitor._was_edge_last_contacted_recently = Mock(return_value=True)

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        bruin_repository.get_client_info.assert_awaited_once_with(edge_serial)
        bruin_repository.get_management_status.assert_awaited_once_with(client_id, edge_serial)
        bruin_repository.is_management_status_active.assert_called_once_with(management_status_response_body)

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_management_status_active_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_data = {
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': edge_serial,
                'lastContact': '2020-07-05T10:13:06.000Z',
            },
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
        client_id = 9994

        bruin_client_info_response_body = {
            'client_id': client_id,
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
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_client_info = CoroutineMock(return_value=bruin_client_info_response)
        bruin_repository.get_management_status = CoroutineMock(return_value=management_status_response)
        bruin_repository.is_management_status_active = Mock(return_value=True)

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._is_valid_last_contact_moment = Mock(return_value=True)
        outage_monitor._was_edge_last_contacted_recently = Mock(return_value=True)

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        bruin_repository.get_client_info.assert_awaited_once_with(edge_serial)
        bruin_repository.get_management_status.assert_awaited_once_with(client_id, edge_serial)
        bruin_repository.is_management_status_active.assert_called_once_with(management_status_response_body)
        assert expected_outcome in outage_monitor._temp_monitoring_map

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_side_effects_over_autoresolve_whitelist_with_autoresolve_filter_test(self):
        edge_full_id = {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_data = {
            'edges': {
                'edgeState': 'OFFLINE',
                'serialNumber': edge_serial,
                'lastContact': '2020-07-05T10:13:06.000Z',
            },
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

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['velocloud_instances_filter'] = {
            "mettel.velocloud.net": [],
            "metvco02.mettel.net": [],
        }
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        scheduler = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_client_info = CoroutineMock(return_value=bruin_client_info_response)
        bruin_repository.get_management_status = CoroutineMock(return_value=management_status_response)
        bruin_repository.is_management_status_active = Mock(return_value=True)

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._is_valid_last_contact_moment = Mock(return_value=True)
        outage_monitor._was_edge_last_contacted_recently = Mock(return_value=True)

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        assert outage_monitor._temp_autoresolve_serials_whitelist == {edge_serial}

    @pytest.mark.asyncio
    async def add_edge_to_temp_cache_with_side_effects_over_autoresolve_whitelist_without_autoresolve_filter_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        edge_serial = 'VC1234567'
        edge_data = {
            'edges': {
                'edgeState': 'CONNECTED',
                'serialNumber': edge_serial,
                'lastContact': '2020-07-05T10:13:06.000Z',
            },
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

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        scheduler = Mock()
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_client_info = CoroutineMock(return_value=bruin_client_info_response)
        bruin_repository.get_management_status = CoroutineMock(return_value=management_status_response)
        bruin_repository.is_management_status_active = Mock(return_value=True)

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._is_valid_last_contact_moment = Mock(return_value=True)
        outage_monitor._was_edge_last_contacted_recently = Mock(return_value=True)

        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['velocloud_instances_filter'] = {}

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._add_edge_to_temp_cache(edge_full_id)

        assert outage_monitor._temp_autoresolve_serials_whitelist == {edge_serial}

    @pytest.mark.asyncio
    async def process_edge_with_retrieval_of_edge_status_returning_non_2XX_status_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        edge_status_response = {
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        logger = Mock()
        config = testconfig
        scheduler = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        await outage_monitor._process_edge(edge_full_id, bruin_client_info_response_body)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
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
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=False)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._process_edge(edge_full_id, bruin_client_info_response_body)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        outage_monitor._run_ticket_autoresolve_for_edge.assert_awaited_once_with(
            edge_full_id, edge_data_with_bruin_info
        )

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
        bruin_client_info_response = {
            "body": bruin_client_info_response_body,
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
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_client_info = CoroutineMock(return_value=bruin_client_info_response)
        bruin_repository.get_management_status = CoroutineMock(return_value=management_status_response)
        bruin_repository.is_management_status_active = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=is_there_an_outage)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

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

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
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
        notifications_repository = Mock()
        triage_repository = Mock()
        bruin_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._process_edge(edge_full_id, bruin_client_info_response_body)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
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
    async def process_edge_exception_test(self):
        edge_full_id = {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        triage_repository = Mock()
        bruin_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=Exception)

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['velocloud_instances_filter'] = {}

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._process_edge(edge_full_id, bruin_client_info_response_body)

        outage_repository.is_there_an_outage.assert_not_called()

    @pytest.mark.asyncio
    async def process_edge_after_error_with_retrieval_of_edge_status_returning_non_2xx_status_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        edge_status_response_body = 'Got internal error from Velocloud'
        edge_status_response_status = 500
        edge_status_response = {
            'body': edge_status_response_body,
            'status': edge_status_response_status,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        triage_repository = Mock()
        bruin_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        await outage_monitor._process_edge_after_error(edge_full_id, bruin_client_info_response_body)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
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
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=False)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._process_edge_after_error(edge_full_id, bruin_client_info_response_body)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        outage_monitor._run_ticket_autoresolve_for_edge.assert_awaited_once_with(
            edge_full_id, edge_data_with_bruin_info
        )

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
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=is_there_an_outage)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

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

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
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
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._process_edge_after_error(edge_full_id, bruin_client_info_response_body)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
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
        bruin_client_info_response_body = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        expected_slack_message = (
            f"Maximum retries happened while trying to process edge {edge_full_id} with "
            f"serial {edge_serial}"
        )
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock(side_effect=Exception)
        outage_monitor._monitoring_map_cache = [
            {'edge_full_id': edge_full_id,
             'edge_data': edge_status_data}
        ]

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['velocloud_instances_filter'] = {}

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._process_edge_after_error(edge_full_id, bruin_client_info_response_body)

        notifications_repository.send_slack_message.assert_awaited_once_with(expected_slack_message)

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
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_down_edge_events = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._autoresolve_serials_whitelist = set()

        await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        velocloud_repository.get_last_down_edge_events.assert_not_awaited()

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
        bruin_repository = Mock()
        bruin_repository.get_outage_ticket_details_by_service_number = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_down_edge_events = CoroutineMock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        bruin_repository.resolve_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_ticket_older_than_config_age_test(self):
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
        bruin_repository = Mock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.get_outage_ticket_details_by_service_number = CoroutineMock()
        bruin_repository.get_ticket_info = CoroutineMock()

        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._can_autoresolve_ticket_by_age = Mock(return_value=False)

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
                await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        bruin_repository.resolve_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_prod_and_ticket_too_old_test(self):
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

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.get_ticket_info = CoroutineMock()
        bruin_repository.get_outage_ticket_details_by_service_number = CoroutineMock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._can_autoresolve_ticket_by_age = Mock(return_value=False)

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
                await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        bruin_repository.resolve_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_retrieval_of_ticket_returning_non_2xx_status_test(self):
        serial_number = 'VC1234567'
        client_id = 9994

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        outage_ticket_response = {
            'body': "Invalid parameters",
            'status': 400,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_down_edge_events = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_outage_ticket_details_by_service_number = CoroutineMock(
            return_value=outage_ticket_response
        )
        bruin_repository.get_ticket_info = CoroutineMock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
                await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        bruin_repository.get_outage_ticket_details_by_service_number.assert_awaited_once_with(client_id, serial_number)
        outage_repository.is_outage_ticket_auto_resolvable.assert_not_called()
        bruin_repository.get_ticket_info.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_prod_and_no_ticket_found_test(self):
        serial_number = 'VC1234567'
        client_id = 9994

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        outage_ticket_response = {
            'body': None,
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_outage_ticket_details_by_service_number = CoroutineMock(
            return_value=outage_ticket_response
        )

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
                await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        bruin_repository.get_outage_ticket_details_by_service_number.assert_awaited_once_with(client_id, serial_number)
        outage_repository.is_outage_ticket_auto_resolvable.assert_not_called()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_fresh_enough_ticket_and_resolve_limit_exceeded_test(self):
        serial_number = 'VC1234567'
        client_id = 9994

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'METTEL/NEW YORK',
            },
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
            {
                "noteId": 68246616,
                "noteValue": "#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            },
        ]
        outage_ticket_response = {
            'body': {
                'ticketID': 12345,
                'ticketDetails': [
                    {
                        "detailID": 2746937,
                        "detailValue": serial_number,
                        "detailStatus": "I",
                    },
                ],
                'ticketNotes': outage_ticket_notes
            },
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_info = CoroutineMock()
        bruin_repository.get_outage_ticket_details_by_service_number = CoroutineMock(
            return_value=outage_ticket_response
        )

        outage_repository = Mock()
        outage_repository.is_outage_ticket_auto_resolvable = Mock(return_value=False)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._can_autoresolve_ticket_by_age = Mock(return_value=True)

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
                await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        bruin_repository.get_outage_ticket_details_by_service_number.assert_awaited_once_with(client_id, serial_number)
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
        outage_ticket_response = {
            'body': {
                'ticketID': outage_ticket_id,
                'ticketDetails': [outage_ticket_detail],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_info = CoroutineMock()
        bruin_repository.get_outage_ticket_details_by_service_number = CoroutineMock(
            return_value=outage_ticket_response
        )
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_outage_ticket_auto_resolvable = Mock(return_value=True)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._is_detail_resolved = Mock(return_value=True)
        outage_monitor._notify_successful_autoresolve = CoroutineMock()
        outage_monitor._can_autoresolve_ticket_by_age = Mock(return_value=True)

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        outage_monitor._notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_resolve_outage_return_non_2xx_status_test(self):
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

        outage_ticket_response = {
            'body': {
                'ticketID': outage_ticket_id,
                'ticketDetails': [outage_ticket_detail],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        resolve_outage_ticket_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_info = CoroutineMock()
        bruin_repository.get_outage_ticket_details_by_service_number = CoroutineMock(
            return_value=outage_ticket_response
        )
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_outage_ticket_response)
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_outage_ticket_auto_resolvable = Mock(return_value=True)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._is_detail_resolved = Mock(return_value=False)
        outage_monitor._notify_successful_autoresolve = CoroutineMock()
        outage_monitor._can_autoresolve_ticket_by_age = Mock(return_value=True)

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
                await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        bruin_repository.get_outage_ticket_details_by_service_number.assert_awaited_once_with(client_id, serial_number)
        outage_repository.is_outage_ticket_auto_resolvable.assert_called_once_with(
            outage_ticket_notes, max_autoresolves=3
        )

        bruin_repository.resolve_ticket.assert_awaited_once_with(outage_ticket_id, outage_ticket_detail_id)
        bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
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

        # createDate here won't be used to check age, is an example of date format
        outage_ticket_info = {'clientID': 9999, 'clientName': 'CustomerCorp',
                              'ticketID': 1919, 'category': 'SD-WAN', 'topic': 'Service Outage Trouble',
                              'referenceTicketNumber': 0, 'ticketStatus': 'In-Progress',
                              'address': {'address': '9493 Some Place', 'city': 'Sausalito',
                                          'state': 'IL', 'zip': '212122', 'country': 'USA'},
                              'createDate': '8/11/2020 4:37:34 PM', 'createdBy': 'Intelygenz Ai', 'creationNote': None,
                              'resolveDate': '', 'resolvedby': None, 'closeDate': None, 'closedBy': None,
                              'lastUpdate': None, 'updatedBy': None,
                              'mostRecentNote': '8/11/2020 8:37:54 PM Intelygenz Ai',
                              'nextScheduledDate': '8/25/2020 9:37:57 AM', 'flags': 'Frozen', 'severity': '2'}

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
        outage_ticket_response = {
            'body': {
                'ticketID': outage_ticket_id,
                'ticketDetails': [outage_ticket_detail],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }
        resolve_outage_ticket_response = {
            'body': 'ok',
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_info = CoroutineMock(return_value=outage_ticket_info)
        bruin_repository.get_outage_ticket_details_by_service_number = CoroutineMock(
            return_value=outage_ticket_response
        )
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_outage_ticket_response)
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_outage_ticket_auto_resolvable = Mock(return_value=True)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._notify_successful_autoresolve = CoroutineMock()
        outage_monitor._can_autoresolve_ticket_by_age = Mock(return_value=True)

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
                await outage_monitor._run_ticket_autoresolve_for_edge(edge_full_id, edge_status)

        bruin_repository.get_outage_ticket_details_by_service_number.assert_awaited_once_with(client_id, serial_number)
        outage_repository.is_outage_ticket_auto_resolvable.assert_called_once_with(
            outage_ticket_notes, max_autoresolves=3
        )
        bruin_repository.resolve_ticket.assert_awaited_once_with(outage_ticket_id, outage_ticket_detail_id)
        bruin_repository.append_autoresolve_note_to_ticket.assert_awaited_once_with(outage_ticket_id, serial_number)
        outage_monitor._notify_successful_autoresolve.assert_awaited_once_with(outage_ticket_id, client_id)

    @pytest.mark.asyncio
    async def notify_successful_autoresolve_test(self):
        ticket_id = 12345
        bruin_client_id = 67890

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()
        config = testconfig
        velocloud_repository = Mock()
        bruin_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        await outage_monitor._notify_successful_autoresolve(ticket_id, bruin_client_id)

        autoresolve_slack_message = (
            f'Ticket {ticket_id} was autoresolved in {config.TRIAGE_CONFIG["environment"].upper()} environment. '
            f'Details at https://app.bruin.com/helpdesk?clientId={bruin_client_id}&ticketId={ticket_id}'
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(autoresolve_slack_message)

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
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=outage_happened)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id, bruin_client_info)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
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
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id, bruin_client_info)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        bruin_repository.create_outage_ticket.assert_not_awaited()

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
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id, bruin_client_info)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        bruin_repository.create_outage_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edge_with_outage_detected_and_production_env_and_failing_ticket_creation_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

        serial_number = 'VC1234567'
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
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

        outage_ticket_creation_response = {
            'request_id': uuid(),
            'body': "Got internal error from Bruin",
            'status': 500,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=outage_ticket_creation_response)

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id, bruin_client_info)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, serial_number)

    @pytest.mark.asyncio
    async def recheck_edge_with_outage_detected_and_production_env_and_ticket_creation_returning_status_200_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_identifier = EdgeIdentifier(**edge_full_id)

        client_id = 12345
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

        serial_number = 'VC1234567'
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
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

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=outage_ticket_creation_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._append_triage_note = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id, bruin_client_info)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, serial_number)
        outage_monitor._append_triage_note.assert_awaited_once_with(
            outage_ticket_creation_body, edge_full_id, edge_status_data_with_bruin_client_info
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(
            f'Outage ticket created for faulty edge {edge_identifier}. Ticket '
            f'details at https://app.bruin.com/helpdesk?clientId={client_id}&'
            f'ticketId={outage_ticket_creation_body}.'
        )

    @pytest.mark.asyncio
    async def append_triage_note_with_retrieval_of_edge_events_returning_non_2xx_status_test(self):
        ticket_id = 12345
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        client_id = 11111
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'METTEL/NEW YORK',
            }
        }

        edge_events_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=edge_events_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._append_triage_note(ticket_id, edge_full_id, edge_status)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        triage_repository.build_triage_note.assert_not_called()

    @pytest.mark.asyncio
    async def append_triage_note_with_no_edge_events_test(self):
        ticket_id = 12345
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        client_id = 11111
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'METTEL/NEW YORK',
            }
        }

        edge_events_response = {
            'body': [],
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=edge_events_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._append_triage_note(ticket_id, edge_full_id, edge_status)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        triage_repository.build_triage_note.assert_not_called()

    @pytest.mark.asyncio
    async def append_triage_note_with_events_sorted_before_building_triage_note_test(self):
        ticket_id = 12345
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        client_id = 11111
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'METTEL/NEW YORK',
            }
        }

        event_1 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:30:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_2 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE1 is now DEAD'
        }
        event_3 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:40:00+00:00',
            'message': 'Link GE1 is no longer DEAD'
        }
        events = [event_1, event_2, event_3]
        events_sorted_by_event_time = [event_3, event_2, event_1]

        edge_events_response = {
            'body': events,
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=edge_events_response)

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
                await outage_monitor._append_triage_note(ticket_id, edge_full_id, edge_status)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        triage_repository.build_triage_note.assert_called_once_with(
            edge_full_id, edge_status, events_sorted_by_event_time
        )

    @pytest.mark.asyncio
    async def append_triage_note_with_dev_environment_test(self):
        ticket_id = 12345
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        client_id = 11111
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'METTEL/NEW YORK',
            }
        }

        event_1 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:30:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_2 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE1 is now DEAD'
        }
        event_3 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:40:00+00:00',
            'message': 'Link GE1 is no longer DEAD'
        }
        events = [event_1, event_2, event_3]
        events_sorted_by_event_time = [event_3, event_2, event_1]

        edge_events_response = {
            'body': events,
            'status': 200,
        }

        triage_note = 'This is a triage note'

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=edge_events_response)

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        triage_repository = Mock()
        triage_repository.build_triage_note = Mock(return_value=triage_note)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
                await outage_monitor._append_triage_note(ticket_id, edge_full_id, edge_status)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        triage_repository.build_triage_note.assert_called_once_with(
            edge_full_id, edge_status, events_sorted_by_event_time
        )
        notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository.append_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_triage_note_with_production_environment_test(self):
        ticket_id = 12345
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        client_id = 11111
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'METTEL/NEW YORK',
            }
        }

        event_1 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:30:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_2 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE1 is now DEAD'
        }
        event_3 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:40:00+00:00',
            'message': 'Link GE1 is no longer DEAD'
        }
        events = [event_1, event_2, event_3]
        events_sorted_by_event_time = [event_3, event_2, event_1]

        edge_events_response = {
            'body': events,
            'status': 200,
        }

        triage_note = 'This is a triage note'

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=edge_events_response)

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        triage_repository = Mock()
        triage_repository.build_triage_note = Mock(return_value=triage_note)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
                await outage_monitor._append_triage_note(ticket_id, edge_full_id, edge_status)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        triage_repository.build_triage_note.assert_called_once_with(
            edge_full_id, edge_status, events_sorted_by_event_time
        )
        notifications_repository.send_slack_message.assert_not_awaited()
        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, triage_note)

    @pytest.mark.asyncio
    async def recheck_edge_with_outage_detected_and_production_env_and_ticket_creation_returning_status_409_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        client_id = 12345
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

        serial_number = 'VC1234567'
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
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

        outage_ticket_creation_response = {
            'request_id': uuid(),
            'body': 12345,  # Ticket ID
            'status': 409,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=outage_ticket_creation_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id, bruin_client_info)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, serial_number)
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edge_with_outage_detected_and_production_env_and_ticket_creation_returning_status_471_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        client_id = 12345
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

        serial_number = 'VC1234567'
        edge_status_data = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': serial_number},
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

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value=edge_status_response)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=outage_ticket_creation_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(return_value=outage_happened)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._reopen_outage_ticket = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_edge_for_ticket_creation(edge_full_id, bruin_client_info)

        velocloud_repository.get_edge_status.assert_awaited_once_with(edge_full_id)
        outage_repository.is_there_an_outage.assert_called_once_with(edge_status_data)
        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, serial_number)
        outage_monitor._reopen_outage_ticket.assert_awaited_once_with(
            outage_ticket_creation_body, edge_status_data
        )

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
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_result)
        bruin_repository.open_ticket = CoroutineMock(return_value=reopen_ticket_result)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        await outage_monitor._reopen_outage_ticket(ticket_id, edge_status)

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        bruin_repository.open_ticket.assert_awaited_once_with(ticket_id, detail_id)
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
            'body': 'ok',
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_result)
        bruin_repository.open_ticket = CoroutineMock(return_value=reopen_ticket_result)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._post_note_in_outage_ticket = CoroutineMock()

        await outage_monitor._reopen_outage_ticket(ticket_id, edge_status)

        outage_monitor._post_note_in_outage_ticket.assert_called_once_with(ticket_id, edge_status)
        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        bruin_repository.open_ticket.assert_awaited_once_with(ticket_id, detail_id)
        notifications_repository.send_slack_message.assert_called_once_with(
            f'Outage ticket {ticket_id} reopened. Ticket details at '
            f'https://app.bruin.com/helpdesk?clientId={bruin_client_id}&ticketId={ticket_id}.'
        )

    @pytest.mark.asyncio
    async def post_note_in_outage_ticket_with_no_outage_causes_test(self):
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
        ticket_note_outage_causes = 'Outage causes: Could not determine causes.'

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.append_reopening_note_to_ticket = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._get_outage_causes = Mock(return_value=outage_causes)

        await outage_monitor._post_note_in_outage_ticket(ticket_id, edge_status)

        bruin_repository.append_reopening_note_to_ticket.assert_awaited_once_with(ticket_id, ticket_note_outage_causes)

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

        ticket_note_outage_causes = f'Outage causes: Edge was {edge_state}.'

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.append_reopening_note_to_ticket = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._get_outage_causes = Mock(return_value=outage_causes)

        await outage_monitor._post_note_in_outage_ticket(ticket_id, edge_status)

        bruin_repository.append_reopening_note_to_ticket.assert_awaited_once_with(ticket_id, ticket_note_outage_causes)

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

        ticket_note_outage_causes = (
            f'Outage causes: Link {link_1_interface} was {links_state}. Link {link_2_interface} was {links_state}.'
        )

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.append_reopening_note_to_ticket = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._get_outage_causes = Mock(return_value=outage_causes)

        await outage_monitor._post_note_in_outage_ticket(ticket_id, edge_status)

        bruin_repository.append_reopening_note_to_ticket.assert_awaited_once_with(ticket_id, ticket_note_outage_causes)

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
        ticket_note_outage_causes = (
            f'Outage causes: Edge was {edge_state}. '
            f'Link {link_1_interface} was {links_state}. Link {link_2_interface} was {links_state}.'
        )

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.append_reopening_note_to_ticket = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)
        outage_monitor._get_outage_causes = Mock(return_value=outage_causes)

        await outage_monitor._post_note_in_outage_ticket(ticket_id, edge_status)

        bruin_repository.append_reopening_note_to_ticket.assert_awaited_once_with(ticket_id, ticket_note_outage_causes)

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
        velocloud_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(side_effect=[False, True, True])
        outage_repository.is_faulty_link = Mock(side_effect=[False, False, True, True, False, True])

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, metrics_repository)

        result = outage_monitor._get_outage_causes(edge_status_1)
        assert result is None

        result = outage_monitor._get_outage_causes(edge_status_2)
        assert result == {'edge': 'OFFLINE', 'links': {'GE1': edge_2_link_ge1_state, 'GE2': edge_2_link_ge2_state}}

        result = outage_monitor._get_outage_causes(edge_status_3)
        assert result == {'edge': 'OFFLINE', 'links': {'GE2': edge_2_link_ge2_state}}

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

    def is_valid_last_contact_moment_test(self):
        last_contact_moment = '0000-00-00 00:00:00'
        result = OutageMonitor._is_valid_last_contact_moment(last_contact_moment)
        assert result is False

        last_contact_moment = '2020-07-05T10:13:06.000Z'
        result = OutageMonitor._is_valid_last_contact_moment(last_contact_moment)
        assert result is True

    def was_edge_last_contacted_recently_test(self):
        last_contact_moment = '2020-07-05T10:13:06.000Z'

        datetime_mock = Mock()

        timestamp = '2020-07-12T10:12:06.000Z'  # Less than 7 days elapsed since last contact moment
        datetime_mock.now = Mock(return_value=parse(timestamp))
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = OutageMonitor._was_edge_last_contacted_recently(last_contact_moment)
        assert result is True

        timestamp = '2020-07-12T10:13:06.000Z'  # Exactly 7 days elapsed since last contact moment
        datetime_mock.now = Mock(return_value=parse(timestamp))
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = OutageMonitor._was_edge_last_contacted_recently(last_contact_moment)
        assert result is True

        timestamp = '2020-07-12T10:14:06.000Z'  # More than 7 days elapsed since last contact moment
        datetime_mock.now = Mock(return_value=parse(timestamp))
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = OutageMonitor._was_edge_last_contacted_recently(last_contact_moment)
        assert result is False
