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

from application import Outages
from application.actions import triage as triage_module
from application.actions.triage import Triage
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
        ha_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)

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
        assert triage._ha_repository is ha_repository

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
        ha_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)

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
        ha_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)

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
        ha_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_triage_monitoring = CoroutineMock(return_value=get_cache_response)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
        triage._build_edges_status_by_serial = CoroutineMock()
        triage._get_all_open_tickets_with_details_for_monitored_companies = CoroutineMock()
        triage._process_ticket_details_with_triage = CoroutineMock()
        triage._process_ticket_details_without_triage = CoroutineMock()

        await triage._run_tickets_polling()

        customer_cache_repository.get_cache_for_triage_monitoring.assert_awaited_once()
        triage._build_edges_status_by_serial.assert_not_awaited()
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
        ha_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_triage_monitoring = CoroutineMock(return_value=get_cache_response)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
        triage._build_edges_status_by_serial = CoroutineMock()
        triage._get_all_open_tickets_with_details_for_monitored_companies = CoroutineMock()
        triage._process_ticket_details_with_triage = CoroutineMock()
        triage._process_ticket_details_without_triage = CoroutineMock()

        await triage._run_tickets_polling()

        customer_cache_repository.get_cache_for_triage_monitoring.assert_awaited_once()
        triage._build_edges_status_by_serial.assert_not_awaited()
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
        links = [
            {
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "SFP1"
                ],
            },
            {
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "GE1"
                ],
            }
        ]

        customer_cache = [
            {
                'edge': edge_1_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_1_serial,
                'ha_serial_number': None,
                'bruin_client_info': {
                    'client_id': bruin_client_1,
                    'client_name': 'EVIL-CORP'
                },
                'links_configuration': links
            },
            {
                'edge': edge_2_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_2_serial,
                'ha_serial_number': None,
                'bruin_client_info': {
                    'client_id': bruin_client_2,
                    'client_name': 'EVIL-CORP'
                },
                'links_configuration': links
            },
            {
                'edge': edge_3_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_3_serial,
                'ha_serial_number': None,
                'bruin_client_info': {
                    'client_id': bruin_client_2,
                    'client_name': 'EVIL-CORP'
                },
                'links_configuration': links
            },
        ]

        get_cache_response = {
            'body': customer_cache,
            'status': 200,
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
                "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
                "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
                "noteValue": f"#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
                "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
        ha_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_triage_monitoring = CoroutineMock(return_value=get_cache_response)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
        triage._build_edges_status_by_serial = CoroutineMock()
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
        triage._build_edges_status_by_serial.assert_awaited_once()
        triage._get_all_open_tickets_with_details_for_monitored_companies.assert_awaited_once()
        triage._filter_tickets_and_details_related_to_edges_under_monitoring.assert_called_once_with(open_tickets)
        triage._filter_irrelevant_notes_in_tickets.assert_called_once_with(relevant_tickets)
        triage._get_ticket_details_with_and_without_triage.assert_called_once_with(
            relevant_tickets_with_notes_filtered
        )
        triage._process_ticket_details_with_triage.assert_awaited_once_with(
            ticket_details_with_triage)
        triage._process_ticket_details_without_triage.assert_awaited_once_with(
            ticket_details_without_triage)

    @pytest.mark.asyncio
    async def build_edges_status_by_serial_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        customer_cache_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        bruin_client_id = 12345

        edge_primary_serial = 'VC1234567'
        edge_standby_serial = 'VC7654321'

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        customer_cache = [
            {
                'edge': edge_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_primary_serial,
                'ha_serial_number': edge_standby_serial,
                'bruin_client_info': {
                    'client_id': bruin_client_id,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_standby_serial,
                'ha_serial_number': edge_primary_serial,
                'bruin_client_info': {
                    'client_id': bruin_client_id,
                    'client_name': 'EVIL-CORP'
                },
            },
        ]

        edge_primary_status = {
            # Some fields omitted for simplicity
            'edgeState': 'OFFLINE',
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_primary_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': 'OFFLINE',
            'haSerialNumber': edge_standby_serial,
            'haState': 'READY',
            'serialNumber': edge_primary_serial,
        }

        edge_primary_status_with_ha_info = {
            **edge_primary_status,
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': True,
        }
        edge_standby_status_with_ha_info = {
            **edge_primary_status,
            'edgeSerialNumber': edge_standby_serial,
            'edgeHASerialNumber': edge_primary_serial,
            'edgeState': 'CONNECTED',
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': False,
        }

        edges_statuses = [
            edge_primary_status,
        ]
        edges_network_enterprises = [
            edge_primary_network_enterprises,
        ]

        edge_primaries_statuses_with_ha_info = [
            edge_primary_status_with_ha_info,
        ]
        all_edge_statuses_with_ha_info = [
            edge_primary_status_with_ha_info,
            edge_standby_status_with_ha_info,
        ]

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_triage = CoroutineMock(return_value=edges_statuses)
        velocloud_repository.get_network_enterprises_for_triage = CoroutineMock(return_value=edges_network_enterprises)

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=edge_primaries_statuses_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(return_value=all_edge_statuses_with_ha_info)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
        triage._cached_info_by_serial = {
            elem['serial_number']: elem['edge']
            for elem in customer_cache
        }

        await triage._build_edges_status_by_serial()

        velocloud_repository.get_edges_for_triage.assert_awaited_once()
        velocloud_repository.get_network_enterprises_for_triage.assert_awaited_once()
        ha_repository.map_edges_with_ha_info.assert_called_once_with(edges_statuses, edges_network_enterprises)
        ha_repository.get_edges_with_standbys_as_standalone_edges.assert_called_once_with(
            edge_primaries_statuses_with_ha_info
        )

        assert triage._edges_status_by_serial == {
            edge_primary_serial: edge_primary_status_with_ha_info,
            edge_standby_serial: edge_standby_status_with_ha_info,
        }

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
                        "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
                        "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
                'ha_serial_number': None,
                'bruin_client_info': {
                    'client_id': bruin_client_1_id,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_2_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_2_serial,
                'ha_serial_number': None,
                'bruin_client_info': {
                    'client_id': bruin_client_2_id,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_3_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_3_serial,
                'ha_serial_number': None,
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
        ha_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
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
                        "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
                        "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
                'ha_serial_number': None,
                'bruin_client_info': {
                    'client_id': bruin_client_1_id,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_2_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_2_serial,
                'ha_serial_number': None,
                'bruin_client_info': {
                    'client_id': bruin_client_2_id,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_3_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_3_serial,
                'ha_serial_number': None,
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
        ha_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
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
                "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894042,
                "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
                "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894044,
                "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response, get_ticket_2_details_response
        ])

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)

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
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)

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
                "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894044,
                "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response, get_ticket_2_details_response
        ])

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)

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
                "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
                "createdDate": "2020-02-24T10:07:13.503-05:00",
            },
            {
                "noteId": 41894042,
                "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=get_open_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            get_ticket_1_details_response, get_ticket_2_details_response
        ])

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)

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
                'ha_serial_number': None,
                'bruin_client_info': {
                    'client_id': bruin_client_1_id,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_2_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_2_serial,
                'ha_serial_number': None,
                'bruin_client_info': {
                    'client_id': bruin_client_1_id,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_4_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_4_serial,
                'ha_serial_number': None,
                'bruin_client_info': {
                    'client_id': bruin_client_2_id,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': edge_5_full_id,
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': edge_5_serial,
                'ha_serial_number': None,
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
                "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
                    "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
                    "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
                    "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
        ha_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
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
                'ha_serial_number': None,
                'bruin_client_info': {
                    'client_id': 9994,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2},
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': service_number_2,
                'ha_serial_number': None,
                'bruin_client_info': {
                    'client_id': 9994,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3},
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': service_number_4,
                'ha_serial_number': None,
                'bruin_client_info': {
                    'client_id': 9994,
                    'client_name': 'EVIL-CORP'
                },
            },
            {
                'edge': {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 4},
                'last_contact': '2020-09-17T02:23:59',
                'serial_number': service_number_6,
                'ha_serial_number': None,
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
            "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
            "createdDate": f"#*MetTel's IPA*#\nAI\nTimeStamp: 2019-07-30 06:38:00+00:00",
            "serviceNumber": [
                service_number_1,
            ],
        }
        ticket_1_note_5 = {
            "noteId": 41894042,
            "noteValue": None,
            "createdDate": f"#*MetTel's IPA*#\nRe-opening ticket\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
            "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
            "createdDate": "2020-02-24T10:08:13.503-05:00",
            "serviceNumber": [
                service_number_2,
                service_number_4,
            ],
        }
        ticket_2_note_3 = {
            "noteId": 41894042,
            "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
            "noteValue": f"#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
        ha_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
        triage._customer_cache = customer_cache

        result = triage._filter_irrelevant_notes_in_tickets(tickets)

        expected = [
            {
                'ticket_id': ticket_1_id,
                'ticket_details': ticket_1_details,
                'ticket_notes': [
                    {
                        "noteId": 41894041,
                        "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
                        "noteValue": f"#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
            "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
            "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
            "createdDate": "2020-02-24T10:07:13.503-05:00",
            "serviceNumber": [
                serial_number_2,
                serial_number_4,
            ],
        }
        ticket_2_note_2 = {
            "noteId": 41894041,
            "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
            "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
        ha_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)

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

        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }
        logical_id_list = [{'interface_name': 'GE1', 'logical_id': '123'}]
        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'ha_serial_number': None,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'ha_serial_number': None,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }
        cached_edge_3 = {
            'edge': edge_3_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_3_serial,
            'ha_serial_number': None,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }
        edges_data_by_serial = {
            edge_1_serial: cached_edge_1,
            edge_2_serial: cached_edge_2,
            edge_3_serial: cached_edge_3,
        }

        ticket_detail_1_ticket_id = 12345
        ticket_detail_1_detail = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
        }
        ticket_detail_1_note_1_creation_date = '2019-07-30T06:38:13.503-05:00'
        ticket_detail_1_note_1 = {
            "noteId": 41894041,
            "noteValue": (
                f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: {ticket_detail_1_note_1_creation_date}"
            ),
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
            "noteValue": (
                f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: {ticket_detail_2_note_1_creation_date}"
            ),
            "createdDate": ticket_detail_2_note_1_creation_date,
        }
        ticket_detail_2_note_2 = {
            "noteId": 41894044,
            "noteValue": (
                f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: {ticket_detail_2_note_2_creation_date}"
            ),
            "createdDate": ticket_detail_2_note_2_creation_date,
        }
        ticket_detail_2_note_3 = {
            "noteId": 41894046,
            "noteValue": (
                f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: {ticket_detail_2_note_3_creation_date}"
            ),
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
        ha_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
        triage._cached_info_by_serial = edges_data_by_serial
        triage._get_most_recent_ticket_note = Mock(side_effect=[ticket_detail_1_note_1, ticket_detail_2_note_3])
        triage._was_ticket_note_appended_recently = Mock(side_effect=[False, True])
        triage._append_new_triage_notes_based_on_recent_events = CoroutineMock()

        await triage._process_ticket_details_with_triage(ticket_details)

        triage._get_most_recent_ticket_note.assert_has_calls([
            call(ticket_detail_1),
            call(ticket_detail_2),
        ])
        triage._was_ticket_note_appended_recently.assert_has_calls([
            call(ticket_detail_1_note_1), call(ticket_detail_2_note_3),
        ])
        triage._append_new_triage_notes_based_on_recent_events.assert_awaited_once_with(
            ticket_detail_1, ticket_detail_1_note_1_creation_date, edge_1_full_id
        )

    def get_most_recent_ticket_note_test(self):
        ticket_note_1 = {
            "noteId": 41894043,
            "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-04-30T06:38:13.503-05:00",
            "createdDate": '2019-12-30T06:38:13.503-05:00',
        }
        ticket_note_2 = {
            "noteId": 41894044,
            "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-04-30T06:38:13.503-05:00",
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket_note_3 = {
            "noteId": 41894046,
            "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-04-30T06:38:13.503-05:00",
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
        ha_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)

        newest_triage_note = triage._get_most_recent_ticket_note(ticket)

        assert newest_triage_note is ticket_note_1

    def was_ticket_note_appended_recently_test(self):
        ticket_note = {
            "noteId": 41894043,
            "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-04-30T06:38:13.503-05:00",
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
        ha_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)

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
                    "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30T06:38:13.503-05:00",
                    "createdDate": '2019-07-30T06:38:13.503-05:00',
                }
            ]
        }

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_data = edge_full_id

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
        ha_repository = Mock()

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
                        triage_repository, metrics_repository, ha_repository)
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
                    "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30T06:38:13.503-05:00",
                    "createdDate": '2019-07-30T06:38:13.503-05:00',
                }
            ]
        }

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_data = edge_full_id

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
        ha_repository = Mock()

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
                        triage_repository, metrics_repository, ha_repository)
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
                    "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30T06:38:13.503-05:00",
                    "createdDate": '2019-07-30T06:38:13.503-05:00',
                }
            ]
        }

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_data = edge_full_id

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
        ha_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        bruin_repository = Mock()
        bruin_repository.append_note_to_ticket = CoroutineMock()

        triage_repository = Mock()
        triage_repository.build_events_note = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
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
                    "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30T06:38:13.503-05:00",
                    "createdDate": '2019-07-30T06:38:13.503-05:00',
                }
            ]
        }

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_data = edge_full_id

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
        ha_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
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
                    "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30T06:38:13.503-05:00",
                    "createdDate": '2019-07-30T06:38:13.503-05:00',
                }
            ]
        }

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_data = edge_full_id

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
        ha_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
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
                    "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30T06:38:13.503-05:00",
                    "createdDate": '2019-07-30T06:38:13.503-05:00',
                }
            ]
        }

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_data = edge_full_id

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
        ha_repository = Mock()

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
                        triage_repository, metrics_repository, ha_repository)
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
                    "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30T06:38:13.503-05:00",
                    "createdDate": '2019-07-30T06:38:13.503-05:00',
                }
            ]
        }

        last_triage_timestamp = "2019-07-30T15:08:22.857-05:00"
        last_triage_datetime = parse(last_triage_timestamp)

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_data = edge_full_id

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
        ha_repository = Mock()

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
                        triage_repository, metrics_repository, ha_repository)
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
        ha_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)

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
                    "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30T06:38:13.503-05:00",
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
        ha_repository = Mock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)

        await triage._notify_triage_note_was_appended_to_ticket(ticket_detail)

        notifications_repository.send_slack_message.assert_awaited_once_with(
            f'Triage appended to detail {ticket_detail_id} (serial: {service_number}) of ticket {ticket_id}. '
            f'Details at https://app.bruin.com/t/{ticket_id}'
        )

    @pytest.mark.asyncio
    async def process_ticket_details_without_triage_with_edge_status_not_found_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC1111111'

        edge_1_ha_partner_serial = 'VC9999999'
        edge_2_ha_partner_serial = None

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}

        links_configuration = [
            {
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "GE7"
                ],
            },
            {
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "GE1"
                ],
            },
            {
                "mode": "PRIVATE",
                "type": "WIRED",
                "interfaces": [
                    "INTERNET3"
                ],
            }
        ]
        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }
        logical_id_list = [{'interface_name': 'GE1', 'logical_id': '123'}]
        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'ha_serial_number': edge_1_ha_partner_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
            'links_configuration': links_configuration
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'ha_serial_number': edge_2_ha_partner_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
            'links_configuration': links_configuration
        }
        cached_edge_1_ha_partner = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_ha_partner_serial,
            'ha_serial_number': edge_1_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
            'links_configuration': links_configuration
        }
        cached_edges_by_serial = {
            edge_1_serial: cached_edge_1,
            edge_2_serial: cached_edge_2,
            edge_1_ha_partner_serial: cached_edge_1_ha_partner,
        }

        ticket_detail_1_ticket_id = 12345
        ticket_detail_1_detail = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
        }
        ticket_detail_1_note = {
            "noteId": 41894040,
            "noteValue": f"#*MetTel's IPA*#\nAuto-resolving detail\nTimeStamp: 2019-07-30T06:38:13.503-05:00",
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
            "detailValue": edge_2_serial,
        }
        ticket_detail_2_note = {
            "noteId": 8793897,
            "noteValue": f"#*MetTel's IPA*#\nAuto-resolving detail\nTimeStamp: 2019-07-18T06:38:13.503-05:00",
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

        edge_status_by_serial = {}

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
        triage._cached_info_by_serial = cached_edges_by_serial
        triage._edges_status_by_serial = edge_status_by_serial
        triage._append_new_triage_notes_based_on_recent_events = CoroutineMock()

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        with patch.object(triage_module, 'datetime', new=datetime_mock):
            with patch.object(triage_module, 'utc', new=Mock()):
                await triage._process_ticket_details_without_triage(tickets)

        outage_repository.get_outage_type_by_edge_status.assert_not_called()
        triage._append_new_triage_notes_based_on_recent_events.assert_not_awaited()
        velocloud_repository.get_last_edge_events.assert_not_awaited()
        outage_repository.should_document_outage.assert_not_called()
        triage_repository.build_triage_note.assert_not_called()
        bruin_repository.append_triage_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_ticket_details_without_triage_with_no_outage_detected_for_edge_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC1111111'

        edge_1_ha_partner_serial = 'VC9999999'
        edge_2_ha_partner_serial = None

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}

        links_configuration = [
            {
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "GE7"
                ],
            },
            {
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "GE1"
                ],
            },
            {
                "mode": "PRIVATE",
                "type": "WIRED",
                "interfaces": [
                    "INTERNET3"
                ],
            }
        ]
        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }
        logical_id_list = [{'interface_name': 'GE1', 'logical_id': '123'}]
        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'ha_serial_number': edge_1_ha_partner_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
            'links_configuration': links_configuration
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'ha_serial_number': edge_2_ha_partner_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
            'links_configuration': links_configuration
        }
        cached_edge_1_ha_partner = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_ha_partner_serial,
            'ha_serial_number': edge_1_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
            'links_configuration': links_configuration
        }
        cached_edges_by_serial = {
            edge_1_serial: cached_edge_1,
            edge_2_serial: cached_edge_2,
            edge_1_ha_partner_serial: cached_edge_1_ha_partner,
        }

        ticket_detail_1_ticket_id = 12345
        ticket_detail_1_detail = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
        }
        ticket_detail_1_note = {
            "noteId": 41894040,
            "noteValue": f"#*MetTel's IPA*#\nAuto-resolving detail\nTimeStamp: 2019-07-30T06:38:13.503-05:00",
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
            "detailValue": edge_2_serial,
        }
        ticket_detail_2_note = {
            "noteId": 8793897,
            "noteValue": f"#*MetTel's IPA*#\nAuto-resolving detail\nTimeStamp: 2019-07-18T06:38:13.503-05:00",
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

        edge_1_status = {
            # Some fields omitted for simplicity
            'host': 'some-host',
            'enterpriseId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeId': 1,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': edge_1_ha_partner_serial,
            'links': [
                {
                    'interface': 'GE1',
                    'linkState': 'STABLE',
                    'linkId': 5293,
                },
            ],
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': True,
        }
        edge_2_status = {
            # Some fields omitted for simplicity
            'host': 'some-host',
            'enterpriseId': 1,
            'edgeName': 'Sniper Wolf',
            'edgeState': 'CONNECTED',
            'edgeId': 1,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': edge_2_ha_partner_serial,
            'links': [
                {
                    'interface': 'GE1',
                    'linkState': 'STABLE',
                    'linkId': 5293,
                },
            ],
            'edgeHAState': None,
            'edgeIsHAPrimary': None,
        }
        edge_1_ha_partner_status = {
            # Some fields omitted for simplicity
            'host': 'some-host',
            'enterpriseId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeId': 1,
            'edgeSerialNumber': edge_1_ha_partner_serial,
            'edgeHASerialNumber': edge_1_serial,
            'links': [
                {
                    'interface': 'GE1',
                    'linkState': 'STABLE',
                    'linkId': 5293,
                },
            ],
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': False,
        }
        edge_status_by_serial = {
            edge_1_serial: edge_1_status,
            edge_2_serial: edge_2_status,
            edge_1_ha_partner_serial: edge_1_ha_partner_status,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock()

        outage_repository = Mock()
        outage_repository.get_outage_type_by_edge_status = Mock(return_value=None)

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
        triage._cached_info_by_serial = cached_edges_by_serial
        triage._edges_status_by_serial = edge_status_by_serial
        triage._append_new_triage_notes_based_on_recent_events = CoroutineMock()

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=1)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        with patch.object(triage_module, 'datetime', new=datetime_mock):
            with patch.object(triage_module, 'utc', new=Mock()):
                await triage._process_ticket_details_without_triage(tickets)

        outage_repository.get_outage_type_by_edge_status.assert_has_calls([
            call(edge_1_status),
            call(edge_2_status),
        ])
        triage._append_new_triage_notes_based_on_recent_events.assert_has_awaits([
            call(ticket_detail_1, str(past_moment_for_events_lookup), edge_1_full_id),
            call(ticket_detail_2, str(past_moment_for_events_lookup), edge_2_full_id),
        ])
        velocloud_repository.get_last_edge_events.assert_not_awaited()
        outage_repository.should_document_outage.assert_not_called()
        triage_repository.build_triage_note.assert_not_called()
        bruin_repository.append_triage_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_ticket_details_without_triage_with_outage_detected_and_events_request_not_having_2xx_status_test(
            self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC1111111'

        edge_1_ha_partner_serial = 'VC9999999'
        edge_2_ha_partner_serial = None

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}

        links_configuration = [
            {
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "GE7"
                ],
            },
            {
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "GE1"
                ],
            },
            {
                "mode": "PRIVATE",
                "type": "WIRED",
                "interfaces": [
                    "INTERNET3"
                ],
            }
        ]
        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }
        logical_id_list = [{'interface_name': 'GE1', 'logical_id': '123'}]
        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'ha_serial_number': edge_1_ha_partner_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
            'links_configuration': links_configuration
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'ha_serial_number': edge_2_ha_partner_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
            'links_configuration': links_configuration
        }
        cached_edge_1_ha_partner = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_ha_partner_serial,
            'ha_serial_number': edge_1_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
            'links_configuration': links_configuration
        }
        cached_edges_by_serial = {
            edge_1_serial: cached_edge_1,
            edge_2_serial: cached_edge_2,
            edge_1_ha_partner_serial: cached_edge_1_ha_partner,
        }

        ticket_detail_1_ticket_id = 12345
        ticket_detail_1_detail = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
        }
        ticket_detail_1_note = {
            "noteId": 41894040,
            "noteValue": f"#*MetTel's IPA*#\nAuto-resolving detail\nTimeStamp: 2019-07-30T06:38:13.503-05:00",
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
            "detailValue": edge_2_serial,
        }
        ticket_detail_2_note = {
            "noteId": 8793897,
            "noteValue": f"#*MetTel's IPA*#\nAuto-resolving detail\nTimeStamp: 2019-07-18T06:38:13.503-05:00",
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

        edge_1_status = {
            # Some fields omitted for simplicity
            'host': 'some-host',
            'enterpriseId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeId': 1,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': edge_1_ha_partner_serial,
            'links': [
                {
                    'interface': 'GE1',
                    'linkState': 'STABLE',
                    'linkId': 5293,
                },
            ],
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': True,
        }
        edge_2_status = {
            # Some fields omitted for simplicity
            'host': 'some-host',
            'enterpriseId': 1,
            'edgeName': 'Sniper Wolf',
            'edgeState': 'CONNECTED',
            'edgeId': 1,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': edge_2_ha_partner_serial,
            'links': [
                {
                    'interface': 'GE1',
                    'linkState': 'STABLE',
                    'linkId': 5293,
                },
            ],
            'edgeHAState': None,
            'edgeIsHAPrimary': None,
        }
        edge_1_ha_partner_status = {
            # Some fields omitted for simplicity
            'host': 'some-host',
            'enterpriseId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeId': 1,
            'edgeSerialNumber': edge_1_ha_partner_serial,
            'edgeHASerialNumber': edge_1_serial,
            'links': [
                {
                    'interface': 'GE1',
                    'linkState': 'STABLE',
                    'linkId': 5293,
                },
            ],
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': False,
        }
        edge_status_by_serial = {
            edge_1_serial: edge_1_status,
            edge_2_serial: edge_2_status,
            edge_1_ha_partner_serial: edge_1_ha_partner_status,
        }

        outage_type = Outages.HA_HARD_DOWN

        last_events_response = {
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        metrics_repository = Mock()
        triage_repository = Mock()
        ha_repository = Mock()

        outage_repository = Mock()
        outage_repository.get_outage_type_by_edge_status = Mock(return_value=outage_type)

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=last_events_response)

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
        triage._cached_info_by_serial = cached_edges_by_serial
        triage._edges_status_by_serial = edge_status_by_serial
        triage._append_new_triage_notes_based_on_recent_events = CoroutineMock()

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        with patch.object(triage_module, 'datetime', new=datetime_mock):
            with patch.object(triage_module, 'utc', new=Mock()):
                await triage._process_ticket_details_without_triage(tickets)

        outage_repository.get_outage_type_by_edge_status.assert_has_calls([
            call(edge_1_status),
            call(edge_2_status),
        ])
        triage._append_new_triage_notes_based_on_recent_events.assert_not_awaited()
        velocloud_repository.get_last_edge_events.assert_has_awaits([
            call(edge_1_full_id, since=past_moment_for_events_lookup),
            call(edge_2_full_id, since=past_moment_for_events_lookup),
        ])
        outage_repository.should_document_outage.assert_not_called()
        triage_repository.build_triage_note.assert_not_called()
        bruin_repository.append_triage_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_ticket_details_without_triage_with_outage_detected_that_should_not_be_documented_test(self):
        edge_serial = 'VC1234567'
        edge_ha_partner_serial = 'VC9999999'

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        links_configuration = [
            {
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "GE7"
                ],
            },
            {
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "GE1"
                ],
            },
            {
                "mode": "PRIVATE",
                "type": "WIRED",
                "interfaces": [
                    "INTERNET3"
                ],
            }
        ]
        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }
        logical_id_list = [{'interface_name': 'GE1', 'logical_id': '123'}]
        cached_edge = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_serial,
            'ha_serial_number': edge_ha_partner_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
            'links_configuration': links_configuration
        }
        cached_edge_ha_partner = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_ha_partner_serial,
            'ha_serial_number': edge_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
            'links_configuration': links_configuration
        }
        cached_edges_by_serial = {
            edge_serial: cached_edge,
            edge_ha_partner_serial: cached_edge_ha_partner,
        }

        ticket_detail_1_ticket_id = 12345
        ticket_detail_1_detail = {
            "detailID": 2746930,
            "detailValue": edge_ha_partner_serial,
        }
        ticket_detail_1_note = {
            "noteId": 41894040,
            "noteValue": f"#*MetTel's IPA*#\nAuto-resolving detail\nTimeStamp: 2019-07-30T06:38:13.503-05:00",
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket_detail_1 = {
            'ticket_id': ticket_detail_1_ticket_id,
            'ticket_detail': ticket_detail_1_detail,
            'ticket_notes': [ticket_detail_1_note]
        }

        tickets = [
            ticket_detail_1,
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
        edge_events = [event_1, event_2]
        edge_last_events_response = {
            'body': edge_events,
            'status': 200,
        }

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'some-host',
            'enterpriseId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeId': 1,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': edge_ha_partner_serial,
            'links': [
                {
                    'interface': 'GE1',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': True,
        }
        edge_ha_partner_status = {
            # Some fields omitted for simplicity
            'host': 'some-host',
            'enterpriseId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeId': 1,
            'edgeSerialNumber': edge_ha_partner_serial,
            'edgeHASerialNumber': edge_serial,
            'links': [
                {
                    'interface': 'GE1',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': False,
        }
        edge_status_by_serial = {
            edge_serial: edge_status,
            edge_ha_partner_serial: edge_ha_partner_status,
        }

        outage_type = Outages.HA_HARD_DOWN

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=edge_last_events_response)

        outage_repository = Mock()
        outage_repository.get_outage_type_by_edge_status = Mock(return_value=outage_type)
        outage_repository.should_document_outage = Mock(return_value=False)

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
        triage._cached_info_by_serial = cached_edges_by_serial
        triage._edges_status_by_serial = edge_status_by_serial
        triage._append_new_triage_notes_based_on_recent_events = CoroutineMock()

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        with patch.object(triage_module, 'datetime', new=datetime_mock):
            with patch.object(triage_module, 'utc', new=Mock()):
                await triage._process_ticket_details_without_triage(tickets)

        outage_repository.get_outage_type_by_edge_status.assert_called_once_with(edge_ha_partner_status)
        triage._append_new_triage_notes_based_on_recent_events.assert_not_awaited()
        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        outage_repository.should_document_outage.assert_called_once_with(edge_ha_partner_status)
        triage_repository.build_triage_note.assert_not_called()
        bruin_repository.append_triage_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_ticket_details_without_triage_with_outage_detected_and_error_appending_triage_note_test(self):
        edge_serial = 'VC1234567'
        edge_ha_partner_serial = 'VC9999999'

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        links_configuration = [
            {
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "GE7"
                ],
            },
            {
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "GE1"
                ],
            },
            {
                "mode": "PRIVATE",
                "type": "WIRED",
                "interfaces": [
                    "INTERNET3"
                ],
            }
        ]
        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }
        logical_id_list = [{'interface_name': 'GE1', 'logical_id': '123'}]
        cached_edge = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_serial,
            'ha_serial_number': edge_ha_partner_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
            'links_configuration': links_configuration
        }
        cached_edge_ha_partner = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_ha_partner_serial,
            'ha_serial_number': edge_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
            'links_configuration': links_configuration
        }
        cached_edges_by_serial = {
            edge_serial: cached_edge,
            edge_ha_partner_serial: cached_edge_ha_partner,
        }

        ticket_detail_1_ticket_id = 12345
        ticket_detail_1_detail = {
            "detailID": 2746930,
            "detailValue": edge_serial,
        }
        ticket_detail_1_note = {
            "noteId": 41894040,
            "noteValue": f"#*MetTel's IPA*#\nAuto-resolving detail\nTimeStamp: 2019-07-30T06:38:13.503-05:00",
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket_detail_1 = {
            'ticket_id': ticket_detail_1_ticket_id,
            'ticket_detail': ticket_detail_1_detail,
            'ticket_notes': [ticket_detail_1_note]
        }

        tickets = [
            ticket_detail_1,
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
        edge_events = [event_1, event_2]
        edge_last_events_response = {
            'body': edge_events,
            'status': 200,
        }

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'some-host',
            'enterpriseId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeId': 1,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': edge_ha_partner_serial,
            'links': [
                {
                    'interface': 'GE1',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': True,
        }
        edge_ha_partner_status = {
            # Some fields omitted for simplicity
            'host': 'some-host',
            'enterpriseId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeId': 1,
            'edgeSerialNumber': edge_ha_partner_serial,
            'edgeHASerialNumber': edge_serial,
            'links': [
                {
                    'interface': 'GE1',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': False,
        }
        edge_status_by_serial = {
            edge_serial: edge_status,
            edge_ha_partner_serial: edge_ha_partner_status,
        }

        outage_type = Outages.HA_HARD_DOWN

        triage_note = 'Some info about the edge'
        append_triage_note_response_status = 503

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=edge_last_events_response)

        outage_repository = Mock()
        outage_repository.get_outage_type_by_edge_status = Mock(return_value=outage_type)
        outage_repository.should_document_outage = Mock(return_value=True)

        triage_repository = Mock()
        triage_repository.build_triage_note = Mock(return_value=triage_note)

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock(return_value=append_triage_note_response_status)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
        triage._cached_info_by_serial = cached_edges_by_serial
        triage._edges_status_by_serial = edge_status_by_serial
        triage._append_new_triage_notes_based_on_recent_events = CoroutineMock()

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        with patch.object(triage_module, 'datetime', new=datetime_mock):
            with patch.object(triage_module, 'utc', new=Mock()):
                await triage._process_ticket_details_without_triage(tickets)

        outage_repository.get_outage_type_by_edge_status.assert_called_once_with(edge_status)
        triage._append_new_triage_notes_based_on_recent_events.assert_not_awaited()
        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        outage_repository.should_document_outage.assert_called_once_with(edge_status)
        triage_repository.build_triage_note.assert_called_once_with(cached_edge, edge_status, edge_events, outage_type)
        bruin_repository.append_triage_note.assert_awaited_once_with(ticket_detail_1, triage_note)
        metrics_repository.increment_note_append_errors.assert_called_once()

    @pytest.mark.asyncio
    async def process_ticket_details_without_triage_with_outage_detected_ok_test(self):
        edge_serial = 'VC1234567'
        edge_ha_partner_serial = 'VC9999999'

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        links_configuration = [
            {
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "GE7"
                ],
            },
            {
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "GE1"
                ],
            },
            {
                "mode": "PRIVATE",
                "type": "WIRED",
                "interfaces": [
                    "INTERNET3"
                ],
            }
        ]
        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }
        logical_id_list = [{'interface_name': 'GE1', 'logical_id': '123'}]
        cached_edge = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_serial,
            'ha_serial_number': edge_ha_partner_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
            'links_configuration': links_configuration
        }
        cached_edge_ha_partner = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_ha_partner_serial,
            'ha_serial_number': edge_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
            'links_configuration': links_configuration
        }
        cached_edges_by_serial = {
            edge_serial: cached_edge,
            edge_ha_partner_serial: cached_edge_ha_partner,
        }

        ticket_detail_1_ticket_id = 12345
        ticket_detail_1_detail = {
            "detailID": 2746930,
            "detailValue": edge_serial,
        }
        ticket_detail_1_note = {
            "noteId": 41894040,
            "noteValue": f"#*MetTel's IPA*#\nAuto-resolving detail\nTimeStamp: 2019-07-30T06:38:13.503-05:00",
            "createdDate": '2019-07-30T06:38:13.503-05:00',
        }
        ticket_detail_1 = {
            'ticket_id': ticket_detail_1_ticket_id,
            'ticket_detail': ticket_detail_1_detail,
            'ticket_notes': [ticket_detail_1_note]
        }

        tickets = [
            ticket_detail_1,
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
        edge_events = [event_1, event_2]
        edge_last_events_response = {
            'body': edge_events,
            'status': 200,
        }

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'some-host',
            'enterpriseId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeId': 1,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': edge_ha_partner_serial,
            'links': [
                {
                    'interface': 'GE1',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': True,
        }
        edge_ha_partner_status = {
            # Some fields omitted for simplicity
            'host': 'some-host',
            'enterpriseId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeId': 1,
            'edgeSerialNumber': edge_ha_partner_serial,
            'edgeHASerialNumber': edge_serial,
            'links': [
                {
                    'interface': 'GE1',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': False,
        }
        edge_status_by_serial = {
            edge_serial: edge_status,
            edge_ha_partner_serial: edge_ha_partner_status,
        }

        outage_type = Outages.HA_HARD_DOWN

        triage_note = 'Some info about the edge'
        append_triage_note_response_status = 200

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()
        metrics_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=edge_last_events_response)

        outage_repository = Mock()
        outage_repository.get_outage_type_by_edge_status = Mock(return_value=outage_type)
        outage_repository.should_document_outage = Mock(return_value=True)

        triage_repository = Mock()
        triage_repository.build_triage_note = Mock(return_value=triage_note)

        bruin_repository = Mock()
        bruin_repository.append_triage_note = CoroutineMock(return_value=append_triage_note_response_status)

        triage = Triage(event_bus, logger, scheduler, config, outage_repository,
                        customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                        triage_repository, metrics_repository, ha_repository)
        triage._cached_info_by_serial = cached_edges_by_serial
        triage._edges_status_by_serial = edge_status_by_serial

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        with patch.object(triage_module, 'datetime', new=datetime_mock):
            with patch.object(triage_module, 'utc', new=Mock()):
                await triage._process_ticket_details_without_triage(tickets)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        outage_repository.get_outage_type_by_edge_status.assert_called_once_with(edge_status)
        outage_repository.should_document_outage.assert_called_once_with(edge_status)
        triage_repository.build_triage_note.assert_called_once_with(cached_edge, edge_status, edge_events, outage_type)
        bruin_repository.append_triage_note.assert_awaited_once_with(ticket_detail_1, triage_note)
        metrics_repository.increment_tickets_without_triage_processed.assert_called_once()
