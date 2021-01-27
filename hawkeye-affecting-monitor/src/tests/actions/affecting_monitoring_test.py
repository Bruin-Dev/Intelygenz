from datetime import datetime
from dateutil.parser import parse
from unittest.mock import call
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from shortuuid import uuid
from pytz import utc

from application.actions import affecting_monitoring as affecting_monitoring_module
from application.actions.affecting_monitoring import AffectingMonitor
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(affecting_monitoring_module, 'uuid', return_value=uuid_)


class TestServiceAffectingMonitor:
    def instance_test(self, affecting_monitor, logger, scheduler, bruin_repository, hawkeye_repository,
                      customer_cache_repository, notifications_repository, utils_repository):
        assert affecting_monitor._logger is logger
        assert affecting_monitor._scheduler is scheduler
        assert affecting_monitor._config is testconfig
        assert affecting_monitor._bruin_repository is bruin_repository
        assert affecting_monitor._hawkeye_repository is hawkeye_repository
        assert affecting_monitor._notifications_repository is notifications_repository
        assert affecting_monitor._customer_cache_repository is customer_cache_repository
        assert affecting_monitor._utils_repository is utils_repository

        assert affecting_monitor._tickets_by_serial == {}

    @pytest.mark.asyncio
    async def start_hawkeye_affecting_monitoring_with_exec_on_start_test(self, affecting_monitor):
        scheduler = affecting_monitor._scheduler
        config = affecting_monitor._config

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
    async def start_hawkeye_affecting_monitoring_with_no_exec_on_start_test(self, affecting_monitor):
        scheduler = affecting_monitor._scheduler
        config = affecting_monitor._config

        await affecting_monitor.start_hawkeye_affecting_monitoring(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            affecting_monitor._affecting_monitoring_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['affecting_monitor'],
            next_run_time=undefined,
            replace_existing=False,
            id='_hawkeye_affecting_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_hawkeye_affecting_monitoring_with_job_id_already_executing_test(self, affecting_monitor):
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        scheduler = affecting_monitor._scheduler
        config = affecting_monitor._config

        scheduler.add_job.side_effect = exception_instance

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
    async def affecting_monitoring_process_ok_test(self, affecting_monitor,
                                                   serial_number_1,
                                                   bruin_client_id,
                                                   get_customer_cache_200_response,
                                                   customer_cache,
                                                   device_cached_info_1,
                                                   get_tests_results_under_probe_uid_1_200_response,
                                                   probe_1_uid,
                                                   passed_icmp_test_result_1_on_2020_01_16,
                                                   passed_icmp_test_result_2_on_2020_01_17,
                                                   failed_icmp_test_result_1_on_2020_01_18,
                                                   failed_icmp_test_result_2_on_2020_01_19,
                                                   error_icmp_test_result_1_on_2020_01_20,
                                                   error_icmp_test_result_2_on_2020_01_21,
                                                   passed_network_kpi_test_result_1_on_2020_01_22,
                                                   failed_network_kpi_test_result_2_on_2020_01_23,
                                                   ):
        probe_uids = [cached_info['probe_uid'] for cached_info in customer_cache]
        tests_results_by_probe_1_uid = get_tests_results_under_probe_uid_1_200_response['body']

        device_1_tests_results = [
            passed_icmp_test_result_1_on_2020_01_16,
            passed_icmp_test_result_2_on_2020_01_17,
            failed_icmp_test_result_1_on_2020_01_18,
            failed_icmp_test_result_2_on_2020_01_19,
            error_icmp_test_result_1_on_2020_01_20,
            error_icmp_test_result_2_on_2020_01_21,
            passed_network_kpi_test_result_1_on_2020_01_22,
            failed_network_kpi_test_result_2_on_2020_01_23,
        ]
        tests_results_sorted_by_date_asc = {
            probe_1_uid: device_1_tests_results,
        }

        cached_device_1_with_tests_results = {
            'cached_info': device_cached_info_1,
            'tests_results': device_1_tests_results,
        }

        affecting_monitor._hawkeye_repository.get_tests_results_for_affecting_monitoring.return_value = \
            get_tests_results_under_probe_uid_1_200_response
        affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.return_value = \
            get_customer_cache_200_response

        await affecting_monitor._affecting_monitoring_process()

        affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        affecting_monitor._get_all_probe_uids_from_cache.assert_called_once_with(customer_cache)
        affecting_monitor._hawkeye_repository.get_tests_results_for_affecting_monitoring.assert_awaited_once_with(
            probe_uids=probe_uids
        )
        affecting_monitor._get_tests_results_sorted_by_date_asc.assert_called_once_with(tests_results_by_probe_1_uid)
        affecting_monitor._map_cached_devices_with_tests_results.assert_called_once_with(
            customer_cache, tests_results_sorted_by_date_asc,
        )
        affecting_monitor._add_device_to_tickets_mapping.assert_awaited_once_with(
            serial_number=serial_number_1, bruin_client_id=bruin_client_id,
        )
        affecting_monitor._process_device.assert_awaited_once_with(cached_device_1_with_tests_results)

    @pytest.mark.asyncio
    async def affecting_monitoring_process_with_retrieval_of_customer_cache_returning_non_200_status_test(
            self, affecting_monitor, get_customer_cache_202_response):
        affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.return_value = \
            get_customer_cache_202_response

        await affecting_monitor._affecting_monitoring_process()

        affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        affecting_monitor._get_all_probe_uids_from_cache.assert_not_called()
        affecting_monitor._process_device.assert_not_awaited()

    @pytest.mark.asyncio
    async def affecting_monitoring_process_with_retrieval_of_tests_results_returning_non_2xx_status_test(
            self, affecting_monitor, get_customer_cache_200_response, hawkeye_500_response):
        customer_cache = get_customer_cache_200_response['body']
        probe_uids = [cached_info['probe_uid'] for cached_info in customer_cache]

        affecting_monitor._hawkeye_repository.get_tests_results_for_affecting_monitoring.return_value = \
            hawkeye_500_response
        affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.return_value = \
            get_customer_cache_200_response
        affecting_monitor._get_all_probe_uids_from_cache.return_value = probe_uids

        await affecting_monitor._affecting_monitoring_process()

        affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        affecting_monitor._get_all_probe_uids_from_cache.assert_called_once_with(customer_cache)
        affecting_monitor._hawkeye_repository.get_tests_results_for_affecting_monitoring.assert_awaited_once_with(
            probe_uids=probe_uids
        )
        affecting_monitor._get_tests_results_sorted_by_date_asc.assert_not_called()
        affecting_monitor._map_cached_devices_with_tests_results.assert_not_called()
        affecting_monitor._process_device.assert_not_awaited()

    def get_all_probe_uids_from_cache_test(self, customer_cache):
        expected = [cached_info['probe_uid'] for cached_info in customer_cache]
        result = AffectingMonitor._get_all_probe_uids_from_cache(customer_cache)
        assert result == expected

    def get_tests_results_sorted_by_date_asc_test(self, probe_1_uid,
                                                  passed_icmp_test_result_1_on_2020_01_16,
                                                  passed_icmp_test_result_2_on_2020_01_17,
                                                  failed_icmp_test_result_1_on_2020_01_18,
                                                  failed_icmp_test_result_2_on_2020_01_19):
        tests_results = {
            probe_1_uid: [
                failed_icmp_test_result_1_on_2020_01_18,
                passed_icmp_test_result_1_on_2020_01_16,
                failed_icmp_test_result_2_on_2020_01_19,
                passed_icmp_test_result_2_on_2020_01_17,
            ]
        }

        result = AffectingMonitor._get_tests_results_sorted_by_date_asc(tests_results)
        expected = {
            probe_1_uid: [
                passed_icmp_test_result_1_on_2020_01_16,
                passed_icmp_test_result_2_on_2020_01_17,
                failed_icmp_test_result_1_on_2020_01_18,
                failed_icmp_test_result_2_on_2020_01_19,
            ]
        }
        assert result == expected

    def map_cached_devices_with_tests_results_test(self, customer_cache,
                                                   device_cached_info_1,
                                                   probe_1_uid,
                                                   tests_results):
        tests_results_by_probe_1_uid = {
            probe_1_uid: tests_results
        }

        result = AffectingMonitor._map_cached_devices_with_tests_results(customer_cache, tests_results_by_probe_1_uid)
        expected = [
            {
                'cached_info': device_cached_info_1,
                'tests_results': tests_results,
            }
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def add_device_to_tickets_mapping_with_resolved_ticket_detail_found_test(
            self, affecting_monitor, bruin_client_id, serial_number_1, get_open_affecting_ticket_200_response,
            ticket_detail_resolved_for_serial_1, ticket_detail_in_progress_for_serial_2,
            ticket_note_for_serial_1_posted_on_2020_01_16, ticket_note_for_serial_1_posted_on_2020_01_17,
            ticket_note_for_serial_2_posted_on_2020_01_16, ticket_note_for_serial_2_posted_on_2020_01_17,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_16, ticket_note_for_serial_1_and_2_posted_on_2020_01_17):
        ticket_id = get_open_affecting_ticket_200_response['body'][0]['ticketID']
        ticket_detail_resolved_for_serial_1_id = ticket_detail_resolved_for_serial_1['detailID']

        ticket_details_list = [
            ticket_detail_resolved_for_serial_1,
            ticket_detail_in_progress_for_serial_2,
        ]

        ticket_notes = [
            ticket_note_for_serial_1_posted_on_2020_01_17,
            ticket_note_for_serial_2_posted_on_2020_01_16,
            ticket_note_for_serial_1_posted_on_2020_01_16,
            ticket_note_for_serial_2_posted_on_2020_01_17,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_17,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_16,
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
            ticket_note_for_serial_1_posted_on_2020_01_17,
            ticket_note_for_serial_1_posted_on_2020_01_16,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_17,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_16,
        ]

        affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = \
            get_open_affecting_ticket_200_response
        affecting_monitor._bruin_repository.get_ticket_details.return_value = \
            ticket_details_response

        await affecting_monitor._add_device_to_tickets_mapping(
            serial_number=serial_number_1, bruin_client_id=bruin_client_id
        )

        affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id=bruin_client_id, service_number=serial_number_1
        )
        affecting_monitor._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        affecting_monitor._find_ticket_detail_by_serial.assert_called_once_with(ticket_details_list, serial_number_1)
        affecting_monitor._find_ticket_notes_by_serial.assert_called_once_with(ticket_notes, serial_number_1)
        affecting_monitor._get_notes_sorted_by_date_and_id_asc.assert_called_once_with(relevant_notes)

        expected_tickets_mapping = {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': ticket_detail_resolved_for_serial_1_id,
                'is_detail_resolved': True,
                'initial_notes': [
                    {
                        'text': ticket_note_for_serial_1_posted_on_2020_01_16['noteValue'],
                        'date': parse(ticket_note_for_serial_1_posted_on_2020_01_16['createdDate']).astimezone(utc),
                    },
                    {
                        'text': ticket_note_for_serial_1_and_2_posted_on_2020_01_16['noteValue'],
                        'date': parse(ticket_note_for_serial_1_and_2_posted_on_2020_01_16['createdDate']).astimezone(
                            utc
                        ),
                    },
                    {
                        'text': ticket_note_for_serial_1_posted_on_2020_01_17['noteValue'],
                        'date': parse(ticket_note_for_serial_1_posted_on_2020_01_17['createdDate']).astimezone(utc),
                    },
                    {
                        'text': ticket_note_for_serial_1_and_2_posted_on_2020_01_17['noteValue'],
                        'date': parse(ticket_note_for_serial_1_and_2_posted_on_2020_01_17['createdDate']).astimezone(
                            utc
                        ),
                    },
                ],
                'new_notes': [],
            },
        }
        assert affecting_monitor._tickets_by_serial == expected_tickets_mapping

    @pytest.mark.asyncio
    async def add_device_to_tickets_mapping_with_unresolved_ticket_detail_found_test(
            self, affecting_monitor, bruin_client_id, serial_number_1, get_open_affecting_ticket_200_response,
            ticket_detail_in_progress_for_serial_1, ticket_detail_in_progress_for_serial_2,
            ticket_note_for_serial_1_posted_on_2020_01_16, ticket_note_for_serial_1_posted_on_2020_01_17,
            ticket_note_for_serial_2_posted_on_2020_01_16, ticket_note_for_serial_2_posted_on_2020_01_17,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_16, ticket_note_for_serial_1_and_2_posted_on_2020_01_17):
        ticket_id = get_open_affecting_ticket_200_response['body'][0]['ticketID']
        ticket_detail_resolved_for_serial_1_id = ticket_detail_in_progress_for_serial_1['detailID']

        ticket_details_list = [
            ticket_detail_in_progress_for_serial_1,
            ticket_detail_in_progress_for_serial_2,
        ]

        ticket_notes = [
            ticket_note_for_serial_1_posted_on_2020_01_17,
            ticket_note_for_serial_2_posted_on_2020_01_16,
            ticket_note_for_serial_1_posted_on_2020_01_16,
            ticket_note_for_serial_2_posted_on_2020_01_17,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_17,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_16,
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
            ticket_note_for_serial_1_posted_on_2020_01_17,
            ticket_note_for_serial_1_posted_on_2020_01_16,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_17,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_16,
        ]

        affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = \
            get_open_affecting_ticket_200_response
        affecting_monitor._bruin_repository.get_ticket_details.return_value = \
            ticket_details_response

        await affecting_monitor._add_device_to_tickets_mapping(
            serial_number=serial_number_1, bruin_client_id=bruin_client_id
        )

        affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id=bruin_client_id, service_number=serial_number_1
        )
        affecting_monitor._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        affecting_monitor._find_ticket_detail_by_serial.assert_called_once_with(ticket_details_list, serial_number_1)
        affecting_monitor._find_ticket_notes_by_serial.assert_called_once_with(ticket_notes, serial_number_1)
        affecting_monitor._get_notes_sorted_by_date_and_id_asc.assert_called_once_with(relevant_notes)

        expected_tickets_mapping = {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': ticket_detail_resolved_for_serial_1_id,
                'is_detail_resolved': False,
                'initial_notes': [
                    {
                        'text': ticket_note_for_serial_1_posted_on_2020_01_16['noteValue'],
                        'date': parse(ticket_note_for_serial_1_posted_on_2020_01_16['createdDate']).astimezone(utc),
                    },
                    {
                        'text': ticket_note_for_serial_1_and_2_posted_on_2020_01_16['noteValue'],
                        'date': parse(ticket_note_for_serial_1_and_2_posted_on_2020_01_16['createdDate']).astimezone(
                            utc
                        ),
                    },
                    {
                        'text': ticket_note_for_serial_1_posted_on_2020_01_17['noteValue'],
                        'date': parse(ticket_note_for_serial_1_posted_on_2020_01_17['createdDate']).astimezone(utc),
                    },
                    {
                        'text': ticket_note_for_serial_1_and_2_posted_on_2020_01_17['noteValue'],
                        'date': parse(ticket_note_for_serial_1_and_2_posted_on_2020_01_17['createdDate']).astimezone(
                            utc
                        ),
                    },
                ],
                'new_notes': [],
            },
        }
        assert affecting_monitor._tickets_by_serial == expected_tickets_mapping

    @pytest.mark.asyncio
    async def add_device_to_tickets_mapping_with_retrieval_of_open_affecting_tickets_returning_non_2xx_status_test(
            self, affecting_monitor, bruin_client_id, serial_number_1, bruin_500_response):
        affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = bruin_500_response

        await affecting_monitor._add_device_to_tickets_mapping(
            serial_number=serial_number_1, bruin_client_id=bruin_client_id
        )

        affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id=bruin_client_id, service_number=serial_number_1
        )
        affecting_monitor._bruin_repository.get_ticket_details.assert_not_awaited()

        expected_tickets_mapping = {}
        assert affecting_monitor._tickets_by_serial == expected_tickets_mapping

    @pytest.mark.asyncio
    async def add_device_to_tickets_mapping_with_no_affecting_tickets_found_test(
            self, affecting_monitor, bruin_client_id, serial_number_1, get_open_affecting_ticket_empty_response):
        affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = \
            get_open_affecting_ticket_empty_response

        await affecting_monitor._add_device_to_tickets_mapping(
            serial_number=serial_number_1, bruin_client_id=bruin_client_id
        )

        affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id=bruin_client_id, service_number=serial_number_1
        )

        expected_tickets_mapping = {
            serial_number_1: {}
        }
        assert affecting_monitor._tickets_by_serial == expected_tickets_mapping

    @pytest.mark.asyncio
    async def add_device_to_tickets_mapping_with_retrieval_of_ticket_details_returning_non_2xx_status_test(
            self, affecting_monitor, bruin_client_id, serial_number_1, get_open_affecting_ticket_200_response,
            bruin_500_response):
        ticket_id = get_open_affecting_ticket_200_response['body'][0]['ticketID']

        affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = \
            get_open_affecting_ticket_200_response
        affecting_monitor._bruin_repository.get_ticket_details.return_value = bruin_500_response

        await affecting_monitor._add_device_to_tickets_mapping(
            serial_number=serial_number_1, bruin_client_id=bruin_client_id
        )

        affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id=bruin_client_id, service_number=serial_number_1
        )
        affecting_monitor._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        affecting_monitor._find_ticket_notes_by_serial.assert_not_called()
        affecting_monitor._get_notes_sorted_by_date_and_id_asc.assert_not_called()

        expected_tickets_mapping = {}
        assert affecting_monitor._tickets_by_serial == expected_tickets_mapping

    def find_ticket_detail_by_serial_test(self, affecting_monitor, serial_number_1,
                                          ticket_detail_in_progress_for_serial_1,
                                          ticket_detail_in_progress_for_serial_2):
        ticket_details_list = [
            ticket_detail_in_progress_for_serial_1,
            ticket_detail_in_progress_for_serial_2,
        ]

        result = affecting_monitor._find_ticket_detail_by_serial(ticket_details_list, serial_number_1)
        assert result == ticket_detail_in_progress_for_serial_1

    def find_ticket_notes_by_serial_test(self, serial_number_1,
                                         ticket_note_for_serial_1_posted_on_2020_01_16,
                                         ticket_note_for_serial_1_posted_on_2020_01_17,
                                         ticket_note_for_serial_2_posted_on_2020_01_16,
                                         ticket_note_for_serial_2_posted_on_2020_01_17,
                                         ticket_note_for_serial_1_and_2_posted_on_2020_01_16,
                                         ticket_note_for_serial_1_and_2_posted_on_2020_01_17):
        ticket_notes = [
            ticket_note_for_serial_1_posted_on_2020_01_16,
            ticket_note_for_serial_1_posted_on_2020_01_17,
            ticket_note_for_serial_2_posted_on_2020_01_16,
            ticket_note_for_serial_2_posted_on_2020_01_17,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_16,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_17,
        ]

        result = AffectingMonitor._find_ticket_notes_by_serial(ticket_notes, serial_number_1)

        expected = [
            ticket_note_for_serial_1_posted_on_2020_01_16,
            ticket_note_for_serial_1_posted_on_2020_01_17,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_16,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_17,
        ]
        assert result == expected

    def get_notes_sorted_by_date_and_id_asc_test(self, ticket_note_for_serial_1_posted_on_2020_01_16,
                                                 ticket_note_for_serial_1_posted_on_2020_01_17,
                                                 ticket_note_for_serial_2_posted_on_2020_01_16,
                                                 ticket_note_for_serial_2_posted_on_2020_01_17,
                                                 ticket_note_for_serial_1_and_2_posted_on_2020_01_16,
                                                 ticket_note_for_serial_1_and_2_posted_on_2020_01_17):
        ticket_notes = [
            ticket_note_for_serial_2_posted_on_2020_01_16,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_17,
            ticket_note_for_serial_2_posted_on_2020_01_17,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_16,
            ticket_note_for_serial_1_posted_on_2020_01_17,
            ticket_note_for_serial_1_posted_on_2020_01_16,
        ]

        result = AffectingMonitor._get_notes_sorted_by_date_and_id_asc(ticket_notes)

        expected = [
            ticket_note_for_serial_1_posted_on_2020_01_16,
            ticket_note_for_serial_2_posted_on_2020_01_16,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_16,
            ticket_note_for_serial_1_posted_on_2020_01_17,
            ticket_note_for_serial_2_posted_on_2020_01_17,
            ticket_note_for_serial_1_and_2_posted_on_2020_01_17,
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def process_device_test(self, affecting_monitor, serial_number_1, device_cached_info_1,
                                  passed_icmp_test_result_1_on_2020_01_16, passed_icmp_test_result_2_on_2020_01_17,
                                  failed_icmp_test_result_1_on_2020_01_18, failed_icmp_test_result_2_on_2020_01_19):
        tests_results = [
            passed_icmp_test_result_1_on_2020_01_16,
            passed_icmp_test_result_2_on_2020_01_17,
            failed_icmp_test_result_1_on_2020_01_18,
            failed_icmp_test_result_2_on_2020_01_19,
        ]

        device_info = {
            'cached_info': device_cached_info_1,
            'tests_results': tests_results,
        }

        # This manager is the only way to check the call order of multiple, different mocks
        manager_mock = Mock()
        manager_mock._process_passed_test_result = affecting_monitor._process_passed_test_result
        manager_mock._process_failed_test_result = affecting_monitor._process_failed_test_result

        await affecting_monitor._process_device(device_info)

        expected_calls_ordered = [
            call._process_passed_test_result(
                test_result=passed_icmp_test_result_1_on_2020_01_16,
                device_cached_info=device_cached_info_1
            ),
            call._process_passed_test_result(
                test_result=passed_icmp_test_result_2_on_2020_01_17,
                device_cached_info=device_cached_info_1
            ),
            call._process_failed_test_result(
                test_result=failed_icmp_test_result_1_on_2020_01_18,
                device_cached_info=device_cached_info_1
            ),
            call._process_failed_test_result(
                test_result=failed_icmp_test_result_2_on_2020_01_19,
                device_cached_info=device_cached_info_1
            ),
        ]
        assert manager_mock.mock_calls == expected_calls_ordered
        affecting_monitor._append_new_notes_for_device.assert_awaited_once_with(serial_number_1)

    @pytest.mark.asyncio
    async def append_new_notes_for_device_with_serial_number_missing_in_tickets_mapping_test(
            self, affecting_monitor, serial_number_1):
        tickets_mapping = {}
        affecting_monitor._tickets_by_serial = tickets_mapping

        await affecting_monitor._append_new_notes_for_device(serial_number_1)

        affecting_monitor._bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_new_notes_for_device_with_no_notes_to_append_test(self, affecting_monitor, serial_number_1,
                                                                       note_text_about_passed_icmp_test):
        ticket_initial_notes = [
            {
                'text': note_text_about_passed_icmp_test,
                'date': parse('2020-12-10T12:01:32Z'),
            }
        ]
        ticket_new_notes = []

        ticket_id = 12345
        ticket_detail_id = 67890
        tickets_mapping = {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': ticket_detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }
        affecting_monitor._tickets_by_serial = tickets_mapping

        await affecting_monitor._append_new_notes_for_device(serial_number_1)

        affecting_monitor._bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_new_notes_for_device_with_notes_to_append_and_environment_not_being_production_test(
            self, affecting_monitor, serial_number_1, note_text_about_passed_icmp_test,
            note_text_about_failed_icmp_test, note_text_about_passed_network_kpi_test,
            note_text_about_failed_network_kpi_test):
        ticket_initial_notes = [
            {
                'text': note_text_about_passed_icmp_test,
                'date': parse('2020-12-10T12:01:32Z'),
            }
        ]

        ticket_new_notes = [
            {
                'text': note_text_about_failed_network_kpi_test,
                'date': parse('2020-12-10T13:01:32Z'),
            },
            {
                'text': note_text_about_failed_icmp_test,
                'date': parse('2020-12-10T14:01:32Z'),
            },
            {
                'text': note_text_about_passed_icmp_test,
                'date': parse('2020-12-10T15:01:32Z'),
            },
            {
                'text': note_text_about_passed_network_kpi_test,
                'date': parse('2020-12-10T16:01:32Z'),
            },
        ]

        ticket_id = 12345
        ticket_detail_id = 67890
        tickets_mapping = {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': ticket_detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }
        affecting_monitor._tickets_by_serial = tickets_mapping

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await affecting_monitor._append_new_notes_for_device(serial_number_1)

        affecting_monitor._bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_new_notes_for_device_with_notes_to_append_test(
            self, affecting_monitor, serial_number_1, note_text_about_passed_icmp_test,
            note_text_about_failed_icmp_test, note_text_about_passed_network_kpi_test,
            note_text_about_failed_network_kpi_test):
        ticket_initial_notes = [
            {
                'text': note_text_about_passed_icmp_test,
                'date': parse('2020-12-10T12:01:32Z'),
            }
        ]

        ticket_new_notes = [
            {
                'text': note_text_about_failed_network_kpi_test,
                'date': parse('2020-12-10T13:01:32Z'),
            },
            {
                'text': note_text_about_failed_icmp_test,
                'date': parse('2020-12-10T14:01:32Z'),
            },
            {
                'text': note_text_about_passed_icmp_test,
                'date': parse('2020-12-10T15:01:32Z'),
            },
            {
                'text': note_text_about_passed_network_kpi_test,
                'date': parse('2020-12-10T16:01:32Z'),
            },
        ]

        ticket_id = 12345
        tickets_mapping = {
            serial_number_1: {
                'ticket_id': ticket_id,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }
        affecting_monitor._tickets_by_serial = tickets_mapping

        notes_payload = [
            {
                'text': note_text_about_failed_network_kpi_test,
                'service_number': serial_number_1,
            },
            {
                'text': note_text_about_failed_icmp_test,
                'service_number': serial_number_1,
            },
            {
                'text': note_text_about_passed_icmp_test,
                'service_number': serial_number_1,
            },
            {
                'text': note_text_about_passed_network_kpi_test,
                'service_number': serial_number_1,
            },
        ]

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await affecting_monitor._append_new_notes_for_device(serial_number_1)

        affecting_monitor._bruin_repository.append_multiple_notes_to_ticket.assert_awaited_once_with(
            ticket_id=ticket_id, notes=notes_payload
        )
        affecting_monitor._notifications_repository.notify_multiple_notes_were_posted_to_ticket.\
            assert_awaited_once_with(ticket_id, serial_number_1)

    def test_result_passed_test(self, passed_icmp_test_result_1_on_2020_01_16, failed_icmp_test_result_1_on_2020_01_18):
        result = AffectingMonitor._test_result_passed(passed_icmp_test_result_1_on_2020_01_16)
        assert result is True

        result = AffectingMonitor._test_result_passed(failed_icmp_test_result_1_on_2020_01_18)
        assert result is False

    def test_result_failed_test(self, passed_icmp_test_result_1_on_2020_01_16, failed_icmp_test_result_1_on_2020_01_18):
        result = AffectingMonitor._test_result_failed(failed_icmp_test_result_1_on_2020_01_18)
        assert result is True

        result = AffectingMonitor._test_result_failed(passed_icmp_test_result_1_on_2020_01_16)
        assert result is False

    def process_passed_test_result_with_serial_number_missing_in_tickets_mapping_test(
            self, affecting_monitor, device_cached_info_1, passed_icmp_test_result_1_on_2020_01_16):
        tickets_mapping = {}
        affecting_monitor._tickets_by_serial = tickets_mapping

        affecting_monitor._process_passed_test_result(
            test_result=passed_icmp_test_result_1_on_2020_01_16,
            device_cached_info=device_cached_info_1,
        )

        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_passed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial == tickets_mapping

    def process_passed_test_result_with_no_ticket_found_for_serial_test(
            self, affecting_monitor, serial_number_1, device_cached_info_1, passed_icmp_test_result_1_on_2020_01_16):
        tickets_mapping = {
            serial_number_1: {}
        }
        affecting_monitor._tickets_by_serial = tickets_mapping

        affecting_monitor._process_passed_test_result(
            test_result=passed_icmp_test_result_1_on_2020_01_16,
            device_cached_info=device_cached_info_1,
        )

        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_passed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial == tickets_mapping

    def process_passed_test_result_with_ticket_having_resolved_detail_found_for_serial_test(
            self, affecting_monitor, serial_number_1, device_cached_info_1, passed_icmp_test_result_1_on_2020_01_16,
            note_text_about_passed_icmp_test, note_text_about_failed_icmp_test):
        ticket_initial_notes = [
            {
                'text': note_text_about_passed_icmp_test,
                'date': parse('2020-12-10T12:01:32Z'),
            }
        ]
        ticket_new_notes = [
            {
                'text': note_text_about_failed_icmp_test,
                'date': parse('2020-12-10T13:01:32Z'),
            }
        ]

        tickets_mapping = {
            serial_number_1: {
                'ticket_id': 1234,
                'detail_id': 5678,
                'is_detail_resolved': True,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }
        affecting_monitor._tickets_by_serial = tickets_mapping

        affecting_monitor._process_passed_test_result(
            test_result=passed_icmp_test_result_1_on_2020_01_16,
            device_cached_info=device_cached_info_1,
        )

        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_passed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial == tickets_mapping

    def process_passed_test_result_with_no_notes_found_for_target_test_type_test(
            self, affecting_monitor, serial_number_1, test_type_network_kpi,
            device_cached_info_1, passed_network_kpi_test_result_1_on_2020_01_22,
            note_text_about_passed_icmp_test, note_text_about_failed_icmp_test):

        ticket_initial_notes = [
            {
                'text': note_text_about_passed_icmp_test,
                'date': parse('2020-12-10T12:01:32Z'),
            }
        ]
        ticket_new_notes = [
            {
                'text': note_text_about_failed_icmp_test,
                'date': parse('2020-12-10T13:01:32Z'),
            }
        ]
        all_ticket_notes = ticket_initial_notes + ticket_new_notes
        tickets_mapping = {
            serial_number_1: {
                'ticket_id': 1234,
                'detail_id': 5678,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }

        affecting_monitor._tickets_by_serial = tickets_mapping
        affecting_monitor._get_last_note_by_test_type.return_value = None

        affecting_monitor._process_passed_test_result(
            test_result=passed_network_kpi_test_result_1_on_2020_01_22,
            device_cached_info=device_cached_info_1,
        )

        affecting_monitor._get_last_note_by_test_type.assert_called_once_with(all_ticket_notes, test_type_network_kpi)
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_passed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial == tickets_mapping

    def process_passed_test_result_with_passed_note_found_test(
            self, affecting_monitor, serial_number_1, test_type_network_kpi,
            device_cached_info_1, passed_network_kpi_test_result_1_on_2020_01_22,
            note_text_about_passed_network_kpi_test, note_text_about_failed_icmp_test):

        ticket_initial_note_1 = {
            'text': note_text_about_passed_network_kpi_test,
            'date': parse('2020-12-10T12:01:32Z'),
        }
        ticket_initial_notes = [
            ticket_initial_note_1
        ]
        ticket_new_notes = [
            {
                'text': note_text_about_failed_icmp_test,
                'date': parse('2020-12-10T13:01:32Z'),
            }
        ]
        all_ticket_notes = ticket_initial_notes + ticket_new_notes

        tickets_mapping = {
            serial_number_1: {
                'ticket_id': 1234,
                'detail_id': 5678,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }
        affecting_monitor._tickets_by_serial = tickets_mapping

        affecting_monitor._process_passed_test_result(
            test_result=passed_network_kpi_test_result_1_on_2020_01_22,
            device_cached_info=device_cached_info_1,
        )

        affecting_monitor._get_last_note_by_test_type.assert_called_once_with(all_ticket_notes, test_type_network_kpi)
        affecting_monitor._is_passed_note.assert_called_once_with(note_text_about_passed_network_kpi_test)
        affecting_monitor._build_passed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial == tickets_mapping

    def process_passed_test_result_with_failed_note_found_test(
            self, affecting_monitor, serial_number_1, test_type_network_kpi,
            device_cached_info_1, passed_network_kpi_test_result_1_on_2020_01_22,
            note_text_about_failed_network_kpi_test, note_text_about_failed_icmp_test):

        ticket_initial_note_1 = {
            'text': note_text_about_failed_network_kpi_test,
            'date': parse('2020-12-10T12:01:32Z'),
        }
        ticket_initial_notes = [
            ticket_initial_note_1
        ]

        ticket_new_note_1 = {
            'text': note_text_about_failed_icmp_test,
            'date': parse('2020-12-10T13:01:32Z'),
        }
        ticket_new_notes = [
            ticket_new_note_1
        ]
        all_ticket_notes = ticket_initial_notes + ticket_new_notes

        ticket_id = 1234
        tickets_mapping = {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': 5678,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }
        affecting_monitor._tickets_by_serial = tickets_mapping

        passed_test_note = 'This is a PASSED note'
        affecting_monitor._build_passed_note.return_value = passed_test_note

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.object(affecting_monitoring_module, 'datetime', new=datetime_mock):
            affecting_monitor._process_passed_test_result(
                test_result=passed_network_kpi_test_result_1_on_2020_01_22,
                device_cached_info=device_cached_info_1,
            )

        affecting_monitor._get_last_note_by_test_type.assert_called_once_with(all_ticket_notes, test_type_network_kpi)
        affecting_monitor._is_passed_note.assert_called_once_with(note_text_about_failed_network_kpi_test)
        affecting_monitor._build_passed_note.assert_called_once_with(passed_network_kpi_test_result_1_on_2020_01_22)

        updated_new_notes = [
            ticket_new_note_1,
            {
                'text': passed_test_note,
                'date': current_datetime,
            }
        ]
        assert affecting_monitor._tickets_by_serial == {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': 5678,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': updated_new_notes,
            }
        }

    def get_last_note_by_test_type_test(self, affecting_monitor, test_type_network_kpi,
                                        note_text_about_passed_network_kpi_test,
                                        note_text_about_passed_icmp_test, ):
        note_1 = {
            'text': note_text_about_passed_network_kpi_test,
            'date': parse('2020-12-10T12:01:32Z'),
        }
        note_2 = {
            'text': note_text_about_passed_icmp_test,
            'date': parse('2020-12-10T12:01:32Z'),
        }
        note_3 = {
            'text': note_text_about_passed_network_kpi_test,
            'date': parse('2020-12-10T12:01:32Z'),
        }
        notes = [
            note_1,
            note_2,
            note_3,
        ]

        result = affecting_monitor._get_last_note_by_test_type(notes, test_type_network_kpi)
        assert result == note_3

    def is_passed_note_test(self, note_text_about_passed_icmp_test, note_text_about_failed_icmp_test):
        result = AffectingMonitor._is_passed_note(note_text_about_passed_icmp_test)
        assert result is True

        result = AffectingMonitor._is_passed_note(note_text_about_failed_icmp_test)
        assert result is False

    def build_passed_note_test(self, passed_network_kpi_test_result_1_on_2020_01_22):
        test_result_id = passed_network_kpi_test_result_1_on_2020_01_22['summary']['id']

        result = AffectingMonitor._build_passed_note(passed_network_kpi_test_result_1_on_2020_01_22)
        expected = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            '\n'
            f'Device Name: Vi_Pi_DRI test\n'
            '\n'
            'Test Type: Network KPI\n'
            f'Test: 335 - Test Result: {test_result_id}\n'
            '\n'
            'All thresholds are normal.\n'
            '\n'
            'Test Status: PASSED'
        )
        assert result == expected

    def build_failed_note_test(self, failed_network_kpi_test_result_2_on_2020_01_23):
        test_result_id = failed_network_kpi_test_result_2_on_2020_01_23['summary']['id']

        result = AffectingMonitor._build_failed_note(failed_network_kpi_test_result_2_on_2020_01_23)
        expected = (
            '#*Automation Engine*#\n'
            'Service Affecting (Ixia)\n'
            '\n'
            f'Device Name: Vi_Pi_DRI test\n'
            '\n'
            'Test Type: Network KPI\n'
            f'Test: 335 - Test Result: {test_result_id}\n'
            '\n'
            'Trouble: Jitter (ms)\n'
            'Threshold: 6\n'
            'Value: 7\n'
            '\n'
            'Trouble: Latency (ms)\n'
            'Threshold: 7\n'
            'Value: 10\n'
            '\n'
            'Test Status: FAILED'
        )
        assert result == expected

    @pytest.mark.asyncio
    async def process_failed_test_result_with_serial_number_missing_in_tickets_mapping_test(
            self, affecting_monitor, device_cached_info_1, failed_network_kpi_test_result_2_on_2020_01_23):

        tickets_mapping = {}
        affecting_monitor._tickets_by_serial = tickets_mapping

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await affecting_monitor._process_failed_test_result(
                test_result=failed_network_kpi_test_result_2_on_2020_01_23,
                device_cached_info=device_cached_info_1,
            )

        affecting_monitor._bruin_repository.create_affecting_ticket.assert_not_awaited()
        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_failed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial == tickets_mapping

    @pytest.mark.asyncio
    async def process_failed_test_result_with_no_ticket_found_for_serial_and_environment_not_being_production_test(
            self, affecting_monitor, serial_number_1, device_cached_info_1,
            failed_network_kpi_test_result_2_on_2020_01_23):

        tickets_mapping = {
            serial_number_1: {}
        }
        affecting_monitor._tickets_by_serial = tickets_mapping

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await affecting_monitor._process_failed_test_result(
                test_result=failed_network_kpi_test_result_2_on_2020_01_23,
                device_cached_info=device_cached_info_1,
            )

        affecting_monitor._bruin_repository.create_affecting_ticket.assert_not_awaited()
        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_failed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial == tickets_mapping

    @pytest.mark.asyncio
    async def process_failed_test_result_with_no_ticket_found_for_serial_and_unsuccessful_ticket_creation_test(
            self, affecting_monitor, serial_number_1, bruin_client_id, device_cached_info_1,
            failed_network_kpi_test_result_2_on_2020_01_23, bruin_500_response):

        tickets_mapping = {
            serial_number_1: {}
        }
        affecting_monitor._tickets_by_serial = tickets_mapping

        affecting_monitor._bruin_repository.create_affecting_ticket.return_value = bruin_500_response

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await affecting_monitor._process_failed_test_result(
                test_result=failed_network_kpi_test_result_2_on_2020_01_23,
                device_cached_info=device_cached_info_1,
            )

        affecting_monitor._bruin_repository.create_affecting_ticket.assert_awaited_once_with(
            client_id=bruin_client_id, service_number=serial_number_1,
        )
        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_failed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial is tickets_mapping

    @pytest.mark.asyncio
    async def process_failed_test_result_with_no_ticket_found_for_serial_and_successful_ticket_creation_test(
            self, affecting_monitor, serial_number_1, bruin_client_id, device_cached_info_1,
            failed_network_kpi_test_result_2_on_2020_01_23, create_affecting_ticket_200_response):

        ticket_id = create_affecting_ticket_200_response['body']['ticketIds'][0]

        tickets_mapping = {
            serial_number_1: {}
        }
        affecting_monitor._tickets_by_serial = tickets_mapping

        failed_test_note = 'This is a FAILED note'
        affecting_monitor._build_failed_note.return_value = failed_test_note

        affecting_monitor._bruin_repository.create_affecting_ticket.return_value = create_affecting_ticket_200_response

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            with patch.object(affecting_monitoring_module, 'datetime', new=datetime_mock):
                await affecting_monitor._process_failed_test_result(
                    test_result=failed_network_kpi_test_result_2_on_2020_01_23,
                    device_cached_info=device_cached_info_1,
                )

        affecting_monitor._bruin_repository.create_affecting_ticket.assert_awaited_once_with(
            client_id=bruin_client_id, service_number=serial_number_1
        )
        affecting_monitor._notifications_repository.notify_ticket_creation.assert_awaited_once_with(
            ticket_id, serial_number_1
        )
        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_failed_note.assert_called_once_with(failed_network_kpi_test_result_2_on_2020_01_23)
        assert affecting_monitor._tickets_by_serial == {
            serial_number_1: {
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
    async def process_failed_test_result_with_unresolved_ticket_detail_found_and_no_note_found_for_test_type_test(
            self, affecting_monitor, serial_number_1, device_cached_info_1, test_type_network_kpi,
            failed_network_kpi_test_result_2_on_2020_01_23,
            note_text_about_failed_icmp_test):

        ticket_initial_notes = [
            {
                'text': note_text_about_failed_icmp_test,
                'date': parse('2020-12-10T12:01:32Z'),
            }
        ]

        ticket_new_note_1 = {
            'text': note_text_about_failed_icmp_test,
            'date': parse('2020-12-10T13:01:32Z'),
        }
        ticket_new_notes = [
            ticket_new_note_1,
        ]
        all_ticket_notes = ticket_initial_notes + ticket_new_notes

        ticket_id = 12345
        detail_id = 67890
        tickets_mapping = {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }
        affecting_monitor._tickets_by_serial = tickets_mapping

        failed_test_note = 'This is a FAILED note'
        affecting_monitor._build_failed_note.return_value = failed_test_note

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.object(affecting_monitoring_module, 'datetime', new=datetime_mock):
            await affecting_monitor._process_failed_test_result(
                test_result=failed_network_kpi_test_result_2_on_2020_01_23,
                device_cached_info=device_cached_info_1,
            )

        affecting_monitor._bruin_repository.create_affecting_ticket.assert_not_awaited()
        affecting_monitor._get_last_note_by_test_type.assert_called_once_with(all_ticket_notes, test_type_network_kpi)
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._build_failed_note.assert_called_once_with(failed_network_kpi_test_result_2_on_2020_01_23)
        updated_new_notes = [
            ticket_new_note_1,
            {
                'text': failed_test_note,
                'date': current_datetime,
            }
        ]
        assert affecting_monitor._tickets_by_serial == {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': updated_new_notes,
            }
        }

    @pytest.mark.asyncio
    async def process_failed_test_result_with_unresolved_ticket_detail_found_and_passed_note_found_for_test_type_test(
            self, affecting_monitor, serial_number_1, device_cached_info_1, test_type_network_kpi,
            failed_network_kpi_test_result_2_on_2020_01_23,
            note_text_about_passed_network_kpi_test, note_text_about_failed_icmp_test):

        ticket_initial_note_1 = {
            'text': note_text_about_passed_network_kpi_test,
            'date': parse('2020-12-10T12:01:32Z'),
        }
        ticket_initial_notes = [
            ticket_initial_note_1
        ]

        ticket_new_note_1 = {
            'text': note_text_about_failed_icmp_test,
            'date': parse('2020-12-10T13:01:32Z'),
        }
        ticket_new_notes = [
            ticket_new_note_1,
        ]
        all_ticket_notes = ticket_initial_notes + ticket_new_notes

        ticket_id = 12345
        detail_id = 67890
        tickets_mapping = {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }
        affecting_monitor._tickets_by_serial = tickets_mapping

        failed_test_note = 'This is a FAILED note'
        affecting_monitor._build_failed_note.return_value = failed_test_note

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.object(affecting_monitoring_module, 'datetime', new=datetime_mock):
            await affecting_monitor._process_failed_test_result(
                test_result=failed_network_kpi_test_result_2_on_2020_01_23,
                device_cached_info=device_cached_info_1,
            )

        affecting_monitor._bruin_repository.create_affecting_ticket.assert_not_awaited()
        affecting_monitor._get_last_note_by_test_type.assert_called_once_with(all_ticket_notes, test_type_network_kpi)
        affecting_monitor._is_passed_note.assert_called_once_with(note_text_about_passed_network_kpi_test)
        affecting_monitor._build_failed_note.assert_called_once_with(failed_network_kpi_test_result_2_on_2020_01_23)
        updated_new_notes = [
            ticket_new_note_1,
            {
                'text': failed_test_note,
                'date': current_datetime,
            }
        ]
        assert affecting_monitor._tickets_by_serial == {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': updated_new_notes,
            }
        }

    @pytest.mark.asyncio
    async def process_failed_test_result_with_unresolved_ticket_detail_found_and_failed_note_found_for_test_type_test(
            self, affecting_monitor, serial_number_1, device_cached_info_1, test_type_network_kpi,
            failed_network_kpi_test_result_2_on_2020_01_23,
            note_text_about_passed_network_kpi_test, note_text_about_failed_network_kpi_test):

        ticket_initial_note_1 = {
            'text': note_text_about_passed_network_kpi_test,
            'date': parse('2020-12-10T12:01:32Z'),
        }
        ticket_initial_notes = [
            ticket_initial_note_1,
        ]

        ticket_new_notes = [
            {
                'text': note_text_about_failed_network_kpi_test,
                'date': parse('2020-12-10T13:01:32Z'),
            },
        ]
        all_ticket_notes = ticket_initial_notes + ticket_new_notes

        ticket_id = 12345
        detail_id = 67890
        tickets_mapping = {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }
        affecting_monitor._tickets_by_serial = tickets_mapping

        failed_test_note = 'This is a FAILED note'
        affecting_monitor._build_failed_note.return_value = failed_test_note

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.object(affecting_monitoring_module, 'datetime', new=datetime_mock):
            await affecting_monitor._process_failed_test_result(
                test_result=failed_network_kpi_test_result_2_on_2020_01_23,
                device_cached_info=device_cached_info_1,
            )

        affecting_monitor._bruin_repository.create_affecting_ticket.assert_not_awaited()
        affecting_monitor._get_last_note_by_test_type.assert_called_once_with(all_ticket_notes, test_type_network_kpi)
        affecting_monitor._is_passed_note.assert_called_once_with(note_text_about_failed_network_kpi_test)
        affecting_monitor._build_failed_note.assert_not_called()
        assert affecting_monitor._tickets_by_serial is tickets_mapping

    @pytest.mark.asyncio
    async def process_failed_test_result_with_resolved_ticket_detail_found_and_unsuccessful_unresolve_test(
            self, affecting_monitor, serial_number_1, device_cached_info_1,
            failed_network_kpi_test_result_2_on_2020_01_23,
            note_text_about_passed_network_kpi_test, note_text_about_failed_icmp_test,
            bruin_500_response):

        ticket_initial_notes = [
            {
                'text': note_text_about_passed_network_kpi_test,
                'date': parse('2020-12-10T12:01:32Z'),
            },
        ]

        ticket_new_note_1 = {
            'text': note_text_about_failed_icmp_test,
            'date': parse('2020-12-10T13:01:32Z'),
        }
        ticket_new_notes = [
            ticket_new_note_1,
        ]

        ticket_id = 12345
        detail_id = 67890
        tickets_mapping = {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': True,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }
        affecting_monitor._tickets_by_serial = tickets_mapping

        failed_test_note = 'This is a FAILED note'
        affecting_monitor._build_failed_note.return_value = failed_test_note

        affecting_monitor._bruin_repository.unresolve_ticket_detail.return_value = bruin_500_response

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.object(affecting_monitoring_module, 'datetime', new=datetime_mock):
            await affecting_monitor._process_failed_test_result(
                test_result=failed_network_kpi_test_result_2_on_2020_01_23,
                device_cached_info=device_cached_info_1,
            )

        affecting_monitor._bruin_repository.create_affecting_ticket.assert_not_awaited()
        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._bruin_repository.unresolve_ticket_detail.assert_awaited_once_with(ticket_id, detail_id)
        affecting_monitor._build_failed_note.assert_called_once_with(failed_network_kpi_test_result_2_on_2020_01_23)
        updated_new_notes = [
            ticket_new_note_1,
            {
                'text': failed_test_note,
                'date': current_datetime,
            }
        ]
        assert affecting_monitor._tickets_by_serial == {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': True,
                'initial_notes': ticket_initial_notes,
                'new_notes': updated_new_notes,
            }
        }

    @pytest.mark.asyncio
    async def process_failed_test_result_with_resolved_ticket_detail_found_and_successful_unresolve_test(
            self, affecting_monitor, serial_number_1, device_cached_info_1,
            failed_network_kpi_test_result_2_on_2020_01_23,
            note_text_about_passed_network_kpi_test, note_text_about_failed_icmp_test,
            unresolve_ticket_detail_200_response):

        ticket_initial_notes = [
            {
                'text': note_text_about_passed_network_kpi_test,
                'date': parse('2020-12-10T12:01:32Z'),
            },
        ]

        ticket_new_note_1 = {
            'text': note_text_about_failed_icmp_test,
            'date': parse('2020-12-10T13:01:32Z'),
        }
        ticket_new_notes = [
            ticket_new_note_1,
        ]

        ticket_id = 12345
        detail_id = 67890
        tickets_mapping = {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': True,
                'initial_notes': ticket_initial_notes,
                'new_notes': ticket_new_notes,
            }
        }
        affecting_monitor._tickets_by_serial = tickets_mapping

        failed_test_note = 'This is a FAILED note'
        affecting_monitor._build_failed_note.return_value = failed_test_note

        affecting_monitor._bruin_repository.unresolve_ticket_detail.return_value = unresolve_ticket_detail_200_response

        current_datetime = datetime.utcnow()
        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=current_datetime)
        with patch.object(affecting_monitoring_module, 'datetime', new=datetime_mock):
            await affecting_monitor._process_failed_test_result(
                test_result=failed_network_kpi_test_result_2_on_2020_01_23,
                device_cached_info=device_cached_info_1,
            )

        affecting_monitor._bruin_repository.create_affecting_ticket.assert_not_awaited()
        affecting_monitor._get_last_note_by_test_type.assert_not_called()
        affecting_monitor._is_passed_note.assert_not_called()
        affecting_monitor._bruin_repository.unresolve_ticket_detail.assert_awaited_once_with(ticket_id, detail_id)
        affecting_monitor._notifications_repository.notify_ticket_detail_was_unresolved.assert_awaited_once_with(
            ticket_id, serial_number_1
        )
        affecting_monitor._build_failed_note.assert_called_once_with(failed_network_kpi_test_result_2_on_2020_01_23)
        updated_new_notes = [
            ticket_new_note_1,
            {
                'text': failed_test_note,
                'date': current_datetime,
            }
        ]
        assert affecting_monitor._tickets_by_serial == {
            serial_number_1: {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'is_detail_resolved': False,
                'initial_notes': ticket_initial_notes,
                'new_notes': updated_new_notes,
            }
        }
