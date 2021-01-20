from datetime import datetime
from dateutil.parser import parse
from unittest.mock import call
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from asynctest import CoroutineMock
from shortuuid import uuid
from pytz import utc

from application.actions import affecting_monitoring as affecting_monitoring_module
from application.actions.affecting_monitoring import AffectingMonitor
from application.repositories.utils_repository import UtilsRepository
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(affecting_monitoring_module, 'uuid', return_value=uuid_)


class TestServiceAffectingMonitor:
    def instance_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        utils_repository = Mock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)

        assert affecting_monitor._logger is logger
        assert affecting_monitor._scheduler is scheduler
        assert affecting_monitor._config is config
        assert affecting_monitor._bruin_repository is bruin_repository
        assert affecting_monitor._hawkeye_repository is hawkeye_repository
        assert affecting_monitor._notifications_repository is notifications_repository
        assert affecting_monitor._customer_cache_repository is customer_cache_repository

        assert affecting_monitor._tickets_by_serial == {}

    @pytest.mark.asyncio
    async def start_hawkeye_affecting_monitoring_with_exec_on_start_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        utils_repository = Mock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(affecting_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(affecting_monitoring_module, 'timezone', new=Mock()):
                await affecting_monitor.start_hawkeye_affecting_monitoring(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            affecting_monitor._affecting_monitoring_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['affecting_monitor'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_hawkeye_affecting_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_hawkeye_affecting_monitoring_with_no_exec_on_start_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        utils_repository = Mock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)

        await affecting_monitor.start_hawkeye_affecting_monitoring(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            affecting_monitor._affecting_monitoring_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['affecting_monitor'],
            next_run_time=undefined,
            replace_existing=False,
            id='_hawkeye_affecting_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_hawkeye_affecting_monitoring_with_job_id_already_executing_test(self):
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        utils_repository = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)

        try:
            await affecting_monitor.start_hawkeye_affecting_monitoring(exec_on_start=False)
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                affecting_monitor._affecting_monitoring_process, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['affecting_monitor'],
                next_run_time=undefined,
                replace_existing=False,
                id='_hawkeye_affecting_monitor_process',
            )

    @pytest.mark.asyncio
    async def affecting_monitoring_process_ok_test(self):
        probe_1_uid = "b8:27:eb:76:a8:de"
        probe_2_uid = "c8:27:fc:76:b8:ef"
        probe_3_uid = "d8:27:ad:76:c8:fa"
        probe_uids = [
            probe_1_uid,
            probe_2_uid,
            probe_3_uid,
        ]

        serial_number_1 = 'B827EB76A8DE'
        serial_number_2 = 'C827FC76B8EF'
        serial_number_3 = 'D8270D76C8F0'

        client_id = 9994

        device_1_cached_info = {
            "probe_uid": probe_1_uid,
            "serial_number": serial_number_1,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "probe_uid": probe_2_uid,
            "serial_number": serial_number_2,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_3_cached_info = {
            "probe_uid": probe_3_uid,
            "serial_number": serial_number_3,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        customer_cache = [
            device_1_cached_info,
            device_2_cached_info,
            device_3_cached_info,
        ]
        customer_cache_response = {
            'body': customer_cache,
            'status': 200,
        }

        test_result_1 = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-11T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "6",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Failed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.5",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }
        test_result_2 = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Passed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }
        tests_results = {
            probe_1_uid: [
                test_result_1,
                test_result_2,
            ]
        }
        tests_results_response = {
            'body': tests_results,
            'status': 200,
        }

        device_1_tests_results = [
            test_result_2,
            test_result_1,
        ]
        tests_results_sorted_by_date_asc = {
            probe_1_uid: device_1_tests_results,
        }

        cached_device_1_with_tests_results = {
            'cached_info': device_1_cached_info,
            'tests_results': device_1_tests_results,
        }
        devices_and_tests_results_map = [
            cached_device_1_with_tests_results,
        ]

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        hawkeye_repository = Mock()
        hawkeye_repository.get_tests_results_for_affecting_monitoring = CoroutineMock(
            return_value=tests_results_response
        )

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(
            return_value=customer_cache_response
        )

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._get_all_probe_uids_from_cache = Mock(return_value=probe_uids)
        affecting_monitor._get_tests_results_sorted_by_date_asc = Mock(return_value=tests_results_sorted_by_date_asc)
        affecting_monitor._map_cached_devices_with_tests_results = Mock(return_value=devices_and_tests_results_map)
        affecting_monitor._add_device_to_tickets_mapping = CoroutineMock()
        affecting_monitor._process_device = CoroutineMock()

        await affecting_monitor._affecting_monitoring_process()

        customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        affecting_monitor._get_all_probe_uids_from_cache.assert_called_once_with(customer_cache)
        hawkeye_repository.get_tests_results_for_affecting_monitoring.assert_awaited_once_with(probe_uids=probe_uids)
        affecting_monitor._get_tests_results_sorted_by_date_asc.assert_called_once_with(tests_results)
        affecting_monitor._map_cached_devices_with_tests_results.assert_called_once_with(
            customer_cache, tests_results_sorted_by_date_asc,
        )
        affecting_monitor._add_device_to_tickets_mapping.assert_awaited_once_with(
            serial_number=serial_number_1, bruin_client_id=client_id
        )
        affecting_monitor._process_device.assert_awaited_once_with(cached_device_1_with_tests_results)

    @pytest.mark.asyncio
    async def affecting_monitoring_process_with_retrieval_of_customer_cache_returning_non_200_status_test(self):
        customer_cache_response = {
            'body': 'Cache is still being built',
            'status': 202,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(
            return_value=customer_cache_response
        )

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._get_all_probe_uids_from_cache = Mock()
        affecting_monitor._process_device = CoroutineMock()

        await affecting_monitor._affecting_monitoring_process()

        customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        affecting_monitor._get_all_probe_uids_from_cache.assert_not_called()
        affecting_monitor._process_device.assert_not_awaited()

    @pytest.mark.asyncio
    async def affecting_monitoring_process_with_retrieval_of_tests_results_returning_non_2xx_status_test(self):
        probe_1_uid = "b8:27:eb:76:a8:de"
        probe_2_uid = "c8:27:fc:76:b8:ef"
        probe_3_uid = "d8:27:ad:76:c8:fa"
        probe_uids = [
            probe_1_uid,
            probe_2_uid,
            probe_3_uid,
        ]

        device_1_cached_info = {
            "probe_uid": probe_1_uid,
            "serial_number": "B827EB76A8DE",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "probe_uid": probe_2_uid,
            "serial_number": "C827FC76B8EF",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_3_cached_info = {
            "probe_uid": probe_3_uid,
            "serial_number": "D8270D76C8F0",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        customer_cache = [
            device_1_cached_info,
            device_2_cached_info,
            device_3_cached_info,
        ]
        customer_cache_response = {
            'body': customer_cache,
            'status': 200,
        }

        tests_results_response = {
            'body': 'Got internal error from Hawkeye',
            'status': 500,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        hawkeye_repository = Mock()
        hawkeye_repository.get_tests_results_for_affecting_monitoring = CoroutineMock(
            return_value=tests_results_response
        )

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(
            return_value=customer_cache_response
        )

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._get_all_probe_uids_from_cache = Mock(return_value=probe_uids)
        affecting_monitor._get_tests_results_sorted_by_date_asc = Mock()
        affecting_monitor._map_cached_devices_with_tests_results = Mock()
        affecting_monitor._process_device = CoroutineMock()

        await affecting_monitor._affecting_monitoring_process()

        customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        affecting_monitor._get_all_probe_uids_from_cache.assert_called_once_with(customer_cache)
        hawkeye_repository.get_tests_results_for_affecting_monitoring.assert_awaited_once_with(probe_uids=probe_uids)
        affecting_monitor._get_tests_results_sorted_by_date_asc.assert_not_called()
        affecting_monitor._map_cached_devices_with_tests_results.assert_not_called()
        affecting_monitor._process_device.assert_not_awaited()

    def get_all_probe_uids_from_cache_test(self):
        probe_1_uid = "b8:27:eb:76:a8:de"
        probe_2_uid = "c8:27:fc:76:b8:ef"
        probe_3_uid = "d8:27:0d:76:c8:f0"
        probe_uids = [
            probe_1_uid,
            probe_2_uid,
            probe_3_uid,
        ]

        customer_cache = [
            {
                "probe_uid": probe_1_uid,
                "serial_number": "B827EB76A8DE",
                "last_contact": "2020-01-16T14:59:56.245Z",
                "bruin_client_info": {
                    "client_id": 9994,
                    "client_name": "METTEL/NEW YORK",
                },
            },
            {
                "probe_uid": probe_2_uid,
                "serial_number": "C827FC76B8EF",
                "last_contact": "2020-01-16T14:59:56.245Z",
                "bruin_client_info": {
                    "client_id": 9994,
                    "client_name": "METTEL/NEW YORK",
                },
            },
            {
                "probe_uid": probe_3_uid,
                "serial_number": "D8270D76C8F0",
                "last_contact": "2020-01-16T14:59:56.245Z",
                "bruin_client_info": {
                    "client_id": 9994,
                    "client_name": "METTEL/NEW YORK",
                },
            },
        ]

        result = AffectingMonitor._get_all_probe_uids_from_cache(customer_cache)
        assert result == probe_uids

    def get_tests_results_sorted_by_date_asc_test(self):
        probe_uid = "b8:27:eb:76:a8:de"

        test_result_1 = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-11T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "6",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Failed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.5",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }
        test_result_2 = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Passed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }
        tests_results = {
            probe_uid: [
                test_result_1,
                test_result_2,
            ]
        }

        result = AffectingMonitor._get_tests_results_sorted_by_date_asc(tests_results)
        expected = {
            probe_uid: [
                test_result_2,
                test_result_1,
            ]
        }
        assert result == expected

    def map_cached_devices_with_tests_results_test(self):
        probe_1_uid = "b8:27:eb:76:a8:de"
        probe_2_uid = "c8:27:fc:76:b8:ef"
        probe_3_uid = "d8:27:ad:76:c8:fa"
        probe_uids = [
            probe_1_uid,
            probe_2_uid,
            probe_3_uid,
        ]

        device_1_cached_info = {
            "probe_uid": probe_1_uid,
            "serial_number": "B827EB76A8DE",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "probe_uid": probe_2_uid,
            "serial_number": "C827FC76B8EF",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_3_cached_info = {
            "probe_uid": probe_3_uid,
            "serial_number": "D8270D76C8F0",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        customer_cache = [
            device_1_cached_info,
            device_2_cached_info,
            device_3_cached_info,
        ]

        test_result_1 = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-11T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "6",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Failed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.5",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }
        test_result_2 = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Passed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        tests_results_list = [
            test_result_2,
            test_result_1,
        ]
        tests_results = {
            probe_1_uid: tests_results_list
        }

        result = AffectingMonitor._map_cached_devices_with_tests_results(customer_cache, tests_results)
        expected = [
            {
                'cached_info': device_1_cached_info,
                'tests_results': tests_results_list,
            }
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def add_device_to_tickets_mapping_with_resolved_ticket_detail_found_test(self):
        bruin_client_id = 9994

        serial_number_1 = "B827EB76A8DE"
        serial_number_2 = "IXPR-TW19480107"

        ticket_id = 12345
        open_affecting_ticket_response = {
            'body': [
                {
                    'ticketID': ticket_id,
                    'clientID': bruin_client_id,
                    'clientName': 'METTEL/NEW YORK',
                    'createDate': '4/23/2019 7:59:50 PM',
                }
            ],
            'status': 200,
        }

        ticket_detail_1_id = 2746930
        ticket_detail_1 = {
            "detailID": ticket_detail_1_id,
            "detailValue": serial_number_1,
            'detailStatus': 'R',
        }

        ticket_detail_2_id = 2746931
        ticket_detail_2 = {
            "detailID": ticket_detail_2_id,
            "detailValue": serial_number_2,
            'detailStatus': 'I',
        }
        ticket_details_list = [
            ticket_detail_1,
            ticket_detail_2,
        ]

        ticket_note_1 = {
            "noteId": 41894041,
            "noteValue": f'Some note',
            "createdDate": "2020-02-25T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_2 = {
            "noteId": 41894042,
            "noteValue": f'Some note 2',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        ticket_note_3 = {
            "noteId": 41894042,
            "noteValue": f'Some note 3',
            "createdDate": "2020-02-26T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_4 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": "2020-02-21T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
        ]

        ticket_details = {
            'ticketDetails': ticket_details_list,
            'ticketNotes': ticket_notes,
        }
        ticket_details_response = {
            'body': ticket_details,
            'status': 200,
        }

        relevant_notes = [
            ticket_note_2,
            ticket_note_1,
        ]

        relevant_notes_sorted = [
            ticket_note_1,
            ticket_note_2,
        ]

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=open_affecting_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._find_ticket_detail_by_serial = Mock(return_value=ticket_detail_1)
        affecting_monitor._find_ticket_notes_by_serial = Mock(return_value=relevant_notes)
        affecting_monitor._get_notes_sorted_by_date_and_id_asc = Mock(return_value=relevant_notes_sorted)

        await affecting_monitor._add_device_to_tickets_mapping(
            serial_number=serial_number_1, bruin_client_id=bruin_client_id
        )

        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id=bruin_client_id, service_number=serial_number_1
        )
        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        affecting_monitor._find_ticket_detail_by_serial.assert_called_once_with(ticket_details_list, serial_number_1)
        affecting_monitor._find_ticket_notes_by_serial.assert_called_once_with(ticket_notes, serial_number_1)
        affecting_monitor._get_notes_sorted_by_date_and_id_asc.assert_called_once_with(relevant_notes)

        expected_tickets_mapping = {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': ticket_detail_1_id,
                'is_detail_resolved': True,
                'initial_notes': [
                    {
                        'text': ticket_note_1['noteValue'],
                        'date': parse(ticket_note_1['createdDate']).astimezone(utc),
                    },
                    {
                        'text': ticket_note_2['noteValue'],
                        'date': parse(ticket_note_2['createdDate']).astimezone(utc),
                    },
                ],
                'new_notes': [],
            },
        }
        assert affecting_monitor._tickets_by_serial == expected_tickets_mapping

    @pytest.mark.asyncio
    async def add_device_to_tickets_mapping_with_unresolved_ticket_detail_found_test(self):
        bruin_client_id = 9994

        serial_number_1 = "B827EB76A8DE"
        serial_number_2 = "IXPR-TW19480107"

        ticket_id = 12345
        open_affecting_ticket_response = {
            'body': [
                {
                    'ticketID': ticket_id,
                    'clientID': bruin_client_id,
                    'clientName': 'METTEL/NEW YORK',
                    'createDate': '4/23/2019 7:59:50 PM',
                }
            ],
            'status': 200,
        }

        ticket_detail_1_id = 2746930
        ticket_detail_1 = {
            "detailID": ticket_detail_1_id,
            "detailValue": serial_number_1,
            'detailStatus': 'I',
        }

        ticket_detail_2_id = 2746931
        ticket_detail_2 = {
            "detailID": ticket_detail_2_id,
            "detailValue": serial_number_2,
            'detailStatus': 'I',
        }
        ticket_details_list = [
            ticket_detail_1,
            ticket_detail_2,
        ]

        ticket_note_1 = {
            "noteId": 41894041,
            "noteValue": f'Some note',
            "createdDate": "2020-02-25T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_2 = {
            "noteId": 41894042,
            "noteValue": f'Some note 2',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        ticket_note_3 = {
            "noteId": 41894042,
            "noteValue": f'Some note 3',
            "createdDate": "2020-02-26T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_4 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": "2020-02-21T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
        ]

        ticket_details = {
            'ticketDetails': ticket_details_list,
            'ticketNotes': ticket_notes,
        }
        ticket_details_response = {
            'body': ticket_details,
            'status': 200,
        }

        relevant_notes = [
            ticket_note_2,
            ticket_note_1,
        ]

        relevant_notes_sorted = [
            ticket_note_1,
            ticket_note_2,
        ]

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=open_affecting_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._find_ticket_detail_by_serial = Mock(return_value=ticket_detail_1)
        affecting_monitor._find_ticket_notes_by_serial = Mock(return_value=relevant_notes)
        affecting_monitor._get_notes_sorted_by_date_and_id_asc = Mock(return_value=relevant_notes_sorted)

        await affecting_monitor._add_device_to_tickets_mapping(
            serial_number=serial_number_1, bruin_client_id=bruin_client_id
        )

        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id=bruin_client_id, service_number=serial_number_1
        )
        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        affecting_monitor._find_ticket_detail_by_serial.assert_called_once_with(ticket_details_list, serial_number_1)
        affecting_monitor._find_ticket_notes_by_serial.assert_called_once_with(ticket_notes, serial_number_1)
        affecting_monitor._get_notes_sorted_by_date_and_id_asc.assert_called_once_with(relevant_notes)

        expected_tickets_mapping = {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': ticket_detail_1_id,
                'is_detail_resolved': False,
                'initial_notes': [
                    {
                        'text': ticket_note_1['noteValue'],
                        'date': parse(ticket_note_1['createdDate']).astimezone(utc),
                    },
                    {
                        'text': ticket_note_2['noteValue'],
                        'date': parse(ticket_note_2['createdDate']).astimezone(utc),
                    },
                ],
                'new_notes': [],
            },
        }
        assert affecting_monitor._tickets_by_serial == expected_tickets_mapping

    @pytest.mark.asyncio
    async def add_device_to_tickets_mapping_with_retrieval_of_open_affecting_tickets_returning_non_2xx_status_test(
            self):
        bruin_client_id = 9994
        serial_number = "B827EB76A8DE"

        open_affecting_ticket_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=open_affecting_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)

        await affecting_monitor._add_device_to_tickets_mapping(
            serial_number=serial_number, bruin_client_id=bruin_client_id
        )

        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id=bruin_client_id, service_number=serial_number
        )
        bruin_repository.get_ticket_details.assert_not_awaited()

        expected_tickets_mapping = {}
        assert affecting_monitor._tickets_by_serial == expected_tickets_mapping

    @pytest.mark.asyncio
    async def add_device_to_tickets_mapping_with_no_affecting_tickets_found_test(self):
        bruin_client_id = 9994
        serial_number = "B827EB76A8DE"

        open_affecting_ticket_response = {
            'body': [],
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=open_affecting_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)

        await affecting_monitor._add_device_to_tickets_mapping(
            serial_number=serial_number, bruin_client_id=bruin_client_id
        )

        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id=bruin_client_id, service_number=serial_number
        )

        expected_tickets_mapping = {
            serial_number: {}
        }
        assert affecting_monitor._tickets_by_serial == expected_tickets_mapping

    @pytest.mark.asyncio
    async def add_device_to_tickets_mapping_with_retrieval_of_ticket_details_returning_non_2xx_status_test(self):
        bruin_client_id = 9994
        serial_number = "B827EB76A8DE"

        ticket_id = 12345
        open_affecting_ticket_response = {
            'body': [
                {
                    'ticketID': ticket_id,
                    'clientID': bruin_client_id,
                    'clientName': 'METTEL/NEW YORK',
                    'createDate': '4/23/2019 7:59:50 PM',
                }
            ],
            'status': 200,
        }

        ticket_details_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=open_affecting_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._find_ticket_notes_by_serial = Mock()
        affecting_monitor._get_notes_sorted_by_date_and_id_asc = Mock()

        await affecting_monitor._add_device_to_tickets_mapping(
            serial_number=serial_number, bruin_client_id=bruin_client_id
        )

        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id=bruin_client_id, service_number=serial_number
        )
        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        affecting_monitor._find_ticket_notes_by_serial.assert_not_called()
        affecting_monitor._get_notes_sorted_by_date_and_id_asc.assert_not_called()

        expected_tickets_mapping = {}
        assert affecting_monitor._tickets_by_serial == expected_tickets_mapping

    def find_ticket_detail_by_serial_test(self):
        serial_number_1 = "B827EB76A8DE"
        serial_number_2 = "IXPR-TW19480107"

        ticket_detail_1 = {
            "detailID": 2746930,
            "detailValue": serial_number_1,
        }
        ticket_detail_2 = {
            "detailID": 2746931,
            "detailValue": serial_number_2,
        }
        ticket_details_list = [
            ticket_detail_1,
            ticket_detail_2,
        ]

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = UtilsRepository()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)

        result = affecting_monitor._find_ticket_detail_by_serial(ticket_details_list, serial_number_1)
        assert result == ticket_detail_1

    def find_ticket_notes_by_serial_test(self):
        serial_number_1 = "B827EB76A8DE"
        serial_number_2 = "IXPR-TW19480107"

        ticket_note_1 = {
            "noteId": 41894041,
            "noteValue": f'Some note',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_2 = {
            "noteId": 41894042,
            "noteValue": f'Some note 2',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        ticket_note_3 = {
            "noteId": 41894042,
            "noteValue": f'Some note 3',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_4 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
        ]

        result = AffectingMonitor._find_ticket_notes_by_serial(ticket_notes, serial_number_1)

        expected = [
            ticket_note_1,
            ticket_note_2,
        ]
        assert result == expected

    def get_notes_sorted_by_date_and_id_asc_test(self):
        ticket_note_1 = {
            "noteId": 41894041,
            "noteValue": f'Some note',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                'B827EB76A8DE',
            ],
        }
        ticket_note_2 = {
            "noteId": 41894042,
            "noteValue": f'Some note 2',
            "createdDate": "2020-02-22T10:07:13.503-05:00",
            "serviceNumber": [
                'B827EB76A8DE',
                'IXPR-TW19480107',
            ],
        }
        ticket_note_3 = {
            "noteId": 41894043,
            "noteValue": f'Some note 3',
            "createdDate": "2020-02-23T10:07:13.503-05:00",
            "serviceNumber": [
                'B827EB76A8DE',
            ],
        }
        ticket_note_4 = {
            "noteId": 41894044,
            "noteValue": f'Some note 3',
            "createdDate": "2020-02-22T10:07:13.503-05:00",
            "serviceNumber": [
                'B827EB76A8DE',
            ],
        }
        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
        ]

        result = AffectingMonitor._get_notes_sorted_by_date_and_id_asc(ticket_notes)

        expected = [
            ticket_note_2,
            ticket_note_4,
            ticket_note_3,
            ticket_note_1,
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def process_device_test(self):
        serial_number = 'B827EB76A8DE'
        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }

        test_result_1 = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Passed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }
        test_result_2 = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-11T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "6",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Failed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.5",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }
        test_result_3 = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-15T12:01:32Z",
                "duration": "30",
                "status": "Passed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }
        test_result_4 = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-15T12:01:32Z",
                "duration": "30",
                "status": "Error",
                "reasonCause": "Endpoint Vi_Pi_DRI test Not Available for Test",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": []
        }

        tests_results = [
            test_result_1,
            test_result_2,
            test_result_3,
            test_result_4,
        ]
        device_info = {
            'cached_info': device_cached_info,
            'tests_results': tests_results,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._process_passed_test_result = CoroutineMock()
        affecting_monitor._process_failed_test_result = CoroutineMock()
        affecting_monitor._append_new_notes_for_device = CoroutineMock()

        # This manager is the only way to check the call order of multiple, different mocks
        manager_mock = Mock()
        manager_mock._process_passed_test_result = affecting_monitor._process_passed_test_result
        manager_mock._process_failed_test_result = affecting_monitor._process_failed_test_result

        await affecting_monitor._process_device(device_info)

        expected_calls_ordered = [
            call._process_passed_test_result(test_result=test_result_1, device_cached_info=device_cached_info),
            call._process_failed_test_result(test_result=test_result_2, device_cached_info=device_cached_info),
            call._process_passed_test_result(test_result=test_result_3, device_cached_info=device_cached_info),
        ]
        assert manager_mock.mock_calls == expected_calls_ordered
        affecting_monitor._append_new_notes_for_device.assert_awaited_once_with(serial_number)

    @pytest.mark.asyncio
    async def append_new_notes_for_device_with_serial_number_missing_in_tickets_mapping_test(self):
        serial_number = 'B827EB76A8DE'

        tickets_mapping = {}

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping

        await affecting_monitor._append_new_notes_for_device(serial_number)

        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_new_notes_for_device_with_no_notes_to_append_test(self):
        serial_number = 'B827EB76A8DE'

        ticket_initial_notes = [
            {
                'text': (
                    '#*Automation Engine*#\n'
                    'Service Affecting (Ixia)\n'
                    'Device Name: ATL_XR2000_1\n'
                    '\n'
                    'All thresholds are normal.\n'
                    '\n'
                    'Test Status: PASSED\n'
                    'Test Type: ICMP Test\n'
                    'Test: 316 - Test Result: 2569942'
                ),
                'date': parse('2020-12-10T12:01:32Z'),
            }
        ]
        ticket_new_notes = []

        ticket_id = 12345
        ticket_detail_id = 67890
        tickets_mapping = {
            serial_number: {
                'ticket_id': ticket_id,
                'detail_id': ticket_detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping

        await affecting_monitor._append_new_notes_for_device(serial_number)

        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_new_notes_for_device_with_notes_to_append_and_environment_not_being_production_test(self):
        serial_number = 'B827EB76A8DE'

        ticket_initial_notes = [
            {
                'text': (
                    '#*Automation Engine*#\n'
                    'Service Affecting (Ixia)\n'
                    'Device Name: ATL_XR2000_1\n'
                    '\n'
                    'All thresholds are normal.\n'
                    '\n'
                    'Test Status: PASSED\n'
                    'Test Type: ICMP Test\n'
                    'Test: 316 - Test Result: 2569942'
                ),
                'date': parse('2020-12-10T12:01:32Z'),
            }
        ]

        ticket_new_note_1_text = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            'Device Name: ATL_XR2000_1\n'
            '\n'
            'Trouble: Jitter Max (ms)\n'
            'Threshold: 8\n'
            'Value: 8.3\n'
            '\n'
            'Test Status: FAILED\n'
            'Test Type: Network KPI\n'
            'Test: 316 - Test Result: 2569995'
        )
        ticket_new_note_2_text = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            'Device Name: ATL_XR2000_1\n'
            '\n'
            'All thresholds are normal.\n'
            '\n'
            'Test Status: PASSED\n'
            'Test Type: ICMP Test\n'
            'Test: 322 - Test Result: 2569996'
        )
        ticket_new_note_3_text = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            'Device Name: ATL_XR2000_1\n'
            '\n'
            'Trouble: Loss\n'
            'Threshold: 5\n'
            'Value: 7\n'
            '\n'
            'Test Status: FAILED\n'
            'Test Type: ICMP Test\n'
            'Test: 339 - Test Result: 2569997'
        )
        ticket_new_notes = [
            {
                'text': ticket_new_note_1_text,
                'date': parse('2020-12-10T13:01:32Z'),
            },
            {
                'text': ticket_new_note_2_text,
                'date': parse('2020-12-10T14:01:32Z'),
            },
            {
                'text': ticket_new_note_3_text,
                'date': parse('2020-12-10T15:01:32Z'),
            },
        ]

        ticket_id = 12345
        ticket_detail_id = 67890
        tickets_mapping = {
            serial_number: {
                'ticket_id': ticket_id,
                'detail_id': ticket_detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }

        notes_payload = [
            {
                'text': ticket_new_note_1_text,
                'service_number': serial_number,
            },
            {
                'text': ticket_new_note_2_text,
                'service_number': serial_number,
            },
            {
                'text': ticket_new_note_3_text,
                'service_number': serial_number,
            },
        ]

        logger = Mock()
        scheduler = Mock()
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await affecting_monitor._append_new_notes_for_device(serial_number)

        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_new_notes_for_device_with_notes_to_append_test(self):
        serial_number = 'B827EB76A8DE'

        ticket_initial_notes = [
            {
                'text': (
                    '#*Automation Engine*#\n'
                    'Service Affecting (Ixia)\n'
                    'Device Name: ATL_XR2000_1\n'
                    '\n'
                    'All thresholds are normal.\n'
                    '\n'
                    'Test Status: PASSED\n'
                    'Test Type: ICMP Test\n'
                    'Test: 316 - Test Result: 2569942'
                ),
                'date': parse('2020-12-10T12:01:32Z'),
            }
        ]

        ticket_new_note_1_text = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            'Device Name: ATL_XR2000_1\n'
            '\n'
            'Trouble: Jitter Max (ms)\n'
            'Threshold: 8\n'
            'Value: 8.3\n'
            '\n'
            'Test Status: FAILED\n'
            'Test Type: Network KPI\n'
            'Test: 316 - Test Result: 2569995'
        )
        ticket_new_note_2_text = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            'Device Name: ATL_XR2000_1\n'
            '\n'
            'All thresholds are normal.\n'
            '\n'
            'Test Status: PASSED\n'
            'Test Type: ICMP Test\n'
            'Test: 322 - Test Result: 2569996'
        )
        ticket_new_note_3_text = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            'Device Name: ATL_XR2000_1\n'
            '\n'
            'Trouble: Loss\n'
            'Threshold: 5\n'
            'Value: 7\n'
            '\n'
            'Test Status: FAILED\n'
            'Test Type: ICMP Test\n'
            'Test: 339 - Test Result: 2569997'
        )
        ticket_new_notes = [
            {
                'text': ticket_new_note_1_text,
                'date': parse('2020-12-10T13:01:32Z'),
            },
            {
                'text': ticket_new_note_2_text,
                'date': parse('2020-12-10T14:01:32Z'),
            },
            {
                'text': ticket_new_note_3_text,
                'date': parse('2020-12-10T15:01:32Z'),
            },
        ]

        ticket_id = 12345
        tickets_mapping = {
            serial_number: {
                'ticket_id': ticket_id,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }

        notes_payload = [
            {
                'text': ticket_new_note_1_text,
                'service_number': serial_number,
            },
            {
                'text': ticket_new_note_2_text,
                'service_number': serial_number,
            },
            {
                'text': ticket_new_note_3_text,
                'service_number': serial_number,
            },
        ]

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.notify_multiple_notes_were_posted_to_ticket = CoroutineMock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await affecting_monitor._append_new_notes_for_device(serial_number)

        bruin_repository.append_multiple_notes_to_ticket.assert_awaited_once_with(
            ticket_id=ticket_id, notes=notes_payload
        )
        notifications_repository.notify_multiple_notes_were_posted_to_ticket.assert_awaited_once_with(
            ticket_id, serial_number
        )

    def test_result_passed_test(self):
        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Passed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        result = AffectingMonitor._test_result_passed(test_result)
        assert result is True

        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        result = AffectingMonitor._test_result_passed(test_result)
        assert result is False

    def test_result_failed_test(self):
        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        result = AffectingMonitor._test_result_failed(test_result)
        assert result is True

        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Passed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        result = AffectingMonitor._test_result_failed(test_result)
        assert result is False

    def process_passed_test_result_with_serial_number_missing_in_tickets_mapping_test(self):
        serial_number = 'B827EB76A8DE'

        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Passed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }

        tickets_mapping = {}

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type = Mock()
        affecting_monitor._is_passed_note = Mock()
        affecting_monitor._build_passed_note = Mock()

        affecting_monitor._process_passed_test_result(test_result=test_result, device_cached_info=device_cached_info)

        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_passed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial is tickets_mapping

    def process_passed_test_result_with_no_ticket_found_for_serial_test(self):
        serial_number = 'B827EB76A8DE'

        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Passed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }

        tickets_mapping = {
            serial_number: {}
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type = Mock()
        affecting_monitor._is_passed_note = Mock()
        affecting_monitor._build_passed_note = Mock()

        affecting_monitor._process_passed_test_result(test_result=test_result, device_cached_info=device_cached_info)

        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_passed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial is tickets_mapping

    def process_passed_test_result_with_ticket_having_resolved_detail_found_for_serial_test(self):
        serial_number = 'B827EB76A8DE'

        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Passed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }

        ticket_initial_notes = [
            {
                'text': (
                    '#*Automation Engine*#\n'
                    'Service Affecting (Ixia)\n'
                    'Device Name: ATL_XR2000_1\n'
                    '\n'
                    'All thresholds are normal.\n'
                    '\n'
                    'Test Status: PASSED\n'
                    'Test Type: ICMP Test\n'
                    'Test: 316 - Test Result: 2569942'
                ),
                'date': parse('2020-12-10T12:01:32Z'),
            }
        ]
        ticket_new_notes = [
            {
                'text': (
                    '#*Automation Engine*#\n'
                    'Service Affecting (Ixia)\n'
                    'Device Name: ATL_XR2000_1\n'
                    '\n'
                    'Trouble: Jitter Max (ms)\n'
                    'Threshold: 8\n'
                    'Value: 8.3\n'
                    '\n'
                    'Test Status: FAILED\n'
                    'Test Type: ICMP Test\n'
                    'Test: 316 - Test Result: 2569999'
                ),
                'date': parse('2020-12-10T13:01:32Z'),
            }
        ]

        tickets_mapping = {
            serial_number: {
                'ticket_id': 1234,
                'detail_id': 5678,
                'is_detail_resolved': True,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type = Mock()
        affecting_monitor._is_passed_note = Mock()
        affecting_monitor._build_passed_note = Mock()

        affecting_monitor._process_passed_test_result(test_result=test_result, device_cached_info=device_cached_info)

        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_passed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial is tickets_mapping

    def process_passed_test_result_with_no_notes_found_for_target_test_type_test(self):
        serial_number = 'B827EB76A8DE'

        test_type = 'Network KPI'
        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Passed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": test_type,
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }

        ticket_initial_notes = [
            {
                'text': (
                    '#*Automation Engine*#\n'
                    'Service Affecting (Ixia)\n'
                    'Device Name: ATL_XR2000_1\n'
                    '\n'
                    'All thresholds are normal.\n'
                    '\n'
                    'Test Status: PASSED\n'
                    'Test Type: ICMP Test\n'
                    'Test: 316 - Test Result: 2569942'
                ),
                'date': parse('2020-12-10T12:01:32Z'),
            }
        ]
        ticket_new_notes = [
            {
                'text': (
                    '#*Automation Engine*#\n'
                    'Service Affecting (Ixia)\n'
                    'Device Name: ATL_XR2000_1\n'
                    '\n'
                    'Trouble: Jitter Max (ms)\n'
                    'Threshold: 8\n'
                    'Value: 8.3\n'
                    '\n'
                    'Test Status: FAILED\n'
                    'Test Type: ICMP Test\n'
                    'Test: 316 - Test Result: 2569999'
                ),
                'date': parse('2020-12-10T13:01:32Z'),
            }
        ]
        all_ticket_notes = ticket_initial_notes + ticket_new_notes
        tickets_mapping = {
            serial_number: {
                'ticket_id': 1234,
                'detail_id': 5678,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type = Mock(return_value=None)
        affecting_monitor._is_passed_note = Mock()
        affecting_monitor._build_passed_note = Mock()

        affecting_monitor._process_passed_test_result(test_result=test_result, device_cached_info=device_cached_info)

        affecting_monitor._get_last_note_by_test_type.assert_called_once_with(all_ticket_notes, test_type)
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_passed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial is tickets_mapping

    def process_passed_test_result_with_passed_note_found_test(self):
        serial_number = 'B827EB76A8DE'

        test_type = 'Network KPI'
        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Passed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": test_type,
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }

        ticket_initial_note_1_text = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            'Device Name: ATL_XR2000_1\n'
            '\n'
            'All thresholds are normal.\n'
            '\n'
            'Test Status: PASSED\n'
            f'Test Type: {test_type}\n'
            'Test: 316 - Test Result: 2569942'
        )
        ticket_initial_note_1 = {
            'text': ticket_initial_note_1_text,
            'date': parse('2020-12-10T12:01:32Z'),
        }
        ticket_initial_notes = [
            ticket_initial_note_1
        ]
        ticket_new_notes = [
            {
                'text': (
                    '#*Automation Engine*#\n'
                    'Service Affecting (Ixia)\n'
                    'Device Name: ATL_XR2000_1\n'
                    '\n'
                    'Trouble: Jitter Max (ms)\n'
                    'Threshold: 8\n'
                    'Value: 8.3\n'
                    '\n'
                    'Test Status: FAILED\n'
                    'Test Type: ICMP Test\n'
                    'Test: 316 - Test Result: 2569999'
                ),
                'date': parse('2020-12-10T13:01:32Z'),
            }
        ]
        all_ticket_notes = ticket_initial_notes + ticket_new_notes
        tickets_mapping = {
            serial_number: {
                'ticket_id': 1234,
                'detail_id': 5678,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type = Mock(return_value=ticket_initial_note_1)
        affecting_monitor._is_passed_note = Mock(return_value=True)
        affecting_monitor._build_passed_note = Mock()

        affecting_monitor._process_passed_test_result(test_result=test_result, device_cached_info=device_cached_info)

        affecting_monitor._get_last_note_by_test_type.assert_called_once_with(all_ticket_notes, test_type)
        affecting_monitor._is_passed_note.assert_called_once_with(ticket_initial_note_1_text)
        affecting_monitor._build_passed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial is tickets_mapping

    def process_passed_test_result_with_failed_note_found_test(self):
        serial_number = 'B827EB76A8DE'

        test_type = 'Network KPI'
        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Passed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": test_type,
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }

        ticket_initial_note_1_text = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            'Device Name: ATL_XR2000_1\n'
            '\n'
            'All thresholds are normal.\n'
            '\n'
            'Test Status: PASSED\n'
            f'Test Type: {test_type}\n'
            'Test: 316 - Test Result: 2569942'
        )
        ticket_initial_note_1 = {
            'text': ticket_initial_note_1_text,
            'date': parse('2020-12-10T12:01:32Z'),
        }
        ticket_initial_notes = [
            ticket_initial_note_1
        ]

        ticket_new_note_1 = {
            'text': (
                '#*Automation Engine*#\n'
                'Service Affecting (Ixia)\n'
                'Device Name: ATL_XR2000_1\n'
                '\n'
                'Trouble: Jitter Max (ms)\n'
                'Threshold: 8\n'
                'Value: 8.3\n'
                '\n'
                'Test Status: FAILED\n'
                'Test Type: ICMP Test\n'
                'Test: 316 - Test Result: 2569999'
            ),
            'date': parse('2020-12-10T13:01:32Z'),
        }
        ticket_new_notes = [
            ticket_new_note_1
        ]
        all_ticket_notes = ticket_initial_notes + ticket_new_notes

        ticket_id = 1234
        tickets_mapping = {
            serial_number: {
                'ticket_id': ticket_id,
                'detail_id': 5678,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }

        passed_test_note = 'This is a PASSED note'

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type = Mock(return_value=ticket_initial_note_1)
        affecting_monitor._is_passed_note = Mock(return_value=False)
        affecting_monitor._build_passed_note = Mock(return_value=passed_test_note)

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.object(affecting_monitoring_module, 'datetime', new=datetime_mock):
            affecting_monitor._process_passed_test_result(
                test_result=test_result, device_cached_info=device_cached_info
            )

        affecting_monitor._get_last_note_by_test_type.assert_called_once_with(all_ticket_notes, test_type)
        affecting_monitor._is_passed_note.assert_called_once_with(ticket_initial_note_1_text)
        affecting_monitor._build_passed_note.assert_called_once_with(test_result)

        updated_new_notes = [
            ticket_new_note_1,
            {
                'text': passed_test_note,
                'date': current_datetime,
            }
        ]
        assert affecting_monitor._tickets_by_serial == {
            serial_number: {
                'ticket_id': ticket_id,
                'detail_id': 5678,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': updated_new_notes,
            }
        }

    def get_last_note_by_test_type_test(self):
        target_test_type = 'Network KPI'

        note_1 = {
            'text': (
                '#*Automation Engine*#\n'
                'Service Affecting (Ixia)\n'
                'Device Name: ATL_XR2000_1\n'
                '\n'
                'All thresholds are normal.\n'
                '\n'
                'Test Status: PASSED\n'
                f'Test Type: {target_test_type}\n'
                'Test: 316 - Test Result: 2569942'
            ),
            'date': parse('2020-12-10T12:01:32Z'),
        }
        note_2 = {
            'text': (
                '#*Automation Engine*#\n'
                'Service Affecting (Ixia)\n'
                'Device Name: ATL_XR2000_1\n'
                '\n'
                'All thresholds are normal.\n'
                '\n'
                'Test Status: PASSED\n'
                f'Test Type: ICMP Test\n'
                'Test: 316 - Test Result: 2569942'
            ),
            'date': parse('2020-12-10T12:01:32Z'),
        }
        note_3 = {
            'text': (
                '#*Automation Engine*#\n'
                'Service Affecting (Ixia)\n'
                'Device Name: ATL_XR2000_1\n'
                '\n'
                'All thresholds are normal.\n'
                '\n'
                'Test Status: PASSED\n'
                f'Test Type: {target_test_type}\n'
                'Test: 316 - Test Result: 2569942'
            ),
            'date': parse('2020-12-10T12:01:32Z'),
        }
        notes = [
            note_1,
            note_2,
            note_3,
        ]

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = UtilsRepository()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)

        result = affecting_monitor._get_last_note_by_test_type(notes, target_test_type)
        assert result == note_3

    def is_passed_note_test(self):
        note = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            'Device Name: ATL_XR2000_1\n'
            '\n'
            'All thresholds are normal.\n'
            '\n'
            'Test Status: PASSED\n'
            f'Test Type: ICMP Test\n'
            'Test: 316 - Test Result: 2569942'
        )

        result = AffectingMonitor._is_passed_note(note)
        assert result is True

        note = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            'Device Name: ATL_XR2000_1\n'
            '\n'
            'Trouble: Jitter Max (ms)\n'
            'Threshold: 8\n'
            'Value: 8.3\n'
            '\n'
            'Test Status: FAILED\n'
            'Test Type: ICMP Test\n'
            'Test: 316 - Test Result: 2569999'
        )

        result = AffectingMonitor._is_passed_note(note)
        assert result is False

    def build_passed_note_test(self):
        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Passed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": 'Network KPI',
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "4",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        result = AffectingMonitor._build_passed_note(test_result)
        expected = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            '\n'
            f'Device Name: Vi_Pi_DRI test\n'
            '\n'
            'Test Type: Network KPI\n'
            'Test: 335 - Test Result: DlfsJHcB0dCO9W0n6nGC\n'
            '\n'
            'All thresholds are normal.\n'
            '\n'
            'Test Status: PASSED'
        )
        assert result == expected

    def build_failed_note_test(self):
        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": 'Network KPI',
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "6",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Failed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
                {
                    "metric": "Latency (ms)",
                    "pairName": "KPI from->to",
                    "value": "10",
                    "threshold": "7",
                    "thresholdType": "0",
                    "status": "Failed"
                },
            ]
        }

        result = AffectingMonitor._build_failed_note(test_result)
        expected = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            '\n'
            f'Device Name: Vi_Pi_DRI test\n'
            '\n'
            'Test Type: Network KPI\n'
            'Test: 335 - Test Result: DlfsJHcB0dCO9W0n6nGC\n'
            '\n'
            'Trouble: Jitter (ms)\n'
            'Threshold: 5\n'
            'Value: 6\n'
            '\n'
            'Trouble: Latency (ms)\n'
            'Threshold: 7\n'
            'Value: 10\n'
            '\n'
            'Test Status: FAILED'
        )
        assert result == expected

    @pytest.mark.asyncio
    async def process_failed_test_result_with_serial_number_missing_in_tickets_mapping_test(self):
        serial_number = 'B827EB76A8DE'

        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "6",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Failed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        client_id = 9994
        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }

        tickets_mapping = {}

        logger = Mock()
        scheduler = Mock()
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.create_affecting_ticket = CoroutineMock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type = Mock()
        affecting_monitor._is_passed_note = Mock()
        affecting_monitor._build_failed_note = Mock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await affecting_monitor._process_failed_test_result(
                test_result=test_result, device_cached_info=device_cached_info
            )

        bruin_repository.create_affecting_ticket.assert_not_awaited()
        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_failed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial is tickets_mapping

    @pytest.mark.asyncio
    async def process_failed_test_result_with_no_ticket_found_for_serial_and_environment_not_being_production_test(
            self):
        serial_number = 'B827EB76A8DE'

        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "6",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Failed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        client_id = 9994
        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }

        tickets_mapping = {
            serial_number: {}
        }

        logger = Mock()
        scheduler = Mock()
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.create_affecting_ticket = CoroutineMock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type = Mock()
        affecting_monitor._is_passed_note = Mock()
        affecting_monitor._build_failed_note = Mock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await affecting_monitor._process_failed_test_result(
                test_result=test_result, device_cached_info=device_cached_info
            )

        bruin_repository.create_affecting_ticket.assert_not_awaited()
        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_failed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial is tickets_mapping

    @pytest.mark.asyncio
    async def process_failed_test_result_with_no_ticket_found_for_serial_and_unsuccessful_ticket_creation_test(self):
        serial_number = 'B827EB76A8DE'

        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "6",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Failed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        client_id = 9994
        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }

        tickets_mapping = {
            serial_number: {}
        }

        create_ticket_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        logger = Mock()
        scheduler = Mock()
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.create_affecting_ticket = CoroutineMock(return_value=create_ticket_response)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type = Mock()
        affecting_monitor._is_passed_note = Mock()
        affecting_monitor._build_failed_note = Mock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await affecting_monitor._process_failed_test_result(
                test_result=test_result, device_cached_info=device_cached_info
            )

        bruin_repository.create_affecting_ticket.assert_awaited_once_with(
            client_id=client_id, service_number=serial_number
        )
        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_failed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial is tickets_mapping

    @pytest.mark.asyncio
    async def process_failed_test_result_with_no_ticket_found_for_serial_and_successful_ticket_creation_test(self):
        serial_number = 'B827EB76A8DE'

        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": "Network KPI",
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "6",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Failed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        client_id = 9994
        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }

        tickets_mapping = {
            serial_number: {}
        }

        ticket_id = 12345
        create_ticket_response = {
            'body': {
                'ticketIds': [
                    ticket_id,
                ],
            },
            'status': 200,
        }

        failed_test_note = 'This is a FAILED note'

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.create_affecting_ticket = CoroutineMock(return_value=create_ticket_response)

        notifications_repository = Mock()
        notifications_repository.notify_ticket_creation = CoroutineMock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type = Mock()
        affecting_monitor._is_passed_note = Mock()
        affecting_monitor._build_failed_note = Mock(return_value=failed_test_note)

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            with patch.object(affecting_monitoring_module, 'datetime', new=datetime_mock):
                await affecting_monitor._process_failed_test_result(
                    test_result=test_result, device_cached_info=device_cached_info
                )

        bruin_repository.create_affecting_ticket.assert_awaited_once_with(
            client_id=client_id, service_number=serial_number
        )
        notifications_repository.notify_ticket_creation.assert_awaited_once_with(ticket_id, serial_number)
        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_failed_note.assert_called_once_with(test_result)
        assert affecting_monitor._tickets_by_serial == {
            serial_number: {
                'ticket_id': ticket_id,
                'detail_id': None,
                'is_detail_resolved': False,
                'initial_notes': [],
                'new_notes': [
                    {
                        'text': failed_test_note,
                        'date': current_datetime,
                    }
                ]
            }
        }

    @pytest.mark.asyncio
    async def process_failed_test_result_with_unresolved_ticket_detail_found_and_no_note_found_for_test_type_test(self):
        serial_number = 'B827EB76A8DE'

        test_type = 'Network KPI'
        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": test_type,
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "6",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Failed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        client_id = 9994
        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }

        ticket_initial_notes = [
            {
                'text': (
                    '#*Automation Engine*#\n'
                    'Service Affecting (Ixia)\n'
                    'Device Name: ATL_XR2000_1\n'
                    '\n'
                    'Trouble: Jitter Max (ms)\n'
                    'Threshold: 8\n'
                    'Value: 8.3\n'
                    '\n'
                    'Test Status: FAILED\n'
                    'Test Type: ICMP Test\n'
                    'Test: 316 - Test Result: 2569942'
                ),
                'date': parse('2020-12-10T12:01:32Z'),
            }
        ]

        ticket_new_note_1 = {
            'text': (
                '#*Automation Engine*#\n'
                'Service Affecting (Ixia)\n'
                'Device Name: ATL_XR2000_1\n'
                '\n'
                'Trouble: Jitter Max (ms)\n'
                'Threshold: 8\n'
                'Value: 8.3\n'
                '\n'
                'Test Status: FAILED\n'
                'Test Type: ICMP Test\n'
                'Test: 316 - Test Result: 2569999'
            ),
            'date': parse('2020-12-10T13:01:32Z'),
        }
        ticket_new_notes = [
            ticket_new_note_1,
        ]
        all_ticket_notes = ticket_initial_notes + ticket_new_notes

        ticket_id = 12345
        detail_id = 67890
        tickets_mapping = {
            serial_number: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }

        failed_test_note = 'This is a FAILED note'

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.create_affecting_ticket = CoroutineMock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type = Mock(return_value=None)
        affecting_monitor._is_passed_note = Mock()
        affecting_monitor._build_failed_note = Mock(return_value=failed_test_note)

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.object(affecting_monitoring_module, 'datetime', new=datetime_mock):
            await affecting_monitor._process_failed_test_result(
                test_result=test_result, device_cached_info=device_cached_info
            )

        bruin_repository.create_affecting_ticket.assert_not_awaited()
        affecting_monitor._get_last_note_by_test_type.assert_called_once_with(all_ticket_notes, test_type)
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_failed_note.assert_called_once_with(test_result)
        updated_new_notes = [
            ticket_new_note_1,
            {
                'text': failed_test_note,
                'date': current_datetime,
            }
        ]
        assert affecting_monitor._tickets_by_serial == {
            serial_number: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': updated_new_notes,
            }
        }

    @pytest.mark.asyncio
    async def process_failed_test_result_with_unresolved_ticket_detail_found_and_passed_note_found_for_test_type_test(
            self):
        serial_number = 'B827EB76A8DE'

        test_type = 'Network KPI'
        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": test_type,
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "6",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Failed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        client_id = 9994
        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }

        ticket_initial_note_1_text = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            'Device Name: ATL_XR2000_1\n'
            '\n'
            'Trouble: Jitter Max (ms)\n'
            'Threshold: 8\n'
            'Value: 8.3\n'
            '\n'
            'Test Status: PASSED\n'
            f'Test Type: {test_type}\n'
            'Test: 316 - Test Result: 2569942'
        )
        ticket_initial_note_1 = {
            'text': ticket_initial_note_1_text,
            'date': parse('2020-12-10T12:01:32Z'),
        }
        ticket_initial_notes = [
            ticket_initial_note_1
        ]

        ticket_new_note_1 = {
            'text': (
                '#*Automation Engine*#\n'
                'Service Affecting (Ixia)\n'
                'Device Name: ATL_XR2000_1\n'
                '\n'
                'Trouble: Jitter Max (ms)\n'
                'Threshold: 8\n'
                'Value: 8.3\n'
                '\n'
                'Test Status: FAILED\n'
                'Test Type: ICMP Test\n'
                'Test: 316 - Test Result: 2569999'
            ),
            'date': parse('2020-12-10T13:01:32Z'),
        }
        ticket_new_notes = [
            ticket_new_note_1,
        ]
        all_ticket_notes = ticket_initial_notes + ticket_new_notes

        ticket_id = 12345
        detail_id = 67890
        tickets_mapping = {
            serial_number: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }

        failed_test_note = 'This is a FAILED note'

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.create_affecting_ticket = CoroutineMock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type = Mock(return_value=ticket_initial_note_1)
        affecting_monitor._is_passed_note = Mock(return_value=True)
        affecting_monitor._build_failed_note = Mock(return_value=failed_test_note)

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.object(affecting_monitoring_module, 'datetime', new=datetime_mock):
            await affecting_monitor._process_failed_test_result(
                test_result=test_result, device_cached_info=device_cached_info
            )

        bruin_repository.create_affecting_ticket.assert_not_awaited()
        affecting_monitor._get_last_note_by_test_type.assert_called_once_with(all_ticket_notes, test_type)
        affecting_monitor._is_passed_note.assert_called_once_with(ticket_initial_note_1_text)
        affecting_monitor._build_failed_note.assert_called_once_with(test_result)
        updated_new_notes = [
            ticket_new_note_1,
            {
                'text': failed_test_note,
                'date': current_datetime,
            }
        ]
        assert affecting_monitor._tickets_by_serial == {
            serial_number: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': updated_new_notes,
            }
        }

    @pytest.mark.asyncio
    async def process_failed_test_result_with_unresolved_ticket_detail_found_and_failed_note_found_for_test_type_test(
            self):
        serial_number = 'B827EB76A8DE'

        test_type = 'Network KPI'
        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": test_type,
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "6",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Failed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        client_id = 9994
        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }

        ticket_initial_note_1_text = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            'Device Name: ATL_XR2000_1\n'
            '\n'
            'Trouble: Jitter Max (ms)\n'
            'Threshold: 8\n'
            'Value: 8.3\n'
            '\n'
            'Test Status: PASSED\n'
            f'Test Type: {test_type}\n'
            'Test: 316 - Test Result: 2569942'
        )
        ticket_initial_note_1 = {
            'text': ticket_initial_note_1_text,
            'date': parse('2020-12-10T12:01:32Z'),
        }
        ticket_initial_notes = [
            ticket_initial_note_1,
        ]

        ticket_new_notes = [
            {
                'text': (
                    '#*Automation Engine*#\n'
                    'Service Affecting (Ixia)\n'
                    'Device Name: ATL_XR2000_1\n'
                    '\n'
                    'Trouble: Jitter Max (ms)\n'
                    'Threshold: 8\n'
                    'Value: 8.3\n'
                    '\n'
                    'Test Status: FAILED\n'
                    'Test Type: ICMP Test\n'
                    'Test: 316 - Test Result: 2569999'
                ),
                'date': parse('2020-12-10T13:01:32Z'),
            },
        ]
        all_ticket_notes = ticket_initial_notes + ticket_new_notes

        ticket_id = 12345
        detail_id = 67890
        tickets_mapping = {
            serial_number: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }

        failed_test_note = 'This is a FAILED note'

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.create_affecting_ticket = CoroutineMock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type = Mock(return_value=ticket_initial_note_1)
        affecting_monitor._is_passed_note = Mock(return_value=False)
        affecting_monitor._build_failed_note = Mock(return_value=failed_test_note)

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.object(affecting_monitoring_module, 'datetime', new=datetime_mock):
            await affecting_monitor._process_failed_test_result(
                test_result=test_result, device_cached_info=device_cached_info
            )

        bruin_repository.create_affecting_ticket.assert_not_awaited()
        affecting_monitor._get_last_note_by_test_type.assert_called_once_with(all_ticket_notes, test_type)
        affecting_monitor._is_passed_note.assert_called_once_with(ticket_initial_note_1_text)
        affecting_monitor._build_failed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial is tickets_mapping

    @pytest.mark.asyncio
    async def process_failed_test_result_with_resolved_ticket_detail_found_and_unsuccessful_unresolve_test(self):
        serial_number = 'B827EB76A8DE'

        test_type = 'Network KPI'
        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": test_type,
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "6",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Failed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        client_id = 9994
        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }

        ticket_initial_notes = [
            {
                'text': (
                    '#*Automation Engine*#\n'
                    'Service Affecting (Ixia)\n'
                    'Device Name: ATL_XR2000_1\n'
                    '\n'
                    'Trouble: Jitter Max (ms)\n'
                    'Threshold: 8\n'
                    'Value: 8.3\n'
                    '\n'
                    'Test Status: PASSED\n'
                    f'Test Type: {test_type}\n'
                    'Test: 316 - Test Result: 2569942'
                ),
                'date': parse('2020-12-10T12:01:32Z'),
            },
        ]

        ticket_new_note_1 = {
            'text': (
                '#*Automation Engine*#\n'
                'Service Affecting (Ixia)\n'
                'Device Name: ATL_XR2000_1\n'
                '\n'
                'Trouble: Jitter Max (ms)\n'
                'Threshold: 8\n'
                'Value: 8.3\n'
                '\n'
                'Test Status: FAILED\n'
                'Test Type: ICMP Test\n'
                'Test: 316 - Test Result: 2569999'
            ),
            'date': parse('2020-12-10T13:01:32Z'),
        }
        ticket_new_notes = [
            ticket_new_note_1,
        ]

        ticket_id = 12345
        detail_id = 67890
        tickets_mapping = {
            serial_number: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': True,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }

        failed_test_note = 'This is a FAILED note'

        unresolve_detail_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.create_affecting_ticket = CoroutineMock()
        bruin_repository.unresolve_ticket_detail = CoroutineMock(return_value=unresolve_detail_response)

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type = Mock()
        affecting_monitor._is_passed_note = Mock()
        affecting_monitor._build_failed_note = Mock(return_value=failed_test_note)

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.object(affecting_monitoring_module, 'datetime', new=datetime_mock):
            await affecting_monitor._process_failed_test_result(
                test_result=test_result, device_cached_info=device_cached_info
            )

        bruin_repository.create_affecting_ticket.assert_not_awaited()
        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        bruin_repository.unresolve_ticket_detail.assert_awaited_once_with(ticket_id, detail_id)
        affecting_monitor._build_failed_note.assert_called_once_with(test_result)
        updated_new_notes = [
            ticket_new_note_1,
            {
                'text': failed_test_note,
                'date': current_datetime,
            }
        ]
        assert affecting_monitor._tickets_by_serial == {
            serial_number: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': True,
                'initial_notes': ticket_initial_notes,
                'new_notes': updated_new_notes,
            }
        }

    @pytest.mark.asyncio
    async def process_failed_test_result_with_resolved_ticket_detail_found_and_successful_unresolve_test(self):
        serial_number = 'B827EB76A8DE'

        test_type = 'Network KPI'
        test_result = {
            "summary": {
                "id": "DlfsJHcB0dCO9W0n6nGC",
                "date": "2020-12-10T12:01:32Z",
                "duration": "30",
                "status": "Failed",
                "reasonCause": "",
                "module": "MESH",
                "testId": "335",
                "testType": test_type,
                "probeFrom": "Vi_Pi_DRI test",
                "probeTo": "V_Basement",
                "mesh": 1,
                "testOptions": "DSCP Setting: Best Effort ",
                "meshId": "CORE",
                "testTag": "",
                "userId": 6,
            },
            "metrics": [
                {
                    "metric": "Jitter (ms)",
                    "pairName": "KPI from->to",
                    "value": "6",
                    "threshold": "5",
                    "thresholdType": "0",
                    "status": "Failed"
                },
                {
                    "metric": "Loss",
                    "pairName": "KPI from->to",
                    "value": "0.1",
                    "threshold": "0.2",
                    "thresholdType": "0",
                    "status": "Passed"
                },
            ]
        }

        client_id = 9994
        device_cached_info = {
            "probe_uid": 'b8:27:eb:76:a8:de',
            "serial_number": serial_number,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }

        ticket_initial_notes = [
            {
                'text': (
                    '#*Automation Engine*#\n'
                    'Service Affecting (Ixia)\n'
                    'Device Name: ATL_XR2000_1\n'
                    '\n'
                    'Trouble: Jitter Max (ms)\n'
                    'Threshold: 8\n'
                    'Value: 8.3\n'
                    '\n'
                    'Test Status: PASSED\n'
                    f'Test Type: {test_type}\n'
                    'Test: 316 - Test Result: 2569942'
                ),
                'date': parse('2020-12-10T12:01:32Z'),
            },
        ]

        ticket_new_note_1 = {
            'text': (
                '#*Automation Engine*#\n'
                'Service Affecting (Ixia)\n'
                'Device Name: ATL_XR2000_1\n'
                '\n'
                'Trouble: Jitter Max (ms)\n'
                'Threshold: 8\n'
                'Value: 8.3\n'
                '\n'
                'Test Status: FAILED\n'
                'Test Type: ICMP Test\n'
                'Test: 316 - Test Result: 2569999'
            ),
            'date': parse('2020-12-10T13:01:32Z'),
        }
        ticket_new_notes = [
            ticket_new_note_1,
        ]

        ticket_id = 12345
        detail_id = 67890
        tickets_mapping = {
            serial_number: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': True,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }

        failed_test_note = 'This is a FAILED note'

        unresolve_detail_response = {
            'body': 'ok',
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        hawkeye_repository = Mock()
        customer_cache_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.create_affecting_ticket = CoroutineMock()
        bruin_repository.unresolve_ticket_detail = CoroutineMock(return_value=unresolve_detail_response)

        notifications_repository = Mock()
        notifications_repository.notify_ticket_detail_was_unresolved = CoroutineMock()

        affecting_monitor = AffectingMonitor(logger, scheduler, config, bruin_repository, hawkeye_repository,
                                             notifications_repository, customer_cache_repository, utils_repository)
        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type = Mock()
        affecting_monitor._is_passed_note = Mock()
        affecting_monitor._build_failed_note = Mock(return_value=failed_test_note)

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.object(affecting_monitoring_module, 'datetime', new=datetime_mock):
            await affecting_monitor._process_failed_test_result(
                test_result=test_result, device_cached_info=device_cached_info
            )

        bruin_repository.create_affecting_ticket.assert_not_awaited()
        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        bruin_repository.unresolve_ticket_detail.assert_awaited_once_with(ticket_id, detail_id)
        notifications_repository.notify_ticket_detail_was_unresolved.assert_awaited_once_with(ticket_id, serial_number)
        affecting_monitor._build_failed_note.assert_called_once_with(test_result)
        updated_new_notes = [
            ticket_new_note_1,
            {
                'text': failed_test_note,
                'date': current_datetime,
            }
        ]
        assert affecting_monitor._tickets_by_serial == {
            serial_number: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': updated_new_notes,
            }
        }
