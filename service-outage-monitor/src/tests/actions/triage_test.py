import os

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
        monitoring_map_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        assert triage._event_bus is event_bus
        assert triage._logger is logger
        assert triage._scheduler is scheduler
        assert triage._config is config
        assert triage._outage_repository is outage_repository
        assert triage._monitoring_map_repository is monitoring_map_repository
        assert triage._bruin_repository is bruin_repository
        assert triage._velocloud_repository is velocloud_repository
        assert triage._notifications_repository is notifications_repository
        assert triage._triage_repository is triage_repository
        assert triage._metrics_repository is metrics_repository

        assert triage._monitoring_mapping == {}

    @pytest.mark.asyncio
    async def start_triage_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        monitoring_map_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
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
        monitoring_map_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
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

        edges_data_by_serial = {
            edge_1_serial: edge_1_data,
            edge_2_serial: edge_2_data,
            edge_3_serial: edge_3_data,
        }

        ticket_1 = {
            'ticket_id': 12345,
            'ticket_details': [
                {
                    "detailID": 2746930,
                    "detailValue": edge_1_serial,
                },
            ],
            'ticket_notes': {
                "noteId": 41894040,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        }
        ticket_2 = {
            'ticket_id': 67890,
            'ticket_details': [
                {
                    "detailID": 2746931,
                    "detailValue": edge_2_serial,
                },
            ],
            'ticket_notes': {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        }
        ticket_3 = {
            'ticket_id': 11111,
            'ticket_details': [
                {
                    "detailID": 2746932,
                    "detailValue": edge_3_serial,
                },
            ],
            'ticket_notes': {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        }
        open_tickets = [ticket_1, ticket_2, ticket_3]
        relevant_tickets = [ticket_1, ticket_2, ticket_3]
        tickets_with_triage = [ticket_1, ticket_2]
        tickets_without_triage = [ticket_3]

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

        monitoring_map_repository = Mock()
        monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses = CoroutineMock()
        monitoring_map_repository.get_monitoring_map_cache = Mock(return_value=monitoring_mapping)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._monitoring_mapping = {'obsolete': 'data'}
        triage._get_all_open_tickets_with_details_for_monitored_companies = CoroutineMock(return_value=open_tickets)
        triage._filter_tickets_related_to_edges_under_monitoring = Mock(return_value=relevant_tickets)
        triage._distinguish_tickets_with_and_without_triage = Mock(
            return_value=(tickets_with_triage, tickets_without_triage)
        )
        triage._process_tickets_with_triage = CoroutineMock()
        triage._process_tickets_without_triage = CoroutineMock()

        await triage._run_tickets_polling()

        monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses.assert_not_awaited()
        triage._get_all_open_tickets_with_details_for_monitored_companies.assert_awaited_once()
        triage._filter_tickets_related_to_edges_under_monitoring.assert_called_once_with(open_tickets)
        triage._distinguish_tickets_with_and_without_triage.assert_called_once_with(relevant_tickets)
        triage._process_tickets_with_triage.assert_awaited_once_with(tickets_with_triage, edges_data_by_serial)
        triage._process_tickets_without_triage.assert_awaited_once_with(tickets_without_triage, edges_data_by_serial)

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

        edges_data_by_serial = {
            edge_1_serial: edge_1_data,
            edge_2_serial: edge_2_data,
            edge_3_serial: edge_3_data,
        }

        ticket_1 = {
            'ticket_id': 12345,
            'ticket_details': [
                {
                    "detailID": 2746930,
                    "detailValue": edge_1_serial,
                },
            ],
            'ticket_notes': {
                "noteId": 41894040,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        }
        ticket_2 = {
            'ticket_id': 67890,
            'ticket_details': [
                {
                    "detailID": 2746931,
                    "detailValue": edge_2_serial,
                },
            ],
            'ticket_notes': {
                "noteId": 41894041,
                "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        }
        ticket_3 = {
            'ticket_id': 11111,
            'ticket_details': [
                {
                    "detailID": 2746932,
                    "detailValue": edge_3_serial,
                },
            ],
            'ticket_notes': {
                "noteId": 41894042,
                "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30 06:38:00+00:00',
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
        }
        open_tickets = [ticket_1, ticket_2, ticket_3]
        relevant_tickets = [ticket_1, ticket_2, ticket_3]
        tickets_with_triage = [ticket_1, ticket_2]
        tickets_without_triage = [ticket_3]

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

        monitoring_map_repository = Mock()
        monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses = CoroutineMock()
        monitoring_map_repository.start_create_monitoring_map_job = CoroutineMock()
        monitoring_map_repository.get_monitoring_map_cache = Mock(return_value=monitoring_mapping)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_all_open_tickets_with_details_for_monitored_companies = CoroutineMock(return_value=open_tickets)
        triage._filter_tickets_related_to_edges_under_monitoring = Mock(return_value=relevant_tickets)
        triage._distinguish_tickets_with_and_without_triage = Mock(
            return_value=(tickets_with_triage, tickets_without_triage)
        )
        triage._process_tickets_with_triage = CoroutineMock()
        triage._process_tickets_without_triage = CoroutineMock()

        await triage._run_tickets_polling()

        monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses.assert_awaited_once()
        monitoring_map_repository.start_create_monitoring_map_job.assert_awaited_once()
        triage._get_all_open_tickets_with_details_for_monitored_companies.assert_awaited_once()
        triage._filter_tickets_related_to_edges_under_monitoring.assert_called_once_with(open_tickets)
        triage._distinguish_tickets_with_and_without_triage.assert_called_once_with(relevant_tickets)
        triage._process_tickets_with_triage.assert_awaited_once_with(tickets_with_triage, edges_data_by_serial)
        triage._process_tickets_without_triage.assert_awaited_once_with(tickets_without_triage, edges_data_by_serial)

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
        tickets_with_details = tickets_with_details_for_bruin_client_1 + tickets_with_details_for_bruin_client_2

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
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._monitoring_mapping = monitoring_mapping
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
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._monitoring_mapping = monitoring_mapping
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
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response, get_ticket_2_details_response
        ])

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
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
                'ticket_detail': ticket_1_details_item_1,
                'ticket_notes': ticket_1_notes,
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_detail': ticket_2_details_item_1,
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
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
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
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response, get_ticket_2_details_response
        ])

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
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
                'ticket_detail': ticket_2_details_item_1,
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
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response, get_ticket_2_details_response
        ])

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
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
                'ticket_detail': ticket_1_details_item_1,
                'ticket_notes': ticket_1_notes,
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
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._monitoring_mapping = monitoring_mapping

        result = triage._filter_tickets_related_to_edges_under_monitoring(tickets)

        expected = [ticket_1, ticket_3]
        assert result == expected

    def distinguish_tickets_with_and_without_triage_test(self):
        ticket_1 = {
            'ticket_id': 12345,
            'ticket_detail': {
                "detailID": 2746930,
                "detailValue": 'VC1234567',
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
                "detailValue": 'VC7654321',
            },
            'ticket_notes': [
                {
                    "noteId": 41894042,
                    "noteValue": None,
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894041,
                    "noteValue": 'This not is not a triage',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ]
        }
        ticket_3 = {
            'ticket_id': 11111,
            'ticket_detail': {
                "detailID": 2746932,
                "detailValue": 'VC1112223',
            },
            'ticket_notes': [
                {
                    "noteId": 41894042,
                    "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ]
        }
        ticket_4 = {
            'ticket_id': 11111,
            'ticket_detail': {
                "detailID": 2746932,
                "detailValue": 'VC1112223',
            },
            'ticket_notes': [
                {
                    "noteId": 41894042,
                    "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-07-30 06:38:00+00:00',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
            ]
        }
        tickets = [ticket_1, ticket_2, ticket_3, ticket_4]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        tickets_with_triage, tickets_without_triage = triage._distinguish_tickets_with_and_without_triage(tickets)

        assert tickets_with_triage == [ticket_1, ticket_3]
        assert tickets_without_triage == [ticket_2, ticket_4]

    @pytest.mark.asyncio
    async def process_tickets_with_triage_test(self):
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
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            },
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|67890|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            },
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|67890|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        edge_1_data = {'edge_id': edge_1_full_id, 'edge_status': edge_1_status}
        edge_2_data = {'edge_id': edge_2_full_id, 'edge_status': edge_2_status}
        edge_3_data = {'edge_id': edge_3_full_id, 'edge_status': edge_3_status}
        edges_data_by_serial = {
            edge_1_serial: edge_1_data,
            edge_2_serial: edge_2_data,
            edge_3_serial: edge_3_data,
        }

        ticket_1_id = 12345
        ticket_1_detail = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
        }
        ticket_1_note_1_creation_date = '2019-07-30T06:38:13.503-05:00'
        ticket_1_note_2_creation_date = '2019-03-30T06:38:13.503-05:00'
        ticket_1_note_3_creation_date = '2019-11-30T06:38:13.503-05:00'
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: {ticket_1_note_1_creation_date}',
            "createdDate": ticket_1_note_1_creation_date,
        }
        ticket_1_note_2 = {
            "noteId": 41894041,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: {ticket_1_note_2_creation_date}',
            "createdDate": ticket_1_note_2_creation_date,
        }
        ticket_1_note_3 = {
            "noteId": 41894042,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: {ticket_1_note_3_creation_date}',
            "createdDate": ticket_1_note_3_creation_date,
        }
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_detail': ticket_1_detail,
            'ticket_notes': [ticket_1_note_1, ticket_1_note_2, ticket_1_note_3]
        }

        ticket_2_id = 67890
        ticket_2_detail = {
            "detailID": 2746931,
            "detailValue": edge_2_serial,
        }
        ticket_2_note_1_creation_date = '2019-04-30T06:38:13.503-05:00'
        ticket_2_note_2_creation_date = '2019-04-30T06:38:13.503-05:00'
        ticket_2_note_3_creation_date = '2019-12-30T06:38:13.503-05:00'
        ticket_2_note_4_creation_date = '2019-03-30T06:38:13.503-05:00'
        ticket_2_note_1 = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: {ticket_2_note_1_creation_date}',
            "createdDate": ticket_2_note_1_creation_date,
        }
        ticket_2_note_2 = {
            "noteId": 41894044,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: {ticket_2_note_2_creation_date}',
            "createdDate": ticket_2_note_2_creation_date,
        }
        ticket_2_note_3 = {
            "noteId": 41894045,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: {ticket_2_note_3_creation_date}',
            "createdDate": ticket_2_note_3_creation_date,
        }
        ticket_2_note_4 = {
            "noteId": 41894046,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: {ticket_2_note_4_creation_date}',
            "createdDate": ticket_2_note_4_creation_date,
        }
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_detail': ticket_2_detail,
            'ticket_notes': [ticket_2_note_1, ticket_2_note_2, ticket_2_note_3, ticket_2_note_4]
        }

        tickets = [ticket_1, ticket_2]

        tickets_after_discarding_non_triage_notes = [
            {
                'ticket_id': ticket_1_id,
                'ticket_detail': ticket_1_detail,
                'ticket_notes': [ticket_1_note_2],
            },
            {
                'ticket_id': ticket_2_id,
                'ticket_detail': ticket_2_detail,
                'ticket_notes': [ticket_2_note_1, ticket_2_note_2, ticket_2_note_4],
            }
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._discard_non_triage_notes = Mock(wraps=triage._discard_non_triage_notes)
        triage._get_most_recent_ticket_note = Mock(side_effect=[ticket_1_note_2, ticket_2_note_3])
        triage._was_ticket_note_appended_recently = Mock(side_effect=[False, True])
        triage._append_new_triage_notes_based_on_recent_events = CoroutineMock()

        await triage._process_tickets_with_triage(tickets, edges_data_by_serial)

        triage._discard_non_triage_notes.assert_called_once_with(tickets)
        triage._get_most_recent_ticket_note.assert_has_calls([
            call(tickets_after_discarding_non_triage_notes[0]),
            call(tickets_after_discarding_non_triage_notes[1]),
        ])
        triage._was_ticket_note_appended_recently.assert_has_calls([
            call(ticket_1_note_2), call(ticket_2_note_3),
        ])
        triage._append_new_triage_notes_based_on_recent_events.assert_awaited_once_with(
            ticket_1_id, ticket_1_note_2_creation_date, edge_1_data
        )

    def discard_non_triage_notes_test(self):
        ticket_1_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
            "createdDate": '2019-07-30T06:38:13.503-05:00'
        }
        ticket_1_note_2 = {
            "noteId": 41894041,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
            "createdDate": '2019-07-30T06:38:13.503-05:00'
        }
        ticket_1_note_3 = {
            "noteId": 41894042,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
            "createdDate": '2019-07-30T06:38:13.503-05:00'
        }
        ticket_1 = {
            'ticket_id': 12345,
            'ticket_detail': {
                "detailID": 2746930,
                "detailValue": 'VC1234567',
            },
            'ticket_notes': [ticket_1_note_1, ticket_1_note_2, ticket_1_note_3]
        }

        ticket_2_note_1 = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-04-30T06:38:13.503-05:00',
        }
        ticket_2_note_2 = {
            "noteId": 41894044,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-04-30T06:38:13.503-05:00',
        }
        ticket_2_note_3 = {
            "noteId": 41894045,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-04-30T06:38:13.503-05:00',
        }
        ticket_2_note_4 = {
            "noteId": 41894046,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-04-30T06:38:13.503-05:00',
        }
        ticket_2 = {
            'ticket_id': 67890,
            'ticket_detail': {
                "detailID": 2746931,
                "detailValue": 'VC7654321',
            },
            'ticket_notes': [ticket_2_note_1, ticket_2_note_2, ticket_2_note_3, ticket_2_note_4]
        }

        tickets = [ticket_1, ticket_2]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        triage._discard_non_triage_notes(tickets)

        assert ticket_1['ticket_notes'] == [ticket_1_note_2]
        assert ticket_2['ticket_notes'] == [ticket_2_note_1, ticket_2_note_2, ticket_2_note_4]

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
            'ticket_detail': {
                "detailID": 2746931,
                "detailValue": 'VC7654321',
            },
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
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
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
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
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

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        client_id = 12345
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
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
            },
        }
        edge_data = {
            'edge_id': edge_full_id,
            'edge_status': edge_status
        }

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
        monitoring_map_repository = Mock()
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
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
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
            await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

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
            call(ticket_id, note_for_events_chunk_1),
            call(ticket_id, note_for_events_chunk_2),
            call(ticket_id, note_for_events_chunk_3),
            call(ticket_id, note_for_events_chunk_4),
        ])
        triage._notify_triage_note_was_appended_to_ticket.assert_awaited_once_with(ticket_id, client_id)

    @pytest.mark.asyncio
    async def append_new_triage_notes_based_on_recent_events_with_environment_different_from_production_test(self):
        ticket_id = 12345

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        client_id = 12345
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
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
            },
        }
        edge_data = {
            'edge_id': edge_full_id,
            'edge_status': edge_status
        }

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
        monitoring_map_repository = Mock()
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
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
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
            await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_called_once_with(events)
        triage_repository.build_events_note.assert_has_calls([
            call(events_chunk_1),
            call(events_chunk_2),
            call(events_chunk_3),
            call(events_chunk_4),
        ])
        bruin_repository.append_note_to_ticket.assert_not_awaited()
        triage._notify_triage_note_was_appended_to_ticket.assert_awaited_once_with(ticket_id, client_id)

    @pytest.mark.asyncio
    async def append_new_triage_notes_based_on_recent_events_with_events_sorted_by_event_time_before_chunking_test(
            self):
        ticket_id = 12345

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        client_id = 12345
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{client_id}|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            },
        }
        edge_data = {
            'edge_id': edge_full_id,
            'edge_status': edge_status
        }

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
        monitoring_map_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock()

        triage_repository = Mock()
        triage_repository.build_events_note = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_events_chunked = Mock(return_value=[])  # Just tricking this return value to "stop" execution here
        triage._notify_triage_note_was_appended_to_ticket = CoroutineMock()

        await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_called_once_with(events_sorted_by_event_time)

    @pytest.mark.asyncio
    async def append_new_triage_notes_based_on_recent_events_with_edge_events_request_not_having_2XX_status_test(self):
        ticket_id = 12345

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        client_id = 12345
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
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
            },
        }
        edge_data = {
            'edge_id': edge_full_id,
            'edge_status': edge_status
        }

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
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_events_chunked = Mock()

        await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_not_called()

    @pytest.mark.asyncio
    async def append_new_triage_notes_based_on_recent_events_with_edge_events_request_returning_no_events_test(self):
        ticket_id = 12345

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        client_id = 12345
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
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
            },
        }
        edge_data = {
            'edge_id': edge_full_id,
            'edge_status': edge_status
        }

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
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_events_chunked = Mock()

        await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_not_called()

    @pytest.mark.asyncio
    async def append_new_triage_notes_based_on_recent_events_with_append_note_request_not_having_2XX_status_test(self):
        ticket_id = 12345

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        client_id = 12345
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
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
            },
        }
        edge_data = {
            'edge_id': edge_full_id,
            'edge_status': edge_status
        }

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
        monitoring_map_repository = Mock()
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
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
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
            await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_called_once_with(events)
        triage_repository.build_events_note.assert_has_calls([
            call(events_chunk_1),
            call(events_chunk_2),
            call(events_chunk_3),
            call(events_chunk_4),
        ])
        bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id, note_for_events_chunk_1),
            call(ticket_id, note_for_events_chunk_2),
            call(ticket_id, note_for_events_chunk_3),
            call(ticket_id, note_for_events_chunk_4),
        ])
        triage._notify_triage_note_was_appended_to_ticket.assert_awaited_once_with(ticket_id, client_id)

    @pytest.mark.asyncio
    async def append_new_triage_notes_based_on_recent_events_with_no_notes_appended_to_ticket_test(self):
        ticket_id = 12345

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        client_id = 12345
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
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
            },
        }
        edge_data = {
            'edge_id': edge_full_id,
            'edge_status': edge_status
        }

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
        monitoring_map_repository = Mock()
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
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._get_events_chunked = Mock(return_value=[
            events_chunk_1,
            events_chunk_2,
        ])
        triage._notify_triage_note_was_appended_to_ticket = CoroutineMock()

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_called_once_with(events)
        triage_repository.build_events_note.assert_has_calls([
            call(events_chunk_1),
            call(events_chunk_2),
        ])
        bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id, note_for_events_chunk_1),
            call(ticket_id, note_for_events_chunk_2),
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
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
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
        bruin_client_id = 12345

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)

        await triage._notify_triage_note_was_appended_to_ticket(ticket_id, bruin_client_id)

        notifications_repository.send_slack_message.assert_awaited_once_with(
            f'Triage appended to ticket {ticket_id} in '
            f'{config.TRIAGE_CONFIG["environment"].upper()} environment. Details at '
            f'https://app.bruin.com/helpdesk?clientId={bruin_client_id}&ticketId={ticket_id}'
        )

    @pytest.mark.asyncio
    async def process_tickets_without_triage_test(self):
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
            'enterprise_name': 'EVIL-CORP|12345|',
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'METTEL/NEW YORK',
            },
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
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
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|67890|',
            'bruin_client_info': {
                'client_id': 67890,
                'client_name': 'METTEL/NEW YORK',
            },
        }

        edge_1_data = {'edge_id': edge_1_full_id, 'edge_status': edge_1_status}
        edge_2_data = {'edge_id': edge_2_full_id, 'edge_status': edge_2_status}
        edge_3_data = {'edge_id': edge_3_full_id, 'edge_status': edge_3_status}
        edges_data_by_serial = {
            edge_1_serial: edge_1_data,
            edge_2_serial: edge_2_data,
            edge_3_serial: edge_3_data,
        }

        ticket_1_id = 12345
        ticket_1_detail = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
        }
        ticket_1_note = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket_1 = {
            'ticket_id': ticket_1_id,
            'ticket_detail': ticket_1_detail,
            'ticket_notes': [ticket_1_note]
        }

        ticket_2_id = 67890
        ticket_2_detail = {
            "detailID": 6895947,
            "detailValue": edge_3_serial,
        }
        ticket_2_note = {
            "noteId": 8793897,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-18T06:38:13.503-05:00',
            "createdDate": '2019-07-18T06:38:13.503-05:00',
        }
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_detail': ticket_2_detail,
            'ticket_notes': [ticket_2_note]
        }

        tickets = [
            ticket_1,
            ticket_2,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        monitoring_map_repository = Mock()
        velocloud_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage._process_single_ticket_without_triage = CoroutineMock()

        await triage._process_tickets_without_triage(tickets, edges_data_by_serial)

        triage._process_single_ticket_without_triage.assert_has_awaits([
            call(ticket_1, edge_1_data),
            call(ticket_2, edge_3_data),
        ])

    @pytest.mark.asyncio
    async def process_single_ticket_without_triage_with_events_sorted_before_building_triage_note_test(self):
        edge_serial = 'VC1234567'

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial},
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

        edge_data = {'edge_id': edge_full_id, 'edge_status': edge_status}

        ticket_id = 12345
        ticket_detail = {
            "detailID": 2746930,
            "detailValue": edge_serial,
        }
        ticket_note = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket = {
            'ticket_id': ticket_id,
            'ticket_detail': ticket_detail,
            'ticket_notes': [ticket_note]
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

        last_events_response = {'body': events, 'status': 200}

        relevant_data_for_triage_note = {
            'data-1': 'some-data-1',
            'data-2': 'some-more-data-1',
            'data-3': 42,
            'data-4': 'Travis Touchdown',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        metrics_repository.increment_tickets_without_triage_processed = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value={
            'body': {'edge_id': edge_full_id, 'edge_info': edge_status}, 'status': 200
        })
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock(return_value=200)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage_repository.build_triage_note = Mock(return_value=relevant_data_for_triage_note)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_single_ticket_without_triage(ticket, edge_data)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup)
        triage_repository.build_triage_note.assert_called_once_with(
            edge_full_id, edge_status, events_sorted_by_event_time
        )
        bruin_repository.append_triage_note.assert_awaited_with(ticket_id, relevant_data_for_triage_note, edge_status)
        metrics_repository.increment_tickets_without_triage_processed.assert_called_once()

    @pytest.mark.asyncio
    async def process_single_ticket_without_triage_with_error_appending_triage_note_test(self):
        edge_serial = 'VC1234567'

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial},
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

        edge_data = {'edge_id': edge_full_id, 'edge_status': edge_status}

        ticket_id = 12345
        ticket_detail = {
            "detailID": 2746930,
            "detailValue": edge_serial,
        }
        ticket_note = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket = {
            'ticket_id': ticket_id,
            'ticket_detail': ticket_detail,
            'ticket_notes': [ticket_note]
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

        last_events_response = {'body': events, 'status': 200}

        relevant_data_for_triage_note = {
            'data-1': 'some-data-1',
            'data-2': 'some-more-data-1',
            'data-3': 42,
            'data-4': 'Travis Touchdown',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        metrics_repository.increment_note_append_errors = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value={
            'body': {'edge_id': edge_full_id, 'edge_info': edge_status}, 'status': 200
        })
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock(return_value=503)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage_repository.build_triage_note = Mock(return_value=relevant_data_for_triage_note)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_single_ticket_without_triage(ticket, edge_data)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup)
        triage_repository.build_triage_note.assert_called_once_with(
            edge_full_id, edge_status, events_sorted_by_event_time
        )
        bruin_repository.append_triage_note.assert_awaited_with(ticket_id, relevant_data_for_triage_note, edge_status)
        metrics_repository.increment_note_append_errors.assert_called_once()

    @pytest.mark.asyncio
    async def process_single_ticket_without_triage_with_edge_events_request_not_having_2xx_status_test(self):
        edge_serial = 'VC1234567'

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial},
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

        edge_data = {'edge_id': edge_full_id, 'edge_status': edge_status}

        ticket_id = 12345
        ticket_detail = {
            "detailID": 2746930,
            "detailValue": edge_serial,
        }
        ticket_note = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket = {
            'ticket_id': ticket_id,
            'ticket_detail': ticket_detail,
            'ticket_notes': [ticket_note]
        }

        event_1 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_2 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:40:00+00:00',
            'message': 'Link GE1 is now DEAD'
        }
        events = [event_1, event_2]

        last_events_response = {'body': events, 'status': 400}

        ticket_note = 'This is the first ticket note'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value={
            'body': {'edge_id': edge_full_id, 'edge_info': edge_status}, 'status': 200
        })
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_email = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage_repository.build_triage_note = Mock(return_value=ticket_note)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_single_ticket_without_triage(ticket, edge_data)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        triage_repository.build_triage_note.assert_not_called()
        bruin_repository.append_triage_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_single_ticket_without_triage_with_edge_events_request_returning_no_events_test(self):
        edge_serial = 'VC1234567'

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial},
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

        edge_data = {'edge_id': edge_full_id, 'edge_status': edge_status}

        ticket_id = 12345
        ticket_detail = {
            "detailID": 2746930,
            "detailValue": edge_serial,
        }
        ticket_note = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket = {
            'ticket_id': ticket_id,
            'ticket_detail': ticket_detail,
            'ticket_notes': [ticket_note]
        }

        events = []

        last_events_response = {'body': events, 'status': 200}

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value={
            'body': {'edge_id': edge_full_id, 'edge_info': edge_status}, 'status': 200
        })
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_email = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage_repository.build_triage_note = Mock()

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_single_ticket_without_triage(ticket, edge_data)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        triage_repository.build_triage_note.assert_not_called()
        bruin_repository.append_triage_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_single_ticket_without_triage_with_edge_status_request_not_having_2xx_status_test(self):
        edge_serial = 'VC1234567'

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_serial},
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

        edge_data = {'edge_id': edge_full_id, 'edge_status': edge_status}

        ticket_id = 12345
        ticket_detail = {
            "detailID": 2746930,
            "detailValue": edge_serial,
        }
        ticket_note = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-07-30T06:38:13.503-05:00',
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket = {
            'ticket_id': ticket_id,
            'ticket_detail': ticket_detail,
            'ticket_notes': [ticket_note]
        }

        event_1 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_2 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:40:00+00:00',
            'message': 'Link GE1 is now DEAD'
        }
        events = [event_1, event_2]

        last_events_response = {'body': events, 'status': 200}

        ticket_note = 'This is the first ticket note'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        monitoring_map_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock(return_value={
            'body': {'edge_id': edge_full_id, 'edge_info': edge_status}, 'status': 400
        })
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_email = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        monitoring_map_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository)
        triage_repository.build_triage_note = Mock(return_value=ticket_note)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_single_ticket_without_triage(ticket, edge_data)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        triage_repository.build_triage_note.assert_not_called()
        bruin_repository.append_triage_note.assert_not_awaited()
