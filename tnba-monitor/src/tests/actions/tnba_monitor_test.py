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

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)

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

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            with patch.object(tnba_monitor_module, 'timezone', new=Mock()):
                await tnba_monitor.start_tnba_automated_process(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            tnba_monitor._tnba_automated_process, 'interval',
            seconds=config.MONITORING_INTERVAL_SECONDS,
            next_run_time=next_run_time,
            replace_existing=False,
            id='_tnba_automated_process',
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

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)

        await tnba_monitor.start_tnba_automated_process(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            tnba_monitor._tnba_automated_process, 'interval',
            seconds=config.MONITORING_INTERVAL_SECONDS,
            next_run_time=undefined,
            replace_existing=False,
            id='_tnba_automated_process',
        )

    @pytest.mark.asyncio
    async def tnba_automated_process_with_filled_cache_test(self):
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

        ticket_1 = {
            'ticket_id': 12345,
            'ticket_detail': {
                "detailID": 2746930,
                "detailValue": edge_1_serial,
            },
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ],
        }
        ticket_2 = {
            'ticket_id': 67890,
            'ticket_detail': {
                "detailID": 2746931,
                "detailValue": edge_2_serial,
            },
            'ticket_notes': [
                {
                    "noteId": 41894041,
                    "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ],
        }
        ticket_3 = {
            'ticket_id': 11111,
            'ticket_detail': {
                "detailID": 2746932,
                "detailValue": edge_3_serial,
            },
            'ticket_note': {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        }
        relevant_tickets = [ticket_1, ticket_2, ticket_3]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()

        monitoring_map_repository = Mock()
        monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses = CoroutineMock()
        monitoring_map_repository.get_monitoring_map_cache = Mock(return_value=monitoring_mapping)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)
        tnba_monitor._monitoring_mapping = {'obsolete': 'data'}
        tnba_monitor._get_relevant_tickets = CoroutineMock(return_value=relevant_tickets)
        tnba_monitor._process_ticket = CoroutineMock()

        await tnba_monitor._tnba_automated_process()

        monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses.assert_not_awaited()
        tnba_monitor._get_relevant_tickets.assert_awaited_once()
        tnba_monitor._process_ticket.assert_has_awaits([
            call(ticket_1),
            call(ticket_2),
            call(ticket_3),
        ])

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

        ticket_1 = {
            'ticket_id': 12345,
            'ticket_detail': {
                "detailID": 2746930,
                "detailValue": edge_1_serial,
            },
            'ticket_notes': {
                "noteId": 41894040,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        }
        ticket_2 = {
            'ticket_id': 67890,
            'ticket_detail': {
                "detailID": 2746931,
                "detailValue": edge_2_serial,
            },
            'ticket_notes': {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        }
        ticket_3 = {
            'ticket_id': 11111,
            'ticket_detail': {
                "detailID": 2746932,
                "detailValue": edge_3_serial,
            },
            'ticket_notes': {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        }
        relevant_tickets = [ticket_1, ticket_2, ticket_3]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        t7_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        prediction_repository = Mock()

        monitoring_map_repository = Mock()
        monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses = CoroutineMock()
        monitoring_map_repository.start_create_monitoring_map_job = CoroutineMock()
        monitoring_map_repository.get_monitoring_map_cache = Mock(return_value=monitoring_mapping)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)
        tnba_monitor._get_relevant_tickets = CoroutineMock(return_value=relevant_tickets)
        tnba_monitor._process_ticket = CoroutineMock()

        await tnba_monitor._tnba_automated_process()

        monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses.assert_awaited_once()
        monitoring_map_repository.start_create_monitoring_map_job.assert_awaited_once()
        tnba_monitor._get_relevant_tickets.assert_awaited_once()
        tnba_monitor._process_ticket.assert_has_awaits([
            call(ticket_1),
            call(ticket_2),
            call(ticket_3),
        ])

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

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)

        await tnba_monitor.start_tnba_automated_process(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            tnba_monitor._tnba_automated_process, 'interval',
            seconds=config.MONITORING_INTERVAL_SECONDS,
            next_run_time=undefined,
            replace_existing=False,
            id='_tnba_automated_process',
        )

    @pytest.mark.asyncio
    async def get_relevant_tickets_test(self):
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

        open_tickets_with_details = [
            ticket_with_details_1_for_bruin_client_1,
            ticket_with_details_2_for_bruin_client_1,
            ticket_with_details_1_for_bruin_client_2,
        ]
        relevant_open_tickets = [
            ticket_with_details_1_for_bruin_client_1,
            ticket_with_details_1_for_bruin_client_2,
        ]

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

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)
        tnba_monitor._get_all_open_tickets_with_details_for_monitored_companies = CoroutineMock(
            return_value=open_tickets_with_details)
        tnba_monitor._filter_tickets_related_to_edges_under_monitoring = Mock(return_value=relevant_open_tickets)

        result = await tnba_monitor._get_relevant_tickets()

        tnba_monitor._get_all_open_tickets_with_details_for_monitored_companies.assert_awaited_once()
        tnba_monitor._filter_tickets_related_to_edges_under_monitoring.assert_called_once_with(
            open_tickets_with_details
        )
        assert result == relevant_open_tickets

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

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)
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

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)
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
                                   prediction_repository)

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id)
        ])

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_detail': outage_ticket_1_details_item_1,
                'ticket_notes': outage_ticket_1_notes,
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_detail': outage_ticket_2_details_item_1,
                'ticket_notes': outage_ticket_2_notes,
            },
            {
                'ticket_id': ticket_3_id,
                'ticket_detail': affecting_ticket_1_details_item_1,
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

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)

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
                'ticket_detail': affecting_ticket_1_details_item_1,
                'ticket_notes': affecting_ticket_1_notes,
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_detail': affecting_ticket_2_details_item_1,
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

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)

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
                'ticket_detail': outage_ticket_1_details_item_1,
                'ticket_notes': outage_ticket_1_notes,
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_detail': outage_ticket_2_details_item_1,
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
                                   prediction_repository)

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id)
        ])

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_detail': outage_ticket_1_details_item_1,
                'ticket_notes': outage_ticket_1_notes,
            },
            {
                'ticket_id': ticket_3_id,
                'ticket_detail': affecting_ticket_1_details_item_1,
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
                                   prediction_repository)

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id)
        ])

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_detail': outage_ticket_1_details_item_1,
                'ticket_notes': outage_ticket_1_notes,
            },
            {
                'ticket_id': ticket_3_id,
                'ticket_detail': affecting_ticket_1_details_item_1,
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
        edge_4_data = {'edge_id': edge_4_full_id, 'edge_status': edge_4_status}
        edge_5_data = {'edge_id': edge_5_full_id, 'edge_status': edge_5_status}

        monitoring_mapping = {
            bruin_client_1_id: {
                edge_1_serial: edge_1_data,
                edge_2_serial: edge_2_data,
            },
            bruin_client_2_id: {
                edge_4_serial: edge_4_data,
                edge_5_serial: edge_5_data,
            }
        }

        ticket_1 = {
            'ticket_id': 12345,
            'ticket_detail': {
                "detailID": 2746930,
                "detailValue": edge_1_serial,
            },
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ]
        }
        ticket_2 = {
            'ticket_id': 67890,
            'ticket_detail': {
                "detailID": 2746931,
                "detailValue": edge_3_serial,
            },
            'ticket_notes': [
                {
                    "noteId": 41894041,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ]
        }
        ticket_3 = {
            'ticket_id': 11111,
            'ticket_detail': {
                "detailID": 2746932,
                "detailValue": edge_5_serial,
            },
            'ticket_notes': [
                {
                    "noteId": 41894042,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ]
        }
        tickets = [ticket_1, ticket_2, ticket_3]

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

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)
        tnba_monitor._monitoring_mapping = monitoring_mapping

        result = tnba_monitor._filter_tickets_related_to_edges_under_monitoring(tickets)

        expected = [ticket_1, ticket_3]
        assert result == expected

    @pytest.mark.asyncio
    async def process_ticket_with_no_tnba_note_found_and_retrieval_of_prediction_returning_non_2xx_status_test(
            self):
        ticket_id = 12345
        ticket = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                "detailID": 2746930,
                "detailValue": 'VC1234567',
            },
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
                    "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ]
        }
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

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note = Mock(return_value=None)
        ticket_repository.build_tnba_note_from_prediction = Mock()

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(return_value=t7_prediction_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)

        await tnba_monitor._process_ticket(ticket)

        t7_repository.get_prediction.assert_awaited_once_with(ticket_id)
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_ticket_test_with_no_tnba_note_found_and_no_prediction_found_for_target_serial_test(
            self):
        ticket_id = 12345
        ticket = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                "detailID": 2746930,
                "detailValue": 'VC1234567',
            },
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
                    "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ]
        }
        t7_prediction_response = {
            'body': [
                {
                    'assetId': 'VC1111222',
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
                }
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
        ticket_repository.find_newest_tnba_note = Mock(return_value=None)

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(return_value=None)

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(return_value=t7_prediction_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)

        await tnba_monitor._process_ticket(ticket)

        t7_repository.get_prediction.assert_awaited_once_with(ticket_id)
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_ticket_test_with_no_tnba_note_found_and_all_conditions_met_for_appending_tnba_note_test(
            self):
        serial_number = 'VC1234567'
        ticket_id = 12345
        ticket = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                "detailID": 2746930,
                "detailValue": serial_number,
            },
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
                    "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ]
        }

        predictions_1_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        predictions_1_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        predictions_1 = [
            predictions_1_item_1,
            predictions_1_item_2,
        ]
        predictions_2 = [
            {
                'name': 'Request Completed',
                'probability': 0.1111111111111111
            },
            {
                'name': 'No Trouble Found - Carrier Issue',
                'probability': 0.2222222222222222
            },
        ]
        prediction_object_1 = {
            'assetId': serial_number,
            'predictions': predictions_1,
        }
        prediction_object_2 = {
            'assetId': 'VC9999999',
            'predictions': predictions_2,
        }

        t7_prediction_response = {
            'body': [
                prediction_object_1,
                prediction_object_2,
            ],
            'status': 200
        }
        tnba_note = 'This is a TNBA note'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note = Mock(return_value=None)
        ticket_repository.build_tnba_note_from_prediction = Mock(return_value=tnba_note)

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(return_value=prediction_object_1)
        prediction_repository.get_best_prediction = Mock(return_value=predictions_1_item_1)

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(return_value=t7_prediction_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)

        await tnba_monitor._process_ticket(ticket)

        t7_repository.get_prediction.assert_awaited_once_with(ticket_id)
        ticket_repository.build_tnba_note_from_prediction.assert_called_once_with(predictions_1_item_1)
        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, tnba_note, is_private=True)

    @pytest.mark.asyncio
    async def process_ticket_test_with_tnba_note_found_and_tnba_note_too_recent_for_a_new_append_test(
            self):
        serial_number = 'VC1234567'
        ticket_id = 12345
        ticket_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                "detailID": 2746930,
                "detailValue": serial_number,
            },
            'ticket_notes': [
                ticket_note_1,
                ticket_note_2,
                ticket_note_3,
            ]
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        prediction_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note = Mock(return_value=ticket_note_1)
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=False)
        ticket_repository.build_tnba_note_from_prediction = Mock()

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)

        await tnba_monitor._process_ticket(ticket)

        t7_repository.get_prediction.assert_not_awaited()
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_ticket_test_with_tnba_note_found_and_retrieval_of_prediction_returning_non_2xx_status_test(
            self):
        serial_number = 'VC1234567'
        ticket_id = 12345
        ticket_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                "detailID": 2746930,
                "detailValue": serial_number,
            },
            'ticket_notes': [
                ticket_note_1,
                ticket_note_2,
                ticket_note_3,
            ]
        }
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

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note = Mock(return_value=ticket_note_1)
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)
        ticket_repository.build_tnba_note_from_prediction = Mock()

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(return_value=t7_prediction_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)

        await tnba_monitor._process_ticket(ticket)

        t7_repository.get_prediction.assert_awaited_once_with(ticket_id)
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_ticket_test_with_tnba_note_found_and_no_prediction_found_for_target_serial_test(
            self):
        ticket_id = 12345
        ticket_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                "detailID": 2746930,
                "detailValue": 'VC1234567',
            },
            'ticket_notes': [
                ticket_note_1,
                ticket_note_2,
                ticket_note_3,
            ]
        }
        t7_prediction_response = {
            'body': [
                {
                    'assetId': 'VC1111222',
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
                }
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
        ticket_repository.find_newest_tnba_note = Mock(return_value=ticket_note_1)
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)
        ticket_repository.build_tnba_note_from_prediction = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(return_value=None)

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(return_value=t7_prediction_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)

        await tnba_monitor._process_ticket(ticket)

        t7_repository.get_prediction.assert_awaited_once_with(ticket_id)
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_ticket_test_with_tnba_note_found_and_no_changes_since_last_prediction_test(self):
        ticket_id = 12345
        serial_number = 'VC1234567'
        ticket_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                "detailID": 2746930,
                "detailValue": serial_number,
            },
            'ticket_notes': [
                ticket_note_1,
                ticket_note_2,
                ticket_note_3,
            ]
        }

        predictions_1_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        predictions_1_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        predictions_1 = [
            predictions_1_item_1,
            predictions_1_item_2,
        ]
        prediction_object_1 = {
            'assetId': serial_number,
            'predictions': predictions_1,
        }
        t7_prediction_response = {
            'body': [
                prediction_object_1,
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
                }
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
        ticket_repository.find_newest_tnba_note = Mock(return_value=ticket_note_1)
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)
        ticket_repository.build_tnba_note_from_prediction = Mock()

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(return_value=prediction_object_1)
        prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note = Mock(return_value=False)

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(return_value=t7_prediction_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)

        await tnba_monitor._process_ticket(ticket)

        t7_repository.get_prediction.assert_awaited_once_with(ticket_id)
        ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        bruin_repository.append_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_ticket_test_with_tnba_note_found_and_all_conditions_met_for_appending_tnba_note_test(self):
        ticket_id = 12345
        serial_number = 'VC1234567'
        ticket_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                "detailID": 2746930,
                "detailValue": serial_number,
            },
            'ticket_notes': [
                ticket_note_1,
                ticket_note_2,
                ticket_note_3,
            ]
        }

        predictions_1_item_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        predictions_1_item_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        predictions_1 = [
            predictions_1_item_1,
            predictions_1_item_2,
        ]
        predictions_2 = [
            {
                'name': 'Request Completed',
                'probability': 0.1111111111111111
            },
            {
                'name': 'No Trouble Found - Carrier Issue',
                'probability': 0.2222222222222222
            },
        ]
        prediction_object_1 = {
            'assetId': serial_number,
            'predictions': predictions_1,
        }
        prediction_object_2 = {
            'assetId': 'VC9999999',
            'predictions': predictions_2,
        }

        t7_prediction_response = {
            'body': [
                prediction_object_1,
                prediction_object_2,
            ],
            'status': 200
        }
        tnba_note = 'This is a TNBA note'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        ticket_repository = Mock()
        ticket_repository.find_newest_tnba_note = Mock(return_value=ticket_note_1)
        ticket_repository.is_tnba_note_old_enough = Mock(return_value=True)
        ticket_repository.build_tnba_note_from_prediction = Mock(return_value=tnba_note)

        prediction_repository = Mock()
        prediction_repository.find_prediction_object_by_serial = Mock(return_value=prediction_object_1)
        prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note = Mock(return_value=True)
        prediction_repository.get_best_prediction = Mock(return_value=predictions_1_item_1)

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock()

        t7_repository = Mock()
        t7_repository.get_prediction = CoroutineMock(return_value=t7_prediction_response)

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository,
                                   prediction_repository)

        await tnba_monitor._process_ticket(ticket)

        t7_repository.get_prediction.assert_awaited_once_with(ticket_id)
        ticket_repository.build_tnba_note_from_prediction.assert_called_once_with(predictions_1_item_1)
        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, tnba_note, is_private=True)
