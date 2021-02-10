from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest

from apscheduler.util import undefined
from asynctest import CoroutineMock
from dateutil.parser import parse
from shortuuid import uuid

from application.actions.tnba_monitor import TNBAMonitor
from application.actions import tnba_monitor as tnba_monitor_module
from application.repositories.utils_repository import UtilsRepository
from config import testconfig


class TestTNBAMonitor:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        customer_cache_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        assert tnba_monitor._event_bus is event_bus
        assert tnba_monitor._logger is logger
        assert tnba_monitor._scheduler is scheduler
        assert tnba_monitor._config is config
        assert tnba_monitor._t7_repository is t7_repository
        assert tnba_monitor._ticket_repository is ticket_repository
        assert tnba_monitor._customer_cache_repository is customer_cache_repository
        assert tnba_monitor._bruin_repository is bruin_repository
        assert tnba_monitor._velocloud_repository is velocloud_repository
        assert tnba_monitor._prediction_repository is prediction_repository
        assert tnba_monitor._notifications_repository is notifications_repository

        assert tnba_monitor._customer_cache_by_serial == {}
        assert tnba_monitor._edge_status_by_serial == {}
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def start_tnba_automated_process_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        customer_cache_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            with patch.object(tnba_monitor_module, 'timezone', new=Mock()):
                await tnba_monitor.start_tnba_automated_process(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            tnba_monitor._run_tickets_polling, 'interval',
            seconds=config.MONITORING_INTERVAL_SECONDS,
            next_run_time=next_run_time,
            replace_existing=False,
            id='_run_tickets_polling',
        )

    @pytest.mark.asyncio
    async def start_tnba_automated_process_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        customer_cache_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        await tnba_monitor.start_tnba_automated_process(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            tnba_monitor._run_tickets_polling, 'interval',
            seconds=config.MONITORING_INTERVAL_SECONDS,
            next_run_time=undefined,
            replace_existing=False,
            id='_run_tickets_polling',
        )

    @pytest.mark.asyncio
    async def run_tickets_polling_with_get_cache_request_having_202_status_test(self):
        get_cache_response = {
            'body': 'Cache is still being built for host(s): mettel_velocloud.net, metvco03.mettel.net',
            'status': 202,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_tnba_monitoring = CoroutineMock(return_value=get_cache_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._process_ticket_details_with_tnba = CoroutineMock()
        tnba_monitor._process_ticket_details_without_tnba = CoroutineMock()

        await tnba_monitor._run_tickets_polling()

        customer_cache_repository.get_cache_for_tnba_monitoring.assert_awaited_once()
        tnba_monitor._process_ticket_details_with_tnba.assert_not_awaited()
        tnba_monitor._process_ticket_details_without_tnba.assert_not_awaited()
        assert tnba_monitor._customer_cache_by_serial == {}

    @pytest.mark.asyncio
    async def run_tickets_polling_with_get_cache_request_having_non_2xx_status_and_different_from_202_test(self):
        get_cache_response = {
            'body': 'No edges were found for the specified filters',
            'status': 404,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_tnba_monitoring = CoroutineMock(return_value=get_cache_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._process_ticket_details_with_tnba = CoroutineMock()
        tnba_monitor._process_ticket_details_without_tnba = CoroutineMock()

        await tnba_monitor._run_tickets_polling()

        customer_cache_repository.get_cache_for_tnba_monitoring.assert_awaited_once()
        tnba_monitor._process_ticket_details_with_tnba.assert_not_awaited()
        tnba_monitor._process_ticket_details_without_tnba.assert_not_awaited()
        assert tnba_monitor._customer_cache_by_serial == {}

    @pytest.mark.asyncio
    async def run_tickets_polling_with_empty_list_of_edges_statuses_test(self):
        bruin_client_1_id = 12345
        bruin_client_2_id = 67890

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}

        cached_info_1 = {
            'edge': edge_1_full_id,
            'serial_number': edge_1_serial,
            'last_contact': '2020-08-27T15:25:42.000',
            'bruin_client_info': {
                'client_id': bruin_client_1_id,
                'client_name': 'Aperture Science',
            }
        }
        cached_info_2 = {
            'edge': edge_2_full_id,
            'serial_number': edge_2_serial,
            'last_contact': '2020-08-27T15:25:42.000',
            'bruin_client_info': {
                'client_id': bruin_client_2_id,
                'client_name': 'Sarif Industries',
            }
        }
        cached_info_3 = {
            'edge': edge_3_full_id,
            'serial_number': edge_3_serial,
            'last_contact': '2020-08-27T15:25:42.000',
            'bruin_client_info': {
                'client_id': bruin_client_2_id,
                'client_name': 'Sarif Industries',
            }
        }
        customer_cache = [
            cached_info_1,
            cached_info_2,
            cached_info_3,
        ]

        get_cache_response = {
            'body': customer_cache,
            'status': 200,
        }

        edges_statuses = []

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        prediction_repository = Mock()
        utils_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_tnba_monitoring = CoroutineMock(return_value=get_cache_response)

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_tnba_monitoring = CoroutineMock(return_value=edges_statuses)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._process_ticket_details_with_tnba = CoroutineMock()
        tnba_monitor._process_ticket_details_without_tnba = CoroutineMock()

        await tnba_monitor._run_tickets_polling()

        customer_cache_repository.get_cache_for_tnba_monitoring.assert_awaited_once()
        velocloud_repository.get_edges_for_tnba_monitoring.assert_awaited_once()
        notifications_repository.send_slack_message.assert_awaited_once()
        tnba_monitor._process_ticket_details_with_tnba.assert_not_awaited()
        tnba_monitor._process_ticket_details_without_tnba.assert_not_awaited()
        assert tnba_monitor._customer_cache_by_serial == {}
        assert tnba_monitor._edge_status_by_serial == {}

    @pytest.mark.asyncio
    async def run_tickets_polling_with_customer_cache_ready_and_edge_statuses_received_and_no_notes_to_append_test(
            self):
        bruin_client_1_id = 12345
        bruin_client_2_id = 67890

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        affecting_topic = 'Service Affecting Trouble'
        outage_topic = 'Service Outage Trouble'

        edges_host = 'some-host'
        edges_enterprise_id = 1

        edge_1_id = 1
        edge_1_full_id = {'host': edges_host, 'enterprise_id': edges_enterprise_id, 'edge_id': edge_1_id}

        edge_2_id = 2
        edge_2_full_id = {'host': edges_host, 'enterprise_id': edges_enterprise_id, 'edge_id': edge_2_id}

        edge_3_id = 3
        edge_3_full_id = {'host': edges_host, 'enterprise_id': edges_enterprise_id, 'edge_id': edge_3_id}

        cached_info_1 = {
            'edge': edge_1_full_id,
            'serial_number': edge_1_serial,
            'last_contact': '2020-08-27T15:25:42.000',
            'bruin_client_info': {
                'client_id': bruin_client_1_id,
                'client_name': 'Aperture Science',
            }
        }
        cached_info_2 = {
            'edge': edge_2_full_id,
            'serial_number': edge_2_serial,
            'last_contact': '2020-08-27T15:25:42.000',
            'bruin_client_info': {
                'client_id': bruin_client_2_id,
                'client_name': 'Sarif Industries',
            }
        }
        cached_info_3 = {
            'edge': edge_3_full_id,
            'serial_number': edge_3_serial,
            'last_contact': '2020-08-27T15:25:42.000',
            'bruin_client_info': {
                'client_id': bruin_client_2_id,
                'client_name': 'Sarif Industries',
            }
        }
        customer_cache = [
            cached_info_1,
            cached_info_2,
            cached_info_3,
        ]

        get_cache_response = {
            'body': customer_cache,
            'status': 200,
        }

        customer_cache_by_serial = {
            edge_1_serial: cached_info_1,
            edge_2_serial: cached_info_2,
            edge_3_serial: cached_info_3,
        }

        edge_1_status = {
            'host': edges_host,
            'enterpriseId': edges_enterprise_id,
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            # Some fields omitted for simplicity
        }
        edge_2_status = {
            'host': edges_host,
            'enterpriseId': edges_enterprise_id,
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            # Some fields omitted for simplicity
        }
        edge_3_status = {
            'host': edges_host,
            'enterpriseId': edges_enterprise_id,
            'edgeId': edge_3_id,
            'edgeSerialNumber': edge_3_serial,
            # Some fields omitted for simplicity
        }
        edges_statuses = [
            edge_1_status,
            edge_2_status,
            edge_3_status,
        ]
        edge_status_by_serial = {
            edge_1_serial: edge_1_status,
            edge_2_serial: edge_2_status,
            edge_3_serial: edge_3_status,
        }

        tickets_creator = 'Intelygenz Ai'

        ticket_1_for_bruin_client_1_id = 12345
        ticket_1_for_bruin_client_1_creation_date = '1/02/2021 10:08:13 AM'
        ticket_1_for_bruin_client_1_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_1_serial,
        }
        ticket_1_for_bruin_client_1_detail_2 = {
            "detailID": 2746938,
            "detailValue": edge_2_serial,
        }
        ticket_1_for_bruin_client_1_details = [
            ticket_1_for_bruin_client_1_detail_1,
        ]
        ticket_1_note_1_for_bruin_client_1 = {
            "noteId": 41894040,
            "noteValue": None,
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                edge_1_serial,
            ]
        }
        ticket_1_note_2_for_bruin_client_1 = {
            "noteId": 41894041,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                edge_1_serial,
            ]
        }
        ticket_1_note_3_for_bruin_client_1 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                edge_1_serial,
            ]
        }
        ticket_1_note_4_for_bruin_client_1 = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                edge_1_serial,
                edge_2_serial,
            ]
        }
        ticket_1_note_5_for_bruin_client_1 = {
            "noteId": 41894044,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                edge_2_serial,
            ]
        }
        ticket_1_with_details_for_bruin_client_1 = {
            'ticket_id': ticket_1_for_bruin_client_1_id,
            'ticket_creation_date': ticket_1_for_bruin_client_1_creation_date,
            'ticket_topic': outage_topic,
            'ticket_creator': tickets_creator,
            'ticket_details': ticket_1_for_bruin_client_1_details,
            'ticket_notes': [
                ticket_1_note_1_for_bruin_client_1,
                ticket_1_note_2_for_bruin_client_1,
                ticket_1_note_3_for_bruin_client_1,
                ticket_1_note_4_for_bruin_client_1,
                ticket_1_note_5_for_bruin_client_1
            ],
        }

        ticket_2_for_bruin_client_1_id = 11223
        ticket_2_for_bruin_client_1_creation_date = '1/03/2021 10:08:13 AM'
        ticket_2_for_bruin_client_1_detail_1 = {
            "detailID": 2746938,
            "detailValue": 'VC999999999',
        }
        ticket_2_for_bruin_client_1_details = [
            ticket_2_for_bruin_client_1_detail_1,
        ]
        ticket_2_note_1_for_bruin_client_1 = {
            "noteId": 41894042,
            "noteValue": 'There were some troubles with this service number',
            "createdDate": "2020-02-24T10:08:13.503-05:00",
            "serviceNumber": [
                'VC999999999',
            ]
        }
        ticket_2_with_details_for_bruin_client_1 = {
            'ticket_id': ticket_2_for_bruin_client_1_id,
            'ticket_creation_date': ticket_2_for_bruin_client_1_creation_date,
            'ticket_topic': affecting_topic,
            'ticket_creator': tickets_creator,
            'ticket_details': ticket_2_for_bruin_client_1_details,
            'ticket_notes': [
                ticket_2_note_1_for_bruin_client_1,
            ],
        }

        ticket_1_for_bruin_client_2_id = 67890
        ticket_1_for_bruin_client_2_creation_date = '1/04/2021 10:08:13 AM'
        ticket_1_for_bruin_client_2_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_3_serial,
        }
        ticket_1_for_bruin_client_2_details = [
            ticket_1_for_bruin_client_2_detail_1,
        ]
        ticket_1_note_1_for_bruin_client_2 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": "2020-02-24T10:08:13.503-05:00",
            "serviceNumber": [
                edge_3_serial,
            ]
        }
        ticket_1_with_details_for_bruin_client_2 = {
            'ticket_id': ticket_1_for_bruin_client_2_id,
            'ticket_creation_date': ticket_1_for_bruin_client_2_creation_date,
            'ticket_topic': outage_topic,
            'ticket_creator': tickets_creator,
            'ticket_details': ticket_1_for_bruin_client_2_details,
            'ticket_notes': [
                ticket_1_note_1_for_bruin_client_2,
            ],
        }

        predictions_for_serial_1_of_ticket_1_of_bruin_client_1 = {
            'assetId': edge_1_serial,
            'predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
            ],
        }
        predictions_for_serial_2_of_ticket_1_of_bruin_client_1 = {
            'assetId': edge_2_serial,
            'predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
            ],
        }
        predictions_for_ticket_1_of_bruin_client_1 = [
            predictions_for_serial_1_of_ticket_1_of_bruin_client_1,
            predictions_for_serial_2_of_ticket_1_of_bruin_client_1,
        ]

        predictions_for_serial_3_of_ticket_1_of_bruin_client_2 = {
            'assetId': edge_3_serial,
            'predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
            ],
        }
        predictions_for_ticket_1_of_bruin_client_2 = [
            predictions_for_serial_3_of_ticket_1_of_bruin_client_2,
        ]

        ticket_1_with_details_for_bruin_client_1_notes_filtered = {
            'ticket_id': ticket_1_for_bruin_client_1_id,
            'ticket_details': ticket_1_for_bruin_client_1_details,
            'ticket_notes': [
                ticket_1_note_2_for_bruin_client_1,
                ticket_1_note_4_for_bruin_client_1,
                ticket_1_note_5_for_bruin_client_1,
            ]
        }
        ticket_1_with_details_for_bruin_client_2_notes_filtered = {
            'ticket_id': ticket_1_for_bruin_client_2_id,
            'ticket_details': ticket_1_for_bruin_client_2_details,
            'ticket_notes': []
        }

        open_tickets_with_details = [
            ticket_1_with_details_for_bruin_client_1,
            ticket_2_with_details_for_bruin_client_1,
            ticket_1_with_details_for_bruin_client_2,
        ]
        relevant_open_tickets = [
            ticket_1_with_details_for_bruin_client_1,
            ticket_1_with_details_for_bruin_client_2,
        ]
        relevant_open_tickets_with_notes_filtered = [
            ticket_1_with_details_for_bruin_client_1_notes_filtered,
            ticket_1_with_details_for_bruin_client_2_notes_filtered,
        ]

        predictions_by_ticket_id = {
            ticket_1_for_bruin_client_1_id: predictions_for_ticket_1_of_bruin_client_1,
            ticket_1_for_bruin_client_2_id: predictions_for_ticket_1_of_bruin_client_2,
        }

        ticket_1_for_client_1_detail_object_1 = {
            'ticket_id': ticket_1_for_bruin_client_1_id,
            'ticket_creation_date': ticket_1_for_bruin_client_1_creation_date,
            'ticket_topic': outage_topic,
            'ticket_creator': tickets_creator,
            'ticket_detail': ticket_1_for_bruin_client_1_detail_1,
            'ticket_notes': [
                ticket_1_note_2_for_bruin_client_1,
                ticket_1_note_4_for_bruin_client_1,
            ],
        }
        ticket_1_for_client_1_detail_object_2 = {
            'ticket_id': ticket_1_for_bruin_client_1_id,
            'ticket_creation_date': ticket_1_for_bruin_client_1_creation_date,
            'ticket_topic': affecting_topic,
            'ticket_creator': tickets_creator,
            'ticket_detail': ticket_1_for_bruin_client_1_detail_2,
            'ticket_notes': [
                ticket_1_note_4_for_bruin_client_1,
                ticket_1_note_5_for_bruin_client_1,
            ],
        }
        ticket_1_for_client_2_detail_object_1 = {
            'ticket_id': ticket_2_for_bruin_client_1_id,
            'ticket_creation_date': ticket_1_for_bruin_client_2_creation_date,
            'ticket_topic': outage_topic,
            'ticket_creator': tickets_creator,
            'ticket_detail': ticket_2_for_bruin_client_1_detail_1,
            'ticket_notes': [],
        }
        ticket_details_with_tnba = [
            ticket_1_for_client_1_detail_object_1,
            ticket_1_for_client_1_detail_object_2,
        ]
        ticket_details_without_tnba = [
            ticket_1_for_client_2_detail_object_1,
        ]

        ticket_details_with_tnba_with_outage_details_filtered = [
            ticket_1_for_client_1_detail_object_2,
        ]
        ticket_details_without_tnba_with_outage_details_filtered = [
            ticket_1_for_client_2_detail_object_1,
        ]

        ticket_1_for_client_1_detail_object_2_with_predictions = {
            'ticket_id': ticket_1_for_bruin_client_1_id,
            'ticket_creation_date': ticket_1_for_bruin_client_1_creation_date,
            'ticket_topic': affecting_topic,
            'ticket_creator': tickets_creator,
            'ticket_detail': ticket_1_for_bruin_client_1_detail_2,
            'ticket_notes': [
                ticket_1_note_4_for_bruin_client_1,
                ticket_1_note_5_for_bruin_client_1,
            ],
            'ticket_detail_predictions': [
                predictions_for_serial_2_of_ticket_1_of_bruin_client_1,
            ]
        }
        ticket_1_for_client_2_detail_object_1_with_predictions = {
            'ticket_id': ticket_2_for_bruin_client_1_id,
            'ticket_creation_date': ticket_1_for_bruin_client_2_creation_date,
            'ticket_topic': outage_topic,
            'ticket_creator': tickets_creator,
            'ticket_detail': ticket_2_for_bruin_client_1_detail_1,
            'ticket_notes': [],
            'ticket_detail_predictions': [
                predictions_for_serial_3_of_ticket_1_of_bruin_client_2,
            ]
        }
        ticket_details_with_tnba_with_predictions = [
            ticket_1_for_client_1_detail_object_2_with_predictions,
        ]
        ticket_details_without_tnba_with_predictions = [
            ticket_1_for_client_2_detail_object_1_with_predictions,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_tnba_monitoring = CoroutineMock(return_value=get_cache_response)

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_tnba_monitoring = CoroutineMock(return_value=edges_statuses)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._tnba_notes_to_append = []
        tnba_monitor._filter_edges_in_customer_cache_and_edges_statuses = Mock(
            return_value=(customer_cache, edges_statuses)
        )
        tnba_monitor._get_all_open_tickets_with_details_for_monitored_companies = CoroutineMock(
            return_value=open_tickets_with_details)
        tnba_monitor._filter_tickets_and_details_related_to_edges_under_monitoring = Mock(
            return_value=relevant_open_tickets)
        tnba_monitor._filter_irrelevant_notes_in_tickets = Mock(return_value=relevant_open_tickets_with_notes_filtered)
        tnba_monitor._get_predictions_by_ticket_id = CoroutineMock(return_value=predictions_by_ticket_id)
        tnba_monitor._remove_erroneous_predictions = Mock(return_value=predictions_by_ticket_id)
        tnba_monitor._distinguish_ticket_details_with_and_without_tnba = Mock(
            return_value=(ticket_details_with_tnba, ticket_details_without_tnba)
        )
        tnba_monitor._filter_outage_ticket_details_based_on_last_outage = Mock(side_effect=[
            ticket_details_with_tnba_with_outage_details_filtered,
            ticket_details_without_tnba_with_outage_details_filtered,
        ])
        tnba_monitor._map_ticket_details_with_predictions = Mock(side_effect=[
            ticket_details_with_tnba_with_predictions,
            ticket_details_without_tnba_with_predictions,
        ])
        tnba_monitor._process_ticket_details_with_tnba = CoroutineMock()
        tnba_monitor._process_ticket_details_without_tnba = CoroutineMock()
        tnba_monitor._append_tnba_notes = CoroutineMock()

        await tnba_monitor._run_tickets_polling()

        customer_cache_repository.get_cache_for_tnba_monitoring.assert_awaited_once()
        tnba_monitor._filter_outage_ticket_details_based_on_last_outage.assert_has_calls([
            call(ticket_details_with_tnba),
            call(ticket_details_without_tnba),
        ])
        tnba_monitor._map_ticket_details_with_predictions.assert_has_calls([
            call(ticket_details_with_tnba_with_outage_details_filtered, predictions_by_ticket_id),
            call(ticket_details_without_tnba_with_outage_details_filtered, predictions_by_ticket_id),
        ])
        tnba_monitor._process_ticket_details_with_tnba.assert_awaited_once_with(
            ticket_details_with_tnba_with_predictions
        )
        tnba_monitor._process_ticket_details_without_tnba.assert_awaited_once_with(
            ticket_details_without_tnba_with_predictions
        )
        tnba_monitor._append_tnba_notes.assert_not_awaited()
        assert tnba_monitor._customer_cache_by_serial == customer_cache_by_serial
        assert tnba_monitor._edge_status_by_serial == edge_status_by_serial

    def filter_edges_in_customer_cache_and_edges_statuses_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'
        edge_4_serial = 'VC2222222'

        edges_host = 'some-host'
        edges_enterprise_id = 1

        edge_1_id = 1
        edge_1_full_id = {'host': edges_host, 'enterprise_id': edges_enterprise_id, 'edge_id': edge_1_id}

        edge_2_id = 2
        edge_2_full_id = {'host': edges_host, 'enterprise_id': edges_enterprise_id, 'edge_id': edge_2_id}

        edge_3_id = 3
        edge_3_full_id = {'host': edges_host, 'enterprise_id': edges_enterprise_id, 'edge_id': edge_3_id}

        edge_4_id = 4

        cached_info_1 = {
            'edge': edge_1_full_id,
            'serial_number': edge_1_serial,
            'last_contact': '2020-08-27T15:25:42.000',
            'bruin_client_info': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            }
        }
        cached_info_2 = {
            'edge': edge_2_full_id,
            'serial_number': edge_2_serial,
            'last_contact': '2020-08-27T15:25:42.000',
            'bruin_client_info': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            }
        }
        cached_info_3 = {
            'edge': edge_3_full_id,
            'serial_number': edge_3_serial,
            'last_contact': '2020-08-27T15:25:42.000',
            'bruin_client_info': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            }
        }
        customer_cache = [
            cached_info_1,
            cached_info_2,
            cached_info_3,
        ]

        edge_2_status = {
            'host': edges_host,
            'enterpriseId': edges_enterprise_id,
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            # Some fields omitted for simplicity
        }
        edge_3_status = {
            'host': edges_host,
            'enterpriseId': edges_enterprise_id,
            'edgeId': edge_3_id,
            'edgeSerialNumber': edge_3_serial,
            # Some fields omitted for simplicity
        }
        edge_4_status = {
            'host': edges_host,
            'enterpriseId': edges_enterprise_id,
            'edgeId': edge_4_id,
            'edgeSerialNumber': edge_4_serial,
            # Some fields omitted for simplicity
        }
        edges_statuses = [
            edge_2_status,
            edge_3_status,
            edge_4_status,
        ]

        filtered_customer_cache, filtered_edges_statuses = \
            TNBAMonitor._filter_edges_in_customer_cache_and_edges_statuses(customer_cache, edges_statuses)

        assert filtered_customer_cache == [
            cached_info_2,
            cached_info_3,
        ]
        assert filtered_edges_statuses == [
            edge_2_status,
            edge_3_status,
        ]

    @pytest.mark.asyncio
    async def start_tnba_automated_process_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        customer_cache_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        await tnba_monitor.start_tnba_automated_process(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            tnba_monitor._run_tickets_polling, 'interval',
            seconds=config.MONITORING_INTERVAL_SECONDS,
            next_run_time=undefined,
            replace_existing=False,
            id='_run_tickets_polling',
        )

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_for_monitored_companies_test(self):
        ticket_with_details_1_for_bruin_client_1 = {
            'ticket_id': 12345,
            'ticket_details': [
                {
                    "detailID": 2746937,
                    "detailValue": 'VC1234567890',
                },
            ],
            'ticket_notes': [
                {
                    "noteId": 41894041,
                    "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                }
            ],
        }
        ticket_with_details_2_for_bruin_client_1 = {
            'ticket_id': 11223,
            'ticket_details': [
                {
                    "detailID": 2746938,
                    "detailValue": 'VC1234567890',
                },
            ],
            'ticket_notes': [
                {
                    "noteId": 41894042,
                    "noteValue": 'There were some troubles with this service number',
                    "createdDate": "2020-02-24T10:08:13.503-05:00",
                }
            ],
        }
        ticket_with_details_1_for_bruin_client_2 = {
            'ticket_id': 67890,
            'ticket_details': [
                {
                    "detailID": 2746937,
                    "detailValue": 'VC0987654321',
                },
            ],
            'ticket_notes': [
                {
                    "noteId": 41894042,
                    "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                }
            ],
        }

        tickets_with_details_for_bruin_client_1 = [
            ticket_with_details_1_for_bruin_client_1,
            ticket_with_details_2_for_bruin_client_1,
        ]
        tickets_with_details_for_bruin_client_2 = [
            ticket_with_details_1_for_bruin_client_2,
        ]

        bruin_client_1_id = 12345
        bruin_client_2_id = 67890

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}

        customer_cache_by_serial = {
            edge_1_serial: {
                'edge': edge_1_full_id,
                'serial_number': edge_1_serial,
                'last_contact': '2020-08-27T15:25:42.000',
                'bruin_client_info': {
                    'client_id': bruin_client_1_id,
                    'client_name': 'Aperture Science',
                }
            },
            edge_2_serial: {
                'edge': edge_2_full_id,
                'serial_number': edge_2_serial,
                'last_contact': '2020-08-27T15:25:42.000',
                'bruin_client_info': {
                    'client_id': bruin_client_2_id,
                    'client_name': 'Sarif Industries',
                }
            },
            edge_3_serial: {
                'edge': edge_3_full_id,
                'serial_number': edge_3_serial,
                'last_contact': '2020-08-27T15:25:42.000',
                'bruin_client_info': {
                    'client_id': bruin_client_2_id,
                    'client_name': 'Sarif Industries',
                }
            },
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._customer_cache_by_serial = customer_cache_by_serial
        tnba_monitor._get_open_tickets_with_details_by_client_id = CoroutineMock(side_effect=[
            tickets_with_details_for_bruin_client_1,
            tickets_with_details_for_bruin_client_2,
        ])

        await tnba_monitor._get_all_open_tickets_with_details_for_monitored_companies()

        tnba_monitor._get_open_tickets_with_details_by_client_id.assert_has_awaits([
            call(bruin_client_1_id, []), call(bruin_client_2_id, [])
        ], any_order=True)

    @pytest.mark.asyncio
    async def get_all_open_tickets_with_details_for_monitored_companies_with_some_requests_failing_test(self):
        tickets_with_details_for_bruin_client_1 = [
            {
                'ticket_id': 12345,
                'ticket_details': [
                    {
                        "detailID": 2746937,
                        "detailValue": 'VC1234567890',
                    },
                ],
                'ticket_notes': [
                    {
                        "noteId": 41894041,
                        "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                        "createdDate": "2020-02-24T10:07:13.503-05:00",
                    }
                ],
            }
        ]
        tickets_with_details_for_bruin_client_3 = [
            {
                'ticket_id': 67890,
                'ticket_details': [
                    {
                        "detailID": 2746937,
                        "detailValue": 'VC0987654321',
                    },
                ],
                'ticket_notes': [
                    {
                        "noteId": 41894042,
                        "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                        "createdDate": "2020-02-24T10:07:13.503-05:00",
                    }
                ],
            }
        ]

        bruin_client_1_id = 12345
        bruin_client_2_id = 67890
        bruin_client_3_id = 11223

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}

        customer_cache_by_serial = {
            edge_1_serial: {
                'edge': edge_1_full_id,
                'serial_number': edge_1_serial,
                'last_contact': '2020-08-27T15:25:42.000',
                'bruin_client_info': {
                    'client_id': bruin_client_1_id,
                    'client_name': 'Aperture Science',
                }
            },
            edge_2_serial: {
                'edge': edge_2_full_id,
                'serial_number': edge_2_serial,
                'last_contact': '2020-08-27T15:25:42.000',
                'bruin_client_info': {
                    'client_id': bruin_client_2_id,
                    'client_name': 'Sarif Industries',
                }
            },
            edge_3_serial: {
                'edge': edge_3_full_id,
                'serial_number': edge_3_serial,
                'last_contact': '2020-08-27T15:25:42.000',
                'bruin_client_info': {
                    'client_id': bruin_client_3_id,
                    'client_name': 'Rupture Farms',
                }
            },
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._customer_cache_by_serial = customer_cache_by_serial
        tnba_monitor._get_open_tickets_with_details_by_client_id = CoroutineMock(side_effect=[
            tickets_with_details_for_bruin_client_1,
            Exception,
            tickets_with_details_for_bruin_client_3,
        ])

        await tnba_monitor._get_all_open_tickets_with_details_for_monitored_companies()

        tnba_monitor._get_open_tickets_with_details_by_client_id.assert_has_awaits([
            call(bruin_client_1_id, []), call(bruin_client_2_id, []), call(bruin_client_3_id, [])
        ], any_order=True)

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_test(self):
        uuid_ = uuid()
        bruin_client_id = 12345

        affecting_topic = 'Service Affecting Trouble'
        outage_topic = 'Service Outage Trouble'

        tickets_creator = 'Intelygenz Ai'

        ticket_1_id = 11111
        ticket_1_creation_date = "1/02/2021 10:08:13 AM"

        ticket_2_id = 22222
        ticket_2_creation_date = "1/03/2021 10:08:13 AM"

        ticket_3_id = 33333
        ticket_3_creation_date = "1/04/2021 10:08:13 AM"

        outage_tickets = [
            {
                'ticketID': ticket_1_id,
                'createDate': ticket_1_creation_date,
                'topic': outage_topic,
                'createdBy': tickets_creator,
            },
            {
                'ticketID': ticket_2_id,
                'createDate': ticket_2_creation_date,
                'topic': outage_topic,
                'createdBy': tickets_creator,
            },
        ]
        affecting_tickets = [
            {
                'ticketID': ticket_3_id,
                'createDate': ticket_3_creation_date,
                'topic': affecting_topic,
                'createdBy': tickets_creator,
            },
        ]

        outage_ticket_1_details_item_1 = {
            "detailID": 2746937,
            "detailValue": 'VC1234567890',
        }
        outage_ticket_1_details_items = [outage_ticket_1_details_item_1]
        outage_ticket_1_notes = [
            {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            }
        ]
        outage_ticket_1_details = {
            'ticketDetails': outage_ticket_1_details_items,
            'ticketNotes': outage_ticket_1_notes,
        }

        outage_ticket_2_details_item_1 = {
            "detailID": 2746938,
            "detailValue": 'VC1234567890',
        }
        outage_ticket_2_details_items = [outage_ticket_2_details_item_1]
        outage_ticket_2_notes = [
            {
                "noteId": 41894043,
                "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894044,
                "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            }
        ]
        outage_ticket_2_details = {
            'ticketDetails': outage_ticket_2_details_items,
            'ticketNotes': outage_ticket_2_notes,
        }

        affecting_ticket_1_details_item_1 = {
            "detailID": 2746937,
            "detailValue": 'VC1234567890',
        }
        affecting_ticket_1_details_items = [affecting_ticket_1_details_item_1]
        affecting_ticket_1_notes = [
            {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            }
        ]
        affecting_ticket_1_details = {
            'ticketDetails': affecting_ticket_1_details_items,
            'ticketNotes': affecting_ticket_1_notes,
        }

        get_open_outage_tickets_response = {
            'request_id': uuid_,
            'body': outage_tickets,
            'status': 200,
        }
        get_open_affecting_tickets_response = {
            'request_id': uuid_,
            'body': affecting_tickets,
            'status': 200,
        }

        get_ticket_1_details_response = {
            'request_id': uuid_,
            'body': outage_ticket_1_details,
            'status': 200,
        }

        get_ticket_2_details_response = {
            'request_id': uuid_,
            'body': outage_ticket_2_details,
            'status': 200,
        }

        get_ticket_3_details_response = {
            'request_id': uuid_,
            'body': affecting_ticket_1_details,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        velocloud_repository = Mock()
        ticket_repository = Mock()
        customer_cache_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
            get_ticket_3_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id)
        ])

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_creation_date': ticket_1_creation_date,
                'ticket_topic': outage_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': outage_ticket_1_details_items,
                'ticket_notes': outage_ticket_1_notes,
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_creation_date': ticket_2_creation_date,
                'ticket_topic': outage_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': outage_ticket_2_details_items,
                'ticket_notes': outage_ticket_2_notes,
            },
            {
                'ticket_id': ticket_3_id,
                'ticket_creation_date': ticket_3_creation_date,
                'ticket_topic': affecting_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': affecting_ticket_1_details_items,
                'ticket_notes': affecting_ticket_1_notes,
            },
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_with_open_outage_tickets_request_not_having_2xx_status_test(
            self):
        bruin_client_id = 12345

        uuid_ = uuid()

        affecting_topic = 'Service Affecting Trouble'

        tickets_creator = 'Intelygenz Ai'

        ticket_1_id = 11111
        ticket_1_creation_date = "1/02/2021 10:08:13 AM"

        ticket_2_id = 22222
        ticket_2_creation_date = "1/03/2021 10:08:13 AM"

        get_open_outage_tickets_response = {
            'request_id': uuid_,
            'body': 'Got internal error from Bruin',
            'status': 500,
        }
        get_open_affecting_tickets_response = {
            'request_id': uuid_,
            'body': [
                {
                    'ticketID': ticket_1_id,
                    'createDate': ticket_1_creation_date,
                    'topic': affecting_topic,
                    'createdBy': tickets_creator,
                },
                {
                    'ticketID': ticket_2_id,
                    'createDate': ticket_2_creation_date,
                    'topic': affecting_topic,
                    'createdBy': tickets_creator,
                },
            ],
            'status': 200,
        }

        affecting_ticket_1_details_item_1 = {
            "detailID": 2746937,
            "detailValue": 'VC1234567890',
        }
        affecting_ticket_1_details_items = [affecting_ticket_1_details_item_1]
        affecting_ticket_1_notes = [
            {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            }
        ]
        affecting_ticket_1_details = {
            'ticketDetails': affecting_ticket_1_details_items,
            'ticketNotes': affecting_ticket_1_notes,
        }

        affecting_ticket_2_details_item_1 = {
            "detailID": 2746938,
            "detailValue": 'VC1234567890',
        }
        affecting_ticket_2_details_items = [affecting_ticket_2_details_item_1]
        affecting_ticket_2_notes = [
            {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-31 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-31 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            }
        ]
        affecting_ticket_2_details = {
            'ticketDetails': affecting_ticket_2_details_items,
            'ticketNotes': affecting_ticket_2_notes,
        }

        get_ticket_1_details_response = {
            'request_id': uuid_,
            'body': affecting_ticket_1_details,
            'status': 200,
        }
        get_ticket_2_details_response = {
            'request_id': uuid_,
            'body': affecting_ticket_2_details,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        velocloud_repository = Mock()
        ticket_repository = Mock()
        customer_cache_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id),
        ])

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_creation_date': ticket_1_creation_date,
                'ticket_topic': affecting_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': affecting_ticket_1_details_items,
                'ticket_notes': affecting_ticket_1_notes,
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_creation_date': ticket_2_creation_date,
                'ticket_topic': affecting_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': affecting_ticket_2_details_items,
                'ticket_notes': affecting_ticket_2_notes,
            },
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_with_open_affecting_tickets_request_not_having_2xx_status_test(
            self):
        bruin_client_id = 12345

        uuid_ = uuid()

        outage_topic = 'Service Outage Trouble'

        tickets_creator = 'Intelygenz Ai'

        ticket_1_id = 11111
        ticket_1_creation_date = "1/02/2021 10:08:13 AM"

        ticket_2_id = 22222
        ticket_2_creation_date = "1/03/2021 10:08:13 AM"

        get_open_outage_tickets_response = {
            'request_id': uuid_,
            'body': [
                {
                    'ticketID': ticket_1_id,
                    'createDate': ticket_1_creation_date,
                    'topic': outage_topic,
                    'createdBy': tickets_creator,
                },
                {
                    'ticketID': ticket_2_id,
                    'createDate': ticket_2_creation_date,
                    'topic': outage_topic,
                    'createdBy': tickets_creator,
                },
            ],
            'status': 200,
        }
        get_open_affecting_tickets_response = {
            'request_id': uuid_,
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        outage_ticket_1_details_item_1 = {
            "detailID": 2746937,
            "detailValue": 'VC1234567890',
        }
        outage_ticket_1_details_items = [outage_ticket_1_details_item_1]
        outage_ticket_1_notes = [
            {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            }
        ]
        outage_ticket_1_details = {
            'ticketDetails': outage_ticket_1_details_items,
            'ticketNotes': outage_ticket_1_notes,
        }

        outage_ticket_2_details_item_1 = {
            "detailID": 2746938,
            "detailValue": 'VC1234567890',
        }
        outage_ticket_2_details_items = [outage_ticket_2_details_item_1]
        outage_ticket_2_notes = [
            {
                "noteId": 41894043,
                "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894044,
                "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            }
        ]
        outage_ticket_2_details = {
            'ticketDetails': outage_ticket_2_details_items,
            'ticketNotes': outage_ticket_2_notes,
        }

        get_ticket_1_details_response = {
            'request_id': uuid_,
            'body': outage_ticket_1_details,
            'status': 200,
        }
        get_ticket_2_details_response = {
            'request_id': uuid_,
            'body': outage_ticket_2_details,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        velocloud_repository = Mock()
        ticket_repository = Mock()
        customer_cache_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id),
        ])

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_creation_date': ticket_1_creation_date,
                'ticket_topic': outage_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': outage_ticket_1_details_items,
                'ticket_notes': outage_ticket_1_notes,
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_creation_date': ticket_2_creation_date,
                'ticket_topic': outage_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': outage_ticket_2_details_items,
                'ticket_notes': outage_ticket_2_notes,
            },
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_with_ticket_details_request_not_having_2xx_status_test(self):
        uuid_ = uuid()
        bruin_client_id = 12345

        affecting_topic = 'Service Affecting Trouble'
        outage_topic = 'Service Outage Trouble'

        tickets_creator = 'Intelygenz Ai'

        ticket_1_id = 11111
        ticket_1_creation_date = "1/02/2021 10:08:13 AM"

        ticket_2_id = 22222
        ticket_2_creation_date = "1/03/2021 10:08:13 AM"

        ticket_3_id = 33333
        ticket_3_creation_date = "1/04/2021 10:08:13 AM"

        outage_tickets = [
            {
                'ticketID': ticket_1_id,
                'createDate': ticket_1_creation_date,
                'topic': outage_topic,
                'createdBy': tickets_creator,
            },
            {
                'ticketID': ticket_2_id,
                'createDate': ticket_2_creation_date,
                'topic': outage_topic,
                'createdBy': tickets_creator,
            },
        ]
        affecting_tickets = [
            {
                'ticketID': ticket_3_id,
                'createDate': ticket_3_creation_date,
                'topic': affecting_topic,
                'createdBy': tickets_creator,
            },
        ]

        outage_ticket_1_details_item_1 = {
            "detailID": 2746937,
            "detailValue": 'VC1234567890',
        }
        outage_ticket_1_details_items = [outage_ticket_1_details_item_1]
        outage_ticket_1_notes = [
            {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            }
        ]
        outage_ticket_1_details = {
            'ticketDetails': outage_ticket_1_details_items,
            'ticketNotes': outage_ticket_1_notes,
        }

        affecting_ticket_1_details_item_1 = {
            "detailID": 2746937,
            "detailValue": 'VC1234567890',
        }
        affecting_ticket_1_details_items = [affecting_ticket_1_details_item_1]
        affecting_ticket_1_notes = [
            {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            }
        ]
        affecting_ticket_1_details = {
            'ticketDetails': affecting_ticket_1_details_items,
            'ticketNotes': affecting_ticket_1_notes,
        }

        get_open_outage_tickets_response = {
            'request_id': uuid_,
            'body': outage_tickets,
            'status': 200,
        }
        get_open_affecting_tickets_response = {
            'request_id': uuid_,
            'body': affecting_tickets,
            'status': 200,
        }

        get_ticket_1_details_response = {
            'request_id': uuid_,
            'body': outage_ticket_1_details,
            'status': 200,
        }

        get_ticket_2_details_response = {
            'request_id': uuid_,
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        get_ticket_3_details_response = {
            'request_id': uuid_,
            'body': affecting_ticket_1_details,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        velocloud_repository = Mock()
        ticket_repository = Mock()
        customer_cache_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
            get_ticket_3_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id)
        ])

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_creation_date': ticket_1_creation_date,
                'ticket_topic': outage_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': outage_ticket_1_details_items,
                'ticket_notes': outage_ticket_1_notes,
            },
            {
                'ticket_id': ticket_3_id,
                'ticket_creation_date': ticket_3_creation_date,
                'ticket_topic': affecting_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': affecting_ticket_1_details_items,
                'ticket_notes': affecting_ticket_1_notes,
            }
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_with_ticket_details_not_having_details_actually_test(self):
        uuid_ = uuid()
        bruin_client_id = 12345

        affecting_topic = 'Service Affecting Trouble'
        outage_topic = 'Service Outage Trouble'

        tickets_creator = 'Intelygenz Ai'

        ticket_1_id = 11111
        ticket_1_creation_date = "1/02/2021 10:08:13 AM"

        ticket_2_id = 22222
        ticket_2_creation_date = "1/03/2021 10:08:13 AM"

        ticket_3_id = 33333
        ticket_3_creation_date = "1/04/2021 10:08:13 AM"

        outage_tickets = [
            {
                'ticketID': ticket_1_id,
                'createDate': ticket_1_creation_date,
                'topic': outage_topic,
                'createdBy': tickets_creator,
            },
            {
                'ticketID': ticket_2_id,
                'createDate': ticket_2_creation_date,
                'topic': outage_topic,
                'createdBy': tickets_creator,
            },
        ]
        affecting_tickets = [
            {
                'ticketID': ticket_3_id,
                'createDate': ticket_3_creation_date,
                'topic': affecting_topic,
                'createdBy': tickets_creator,
            },
        ]

        outage_ticket_1_details_item_1 = {
            "detailID": 2746937,
            "detailValue": 'VC1234567890',
        }
        outage_ticket_1_details_items = [outage_ticket_1_details_item_1]
        outage_ticket_1_notes = [
            {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            }
        ]
        outage_ticket_1_details = {
            'ticketDetails': outage_ticket_1_details_items,
            'ticketNotes': outage_ticket_1_notes,
        }

        outage_ticket_2_details_items = []
        outage_ticket_2_notes = []
        outage_ticket_2_details = {
            'ticketDetails': outage_ticket_2_details_items,
            'ticketNotes': outage_ticket_2_notes,
        }

        affecting_ticket_1_details_item_1 = {
            "detailID": 2746937,
            "detailValue": 'VC1234567890',
        }
        affecting_ticket_1_details_items = [affecting_ticket_1_details_item_1]
        affecting_ticket_1_notes = [
            {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            }
        ]
        affecting_ticket_1_details = {
            'ticketDetails': affecting_ticket_1_details_items,
            'ticketNotes': affecting_ticket_1_notes,
        }

        get_open_outage_tickets_response = {
            'request_id': uuid_,
            'body': outage_tickets,
            'status': 200,
        }
        get_open_affecting_tickets_response = {
            'request_id': uuid_,
            'body': affecting_tickets,
            'status': 200,
        }

        get_ticket_1_details_response = {
            'request_id': uuid_,
            'body': outage_ticket_1_details,
            'status': 200,
        }

        get_ticket_2_details_response = {
            'request_id': uuid_,
            'body': outage_ticket_2_details,
            'status': 200,
        }

        get_ticket_3_details_response = {
            'request_id': uuid_,
            'body': affecting_ticket_1_details,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        velocloud_repository = Mock()
        ticket_repository = Mock()
        customer_cache_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
            get_ticket_3_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id)
        ])

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_creation_date': ticket_1_creation_date,
                'ticket_topic': outage_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': outage_ticket_1_details_items,
                'ticket_notes': outage_ticket_1_notes,
            },
            {
                'ticket_id': ticket_3_id,
                'ticket_creation_date': ticket_3_creation_date,
                'ticket_topic': affecting_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': affecting_ticket_1_details_items,
                'ticket_notes': affecting_ticket_1_notes,
            }
        ]
        assert result == expected

    def filter_tickets_related_to_edges_under_monitoring_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1112223'
        edge_4_serial = 'VC3344455'
        edge_5_serial = 'VC5666777'

        bruin_client_1_id = 12345
        bruin_client_2_id = 67890

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}
        edge_4_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 4}
        edge_5_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 5}

        customer_cache_by_serial = {
            edge_1_serial: {
                'edge': edge_1_full_id,
                'serial_number': edge_1_serial,
                'last_contact': '2020-08-27T15:25:42.000',
                'bruin_client_info': {
                    'client_id': bruin_client_1_id,
                    'client_name': 'Aperture Science',
                }
            },
            edge_2_serial: {
                'edge': edge_2_full_id,
                'serial_number': edge_2_serial,
                'last_contact': '2020-08-27T15:25:42.000',
                'bruin_client_info': {
                    'client_id': bruin_client_1_id,
                    'client_name': 'Aperture Science',
                }
            },
            edge_3_serial: {
                'edge': edge_3_full_id,
                'serial_number': edge_3_serial,
                'last_contact': '2020-08-27T15:25:42.000',
                'bruin_client_info': {
                    'client_id': bruin_client_1_id,
                    'client_name': 'Aperture Science',
                }
            },
            edge_4_serial: {
                'edge': edge_4_full_id,
                'serial_number': edge_4_serial,
                'last_contact': '2020-08-27T15:25:42.000',
                'bruin_client_info': {
                    'client_id': bruin_client_2_id,
                    'client_name': 'Sarif Industries',
                }
            },
            edge_5_serial: {
                'edge': edge_5_full_id,
                'serial_number': edge_5_serial,
                'last_contact': '2020-08-27T15:25:42.000',
                'bruin_client_info': {
                    'client_id': bruin_client_2_id,
                    'client_name': 'Sarif Industries',
                }
            },
        }

        ticket_topic = 'Service Outage Trouble'
        tickets_creator = 'Intelygenz Ai'

        ticket_1_id = 12345
        ticket_1_creation_date = "1/02/2021 10:08:13 AM"
        ticket_1_detail_1 = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
        }
        ticket_1_detail_2 = {
            "detailID": 2746931,
            "detailValue": 'VC9999999',
        }
        ticket_1_notes = [
            {
                "noteId": 41894040,
                "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        ]
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_creation_date': ticket_1_creation_date,
            'ticket_topic': ticket_topic,
            'ticket_creator': tickets_creator,
            'ticket_details': [
                ticket_1_detail_1,
                ticket_1_detail_2,
            ],
            'ticket_notes': ticket_1_notes,
        }

        ticket_2_id = 67890
        ticket_2_creation_date = "1/03/2021 10:08:13 AM"
        ticket_2_detail_1 = {
            "detailID": 2746932,
            "detailValue": edge_3_serial,
        }
        ticket_2_detail_2 = {
            "detailID": 2746933,
            "detailValue": 'VC1111111',
        }
        ticket_2_detail_3 = {
            "detailID": 2746934,
            "detailValue": edge_4_serial,
        }
        ticket_2_notes = [
            {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        ]
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_creation_date': ticket_2_creation_date,
            'ticket_topic': ticket_topic,
            'ticket_creator': tickets_creator,
            'ticket_details': [
                ticket_2_detail_1,
                ticket_2_detail_2,
                ticket_2_detail_3,
            ],
            'ticket_notes': ticket_2_notes,
        }

        ticket_3_id = 22222
        ticket_3_creation_date = "1/04/2021 10:08:13 AM"
        ticket_3_detail_1 = {
            "detailID": 2746932,
            "detailValue": 'VC9992221',
        }
        ticket_3_notes = [
            {
                "noteId": 41894042,
                "noteValue": f"This note was posted by a member of Bruin's support team",
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        ]
        ticket_3 = {
            'ticket_id': ticket_3_id,
            'ticket_creation_date': ticket_3_creation_date,
            'ticket_topic': ticket_topic,
            'ticket_creator': tickets_creator,
            'ticket_details': [
                ticket_3_detail_1,
            ],
            'ticket_notes': ticket_3_notes,
        }

        ticket_4_id = 11111
        ticket_4_creation_date = "1/05/2021 10:08:13 AM"
        ticket_4_detail_1 = {
            "detailID": 2746935,
            "detailValue": edge_5_serial,
        }
        ticket_4_notes = [
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        ]
        ticket_4 = {
            'ticket_id': ticket_4_id,
            'ticket_creation_date': ticket_4_creation_date,
            'ticket_topic': ticket_topic,
            'ticket_creator': tickets_creator,
            'ticket_details': [
                ticket_4_detail_1,
            ],
            'ticket_notes': ticket_4_notes,
        }

        tickets = [
            ticket_1,
            ticket_2,
            ticket_3,
            ticket_4,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        velocloud_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        customer_cache_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._customer_cache_by_serial = customer_cache_by_serial

        result = tnba_monitor._filter_tickets_and_details_related_to_edges_under_monitoring(tickets)

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_creation_date': ticket_1_creation_date,
                'ticket_topic': ticket_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': [
                    ticket_1_detail_1,
                ],
                'ticket_notes': ticket_1_notes,
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_creation_date': ticket_2_creation_date,
                'ticket_topic': ticket_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': [
                    ticket_2_detail_1,
                    ticket_2_detail_3,
                ],
                'ticket_notes': ticket_2_notes,
            },
            {
                'ticket_id': ticket_4_id,
                'ticket_creation_date': ticket_4_creation_date,
                'ticket_topic': ticket_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': [
                    ticket_4_detail_1,
                ],
                'ticket_notes': ticket_4_notes,
            },
        ]
        assert result == expected

    def filter_irrelevant_notes_in_tickets_test(self):
        service_number_1 = 'VC1234567'
        service_number_2 = 'VC8901234'
        service_number_3 = '20.RBDB.872345'
        service_number_4 = 'VC1112223'
        service_number_5 = '18.RBDB.105641'
        service_number_6 = 'VC3344455'

        customer_cache_by_serial = {
            service_number_1: {
                'edge': {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1},
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': service_number_1,
                'bruin_client_info': {
                    'client_id': 9994,
                    'client_name': 'EVIL-CORP'
                },
            },
            service_number_2: {
                'edge': {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2},
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': service_number_2,
                'bruin_client_info': {
                    'client_id': 9994,
                    'client_name': 'EVIL-CORP'
                },
            },
            service_number_4: {
                'edge': {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3},
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': service_number_4,
                'bruin_client_info': {
                    'client_id': 9994,
                    'client_name': 'EVIL-CORP'
                },
            },
            service_number_6: {
                'edge': {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 4},
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': service_number_6,
                'bruin_client_info': {
                    'client_id': 9994,
                    'client_name': 'EVIL-CORP'
                },
            },
        }

        ticket_topic = 'Service Outage Trouble'
        tickets_creator = 'Intelygenz Ai'

        ticket_1_id = 12345
        ticket_1_creation_date = "1/02/2021 10:08:13 AM"
        ticket_1_details = [
            {
                "detailID": 2746937,
                "detailValue": service_number_1,
            },
        ]
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": None,
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                service_number_1,
            ],
        }
        ticket_1_note_2 = {
            "noteId": 41894041,
            "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                service_number_1,
                service_number_3,
            ],
        }
        ticket_1_note_3 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                service_number_3,
            ],
        }
        ticket_1_note_4 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                service_number_1,
            ],
        }
        ticket_1_note_5 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                service_number_1,
            ],
        }
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_creation_date': ticket_1_creation_date,
            'ticket_topic': ticket_topic,
            'ticket_creator': tickets_creator,
            'ticket_details': ticket_1_details,
            'ticket_notes': [
                ticket_1_note_1,
                ticket_1_note_2,
                ticket_1_note_3,
                ticket_1_note_4,
                ticket_1_note_5,
            ],
        }

        ticket_2_id = 11223
        ticket_2_creation_date = "1/03/2021 10:08:13 AM"
        ticket_2_details = [
            {
                "detailID": 2746938,
                "detailValue": service_number_2,
            },
            {
                "detailID": 2746938,
                "detailValue": service_number_4,
            },
        ]
        ticket_2_note_1 = {
            "noteId": 41894042,
            "noteValue": 'There were some troubles with this service number',
            "createdDate": "2020-02-24T10:08:13.503-05:00",
            "serviceNumber": [
                service_number_2,
            ],
        }
        ticket_2_note_2 = {
            "noteId": 41894042,
            "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:08:13.503-05:00",
            "serviceNumber": [
                service_number_2,
                service_number_4,
            ],
        }
        ticket_2_note_3 = {
            "noteId": 41894042,
            "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:08:13.503-05:00",
            "serviceNumber": [
                service_number_3,
                service_number_5,
            ],
        }
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_creation_date': ticket_2_creation_date,
            'ticket_topic': ticket_topic,
            'ticket_creator': tickets_creator,
            'ticket_details': ticket_2_details,
            'ticket_notes': [
                ticket_2_note_1,
                ticket_2_note_2,
                ticket_2_note_3,
            ],
        }

        ticket_3_id = 67890
        ticket_3_creation_date = "1/04/2021 10:08:13 AM"
        ticket_3_details = [
            {
                "detailID": 2746937,
                "detailValue": service_number_6,
            },
        ]
        ticket_3_note_1 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": "2020-02-24T10:08:13.503-05:00",
            "serviceNumber": [
                service_number_5,
                service_number_6,
            ],
        }
        ticket_3_note_2 = {
            "noteId": 41894042,
            "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:08:13.503-05:00",
            "serviceNumber": [
                service_number_5,
                service_number_6,
            ],
        }
        ticket_3 = {
            'ticket_id': ticket_3_id,
            'ticket_creation_date': ticket_3_creation_date,
            'ticket_topic': ticket_topic,
            'ticket_creator': tickets_creator,
            'ticket_details': ticket_3_details,
            'ticket_notes': [
                ticket_3_note_1,
                ticket_3_note_2,
            ],
        }

        tickets = [
            ticket_1,
            ticket_2,
            ticket_3,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        velocloud_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        customer_cache_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._customer_cache_by_serial = customer_cache_by_serial

        result = tnba_monitor._filter_irrelevant_notes_in_tickets(tickets)

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_creation_date': ticket_1_creation_date,
                'ticket_topic': ticket_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': ticket_1_details,
                'ticket_notes': [
                    {
                        "noteId": 41894041,
                        "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                        "createdDate": "2020-02-24T10:07:13.503-05:00",
                        "serviceNumber": [
                            service_number_1,
                        ],
                    },
                ],
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_creation_date': ticket_2_creation_date,
                'ticket_topic': ticket_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': ticket_2_details,
                'ticket_notes': [
                    ticket_2_note_1,
                    ticket_2_note_2,
                ],
            },
            {
                'ticket_id': ticket_3_id,
                'ticket_creation_date': ticket_3_creation_date,
                'ticket_topic': ticket_topic,
                'ticket_creator': tickets_creator,
                'ticket_details': ticket_3_details,
                'ticket_notes': [
                    {
                        "noteId": 41894042,
                        "noteValue": f'#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                        "createdDate": "2020-02-24T10:08:13.503-05:00",
                        "serviceNumber": [
                            service_number_6,
                        ],
                    }
                ],
            },
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def get_predictions_by_ticket_id_ok_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        ticket_id = 12345

        ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_1_serial,
        }
        ticket_detail_2 = {
            "detailID": 2746938,
            "detailValue": edge_2_serial,
        }
        ticket_detail_3 = {
            "detailID": 2746939,
            "detailValue": edge_3_serial,
        }
        ticket_details = [
            ticket_detail_1,
            ticket_detail_2,
            ticket_detail_3,
        ]
        ticket_with_details = {
            'ticket_id': ticket_id,
            'ticket_details': ticket_details,
            'ticket_notes': [],
        }

        tickets = [
            ticket_with_details,
        ]

        ticket_predictions_for_serial_1 = {
            'assetId': edge_1_serial,
            'predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
            ],
        }
        ticket_predictions_for_serial_2 = {
            'assetId': edge_2_serial,
            'predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
            ],
        }
        ticket_predictions = [
            ticket_predictions_for_serial_1,
            ticket_predictions_for_serial_2,
        ]

        get_predictions_response = {
            'body': ticket_predictions,
            'status': 200,
        }

        task_history = [
            {
                "Initial Note @ Ticket Creation": "Automation Engine -- Service Outage Trouble",
                "DetailID": 5672725,
                "Product": "SD-WAN",
                "Asset": edge_1_serial,
                "Ticket Status": "In Progress",
                # Rest of fields omitted for simplicity
            }
        ]
        get_task_history_response = {
            'body': task_history,
            'status': 200,
        }

        assets_to_predict = ['VC1234567', 'VC7654321', 'VC1111111']

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        ticket_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = CoroutineMock(return_value=get_task_history_response)

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(return_value=get_predictions_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        result = await tnba_monitor._get_predictions_by_ticket_id(tickets)

        bruin_repository.get_ticket_task_history.assert_awaited_once_with(ticket_id)
        t7_repository.get_prediction.assert_awaited_once_with(ticket_id, task_history, assets_to_predict)

        expected = {
            ticket_id: ticket_predictions,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_predictions_by_ticket_id_with_retrieval_of_task_history_returning_non_2xx_status_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        ticket_id = 12345

        ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_1_serial,
        }
        ticket_detail_2 = {
            "detailID": 2746938,
            "detailValue": edge_2_serial,
        }
        ticket_detail_3 = {
            "detailID": 2746939,
            "detailValue": edge_3_serial,
        }
        ticket_details = [
            ticket_detail_1,
            ticket_detail_2,
            ticket_detail_3,
        ]
        ticket_with_details = {
            'ticket_id': ticket_id,
            'ticket_details': ticket_details,
            'ticket_notes': [],
        }

        tickets = [
            ticket_with_details,
        ]

        get_task_history_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        ticket_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = CoroutineMock(return_value=get_task_history_response)

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        result = await tnba_monitor._get_predictions_by_ticket_id(tickets)

        bruin_repository.get_ticket_task_history.assert_awaited_once_with(ticket_id)
        t7_repository.get_prediction.assert_not_awaited()

        expected = {}
        assert result == expected

    @pytest.mark.asyncio
    async def get_predictions_by_ticket_id_with_not_a_single_valid_asset_in_task_history_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        ticket_id = 12345

        ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_1_serial,
        }
        ticket_detail_2 = {
            "detailID": 2746938,
            "detailValue": edge_2_serial,
        }
        ticket_detail_3 = {
            "detailID": 2746939,
            "detailValue": edge_3_serial,
        }
        ticket_details = [
            ticket_detail_1,
            ticket_detail_2,
            ticket_detail_3,
        ]
        ticket_with_details = {
            'ticket_id': ticket_id,
            'ticket_details': ticket_details,
            'ticket_notes': [],
        }

        tickets = [
            ticket_with_details,
        ]

        task_history = [
            {
                "Initial Note @ Ticket Creation": "Automation Engine -- Service Outage Trouble",
                "DetailID": 5672725,
                "Product": "SD-WAN",
                "Asset": None,
                "Ticket Status": "In Progress",
                # Rest of fields omitted for simplicity
            }
        ]
        get_task_history_response = {
            'body': task_history,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        ticket_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = CoroutineMock(return_value=get_task_history_response)

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        result = await tnba_monitor._get_predictions_by_ticket_id(tickets)

        bruin_repository.get_ticket_task_history.assert_awaited_once_with(ticket_id)
        t7_repository.get_prediction.assert_not_awaited()

        expected = {}
        assert result == expected

    @pytest.mark.asyncio
    async def get_predictions_by_ticket_id_with_retrieval_of_predictions_returning_non_2xx_status_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        ticket_id = 12345

        ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_1_serial,
        }
        ticket_detail_2 = {
            "detailID": 2746938,
            "detailValue": edge_2_serial,
        }
        ticket_detail_3 = {
            "detailID": 2746939,
            "detailValue": edge_3_serial,
        }
        ticket_details = [
            ticket_detail_1,
            ticket_detail_2,
            ticket_detail_3,
        ]
        ticket_with_details = {
            'ticket_id': ticket_id,
            'ticket_details': ticket_details,
            'ticket_notes': [],
        }

        tickets = [
            ticket_with_details,
        ]

        get_predictions_response = {
            'body': 'Got internal error from T7',
            'status': 500,
        }

        task_history = [
            {
                "Initial Note @ Ticket Creation": "Automation Engine -- Service Outage Trouble",
                "DetailID": 5672725,
                "Product": "SD-WAN",
                "Asset": edge_1_serial,
                "Ticket Status": "In Progress",
                # Rest of fields omitted for simplicity
            }
        ]
        get_task_history_response = {
            'body': task_history,
            'status': 200,
        }

        assets_to_predict = ['VC1234567', 'VC7654321', 'VC1111111']

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        ticket_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = CoroutineMock(return_value=get_task_history_response)

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(return_value=get_predictions_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        result = await tnba_monitor._get_predictions_by_ticket_id(tickets)

        bruin_repository.get_ticket_task_history.assert_awaited_once_with(ticket_id)
        t7_repository.get_prediction.assert_awaited_once_with(ticket_id, task_history, assets_to_predict)

        expected = {}
        assert result == expected

    @pytest.mark.asyncio
    async def get_predictions_by_ticket_id_with_no_predictions_found_for_ticket_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        ticket_id = 12345

        ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_1_serial,
        }
        ticket_detail_2 = {
            "detailID": 2746938,
            "detailValue": edge_2_serial,
        }
        ticket_detail_3 = {
            "detailID": 2746939,
            "detailValue": edge_3_serial,
        }
        ticket_details = [
            ticket_detail_1,
            ticket_detail_2,
            ticket_detail_3,
        ]
        ticket_with_details = {
            'ticket_id': ticket_id,
            'ticket_details': ticket_details,
            'ticket_notes': [],
        }

        tickets = [
            ticket_with_details,
        ]

        get_predictions_response = {
            'body': [],
            'status': 200,
        }

        task_history = [
            {
                "Initial Note @ Ticket Creation": "Automation Engine -- Service Outage Trouble",
                "DetailID": 5672725,
                "Product": "SD-WAN",
                "Asset": edge_1_serial,
                "Ticket Status": "In Progress",
                # Rest of fields omitted for simplicity
            }
        ]
        get_task_history_response = {
            'body': task_history,
            'status': 200,
        }

        assets_to_predict = ['VC1234567', 'VC7654321', 'VC1111111']

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        ticket_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = CoroutineMock(return_value=get_task_history_response)

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(return_value=get_predictions_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        result = await tnba_monitor._get_predictions_by_ticket_id(tickets)

        bruin_repository.get_ticket_task_history.assert_awaited_once_with(ticket_id)
        t7_repository.get_prediction.assert_awaited_once_with(ticket_id, task_history, assets_to_predict)

        expected = {}
        assert result == expected

    @pytest.mark.asyncio
    async def remove_erroneous_predictions_with_some_predictions_being_erroneous_test(self):
        ticket_id = 12345
        ticket_prediction_object_1 = {
            'assetId': 'VC1234567',
            'predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
            ],
        }
        ticket_prediction_object_2 = {
            'assetId': 'VC7654321',
            'error': {
                'code': 'error_in_prediction',
                'message': (
                    'Error executing prediction: The labels [\'Additional Information Required\'] are not in the '
                    '"task_result" labels map.'
                ),
            },
        }
        ticket_prediction_object_3 = {
            'assetId': 'VC7654321',
            'predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
            ],
        }
        predictions_by_ticket_id = {
            ticket_id: [
                ticket_prediction_object_1,
                ticket_prediction_object_2,
                ticket_prediction_object_3,
            ],
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        bruin_repository = Mock()
        t7_repository = Mock()
        ticket_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        result = tnba_monitor._remove_erroneous_predictions(predictions_by_ticket_id)

        assert result == {
            ticket_id: [
                ticket_prediction_object_1,
                ticket_prediction_object_3,
            ],
        }

    @pytest.mark.asyncio
    async def remove_erroneous_predictions_with_all_predictions_being_erroneous_test(self):
        ticket_id = 12345
        ticket_prediction_object_1 = {
            'assetId': 'VC1234567',
            'error': {
                'code': 'error_in_prediction',
                'message': (
                    'Error executing prediction: The labels [\'Additional Information Required\'] are not in the '
                    '"task_result" labels map.'
                ),
            },
        }
        ticket_prediction_object_2 = {
            'assetId': 'VC7654321',
            'error': {
                'code': 'error_in_prediction',
                'message': (
                    'Error executing prediction: The labels [\'Additional Information Required\'] are not in the '
                    '"task_result" labels map.'
                ),
            },
        }
        ticket_prediction_object_3 = {
            'assetId': 'VC7654321',
            'error': {
                'code': 'error_in_prediction',
                'message': (
                    'Error executing prediction: The labels [\'Additional Information Required\'] are not in the '
                    '"task_result" labels map.'
                ),
            },
        }
        predictions_by_ticket_id = {
            ticket_id: [
                ticket_prediction_object_1,
                ticket_prediction_object_2,
                ticket_prediction_object_3,
            ],
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        bruin_repository = Mock()
        t7_repository = Mock()
        ticket_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        result = tnba_monitor._remove_erroneous_predictions(predictions_by_ticket_id)

        assert result == {}

    @pytest.mark.asyncio
    async def map_ticket_details_with_predictions_test(self):
        edge_serial_1 = 'VC1234567'
        edge_serial_2 = 'VC7654321'
        edge_serial_3 = 'VC7654321'

        ticket_id_1 = 12345
        ticket_id_2 = 67890
        ticket_creation_date = "1/02/2021 10:08:13 AM"
        ticket_topic = "Service Outage Trouble"
        tickets_creator = 'Intelygenz Ai'

        ticket_prediction_object_1_predictions = [
            {
                'name': 'Repair Completed',
                'probability': 0.9484384655952454
            },
        ]
        ticket_prediction_object_1 = {
            'assetId': edge_serial_1,
            'predictions': ticket_prediction_object_1_predictions,
        }

        ticket_prediction_object_2_predictions = [
            {
                'name': 'Repair Completed',
                'probability': 0.9484384655952454
            },
        ]
        ticket_prediction_object_2 = {
            'assetId': edge_serial_2,
            'predictions': ticket_prediction_object_2_predictions,
        }
        predictions_by_ticket_id = {
            ticket_id_1: [
                ticket_prediction_object_1,
                ticket_prediction_object_2,
            ],
        }

        ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_serial_1,
        }
        ticket_detail_2 = {
            "detailID": 2746938,
            "detailValue": edge_serial_2,
        }
        ticket_detail_3 = {
            "detailID": 2746939,
            "detailValue": edge_serial_3,
        }
        ticket_detail_4 = {
            "detailID": 2746940,
            "detailValue": edge_serial_1,
        }

        ticket_detail_object_1 = {
            'ticket_id': ticket_id_1,
            'ticket_creation_date': ticket_creation_date,
            'ticket_topic': ticket_topic,
            'ticket_creator': tickets_creator,
            'ticket_detail': ticket_detail_1,
            'ticket_notes': [],
        }
        ticket_detail_object_2 = {
            'ticket_id': ticket_id_1,
            'ticket_creation_date': ticket_creation_date,
            'ticket_topic': ticket_topic,
            'ticket_creator': tickets_creator,
            'ticket_detail': ticket_detail_2,
            'ticket_notes': [],
        }
        ticket_detail_object_3 = {
            'ticket_id': ticket_id_1,
            'ticket_creation_date': ticket_creation_date,
            'ticket_topic': ticket_topic,
            'ticket_creator': tickets_creator,
            'ticket_detail': ticket_detail_3,
            'ticket_notes': [],
        }
        ticket_detail_object_4 = {
            'ticket_id': ticket_id_2,
            'ticket_creation_date': ticket_creation_date,
            'ticket_topic': ticket_topic,
            'ticket_detail': ticket_detail_4,
            'ticket_notes': [],
        }
        ticket_detail_objects = [
            ticket_detail_object_1,
            ticket_detail_object_2,
            ticket_detail_object_3,
            ticket_detail_object_4,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(side_effect=[
            ticket_prediction_object_1,
            ticket_prediction_object_2,
            None,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        result = tnba_monitor._map_ticket_details_with_predictions(ticket_detail_objects, predictions_by_ticket_id)

        assert result == [
            {
                **ticket_detail_object_1,
                'ticket_detail_predictions': ticket_prediction_object_1_predictions,
            },
            {
                **ticket_detail_object_2,
                'ticket_detail_predictions': ticket_prediction_object_2_predictions,
            }
        ]

    @pytest.mark.asyncio
    async def distinguish_ticket_details_with_and_without_tnba_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        ticket_1_id = 12345
        ticket_1_creation_date = "1/02/2021 10:08:13 AM"
        ticket_topic = "Service Outage Trouble"
        tickets_creator = 'Intelygenz Ai'

        ticket_1_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_1_serial,
        }
        ticket_1_detail_2 = {
            "detailID": 2746938,
            "detailValue": edge_2_serial,
        }
        ticket_1_detail_3 = {
            "detailID": 2746939,
            "detailValue": edge_3_serial,
        }
        ticket_1_details = [
            ticket_1_detail_1,
            ticket_1_detail_2,
            ticket_1_detail_3,
        ]
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                edge_1_serial,
            ]
        }
        ticket_1_note_2 = {
            "noteId": 41894041,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                edge_1_serial,
            ]
        }
        ticket_1_note_3 = {
            "noteId": 41894042,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                edge_1_serial,
                edge_2_serial,
            ]
        }
        ticket_1_note_4 = {
            "noteId": 41894044,
            "noteValue": f'#*Automation Engine*#\nRe-opening\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                edge_2_serial,
            ]
        }
        ticket_1_with_details = {
            'ticket_id': ticket_1_id,
            'ticket_creation_date': ticket_1_creation_date,
            'ticket_topic': ticket_topic,
            'ticket_creator': tickets_creator,
            'ticket_details': ticket_1_details,
            'ticket_notes': [
                ticket_1_note_1,
                ticket_1_note_2,
                ticket_1_note_3,
                ticket_1_note_4,
            ],
        }

        ticket_2_id = 11223
        ticket_2_creation_date = "1/03/2021 10:08:13 AM"
        ticket_2_detail_1 = {
            "detailID": 2746938,
            "detailValue": edge_1_serial,
        }
        ticket_2_detail_2 = {
            "detailID": 2746938,
            "detailValue": edge_2_serial,
        }
        ticket_2_details = [
            ticket_2_detail_1,
            ticket_2_detail_2,
        ]
        ticket_2_note_1 = {
            "noteId": 41894042,
            "noteValue": 'There were some troubles with this service number',
            "createdDate": "2020-02-24T10:08:13.503-05:00",
            "serviceNumber": [
                edge_1_serial,
            ]
        }
        ticket_2_with_details = {
            'ticket_id': ticket_2_id,
            'ticket_creation_date': ticket_2_creation_date,
            'ticket_topic': ticket_topic,
            'ticket_creator': tickets_creator,
            'ticket_details': ticket_2_details,
            'ticket_notes': [
                ticket_2_note_1,
            ],
        }

        tickets = [
            ticket_1_with_details,
            ticket_2_with_details,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        bruin_repository = Mock()
        t7_repository = Mock()
        utils_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.has_tnba_note = Mock(side_effect=[
            True,
            True,
            False,
            False,
            False,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        ticket_details_with_tnba, ticket_details_without_tnba = \
            tnba_monitor._distinguish_ticket_details_with_and_without_tnba(tickets)

        assert ticket_details_with_tnba == [
            {
                'ticket_id': ticket_1_id,
                'ticket_creation_date': ticket_1_creation_date,
                'ticket_topic': ticket_topic,
                'ticket_creator': tickets_creator,
                'ticket_detail': ticket_1_detail_1,
                'ticket_notes': [
                    ticket_1_note_1,
                    ticket_1_note_2,
                    ticket_1_note_3,
                ],
            },
            {
                'ticket_id': ticket_1_id,
                'ticket_creation_date': ticket_1_creation_date,
                'ticket_topic': ticket_topic,
                'ticket_creator': tickets_creator,
                'ticket_detail': ticket_1_detail_2,
                'ticket_notes': [
                    ticket_1_note_3,
                    ticket_1_note_4,
                ],
            }
        ]
        assert ticket_details_without_tnba == [
            {
                'ticket_id': ticket_1_id,
                'ticket_creation_date': ticket_1_creation_date,
                'ticket_topic': ticket_topic,
                'ticket_creator': tickets_creator,
                'ticket_detail': ticket_1_detail_3,
                'ticket_notes': [],
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_creation_date': ticket_2_creation_date,
                'ticket_topic': ticket_topic,
                'ticket_creator': tickets_creator,
                'ticket_detail': ticket_2_detail_1,
                'ticket_notes': [
                    ticket_2_note_1,
                ],
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_creation_date': ticket_2_creation_date,
                'ticket_topic': ticket_topic,
                'ticket_creator': tickets_creator,
                'ticket_detail': ticket_2_detail_2,
                'ticket_notes': [],
            },
        ]

    def filter_outage_ticket_details_based_on_last_outage_with_affecting_ticket_details_test(self):
        affecting_ticket_detail_1 = {
            'ticket_id': 12345,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': 1,
                'detailValue': 'VC1234567',
            },
            'ticket_notes': [],
        }
        affecting_ticket_detail_2 = {
            'ticket_id': 67890,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': 1,
                'detailValue': 'VC1234567',
            },
            'ticket_notes': [],
        }
        ticket_details = [
            affecting_ticket_detail_1,
            affecting_ticket_detail_2,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        bruin_repository = Mock()
        t7_repository = Mock()
        utils_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.is_detail_in_outage_ticket = Mock(return_value=False)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        result = tnba_monitor._filter_outage_ticket_details_based_on_last_outage(ticket_details)
        assert result == ticket_details

    def filter_outage_ticket_details_based_on_last_outage_with_outage_ticket_details_test(self):
        outage_ticket_detail_1 = {
            'ticket_id': 12345,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Outage Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': 1,
                'detailValue': 'VC1234567',
            },
            'ticket_notes': [],
        }
        outage_ticket_detail_2 = {
            'ticket_id': 67890,
            'ticket_creation_date': "1/04/2021 10:08:13 AM",
            'ticket_topic': "Service Outage Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': 1,
                'detailValue': 'VC1234567',
            },
            'ticket_notes': [],
        }
        ticket_details = [
            outage_ticket_detail_1,
            outage_ticket_detail_2,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        bruin_repository = Mock()
        t7_repository = Mock()
        utils_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.is_detail_in_outage_ticket = Mock(return_value=True)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._was_last_outage_detected_recently = Mock(side_effect=[
            True,
            False,
        ])

        result = tnba_monitor._filter_outage_ticket_details_based_on_last_outage(ticket_details)
        expected = [
            outage_ticket_detail_2,
        ]
        assert result == expected

    def was_last_outage_detected_recently_with_reopen_note_not_found_and_triage_not_found_test(self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        ticket_notes = []

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        bruin_repository = Mock()
        t7_repository = Mock()
        ticket_repository = Mock()
        utils_repository = UtilsRepository()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        new_now = parse(ticket_creation_date) + timedelta(minutes=59, seconds=59)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(ticket_creation_date) + timedelta(hours=1)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(ticket_creation_date) + timedelta(hours=1, seconds=1)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    def was_last_outage_detected_recently_with_reopen_note_found_test(self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        triage_timestamp = '2021-01-02T10:18:16.71-05:00'
        reopen_timestamp = '2021-01-02T11:00:16.71-05:00'

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*Automation Engine*#\nTriage\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                'VC1234567',
            ],
            "createdDate": triage_timestamp,
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*Automation Engine*#\nRe-opening\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                'VC1234567',
            ],
            "createdDate": reopen_timestamp,
        }

        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        bruin_repository = Mock()
        t7_repository = Mock()
        ticket_repository = Mock()
        utils_repository = UtilsRepository()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        datetime_mock = Mock()

        new_now = parse(reopen_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    def was_last_outage_detected_recently_with_reopen_note_not_found_and_triage_note_found_test(self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        triage_timestamp = '2021-01-02T10:18:16.71-05:00'

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                'VC1234567',
            ],
            "createdDate": triage_timestamp,
        }

        ticket_notes = [
            ticket_note_1,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        bruin_repository = Mock()
        t7_repository = Mock()
        ticket_repository = Mock()
        utils_repository = UtilsRepository()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        datetime_mock = Mock()

        new_now = parse(triage_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    @pytest.mark.asyncio
    async def process_ticket_details_without_tnba_ok_test(self):
        detail_object_1 = {
            'ticket_id': 12345,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': 1,
                'detailValue': 'VC1234567',
            },
            'ticket_notes': [],
            'ticket_detail_predictions': [
                {
                    'name': 'Service Repaired',
                    'probability': 0.9484384655952454
                },
            ]
        }
        detail_object_2 = {
            'ticket_id': 12345,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': 2,
                'detailValue': 'VC8909876',
            },
            'ticket_notes': [],
            'ticket_detail_predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
            ]
        }
        ticket_details = [
            detail_object_1,
            detail_object_2,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        t7_repository = Mock()
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        ticket_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._process_ticket_detail_without_tnba = CoroutineMock()

        await tnba_monitor._process_ticket_details_without_tnba(ticket_details)

        tnba_monitor._process_ticket_detail_without_tnba.assert_has_awaits([
            call(detail_object_1),
            call(detail_object_2),
        ], any_order=True)

    @pytest.mark.asyncio
    async def process_ticket_details_without_tnba_with_empty_list_of_ticket_details_test(self):
        ticket_details = []

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.build_tnba_note_from_prediction = Mock()

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock()
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._process_ticket_detail_without_tnba = CoroutineMock()

        await tnba_monitor._process_ticket_details_without_tnba(ticket_details)

        tnba_monitor._process_ticket_detail_without_tnba.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_ticket_detail_without_tnba_with_retrieval_of_next_results_returning_non_2xx_status_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        serial_number = 'VC1234567'

        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': [],
            'ticket_detail_predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
            ]
        }

        next_results_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.build_tnba_note_from_prediction = Mock()

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=next_results_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        await tnba_monitor._process_ticket_detail_without_tnba(detail_object)

        bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number
        )
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def process_ticket_detail_without_tnba_with_no_predictions_after_filtering_with_next_results_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        serial_number = 'VC1234567'

        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': [],
            'ticket_detail_predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
            ]
        }

        next_results_response = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    {
                        "resultTypeId": 620,
                        "resultName": "Request Completed",
                        "notes": [
                            {
                                "noteType": "Notes",
                                "noteDescription": "Notes",
                                "availableValueOptions": None,
                                "defaultValue": None,
                                "required": False,
                            }
                        ]
                    }
                ],
            },
            'status': 200,
        }

        filtered_predictions = []

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        ticket_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        prediction_repository = Mock()
        prediction_repository.filter_predictions_in_next_results = Mock(return_value=filtered_predictions)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=next_results_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        await tnba_monitor._process_ticket_detail_without_tnba(detail_object)

        bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number
        )
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def process_ticket_detail_without_tnba_with_dev_env_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        serial_number = 'VC1234567'

        ticket_detail_prediction_1 = {
            'name': 'ASR Issue Resolved',
            'probability': 0.9484384655952454
        }
        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': [],
            'ticket_detail_predictions': [
                ticket_detail_prediction_1,
            ]
        }

        next_results_response = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    {
                        "resultTypeId": 620,
                        "resultName": "ASR Issue Resolved",
                        "notes": [
                            {
                                "noteType": "Notes",
                                "noteDescription": "Notes",
                                "availableValueOptions": None,
                                "defaultValue": None,
                                "required": False,
                            }
                        ]
                    }
                ],
            },
            'status': 200,
        }

        filtered_predictions = [
            ticket_detail_prediction_1,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        ticket_repository = Mock()
        t7_repository = Mock()
        utils_repository = Mock()

        prediction_repository = Mock()
        prediction_repository.filter_predictions_in_next_results = Mock(return_value=filtered_predictions)
        prediction_repository.get_best_prediction = Mock(return_value=ticket_detail_prediction_1)
        prediction_repository.is_request_or_repair_completed_prediction = Mock(return_value=False)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=next_results_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        with patch.object(config, 'ENVIRONMENT', "dev"):
            await tnba_monitor._process_ticket_detail_without_tnba(detail_object)

        bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number
        )
        ticket_repository.build_tnba_note_from_prediction.assert_called_once_with(
            ticket_detail_prediction_1, serial_number
        )
        notifications_repository.send_slack_message.assert_awaited_once()
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def process_ticket_detail_without_tnba_with_non_request_or_repair_completed_prediction_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        serial_number = 'VC1234567'

        ticket_detail_prediction_1 = {
            'name': 'ASR Issue Resolved',
            'probability': 0.9484384655952454
        }
        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': [],
            'ticket_detail_predictions': [
                ticket_detail_prediction_1,
            ]
        }

        next_results_response = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    {
                        "resultTypeId": 620,
                        "resultName": "ASR Issue Resolved",
                        "notes": [
                            {
                                "noteType": "Notes",
                                "noteDescription": "Notes",
                                "availableValueOptions": None,
                                "defaultValue": None,
                                "required": False,
                            }
                        ]
                    }
                ],
            },
            'status': 200,
        }

        filtered_predictions = [
            ticket_detail_prediction_1,
        ]

        tnba_note = 'This is a TNBA note'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        prediction_repository = Mock()
        prediction_repository.filter_predictions_in_next_results = Mock(return_value=filtered_predictions)
        prediction_repository.get_best_prediction = Mock(return_value=ticket_detail_prediction_1)
        prediction_repository.is_request_or_repair_completed_prediction = Mock(return_value=False)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=next_results_response)

        ticket_repository = Mock()
        ticket_repository.build_tnba_note_from_prediction = Mock(return_value=tnba_note)
        ticket_repository.build_tnba_note_from_request_or_repair_completed_prediction = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._autoresolve_ticket_detail = CoroutineMock()

        with patch.object(config, 'ENVIRONMENT', "production"):
            await tnba_monitor._process_ticket_detail_without_tnba(detail_object)

        bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number
        )
        prediction_repository.is_request_or_repair_completed_prediction.assert_called_once_with(
            ticket_detail_prediction_1
        )
        tnba_monitor._autoresolve_ticket_detail.assert_not_awaited()
        ticket_repository.build_tnba_note_from_request_or_repair_completed_prediction.assert_not_called()
        ticket_repository.build_tnba_note_from_prediction.assert_called_once_with(
            ticket_detail_prediction_1, serial_number
        )
        assert tnba_monitor._tnba_notes_to_append == [
            {
                'ticket_id': ticket_id,
                'text': tnba_note,
                'detail_id': ticket_detail_id,
                'service_number': serial_number,
            }
        ]

    @pytest.mark.asyncio
    async def process_ticket_detail_without_tnba_with_request_repair_completed_prediction_and_autoresolve_failed_test(
            self):
        ticket_id = 12345
        ticket_detail_id = 1
        serial_number = 'VC1234567'

        ticket_detail_prediction_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': [],
            'ticket_detail_predictions': [
                ticket_detail_prediction_1,
            ]
        }

        next_results_response = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    {
                        "resultTypeId": 620,
                        "resultName": "Repair Completed",
                        "notes": [
                            {
                                "noteType": "Notes",
                                "noteDescription": "Notes",
                                "availableValueOptions": None,
                                "defaultValue": None,
                                "required": False,
                            }
                        ]
                    }
                ],
            },
            'status': 200,
        }

        filtered_predictions = [
            ticket_detail_prediction_1,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        prediction_repository = Mock()
        prediction_repository.filter_predictions_in_next_results = Mock(return_value=filtered_predictions)
        prediction_repository.get_best_prediction = Mock(return_value=ticket_detail_prediction_1)
        prediction_repository.is_request_or_repair_completed_prediction = Mock(return_value=True)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=next_results_response)

        ticket_repository = Mock()
        ticket_repository.build_tnba_note_from_prediction = Mock()
        ticket_repository.build_tnba_note_from_request_or_repair_completed_prediction = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._autoresolve_ticket_detail = CoroutineMock(return_value=False)

        with patch.object(config, 'ENVIRONMENT', "production"):
            await tnba_monitor._process_ticket_detail_without_tnba(detail_object)

        bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number
        )
        prediction_repository.is_request_or_repair_completed_prediction.assert_called_once_with(
            ticket_detail_prediction_1
        )
        tnba_monitor._autoresolve_ticket_detail.assert_awaited_once_with(
            detail_object=detail_object,
            best_prediction=ticket_detail_prediction_1,
        )
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        ticket_repository.build_tnba_note_from_request_or_repair_completed_prediction.assert_not_called()
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def process_ticket_detail_without_tnba_with_request_repair_completed_prediction_and_autoresolve_ok_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        serial_number = 'VC1234567'

        ticket_detail_prediction_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': [],
            'ticket_detail_predictions': [
                ticket_detail_prediction_1,
            ]
        }

        next_results_response = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    {
                        "resultTypeId": 620,
                        "resultName": "Repair Completed",
                        "notes": [
                            {
                                "noteType": "Notes",
                                "noteDescription": "Notes",
                                "availableValueOptions": None,
                                "defaultValue": None,
                                "required": False,
                            }
                        ]
                    }
                ],
            },
            'status': 200,
        }

        filtered_predictions = [
            ticket_detail_prediction_1,
        ]

        tnba_note = 'This is a TNBA note'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        prediction_repository = Mock()
        prediction_repository.filter_predictions_in_next_results = Mock(return_value=filtered_predictions)
        prediction_repository.get_best_prediction = Mock(return_value=ticket_detail_prediction_1)
        prediction_repository.is_request_or_repair_completed_prediction = Mock(return_value=True)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=next_results_response)

        ticket_repository = Mock()
        ticket_repository.build_tnba_note_from_prediction = Mock()
        ticket_repository.build_tnba_note_from_request_or_repair_completed_prediction = Mock(return_value=tnba_note)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._autoresolve_ticket_detail = CoroutineMock(return_value=True)

        with patch.object(config, 'ENVIRONMENT', "production"):
            await tnba_monitor._process_ticket_detail_without_tnba(detail_object)

        bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number
        )
        prediction_repository.is_request_or_repair_completed_prediction.assert_called_once_with(
            ticket_detail_prediction_1
        )
        tnba_monitor._autoresolve_ticket_detail.assert_awaited_once_with(
            detail_object=detail_object,
            best_prediction=ticket_detail_prediction_1,
        )
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        ticket_repository.build_tnba_note_from_request_or_repair_completed_prediction.assert_called_once_with(
            ticket_detail_prediction_1, serial_number
        )
        assert tnba_monitor._tnba_notes_to_append == [
            {
                'ticket_id': ticket_id,
                'text': tnba_note,
                'detail_id': ticket_detail_id,
                'service_number': serial_number,
            }
        ]

    @pytest.mark.asyncio
    async def process_ticket_details_with_tnba_ok_test(self):
        detail_object_1 = {
            'ticket_id': 12345,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': 1,
                'detailValue': 'VC1234567',
            },
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                }
            ],
            'ticket_detail_predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
            ]
        }
        detail_object_2 = {
            'ticket_id': 12345,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': 2,
                'detailValue': 'VC8909876',
            },
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                }
            ],
            'ticket_detail_predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
            ]
        }
        ticket_details = [
            detail_object_1,
            detail_object_2,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        ticket_repository = Mock()
        prediction_repository = Mock()
        bruin_repository = Mock()
        t7_repository = Mock()
        utils_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._process_ticket_detail_with_tnba = CoroutineMock()

        await tnba_monitor._process_ticket_details_with_tnba(ticket_details)

        tnba_monitor._process_ticket_detail_with_tnba.assert_has_awaits([
            call(detail_object_1),
            call(detail_object_2),
        ], any_order=True)

    @pytest.mark.asyncio
    async def process_ticket_details_with_tnba_with_empty_list_of_ticket_details_test(self):
        ticket_details = []

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        ticket_repository = Mock()
        prediction_repository = Mock()
        bruin_repository = Mock()
        t7_repository = Mock()
        utils_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._process_ticket_detail_with_tnba = CoroutineMock()

        await tnba_monitor._process_ticket_details_with_tnba(ticket_details)

        tnba_monitor._process_ticket_detail_with_tnba.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_ticket_detail_with_tnba_with_tnba_note_too_recent_for_a_new_append_test(self):
        ticket_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_notes = [
            ticket_note_1,
        ]

        serial_number = 'VC1234567'

        detail_object = {
            'ticket_id': 12345,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': 1,
                'detailValue': serial_number,
            },
            'ticket_notes': ticket_notes,
            'ticket_detail_predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
            ]
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        prediction_repository = Mock()
        bruin_repository = Mock()
        t7_repository = Mock()
        utils_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(return_value=ticket_note_1)
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=False)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        await tnba_monitor._process_ticket_detail_with_tnba(detail_object)

        ticket_repository.find_newest_tnba_note_by_service_number.assert_called_once_with(ticket_notes, serial_number)
        ticket_repository.is_tnba_note_old_enough.assert_called_once_with(ticket_note_1)
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def process_ticket_detail_with_tnba_with_retrieval_of_next_results_returning_non_2xx_status_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_notes = [
            ticket_note_1,
        ]

        serial_number = 'VC1234567'

        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': ticket_notes,
            'ticket_detail_predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
            ]
        }

        next_results_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        prediction_repository = Mock()
        t7_repository = Mock()
        utils_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(return_value=ticket_note_1)
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=next_results_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        await tnba_monitor._process_ticket_detail_with_tnba(detail_object)

        ticket_repository.find_newest_tnba_note_by_service_number.assert_called_once_with(ticket_notes, serial_number)
        ticket_repository.is_tnba_note_old_enough.assert_called_once_with(ticket_note_1)
        bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number
        )
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def process_ticket_detail_with_tnba_with_no_predictions_after_filtering_with_next_results_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_notes = [
            ticket_note_1,
        ]

        serial_number = 'VC1234567'

        ticket_detail_prediction_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': ticket_notes,
            'ticket_detail_predictions': [
                ticket_detail_prediction_1,
            ]
        }

        next_results_response = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    {
                        "resultTypeId": 620,
                        "resultName": "Request Completed",
                        "notes": [
                            {
                                "noteType": "Notes",
                                "noteDescription": "Notes",
                                "availableValueOptions": None,
                                "defaultValue": None,
                                "required": False,
                            }
                        ]
                    }
                ],
            },
            'status': 200,
        }

        filtered_predictions = []

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        prediction_repository = Mock()
        prediction_repository.filter_predictions_in_next_results = Mock(return_value=filtered_predictions)

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(return_value=ticket_note_1)
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=next_results_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        await tnba_monitor._process_ticket_detail_with_tnba(detail_object)

        ticket_repository.find_newest_tnba_note_by_service_number.assert_called_once_with(ticket_notes, serial_number)
        ticket_repository.is_tnba_note_old_enough.assert_called_once_with(ticket_note_1)
        bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number
        )
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def process_ticket_detail_with_tnba_with_no_changes_since_last_prediction_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_notes = [
            ticket_note_1,
        ]

        serial_number = 'VC1234567'

        ticket_detail_prediction_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': ticket_notes,
            'ticket_detail_predictions': [
                ticket_detail_prediction_1,
            ]
        }

        next_results_response = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    {
                        "resultTypeId": 620,
                        "resultName": "Repair Completed",
                        "notes": [
                            {
                                "noteType": "Notes",
                                "noteDescription": "Notes",
                                "availableValueOptions": None,
                                "defaultValue": None,
                                "required": False,
                            }
                        ]
                    }
                ],
            },
            'status': 200,
        }

        filtered_predictions = [
            ticket_detail_prediction_1,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        prediction_repository = Mock()
        prediction_repository.filter_predictions_in_next_results = Mock(return_value=filtered_predictions)
        prediction_repository.get_best_prediction = Mock(return_value=ticket_detail_prediction_1)
        prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note = Mock(return_value=False)

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(return_value=ticket_note_1)
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=next_results_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        await tnba_monitor._process_ticket_detail_with_tnba(detail_object)

        ticket_repository.find_newest_tnba_note_by_service_number.assert_called_once_with(ticket_notes, serial_number)
        ticket_repository.is_tnba_note_old_enough.assert_called_once_with(ticket_note_1)
        bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number
        )
        prediction_repository.get_best_prediction.assert_called_once_with(filtered_predictions)
        prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note.assert_called_once_with(
            ticket_note_1, ticket_detail_prediction_1
        )
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def process_ticket_detail_with_tnba_with_changes_since_last_prediction_and_dev_env_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_notes = [
            ticket_note_1,
        ]

        serial_number = 'VC1234567'

        ticket_detail_prediction_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': ticket_notes,
            'ticket_detail_predictions': [
                ticket_detail_prediction_1,
            ]
        }

        next_results_response = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    {
                        "resultTypeId": 620,
                        "resultName": "Repair Completed",
                        "notes": [
                            {
                                "noteType": "Notes",
                                "noteDescription": "Notes",
                                "availableValueOptions": None,
                                "defaultValue": None,
                                "required": False,
                            }
                        ]
                    }
                ],
            },
            'status': 200,
        }

        filtered_predictions = [
            ticket_detail_prediction_1,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        utils_repository = Mock()

        prediction_repository = Mock()
        prediction_repository.filter_predictions_in_next_results = Mock(return_value=filtered_predictions)
        prediction_repository.get_best_prediction = Mock(return_value=ticket_detail_prediction_1)
        prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note = Mock(return_value=True)
        prediction_repository.is_request_or_repair_completed_prediction = Mock(return_value=False)

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(return_value=ticket_note_1)
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=next_results_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        with patch.object(config, 'ENVIRONMENT', "dev"):
            await tnba_monitor._process_ticket_detail_with_tnba(detail_object)

        ticket_repository.find_newest_tnba_note_by_service_number.assert_called_once_with(ticket_notes, serial_number)
        ticket_repository.is_tnba_note_old_enough.assert_called_once_with(ticket_note_1)
        bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number
        )
        prediction_repository.get_best_prediction.assert_called_once_with(filtered_predictions)
        prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note.assert_called_once_with(
            ticket_note_1, ticket_detail_prediction_1
        )
        ticket_repository.build_tnba_note_from_prediction.assert_called_once_with(
            ticket_detail_prediction_1, serial_number
        )
        notifications_repository.send_slack_message.assert_awaited()
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def process_ticket_detail_with_tnba_with_non_request_or_repair_completed_prediction_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_notes = [
            ticket_note_1,
        ]

        serial_number = 'VC1234567'

        ticket_detail_prediction_1 = {
            'name': 'ASR Issue Resolved',
            'probability': 0.9484384655952454
        }
        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': ticket_notes,
            'ticket_detail_predictions': [
                ticket_detail_prediction_1,
            ]
        }

        next_results_response = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    {
                        "resultTypeId": 620,
                        "resultName": "ASR Issue Resolved",
                        "notes": [
                            {
                                "noteType": "Notes",
                                "noteDescription": "Notes",
                                "availableValueOptions": None,
                                "defaultValue": None,
                                "required": False,
                            }
                        ]
                    }
                ],
            },
            'status': 200,
        }

        filtered_predictions = [
            ticket_detail_prediction_1,
        ]

        tnba_note = 'This is a TNBA note'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        prediction_repository = Mock()
        prediction_repository.filter_predictions_in_next_results = Mock(return_value=filtered_predictions)
        prediction_repository.get_best_prediction = Mock(return_value=ticket_detail_prediction_1)
        prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note = Mock(return_value=True)
        prediction_repository.is_request_or_repair_completed_prediction = Mock(return_value=False)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=next_results_response)

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(return_value=ticket_note_1)
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)
        ticket_repository.build_tnba_note_from_prediction = Mock(return_value=tnba_note)
        ticket_repository.build_tnba_note_from_request_or_repair_completed_prediction = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._autoresolve_ticket_detail = CoroutineMock()

        with patch.object(config, 'ENVIRONMENT', "production"):
            await tnba_monitor._process_ticket_detail_with_tnba(detail_object)

        bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number
        )
        prediction_repository.is_request_or_repair_completed_prediction.assert_called_once_with(
            ticket_detail_prediction_1
        )
        tnba_monitor._autoresolve_ticket_detail.assert_not_awaited()
        ticket_repository.build_tnba_note_from_request_or_repair_completed_prediction.assert_not_called()
        ticket_repository.build_tnba_note_from_prediction.assert_called_once_with(
            ticket_detail_prediction_1, serial_number
        )
        assert tnba_monitor._tnba_notes_to_append == [
            {
                'ticket_id': ticket_id,
                'text': tnba_note,
                'detail_id': ticket_detail_id,
                'service_number': serial_number,
            }
        ]

    @pytest.mark.asyncio
    async def process_ticket_detail_with_tnba_with_request_repair_completed_prediction_and_autoresolve_failed_test(
            self):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_notes = [
            ticket_note_1,
        ]

        serial_number = 'VC1234567'

        ticket_detail_prediction_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': ticket_notes,
            'ticket_detail_predictions': [
                ticket_detail_prediction_1,
            ]
        }

        next_results_response = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    {
                        "resultTypeId": 620,
                        "resultName": "Repair Completed",
                        "notes": [
                            {
                                "noteType": "Notes",
                                "noteDescription": "Notes",
                                "availableValueOptions": None,
                                "defaultValue": None,
                                "required": False,
                            }
                        ]
                    }
                ],
            },
            'status': 200,
        }

        filtered_predictions = [
            ticket_detail_prediction_1,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        prediction_repository = Mock()
        prediction_repository.filter_predictions_in_next_results = Mock(return_value=filtered_predictions)
        prediction_repository.get_best_prediction = Mock(return_value=ticket_detail_prediction_1)
        prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note = Mock(return_value=True)
        prediction_repository.is_request_or_repair_completed_prediction = Mock(return_value=True)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=next_results_response)

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(return_value=ticket_note_1)
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)
        ticket_repository.build_tnba_note_from_prediction = Mock()
        ticket_repository.build_tnba_note_from_request_or_repair_completed_prediction = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._autoresolve_ticket_detail = CoroutineMock(return_value=False)

        with patch.object(config, 'ENVIRONMENT', "production"):
            await tnba_monitor._process_ticket_detail_with_tnba(detail_object)

        bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number
        )
        prediction_repository.is_request_or_repair_completed_prediction.assert_called_once_with(
            ticket_detail_prediction_1
        )
        tnba_monitor._autoresolve_ticket_detail.assert_awaited_once_with(
            detail_object=detail_object,
            best_prediction=ticket_detail_prediction_1,
        )
        ticket_repository.build_tnba_note_from_request_or_repair_completed_prediction.assert_not_called()
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def process_ticket_detail_without_tnba_with_request_repair_completed_prediction_and_autoresolve_ok_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_notes = [
            ticket_note_1,
        ]

        serial_number = 'VC1234567'

        ticket_detail_prediction_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': "Service Affecting Trouble",
            'ticket_creator': 'Intelygenz Ai',
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': ticket_notes,
            'ticket_detail_predictions': [
                ticket_detail_prediction_1,
            ]
        }

        next_results_response = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    {
                        "resultTypeId": 620,
                        "resultName": "Repair Completed",
                        "notes": [
                            {
                                "noteType": "Notes",
                                "noteDescription": "Notes",
                                "availableValueOptions": None,
                                "defaultValue": None,
                                "required": False,
                            }
                        ]
                    }
                ],
            },
            'status': 200,
        }

        filtered_predictions = [
            ticket_detail_prediction_1,
        ]

        tnba_note = 'This is a TNBA note'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        prediction_repository = Mock()
        prediction_repository.filter_predictions_in_next_results = Mock(return_value=filtered_predictions)
        prediction_repository.get_best_prediction = Mock(return_value=ticket_detail_prediction_1)
        prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note = Mock(return_value=True)
        prediction_repository.is_request_or_repair_completed_prediction = Mock(return_value=True)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=next_results_response)

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(return_value=ticket_note_1)
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)
        ticket_repository.build_tnba_note_from_prediction = Mock()
        ticket_repository.build_tnba_note_from_request_or_repair_completed_prediction = Mock(return_value=tnba_note)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._autoresolve_ticket_detail = CoroutineMock(return_value=True)

        with patch.object(config, 'ENVIRONMENT', "production"):
            await tnba_monitor._process_ticket_detail_with_tnba(detail_object)

        bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number
        )
        prediction_repository.is_request_or_repair_completed_prediction.assert_called_once_with(
            ticket_detail_prediction_1
        )
        tnba_monitor._autoresolve_ticket_detail.assert_awaited_once_with(
            detail_object=detail_object,
            best_prediction=ticket_detail_prediction_1,
        )
        ticket_repository.build_tnba_note_from_request_or_repair_completed_prediction.assert_called_once_with(
            ticket_detail_prediction_1, serial_number
        )
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        assert tnba_monitor._tnba_notes_to_append == [
            {
                'ticket_id': ticket_id,
                'text': tnba_note,
                'detail_id': ticket_detail_id,
                'service_number': serial_number,
            }
        ]

    @pytest.mark.asyncio
    async def autoresolve_ticket_detail_ok_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_creator = 'Intelygenz Ai'
        ticket_topic = 'Service Outage Trouble'

        serial_number = 'VC1234567'

        prediction = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }

        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': ticket_topic,
            'ticket_creator': ticket_creator,
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': [],
            'ticket_detail_predictions': [
                prediction,
            ]
        }

        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSerialNumber': serial_number,
            'links': [
                {
                    'interface': 'REX',
                    'linkState': 'STABLE',
                },
            ],
        }
        edge_status_by_serial = {
            serial_number: edge_status,
        }

        resolve_detail_response = {
            'body': 'ok',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.resolve_ticket_detail = CoroutineMock(return_value=resolve_detail_response)

        ticket_repository = Mock()
        ticket_repository.is_detail_in_outage_ticket = Mock(return_value=True)
        ticket_repository.was_ticket_created_by_automation_engine = Mock(return_value=True)

        prediction_repository = Mock()
        prediction_repository.is_prediction_confident_enough = Mock(return_value=True)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._edge_status_by_serial = edge_status_by_serial
        tnba_monitor._is_there_an_outage = Mock(return_value=False)

        with patch.object(config, 'ENVIRONMENT', "production"):
            was_detail_autoresolved = await tnba_monitor._autoresolve_ticket_detail(
                detail_object=detail_object,
                best_prediction=prediction,
            )

        ticket_repository.is_detail_in_outage_ticket.assert_called_once_with(detail_object)
        ticket_repository.was_ticket_created_by_automation_engine.assert_called_once_with(detail_object)
        prediction_repository.is_prediction_confident_enough.assert_called_once_with(prediction)
        tnba_monitor._is_there_an_outage.assert_called_once_with(edge_status)
        bruin_repository.resolve_ticket_detail.assert_awaited_once_with(ticket_id, ticket_detail_id)
        assert was_detail_autoresolved is True

    @pytest.mark.asyncio
    async def autoresolve_ticket_detail_with_ticket_being_an_affecting_ticket_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_creator = 'Intelygenz Ai'
        ticket_topic = 'Service Affecting Trouble'

        serial_number = 'VC1234567'

        prediction = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }

        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': ticket_topic,
            'ticket_creator': ticket_creator,
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': [],
            'ticket_detail_predictions': [
                prediction,
            ]
        }

        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSerialNumber': serial_number,
            'links': [
                {
                    'interface': 'REX',
                    'linkState': 'STABLE',
                },
            ],
        }
        edge_status_by_serial = {
            serial_number: edge_status,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.resolve_ticket_detail = CoroutineMock()

        ticket_repository = Mock()
        ticket_repository.is_detail_in_outage_ticket = Mock(return_value=False)
        ticket_repository.was_ticket_created_by_automation_engine = Mock()

        prediction_repository = Mock()
        prediction_repository.is_prediction_confident_enough = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._edge_status_by_serial = edge_status_by_serial
        tnba_monitor._is_there_an_outage = Mock()

        was_detail_autoresolved = await tnba_monitor._autoresolve_ticket_detail(
            detail_object=detail_object,
            best_prediction=prediction,
        )

        ticket_repository.is_detail_in_outage_ticket.assert_called_once_with(detail_object)
        ticket_repository.was_ticket_created_by_automation_engine.assert_not_called()
        prediction_repository.is_prediction_confident_enough.assert_not_called()
        tnba_monitor._is_there_an_outage.assert_not_called()
        bruin_repository.resolve_ticket_detail.assert_not_awaited()
        assert was_detail_autoresolved is False

    @pytest.mark.asyncio
    async def autoresolve_ticket_detail_with_ticket_not_automatically_created_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_creator = 'Otacon'
        ticket_topic = 'Service Outage Trouble'

        serial_number = 'VC1234567'

        prediction = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }

        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': ticket_topic,
            'ticket_creator': ticket_creator,
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': [],
            'ticket_detail_predictions': [
                prediction,
            ]
        }

        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSerialNumber': serial_number,
            'links': [
                {
                    'interface': 'REX',
                    'linkState': 'STABLE',
                },
            ],
        }
        edge_status_by_serial = {
            serial_number: edge_status,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.resolve_ticket_detail = CoroutineMock()

        ticket_repository = Mock()
        ticket_repository.is_detail_in_outage_ticket = Mock(return_value=True)
        ticket_repository.was_ticket_created_by_automation_engine = Mock(return_value=False)

        prediction_repository = Mock()
        prediction_repository.is_prediction_confident_enough = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._edge_status_by_serial = edge_status_by_serial
        tnba_monitor._is_there_an_outage = Mock()

        was_detail_autoresolved = await tnba_monitor._autoresolve_ticket_detail(
            detail_object=detail_object,
            best_prediction=prediction,
        )

        ticket_repository.is_detail_in_outage_ticket.assert_called_once_with(detail_object)
        ticket_repository.was_ticket_created_by_automation_engine.assert_called_once_with(detail_object)
        prediction_repository.is_prediction_confident_enough.assert_not_called()
        tnba_monitor._is_there_an_outage.assert_not_called()
        bruin_repository.resolve_ticket_detail.assert_not_awaited()
        assert was_detail_autoresolved is False

    @pytest.mark.asyncio
    async def autoresolve_ticket_detail_with_prediction_having_insufficient_confidence_level_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_creator = 'Intelygenz Ai'
        ticket_topic = 'Service Outage Trouble'

        serial_number = 'VC1234567'

        prediction = {
            'name': 'Repair Completed',
            'probability': 0.5484384655952454
        }

        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': ticket_topic,
            'ticket_creator': ticket_creator,
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': [],
            'ticket_detail_predictions': [
                prediction,
            ]
        }

        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSerialNumber': serial_number,
            'links': [
                {
                    'interface': 'REX',
                    'linkState': 'STABLE',
                },
            ],
        }
        edge_status_by_serial = {
            serial_number: edge_status,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.resolve_ticket_detail = CoroutineMock()

        ticket_repository = Mock()
        ticket_repository.is_detail_in_outage_ticket = Mock(return_value=True)
        ticket_repository.was_ticket_created_by_automation_engine = Mock(return_value=True)

        prediction_repository = Mock()
        prediction_repository.is_prediction_confident_enough = Mock(return_value=False)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._edge_status_by_serial = edge_status_by_serial
        tnba_monitor._is_there_an_outage = Mock()

        was_detail_autoresolved = await tnba_monitor._autoresolve_ticket_detail(
            detail_object=detail_object,
            best_prediction=prediction,
        )

        ticket_repository.is_detail_in_outage_ticket.assert_called_once_with(detail_object)
        ticket_repository.was_ticket_created_by_automation_engine.assert_called_once_with(detail_object)
        prediction_repository.is_prediction_confident_enough.assert_called_once_with(prediction)
        tnba_monitor._is_there_an_outage.assert_not_called()
        bruin_repository.resolve_ticket_detail.assert_not_awaited()
        assert was_detail_autoresolved is False

    @pytest.mark.asyncio
    async def autoresolve_ticket_detail_with_edge_in_outage_state_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_creator = 'Intelygenz Ai'
        ticket_topic = 'Service Outage Trouble'

        serial_number = 'VC1234567'

        prediction = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }

        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': ticket_topic,
            'ticket_creator': ticket_creator,
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': [],
            'ticket_detail_predictions': [
                prediction,
            ]
        }

        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeSerialNumber': serial_number,
            'links': [
                {
                    'interface': 'REX',
                    'linkState': 'STABLE',
                },
            ],
        }
        edge_status_by_serial = {
            serial_number: edge_status,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.resolve_ticket_detail = CoroutineMock()

        ticket_repository = Mock()
        ticket_repository.is_detail_in_outage_ticket = Mock(return_value=True)
        ticket_repository.was_ticket_created_by_automation_engine = Mock(return_value=True)

        prediction_repository = Mock()
        prediction_repository.is_prediction_confident_enough = Mock(return_value=True)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._edge_status_by_serial = edge_status_by_serial
        tnba_monitor._is_there_an_outage = Mock(return_value=True)

        was_detail_autoresolved = await tnba_monitor._autoresolve_ticket_detail(
            detail_object=detail_object,
            best_prediction=prediction,
        )

        ticket_repository.is_detail_in_outage_ticket.assert_called_once_with(detail_object)
        ticket_repository.was_ticket_created_by_automation_engine.assert_called_once_with(detail_object)
        prediction_repository.is_prediction_confident_enough.assert_called_once_with(prediction)
        tnba_monitor._is_there_an_outage.assert_called_once_with(edge_status)
        bruin_repository.resolve_ticket_detail.assert_not_awaited()
        assert was_detail_autoresolved is False

    @pytest.mark.asyncio
    async def autoresolve_ticket_detail_with_non_production_environment_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_creator = 'Intelygenz Ai'
        ticket_topic = 'Service Outage Trouble'

        serial_number = 'VC1234567'

        prediction = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }

        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': ticket_topic,
            'ticket_creator': ticket_creator,
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': [],
            'ticket_detail_predictions': [
                prediction,
            ]
        }

        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeSerialNumber': serial_number,
            'links': [
                {
                    'interface': 'REX',
                    'linkState': 'STABLE',
                },
            ],
        }
        edge_status_by_serial = {
            serial_number: edge_status,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.resolve_ticket_detail = CoroutineMock()

        ticket_repository = Mock()
        ticket_repository.is_detail_in_outage_ticket = Mock(return_value=True)
        ticket_repository.was_ticket_created_by_automation_engine = Mock(return_value=True)

        prediction_repository = Mock()
        prediction_repository.is_prediction_confident_enough = Mock(return_value=True)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._edge_status_by_serial = edge_status_by_serial
        tnba_monitor._is_there_an_outage = Mock(return_value=False)

        with patch.object(config, 'ENVIRONMENT', "dev"):
            was_detail_autoresolved = await tnba_monitor._autoresolve_ticket_detail(
                detail_object=detail_object,
                best_prediction=prediction,
            )

        ticket_repository.is_detail_in_outage_ticket.assert_called_once_with(detail_object)
        ticket_repository.was_ticket_created_by_automation_engine.assert_called_once_with(detail_object)
        prediction_repository.is_prediction_confident_enough.assert_called_once_with(prediction)
        tnba_monitor._is_there_an_outage.assert_called_once_with(edge_status)
        bruin_repository.resolve_ticket_detail.assert_not_awaited()
        assert was_detail_autoresolved is False

    @pytest.mark.asyncio
    async def autoresolve_ticket_detail_with_failure_in_autoresolve_request_test(self):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_creator = 'Intelygenz Ai'
        ticket_topic = 'Service Outage Trouble'

        serial_number = 'VC1234567'

        prediction = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }

        detail_object = {
            'ticket_id': ticket_id,
            'ticket_creation_date': "1/03/2021 10:08:13 AM",
            'ticket_topic': ticket_topic,
            'ticket_creator': ticket_creator,
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': serial_number,
            },
            'ticket_notes': [],
            'ticket_detail_predictions': [
                prediction,
            ]
        }

        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeSerialNumber': serial_number,
            'links': [
                {
                    'interface': 'REX',
                    'linkState': 'STABLE',
                },
            ],
        }
        edge_status_by_serial = {
            serial_number: edge_status,
        }

        resolve_detail_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        notifications_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.resolve_ticket_detail = CoroutineMock(return_value=resolve_detail_response)

        ticket_repository = Mock()
        ticket_repository.is_detail_in_outage_ticket = Mock(return_value=True)
        ticket_repository.was_ticket_created_by_automation_engine = Mock(return_value=True)

        prediction_repository = Mock()
        prediction_repository.is_prediction_confident_enough = Mock(return_value=True)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._edge_status_by_serial = edge_status_by_serial
        tnba_monitor._is_there_an_outage = Mock(return_value=False)

        with patch.object(config, 'ENVIRONMENT', "production"):
            was_detail_autoresolved = await tnba_monitor._autoresolve_ticket_detail(
                detail_object=detail_object,
                best_prediction=prediction,
            )

        ticket_repository.is_detail_in_outage_ticket.assert_called_once_with(detail_object)
        ticket_repository.was_ticket_created_by_automation_engine.assert_called_once_with(detail_object)
        prediction_repository.is_prediction_confident_enough.assert_called_once_with(prediction)
        tnba_monitor._is_there_an_outage.assert_called_once_with(edge_status)
        bruin_repository.resolve_ticket_detail.assert_awaited_once_with(ticket_id, ticket_detail_id)
        assert was_detail_autoresolved is False

    @pytest.mark.asyncio
    async def append_tnba_notes_test(self):
        ticket_1_id = 12345
        ticket_2_id = 67890

        ticket_detail_1_id = 12345
        ticket_detail_2_id = 67890
        ticket_detail_3_id = 87654

        service_number_1 = 'VC1234567'
        service_number_2 = 'VC8901234'
        service_number_3 = 'VC5678901'

        tnba_note_1 = 'This is a TNBA note (1)'
        tnba_note_2 = 'This is a TNBA note (2)'
        tnba_note_3 = 'This is a TNBA note (3)'

        ticket_1_notes_payload = [
            {
                'text': tnba_note_1,
                'detail_id': ticket_detail_1_id,
                'service_number': service_number_1,
            },
            {
                'text': tnba_note_2,
                'detail_id': ticket_detail_2_id,
                'service_number': service_number_2,
            },
        ]
        ticket_2_notes_payload = [
            {
                'text': tnba_note_3,
                'detail_id': ticket_detail_3_id,
                'service_number': service_number_3,
            },
        ]

        append_notes_response = {
            'body': 'ok',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        prediction_repository = Mock()
        ticket_repository = Mock()
        utils_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock(return_value=append_notes_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)
        tnba_monitor._tnba_notes_to_append = [
            {
                'ticket_id': ticket_1_id,
                'text': tnba_note_1,
                'detail_id': ticket_detail_1_id,
                'service_number': service_number_1,
            },
            {
                'ticket_id': ticket_1_id,
                'text': tnba_note_2,
                'detail_id': ticket_detail_2_id,
                'service_number': service_number_2,
            },
            {
                'ticket_id': ticket_2_id,
                'text': tnba_note_3,
                'detail_id': ticket_detail_3_id,
                'service_number': service_number_3,
            },
        ]

        await tnba_monitor._append_tnba_notes()

        bruin_repository.append_multiple_notes_to_ticket.assert_has_awaits([
            call(ticket_1_id, ticket_1_notes_payload),
            call(ticket_2_id, ticket_2_notes_payload),
        ])
        assert notifications_repository.send_slack_message.await_count == 2

    def is_there_an_outage_test(self):
        edge_1_state = 'CONNECTED'
        edge_1_link_ge1_state = edge_1_link_ge2_state = 'STABLE'
        edge_status_1 = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': edge_1_state,
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'links': [
                {
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': edge_1_link_ge1_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'interface': 'RAY',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': edge_1_link_ge2_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        edge_2_state = 'OFFLINE'
        edge_2_link_ge1_state = edge_2_link_ge2_state = 'DISCONNECTED'
        edge_status_2 = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': edge_2_state,
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'links': [
                {
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': edge_2_link_ge1_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'interface': 'RAY',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': edge_2_link_ge2_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        edge_3_state = 'OFFLINE'
        edge_3_link_ge1_state = 'STABLE'
        edge_3_link_ge2_state = 'DISCONNECTED'
        edge_status_3 = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': edge_3_state,
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'links': [
                {
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': edge_3_link_ge1_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'interface': 'RAY',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': edge_3_link_ge2_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()
        velocloud_repository = Mock()
        t7_repository = Mock()
        prediction_repository = Mock()
        ticket_repository = Mock()
        utils_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   customer_cache_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository, utils_repository)

        result = tnba_monitor._is_there_an_outage(edge_status_1)
        assert result is False

        result = tnba_monitor._is_there_an_outage(edge_status_2)
        assert result is True

        result = tnba_monitor._is_there_an_outage(edge_status_3)
        assert result is True

    def is_faulty_edge_test(self):
        edge_state_1 = 'CONNECTED'
        edge_state_2 = 'OFFLINE'

        result = TNBAMonitor._is_faulty_edge(edge_state_1)
        assert result is False

        result = TNBAMonitor._is_faulty_edge(edge_state_2)
        assert result is True

    def is_faulty_link_test(self):
        link_state_1 = 'STABLE'
        link_state_2 = 'DISCONNECTED'

        result = TNBAMonitor._is_faulty_link(link_state_1)
        assert result is False

        result = TNBAMonitor._is_faulty_link(link_state_2)
        assert result is True
