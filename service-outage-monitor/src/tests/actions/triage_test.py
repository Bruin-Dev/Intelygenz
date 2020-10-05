from datetime import datetime
from datetime import timedelta
from typing import Generator
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest

from apscheduler.util import undefined
from asynctest import CoroutineMock
from dateutil.parser import parse
from shortuuid import uuid

from application.actions.triage import Triage
from application.actions import triage as triage_module
from config import testconfig


class TestTriage:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        customer_cache_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        assert triage._event_bus is event_bus
        assert triage._logger is logger
        assert triage._scheduler is scheduler
        assert triage._config is config
        assert triage._outage_repository is outage_repository
        assert triage._customer_cache_repository is customer_cache_repository
        assert triage._bruin_repository is bruin_repository
        assert triage._velocloud_repository is velocloud_repository
        assert triage._notifications_repository is notifications_repository
        assert triage._triage_repository is triage_repository
        assert triage._metrics_repository is metrics_repository

        assert triage._customer_cache == []

    @pytest.mark.asyncio
    async def start_triage_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        customer_cache_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(triage_module, 'datetime', new=datetime_mock):
            with patch.object(triage_module, 'timezone', new=Mock()):
                await triage.start_triage_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            triage._run_tickets_polling, 'interval',
            minutes=config.TRIAGE_CONFIG["polling_minutes"],
            next_run_time=next_run_time,
            replace_existing=True,
            id='_triage_process',
        )

    @pytest.mark.asyncio
    async def start_triage_job_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        customer_cache_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        await triage.start_triage_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            triage._run_tickets_polling, 'interval',
            minutes=config.TRIAGE_CONFIG["polling_minutes"],
            next_run_time=undefined,
            replace_existing=True,
            id='_triage_process',
        )

    @pytest.mark.asyncio
    async def run_tickets_polling_with_get_cache_request_having_202_status_test(self):
        get_cache_response = {
            'body': None,
            'status': 503,
        }

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

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_triage_monitoring = CoroutineMock(return_value=get_cache_response)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_all_open_tickets_with_details_for_monitored_companies = CoroutineMock()
        triage._process_ticket_details_with_triage = CoroutineMock()
        triage._process_ticket_details_without_triage = CoroutineMock()

        await triage._run_tickets_polling()

        customer_cache_repository.get_cache_for_triage_monitoring.assert_awaited_once()
        triage._get_all_open_tickets_with_details_for_monitored_companies.assert_not_awaited()
        triage._process_ticket_details_with_triage.assert_not_awaited()
        triage._process_ticket_details_without_triage.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_tickets_polling_with_get_cache_request_having_non_2xx_status_and_different_from_202_test(self):
        get_cache_response = {
            'body': 'Cache is still being built for host(s): mettel_velocloud.net, metvco03.mettel.net',
            'status': 202,
        }

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

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_triage_monitoring = CoroutineMock(return_value=get_cache_response)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_all_open_tickets_with_details_for_monitored_companies = CoroutineMock()
        triage._process_ticket_details_with_triage = CoroutineMock()
        triage._process_ticket_details_without_triage = CoroutineMock()

        await triage._run_tickets_polling()

        customer_cache_repository.get_cache_for_triage_monitoring.assert_awaited_once()
        triage._get_all_open_tickets_with_details_for_monitored_companies.assert_not_awaited()
        triage._process_ticket_details_with_triage.assert_not_awaited()
        triage._process_ticket_details_without_triage.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_tickets_polling_with_customer_cache_ready_test(self):
        bruin_client_1 = 12345
        bruin_client_2 = 67890

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'
        edge_4_serial = 'VC2222222'

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}

        customer_cache = [
            {
                'edge': edge_1_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_1_serial,
                'bruin_client_info': {
                    'client_id': bruin_client_1,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_2_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_2_serial,
                'bruin_client_info': {
                    'client_id': bruin_client_2,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_3_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_3_serial,
                'bruin_client_info': {
                    'client_id': bruin_client_2,
                    'client_name': 'EVIL-CORP'
                },
            },
        ]

        get_cache_response = {
            'body': customer_cache,
            'status': 200,
        }

        edges_data_by_serial = {
            edge_1_serial: {'edge_id': edge_1_full_id},
            edge_2_serial: {'edge_id': edge_2_full_id},
            edge_3_serial: {'edge_id': edge_3_full_id},
        }

        ticket_1_id = 12345
        ticket_1_detail_1 = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
        }
        ticket_1_detail_2 = {
            "detailID": 2746930,
            "detailValue": None,
        }
        ticket_1_notes = [
            {
                "noteId": 41894040,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
                "serviceNumber": [
                    edge_1_serial,
                ],
            }
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
            "detailID": 2746931,
            "detailValue": edge_2_serial,
        }
        ticket_2_notes = [
            {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
                "serviceNumber": [
                    edge_2_serial,
                ],
            }
        ]
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                ticket_2_detail_1,
            ],
            'ticket_notes': ticket_2_notes,
        }

        ticket_3_id = 11111
        ticket_3_detail_1 = {
            "detailID": 2746932,
            "detailValue": edge_3_serial,
        }
        ticket_3_notes = [
            {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
                "serviceNumber": [
                    edge_3_serial,
                ],
            }
        ]
        ticket_3 = {
            'ticket_id': ticket_3_id,
            'ticket_details': [
                ticket_3_detail_1,
            ],
            'ticket_notes': ticket_3_notes,
        }

        ticket_4_id = 22222
        ticket_4_detail_1 = {
            "detailID": 2746933,
            "detailValue": edge_4_serial,
        }
        ticket_4_notes = [
            {
                "noteId": 41894043,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
                "serviceNumber": [
                    edge_4_serial,
                ],
            }
        ]
        ticket_4 = {
            'ticket_id': ticket_4_id,
            'ticket_details': [
                ticket_4_detail_1,
            ],
            'ticket_notes': ticket_4_notes,
        }

        ticket_1_with_notes_filtered = {
            'ticket_id': ticket_1,
            'ticket_details': [
                ticket_1_detail_1,
            ],
            'ticket_notes': ticket_1_notes,
        }
        ticket_2_with_notes_filtered = {
            'ticket_id': ticket_2,
            'ticket_details': [
                ticket_2_detail_1,
            ],
            'ticket_notes': ticket_2_notes,
        }
        ticket_3_with_notes_filtered = {
            'ticket_id': ticket_3,
            'ticket_details': [
                ticket_3_detail_1,
            ],
            'ticket_notes': ticket_3_notes,
        }

        open_tickets = [ticket_1, ticket_2, ticket_3, ticket_4]
        relevant_tickets = [ticket_1, ticket_2, ticket_3]
        relevant_tickets_with_notes_filtered = [
            ticket_1_with_notes_filtered,
            ticket_2_with_notes_filtered,
            ticket_3_with_notes_filtered,
        ]
        ticket_details_with_triage = [
            {
                'ticket_id': ticket_1_id,
                'ticket_detail': ticket_1_detail_1,
                'ticket_notes': ticket_1_with_notes_filtered
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_detail': ticket_2_detail_1,
                'ticket_notes': ticket_2_with_notes_filtered
            },
        ]
        ticket_details_without_triage = [
            {
                'ticket_id': ticket_3_id,
                'ticket_detail': ticket_3_detail_1,
                'ticket_notes': ticket_3_with_notes_filtered
            },
        ]

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

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_triage_monitoring = CoroutineMock(return_value=get_cache_response)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_all_open_tickets_with_details_for_monitored_companies = CoroutineMock(return_value=open_tickets)
        triage._filter_tickets_and_details_related_to_edges_under_monitoring = Mock(return_value=relevant_tickets)
        triage._filter_irrelevant_notes_in_tickets = Mock(return_value=relevant_tickets_with_notes_filtered)
        triage._get_ticket_details_with_and_without_triage = Mock(
            return_value=(ticket_details_with_triage, ticket_details_without_triage)
        )
        triage._process_ticket_details_with_triage = CoroutineMock()
        triage._process_ticket_details_without_triage = CoroutineMock()

        await triage._run_tickets_polling()

        customer_cache_repository.get_cache_for_triage_monitoring.assert_awaited_once()
        triage._get_all_open_tickets_with_details_for_monitored_companies.assert_awaited_once()
        triage._filter_tickets_and_details_related_to_edges_under_monitoring.assert_called_once_with(open_tickets)
        triage._filter_irrelevant_notes_in_tickets.assert_called_once_with(relevant_tickets)
        triage._get_ticket_details_with_and_without_triage.assert_called_once_with(
            relevant_tickets_with_notes_filtered
        )
        triage._process_ticket_details_with_triage.assert_awaited_once_with(
            ticket_details_with_triage, edges_data_by_serial
        )
        triage._process_ticket_details_without_triage.assert_awaited_once_with(
            ticket_details_without_triage, edges_data_by_serial
        )

    @pytest.mark.asyncio
    async def get_all_open_tickets_with_details_for_monitored_companies_test(self):
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
        tickets_with_details_for_bruin_client_2 = [
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

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}

        customer_cache = [
            {
                'edge': edge_1_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_1_serial,
                'bruin_client_info': {
                    'client_id': bruin_client_1_id,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_2_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_2_serial,
                'bruin_client_info': {
                    'client_id': bruin_client_2_id,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_3_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_3_serial,
                'bruin_client_info': {
                    'client_id': bruin_client_2_id,
                    'client_name': 'EVIL-CORP'
                },
            },
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._customer_cache = customer_cache
        triage._get_open_tickets_with_details_by_client_id = CoroutineMock(side_effect=[
            tickets_with_details_for_bruin_client_1, tickets_with_details_for_bruin_client_2
        ])

        await triage._get_all_open_tickets_with_details_for_monitored_companies()

        triage._get_open_tickets_with_details_by_client_id.assert_has_awaits([
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

        customer_cache = [
            {
                'edge': edge_1_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_1_serial,
                'bruin_client_info': {
                    'client_id': bruin_client_1_id,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_2_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_2_serial,
                'bruin_client_info': {
                    'client_id': bruin_client_2_id,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_3_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_3_serial,
                'bruin_client_info': {
                    'client_id': bruin_client_3_id,
                    'client_name': 'EVIL-CORP'
                },
            },
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._customer_cache = customer_cache
        triage._get_open_tickets_with_details_by_client_id = CoroutineMock(side_effect=[
            tickets_with_details_for_bruin_client_1,
            Exception,
            tickets_with_details_for_bruin_client_3,
        ])

        await triage._get_all_open_tickets_with_details_for_monitored_companies()

        triage._get_open_tickets_with_details_by_client_id.assert_has_awaits([
            call(bruin_client_1_id, []), call(bruin_client_2_id, []), call(bruin_client_3_id, [])
        ], any_order=True)

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_test(self):
        bruin_client_id = 12345

        ticket_1_id = 11111
        ticket_2_id = 22222
        ticket_ids = [{'ticketID': ticket_1_id}, {'ticketID': ticket_2_id}]

        ticket_1_details_item_1 = {
            "detailID": 2746937,
            "detailValue": 'VC1234567890',
        }
        ticket_1_details_items = [ticket_1_details_item_1]
        ticket_1_notes = [
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
        ticket_1_details = {
            'ticketDetails': ticket_1_details_items,
            'ticketNotes': ticket_1_notes,
        }

        ticket_2_details_item_1 = {
            "detailID": 2746938,
            "detailValue": 'VC1234567890',
        }
        ticket_2_details_items = [ticket_2_details_item_1]
        ticket_2_notes = [
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
        ticket_2_details = {
            'ticketDetails': ticket_2_details_items,
            'ticketNotes': ticket_2_notes,
        }

        uuid_1 = uuid()
        get_open_tickets_response = {
            'request_id': uuid_1,
            'body': ticket_ids,
            'status': 200,
        }

        uuid_2 = uuid()
        get_ticket_1_details_response = {
            'request_id': uuid_2,
            'body': ticket_1_details,
            'status': 200,
        }

        uuid_3 = uuid()
        get_ticket_2_details_response = {
            'request_id': uuid_3,
            'body': ticket_2_details,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response, get_ticket_2_details_response
        ])

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        result = []
        await triage._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id)
        ])

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_details': ticket_1_details_items,
                'ticket_notes': ticket_1_notes,
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_details': ticket_2_details_items,
                'ticket_notes': ticket_2_notes,
            }
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_with_open_tickets_request_not_having_2XX_status_test(self):
        bruin_client_id = 12345

        uuid_ = uuid()
        get_open_tickets_response = {
            'request_id': uuid_,
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        result = []
        await triage._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_ticket_details.assert_not_awaited()
        assert result == []

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_with_ticket_details_request_not_having_2XX_status_test(self):
        bruin_client_id = 12345

        ticket_1_id = 11111
        ticket_2_id = 22222
        ticket_ids = [{'ticketID': ticket_1_id}, {'ticketID': ticket_2_id}]

        ticket_2_details_item_1 = {
            "detailID": 2746938,
            "detailValue": 'VC1234567890',
        }
        ticket_2_details_items = [ticket_2_details_item_1]
        ticket_2_notes = [
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
        ticket_2_details = {
            'ticketDetails': ticket_2_details_items,
            'ticketNotes': ticket_2_notes,
        }

        uuid_1 = uuid()
        get_open_tickets_response = {
            'request_id': uuid_1,
            'body': ticket_ids,
            'status': 200,
        }

        uuid_2 = uuid()
        get_ticket_1_details_response = {
            'request_id': uuid_2,
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        uuid_3 = uuid()
        get_ticket_2_details_response = {
            'request_id': uuid_3,
            'body': ticket_2_details,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response, get_ticket_2_details_response
        ])

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        result = []
        await triage._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id)
        ])

        expected = [
            {
                'ticket_id': ticket_2_id,
                'ticket_details': ticket_2_details_items,
                'ticket_notes': ticket_2_notes,
            }
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_with_ticket_details_not_having_details_actually_test(self):
        bruin_client_id = 12345

        ticket_1_id = 11111
        ticket_2_id = 22222
        ticket_ids = [{'ticketID': ticket_1_id}, {'ticketID': ticket_2_id}]

        ticket_1_details_item_1 = {
            "detailID": 2746937,
            "detailValue": 'VC1234567890',
        }
        ticket_1_details_items = [ticket_1_details_item_1]
        ticket_1_notes = [
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
        ticket_1_details = {
            'ticketDetails': ticket_1_details_items,
            'ticketNotes': ticket_1_notes,
        }

        ticket_2_details_items = []
        ticket_2_notes = []
        ticket_2_details = {
            'ticketDetails': ticket_2_details_items,
            'ticketNotes': ticket_2_notes,
        }

        uuid_1 = uuid()
        get_open_tickets_response = {
            'request_id': uuid_1,
            'body': ticket_ids,
            'status': 200,
        }

        uuid_2 = uuid()
        get_ticket_1_details_response = {
            'request_id': uuid_2,
            'body': ticket_1_details,
            'status': 200,
        }

        uuid_3 = uuid()
        get_ticket_2_details_response = {
            'request_id': uuid_3,
            'body': ticket_2_details,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response, get_ticket_2_details_response
        ])

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        result = []
        await triage._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id)
        ])

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_details': ticket_1_details_items,
                'ticket_notes': ticket_1_notes,
            }
        ]
        assert result == expected

    def filter_tickets_and_details_related_to_edges_under_monitoring_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1112223'
        edge_4_serial = 'VC3344455'
        edge_5_serial = 'VC5666777'
        edge_6_serial = 'VC8889991'
        edge_7_serial = 'VC1122334'

        bruin_client_1_id = 12345
        bruin_client_2_id = 67890

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_4_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 4}
        edge_5_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 5}

        customer_cache = [
            {
                'edge': edge_1_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_1_serial,
                'bruin_client_info': {
                    'client_id': bruin_client_1_id,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_2_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_2_serial,
                'bruin_client_info': {
                    'client_id': bruin_client_1_id,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_4_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_4_serial,
                'bruin_client_info': {
                    'client_id': bruin_client_2_id,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_5_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_5_serial,
                'bruin_client_info': {
                    'client_id': bruin_client_2_id,
                    'client_name': 'EVIL-CORP'
                },
            },
        ]

        ticket_1_id = 12345
        ticket_1_detail_1 = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
        }
        ticket_1_detail_2 = {
            "detailID": 2746931,
            "detailValue": edge_6_serial,
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
        ticket_2 = {
            'ticket_id': 67890,
            'ticket_details': [
                {
                    "detailID": 2746932,
                    "detailValue": edge_3_serial,
                },
            ],
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
            'ticket_details': [
                {
                    "detailID": 2746933,
                    "detailValue": edge_5_serial,
                },
            ],
            'ticket_notes': [
                {
                    "noteId": 41894042,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ]
        }
        ticket_4 = {
            'ticket_id': 22222,
            'ticket_details': [
                {
                    "detailID": 2746934,
                    "detailValue": edge_6_serial,
                },
                {
                    "detailID": 2746935,
                    "detailValue": edge_7_serial,
                },
            ],
            'ticket_notes': [
                {
                    "noteId": 41894043,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ]
        }
        tickets = [ticket_1, ticket_2, ticket_3, ticket_4]

        ticket_1_filtered = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                ticket_1_detail_1,
            ],
            'ticket_notes': ticket_1_notes,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._customer_cache = customer_cache

        result = triage._filter_tickets_and_details_related_to_edges_under_monitoring(tickets)

        expected = [ticket_1_filtered, ticket_3]
        assert result == expected

    def filter_invalid_notes_in_tickets_test(self):
        service_number_1 = 'VC1234567'
        service_number_2 = 'VC8901234'
        service_number_3 = '20.RBDB.872345'
        service_number_4 = 'VC1112223'
        service_number_5 = '18.RBDB.105641'
        service_number_6 = 'VC3344455'

        customer_cache = [
            {
                'edge': {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1},
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': service_number_1,
                'bruin_client_info': {
                    'client_id': 9994,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2},
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': service_number_2,
                'bruin_client_info': {
                    'client_id': 9994,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3},
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': service_number_4,
                'bruin_client_info': {
                    'client_id': 9994,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 4},
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': service_number_6,
                'bruin_client_info': {
                    'client_id': 9994,
                    'client_name': 'EVIL-CORP'
                },
            },
        ]

        ticket_1_id = 12345
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
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
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
            "createdDate": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "serviceNumber": [
                service_number_1,
            ],
        }
        ticket_1_note_5 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": f'#*Automation Engine*#\nRe-opening ticket\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "serviceNumber": [
                service_number_1,
            ],
        }
        ticket_1 = {
            'ticket_id': ticket_1_id,
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
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:08:13.503-05:00",
            "serviceNumber": [
                service_number_2,
                service_number_4,
            ],
        }
        ticket_2_note_3 = {
            "noteId": 41894042,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:08:13.503-05:00",
            "serviceNumber": [
                service_number_3,
                service_number_5,
            ],
        }
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': ticket_2_details,
            'ticket_notes': [
                ticket_2_note_1,
                ticket_2_note_2,
                ticket_2_note_3,
            ],
        }

        ticket_3_id = 67890
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
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:08:13.503-05:00",
            "serviceNumber": [
                service_number_5,
                service_number_6,
            ],
        }
        ticket_3 = {
            'ticket_id': ticket_3_id,
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
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._customer_cache = customer_cache

        result = triage._filter_irrelevant_notes_in_tickets(tickets)

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_details': ticket_1_details,
                'ticket_notes': [
                    {
                        "noteId": 41894041,
                        "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                        "createdDate": "2020-02-24T10:07:13.503-05:00",
                        "serviceNumber": [
                            service_number_1,
                        ],
                    }
                ],
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_details': ticket_2_details,
                'ticket_notes': [
                    ticket_2_note_2,
                ],
            },
            {
                'ticket_id': ticket_3_id,
                'ticket_details': ticket_3_details,
                'ticket_notes': [
                    {
                        "noteId": 41894042,
                        "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                        "createdDate": "2020-02-24T10:08:13.503-05:00",
                        "serviceNumber": [
                            service_number_6,
                        ],
                    }
                ],
            },
        ]
        assert result == expected

    def get_ticket_details_with_and_without_triage_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC7654321'
        serial_number_3 = 'VC1112223'
        serial_number_4 = 'VC3344455'

        ticket_1_id = 12345
        ticket_1_detail_1 = {
            "detailID": 2746930,
            "detailValue": serial_number_1,
        }
        ticket_1_detail_2 = {
            "detailID": 2746930,
            "detailValue": serial_number_3,
        }
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_details': [
                ticket_1_detail_1,
                ticket_1_detail_2,
            ],
            'ticket_notes': [
                ticket_1_note_1,
            ]
        }

        ticket_2_id = 67890
        ticket_2_detail_1 = {
            "detailID": 2746931,
            "detailValue": serial_number_2,
        }
        ticket_2_detail_2 = {
            "detailID": 2746931,
            "detailValue": serial_number_4,
        }
        ticket_2_note_1 = {
            "noteId": 41894041,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_2,
                serial_number_4,
            ],
        }
        ticket_2_note_2 = {
            "noteId": 41894041,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_details': [
                ticket_2_detail_1,
                ticket_2_detail_2,
            ],
            'ticket_notes': [
                ticket_2_note_1,
                ticket_2_note_2,
            ]
        }

        ticket_3_id = 11111
        ticket_3_detail_1 = {
            "detailID": 2746932,
            "detailValue": serial_number_3,
        }
        ticket_3 = {
            'ticket_id': ticket_3_id,
            'ticket_details': [
                ticket_3_detail_1,
            ],
            'ticket_notes': []
        }

        ticket_4_id = 22222
        ticket_4_detail_1 = {
            "detailID": 2746932,
            "detailValue": serial_number_4,
        }
        ticket_4_note_1 = {
            "noteId": 41894042,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_4,
            ],
        }
        ticket_4 = {
            'ticket_id': ticket_4_id,
            'ticket_details': [
                ticket_4_detail_1,
            ],
            'ticket_notes': [
                ticket_4_note_1,
            ]
        }
        tickets = [ticket_1, ticket_2, ticket_3, ticket_4]

        expected_details_with_triage = [
            {
                'ticket_id': ticket_1_id,
                'ticket_detail': ticket_1_detail_1,
                'ticket_notes': [
                    ticket_1_note_1,
                ]
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_detail': ticket_2_detail_1,
                'ticket_notes': [
                    ticket_2_note_1,
                    ticket_2_note_2,
                ]
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_detail': ticket_2_detail_2,
                'ticket_notes': [
                    ticket_2_note_1,
                ]
            },
            {
                'ticket_id': ticket_4_id,
                'ticket_detail': ticket_4_detail_1,
                'ticket_notes': [
                    ticket_4_note_1,
                ]
            },
        ]
        expected_details_without_triage = [
            {
                'ticket_id': ticket_1_id,
                'ticket_detail': ticket_1_detail_2,
            },
            {
                'ticket_id': ticket_3_id,
                'ticket_detail': ticket_3_detail_1,
            },
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        details_with_triage, details_without_triage = triage._get_ticket_details_with_and_without_triage(tickets)

        assert details_with_triage == expected_details_with_triage
        assert details_without_triage == expected_details_without_triage

    @pytest.mark.asyncio
    async def process_ticket_details_with_triage_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}

        edge_1_data = {'edge_id': edge_1_full_id}
        edge_2_data = {'edge_id': edge_2_full_id}
        edge_3_data = {'edge_id': edge_3_full_id}
        edges_data_by_serial = {
            edge_1_serial: edge_1_data,
            edge_2_serial: edge_2_data,
            edge_3_serial: edge_3_data,
        }

        ticket_detail_1_ticket_id = 12345
        ticket_detail_1_detail = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
        }
        ticket_detail_1_note_1_creation_date = '2019-07-30T06:38:13.503-05:00'
        ticket_detail_1_note_1 = {
            "noteId": 41894041,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: {ticket_detail_1_note_1_creation_date}',
            "createdDate": ticket_detail_1_note_1_creation_date,
        }
        ticket_detail_1 = {
            'ticket_id': ticket_detail_1_ticket_id,
            'ticket_detail': ticket_detail_1_detail,
            'ticket_notes': [ticket_detail_1_note_1]
        }

        ticket_detail_2_ticket_id = 67890
        ticket_detail_2_detail = {
            "detailID": 2746931,
            "detailValue": edge_2_serial,
        }
        ticket_detail_2_note_1_creation_date = '2019-04-30T06:38:13.503-05:00'
        ticket_detail_2_note_2_creation_date = '2019-04-30T06:38:13.503-05:00'
        ticket_detail_2_note_3_creation_date = '2019-12-30T06:38:13.503-05:00'
        ticket_detail_2_note_1 = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: {ticket_detail_2_note_1_creation_date}',
            "createdDate": ticket_detail_2_note_1_creation_date,
        }
        ticket_detail_2_note_2 = {
            "noteId": 41894044,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: {ticket_detail_2_note_2_creation_date}',
            "createdDate": ticket_detail_2_note_2_creation_date,
        }
        ticket_detail_2_note_3 = {
            "noteId": 41894046,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: {ticket_detail_2_note_3_creation_date}',
            "createdDate": ticket_detail_2_note_3_creation_date,
        }
        ticket_detail_2 = {
            'ticket_id': ticket_detail_2_ticket_id,
            'ticket_detail': ticket_detail_2_detail,
            'ticket_notes': [ticket_detail_2_note_1, ticket_detail_2_note_2, ticket_detail_2_note_3]
        }

        ticket_details = [
            ticket_detail_1,
            ticket_detail_2,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_most_recent_ticket_note = Mock(side_effect=[ticket_detail_1_note_1, ticket_detail_2_note_3])
        triage._was_ticket_note_appended_recently = Mock(side_effect=[False, True])
        triage._append_new_triage_notes_based_on_recent_events = CoroutineMock()

        await triage._process_ticket_details_with_triage(ticket_details, edges_data_by_serial)

        triage._get_most_recent_ticket_note.assert_has_calls([
            call(ticket_detail_1),
            call(ticket_detail_2),
        ])
        triage._was_ticket_note_appended_recently.assert_has_calls([
            call(ticket_detail_1_note_1), call(ticket_detail_2_note_3),
        ])
        triage._append_new_triage_notes_based_on_recent_events.assert_awaited_once_with(
            ticket_detail_1, ticket_detail_1_note_1_creation_date, edge_1_data
        )

    def get_most_recent_ticket_note_test(self):
        ticket_note_1 = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-12-30T06:38:13.503-05:00',
        }
        ticket_note_2 = {
            "noteId": 41894044,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket_note_3 = {
            "noteId": 41894046,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-11-30T06:38:13.503-05:00',
        }
        ticket = {
            'ticket_id': 67890,
            'ticket_details': [
                {
                    "detailID": 2746931,
                    "detailValue": 'VC7654321',
                },
            ],
            'ticket_notes': [ticket_note_1, ticket_note_2, ticket_note_3]
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        newest_triage_note = triage._get_most_recent_ticket_note(ticket)

        assert newest_triage_note is ticket_note_1

    def was_ticket_note_appended_recently_test(self):
        ticket_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-12-30T06:38:13.503-05:00',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        datetime_mock = Mock()

        timestamp = '2019-12-30T06:43:13.503-05:00'
        datetime_mock.now = Mock(return_value=parse(timestamp))
        with patch.object(triage_module, 'datetime', new=datetime_mock):
            result = triage._was_ticket_note_appended_recently(ticket_note)
        assert result is True

        timestamp = '2019-12-30T07:08:13.503-05:00'
        datetime_mock.now = Mock(return_value=parse(timestamp))
        with patch.object(triage_module, 'datetime', new=datetime_mock):
            result = triage._was_ticket_note_appended_recently(ticket_note)
        assert result is True

        timestamp = '2019-12-30T09:00:00.000-05:00'
        datetime_mock.now = Mock(return_value=parse(timestamp))
        with patch.object(triage_module, 'datetime', new=datetime_mock):
            result = triage._was_ticket_note_appended_recently(ticket_note)
        assert result is False

    @pytest.mark.asyncio
    async def append_new_triage_notes_based_on_recent_events_with_production_environment_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'
        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': 67890,
                'detailValue': service_number,
            },
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
                    "createdDate": '2019-07-30T06:38:13.503-05:00',
                }
            ]
        }

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_data = {'edge_id': edge_full_id}

        events = [
            {
                'event': 'LINK_DEAD',
                'category': 'NETWORK',
                'eventTime': '2019-07-30 07:38:00+00:00',
                'message': 'Link GE2 is now DEAD'
            }
        ] * 100
        last_events_response = {'body': events, 'status': 200}

        events_chunk_1 = events[:25]
        events_chunk_2 = events[25:50]
        events_chunk_3 = events[50:75]
        events_chunk_4 = events[75:]

        note_for_events_chunk_1 = 'This is the note for the first chunk'
        note_for_events_chunk_2 = 'This is the note for the second chunk'
        note_for_events_chunk_3 = 'This is the note for the third chunk'
        note_for_events_chunk_4 = 'This is the note for the fourth chunk'

        append_note_1_response = {
            'body': 'Note appended successfully',
            'status': 200,
        }
        append_note_2_response = {
            'body': 'Note appended successfully',
            'status': 200,
        }
        append_note_3_response = {
            'body': 'Note appended successfully',
            'status': 200,
        }
        append_note_4_response = {
            'body': 'Note appended successfully',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock(side_effect=[
            append_note_1_response,
            append_note_2_response,
            append_note_3_response,
            append_note_4_response,
        ])

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        triage_repository = Mock()
        triage_repository.build_events_note = Mock(side_effect=[
            note_for_events_chunk_1,
            note_for_events_chunk_2,
            note_for_events_chunk_3,
            note_for_events_chunk_4,
        ])

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_events_chunked = Mock(return_value=[
            events_chunk_1,
            events_chunk_2,
            events_chunk_3,
            events_chunk_4,
        ])
        triage._notify_triage_note_was_appended_to_ticket = CoroutineMock()

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            await triage._append_new_triage_notes_based_on_recent_events(
                ticket_detail, last_triage_timestamp, edge_data
            )

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_called_once_with(events)
        triage_repository.build_events_note.assert_has_calls([
            call(events_chunk_1),
            call(events_chunk_2),
            call(events_chunk_3),
            call(events_chunk_4),
        ])
        bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id, note_for_events_chunk_1, service_numbers=[service_number]),
            call(ticket_id, note_for_events_chunk_2, service_numbers=[service_number]),
            call(ticket_id, note_for_events_chunk_3, service_numbers=[service_number]),
            call(ticket_id, note_for_events_chunk_4, service_numbers=[service_number]),
        ])
        triage._notify_triage_note_was_appended_to_ticket.assert_awaited_once_with(ticket_detail)

    @pytest.mark.asyncio
    async def append_new_triage_notes_based_on_recent_events_with_environment_different_from_production_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'
        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': 67890,
                'detailValue': service_number,
            },
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
                    "createdDate": '2019-07-30T06:38:13.503-05:00',
                }
            ]
        }

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_data = {'edge_id': edge_full_id}

        events = [
            {
                'event': 'LINK_DEAD',
                'category': 'NETWORK',
                'eventTime': '2019-07-30 07:38:00+00:00',
                'message': 'Link GE2 is now DEAD'
            }
        ] * 100
        last_events_response = {'body': events, 'status': 200}

        events_chunk_1 = events[:25]
        events_chunk_2 = events[25:50]
        events_chunk_3 = events[50:75]
        events_chunk_4 = events[75:]

        note_for_events_chunk_1 = 'This is the note for the first chunk'
        note_for_events_chunk_2 = 'This is the note for the second chunk'
        note_for_events_chunk_3 = 'This is the note for the third chunk'
        note_for_events_chunk_4 = 'This is the note for the fourth chunk'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock()

        triage_repository = Mock()
        triage_repository.build_events_note = Mock(side_effect=[
            note_for_events_chunk_1,
            note_for_events_chunk_2,
            note_for_events_chunk_3,
            note_for_events_chunk_4,
        ])

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_events_chunked = Mock(return_value=[
            events_chunk_1,
            events_chunk_2,
            events_chunk_3,
            events_chunk_4,
        ])
        triage._notify_triage_note_was_appended_to_ticket = CoroutineMock()

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            await triage._append_new_triage_notes_based_on_recent_events(
                ticket_detail, last_triage_timestamp, edge_data
            )

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_called_once_with(events)
        triage_repository.build_events_note.assert_has_calls([
            call(events_chunk_1),
            call(events_chunk_2),
            call(events_chunk_3),
            call(events_chunk_4),
        ])
        bruin_repository.append_note_to_ticket.assert_not_awaited()
        triage._notify_triage_note_was_appended_to_ticket.assert_awaited_once_with(ticket_detail)

    @pytest.mark.asyncio
    async def append_new_triage_notes_based_on_recent_events_with_events_sorted_by_event_time_before_chunking_test(
            self):
        ticket_id = 12345
        service_number = 'VC1234567'
        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': 67890,
                'detailValue': service_number,
            },
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
                    "createdDate": '2019-07-30T06:38:13.503-05:00',
                }
            ]
        }

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_data = {'edge_id': edge_full_id}

        event_1 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_2 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-29 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_3 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-31 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_4 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-28 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        events = [event_1, event_2, event_3, event_4]
        last_events_response = {'body': events, 'status': 200}

        events_sorted_by_event_time = [event_3, event_1, event_2, event_4]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock()

        triage_repository = Mock()
        triage_repository.build_events_note = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_events_chunked = Mock(return_value=[])  # Just tricking this return value to "stop" execution here
        triage._notify_triage_note_was_appended_to_ticket = CoroutineMock()

        await triage._append_new_triage_notes_based_on_recent_events(
            ticket_detail, last_triage_timestamp, edge_data
        )

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_called_once_with(events_sorted_by_event_time)

    @pytest.mark.asyncio
    async def append_new_triage_notes_based_on_recent_events_with_edge_events_request_not_having_2XX_status_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'
        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': 67890,
                'detailValue': service_number,
            },
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
                    "createdDate": '2019-07-30T06:38:13.503-05:00',
                }
            ]
        }

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_data = {'edge_id': edge_full_id}

        last_events_response_body = 'Got internal error from Velocloud'
        last_events_response_status = 500
        last_events_response = {
            'body': last_events_response_body,
            'status': last_events_response_status,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_events_chunked = Mock()

        await triage._append_new_triage_notes_based_on_recent_events(
            ticket_detail, last_triage_timestamp, edge_data
        )

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_not_called()

    @pytest.mark.asyncio
    async def append_new_triage_notes_based_on_recent_events_with_edge_events_request_returning_no_events_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'
        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': 67890,
                'detailValue': service_number,
            },
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
                    "createdDate": '2019-07-30T06:38:13.503-05:00',
                }
            ]
        }

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_data = {'edge_id': edge_full_id}

        last_events_response_body = []
        last_events_response_status = 200
        last_events_response = {
            'body': last_events_response_body,
            'status': last_events_response_status,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_events_chunked = Mock()

        await triage._append_new_triage_notes_based_on_recent_events(
            ticket_detail, last_triage_timestamp, edge_data
        )

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_not_called()

    @pytest.mark.asyncio
    async def append_new_triage_notes_based_on_recent_events_with_append_note_request_not_having_2XX_status_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'
        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': 67890,
                'detailValue': service_number,
            },
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
                    "createdDate": '2019-07-30T06:38:13.503-05:00',
                }
            ]
        }

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_data = {'edge_id': edge_full_id}

        events = [
            {
                'event': 'LINK_DEAD',
                'category': 'NETWORK',
                'eventTime': '2019-07-30 07:38:00+00:00',
                'message': 'Link GE2 is now DEAD'
            }
        ] * 100
        last_events_response = {'body': events, 'status': 200}

        events_chunk_1 = events[:25]
        events_chunk_2 = events[25:50]
        events_chunk_3 = events[50:75]
        events_chunk_4 = events[75:]

        note_for_events_chunk_1 = 'This is the note for the first chunk'
        note_for_events_chunk_2 = 'This is the note for the second chunk'
        note_for_events_chunk_3 = 'This is the note for the third chunk'
        note_for_events_chunk_4 = 'This is the note for the fourth chunk'

        append_note_1_response = {
            'body': 'Note appended successfully',
            'status': 200,
        }
        append_note_2_response = {
            'body': 'Could not append note to ticket',
            'status': 500,
        }
        append_note_3_response = {
            'body': 'Note appended successfully',
            'status': 200,
        }
        append_note_4_response = {
            'body': 'Could not append note to ticket',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock(side_effect=[
            append_note_1_response,
            append_note_2_response,
            append_note_3_response,
            append_note_4_response,
        ])

        triage_repository = Mock()
        triage_repository.build_events_note = Mock(side_effect=[
            note_for_events_chunk_1,
            note_for_events_chunk_2,
            note_for_events_chunk_3,
            note_for_events_chunk_4,
        ])

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_events_chunked = Mock(return_value=[
            events_chunk_1,
            events_chunk_2,
            events_chunk_3,
            events_chunk_4,
        ])
        triage._notify_triage_note_was_appended_to_ticket = CoroutineMock()

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            await triage._append_new_triage_notes_based_on_recent_events(
                ticket_detail, last_triage_timestamp, edge_data
            )

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_called_once_with(events)
        triage_repository.build_events_note.assert_has_calls([
            call(events_chunk_1),
            call(events_chunk_2),
            call(events_chunk_3),
            call(events_chunk_4),
        ])
        bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id, note_for_events_chunk_1, service_numbers=[service_number]),
            call(ticket_id, note_for_events_chunk_2, service_numbers=[service_number]),
            call(ticket_id, note_for_events_chunk_3, service_numbers=[service_number]),
            call(ticket_id, note_for_events_chunk_4, service_numbers=[service_number]),
        ])
        triage._notify_triage_note_was_appended_to_ticket.assert_awaited_once_with(ticket_detail)

    @pytest.mark.asyncio
    async def append_new_triage_notes_based_on_recent_events_with_no_notes_appended_to_ticket_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'
        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': 67890,
                'detailValue': service_number,
            },
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
                    "createdDate": '2019-07-30T06:38:13.503-05:00',
                }
            ]
        }

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_data = {'edge_id': edge_full_id}

        events = [
            {
                'event': 'LINK_DEAD',
                'category': 'NETWORK',
                'eventTime': '2019-07-30 07:38:00+00:00',
                'message': 'Link GE2 is now DEAD'
            },
            {
                'event': 'LINK_DEAD',
                'category': 'NETWORK',
                'eventTime': '2019-07-31 07:38:00+00:00',
                'message': 'Link GE1 is now DEAD'
            }
        ]
        last_events_response = {'body': events, 'status': 200}

        events_chunk_1 = [events[0]]
        events_chunk_2 = [events[1]]

        note_for_events_chunk_1 = 'This is the note for the first chunk'
        note_for_events_chunk_2 = 'This is the note for the second chunk'

        append_note_response = {
            'body': 'Got error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock(return_value=append_note_response)

        triage_repository = Mock()
        triage_repository.build_events_note = Mock(side_effect=[
            note_for_events_chunk_1,
            note_for_events_chunk_2,
        ])

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_events_chunked = Mock(return_value=[
            events_chunk_1,
            events_chunk_2,
        ])
        triage._notify_triage_note_was_appended_to_ticket = CoroutineMock()

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            await triage._append_new_triage_notes_based_on_recent_events(
                ticket_detail, last_triage_timestamp, edge_data
            )

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_called_once_with(events)
        triage_repository.build_events_note.assert_has_calls([
            call(events_chunk_1),
            call(events_chunk_2),
        ])
        bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id, note_for_events_chunk_1, service_numbers=[service_number]),
            call(ticket_id, note_for_events_chunk_2, service_numbers=[service_number]),
        ])
        triage._notify_triage_note_was_appended_to_ticket.assert_not_awaited()

    def get_events_chunked_test(self):
        event_1 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_2 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-29 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_3 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-31 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_4 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-28 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_5 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-01 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        events = [event_1, event_2, event_3, event_4, event_5]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['event_limit'] = 2
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            chunks = triage._get_events_chunked(events)

            assert isinstance(chunks, Generator)
            assert list(chunks) == [
                [event_1, event_2],
                [event_3, event_4],
                [event_5],
            ]

    @pytest.mark.asyncio
    async def notify_triage_note_was_appended_to_ticket_test(self):
        ticket_id = 12345
        ticket_detail_id = 67890
        service_number = 'VC1234567'
        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': ticket_detail_id,
                'detailValue': service_number,
            },
            'ticket_notes': [
                {
                    "noteId": 41894040,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
                    "createdDate": '2019-07-30T06:38:13.503-05:00',
                }
            ]
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        await triage._notify_triage_note_was_appended_to_ticket(ticket_detail)

        notifications_repository.send_slack_message.assert_awaited_once_with(
            f'Triage appended to detail {ticket_detail_id} (serial: {service_number}) of ticket {ticket_id}. '
            f'Details at https://app.bruin.com/t/{ticket_id}'
        )

    @pytest.mark.asyncio
    async def process_ticket_details_without_triage_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}

        edge_1_data = {'edge_id': edge_1_full_id}
        edge_2_data = {'edge_id': edge_2_full_id}
        edge_3_data = {'edge_id': edge_3_full_id}
        edges_data_by_serial = {
            edge_1_serial: edge_1_data,
            edge_2_serial: edge_2_data,
            edge_3_serial: edge_3_data,
        }

        ticket_detail_1_ticket_id = 12345
        ticket_detail_1_detail = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
        }
        ticket_detail_1_note = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket_detail_1 = {
            'ticket_id': ticket_detail_1_ticket_id,
            'ticket_detail': ticket_detail_1_detail,
            'ticket_notes': [ticket_detail_1_note]
        }

        ticket_detail_2_ticket_id = 67890
        ticket_detail_2_detail = {
            "detailID": 6895947,
            "detailValue": edge_3_serial,
        }
        ticket_detail_2_note = {
            "noteId": 8793897,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-18T06:38:13.503-05:00',
            "createdDate": '2019-07-18T06:38:13.503-05:00',
        }
        ticket_detail_2 = {
            'ticket_id': ticket_detail_2_ticket_id,
            'ticket_detail': ticket_detail_2_detail,
            'ticket_notes': [ticket_detail_2_note]
        }

        tickets = [
            ticket_detail_1,
            ticket_detail_2,
        ]

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
        edge_1_events = [event_1, event_2]
        edge_3_events = [event_3]
        edge_1_events_sorted_by_event_time = [event_2, event_1]
        edge_3_events_sorted_by_event_time = [event_3]
        edge_1_last_events_response = {
            'body': edge_1_events,
            'status': 200,
        }
        edge_3_last_events_response = {
            'body': edge_3_events,
            'status': 200,
        }

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_1_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            },
        }
        edge_1_status_response = {
            'body': {
                'edge_id': edge_1_full_id,
                'edge_info': edge_1_status,
            },
            'status': 200,
        }

        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|67890|',
            'bruin_client_info': {
                'client_id': 67890,
                'client_name': 'METTEL/NEW YORK',
            },
        }
        edge_3_status_response = {
            'body': {
                'edge_id': edge_3_full_id,
                'edge_info': edge_3_status,
            },
            'status': 200,
        }

        triage_note = 'This is a triage note'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        customer_cache_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response,
            edge_3_status_response,
        ])
        velocloud_repository.get_last_edge_events = CoroutineMock(side_effect=[
            edge_1_last_events_response,
            edge_3_last_events_response,
        ])

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock(return_value=200)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        triage_repository = Mock()
        triage_repository.build_triage_note = Mock(return_value=triage_note)

        metrics_repository = Mock()
        metrics_repository.increment_tickets_without_triage_processed = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_ticket_details_without_triage(tickets, edges_data_by_serial)

        velocloud_repository.get_last_edge_events.assert_has_awaits([
            call(edge_1_full_id, since=past_moment_for_events_lookup),
            call(edge_3_full_id, since=past_moment_for_events_lookup),
        ])
        velocloud_repository.get_edge_status.assert_has_awaits([
            call(edge_1_full_id),
            call(edge_3_full_id),
        ])
        triage_repository.build_triage_note.assert_has_calls([
            call(edge_1_full_id, edge_1_status, edge_1_events_sorted_by_event_time),
            call(edge_3_full_id, edge_3_status, edge_3_events_sorted_by_event_time),
        ])
        bruin_repository.append_triage_note.assert_has_awaits([
            call(ticket_detail_1, triage_note),
            call(ticket_detail_2, triage_note),
        ])
        assert metrics_repository.increment_tickets_without_triage_processed.call_count == 2

    @pytest.mark.asyncio
    async def process_ticket_details_without_triage_with_edge_events_request_not_having_2xx_status_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}

        edge_1_data = {'edge_id': edge_1_full_id}
        edge_2_data = {'edge_id': edge_2_full_id}
        edge_3_data = {'edge_id': edge_3_full_id}
        edges_data_by_serial = {
            edge_1_serial: edge_1_data,
            edge_2_serial: edge_2_data,
            edge_3_serial: edge_3_data,
        }

        ticket_detail_1_ticket_id = 12345
        ticket_detail_1_detail = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
        }
        ticket_detail_1_note = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket_detail_1 = {
            'ticket_id': ticket_detail_1_ticket_id,
            'ticket_detail': ticket_detail_1_detail,
            'ticket_notes': [ticket_detail_1_note]
        }

        ticket_detail_2_id = 67890
        ticket_detail_2_detail = {
            "detailID": 6895947,
            "detailValue": edge_3_serial,
        }
        ticket_detail_2_note = {
            "noteId": 8793897,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-18T06:38:13.503-05:00',
            "createdDate": '2019-07-18T06:38:13.503-05:00',
        }
        ticket_detail_2 = {
            'ticket_id': ticket_detail_2_id,
            'ticket_detail': ticket_detail_2_detail,
            'ticket_notes': [ticket_detail_2_note]
        }

        tickets = [
            ticket_detail_1,
            ticket_detail_2,
        ]

        edge_1_last_events_response = {
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }
        edge_3_last_events_response = {
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        customer_cache_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock()
        velocloud_repository.get_last_edge_events = CoroutineMock(side_effect=[
            edge_1_last_events_response,
            edge_3_last_events_response,
        ])

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        triage_repository = Mock()
        triage_repository.build_triage_note = Mock()

        metrics_repository = Mock()
        metrics_repository.increment_tickets_without_triage_processed = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_ticket_details_without_triage(tickets, edges_data_by_serial)

        velocloud_repository.get_last_edge_events.assert_has_awaits([
            call(edge_1_full_id, since=past_moment_for_events_lookup),
            call(edge_3_full_id, since=past_moment_for_events_lookup),
        ])
        velocloud_repository.get_edge_status.assert_not_awaited()
        triage_repository.build_triage_note.assert_not_called()
        bruin_repository.append_triage_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_ticket_details_without_triage_with_edge_events_list_empty_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}

        edge_1_data = {'edge_id': edge_1_full_id}
        edge_2_data = {'edge_id': edge_2_full_id}
        edge_3_data = {'edge_id': edge_3_full_id}
        edges_data_by_serial = {
            edge_1_serial: edge_1_data,
            edge_2_serial: edge_2_data,
            edge_3_serial: edge_3_data,
        }

        ticket_detail_1_ticket_id = 12345
        ticket_detail_1_detail = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
        }
        ticket_detail_1_note = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket_detail_1 = {
            'ticket_id': ticket_detail_1_ticket_id,
            'ticket_detail': ticket_detail_1_detail,
            'ticket_notes': [ticket_detail_1_note]
        }

        ticket_detail_2_ticket_id = 67890
        ticket_detail_2_detail = {
            "detailID": 6895947,
            "detailValue": edge_3_serial,
        }
        ticket_detail_2_note = {
            "noteId": 8793897,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-18T06:38:13.503-05:00',
            "createdDate": '2019-07-18T06:38:13.503-05:00',
        }
        ticket_detail_2 = {
            'ticket_id': ticket_detail_2_ticket_id,
            'ticket_detail': ticket_detail_2_detail,
            'ticket_notes': [ticket_detail_2_note]
        }

        tickets = [
            ticket_detail_1,
            ticket_detail_2,
        ]

        edge_1_events = []
        edge_3_events = []
        edge_1_last_events_response = {
            'body': edge_1_events,
            'status': 200,
        }
        edge_3_last_events_response = {
            'body': edge_3_events,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        customer_cache_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock()
        velocloud_repository.get_last_edge_events = CoroutineMock(side_effect=[
            edge_1_last_events_response,
            edge_3_last_events_response,
        ])

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        triage_repository = Mock()
        triage_repository.build_triage_note = Mock()

        metrics_repository = Mock()
        metrics_repository.increment_tickets_without_triage_processed = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_ticket_details_without_triage(tickets, edges_data_by_serial)

        velocloud_repository.get_last_edge_events.assert_has_awaits([
            call(edge_1_full_id, since=past_moment_for_events_lookup),
            call(edge_3_full_id, since=past_moment_for_events_lookup),
        ])
        velocloud_repository.get_edge_status.assert_not_awaited()
        triage_repository.build_triage_note.assert_not_called()
        bruin_repository.append_triage_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_ticket_details_without_triage_with_edge_status_request_not_having_2xx_status_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}

        edge_1_data = {'edge_id': edge_1_full_id}
        edge_2_data = {'edge_id': edge_2_full_id}
        edge_3_data = {'edge_id': edge_3_full_id}
        edges_data_by_serial = {
            edge_1_serial: edge_1_data,
            edge_2_serial: edge_2_data,
            edge_3_serial: edge_3_data,
        }

        ticket_detail_1_ticket_id = 12345
        ticket_detail_1_detail = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
        }
        ticket_detail_1_note = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket_detail_1 = {
            'ticket_id': ticket_detail_1_ticket_id,
            'ticket_detail': ticket_detail_1_detail,
            'ticket_notes': [ticket_detail_1_note]
        }

        ticket_detail_2_ticket_id = 67890
        ticket_detail_2_detail = {
            "detailID": 6895947,
            "detailValue": edge_3_serial,
        }
        ticket_detail_2_note = {
            "noteId": 8793897,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-18T06:38:13.503-05:00',
            "createdDate": '2019-07-18T06:38:13.503-05:00',
        }
        ticket_detail_2 = {
            'ticket_id': ticket_detail_2_ticket_id,
            'ticket_detail': ticket_detail_2_detail,
            'ticket_notes': [ticket_detail_2_note]
        }

        tickets = [
            ticket_detail_1,
            ticket_detail_2,
        ]

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
        edge_1_events = [event_1, event_2]
        edge_3_events = [event_3]
        edge_1_last_events_response = {
            'body': edge_1_events,
            'status': 200,
        }
        edge_3_last_events_response = {
            'body': edge_3_events,
            'status': 200,
        }

        edge_1_status_response = {
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        edge_3_status_response = {
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        customer_cache_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response,
            edge_3_status_response,
        ])
        velocloud_repository.get_last_edge_events = CoroutineMock(side_effect=[
            edge_1_last_events_response,
            edge_3_last_events_response,
        ])

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock(return_value=200)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        triage_repository = Mock()
        triage_repository.build_triage_note = Mock()

        metrics_repository = Mock()
        metrics_repository.increment_tickets_without_triage_processed = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_ticket_details_without_triage(tickets, edges_data_by_serial)

        velocloud_repository.get_last_edge_events.assert_has_awaits([
            call(edge_1_full_id, since=past_moment_for_events_lookup),
            call(edge_3_full_id, since=past_moment_for_events_lookup),
        ])
        velocloud_repository.get_edge_status.assert_has_awaits([
            call(edge_1_full_id),
            call(edge_3_full_id),
        ])
        triage_repository.build_triage_note.assert_not_called()
        bruin_repository.append_triage_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_ticket_details_without_triage_with_error_appending_triage_note_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}

        edge_1_data = {'edge_id': edge_1_full_id}
        edge_2_data = {'edge_id': edge_2_full_id}
        edge_3_data = {'edge_id': edge_3_full_id}
        edges_data_by_serial = {
            edge_1_serial: edge_1_data,
            edge_2_serial: edge_2_data,
            edge_3_serial: edge_3_data,
        }

        ticket_detail_1_ticket_id = 12345
        ticket_detail_1_detail = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
        }
        ticket_detail_1_note = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket_detail_1 = {
            'ticket_id': ticket_detail_1_ticket_id,
            'ticket_detail': ticket_detail_1_detail,
            'ticket_notes': [ticket_detail_1_note]
        }

        ticket_detail_2_ticket_id = 67890
        ticket_detail_2_detail = {
            "detailID": 6895947,
            "detailValue": edge_3_serial,
        }
        ticket_detail_2_note = {
            "noteId": 8793897,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-18T06:38:13.503-05:00',
            "createdDate": '2019-07-18T06:38:13.503-05:00',
        }
        ticket_detail_2 = {
            'ticket_id': ticket_detail_2_ticket_id,
            'ticket_detail': ticket_detail_2_detail,
            'ticket_notes': [ticket_detail_2_note]
        }

        tickets = [
            ticket_detail_1,
            ticket_detail_2,
        ]

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
        edge_1_events = [event_1, event_2]
        edge_3_events = [event_3]
        edge_1_events_sorted_by_event_time = [event_2, event_1]
        edge_3_events_sorted_by_event_time = [event_3]
        edge_1_last_events_response = {
            'body': edge_1_events,
            'status': 200,
        }
        edge_3_last_events_response = {
            'body': edge_3_events,
            'status': 200,
        }

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_1_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            },
        }
        edge_1_status_response = {
            'body': {
                'edge_id': edge_1_full_id,
                'edge_info': edge_1_status,
            },
            'status': 200,
        }

        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|67890|',
            'bruin_client_info': {
                'client_id': 67890,
                'client_name': 'METTEL/NEW YORK',
            },
        }
        edge_3_status_response = {
            'body': {
                'edge_id': edge_3_full_id,
                'edge_info': edge_3_status,
            },
            'status': 200,
        }

        triage_note = 'This is a triage note'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        customer_cache_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response,
            edge_3_status_response,
        ])
        velocloud_repository.get_last_edge_events = CoroutineMock(side_effect=[
            edge_1_last_events_response,
            edge_3_last_events_response,
        ])

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock(return_value=503)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        triage_repository = Mock()
        triage_repository.build_triage_note = Mock(return_value=triage_note)

        metrics_repository = Mock()
        metrics_repository.increment_note_append_errors = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_ticket_details_without_triage(tickets, edges_data_by_serial)

        velocloud_repository.get_last_edge_events.assert_has_awaits([
            call(edge_1_full_id, since=past_moment_for_events_lookup),
            call(edge_3_full_id, since=past_moment_for_events_lookup),
        ])
        velocloud_repository.get_edge_status.assert_has_awaits([
            call(edge_1_full_id),
            call(edge_3_full_id),
        ])
        triage_repository.build_triage_note.assert_has_calls([
            call(edge_1_full_id, edge_1_status, edge_1_events_sorted_by_event_time),
            call(edge_3_full_id, edge_3_status, edge_3_events_sorted_by_event_time),
        ])
        bruin_repository.append_triage_note.assert_has_awaits([
            call(ticket_detail_1, triage_note),
            call(ticket_detail_2, triage_note),
        ])
        assert metrics_repository.increment_note_append_errors.call_count == 2
