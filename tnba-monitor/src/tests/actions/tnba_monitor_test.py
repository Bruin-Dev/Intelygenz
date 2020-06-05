from datetime import datetime
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest

from apscheduler.util import undefined
from asynctest import CoroutineMock
from shortuuid import uuid

from application.actions.tnba_monitor import TNBAMonitor
from application.actions import tnba_monitor as tnba_monitor_module
from config import testconfig


class TestTNBAMonitor:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        monitoring_map_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        assert tnba_monitor._event_bus is event_bus
        assert tnba_monitor._logger is logger
        assert tnba_monitor._scheduler is scheduler
        assert tnba_monitor._config is config
        assert tnba_monitor._t7_repository is t7_repository
        assert tnba_monitor._ticket_repository is ticket_repository
        assert tnba_monitor._monitoring_map_repository is monitoring_map_repository
        assert tnba_monitor._bruin_repository is bruin_repository
        assert tnba_monitor._velocloud_repository is velocloud_repository
        assert tnba_monitor._prediction_repository is prediction_repository
        assert tnba_monitor._notifications_repository is notifications_repository

        assert tnba_monitor._monitoring_mapping == {}

    @pytest.mark.asyncio
    async def start_tnba_automated_process_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        monitoring_map_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

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
        monitoring_map_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        await tnba_monitor.start_tnba_automated_process(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            tnba_monitor._run_tickets_polling, 'interval',
            seconds=config.MONITORING_INTERVAL_SECONDS,
            next_run_time=undefined,
            replace_existing=False,
            id='_run_tickets_polling',
        )

    @pytest.mark.asyncio
    async def run_tickets_polling_with_filled_cache_test(self):
        bruin_client_1 = 12345
        bruin_client_2 = 67890

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_1_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_1}|',
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_2}|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_2}|',
        }

        edge_1_data = {'edge_id': edge_1_full_id, 'edge_status': edge_1_status}
        edge_2_data = {'edge_id': edge_2_full_id, 'edge_status': edge_2_status}
        edge_3_data = {'edge_id': edge_3_full_id, 'edge_status': edge_3_status}

        monitoring_mapping = {
            bruin_client_1: {
                edge_1_serial: edge_1_data,
            },
            bruin_client_2: {
                edge_2_serial: edge_2_data,
                edge_3_serial: edge_3_data,
            }
        }

        ticket_1_for_bruin_client_1_id = 12345
        ticket_1_for_bruin_client_1_details = [
            {
                "detailID": 2746937,
                "detailValue": 'VC1234567890',
            },
        ]
        ticket_1_note_1_for_bruin_client_1 = {
            "noteId": 41894040,
            "noteValue": None,
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_1_note_2_for_bruin_client_1 = {
            "noteId": 41894041,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_1_note_3_for_bruin_client_1 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_with_details_1_for_bruin_client_1 = {
            'ticket_id': ticket_1_for_bruin_client_1_id,
            'ticket_details': ticket_1_for_bruin_client_1_details,
            'ticket_notes': [
                ticket_1_note_1_for_bruin_client_1,
                ticket_1_note_2_for_bruin_client_1,
                ticket_1_note_3_for_bruin_client_1,
            ],
        }

        ticket_2_for_bruin_client_1_id = 11223
        ticket_2_for_bruin_client_1_details = [
            {
                "detailID": 2746938,
                "detailValue": 'VC1234567890',
            },
        ]
        ticket_2_note_1_for_bruin_client_1 = {
            "noteId": 41894042,
            "noteValue": 'There were some troubles with this service number',
            "createdDate": "2020-02-24T10:08:13.503-05:00",
        }
        ticket_with_details_2_for_bruin_client_1 = {
            'ticket_id': ticket_2_for_bruin_client_1_id,
            'ticket_details': ticket_2_for_bruin_client_1_details,
            'ticket_notes': [
                ticket_2_note_1_for_bruin_client_1,
            ],
        }

        ticket_1_for_bruin_client_2_id = 67890
        ticket_1_for_bruin_client_2_details = [
            {
                "detailID": 2746937,
                "detailValue": 'VC0987654321',
            },
        ]
        ticket_1_note_1_for_bruin_client_2 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": "2020-02-24T10:08:13.503-05:00",
        }
        ticket_with_details_1_for_bruin_client_2 = {
            'ticket_id': ticket_1_for_bruin_client_2_id,
            'ticket_details': ticket_1_for_bruin_client_2_details,
            'ticket_notes': [
                ticket_1_note_1_for_bruin_client_2,
            ],
        }

        ticket_with_details_1_for_bruin_client_1_notes_filtered = {
            'ticket_id': ticket_1_for_bruin_client_1_id,
            'ticket_details': ticket_1_for_bruin_client_1_details,
            'ticket_notes': [
                ticket_1_note_2_for_bruin_client_1,
            ]
        }
        ticket_with_details_2_for_bruin_client_1_notes_filtered = {
            'ticket_id': ticket_2_for_bruin_client_1_id,
            'ticket_details': ticket_2_for_bruin_client_1_details,
            'ticket_notes': [
                ticket_2_note_1_for_bruin_client_1,
            ]
        }
        ticket_with_details_1_for_bruin_client_2_notes_filtered = {
            'ticket_id': ticket_1_for_bruin_client_2_id,
            'ticket_details': ticket_1_for_bruin_client_2_details,
            'ticket_notes': []
        }

        open_tickets_with_details = [
            ticket_with_details_1_for_bruin_client_1,
            ticket_with_details_2_for_bruin_client_1,
            ticket_with_details_1_for_bruin_client_2,
        ]
        relevant_open_tickets = [
            ticket_with_details_1_for_bruin_client_1,
            ticket_with_details_1_for_bruin_client_2,
        ]
        relevant_open_tickets_with_notes_filtered = [
            ticket_with_details_1_for_bruin_client_1_notes_filtered,
            ticket_with_details_2_for_bruin_client_1_notes_filtered,
            ticket_with_details_1_for_bruin_client_2_notes_filtered,
        ]

        tickets_with_tnba = [
            ticket_with_details_1_for_bruin_client_1_notes_filtered,
        ]
        tickets_without_tnba = [
            ticket_with_details_2_for_bruin_client_1_notes_filtered,
            ticket_with_details_1_for_bruin_client_2_notes_filtered,
        ]

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

        monitoring_map_repository = Mock()
        monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses = CoroutineMock()
        monitoring_map_repository.get_monitoring_map_cache = Mock(return_value=monitoring_mapping)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)
        tnba_monitor._monitoring_mapping = {'obsolete': 'data'}
        tnba_monitor._get_all_open_tickets_with_details_for_monitored_companies = CoroutineMock(
            return_value=open_tickets_with_details)
        tnba_monitor._filter_tickets_and_details_related_to_edges_under_monitoring = Mock(
            return_value=relevant_open_tickets)
        tnba_monitor._filter_invalid_notes_in_tickets = Mock(return_value=relevant_open_tickets_with_notes_filtered)
        tnba_monitor._distinguish_tickets_with_and_without_tnba = Mock(
            return_value=(tickets_with_tnba, tickets_without_tnba)
        )
        tnba_monitor._process_tickets_with_tnba = CoroutineMock()
        tnba_monitor._process_tickets_without_tnba = CoroutineMock()

        await tnba_monitor._run_tickets_polling()

        monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses.assert_not_awaited()
        tnba_monitor._process_tickets_with_tnba.assert_awaited_once_with(tickets_with_tnba)
        tnba_monitor._process_tickets_without_tnba.assert_awaited_once_with(tickets_without_tnba)

    @pytest.mark.asyncio
    async def run_tickets_polling_with_empty_cache_test(self):
        bruin_client_1 = 12345
        bruin_client_2 = 67890

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_1_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_1}|',
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_2}|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_2}|',
        }

        edge_1_data = {'edge_id': edge_1_full_id, 'edge_status': edge_1_status}
        edge_2_data = {'edge_id': edge_2_full_id, 'edge_status': edge_2_status}
        edge_3_data = {'edge_id': edge_3_full_id, 'edge_status': edge_3_status}

        monitoring_mapping = {
            bruin_client_1: {
                edge_1_serial: edge_1_data,
            },
            bruin_client_2: {
                edge_2_serial: edge_2_data,
                edge_3_serial: edge_3_data,
            }
        }

        ticket_1_for_bruin_client_1_id = 12345
        ticket_1_for_bruin_client_1_details = [
            {
                "detailID": 2746937,
                "detailValue": 'VC1234567890',
            },
        ]
        ticket_1_note_1_for_bruin_client_1 = {
            "noteId": 41894040,
            "noteValue": None,
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_1_note_2_for_bruin_client_1 = {
            "noteId": 41894041,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_1_note_3_for_bruin_client_1 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_with_details_1_for_bruin_client_1 = {
            'ticket_id': ticket_1_for_bruin_client_1_id,
            'ticket_details': ticket_1_for_bruin_client_1_details,
            'ticket_notes': [
                ticket_1_note_1_for_bruin_client_1,
                ticket_1_note_2_for_bruin_client_1,
                ticket_1_note_3_for_bruin_client_1,
            ],
        }

        ticket_2_for_bruin_client_1_id = 11223
        ticket_2_for_bruin_client_1_details = [
            {
                "detailID": 2746938,
                "detailValue": 'VC1234567890',
            },
        ]
        ticket_2_note_1_for_bruin_client_1 = {
            "noteId": 41894042,
            "noteValue": 'There were some troubles with this service number',
            "createdDate": "2020-02-24T10:08:13.503-05:00",
        }
        ticket_with_details_2_for_bruin_client_1 = {
            'ticket_id': ticket_2_for_bruin_client_1_id,
            'ticket_details': ticket_2_for_bruin_client_1_details,
            'ticket_notes': [
                ticket_2_note_1_for_bruin_client_1,
            ],
        }

        ticket_1_for_bruin_client_2_id = 67890
        ticket_1_for_bruin_client_2_details = [
            {
                "detailID": 2746937,
                "detailValue": 'VC0987654321',
            },
        ]
        ticket_1_note_1_for_bruin_client_2 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": "2020-02-24T10:08:13.503-05:00",
        }
        ticket_with_details_1_for_bruin_client_2 = {
            'ticket_id': ticket_1_for_bruin_client_2_id,
            'ticket_details': ticket_1_for_bruin_client_2_details,
            'ticket_notes': [
                ticket_1_note_1_for_bruin_client_2,
            ],
        }

        ticket_with_details_1_for_bruin_client_1_notes_filtered = {
            'ticket_id': ticket_1_for_bruin_client_1_id,
            'ticket_details': ticket_1_for_bruin_client_1_details,
            'ticket_notes': [
                ticket_1_note_2_for_bruin_client_1,
            ]
        }
        ticket_with_details_2_for_bruin_client_1_notes_filtered = {
            'ticket_id': ticket_2_for_bruin_client_1_id,
            'ticket_details': ticket_2_for_bruin_client_1_details,
            'ticket_notes': [
                ticket_2_note_1_for_bruin_client_1,
            ]
        }
        ticket_with_details_1_for_bruin_client_2_notes_filtered = {
            'ticket_id': ticket_1_for_bruin_client_2_id,
            'ticket_details': ticket_1_for_bruin_client_2_details,
            'ticket_notes': []
        }

        open_tickets_with_details = [
            ticket_with_details_1_for_bruin_client_1,
            ticket_with_details_2_for_bruin_client_1,
            ticket_with_details_1_for_bruin_client_2,
        ]
        relevant_open_tickets = [
            ticket_with_details_1_for_bruin_client_1,
            ticket_with_details_1_for_bruin_client_2,
        ]
        relevant_open_tickets_with_notes_filtered = [
            ticket_with_details_1_for_bruin_client_1_notes_filtered,
            ticket_with_details_2_for_bruin_client_1_notes_filtered,
            ticket_with_details_1_for_bruin_client_2_notes_filtered,
        ]

        tickets_with_tnba = [
            ticket_with_details_1_for_bruin_client_1_notes_filtered,
        ]
        tickets_without_tnba = [
            ticket_with_details_2_for_bruin_client_1_notes_filtered,
            ticket_with_details_1_for_bruin_client_2_notes_filtered,
        ]

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

        monitoring_map_repository = Mock()
        monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses = CoroutineMock()
        monitoring_map_repository.start_create_monitoring_map_job = CoroutineMock()
        monitoring_map_repository.get_monitoring_map_cache = Mock(return_value=monitoring_mapping)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)
        tnba_monitor._get_all_open_tickets_with_details_for_monitored_companies = CoroutineMock(
            return_value=open_tickets_with_details)
        tnba_monitor._filter_tickets_and_details_related_to_edges_under_monitoring = Mock(
            return_value=relevant_open_tickets)
        tnba_monitor._filter_invalid_notes_in_tickets = Mock(return_value=relevant_open_tickets_with_notes_filtered)
        tnba_monitor._distinguish_tickets_with_and_without_tnba = Mock(
            return_value=(tickets_with_tnba, tickets_without_tnba)
        )
        tnba_monitor._process_tickets_with_tnba = CoroutineMock()
        tnba_monitor._process_tickets_without_tnba = CoroutineMock()

        await tnba_monitor._run_tickets_polling()

        monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses.assert_awaited_once()
        monitoring_map_repository.start_create_monitoring_map_job.assert_awaited_once()
        tnba_monitor._process_tickets_with_tnba.assert_awaited_once_with(tickets_with_tnba)
        tnba_monitor._process_tickets_without_tnba.assert_awaited_once_with(tickets_without_tnba)

    @pytest.mark.asyncio
    async def start_tnba_automated_process_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        monitoring_map_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

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
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
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
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
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

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_1_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_1_id}|',
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_2_id}|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_2_id}|',
        }

        edge_1_data = {'edge_id': edge_1_full_id, 'edge_status': edge_1_status}
        edge_2_data = {'edge_id': edge_2_full_id, 'edge_status': edge_2_status}
        edge_3_data = {'edge_id': edge_3_full_id, 'edge_status': edge_3_status}

        monitoring_mapping = {
            bruin_client_1_id: {
                edge_1_serial: edge_1_data,
            },
            bruin_client_2_id: {
                edge_2_serial: edge_2_data,
                edge_3_serial: edge_3_data,
            }
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)
        tnba_monitor._monitoring_mapping = monitoring_mapping
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
                        "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
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
                        "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
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

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_1_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_1_id}|',
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_2_id}|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_3_id}|',
        }

        edge_1_data = {'edge_id': edge_1_full_id, 'edge_status': edge_1_status}
        edge_2_data = {'edge_id': edge_2_full_id, 'edge_status': edge_2_status}
        edge_3_data = {'edge_id': edge_3_full_id, 'edge_status': edge_3_status}

        monitoring_mapping = {
            bruin_client_1_id: {
                edge_1_serial: edge_1_data,
            },
            bruin_client_2_id: {
                edge_2_serial: edge_2_data,
            },
            bruin_client_3_id: {
                edge_3_serial: edge_3_data,
            }
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)
        tnba_monitor._monitoring_mapping = monitoring_mapping
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

        ticket_1_id = 11111
        ticket_2_id = 22222
        ticket_3_id = 33333
        outage_ticket_ids = [{'ticketID': ticket_1_id}, {'ticketID': ticket_2_id}]
        affecting_ticket_ids = [{'ticketID': ticket_3_id}]

        outage_ticket_1_details_item_1 = {
            "detailID": 2746937,
            "detailValue": 'VC1234567890',
        }
        outage_ticket_1_details_items = [outage_ticket_1_details_item_1]
        outage_ticket_1_notes = [
            {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
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
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894044,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
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
            'body': outage_ticket_ids,
            'status': 200,
        }
        get_open_affecting_tickets_response = {
            'request_id': uuid_,
            'body': affecting_ticket_ids,
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
        ticket_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
            get_ticket_3_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id)
        ])

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_details': outage_ticket_1_details_items,
                'ticket_notes': outage_ticket_1_notes,
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_details': outage_ticket_2_details_items,
                'ticket_notes': outage_ticket_2_notes,
            },
            {
                'ticket_id': ticket_3_id,
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
        ticket_1_id = 11111
        ticket_2_id = 22222
        get_open_outage_tickets_response = {
            'request_id': uuid_,
            'body': 'Got internal error from Bruin',
            'status': 500,
        }
        get_open_affecting_tickets_response = {
            'request_id': uuid_,
            'body': [{'ticketID': ticket_1_id}, {'ticketID': ticket_2_id}],
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
        ticket_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

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
                'ticket_details': affecting_ticket_1_details_items,
                'ticket_notes': affecting_ticket_1_notes,
            },
            {
                'ticket_id': ticket_2_id,
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
        ticket_1_id = 11111
        ticket_2_id = 22222
        get_open_outage_tickets_response = {
            'request_id': uuid_,
            'body': [{'ticketID': ticket_1_id}, {'ticketID': ticket_2_id}],
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
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
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
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894044,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
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
        ticket_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

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
                'ticket_details': outage_ticket_1_details_items,
                'ticket_notes': outage_ticket_1_notes,
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_details': outage_ticket_2_details_items,
                'ticket_notes': outage_ticket_2_notes,
            },
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_with_ticket_details_request_not_having_2xx_status_test(self):
        uuid_ = uuid()
        bruin_client_id = 12345

        ticket_1_id = 11111
        ticket_2_id = 22222
        ticket_3_id = 33333
        outage_ticket_ids = [{'ticketID': ticket_1_id}, {'ticketID': ticket_2_id}]
        affecting_ticket_ids = [{'ticketID': ticket_3_id}]

        outage_ticket_1_details_item_1 = {
            "detailID": 2746937,
            "detailValue": 'VC1234567890',
        }
        outage_ticket_1_details_items = [outage_ticket_1_details_item_1]
        outage_ticket_1_notes = [
            {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
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
            'body': outage_ticket_ids,
            'status': 200,
        }
        get_open_affecting_tickets_response = {
            'request_id': uuid_,
            'body': affecting_ticket_ids,
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
        ticket_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
            get_ticket_3_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id)
        ])

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_details': outage_ticket_1_details_items,
                'ticket_notes': outage_ticket_1_notes,
            },
            {
                'ticket_id': ticket_3_id,
                'ticket_details': affecting_ticket_1_details_items,
                'ticket_notes': affecting_ticket_1_notes,
            }
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_with_ticket_details_not_having_details_actually_test(self):
        uuid_ = uuid()
        bruin_client_id = 12345

        ticket_1_id = 11111
        ticket_2_id = 22222
        ticket_3_id = 33333
        outage_ticket_ids = [{'ticketID': ticket_1_id}, {'ticketID': ticket_2_id}]
        affecting_ticket_ids = [{'ticketID': ticket_3_id}]

        outage_ticket_1_details_item_1 = {
            "detailID": 2746937,
            "detailValue": 'VC1234567890',
        }
        outage_ticket_1_details_items = [outage_ticket_1_details_item_1]
        outage_ticket_1_notes = [
            {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
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
            'body': outage_ticket_ids,
            'status': 200,
        }
        get_open_affecting_tickets_response = {
            'request_id': uuid_,
            'body': affecting_ticket_ids,
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
        ticket_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
            get_ticket_3_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id)
        ])

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_details': outage_ticket_1_details_items,
                'ticket_notes': outage_ticket_1_notes,
            },
            {
                'ticket_id': ticket_3_id,
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

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_1_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_1_id}|',
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_1_id}|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_1_id}|',
        }
        edge_4_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_4_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_2_id}|',
        }
        edge_5_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_5_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_2_id}|',
        }

        edge_1_data = {'edge_id': edge_1_full_id, 'edge_status': edge_1_status}
        edge_2_data = {'edge_id': edge_2_full_id, 'edge_status': edge_2_status}
        edge_3_data = {'edge_id': edge_3_full_id, 'edge_status': edge_3_status}
        edge_4_data = {'edge_id': edge_4_full_id, 'edge_status': edge_4_status}
        edge_5_data = {'edge_id': edge_5_full_id, 'edge_status': edge_5_status}

        monitoring_mapping = {
            bruin_client_1_id: {
                edge_1_serial: edge_1_data,
                edge_2_serial: edge_2_data,
                edge_3_serial: edge_3_data,
            },
            bruin_client_2_id: {
                edge_4_serial: edge_4_data,
                edge_5_serial: edge_5_data,
            }
        }

        ticket_1_id = 12345
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
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        ]
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                ticket_1_detail_1,
                ticket_1_detail_2,
            ],
            'ticket_notes': ticket_1_notes,
        }

        ticket_2_id = 67890
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
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        ]
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                ticket_2_detail_1,
                ticket_2_detail_2,
                ticket_2_detail_3,
            ],
            'ticket_notes': ticket_2_notes,
        }

        ticket_3_id = 22222
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
            'ticket_details': [
                ticket_3_detail_1,
            ],
            'ticket_notes': ticket_3_notes,
        }

        ticket_4_id = 11111
        ticket_4_detail_1 = {
            "detailID": 2746935,
            "detailValue": edge_5_serial,
        }
        ticket_4_notes = [
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        ]
        ticket_4 = {
            'ticket_id': ticket_4_id,
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
        ticket_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)
        tnba_monitor._monitoring_mapping = monitoring_mapping

        result = tnba_monitor._filter_tickets_and_details_related_to_edges_under_monitoring(tickets)

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_details': [
                    ticket_1_detail_1,
                ],
                'ticket_notes': ticket_1_notes,
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_details': [
                    ticket_2_detail_1,
                    ticket_2_detail_3,
                ],
                'ticket_notes': ticket_2_notes,
            },
            {
                'ticket_id': ticket_4_id,
                'ticket_details': [
                    ticket_4_detail_1,
                ],
                'ticket_notes': ticket_4_notes,
            },
        ]
        assert result == expected

    def filter_invalid_notes_in_tickets_test(self):
        ticket_1_id = 12345
        ticket_1_details = [
            {
                "detailID": 2746937,
                "detailValue": 'VC1234567890',
            },
        ]
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": None,
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_1_note_2 = {
            "noteId": 41894041,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_1_note_3 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': ticket_1_details,
            'ticket_notes': [
                ticket_1_note_1,
                ticket_1_note_2,
                ticket_1_note_3,
            ],
        }

        ticket_2_id = 11223
        ticket_2_details = [
            {
                "detailID": 2746938,
                "detailValue": 'VC1234567890',
            },
        ]
        ticket_2_note_1 = {
            "noteId": 41894042,
            "noteValue": 'There were some troubles with this service number',
            "createdDate": "2020-02-24T10:08:13.503-05:00",
        }
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': ticket_2_details,
            'ticket_notes': [
                ticket_2_note_1,
            ],
        }

        ticket_3_id = 67890
        ticket_3_details = [
            {
                "detailID": 2746937,
                "detailValue": 'VC0987654321',
            },
        ]
        ticket_3_note_1 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": "2020-02-24T10:08:13.503-05:00",
        }
        ticket_3 = {
            'ticket_id': ticket_3_id,
            'ticket_details': ticket_3_details,
            'ticket_notes': [
                ticket_3_note_1,
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
        ticket_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        result = tnba_monitor._filter_invalid_notes_in_tickets(tickets)

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_details': ticket_1_details,
                'ticket_notes': [
                    ticket_1_note_2,
                ],
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_details': ticket_2_details,
                'ticket_notes': [
                    ticket_2_note_1,
                ],
            },
            {
                'ticket_id': ticket_3_id,
                'ticket_details': ticket_3_details,
                'ticket_notes': [],
            },
        ]
        assert result == expected

    def distinguish_tickets_with_and_without_tnba_test(self):
        ticket_1 = {
            'ticket_id': 12345,
            'ticket_details': [
                {
                    "detailID": 2746930,
                    "detailValue": 'VC1234567',
                }
            ],
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ]
        }
        ticket_2 = {
            'ticket_id': 67890,
            'ticket_details': [
                {
                    "detailID": 2746931,
                    "detailValue": 'VC7654321',
                }
            ],
            'ticket_notes': [
                {
                    "noteId": 41894041,
                    "noteValue": 'This not is not a triage',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ]
        }
        ticket_3 = {
            'ticket_id': 11111,
            'ticket_details': [
                {
                    "detailID": 2746932,
                    "detailValue": 'VC1112223',
                }
            ],
            'ticket_notes': [
                {
                    "noteId": 41894042,
                    "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ]
        }
        ticket_4 = {
            'ticket_id': 11111,
            'ticket_details': [
                {
                    "detailID": 2746932,
                    "detailValue": 'VC1112223',
                }
            ],
            'ticket_notes': [
                {
                    "noteId": 41894042,
                    "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ]
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
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()
        bruin_repository = Mock()
        t7_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.has_tnba_note = Mock(side_effect=[
            True,
            False,
            True,
            False,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        tickets_with_tnba, tickets_without_tnba = tnba_monitor._distinguish_tickets_with_and_without_tnba(tickets)

        assert tickets_with_tnba == [ticket_1, ticket_3]
        assert tickets_without_tnba == [ticket_2, ticket_4]

    @pytest.mark.asyncio
    async def process_tickets_without_tnba_with_empty_list_of_tickets_test(self):
        tickets = []

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.build_tnba_note_from_prediction = Mock()

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock()
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        await tnba_monitor._process_tickets_without_tnba(tickets)

        t7_repository.get_prediction.assert_not_awaited()
        bruin_repository.get_next_results_for_ticket_detail.assert_not_awaited()
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_without_tnba_with_retrievals_of_predictions_returning_non_2xx_status_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": (
                        f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00'
                    ),
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ],
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': [],
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        t7_prediction_response = {
            'body': 'Got internal error from T7',
            'status': 500
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        prediction_repository = Mock()
        notifications_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.build_tnba_note_from_prediction = Mock()

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock()
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(return_value=t7_prediction_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        await tnba_monitor._process_tickets_without_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        bruin_repository.get_next_results_for_ticket_detail.assert_not_awaited()
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_without_tnba_with_no_predictions_found_for_target_serials_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": (
                        f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00'
                    ),
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ],
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': [],
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        t7_prediction_response_for_ticket_1 = {
            'body': [
                {
                    'assetId': 'VC9876543',
                    'predictions': [
                        {
                            'name': 'Repair Completed',
                            'probability': 0.9484384655952454
                        },
                        {
                            'name': 'Holmdel NOC Investigate',
                            'probability': 0.1234567890123456
                        },
                    ]
                },
            ],
            'status': 200
        }
        t7_prediction_response_for_ticket_2 = {
            'body': [
                {
                    'assetId': 'VC8888888',
                    'predictions': [
                        {
                            'name': 'Repair Completed',
                            'probability': 0.9484384655952454
                        },
                        {
                            'name': 'Holmdel NOC Investigate',
                            'probability': 0.1234567890123456
                        },
                    ]
                },
            ],
            'status': 200
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        notifications_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.build_tnba_note_from_prediction = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(return_value=None)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock()
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_response_for_ticket_1,
            t7_prediction_response_for_ticket_2,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        await tnba_monitor._process_tickets_without_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        bruin_repository.get_next_results_for_ticket_detail.assert_not_awaited()
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_without_tnba_with_predictions_found_for_target_serials_and_predictions_having_error_test(
            self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": (
                        f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00'
                    ),
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ],
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': [],
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        prediction_for_ticket_1_detail_1 = {
            'assetId': ticket_1_detail_1_serial_number,
            'error': {
                'code': 'error_in_prediction',
                'message': 'Error executing prediction: The labels [\'Refer to ASR Carrier\'] are not in the '
                           'Task Result" labels map.'
            },
        }
        prediction_for_ticket_1_detail_2 = {
            'assetId': ticket_1_detail_2_serial_number,
            'error': {
                'code': 'error_in_prediction',
                'message': "Error executing prediction: The labels "
                           "['Service Repaired', 'Investigating Wireless Device Issue'] are not "
                           "in the \"Task Result\" labels map."
            },
        }
        t7_prediction_response_for_ticket_1 = {
            'body': [
                prediction_for_ticket_1_detail_1,
                prediction_for_ticket_1_detail_2,
            ],
            'status': 200
        }

        prediction_for_ticket_2_detail_1 = {
            'assetId': ticket_2_detail_1_serial_number,
            'error': {
                'code': 'error_in_prediction',
                'message': "Error executing prediction: The labels "
                           "['Line Test Results Provided'] are not in the \"Task Result\" labels map."
            },
        }
        t7_prediction_response_for_ticket_2 = {
            'body': [
                prediction_for_ticket_2_detail_1,
            ],
            'status': 200
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.build_tnba_note_from_prediction = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(side_effect=[
            prediction_for_ticket_1_detail_1,
            prediction_for_ticket_1_detail_2,
            prediction_for_ticket_2_detail_1,
        ])

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock()
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_response_for_ticket_1,
            t7_prediction_response_for_ticket_2,
        ])

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        await tnba_monitor._process_tickets_without_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        assert notifications_repository.send_slack_message.await_count == 3
        bruin_repository.get_next_results_for_ticket_detail.assert_not_awaited()
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_without_tnba_with_retrieval_of_next_results_returning_non_2xx_status_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": (
                        f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00'
                    ),
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ],
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': [],
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        t7_prediction_response_for_ticket_1_detail_1_predictions_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        t7_prediction_response_for_ticket_1_detail_1_predictions_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        t7_prediction_response_for_ticket_1_detail_1_predictions = [
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_1,
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_2,
        ]
        t7_prediction_response_for_ticket_1_detail_1_prediction_object = {
            'assetId': ticket_1_detail_1_serial_number,
            'predictions': t7_prediction_response_for_ticket_1_detail_1_predictions,
        }
        t7_prediction_response_for_ticket_1_detail_2_predictions_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        t7_prediction_response_for_ticket_1_detail_2_predictions_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        t7_prediction_response_for_ticket_1_detail_2_predictions = [
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_1,
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_2,
        ]
        t7_prediction_response_for_ticket_1_detail_2_prediction_object = {
            'assetId': ticket_1_detail_2_serial_number,
            'predictions': t7_prediction_response_for_ticket_1_detail_2_predictions,
        }
        t7_prediction_response_for_ticket_1 = {
            'body': [
                t7_prediction_response_for_ticket_1_detail_1_prediction_object,
                t7_prediction_response_for_ticket_1_detail_2_prediction_object,
            ],
            'status': 200
        }

        t7_prediction_response_for_ticket_2_detail_1_predictions_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        t7_prediction_response_for_ticket_2_detail_1_predictions_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        t7_prediction_response_for_ticket_2_detail_1_predictions = [
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_1,
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_2,
        ]
        t7_prediction_response_for_ticket_2_detail_1_prediction_object = {
            'assetId': ticket_2_detail_1_serial_number,
            'predictions': t7_prediction_response_for_ticket_2_detail_1_predictions,
        }
        t7_prediction_response_for_ticket_2 = {
            'body': [
                t7_prediction_response_for_ticket_2_detail_1_prediction_object,
            ],
            'status': 200
        }

        next_results_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        notifications_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.build_tnba_note_from_prediction = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(side_effect=[
            t7_prediction_response_for_ticket_1_detail_1_prediction_object,
            t7_prediction_response_for_ticket_1_detail_2_prediction_object,
            t7_prediction_response_for_ticket_2_detail_1_prediction_object
        ])

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=next_results_response)
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_response_for_ticket_1,
            t7_prediction_response_for_ticket_2,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        await tnba_monitor._process_tickets_without_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        bruin_repository.get_next_results_for_ticket_detail.assert_has_awaits([
            call(ticket_1_id, ticket_1_detail_1_id, ticket_1_detail_1_serial_number),
            call(ticket_1_id, ticket_1_detail_2_id, ticket_1_detail_2_serial_number),
            call(ticket_2_id, ticket_2_detail_1_id, ticket_2_detail_1_serial_number),
        ])
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_without_tnba_with_no_predictions_after_filtering_with_next_results_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": (
                        f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00'
                    ),
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ],
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': [],
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        t7_prediction_response_for_ticket_1_detail_1_predictions_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        t7_prediction_response_for_ticket_1_detail_1_predictions_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        t7_prediction_response_for_ticket_1_detail_1_predictions = [
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_1,
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_2,
        ]
        t7_prediction_response_for_ticket_1_detail_1_prediction_object = {
            'assetId': ticket_1_detail_1_serial_number,
            'predictions': t7_prediction_response_for_ticket_1_detail_1_predictions,
        }
        t7_prediction_response_for_ticket_1_detail_2_predictions_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        t7_prediction_response_for_ticket_1_detail_2_predictions_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        t7_prediction_response_for_ticket_1_detail_2_predictions = [
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_1,
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_2,
        ]
        t7_prediction_response_for_ticket_1_detail_2_prediction_object = {
            'assetId': ticket_1_detail_2_serial_number,
            'predictions': t7_prediction_response_for_ticket_1_detail_2_predictions,
        }
        t7_prediction_response_for_ticket_1 = {
            'body': [
                t7_prediction_response_for_ticket_1_detail_1_prediction_object,
                t7_prediction_response_for_ticket_1_detail_2_prediction_object,
            ],
            'status': 200
        }

        t7_prediction_response_for_ticket_2_detail_1_predictions_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        t7_prediction_response_for_ticket_2_detail_1_predictions_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        t7_prediction_response_for_ticket_2_detail_1_predictions = [
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_1,
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_2,
        ]
        t7_prediction_response_for_ticket_2_detail_1_prediction_object = {
            'assetId': ticket_2_detail_1_serial_number,
            'predictions': t7_prediction_response_for_ticket_2_detail_1_predictions,
        }
        t7_prediction_response_for_ticket_2 = {
            'body': [
                t7_prediction_response_for_ticket_2_detail_1_prediction_object,
            ],
            'status': 200
        }

        next_results_for_ticket_1_detail_1_response = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    {
                        "resultTypeId": 620,
                        "resultName": "Some weird next result!",
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
        next_results_for_ticket_1_detail_2_response = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    {
                        "resultTypeId": 620,
                        "resultName": "Some weird next result!",
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
        next_results_for_ticket_2_detail_1_response = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    {
                        "resultTypeId": 620,
                        "resultName": "Some weird next result!",
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
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        ticket_repository = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(side_effect=[
            t7_prediction_response_for_ticket_1_detail_1_prediction_object,
            t7_prediction_response_for_ticket_1_detail_2_prediction_object,
            t7_prediction_response_for_ticket_2_detail_1_prediction_object
        ])
        prediction_repository.filter_predictions_in_next_results = Mock(return_value=filtered_predictions)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(side_effect=[
            next_results_for_ticket_1_detail_1_response,
            next_results_for_ticket_1_detail_2_response,
            next_results_for_ticket_2_detail_1_response,
        ])
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_response_for_ticket_1,
            t7_prediction_response_for_ticket_2,
        ])

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        await tnba_monitor._process_tickets_without_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        bruin_repository.get_next_results_for_ticket_detail.assert_has_awaits([
            call(ticket_1_id, ticket_1_detail_1_id, ticket_1_detail_1_serial_number),
            call(ticket_1_id, ticket_1_detail_2_id, ticket_1_detail_2_serial_number),
            call(ticket_2_id, ticket_2_detail_1_id, ticket_2_detail_1_serial_number),
        ])
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_without_tnba_with_dev_env_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": (
                        f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00'
                    ),
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ],
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': [],
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        t7_prediction_response_for_ticket_1_detail_1_predictions_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        t7_prediction_response_for_ticket_1_detail_1_predictions_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        t7_prediction_response_for_ticket_1_detail_1_predictions = [
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_1,
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_2,
        ]
        t7_prediction_response_for_ticket_1_detail_1_prediction_object = {
            'assetId': ticket_1_detail_1_serial_number,
            'predictions': t7_prediction_response_for_ticket_1_detail_1_predictions,
        }
        t7_prediction_response_for_ticket_1_detail_2_predictions_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        t7_prediction_response_for_ticket_1_detail_2_predictions_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        t7_prediction_response_for_ticket_1_detail_2_predictions = [
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_1,
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_2,
        ]
        t7_prediction_response_for_ticket_1_detail_2_prediction_object = {
            'assetId': ticket_1_detail_2_serial_number,
            'predictions': t7_prediction_response_for_ticket_1_detail_2_predictions,
        }
        t7_prediction_response_for_ticket_1 = {
            'body': [
                t7_prediction_response_for_ticket_1_detail_1_prediction_object,
                t7_prediction_response_for_ticket_1_detail_2_prediction_object,
            ],
            'status': 200
        }

        t7_prediction_response_for_ticket_2_detail_1_predictions_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        t7_prediction_response_for_ticket_2_detail_1_predictions_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        t7_prediction_response_for_ticket_2_detail_1_predictions = [
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_1,
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_2,
        ]
        t7_prediction_response_for_ticket_2_detail_1_prediction_object = {
            'assetId': ticket_2_detail_1_serial_number,
            'predictions': t7_prediction_response_for_ticket_2_detail_1_predictions,
        }
        t7_prediction_response_for_ticket_2 = {
            'body': [
                t7_prediction_response_for_ticket_2_detail_1_prediction_object,
            ],
            'status': 200
        }

        next_results_for_ticket_1_detail_1_response = {
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
        next_results_for_ticket_1_detail_2_response = {
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
        next_results_for_ticket_2_detail_1_response = {
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

        filtered_predictions_for_ticket_1_detail_1 = [
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_1,
        ]
        filtered_predictions_for_ticket_1_detail_2 = [
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_1,
        ]
        filtered_predictions_for_ticket_2_detail_1 = [
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_1,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        ticket_repository = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(side_effect=[
            t7_prediction_response_for_ticket_1_detail_1_prediction_object,
            t7_prediction_response_for_ticket_1_detail_2_prediction_object,
            t7_prediction_response_for_ticket_2_detail_1_prediction_object
        ])
        prediction_repository.filter_predictions_in_next_results = Mock(side_effect=[
            filtered_predictions_for_ticket_1_detail_1,
            filtered_predictions_for_ticket_1_detail_2,
            filtered_predictions_for_ticket_2_detail_1,
        ])
        prediction_repository.get_best_prediction = Mock(side_effect=[
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_1,
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_1,
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_1,
        ])

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(side_effect=[
            next_results_for_ticket_1_detail_1_response,
            next_results_for_ticket_1_detail_2_response,
            next_results_for_ticket_2_detail_1_response,
        ])
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_response_for_ticket_1,
            t7_prediction_response_for_ticket_2,
        ])

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        with patch.object(config, 'ENVIRONMENT', "dev"):
            await tnba_monitor._process_tickets_without_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        bruin_repository.get_next_results_for_ticket_detail.assert_has_awaits([
            call(ticket_1_id, ticket_1_detail_1_id, ticket_1_detail_1_serial_number),
            call(ticket_1_id, ticket_1_detail_2_id, ticket_1_detail_2_serial_number),
            call(ticket_2_id, ticket_2_detail_1_id, ticket_2_detail_1_serial_number),
        ])
        ticket_repository.build_tnba_note_from_prediction.assert_has_calls([
            call(t7_prediction_response_for_ticket_1_detail_1_predictions_item_1),
            call(t7_prediction_response_for_ticket_1_detail_2_predictions_item_1),
            call(t7_prediction_response_for_ticket_2_detail_1_predictions_item_1),
        ])
        assert notifications_repository.send_slack_message.await_count == 3
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_without_tnba_with_append_multiple_notes_returning_non_2xx_status_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": (
                        f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00'
                    ),
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ],
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': [],
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        t7_prediction_response_for_ticket_1_detail_1_predictions_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        t7_prediction_response_for_ticket_1_detail_1_predictions_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        t7_prediction_response_for_ticket_1_detail_1_predictions = [
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_1,
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_2,
        ]
        t7_prediction_response_for_ticket_1_detail_1_prediction_object = {
            'assetId': ticket_1_detail_1_serial_number,
            'predictions': t7_prediction_response_for_ticket_1_detail_1_predictions,
        }
        t7_prediction_response_for_ticket_1_detail_2_predictions_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        t7_prediction_response_for_ticket_1_detail_2_predictions_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        t7_prediction_response_for_ticket_1_detail_2_predictions = [
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_1,
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_2,
        ]
        t7_prediction_response_for_ticket_1_detail_2_prediction_object = {
            'assetId': ticket_1_detail_2_serial_number,
            'predictions': t7_prediction_response_for_ticket_1_detail_2_predictions,
        }
        t7_prediction_response_for_ticket_1 = {
            'body': [
                t7_prediction_response_for_ticket_1_detail_1_prediction_object,
                t7_prediction_response_for_ticket_1_detail_2_prediction_object,
            ],
            'status': 200
        }

        t7_prediction_response_for_ticket_2_detail_1_predictions_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        t7_prediction_response_for_ticket_2_detail_1_predictions_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        t7_prediction_response_for_ticket_2_detail_1_predictions = [
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_1,
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_2,
        ]
        t7_prediction_response_for_ticket_2_detail_1_prediction_object = {
            'assetId': ticket_2_detail_1_serial_number,
            'predictions': t7_prediction_response_for_ticket_2_detail_1_predictions,
        }
        t7_prediction_response_for_ticket_2 = {
            'body': [
                t7_prediction_response_for_ticket_2_detail_1_prediction_object,
            ],
            'status': 200
        }

        next_results_for_ticket_1_detail_1_response = {
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
        next_results_for_ticket_1_detail_2_response = {
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
        next_results_for_ticket_2_detail_1_response = {
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

        filtered_predictions_for_ticket_1_detail_1 = [
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_1
        ]
        filtered_predictions_for_ticket_1_detail_2 = [
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_1
        ]
        filtered_predictions_for_ticket_2_detail_1 = [
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_1
        ]

        tnba_note_for_ticket_1_detail_1 = 'This is TNBA note 1'
        tnba_note_for_ticket_1_detail_2 = 'This is TNBA note 2'
        tnba_note_for_ticket_2_detail_1 = 'This is TNBA note 3'

        append_multiple_notes_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.build_tnba_note_from_prediction = Mock(side_effect=[
            tnba_note_for_ticket_1_detail_1,
            tnba_note_for_ticket_1_detail_2,
            tnba_note_for_ticket_2_detail_1,
        ])

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(side_effect=[
            t7_prediction_response_for_ticket_1_detail_1_prediction_object,
            t7_prediction_response_for_ticket_1_detail_2_prediction_object,
            t7_prediction_response_for_ticket_2_detail_1_prediction_object,
        ])
        prediction_repository.filter_predictions_in_next_results = Mock(side_effect=[
            filtered_predictions_for_ticket_1_detail_1,
            filtered_predictions_for_ticket_1_detail_2,
            filtered_predictions_for_ticket_2_detail_1,
        ])
        prediction_repository.get_best_prediction = Mock(side_effect=[
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_1,
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_1,
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_1,
        ])

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(side_effect=[
            next_results_for_ticket_1_detail_1_response,
            next_results_for_ticket_1_detail_2_response,
            next_results_for_ticket_2_detail_1_response,
        ])
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock(return_value=append_multiple_notes_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_response_for_ticket_1,
            t7_prediction_response_for_ticket_2,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        with patch.object(config, 'ENVIRONMENT', "production"):
            await tnba_monitor._process_tickets_without_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        bruin_repository.get_next_results_for_ticket_detail.assert_has_awaits([
            call(ticket_1_id, ticket_1_detail_1_id, ticket_1_detail_1_serial_number),
            call(ticket_1_id, ticket_1_detail_2_id, ticket_1_detail_2_serial_number),
            call(ticket_2_id, ticket_2_detail_1_id, ticket_2_detail_1_serial_number),
        ])
        ticket_repository.build_tnba_note_from_prediction.assert_has_calls([
            call(t7_prediction_response_for_ticket_1_detail_1_predictions_item_1),
            call(t7_prediction_response_for_ticket_1_detail_2_predictions_item_1),
            call(t7_prediction_response_for_ticket_2_detail_1_predictions_item_1),
        ])
        bruin_repository.append_multiple_notes_to_ticket.assert_has_awaits([
            call(
                ticket_1_id,
                [
                    {
                        'text': tnba_note_for_ticket_1_detail_1,
                        'detail_id': ticket_1_detail_1_id,
                        'service_number': ticket_1_detail_1_serial_number,
                    },
                    {
                        'text': tnba_note_for_ticket_1_detail_2,
                        'detail_id': ticket_1_detail_2_id,
                        'service_number': ticket_1_detail_2_serial_number,
                    },
                ],
            ),
            call(
                ticket_2_id,
                [
                    {
                        'text': tnba_note_for_ticket_2_detail_1,
                        'detail_id': ticket_2_detail_1_id,
                        'service_number': ticket_2_detail_1_serial_number,
                    },
                ],
            ),
        ])
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_without_tnba_with_all_conditions_met_for_appending_tnba_notes_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894040,
                    "noteValue": (
                        f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00'
                    ),
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ],
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': [],
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        t7_prediction_response_for_ticket_1_detail_1_predictions_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        t7_prediction_response_for_ticket_1_detail_1_predictions_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        t7_prediction_response_for_ticket_1_detail_1_predictions = [
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_1,
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_2,
        ]
        t7_prediction_response_for_ticket_1_detail_1_prediction_object = {
            'assetId': ticket_1_detail_1_serial_number,
            'predictions': t7_prediction_response_for_ticket_1_detail_1_predictions,
        }
        t7_prediction_response_for_ticket_1_detail_2_predictions_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        t7_prediction_response_for_ticket_1_detail_2_predictions_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        t7_prediction_response_for_ticket_1_detail_2_predictions = [
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_1,
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_2,
        ]
        t7_prediction_response_for_ticket_1_detail_2_prediction_object = {
            'assetId': ticket_1_detail_2_serial_number,
            'predictions': t7_prediction_response_for_ticket_1_detail_2_predictions,
        }
        t7_prediction_response_for_ticket_1 = {
            'body': [
                t7_prediction_response_for_ticket_1_detail_1_prediction_object,
                t7_prediction_response_for_ticket_1_detail_2_prediction_object,
            ],
            'status': 200
        }

        t7_prediction_response_for_ticket_2_detail_1_predictions_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        t7_prediction_response_for_ticket_2_detail_1_predictions_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        t7_prediction_response_for_ticket_2_detail_1_predictions = [
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_1,
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_2,
        ]
        t7_prediction_response_for_ticket_2_detail_1_prediction_object = {
            'assetId': ticket_2_detail_1_serial_number,
            'predictions': t7_prediction_response_for_ticket_2_detail_1_predictions,
        }
        t7_prediction_response_for_ticket_2 = {
            'body': [
                t7_prediction_response_for_ticket_2_detail_1_prediction_object,
            ],
            'status': 200
        }

        next_results_for_ticket_1_detail_1_response = {
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
        next_results_for_ticket_1_detail_2_response = {
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
        next_results_for_ticket_2_detail_1_response = {
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

        filtered_predictions_for_ticket_1_detail_1 = [
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_1
        ]
        filtered_predictions_for_ticket_1_detail_2 = [
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_1
        ]
        filtered_predictions_for_ticket_2_detail_1 = [
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_1
        ]

        tnba_note_for_ticket_1_detail_1 = 'This is TNBA note 1'
        tnba_note_for_ticket_1_detail_2 = 'This is TNBA note 2'
        tnba_note_for_ticket_2_detail_1 = 'This is TNBA note 3'

        append_multiple_notes_response = {
            'body': 'ok',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.build_tnba_note_from_prediction = Mock(side_effect=[
            tnba_note_for_ticket_1_detail_1,
            tnba_note_for_ticket_1_detail_2,
            tnba_note_for_ticket_2_detail_1,
        ])

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(side_effect=[
            t7_prediction_response_for_ticket_1_detail_1_prediction_object,
            t7_prediction_response_for_ticket_1_detail_2_prediction_object,
            t7_prediction_response_for_ticket_2_detail_1_prediction_object,
        ])
        prediction_repository.filter_predictions_in_next_results = Mock(side_effect=[
            filtered_predictions_for_ticket_1_detail_1,
            filtered_predictions_for_ticket_1_detail_2,
            filtered_predictions_for_ticket_2_detail_1,
        ])
        prediction_repository.get_best_prediction = Mock(side_effect=[
            t7_prediction_response_for_ticket_1_detail_1_predictions_item_1,
            t7_prediction_response_for_ticket_1_detail_2_predictions_item_1,
            t7_prediction_response_for_ticket_2_detail_1_predictions_item_1,
        ])

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(side_effect=[
            next_results_for_ticket_1_detail_1_response,
            next_results_for_ticket_1_detail_2_response,
            next_results_for_ticket_2_detail_1_response,
        ])
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock(return_value=append_multiple_notes_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_response_for_ticket_1,
            t7_prediction_response_for_ticket_2,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        with patch.object(config, 'ENVIRONMENT', "production"):
            await tnba_monitor._process_tickets_without_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        bruin_repository.get_next_results_for_ticket_detail.assert_has_awaits([
            call(ticket_1_id, ticket_1_detail_1_id, ticket_1_detail_1_serial_number),
            call(ticket_1_id, ticket_1_detail_2_id, ticket_1_detail_2_serial_number),
            call(ticket_2_id, ticket_2_detail_1_id, ticket_2_detail_1_serial_number),
        ])
        ticket_repository.build_tnba_note_from_prediction.assert_has_calls([
            call(t7_prediction_response_for_ticket_1_detail_1_predictions_item_1),
            call(t7_prediction_response_for_ticket_1_detail_2_predictions_item_1),
            call(t7_prediction_response_for_ticket_2_detail_1_predictions_item_1),
        ])
        bruin_repository.append_multiple_notes_to_ticket.assert_has_awaits([
            call(
                ticket_1_id,
                [
                    {
                        'text': tnba_note_for_ticket_1_detail_1,
                        'detail_id': ticket_1_detail_1_id,
                        'service_number': ticket_1_detail_1_serial_number,
                    },
                    {
                        'text': tnba_note_for_ticket_1_detail_2,
                        'detail_id': ticket_1_detail_2_id,
                        'service_number': ticket_1_detail_2_serial_number,
                    },
                ],
            ),
            call(
                ticket_2_id,
                [
                    {
                        'text': tnba_note_for_ticket_2_detail_1,
                        'detail_id': ticket_2_detail_1_id,
                        'service_number': ticket_2_detail_1_serial_number,
                    },
                ],
            ),
        ])
        assert notifications_repository.send_slack_message.await_count == 2

    @pytest.mark.asyncio
    async def process_tickets_with_tnba_with_empty_list_of_tickets_test(self):
        tickets = []

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        notifications_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock()
        ticket_repository.is_tnba_note_old_enough = Mock()
        ticket_repository.build_tnba_note_from_prediction = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock()
        prediction_repository.filter_predictions_in_next_results = Mock()
        prediction_repository.get_best_prediction = Mock()

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock()
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        await tnba_monitor._process_tickets_with_tnba(tickets)

        t7_repository.get_prediction.assert_not_awaited()
        ticket_repository.find_newest_tnba_note_by_service_number.assert_not_called()
        ticket_repository.is_tnba_note_old_enough.assert_not_called()
        prediction_repository.find_prediction_object_by_serial.assert_not_called()
        bruin_repository.get_next_results_for_ticket_detail.assert_not_awaited()
        prediction_repository.filter_predictions_in_next_results.assert_not_called()
        prediction_repository.get_best_prediction.assert_not_called()
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_with_tnba_with_retrieval_of_prediction_returning_non_2xx_status_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_1_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_1_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_1_notes = [
            ticket_1_note_1,
            ticket_1_note_2,
            ticket_1_note_3,
        ]
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': ticket_1_notes,
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_2_notes = [
            ticket_2_note_1,
        ]
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': ticket_2_notes,
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        t7_prediction_response = {
            'body': 'Got internal error from T7',
            'status': 500
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        notifications_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock()
        ticket_repository.is_tnba_note_old_enough = Mock()
        ticket_repository.build_tnba_note_from_prediction = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock()
        prediction_repository.filter_predictions_in_next_results = Mock()
        prediction_repository.get_best_prediction = Mock()

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock()
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(return_value=t7_prediction_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        await tnba_monitor._process_tickets_with_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        ticket_repository.find_newest_tnba_note_by_service_number.assert_not_called()
        ticket_repository.is_tnba_note_old_enough.assert_not_called()
        prediction_repository.find_prediction_object_by_serial.assert_not_called()
        bruin_repository.get_next_results_for_ticket_detail.assert_not_awaited()
        prediction_repository.filter_predictions_in_next_results.assert_not_called()
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_with_tnba_with_tnba_note_too_recent_for_a_new_append_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_1_serial_number,
            ],
        }
        ticket_1_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                'VC0000000',
            ],
        }
        ticket_1_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_2_serial_number,
            ],
        }
        ticket_1_notes = [
            ticket_1_note_1,
            ticket_1_note_2,
            ticket_1_note_3,
        ]
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': ticket_1_notes,
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_2_detail_1_serial_number,
            ],
        }
        ticket_2_notes = [
            ticket_2_note_1,
        ]
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': ticket_2_notes,
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        predictions_for_ticket_1 = [
            {
                'assetId': 'VC8888888',
                'predictions': [
                    {
                        'name': 'Repair Completed',
                        'probability': 0.9484384655952454
                    },
                    {
                        'name': 'Holmdel NOC Investigate',
                        'probability': 0.1234567890123456
                    },
                ]
            },
        ]
        t7_prediction_for_ticket_1_response = {
            'body': predictions_for_ticket_1,
            'status': 200
        }

        predictions_for_ticket_2 = [
            {
                'assetId': 'VC9999999',
                'predictions': [
                    {
                        'name': 'Request Completed',
                        'probability': 0.1111111111111111
                    },
                    {
                        'name': 'No Trouble Found - Carrier Issue',
                        'probability': 0.2222222222222222
                    },
                ]
            },
        ]
        t7_prediction_for_ticket_2_response = {
            'body': predictions_for_ticket_2,
            'status': 200
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        notifications_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(side_effect=[
            ticket_1_note_1,
            ticket_1_note_3,
            ticket_2_note_1,
        ])
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=False)
        ticket_repository.build_tnba_note_from_prediction = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock()
        prediction_repository.filter_predictions_in_next_results = Mock()
        prediction_repository.get_best_prediction = Mock()

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock()
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_for_ticket_1_response,
            t7_prediction_for_ticket_2_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        await tnba_monitor._process_tickets_with_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        ticket_repository.find_newest_tnba_note_by_service_number.assert_has_calls([
            call(ticket_1_notes, ticket_1_detail_1_serial_number),
            call(ticket_1_notes, ticket_1_detail_2_serial_number),
            call(ticket_2_notes, ticket_2_detail_1_serial_number),
        ])
        ticket_repository.is_tnba_note_old_enough.assert_has_calls([
            call(ticket_1_note_1),
            call(ticket_1_note_3),
            call(ticket_2_note_1),
        ])
        prediction_repository.find_prediction_object_by_serial.assert_not_called()
        bruin_repository.get_next_results_for_ticket_detail.assert_not_awaited()
        prediction_repository.filter_predictions_in_next_results.assert_not_called()
        prediction_repository.get_best_prediction.assert_not_called()
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_with_tnba_with_no_predictions_found_for_target_serials_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_1_serial_number,
            ],
        }
        ticket_1_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                'VC0000000',
            ],
        }
        ticket_1_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_2_serial_number,
            ],
        }
        ticket_1_notes = [
            ticket_1_note_1,
            ticket_1_note_2,
            ticket_1_note_3,
        ]
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': ticket_1_notes,
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_2_notes = [
            ticket_2_note_1,
        ]
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': ticket_2_notes,
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        predictions_for_ticket_1 = [
            {
                'assetId': 'VC8888888',
                'predictions': [
                    {
                        'name': 'Repair Completed',
                        'probability': 0.9484384655952454
                    },
                    {
                        'name': 'Holmdel NOC Investigate',
                        'probability': 0.1234567890123456
                    },
                ]
            },
        ]
        t7_prediction_for_ticket_1_response = {
            'body': predictions_for_ticket_1,
            'status': 200
        }

        predictions_for_ticket_2 = [
            {
                'assetId': 'VC0000000',
                'predictions': [
                    {
                        'name': 'Request Completed',
                        'probability': 0.1111111111111111
                    },
                    {
                        'name': 'No Trouble Found - Carrier Issue',
                        'probability': 0.2222222222222222
                    },
                ]
            },
        ]
        t7_prediction_for_ticket_2_response = {
            'body': predictions_for_ticket_2,
            'status': 200
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        notifications_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(side_effect=[
            ticket_1_note_1,
            ticket_1_note_3,
            ticket_2_note_1,
        ])
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)
        ticket_repository.build_tnba_note_from_prediction = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(return_value=None)
        prediction_repository.filter_predictions_in_next_results = Mock()
        prediction_repository.get_best_prediction = Mock()

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock()
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_for_ticket_1_response,
            t7_prediction_for_ticket_2_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        await tnba_monitor._process_tickets_with_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        ticket_repository.find_newest_tnba_note_by_service_number.assert_has_calls([
            call(ticket_1_notes, ticket_1_detail_1_serial_number),
            call(ticket_1_notes, ticket_1_detail_2_serial_number),
            call(ticket_2_notes, ticket_2_detail_1_serial_number),
        ])
        ticket_repository.is_tnba_note_old_enough.assert_has_calls([
            call(ticket_1_note_1),
            call(ticket_1_note_3),
            call(ticket_2_note_1),
        ])
        prediction_repository.find_prediction_object_by_serial.assert_has_calls([
            call(predictions_for_ticket_1, ticket_1_detail_1_serial_number),
            call(predictions_for_ticket_1, ticket_1_detail_2_serial_number),
            call(predictions_for_ticket_2, ticket_2_detail_1_serial_number),
        ])
        bruin_repository.get_next_results_for_ticket_detail.assert_not_awaited()
        prediction_repository.filter_predictions_in_next_results.assert_not_called()
        prediction_repository.get_best_prediction.assert_not_called()
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_with_tnba_with_predictions_found_for_target_serials_and_predictions_having_error_test(
            self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_1_serial_number,
            ],
        }
        ticket_1_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                'VC0000000',
            ],
        }
        ticket_1_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_2_serial_number,
            ],
        }
        ticket_1_notes = [
            ticket_1_note_1,
            ticket_1_note_2,
            ticket_1_note_3,
        ]
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': ticket_1_notes,
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_2_notes = [
            ticket_2_note_1,
        ]
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': ticket_2_notes,
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        prediction_for_ticket_1_detail_1 = {
            'assetId': ticket_1_detail_1_serial_number,
            'error': {
                'code': 'error_in_prediction',
                'message': 'Error executing prediction: The labels [\'Refer to ASR Carrier\'] are not in the '
                           'Task Result" labels map.'
            },
        }
        prediction_for_ticket_1_detail_2 = {
            'assetId': ticket_1_detail_2_serial_number,
            'error': {
                'code': 'error_in_prediction',
                'message': "Error executing prediction: The labels "
                           "['Service Repaired', 'Investigating Wireless Device Issue'] are not "
                           "in the \"Task Result\" labels map."
            },
        }
        predictions_for_ticket_1 = [
            prediction_for_ticket_1_detail_1,
            prediction_for_ticket_1_detail_2,
        ]
        t7_prediction_for_ticket_1_response = {
            'body': predictions_for_ticket_1,
            'status': 200
        }

        prediction_for_ticket_2_detail_1 = {
            'assetId': ticket_2_detail_1_serial_number,
            'error': {
                'code': 'error_in_prediction',
                'message': "Error executing prediction: The labels "
                           "['Line Test Results Provided'] are not in the \"Task Result\" labels map."
            },
        }
        predictions_for_ticket_2 = [
            prediction_for_ticket_2_detail_1,
        ]
        t7_prediction_for_ticket_2_response = {
            'body': predictions_for_ticket_2,
            'status': 200
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(side_effect=[
            ticket_1_note_1,
            ticket_1_note_3,
            ticket_2_note_1,
        ])
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)
        ticket_repository.build_tnba_note_from_prediction = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(side_effect=[
            prediction_for_ticket_1_detail_1,
            prediction_for_ticket_1_detail_2,
            prediction_for_ticket_2_detail_1,
        ])
        prediction_repository.filter_predictions_in_next_results = Mock()
        prediction_repository.get_best_prediction = Mock()

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock()
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_for_ticket_1_response,
            t7_prediction_for_ticket_2_response,
        ])

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        await tnba_monitor._process_tickets_with_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        ticket_repository.find_newest_tnba_note_by_service_number.assert_has_calls([
            call(ticket_1_notes, ticket_1_detail_1_serial_number),
            call(ticket_1_notes, ticket_1_detail_2_serial_number),
            call(ticket_2_notes, ticket_2_detail_1_serial_number),
        ])
        ticket_repository.is_tnba_note_old_enough.assert_has_calls([
            call(ticket_1_note_1),
            call(ticket_1_note_3),
            call(ticket_2_note_1),
        ])
        prediction_repository.find_prediction_object_by_serial.assert_has_calls([
            call(predictions_for_ticket_1, ticket_1_detail_1_serial_number),
            call(predictions_for_ticket_1, ticket_1_detail_2_serial_number),
            call(predictions_for_ticket_2, ticket_2_detail_1_serial_number),
        ])
        assert notifications_repository.send_slack_message.await_count == 3
        bruin_repository.get_next_results_for_ticket_detail.assert_not_awaited()
        prediction_repository.filter_predictions_in_next_results.assert_not_called()
        prediction_repository.get_best_prediction.assert_not_called()
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_with_tnba_with_retrieval_of_next_results_returning_non_2xx_status_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_1_serial_number,
            ],
        }
        ticket_1_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                'VC0000000',
            ],
        }
        ticket_1_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_2_serial_number,
            ],
        }
        ticket_1_notes = [
            ticket_1_note_1,
            ticket_1_note_2,
            ticket_1_note_3,
        ]
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': ticket_1_notes,
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_2_notes = [
            ticket_2_note_1,
        ]
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': ticket_2_notes,
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        prediction_object_for_ticket_1_detail_1 = {
            'assetId': ticket_1_detail_1_serial_number,
            'predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
                {
                    'name': 'Holmdel NOC Investigate',
                    'probability': 0.1234567890123456
                },
            ]
        }
        prediction_object_for_ticket_1_detail_2 = {
            'assetId': ticket_1_detail_2_serial_number,
            'predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
                {
                    'name': 'Holmdel NOC Investigate',
                    'probability': 0.1234567890123456
                },
            ]
        }
        predictions_for_ticket_1 = [
            prediction_object_for_ticket_1_detail_1,
            prediction_object_for_ticket_1_detail_2,
        ]
        t7_prediction_for_ticket_1_response = {
            'body': predictions_for_ticket_1,
            'status': 200
        }

        prediction_object_for_ticket_2_detail_1 = {
            'assetId': ticket_2_detail_1_serial_number,
            'predictions': [
                {
                    'name': 'Request Completed',
                    'probability': 0.1111111111111111
                },
                {
                    'name': 'No Trouble Found - Carrier Issue',
                    'probability': 0.2222222222222222
                },
            ]
        }
        predictions_for_ticket_2 = [
            prediction_object_for_ticket_2_detail_1,
        ]
        t7_prediction_for_ticket_2_response = {
            'body': predictions_for_ticket_2,
            'status': 200
        }

        next_results_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        notifications_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(side_effect=[
            ticket_1_note_1,
            ticket_1_note_3,
            ticket_2_note_1,
        ])
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)
        ticket_repository.build_tnba_note_from_prediction = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(side_effect=[
            prediction_object_for_ticket_1_detail_1,
            prediction_object_for_ticket_1_detail_2,
            prediction_object_for_ticket_2_detail_1,
        ])
        prediction_repository.filter_predictions_in_next_results = Mock()
        prediction_repository.get_best_prediction = Mock()

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(return_value=next_results_response)
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_for_ticket_1_response,
            t7_prediction_for_ticket_2_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        await tnba_monitor._process_tickets_with_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        ticket_repository.find_newest_tnba_note_by_service_number.assert_has_calls([
            call(ticket_1_notes, ticket_1_detail_1_serial_number),
            call(ticket_1_notes, ticket_1_detail_2_serial_number),
            call(ticket_2_notes, ticket_2_detail_1_serial_number),
        ])
        ticket_repository.is_tnba_note_old_enough.assert_has_calls([
            call(ticket_1_note_1),
            call(ticket_1_note_3),
            call(ticket_2_note_1),
        ])
        prediction_repository.find_prediction_object_by_serial.assert_has_calls([
            call(predictions_for_ticket_1, ticket_1_detail_1_serial_number),
            call(predictions_for_ticket_1, ticket_1_detail_2_serial_number),
            call(predictions_for_ticket_2, ticket_2_detail_1_serial_number),
        ])
        bruin_repository.get_next_results_for_ticket_detail.assert_has_awaits([
            call(ticket_1_id, ticket_1_detail_1_id, ticket_1_detail_1_serial_number),
            call(ticket_1_id, ticket_1_detail_2_id, ticket_1_detail_2_serial_number),
            call(ticket_2_id, ticket_2_detail_1_id, ticket_2_detail_1_serial_number),
        ])
        prediction_repository.filter_predictions_in_next_results.assert_not_called()
        prediction_repository.get_best_prediction.assert_not_called()
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_with_tnba_with_no_predictions_after_filtering_with_next_results_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_1_serial_number,
            ],
        }
        ticket_1_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                'VC0000000',
            ],
        }
        ticket_1_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_2_serial_number,
            ],
        }
        ticket_1_notes = [
            ticket_1_note_1,
            ticket_1_note_2,
            ticket_1_note_3,
        ]
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': ticket_1_notes,
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_2_notes = [
            ticket_2_note_1,
        ]
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': ticket_2_notes,
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        prediction_object_for_ticket_1_detail_1_predictions_list = [
            {
                'name': 'Repair Completed',
                'probability': 0.9484384655952454
            },
            {
                'name': 'Holmdel NOC Investigate',
                'probability': 0.1234567890123456
            },
        ]
        prediction_object_for_ticket_1_detail_1 = {
            'assetId': ticket_1_detail_1_serial_number,
            'predictions': prediction_object_for_ticket_1_detail_1_predictions_list,
        }
        prediction_object_for_ticket_1_detail_2_predictions_list = [
            {
                'name': 'Repair Completed',
                'probability': 0.9484384655952454
            },
            {
                'name': 'Holmdel NOC Investigate',
                'probability': 0.1234567890123456
            },
        ]
        prediction_object_for_ticket_1_detail_2 = {
            'assetId': ticket_1_detail_2_serial_number,
            'predictions': prediction_object_for_ticket_1_detail_2_predictions_list,
        }
        predictions_for_ticket_1 = [
            prediction_object_for_ticket_1_detail_1,
            prediction_object_for_ticket_1_detail_2,
        ]
        t7_prediction_for_ticket_1_response = {
            'body': predictions_for_ticket_1,
            'status': 200
        }

        prediction_object_for_ticket_2_detail_1_predictions_list = [
            {
                'name': 'Request Completed',
                'probability': 0.1111111111111111
            },
            {
                'name': 'No Trouble Found - Carrier Issue',
                'probability': 0.2222222222222222
            },
        ]
        prediction_object_for_ticket_2_detail_1 = {
            'assetId': ticket_2_detail_1_serial_number,
            'predictions': prediction_object_for_ticket_2_detail_1_predictions_list,
        }
        predictions_for_ticket_2 = [
            prediction_object_for_ticket_2_detail_1,
        ]
        t7_prediction_for_ticket_2_response = {
            'body': predictions_for_ticket_2,
            'status': 200
        }

        available_results_for_ticket_1_detail_1 = [
            {
                "resultTypeId": 620,
                "resultName": "Some weird next result!",
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
        ]
        next_results_response_for_ticket_1_detail_1 = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": available_results_for_ticket_1_detail_1,
            },
            'status': 200,
        }

        available_results_for_ticket_1_detail_2 = [
            {
                "resultTypeId": 620,
                "resultName": "Some weird next result!",
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
        ]
        next_results_response_for_ticket_1_detail_2 = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": available_results_for_ticket_1_detail_2,
            },
            'status': 200,
        }

        available_results_for_ticket_2_detail_1 = [
            {
                "resultTypeId": 620,
                "resultName": "Some weird next result!",
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
        ]
        next_results_response_for_ticket_2_detail_1 = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": available_results_for_ticket_2_detail_1,
            },
            'status': 200,
        }

        filtered_predictions = []

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        notifications_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(side_effect=[
            ticket_1_note_1,
            ticket_1_note_3,
            ticket_2_note_1,
        ])
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)
        ticket_repository.build_tnba_note_from_prediction = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(side_effect=[
            prediction_object_for_ticket_1_detail_1,
            prediction_object_for_ticket_1_detail_2,
            prediction_object_for_ticket_2_detail_1,
        ])
        prediction_repository.filter_predictions_in_next_results = Mock(return_value=filtered_predictions)
        prediction_repository.get_best_prediction = Mock()

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(side_effect=[
            next_results_response_for_ticket_1_detail_1,
            next_results_response_for_ticket_1_detail_2,
            next_results_response_for_ticket_2_detail_1,
        ])
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_for_ticket_1_response,
            t7_prediction_for_ticket_2_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        await tnba_monitor._process_tickets_with_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        ticket_repository.find_newest_tnba_note_by_service_number.assert_has_calls([
            call(ticket_1_notes, ticket_1_detail_1_serial_number),
            call(ticket_1_notes, ticket_1_detail_2_serial_number),
            call(ticket_2_notes, ticket_2_detail_1_serial_number),
        ])
        ticket_repository.is_tnba_note_old_enough.assert_has_calls([
            call(ticket_1_note_1),
            call(ticket_1_note_3),
            call(ticket_2_note_1),
        ])
        prediction_repository.find_prediction_object_by_serial.assert_has_calls([
            call(predictions_for_ticket_1, ticket_1_detail_1_serial_number),
            call(predictions_for_ticket_1, ticket_1_detail_2_serial_number),
            call(predictions_for_ticket_2, ticket_2_detail_1_serial_number),
        ])
        bruin_repository.get_next_results_for_ticket_detail.assert_has_awaits([
            call(ticket_1_id, ticket_1_detail_1_id, ticket_1_detail_1_serial_number),
            call(ticket_1_id, ticket_1_detail_2_id, ticket_1_detail_2_serial_number),
            call(ticket_2_id, ticket_2_detail_1_id, ticket_2_detail_1_serial_number),
        ])
        prediction_repository.filter_predictions_in_next_results.assert_has_calls([
            call(prediction_object_for_ticket_1_detail_1_predictions_list, available_results_for_ticket_1_detail_1),
            call(prediction_object_for_ticket_1_detail_2_predictions_list, available_results_for_ticket_1_detail_2),
            call(prediction_object_for_ticket_2_detail_1_predictions_list, available_results_for_ticket_2_detail_1),
        ])
        prediction_repository.get_best_prediction.assert_not_called()
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_with_tnba_with_no_changes_since_last_prediction_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_1_serial_number,
            ],
        }
        ticket_1_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                'VC0000000',
            ],
        }
        ticket_1_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_2_serial_number,
            ],
        }
        ticket_1_notes = [
            ticket_1_note_1,
            ticket_1_note_2,
            ticket_1_note_3,
        ]
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': ticket_1_notes,
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_2_notes = [
            ticket_2_note_1,
        ]
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': ticket_2_notes,
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        prediction_object_for_ticket_1_detail_1_predictions_list_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        prediction_object_for_ticket_1_detail_1_predictions_list_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        prediction_object_for_ticket_1_detail_1_predictions_list = [
            prediction_object_for_ticket_1_detail_1_predictions_list_item_1,
            prediction_object_for_ticket_1_detail_1_predictions_list_item_2,
        ]
        prediction_object_for_ticket_1_detail_1 = {
            'assetId': ticket_1_detail_1_serial_number,
            'predictions': prediction_object_for_ticket_1_detail_1_predictions_list,
        }
        prediction_object_for_ticket_1_detail_2_predictions_list_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        prediction_object_for_ticket_1_detail_2_predictions_list_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        prediction_object_for_ticket_1_detail_2_predictions_list = [
            prediction_object_for_ticket_1_detail_2_predictions_list_item_1,
            prediction_object_for_ticket_1_detail_2_predictions_list_item_2,
        ]
        prediction_object_for_ticket_1_detail_2 = {
            'assetId': ticket_1_detail_2_serial_number,
            'predictions': prediction_object_for_ticket_1_detail_2_predictions_list,
        }
        predictions_for_ticket_1 = [
            prediction_object_for_ticket_1_detail_1,
            prediction_object_for_ticket_1_detail_2,
        ]
        t7_prediction_for_ticket_1_response = {
            'body': predictions_for_ticket_1,
            'status': 200
        }

        prediction_object_for_ticket_2_detail_1_predictions_list_item_1 = {
            'name': 'Request Completed',
            'probability': 0.1111111111111111
        }
        prediction_object_for_ticket_2_detail_1_predictions_list_item_2 = {
            'name': 'No Trouble Found - Carrier Issue',
            'probability': 0.2222222222222222
        }
        prediction_object_for_ticket_2_detail_1_predictions_list = [
            prediction_object_for_ticket_2_detail_1_predictions_list_item_1,
            prediction_object_for_ticket_2_detail_1_predictions_list_item_2,
        ]
        prediction_object_for_ticket_2_detail_1 = {
            'assetId': ticket_2_detail_1_serial_number,
            'predictions': prediction_object_for_ticket_2_detail_1_predictions_list,
        }
        predictions_for_ticket_2 = [
            prediction_object_for_ticket_2_detail_1,
        ]
        t7_prediction_for_ticket_2_response = {
            'body': predictions_for_ticket_2,
            'status': 200
        }

        available_results_for_ticket_1_detail_1 = [
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
        ]
        next_results_response_for_ticket_1_detail_1 = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": available_results_for_ticket_1_detail_1,
            },
            'status': 200,
        }

        available_results_for_ticket_1_detail_2 = [
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
        ]
        next_results_response_for_ticket_1_detail_2 = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": available_results_for_ticket_1_detail_2,
            },
            'status': 200,
        }

        available_results_for_ticket_2_detail_1 = [
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
        ]
        next_results_response_for_ticket_2_detail_1 = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": available_results_for_ticket_2_detail_1,
            },
            'status': 200,
        }

        filtered_predictions_for_ticket_1_detail_1 = [
            prediction_object_for_ticket_1_detail_1_predictions_list_item_1,
        ]
        filtered_predictions_for_ticket_1_detail_2 = [
            prediction_object_for_ticket_1_detail_2_predictions_list_item_1,
        ]
        filtered_predictions_for_ticket_2_detail_1 = [
            prediction_object_for_ticket_2_detail_1_predictions_list_item_2,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        notifications_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(side_effect=[
            ticket_1_note_1,
            ticket_1_note_3,
            ticket_2_note_1,
        ])
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)
        ticket_repository.build_tnba_note_from_prediction = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(side_effect=[
            prediction_object_for_ticket_1_detail_1,
            prediction_object_for_ticket_1_detail_2,
            prediction_object_for_ticket_2_detail_1,
        ])
        prediction_repository.filter_predictions_in_next_results = Mock(side_effect=[
            filtered_predictions_for_ticket_1_detail_1,
            filtered_predictions_for_ticket_1_detail_2,
            filtered_predictions_for_ticket_2_detail_1,
        ])
        prediction_repository.get_best_prediction = Mock(side_effect=[
            prediction_object_for_ticket_1_detail_1_predictions_list_item_1,
            prediction_object_for_ticket_1_detail_2_predictions_list_item_1,
            prediction_object_for_ticket_2_detail_1_predictions_list_item_2,
        ])
        prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note = Mock(return_value=False)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(side_effect=[
            next_results_response_for_ticket_1_detail_1,
            next_results_response_for_ticket_1_detail_2,
            next_results_response_for_ticket_2_detail_1,
        ])
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_for_ticket_1_response,
            t7_prediction_for_ticket_2_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        await tnba_monitor._process_tickets_with_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        ticket_repository.find_newest_tnba_note_by_service_number.assert_has_calls([
            call(ticket_1_notes, ticket_1_detail_1_serial_number),
            call(ticket_1_notes, ticket_1_detail_2_serial_number),
            call(ticket_2_notes, ticket_2_detail_1_serial_number),
        ])
        ticket_repository.is_tnba_note_old_enough.assert_has_calls([
            call(ticket_1_note_1),
            call(ticket_1_note_3),
            call(ticket_2_note_1),
        ])
        prediction_repository.find_prediction_object_by_serial.assert_has_calls([
            call(predictions_for_ticket_1, ticket_1_detail_1_serial_number),
            call(predictions_for_ticket_1, ticket_1_detail_2_serial_number),
            call(predictions_for_ticket_2, ticket_2_detail_1_serial_number),
        ])
        bruin_repository.get_next_results_for_ticket_detail.assert_has_awaits([
            call(ticket_1_id, ticket_1_detail_1_id, ticket_1_detail_1_serial_number),
            call(ticket_1_id, ticket_1_detail_2_id, ticket_1_detail_2_serial_number),
            call(ticket_2_id, ticket_2_detail_1_id, ticket_2_detail_1_serial_number),
        ])
        prediction_repository.filter_predictions_in_next_results.assert_has_calls([
            call(prediction_object_for_ticket_1_detail_1_predictions_list, available_results_for_ticket_1_detail_1),
            call(prediction_object_for_ticket_1_detail_2_predictions_list, available_results_for_ticket_1_detail_2),
            call(prediction_object_for_ticket_2_detail_1_predictions_list, available_results_for_ticket_2_detail_1),
        ])
        prediction_repository.get_best_prediction.assert_has_calls([
            call(filtered_predictions_for_ticket_1_detail_1),
            call(filtered_predictions_for_ticket_1_detail_2),
            call(filtered_predictions_for_ticket_2_detail_1),
        ])
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_with_tnba_with_changes_since_last_prediction_and_dev_env_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_1_serial_number,
            ],
        }
        ticket_1_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                'VC0000000',
            ],
        }
        ticket_1_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_2_serial_number,
            ],
        }
        ticket_1_notes = [
            ticket_1_note_1,
            ticket_1_note_2,
            ticket_1_note_3,
        ]
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': ticket_1_notes,
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_2_notes = [
            ticket_2_note_1,
        ]
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': ticket_2_notes,
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        prediction_object_for_ticket_1_detail_1_predictions_list_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        prediction_object_for_ticket_1_detail_1_predictions_list_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        prediction_object_for_ticket_1_detail_1_predictions_list = [
            prediction_object_for_ticket_1_detail_1_predictions_list_item_1,
            prediction_object_for_ticket_1_detail_1_predictions_list_item_2,
        ]
        prediction_object_for_ticket_1_detail_1 = {
            'assetId': ticket_1_detail_1_serial_number,
            'predictions': prediction_object_for_ticket_1_detail_1_predictions_list,
        }
        prediction_object_for_ticket_1_detail_2_predictions_list_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        prediction_object_for_ticket_1_detail_2_predictions_list_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        prediction_object_for_ticket_1_detail_2_predictions_list = [
            prediction_object_for_ticket_1_detail_2_predictions_list_item_1,
            prediction_object_for_ticket_1_detail_2_predictions_list_item_2,
        ]
        prediction_object_for_ticket_1_detail_2 = {
            'assetId': ticket_1_detail_2_serial_number,
            'predictions': prediction_object_for_ticket_1_detail_2_predictions_list,
        }
        predictions_for_ticket_1 = [
            prediction_object_for_ticket_1_detail_1,
            prediction_object_for_ticket_1_detail_2,
        ]
        t7_prediction_for_ticket_1_response = {
            'body': predictions_for_ticket_1,
            'status': 200
        }

        prediction_object_for_ticket_2_detail_1_predictions_list_item_1 = {
            'name': 'Request Completed',
            'probability': 0.1111111111111111
        }
        prediction_object_for_ticket_2_detail_1_predictions_list_item_2 = {
            'name': 'No Trouble Found - Carrier Issue',
            'probability': 0.2222222222222222
        }
        prediction_object_for_ticket_2_detail_1_predictions_list = [
            prediction_object_for_ticket_2_detail_1_predictions_list_item_1,
            prediction_object_for_ticket_2_detail_1_predictions_list_item_2,
        ]
        prediction_object_for_ticket_2_detail_1 = {
            'assetId': ticket_2_detail_1_serial_number,
            'predictions': prediction_object_for_ticket_2_detail_1_predictions_list,
        }
        predictions_for_ticket_2 = [
            prediction_object_for_ticket_2_detail_1,
        ]
        t7_prediction_for_ticket_2_response = {
            'body': predictions_for_ticket_2,
            'status': 200
        }

        available_results_for_ticket_1_detail_1 = [
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
        ]
        next_results_response_for_ticket_1_detail_1 = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": available_results_for_ticket_1_detail_1,
            },
            'status': 200,
        }

        available_results_for_ticket_1_detail_2 = [
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
        ]
        next_results_response_for_ticket_1_detail_2 = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": available_results_for_ticket_1_detail_2,
            },
            'status': 200,
        }

        available_results_for_ticket_2_detail_1 = [
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
        ]
        next_results_response_for_ticket_2_detail_1 = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": available_results_for_ticket_2_detail_1,
            },
            'status': 200,
        }

        filtered_predictions_for_ticket_1_detail_1 = [
            prediction_object_for_ticket_1_detail_1_predictions_list_item_1,
        ]
        filtered_predictions_for_ticket_1_detail_2 = [
            prediction_object_for_ticket_1_detail_2_predictions_list_item_1,
        ]
        filtered_predictions_for_ticket_2_detail_1 = [
            prediction_object_for_ticket_2_detail_1_predictions_list_item_2,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(side_effect=[
            ticket_1_note_1,
            ticket_1_note_3,
            ticket_2_note_1,
        ])
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)
        ticket_repository.build_tnba_note_from_prediction = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(side_effect=[
            prediction_object_for_ticket_1_detail_1,
            prediction_object_for_ticket_1_detail_2,
            prediction_object_for_ticket_2_detail_1,
        ])
        prediction_repository.filter_predictions_in_next_results = Mock(side_effect=[
            filtered_predictions_for_ticket_1_detail_1,
            filtered_predictions_for_ticket_1_detail_2,
            filtered_predictions_for_ticket_2_detail_1,
        ])
        prediction_repository.get_best_prediction = Mock(side_effect=[
            prediction_object_for_ticket_1_detail_1_predictions_list_item_1,
            prediction_object_for_ticket_1_detail_2_predictions_list_item_1,
            prediction_object_for_ticket_2_detail_1_predictions_list_item_2,
        ])
        prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note = Mock(return_value=True)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(side_effect=[
            next_results_response_for_ticket_1_detail_1,
            next_results_response_for_ticket_1_detail_2,
            next_results_response_for_ticket_2_detail_1,
        ])
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_for_ticket_1_response,
            t7_prediction_for_ticket_2_response,
        ])

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        with patch.object(config, 'ENVIRONMENT', "dev"):
            await tnba_monitor._process_tickets_with_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        ticket_repository.find_newest_tnba_note_by_service_number.assert_has_calls([
            call(ticket_1_notes, ticket_1_detail_1_serial_number),
            call(ticket_1_notes, ticket_1_detail_2_serial_number),
            call(ticket_2_notes, ticket_2_detail_1_serial_number),
        ])
        ticket_repository.is_tnba_note_old_enough.assert_has_calls([
            call(ticket_1_note_1),
            call(ticket_1_note_3),
            call(ticket_2_note_1),
        ])
        prediction_repository.find_prediction_object_by_serial.assert_has_calls([
            call(predictions_for_ticket_1, ticket_1_detail_1_serial_number),
            call(predictions_for_ticket_1, ticket_1_detail_2_serial_number),
            call(predictions_for_ticket_2, ticket_2_detail_1_serial_number),
        ])
        bruin_repository.get_next_results_for_ticket_detail.assert_has_awaits([
            call(ticket_1_id, ticket_1_detail_1_id, ticket_1_detail_1_serial_number),
            call(ticket_1_id, ticket_1_detail_2_id, ticket_1_detail_2_serial_number),
            call(ticket_2_id, ticket_2_detail_1_id, ticket_2_detail_1_serial_number),
        ])
        prediction_repository.filter_predictions_in_next_results.assert_has_calls([
            call(prediction_object_for_ticket_1_detail_1_predictions_list, available_results_for_ticket_1_detail_1),
            call(prediction_object_for_ticket_1_detail_2_predictions_list, available_results_for_ticket_1_detail_2),
            call(prediction_object_for_ticket_2_detail_1_predictions_list, available_results_for_ticket_2_detail_1),
        ])
        prediction_repository.get_best_prediction.assert_has_calls([
            call(filtered_predictions_for_ticket_1_detail_1),
            call(filtered_predictions_for_ticket_1_detail_2),
            call(filtered_predictions_for_ticket_2_detail_1),
        ])
        ticket_repository.build_tnba_note_from_prediction.assert_has_calls([
            call(prediction_object_for_ticket_1_detail_1_predictions_list_item_1),
            call(prediction_object_for_ticket_1_detail_2_predictions_list_item_1),
            call(prediction_object_for_ticket_2_detail_1_predictions_list_item_2),
        ])
        assert notifications_repository.send_slack_message.await_count == 3
        bruin_repository.append_multiple_notes_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_with_tnba_with_append_multiple_notes_returning_non_2xx_status_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_1_serial_number,
            ],
        }
        ticket_1_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                'VC0000000',
            ],
        }
        ticket_1_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_2_serial_number,
            ],
        }
        ticket_1_notes = [
            ticket_1_note_1,
            ticket_1_note_2,
            ticket_1_note_3,
        ]
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': ticket_1_notes,
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_2_notes = [
            ticket_2_note_1,
        ]
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': ticket_2_notes,
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        prediction_object_for_ticket_1_detail_1_predictions_list_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        prediction_object_for_ticket_1_detail_1_predictions_list_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        prediction_object_for_ticket_1_detail_1_predictions_list = [
            prediction_object_for_ticket_1_detail_1_predictions_list_item_1,
            prediction_object_for_ticket_1_detail_1_predictions_list_item_2,
        ]
        prediction_object_for_ticket_1_detail_1 = {
            'assetId': ticket_1_detail_1_serial_number,
            'predictions': prediction_object_for_ticket_1_detail_1_predictions_list,
        }
        prediction_object_for_ticket_1_detail_2_predictions_list_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        prediction_object_for_ticket_1_detail_2_predictions_list_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        prediction_object_for_ticket_1_detail_2_predictions_list = [
            prediction_object_for_ticket_1_detail_2_predictions_list_item_1,
            prediction_object_for_ticket_1_detail_2_predictions_list_item_2,
        ]
        prediction_object_for_ticket_1_detail_2 = {
            'assetId': ticket_1_detail_2_serial_number,
            'predictions': prediction_object_for_ticket_1_detail_2_predictions_list,
        }
        predictions_for_ticket_1 = [
            prediction_object_for_ticket_1_detail_1,
            prediction_object_for_ticket_1_detail_2,
        ]
        t7_prediction_for_ticket_1_response = {
            'body': predictions_for_ticket_1,
            'status': 200
        }

        prediction_object_for_ticket_2_detail_1_predictions_list_item_1 = {
            'name': 'Request Completed',
            'probability': 0.1111111111111111
        }
        prediction_object_for_ticket_2_detail_1_predictions_list_item_2 = {
            'name': 'No Trouble Found - Carrier Issue',
            'probability': 0.2222222222222222
        }
        prediction_object_for_ticket_2_detail_1_predictions_list = [
            prediction_object_for_ticket_2_detail_1_predictions_list_item_1,
            prediction_object_for_ticket_2_detail_1_predictions_list_item_2,
        ]
        prediction_object_for_ticket_2_detail_1 = {
            'assetId': ticket_2_detail_1_serial_number,
            'predictions': prediction_object_for_ticket_2_detail_1_predictions_list,
        }
        predictions_for_ticket_2 = [
            prediction_object_for_ticket_2_detail_1,
        ]
        t7_prediction_for_ticket_2_response = {
            'body': predictions_for_ticket_2,
            'status': 200
        }

        available_results_for_ticket_1_detail_1 = [
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
        ]
        next_results_response_for_ticket_1_detail_1 = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": available_results_for_ticket_1_detail_1,
            },
            'status': 200,
        }

        available_results_for_ticket_1_detail_2 = [
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
        ]
        next_results_response_for_ticket_1_detail_2 = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": available_results_for_ticket_1_detail_2,
            },
            'status': 200,
        }

        available_results_for_ticket_2_detail_1 = [
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
        ]
        next_results_response_for_ticket_2_detail_1 = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": available_results_for_ticket_2_detail_1,
            },
            'status': 200,
        }

        filtered_predictions_for_ticket_1_detail_1 = [
            prediction_object_for_ticket_1_detail_1_predictions_list_item_1,
        ]
        filtered_predictions_for_ticket_1_detail_2 = [
            prediction_object_for_ticket_1_detail_2_predictions_list_item_1,
        ]
        filtered_predictions_for_ticket_2_detail_1 = [
            prediction_object_for_ticket_2_detail_1_predictions_list_item_2,
        ]

        tnba_note_for_ticket_1_detail_1 = 'This is TNBA note 1'
        tnba_note_for_ticket_1_detail_2 = 'This is TNBA note 2'
        tnba_note_for_ticket_2_detail_1 = 'This is TNBA note 3'

        append_multiple_notes_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(side_effect=[
            ticket_1_note_1,
            ticket_1_note_3,
            ticket_2_note_1,
        ])
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)
        ticket_repository.build_tnba_note_from_prediction = Mock(side_effect=[
            tnba_note_for_ticket_1_detail_1,
            tnba_note_for_ticket_1_detail_2,
            tnba_note_for_ticket_2_detail_1,
        ])

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(side_effect=[
            prediction_object_for_ticket_1_detail_1,
            prediction_object_for_ticket_1_detail_2,
            prediction_object_for_ticket_2_detail_1,
        ])
        prediction_repository.filter_predictions_in_next_results = Mock(side_effect=[
            filtered_predictions_for_ticket_1_detail_1,
            filtered_predictions_for_ticket_1_detail_2,
            filtered_predictions_for_ticket_2_detail_1,
        ])
        prediction_repository.get_best_prediction = Mock(side_effect=[
            prediction_object_for_ticket_1_detail_1_predictions_list_item_1,
            prediction_object_for_ticket_1_detail_2_predictions_list_item_1,
            prediction_object_for_ticket_2_detail_1_predictions_list_item_2,
        ])
        prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note = Mock(return_value=True)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(side_effect=[
            next_results_response_for_ticket_1_detail_1,
            next_results_response_for_ticket_1_detail_2,
            next_results_response_for_ticket_2_detail_1,
        ])
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock(return_value=append_multiple_notes_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_for_ticket_1_response,
            t7_prediction_for_ticket_2_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        with patch.object(config, 'ENVIRONMENT', "production"):
            await tnba_monitor._process_tickets_with_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        ticket_repository.find_newest_tnba_note_by_service_number.assert_has_calls([
            call(ticket_1_notes, ticket_1_detail_1_serial_number),
            call(ticket_1_notes, ticket_1_detail_2_serial_number),
            call(ticket_2_notes, ticket_2_detail_1_serial_number),
        ])
        ticket_repository.is_tnba_note_old_enough.assert_has_calls([
            call(ticket_1_note_1),
            call(ticket_1_note_3),
            call(ticket_2_note_1),
        ])
        prediction_repository.find_prediction_object_by_serial.assert_has_calls([
            call(predictions_for_ticket_1, ticket_1_detail_1_serial_number),
            call(predictions_for_ticket_1, ticket_1_detail_2_serial_number),
            call(predictions_for_ticket_2, ticket_2_detail_1_serial_number),
        ])
        bruin_repository.get_next_results_for_ticket_detail.assert_has_awaits([
            call(ticket_1_id, ticket_1_detail_1_id, ticket_1_detail_1_serial_number),
            call(ticket_1_id, ticket_1_detail_2_id, ticket_1_detail_2_serial_number),
            call(ticket_2_id, ticket_2_detail_1_id, ticket_2_detail_1_serial_number),
        ])
        prediction_repository.filter_predictions_in_next_results.assert_has_calls([
            call(prediction_object_for_ticket_1_detail_1_predictions_list, available_results_for_ticket_1_detail_1),
            call(prediction_object_for_ticket_1_detail_2_predictions_list, available_results_for_ticket_1_detail_2),
            call(prediction_object_for_ticket_2_detail_1_predictions_list, available_results_for_ticket_2_detail_1),
        ])
        prediction_repository.get_best_prediction.assert_has_calls([
            call(filtered_predictions_for_ticket_1_detail_1),
            call(filtered_predictions_for_ticket_1_detail_2),
            call(filtered_predictions_for_ticket_2_detail_1),
        ])
        ticket_repository.build_tnba_note_from_prediction.assert_has_calls([
            call(prediction_object_for_ticket_1_detail_1_predictions_list_item_1),
            call(prediction_object_for_ticket_1_detail_2_predictions_list_item_1),
            call(prediction_object_for_ticket_2_detail_1_predictions_list_item_2),
        ])
        bruin_repository.append_multiple_notes_to_ticket.assert_has_awaits([
            call(
                ticket_1_id,
                [
                    {
                        'text': tnba_note_for_ticket_1_detail_1,
                        'detail_id': ticket_1_detail_1_id,
                        'service_number': ticket_1_detail_1_serial_number,
                    },
                    {
                        'text': tnba_note_for_ticket_1_detail_2,
                        'detail_id': ticket_1_detail_2_id,
                        'service_number': ticket_1_detail_2_serial_number,
                    },
                ],
            ),
            call(
                ticket_2_id,
                [
                    {
                        'text': tnba_note_for_ticket_2_detail_1,
                        'detail_id': ticket_2_detail_1_id,
                        'service_number': ticket_2_detail_1_serial_number,
                    },
                ],
            ),
        ])
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_with_tnba_with_all_conditions_met_for_appending_tnba_note_test(self):
        ticket_1_id = 12345
        ticket_1_detail_1_id = 2746930
        ticket_1_detail_1_serial_number = 'VC1234567'
        ticket_1_detail_2_id = 2746931
        ticket_1_detail_2_serial_number = 'VC9999999'
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_1_serial_number,
            ],
        }
        ticket_1_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                'VC0000000',
            ],
        }
        ticket_1_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                ticket_1_detail_2_serial_number,
            ],
        }
        ticket_1_notes = [
            ticket_1_note_1,
            ticket_1_note_2,
            ticket_1_note_3,
        ]
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                {
                    "detailID": ticket_1_detail_1_id,
                    "detailValue": ticket_1_detail_1_serial_number,
                },
                {
                    "detailID": ticket_1_detail_2_id,
                    "detailValue": ticket_1_detail_2_serial_number,
                },
            ],
            'ticket_notes': ticket_1_notes,
        }

        ticket_2_id = 67890
        ticket_2_detail_1_id = 2746930
        ticket_2_detail_1_serial_number = 'VC1111222'
        ticket_2_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_2_notes = [
            ticket_2_note_1,
        ]
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                {
                    "detailID": ticket_2_detail_1_id,
                    "detailValue": ticket_2_detail_1_serial_number,
                },
            ],
            'ticket_notes': ticket_2_notes,
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        prediction_object_for_ticket_1_detail_1_predictions_list_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        prediction_object_for_ticket_1_detail_1_predictions_list_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        prediction_object_for_ticket_1_detail_1_predictions_list = [
            prediction_object_for_ticket_1_detail_1_predictions_list_item_1,
            prediction_object_for_ticket_1_detail_1_predictions_list_item_2,
        ]
        prediction_object_for_ticket_1_detail_1 = {
            'assetId': ticket_1_detail_1_serial_number,
            'predictions': prediction_object_for_ticket_1_detail_1_predictions_list,
        }
        prediction_object_for_ticket_1_detail_2_predictions_list_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        prediction_object_for_ticket_1_detail_2_predictions_list_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        prediction_object_for_ticket_1_detail_2_predictions_list = [
            prediction_object_for_ticket_1_detail_2_predictions_list_item_1,
            prediction_object_for_ticket_1_detail_2_predictions_list_item_2,
        ]
        prediction_object_for_ticket_1_detail_2 = {
            'assetId': ticket_1_detail_2_serial_number,
            'predictions': prediction_object_for_ticket_1_detail_2_predictions_list,
        }
        predictions_for_ticket_1 = [
            prediction_object_for_ticket_1_detail_1,
            prediction_object_for_ticket_1_detail_2,
        ]
        t7_prediction_for_ticket_1_response = {
            'body': predictions_for_ticket_1,
            'status': 200
        }

        prediction_object_for_ticket_2_detail_1_predictions_list_item_1 = {
            'name': 'Request Completed',
            'probability': 0.1111111111111111
        }
        prediction_object_for_ticket_2_detail_1_predictions_list_item_2 = {
            'name': 'No Trouble Found - Carrier Issue',
            'probability': 0.2222222222222222
        }
        prediction_object_for_ticket_2_detail_1_predictions_list = [
            prediction_object_for_ticket_2_detail_1_predictions_list_item_1,
            prediction_object_for_ticket_2_detail_1_predictions_list_item_2,
        ]
        prediction_object_for_ticket_2_detail_1 = {
            'assetId': ticket_2_detail_1_serial_number,
            'predictions': prediction_object_for_ticket_2_detail_1_predictions_list,
        }
        predictions_for_ticket_2 = [
            prediction_object_for_ticket_2_detail_1,
        ]
        t7_prediction_for_ticket_2_response = {
            'body': predictions_for_ticket_2,
            'status': 200
        }

        available_results_for_ticket_1_detail_1 = [
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
        ]
        next_results_response_for_ticket_1_detail_1 = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": available_results_for_ticket_1_detail_1,
            },
            'status': 200,
        }

        available_results_for_ticket_1_detail_2 = [
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
        ]
        next_results_response_for_ticket_1_detail_2 = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": available_results_for_ticket_1_detail_2,
            },
            'status': 200,
        }

        available_results_for_ticket_2_detail_1 = [
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
        ]
        next_results_response_for_ticket_2_detail_1 = {
            'body': {
                "currentTaskId": 10683187,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": available_results_for_ticket_2_detail_1,
            },
            'status': 200,
        }

        filtered_predictions_for_ticket_1_detail_1 = [
            prediction_object_for_ticket_1_detail_1_predictions_list_item_1,
        ]
        filtered_predictions_for_ticket_1_detail_2 = [
            prediction_object_for_ticket_1_detail_2_predictions_list_item_1,
        ]
        filtered_predictions_for_ticket_2_detail_1 = [
            prediction_object_for_ticket_2_detail_1_predictions_list_item_2,
        ]

        tnba_note_for_ticket_1_detail_1 = 'This is TNBA note 1'
        tnba_note_for_ticket_1_detail_2 = 'This is TNBA note 2'
        tnba_note_for_ticket_2_detail_1 = 'This is TNBA note 3'

        append_multiple_notes_response = {
            'body': 'ok',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note_by_service_number = Mock(side_effect=[
            ticket_1_note_1,
            ticket_1_note_3,
            ticket_2_note_1,
        ])
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)
        ticket_repository.build_tnba_note_from_prediction = Mock(side_effect=[
            tnba_note_for_ticket_1_detail_1,
            tnba_note_for_ticket_1_detail_2,
            tnba_note_for_ticket_2_detail_1,
        ])

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(side_effect=[
            prediction_object_for_ticket_1_detail_1,
            prediction_object_for_ticket_1_detail_2,
            prediction_object_for_ticket_2_detail_1,
        ])
        prediction_repository.filter_predictions_in_next_results = Mock(side_effect=[
            filtered_predictions_for_ticket_1_detail_1,
            filtered_predictions_for_ticket_1_detail_2,
            filtered_predictions_for_ticket_2_detail_1,
        ])
        prediction_repository.get_best_prediction = Mock(side_effect=[
            prediction_object_for_ticket_1_detail_1_predictions_list_item_1,
            prediction_object_for_ticket_1_detail_2_predictions_list_item_1,
            prediction_object_for_ticket_2_detail_1_predictions_list_item_2,
        ])
        prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note = Mock(return_value=True)

        bruin_repository = Mock()
        bruin_repository.get_next_results_for_ticket_detail = CoroutineMock(side_effect=[
            next_results_response_for_ticket_1_detail_1,
            next_results_response_for_ticket_1_detail_2,
            next_results_response_for_ticket_2_detail_1,
        ])
        bruin_repository.append_multiple_notes_to_ticket = CoroutineMock(return_value=append_multiple_notes_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(side_effect=[
            t7_prediction_for_ticket_1_response,
            t7_prediction_for_ticket_2_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository, notifications_repository)

        with patch.object(config, 'ENVIRONMENT', "production"):
            await tnba_monitor._process_tickets_with_tnba(tickets)

        t7_repository.get_prediction.assert_has_awaits([
            call(ticket_1_id),
            call(ticket_2_id),
        ])
        ticket_repository.find_newest_tnba_note_by_service_number.assert_has_calls([
            call(ticket_1_notes, ticket_1_detail_1_serial_number),
            call(ticket_1_notes, ticket_1_detail_2_serial_number),
            call(ticket_2_notes, ticket_2_detail_1_serial_number),
        ])
        ticket_repository.is_tnba_note_old_enough.assert_has_calls([
            call(ticket_1_note_1),
            call(ticket_1_note_3),
            call(ticket_2_note_1),
        ])
        prediction_repository.find_prediction_object_by_serial.assert_has_calls([
            call(predictions_for_ticket_1, ticket_1_detail_1_serial_number),
            call(predictions_for_ticket_1, ticket_1_detail_2_serial_number),
            call(predictions_for_ticket_2, ticket_2_detail_1_serial_number),
        ])
        bruin_repository.get_next_results_for_ticket_detail.assert_has_awaits([
            call(ticket_1_id, ticket_1_detail_1_id, ticket_1_detail_1_serial_number),
            call(ticket_1_id, ticket_1_detail_2_id, ticket_1_detail_2_serial_number),
            call(ticket_2_id, ticket_2_detail_1_id, ticket_2_detail_1_serial_number),
        ])
        prediction_repository.filter_predictions_in_next_results.assert_has_calls([
            call(prediction_object_for_ticket_1_detail_1_predictions_list, available_results_for_ticket_1_detail_1),
            call(prediction_object_for_ticket_1_detail_2_predictions_list, available_results_for_ticket_1_detail_2),
            call(prediction_object_for_ticket_2_detail_1_predictions_list, available_results_for_ticket_2_detail_1),
        ])
        prediction_repository.get_best_prediction.assert_has_calls([
            call(filtered_predictions_for_ticket_1_detail_1),
            call(filtered_predictions_for_ticket_1_detail_2),
            call(filtered_predictions_for_ticket_2_detail_1),
        ])
        ticket_repository.build_tnba_note_from_prediction.assert_has_calls([
            call(prediction_object_for_ticket_1_detail_1_predictions_list_item_1),
            call(prediction_object_for_ticket_1_detail_2_predictions_list_item_1),
            call(prediction_object_for_ticket_2_detail_1_predictions_list_item_2),
        ])
        bruin_repository.append_multiple_notes_to_ticket.assert_has_awaits([
            call(
                ticket_1_id,
                [
                    {
                        'text': tnba_note_for_ticket_1_detail_1,
                        'detail_id': ticket_1_detail_1_id,
                        'service_number': ticket_1_detail_1_serial_number,
                    },
                    {
                        'text': tnba_note_for_ticket_1_detail_2,
                        'detail_id': ticket_1_detail_2_id,
                        'service_number': ticket_1_detail_2_serial_number,
                    },
                ],
            ),
            call(
                ticket_2_id,
                [
                    {
                        'text': tnba_note_for_ticket_2_detail_1,
                        'detail_id': ticket_2_detail_1_id,
                        'service_number': ticket_2_detail_1_serial_number,
                    },
                ],
            ),
        ])
        assert notifications_repository.send_slack_message.await_count == 2
