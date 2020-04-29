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
        prediction_repository = Mock()
        ticket_repository = Mock()
        monitoring_map_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, prediction_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository)

        assert tnba_monitor._event_bus is event_bus
        assert tnba_monitor._logger is logger
        assert tnba_monitor._scheduler is scheduler
        assert tnba_monitor._config is config
        assert tnba_monitor._prediction_repository is prediction_repository
        assert tnba_monitor._ticket_repository is ticket_repository
        assert tnba_monitor._monitoring_map_repository is monitoring_map_repository
        assert tnba_monitor._bruin_repository is bruin_repository
        assert tnba_monitor._velocloud_repository is velocloud_repository

        assert tnba_monitor._monitoring_mapping == {}

    @pytest.mark.asyncio
    async def start_tnba_automated_process_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        prediction_repository = Mock()
        ticket_repository = Mock()
        monitoring_map_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, prediction_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository)

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
        prediction_repository = Mock()
        ticket_repository = Mock()
        monitoring_map_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, prediction_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository)

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
        prediction_repository = Mock()
        ticket_repository = Mock()
        monitoring_map_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, prediction_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository)
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
        prediction_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, prediction_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository)
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
        prediction_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, prediction_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository)
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
        prediction_repository = Mock()
        ticket_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
            get_ticket_3_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, prediction_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository)

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
        prediction_repository = Mock()
        ticket_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, prediction_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository)

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
        prediction_repository = Mock()
        ticket_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, prediction_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository)

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
        prediction_repository = Mock()
        ticket_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
            get_ticket_3_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, prediction_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository)

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
        prediction_repository = Mock()
        ticket_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_outage_tickets_response)
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=get_open_affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response,
            get_ticket_2_details_response,
            get_ticket_3_details_response,
        ])

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, prediction_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository)

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
        prediction_repository = Mock()
        ticket_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()

        tnba_monitor = TNBAMonitor(event_bus, logger, scheduler, config, prediction_repository, ticket_repository,
                                   monitoring_map_repository, bruin_repository, velocloud_repository)
        tnba_monitor._monitoring_mapping = monitoring_mapping

        result = tnba_monitor._filter_tickets_related_to_edges_under_monitoring(tickets)

        expected = [ticket_1, ticket_3]
        assert result == expected

    def get_first_element_matching_with_match_test(self):
        payload = range(0, 11)

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = TNBAMonitor._get_first_element_matching(iterable=payload, condition=cond)
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

        result = TNBAMonitor._get_first_element_matching(iterable=payload, condition=cond, fallback=fallback_value)

        assert result == fallback_value
