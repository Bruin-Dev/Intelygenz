import os

from collections import OrderedDict
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
from pytz import timezone
from shortuuid import uuid

from application.actions.triage import empty_str
from application.actions.triage import Triage
from application.actions import triage as triage_module
from application.repositories.edge_redis_repository import EdgeIdentifier
from config import testconfig


class TestTriage:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        assert triage._event_bus is event_bus
        assert triage._logger is logger
        assert triage._scheduler is scheduler
        assert triage._config is config
        assert triage._outage_repository is outage_repository

    @pytest.mark.asyncio
    async def start_triage_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        await triage.start_triage_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            triage._run_tickets_polling, 'interval',
            minutes=config.TRIAGE_CONFIG["polling_minutes"],
            next_run_time=undefined,
            replace_existing=True,
            id='_triage_process',
        )

    @pytest.mark.asyncio
    async def run_tickets_polling_test(self):
        bruin_client_1 = 12345
        bruin_client_2 = 67890
        bruin_clients = [bruin_client_1, bruin_client_2]

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'
        edges_serials = [edge_1_serial, edge_2_serial, edge_3_serial]

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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._map_bruin_client_ids_to_edges_serials_and_statuses = CoroutineMock(return_value=monitoring_mapping)
        triage._get_all_open_tickets_with_details_for_monitored_companies = CoroutineMock(return_value=open_tickets)
        triage._filter_tickets_related_to_edges_under_monitoring = Mock(return_value=relevant_tickets)
        triage._distinguish_tickets_with_and_without_triage = Mock(
            return_value=(tickets_with_triage, tickets_without_triage)
        )
        triage._process_tickets_with_triage = CoroutineMock()
        triage._process_tickets_without_triage = CoroutineMock()

        await triage._run_tickets_polling()

        triage._map_bruin_client_ids_to_edges_serials_and_statuses.assert_awaited_once()
        triage._get_all_open_tickets_with_details_for_monitored_companies.assert_awaited_once_with(bruin_clients)
        triage._filter_tickets_related_to_edges_under_monitoring.assert_called_once_with(open_tickets, edges_serials)
        triage._distinguish_tickets_with_and_without_triage.assert_called_once_with(relevant_tickets)
        triage._process_tickets_with_triage.assert_awaited_once_with(tickets_with_triage, edges_data_by_serial)
        triage._process_tickets_without_triage.assert_awaited_once_with(tickets_without_triage, edges_data_by_serial)

    @pytest.mark.asyncio
    async def map_bruin_client_ids_to_edges_serials_and_statuses_test(self):
        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}
        edge_list_response = {
            'body': [edge_1_full_id, edge_2_full_id, edge_3_full_id],
            'status': 200
        }

        bruin_client_1 = 12345
        bruin_client_2 = 54321
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_1_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_1}|',
        }
        edge_1_status_response = {
            'body': {
                'edge_id': edge_1_full_id,
                'edge_info': edge_1_status,
            },
            'status': 200,
        }

        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_2}|',
        }
        edge_2_status_response = {
            'body': {
                'edge_id': edge_2_full_id,
                'edge_info': edge_2_status,
            },
            'status': 200,
        }

        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_2}|',
        }
        edge_3_status_response = {
            'body': {
                'edge_id': edge_3_full_id,
                'edge_info': edge_3_status,
            },
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_edges_for_triage_monitoring = CoroutineMock(return_value=edge_list_response)
        triage._get_edge_status_by_id = CoroutineMock(side_effect=[
            edge_1_status_response,
            edge_2_status_response,
            edge_3_status_response,
        ])

        result = await triage._map_bruin_client_ids_to_edges_serials_and_statuses()

        triage._get_edges_for_triage_monitoring.assert_awaited_once()
        triage._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id),
            call(edge_2_full_id),
            call(edge_3_full_id),
        ])

        expected = {
            bruin_client_1: {
                edge_1_serial: {'edge_id': edge_1_full_id, 'edge_status': edge_1_status},
            },
            bruin_client_2: {
                edge_2_serial: {'edge_id': edge_2_full_id, 'edge_status': edge_2_status},
                edge_3_serial: {'edge_id': edge_3_full_id, 'edge_status': edge_3_status},
            }
        }
        assert result == expected

    @pytest.mark.asyncio
    async def map_bruin_client_ids_to_edges_serials_and_statuses_with_edges_having_null_serials_test(self):
        uuid_1 = uuid()
        uuid_2 = uuid()
        uuid_3 = uuid()
        uuid_4 = uuid()

        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}
        edge_list_response = {
            'request_id': uuid_1,
            'body': [edge_1_full_id, edge_2_full_id, edge_3_full_id],
            'status': 200
        }

        bruin_client_1 = 12345
        bruin_client_2 = 54321
        edge_2_serial = 'VC7654321'

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': None},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_1}|',
        }
        edge_1_status_response = {
            'request_id': uuid_2,
            'body': {
                'edge_id': edge_1_full_id,
                'edge_info': edge_1_status,
            },
            'status': 200,
        }

        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_2}|',
        }
        edge_2_status_response = {
            'request_id': uuid_3,
            'body': {
                'edge_id': edge_2_full_id,
                'edge_info': edge_2_status,
            },
            'status': 200,
        }

        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': None},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client_2}|',
        }
        edge_3_status_response = {
            'request_id': uuid_4,
            'body': {
                'edge_id': edge_3_full_id,
                'edge_info': edge_3_status,
            },
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[
            edge_list_response,
            edge_1_status_response,
            edge_2_status_response,
            edge_3_status_response,
        ])

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', side_effect=[uuid_1, uuid_2, uuid_3, uuid_4]):
            result = await triage._map_bruin_client_ids_to_edges_serials_and_statuses()

        event_bus.rpc_request.assert_has_awaits([
            call(
                "edge.list.request",
                {'request_id': uuid_1, 'body': {'filter': config.TRIAGE_CONFIG['velo_filter']}},
                timeout=600,
            ),
            call(
                "edge.status.request",
                {'request_id': uuid_2, 'body': edge_1_full_id},
                timeout=120,
            ),
            call(
                "edge.status.request",
                {'request_id': uuid_3, 'body': edge_2_full_id},
                timeout=120,
            ),
            call(
                "edge.status.request",
                {'request_id': uuid_4, 'body': edge_3_full_id},
                timeout=120,
            ),
        ])

        expected = {
            bruin_client_2: {
                edge_2_serial: {'edge_id': edge_2_full_id, 'edge_status': edge_2_status},
            }
        }
        assert result == expected

    @pytest.mark.asyncio
    async def map_bruin_client_ids_to_edges_serials_and_statuses_with_edge_list_request_failing_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_edges_for_triage_monitoring = CoroutineMock(side_effect=Exception)
        triage._notify_failing_rpc_request_for_edge_list = CoroutineMock()

        with pytest.raises(Exception):
            await triage._map_bruin_client_ids_to_edges_serials_and_statuses()

        triage._get_edges_for_triage_monitoring.assert_awaited_once()
        triage._notify_failing_rpc_request_for_edge_list.assert_awaited_once()

    @pytest.mark.asyncio
    async def map_bruin_client_ids_to_edges_serials_and_statuses_with_edge_list_request_not_having_2XX_status_test(
            self):
        edge_list_response = {
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=edge_list_response)

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_edges_for_triage_monitoring = CoroutineMock(return_value=edge_list_response)
        triage._notify_http_error_when_requesting_edge_list_from_velocloud = CoroutineMock()

        with pytest.raises(Exception):
            await triage._map_bruin_client_ids_to_edges_serials_and_statuses()

        triage._get_edges_for_triage_monitoring.assert_awaited_once()
        triage._notify_http_error_when_requesting_edge_list_from_velocloud.assert_awaited_once_with(edge_list_response)

    @pytest.mark.asyncio
    async def map_bruin_client_ids_to_edges_serials_and_statuses_with_edge_status_request_failing_test(self):
        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}
        edge_list_response = {
            'body': [edge_1_full_id, edge_2_full_id, edge_3_full_id],
            'status': 200
        }

        bruin_client = 54321
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client}|',
        }
        edge_2_status_response = {
            'body': {
                'edge_id': edge_2_full_id,
                'edge_info': edge_2_status,
            },
            'status': 200,
        }

        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client}|',
        }
        edge_3_status_response = {
            'body': {
                'edge_id': edge_3_full_id,
                'edge_info': edge_3_status,
            },
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_edges_for_triage_monitoring = CoroutineMock(return_value=edge_list_response)
        triage._get_edge_status_by_id = CoroutineMock(side_effect=[
            Exception,
            edge_2_status_response,
            edge_3_status_response,
        ])
        triage._notify_failing_rpc_request_for_edge_status = CoroutineMock()

        result = await triage._map_bruin_client_ids_to_edges_serials_and_statuses()

        triage._get_edges_for_triage_monitoring.assert_awaited_once()
        triage._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id),
            call(edge_2_full_id),
            call(edge_3_full_id),
        ])
        triage._notify_failing_rpc_request_for_edge_status.assert_awaited_once_with(edge_1_full_id)

        expected = {
            bruin_client: {
                edge_2_serial: {'edge_id': edge_2_full_id, 'edge_status': edge_2_status},
                edge_3_serial: {'edge_id': edge_3_full_id, 'edge_status': edge_3_status},
            }
        }
        assert result == expected

    @pytest.mark.asyncio
    async def map_bruin_client_ids_to_edges_serials_and_statuses_with_edge_status_request_not_having_2XX_status_test(
            self):
        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_2_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2}
        edge_3_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 3}
        edge_list_response = {
            'body': [edge_1_full_id, edge_2_full_id, edge_3_full_id],
            'status': 200
        }

        bruin_client = 54321
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_1_status_response = {
            'body': {
                'edge_id': edge_1_full_id,
                'edge_info': 'Got internal error from Velocloud',
            },
            'status': 500,
        }

        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client}|',
        }
        edge_2_status_response = {
            'body': {
                'edge_id': edge_2_full_id,
                'edge_info': edge_2_status,
            },
            'status': 200,
        }

        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|{bruin_client}|',
        }
        edge_3_status_response = {
            'body': {
                'edge_id': edge_3_full_id,
                'edge_info': edge_3_status,
            },
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_edges_for_triage_monitoring = CoroutineMock(return_value=edge_list_response)
        triage._get_edge_status_by_id = CoroutineMock(side_effect=[
            edge_1_status_response,
            edge_2_status_response,
            edge_3_status_response,
        ])
        triage._notify_http_error_when_requesting_edge_status_from_velocloud = CoroutineMock()

        result = await triage._map_bruin_client_ids_to_edges_serials_and_statuses()

        triage._get_edges_for_triage_monitoring.assert_awaited_once()
        triage._get_edge_status_by_id.assert_has_awaits([
            call(edge_1_full_id),
            call(edge_2_full_id),
            call(edge_3_full_id),
        ])
        triage._notify_http_error_when_requesting_edge_status_from_velocloud.assert_awaited_once_with(
            edge_1_full_id, edge_1_status_response
        )

        expected = {
            bruin_client: {
                edge_2_serial: {'edge_id': edge_2_full_id, 'edge_status': edge_2_status},
                edge_3_serial: {'edge_id': edge_3_full_id, 'edge_status': edge_3_status},
            }
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_edges_for_triage_monitoring_test(self):
        uuid_ = uuid()

        edge_list_response = {
            'request_id': uuid_,
            'body': [
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1},
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2},
            ],
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=edge_list_response)

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            result = await triage._get_edges_for_triage_monitoring()

        event_bus.rpc_request.assert_awaited_once_with(
            'edge.list.request',
            {'request_id': uuid_, 'body': {'filter': config.TRIAGE_CONFIG['velo_filter']}},
            timeout=600,
        )
        assert result == edge_list_response

    @pytest.mark.asyncio
    async def notify_failing_rpc_request_for_edge_list_test(self):
        uuid_ = uuid()

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            await triage._notify_failing_rpc_request_for_edge_list()

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'An error occurred when requesting edge list from Velocloud'
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def notify_http_error_when_requesting_edge_list_from_velocloud_test(self):
        uuid_ = uuid()

        edge_list_response_body = 'Got internal error from Velocloud'
        edge_list_response_status = 500
        edge_list_response = {
            'request_id': uuid(),
            'body': edge_list_response_body,
            'status': edge_list_response_status,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            await triage._notify_http_error_when_requesting_edge_list_from_velocloud(edge_list_response)

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'Error while retrieving edge list in {config.TRIAGE_CONFIG["environment"].upper()} '
                           f'environment: Error {edge_list_response_status} - {edge_list_response_body}'
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def get_edge_status_by_id_test(self):
        uuid_ = uuid()

        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_status_response = {
            'request_id': uuid_,
            'body': {
                'edge_id': edge_full_id,
                'edge_info': {
                    'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
                    'links': [
                        {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                        {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
                    ],
                    'enterprise_name': 'EVIL-CORP|12345|',
                }
            },
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=edge_status_response)

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            result = await triage._get_edge_status_by_id(edge_full_id)

        event_bus.rpc_request.assert_awaited_once_with(
            'edge.status.request',
            {'request_id': uuid_, 'body': edge_full_id},
            timeout=120,
        )
        assert result == edge_status_response

    @pytest.mark.asyncio
    async def notify_failing_rpc_request_for_edge_status_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_identifier = EdgeIdentifier(**edge_full_id)

        uuid_ = uuid()

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            await triage._notify_failing_rpc_request_for_edge_status(edge_full_id)

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'An error occurred when requesting edge status from Velocloud for edge {edge_identifier}'
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def notify_http_error_when_requesting_edge_status_from_velocloud_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_identifier = EdgeIdentifier(**edge_full_id)

        uuid_ = uuid()

        edge_status_response_body = 'Got internal error from Velocloud'
        edge_status_response_status = 500
        edge_status_response = {
            'request_id': uuid(),
            'body': edge_status_response_body,
            'status': edge_status_response_status,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            await triage._notify_http_error_when_requesting_edge_status_from_velocloud(
                edge_full_id, edge_status_response
            )

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'Error while retrieving edge status for edge {edge_identifier} in '
                           f'{config.TRIAGE_CONFIG["environment"].upper()} environment: '
                           f'Error {edge_status_response_status} - {edge_status_response_body}'
            },
            timeout=10,
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
        tickets_with_details = tickets_with_details_for_bruin_client_1 + tickets_with_details_for_bruin_client_2

        bruin_client_1_id = 12345
        bruin_client_2_id = 67890
        bruin_client_ids = [bruin_client_1_id, bruin_client_2_id]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_open_tickets_with_details_by_client_id = CoroutineMock(side_effect=[
            tickets_with_details_for_bruin_client_1, tickets_with_details_for_bruin_client_2
        ])

        result = await triage._get_all_open_tickets_with_details_for_monitored_companies(bruin_client_ids)

        triage._get_open_tickets_with_details_by_client_id.assert_has_awaits([
            call(bruin_client_1_id), call(bruin_client_2_id)
        ])
        assert result == tickets_with_details

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
        tickets_with_details = tickets_with_details_for_bruin_client_1 + tickets_with_details_for_bruin_client_3

        bruin_client_1_id = 12345
        bruin_client_2_id = 67890
        bruin_client_3_id = 11223
        bruin_client_ids = [bruin_client_1_id, bruin_client_2_id, bruin_client_3_id]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_open_tickets_with_details_by_client_id = CoroutineMock(side_effect=[
            tickets_with_details_for_bruin_client_1,
            Exception,
            tickets_with_details_for_bruin_client_3,
        ])

        result = await triage._get_all_open_tickets_with_details_for_monitored_companies(bruin_client_ids)

        triage._get_open_tickets_with_details_by_client_id.assert_has_awaits([
            call(bruin_client_1_id), call(bruin_client_2_id), call(bruin_client_3_id)
        ])
        assert result == tickets_with_details

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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_open_tickets_by_client_id = CoroutineMock(return_value=get_open_tickets_response)
        triage._get_ticket_details_by_ticket_id = CoroutineMock(side_effect=[
            get_ticket_1_details_response, get_ticket_2_details_response
        ])

        with patch.object(triage_module, 'uuid', side_effect=[uuid_1, uuid_2, uuid_3]):
            result = await triage._get_open_tickets_with_details_by_client_id(bruin_client_id)

        triage._get_open_tickets_by_client_id.assert_awaited_once_with(bruin_client_id)
        triage._get_ticket_details_by_ticket_id.assert_has_awaits([
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
    async def get_open_tickets_with_details_by_client_id_with_request_for_open_tickets_failing_test(self):
        bruin_client_id = 12345

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_open_tickets_by_client_id = CoroutineMock(side_effect=Exception)
        triage._get_ticket_details_by_ticket_id = CoroutineMock()
        triage._notify_failing_rpc_request_for_open_tickets = CoroutineMock()

        with pytest.raises(Exception):
            await triage._get_open_tickets_with_details_by_client_id(bruin_client_id)

        triage._get_open_tickets_by_client_id.assert_awaited_once_with(bruin_client_id)
        triage._notify_failing_rpc_request_for_open_tickets.assert_awaited_once_with(bruin_client_id)
        triage._get_ticket_details_by_ticket_id.assert_not_awaited()

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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_open_tickets_by_client_id = CoroutineMock(return_value=get_open_tickets_response)
        triage._get_ticket_details_by_ticket_id = CoroutineMock()
        triage._notify_http_error_when_requesting_open_tickets_from_bruin_api = CoroutineMock()

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            with pytest.raises(Exception):
                await triage._get_open_tickets_with_details_by_client_id(bruin_client_id)

        triage._get_open_tickets_by_client_id.assert_awaited_once_with(bruin_client_id)
        triage._notify_http_error_when_requesting_open_tickets_from_bruin_api.assert_awaited_once_with(
            bruin_client_id, get_open_tickets_response
        )
        triage._get_ticket_details_by_ticket_id.assert_not_awaited()

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_with_request_for_ticket_details_failing_test(self):
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
        get_ticket_2_details_response = {
            'request_id': uuid_2,
            'body': ticket_2_details,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_open_tickets_by_client_id = CoroutineMock(return_value=get_open_tickets_response)
        triage._get_ticket_details_by_ticket_id = CoroutineMock(side_effect=[
            Exception,
            get_ticket_2_details_response,
        ])
        triage._notify_failing_rpc_request_for_ticket_details = CoroutineMock()

        with patch.object(triage_module, 'uuid', side_effect=[uuid_1, uuid_2]):
            result = await triage._get_open_tickets_with_details_by_client_id(bruin_client_id)

        triage._get_open_tickets_by_client_id.assert_awaited_once_with(bruin_client_id)
        triage._get_ticket_details_by_ticket_id.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id)
        ])
        triage._notify_failing_rpc_request_for_ticket_details.assert_awaited_once_with(ticket_1_id)

        expected = [
            {
                'ticket_id': ticket_2_id,
                'ticket_detail': ticket_2_details_item_1,
                'ticket_notes': ticket_2_notes,
            }
        ]
        assert result == expected

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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_open_tickets_by_client_id = CoroutineMock(return_value=get_open_tickets_response)
        triage._get_ticket_details_by_ticket_id = CoroutineMock(side_effect=[
            get_ticket_1_details_response, get_ticket_2_details_response
        ])
        triage._notify_http_error_when_requesting_ticket_details_from_bruin_api = CoroutineMock()

        with patch.object(triage_module, 'uuid', side_effect=[uuid_1, uuid_2, uuid_3]):
            result = await triage._get_open_tickets_with_details_by_client_id(bruin_client_id)

        triage._get_open_tickets_by_client_id.assert_awaited_once_with(bruin_client_id)
        triage._get_ticket_details_by_ticket_id.assert_has_awaits([
            call(ticket_1_id), call(ticket_2_id)
        ])
        triage._notify_http_error_when_requesting_ticket_details_from_bruin_api.assert_awaited_once_with(
            bruin_client_id, ticket_1_id, get_ticket_1_details_response
        )

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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_open_tickets_by_client_id = CoroutineMock(return_value=get_open_tickets_response)
        triage._get_ticket_details_by_ticket_id = CoroutineMock(side_effect=[
            get_ticket_1_details_response, get_ticket_2_details_response
        ])
        triage._notify_http_error_when_requesting_ticket_details_from_bruin_api = CoroutineMock()

        with patch.object(triage_module, 'uuid', side_effect=[uuid_1, uuid_2, uuid_3]):
            result = await triage._get_open_tickets_with_details_by_client_id(bruin_client_id)

        triage._get_open_tickets_by_client_id.assert_awaited_once_with(bruin_client_id)
        triage._get_ticket_details_by_ticket_id.assert_has_awaits([
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

    @pytest.mark.asyncio
    async def get_open_tickets_by_client_id_test(self):
        bruin_client_id = 12345

        ticket_1_id = 11111
        ticket_2_id = 22222
        ticket_ids = [{'ticketID': ticket_1_id}, {'ticketID': ticket_2_id}]

        uuid_ = uuid()
        get_open_tickets_request = {
            'request_id': uuid_,
            'body': {
                'client_id': bruin_client_id,
                'ticket_status': ['New', 'InProgress', 'Draft'],
                'category': 'SD-WAN',
                'ticket_topic': 'VOO',
            },
        }
        get_open_tickets_response = {
            'request_id': uuid_,
            'body': ticket_ids,
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=get_open_tickets_response)

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            result = await triage._get_open_tickets_by_client_id(bruin_client_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.request", get_open_tickets_request, timeout=90)
        assert result == get_open_tickets_response

    @pytest.mark.asyncio
    async def get_ticket_details_by_ticket_id_test(self):
        ticket_id = 11111

        uuid_ = uuid()
        get_ticket_details_request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
            },
        }
        get_ticket_details_response = {
            'request_id': uuid_,
            'body': {
                'ticketDetails': [
                    {
                        "detailID": 2746938,
                        "detailValue": 'VC1234567890',
                    },
                ],
                'ticketNotes': [
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
            },
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=get_ticket_details_response)

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            result = await triage._get_ticket_details_by_ticket_id(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.details.request", get_ticket_details_request, timeout=15
        )
        assert result == get_ticket_details_response

    @pytest.mark.asyncio
    async def notify_failing_rpc_request_for_open_tickets_test(self):
        bruin_client_id = 12345

        uuid_ = uuid()

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            await triage._notify_failing_rpc_request_for_open_tickets(bruin_client_id)

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'An error occurred when requesting open tickets from Bruin API for client {bruin_client_id}'
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def notify_http_error_when_requesting_open_tickets_from_bruin_api_test(self):
        bruin_client_id = 12345

        uuid_ = uuid()

        open_tickets_response_body = 'Got internal error from Bruin'
        open_tickets_response_status = 500
        open_tickets_response = {
            'request_id': uuid(),
            'body': open_tickets_response_body,
            'status': open_tickets_response_status,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            await triage._notify_http_error_when_requesting_open_tickets_from_bruin_api(
                bruin_client_id, open_tickets_response
            )

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'Error while retrieving open tickets for Bruin client {bruin_client_id} in '
                           f'{config.TRIAGE_CONFIG["environment"].upper()} environment: '
                           f'Error {open_tickets_response_status} - {open_tickets_response_body}'
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def notify_failing_rpc_request_for_ticket_details_test(self):
        ticket_id = 12345

        uuid_ = uuid()

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            await triage._notify_failing_rpc_request_for_ticket_details(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'An error occurred when requesting ticket details from Bruin API for ticket {ticket_id}'
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def notify_http_error_when_requesting_ticket_details_from_bruin_api_test(self):
        bruin_client_id = 12345
        ticket_id = 67890

        uuid_ = uuid()

        ticket_details_response_body = 'Got internal error from Bruin'
        ticket_details_response_status = 500
        ticket_details_response = {
            'request_id': uuid(),
            'body': ticket_details_response_body,
            'status': ticket_details_response_status,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            await triage._notify_http_error_when_requesting_ticket_details_from_bruin_api(
                bruin_client_id, ticket_id, ticket_details_response
            )

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'Error while retrieving ticket details for Bruin client {bruin_client_id} and ticket '
                           f'{ticket_id} in {config.TRIAGE_CONFIG["environment"].upper()} environment: '
                           f'Error {ticket_details_response_status} - {ticket_details_response_body}'
            },
            timeout=10,
        )

    def filter_tickets_related_to_edges_under_monitoring_test(self):
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1112223'
        edge_4_serial = 'VC3344455'
        edge_5_serial = 'VC5666777'

        edges_under_monitoring = [
            edge_1_serial,
            edge_2_serial,
            edge_4_serial,
            edge_5_serial
        ]

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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        result = triage._filter_tickets_related_to_edges_under_monitoring(tickets, edges_under_monitoring)

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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

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
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|67890|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|67890|',
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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(return_value=last_events_response)
        triage._get_events_chunked = Mock(return_value=[
            events_chunk_1,
            events_chunk_2,
            events_chunk_3,
            events_chunk_4,
        ])
        triage._compose_triage_note = Mock(side_effect=[
            note_for_events_chunk_1,
            note_for_events_chunk_2,
            note_for_events_chunk_3,
            note_for_events_chunk_4,
        ])
        triage._append_note_to_ticket = CoroutineMock(side_effect=[
            append_note_1_response,
            append_note_2_response,
            append_note_3_response,
            append_note_4_response,
        ])
        triage._notify_triage_note_was_appended_to_ticket = CoroutineMock()

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

        triage._get_last_events_for_edge.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_called_once_with(events)
        triage._compose_triage_note.assert_has_calls([
            call(events_chunk_1),
            call(events_chunk_2),
            call(events_chunk_3),
            call(events_chunk_4),
        ])
        triage._append_note_to_ticket.assert_has_awaits([
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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(return_value=last_events_response)
        triage._get_events_chunked = Mock(return_value=[
            events_chunk_1,
            events_chunk_2,
            events_chunk_3,
            events_chunk_4,
        ])
        triage._compose_triage_note = Mock(side_effect=[
            note_for_events_chunk_1,
            note_for_events_chunk_2,
            note_for_events_chunk_3,
            note_for_events_chunk_4,
        ])
        triage._append_note_to_ticket = CoroutineMock()
        triage._notify_triage_note_was_appended_to_ticket = CoroutineMock()

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

        triage._get_last_events_for_edge.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_called_once_with(events)
        triage._compose_triage_note.assert_has_calls([
            call(events_chunk_1),
            call(events_chunk_2),
            call(events_chunk_3),
            call(events_chunk_4),
        ])
        triage._append_note_to_ticket.assert_not_awaited()
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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(return_value=last_events_response)
        triage._get_events_chunked = Mock(return_value=[])  # Just tricking this return value to "stop" execution here
        triage._compose_triage_note = Mock()
        triage._append_note_to_ticket = CoroutineMock()
        triage._notify_triage_note_was_appended_to_ticket = CoroutineMock()

        await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

        triage._get_last_events_for_edge.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_called_once_with(events_sorted_by_event_time)

    @pytest.mark.asyncio
    async def append_new_triage_notes_based_on_recent_events_with_rpc_request_for_recent_events_failing_test(self):
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
        }
        edge_data = {
            'edge_id': edge_full_id,
            'edge_status': edge_status
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(side_effect=Exception)
        triage._notify_failing_rpc_request_for_edge_events = CoroutineMock()
        triage._get_events_chunked = Mock()

        await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

        triage._get_last_events_for_edge.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._notify_failing_rpc_request_for_edge_events.assert_awaited_once_with(edge_full_id)
        triage._get_events_chunked.assert_not_called()

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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(return_value=last_events_response)
        triage._notify_http_error_when_requesting_edge_events_from_velocloud = CoroutineMock()
        triage._get_events_chunked = Mock()

        await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

        triage._get_last_events_for_edge.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._notify_http_error_when_requesting_edge_events_from_velocloud.assert_awaited_once_with(
            edge_full_id, last_events_response
        )
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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(return_value=last_events_response)
        triage._get_events_chunked = Mock()

        await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

        triage._get_last_events_for_edge.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_not_called()

    @pytest.mark.asyncio
    async def append_new_triage_notes_based_on_recent_events_with_request_to_append_note_to_tickets_failing_test(self):
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

        append_note_1_response = {
            'body': 'Note appended successfully',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(return_value=last_events_response)
        triage._get_events_chunked = Mock(return_value=[
            events_chunk_1,
            events_chunk_2,
        ])
        triage._compose_triage_note = Mock(side_effect=[
            note_for_events_chunk_1,
            note_for_events_chunk_2,
        ])
        triage._append_note_to_ticket = CoroutineMock(side_effect=[
            append_note_1_response,
            Exception,
        ])
        triage._notify_failing_rpc_request_for_appending_ticket_note = CoroutineMock()
        triage._notify_triage_note_was_appended_to_ticket = CoroutineMock()

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

        triage._get_last_events_for_edge.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_called_once_with(events)
        triage._compose_triage_note.assert_has_calls([
            call(events_chunk_1),
            call(events_chunk_2),
        ])
        triage._append_note_to_ticket.assert_has_awaits([
            call(ticket_id, note_for_events_chunk_1),
            call(ticket_id, note_for_events_chunk_2),
        ])
        triage._notify_failing_rpc_request_for_appending_ticket_note.assert_awaited_once_with(
            ticket_id, note_for_events_chunk_2
        )
        triage._notify_triage_note_was_appended_to_ticket.assert_awaited_once_with(ticket_id, client_id)

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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(return_value=last_events_response)
        triage._get_events_chunked = Mock(return_value=[
            events_chunk_1,
            events_chunk_2,
            events_chunk_3,
            events_chunk_4,
        ])
        triage._compose_triage_note = Mock(side_effect=[
            note_for_events_chunk_1,
            note_for_events_chunk_2,
            note_for_events_chunk_3,
            note_for_events_chunk_4,
        ])
        triage._append_note_to_ticket = CoroutineMock(side_effect=[
            append_note_1_response,
            append_note_2_response,
            append_note_3_response,
            append_note_4_response,
        ])
        triage._notify_http_error_when_appending_note_to_ticket = CoroutineMock()
        triage._notify_triage_note_was_appended_to_ticket = CoroutineMock()

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

        triage._get_last_events_for_edge.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_called_once_with(events)
        triage._compose_triage_note.assert_has_calls([
            call(events_chunk_1),
            call(events_chunk_2),
            call(events_chunk_3),
            call(events_chunk_4),
        ])
        triage._append_note_to_ticket.assert_has_awaits([
            call(ticket_id, note_for_events_chunk_1),
            call(ticket_id, note_for_events_chunk_2),
            call(ticket_id, note_for_events_chunk_3),
            call(ticket_id, note_for_events_chunk_4),
        ])
        triage._notify_http_error_when_appending_note_to_ticket.assert_has_awaits([
            call(ticket_id, append_note_2_response),
            call(ticket_id, append_note_4_response),
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

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(return_value=last_events_response)
        triage._get_events_chunked = Mock(return_value=[
            events_chunk_1,
            events_chunk_2,
        ])
        triage._compose_triage_note = Mock(side_effect=[
            note_for_events_chunk_1,
            note_for_events_chunk_2,
        ])
        triage._append_note_to_ticket = CoroutineMock(side_effect=[
            Exception,
            Exception,
        ])
        triage._notify_failing_rpc_request_for_appending_ticket_note = CoroutineMock()
        triage._notify_triage_note_was_appended_to_ticket = CoroutineMock()

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            await triage._append_new_triage_notes_based_on_recent_events(ticket_id, last_triage_timestamp, edge_data)

        triage._get_last_events_for_edge.assert_awaited_once_with(edge_full_id, since=last_triage_datetime)
        triage._get_events_chunked.assert_called_once_with(events)
        triage._compose_triage_note.assert_has_calls([
            call(events_chunk_1),
            call(events_chunk_2),
        ])
        triage._append_note_to_ticket.assert_has_awaits([
            call(ticket_id, note_for_events_chunk_1),
            call(ticket_id, note_for_events_chunk_2),
        ])
        triage._notify_failing_rpc_request_for_appending_ticket_note.assert_has_awaits([
            call(ticket_id, note_for_events_chunk_1),
            call(ticket_id, note_for_events_chunk_2),
        ])
        triage._notify_triage_note_was_appended_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def notify_http_error_when_appending_note_to_ticket_test(self):
        ticket_id = 12345

        uuid_ = uuid()

        append_ticket_note_response_body = 'Got internal error from Velocloud'
        append_ticket_note_response_status = 500
        append_ticket_note_response = {
            'request_id': uuid(),
            'body': append_ticket_note_response_body,
            'status': append_ticket_note_response_status,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            await triage._notify_http_error_when_appending_note_to_ticket(ticket_id, append_ticket_note_response)

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'Error while appending note to ticket {ticket_id} in '
                           f'{config.TRIAGE_CONFIG["environment"].upper()} environment: Error '
                           f'{append_ticket_note_response_status} - {append_ticket_note_response_body}'
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def get_last_events_for_edge_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_events = [
            {
                'event': 'LINK_ALIVE',
                'category': 'NETWORK',
                'eventTime': '2019-07-30 07:38:00+00:00',
                'message': 'GE2 alive'
            }
        ]
        rpc_response = {'body': edge_events, 'status': 200}

        scheduler = Mock()
        logger = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=rpc_response)

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        uuid_ = uuid()
        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(minutes=15)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(triage_module, 'datetime', new=datetime_mock):
            with patch.object(triage_module, 'uuid', return_value=uuid_):
                result = await triage._get_last_events_for_edge(edge_full_id, since=past_moment_for_events_lookup)

        event_bus.rpc_request.assert_awaited_once_with(
            "alert.request.event.edge",
            {
                'request_id': uuid_,
                'body': {
                    'edge': edge_full_id,
                    'start_date': past_moment_for_events_lookup,
                    'end_date': current_datetime,
                    'filter': ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD'],
                },
            },
            timeout=180,
        )
        assert result == rpc_response

    @pytest.mark.asyncio
    async def notify_failing_rpc_request_for_edge_events_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_identifier = EdgeIdentifier(**edge_full_id)

        uuid_ = uuid()

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            await triage._notify_failing_rpc_request_for_edge_events(edge_full_id)

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'An error occurred when requesting edge events from Velocloud for edge {edge_identifier}'
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def notify_http_error_when_requesting_edge_events_from_velocloud_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_identifier = EdgeIdentifier(**edge_full_id)

        uuid_ = uuid()

        edge_events_response_body = 'Got internal error from Velocloud'
        edge_events_response_status = 500
        edge_events_response = {
            'request_id': uuid(),
            'events': edge_events_response_body,
            'status': edge_events_response_status,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            await triage._notify_http_error_when_requesting_edge_events_from_velocloud(
                edge_full_id, edge_events_response
            )

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'Error while retrieving edge events for edge {edge_identifier} in '
                           f'{config.TRIAGE_CONFIG["environment"].upper()} environment: Error '
                           f'{edge_events_response_status} - {edge_events_response_body}'
            },
            timeout=10,
        )

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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

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

    def compose_triage_note_test(self):
        event_1 = {
            'event': 'EDGE_NEW_DEVICE',
            'category': 'EDGE',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'New or updated client device'
        }
        event_2 = {
            'event': 'EDGE_INTERFACE_UP',
            'category': 'SYSTEM',
            'eventTime': '2019-07-29 07:38:00+00:00',
            'message': 'Interface GE1 is up'
        }
        event_3 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-31 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_4 = {
            'event': 'EDGE_INTERFACE_DOWN',
            'category': 'SYSTEM',
            'eventTime': '2019-07-28 07:38:00+00:00',
            'message': 'Interface GE2 is down'
        }
        event_5 = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-01 07:38:00+00:00',
            'message': 'Link GE2 is no longer DEAD'
        }
        event_6 = {
            'event': 'EDGE_INTERFACE_UP',
            'category': 'NETWORK',
            'eventTime': '2019-08-01 07:38:00+00:00',
            'message': 'Interface INTERNET3 is up'
        }
        event_7 = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-08-01 07:40:00+00:00',
            'message': 'Link INTERNET3 is no longer DEAD'
        }
        events = [event_1, event_2, event_3, event_4, event_5, event_6, event_7]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['timezone'] = 'UTC'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            triage_note = triage._compose_triage_note(events)

        assert triage_note == os.linesep.join([
            '#*Automation Engine*#',
            '',
            'Triage',
            '',
            'New event: EDGE_NEW_DEVICE',
            'Device: Edge',
            'Event time: 2019-07-30 07:38:00+00:00',
            '',
            'New event: EDGE_INTERFACE_UP',
            'Device: Interface GE1',
            'Event time: 2019-07-29 07:38:00+00:00',
            '',
            'New event: LINK_DEAD',
            'Device: Interface GE2',
            'Event time: 2019-07-31 07:38:00+00:00',
            '',
            'New event: EDGE_INTERFACE_DOWN',
            'Device: Interface GE2',
            'Event time: 2019-07-28 07:38:00+00:00',
            '',
            'New event: LINK_ALIVE',
            'Device: Interface GE2',
            'Event time: 2019-07-01 07:38:00+00:00',
            '',
            'New event: EDGE_INTERFACE_UP',
            'Device: Interface INTERNET3',
            'Event time: 2019-08-01 07:38:00+00:00',
            '',
            'New event: LINK_ALIVE',
            'Device: Interface INTERNET3',
            'Event time: 2019-08-01 07:40:00+00:00',
            '',
            'Timestamp: 2019-08-01 07:40:00+00:00',
        ])

    @pytest.mark.asyncio
    async def append_note_to_ticket_test(self):
        ticket_id = 12345
        ticket_note = 'This is a ticket note'

        uuid_ = uuid()
        append_note_to_ticket_request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'note': ticket_note,
            },
        }
        append_note_to_ticket_response = {
            'request_id': uuid_,
            'body': 'Note appended with success',
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=append_note_to_ticket_response)

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            result = await triage._append_note_to_ticket(ticket_id, ticket_note)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.note.append.request", append_note_to_ticket_request, timeout=15
        )
        assert result == append_note_to_ticket_response

    @pytest.mark.asyncio
    async def notify_failing_rpc_request_for_edge_events_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_identifier = EdgeIdentifier(**edge_full_id)

        uuid_ = uuid()

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            await triage._notify_failing_rpc_request_for_edge_events(edge_full_id)

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'An error occurred when requesting edge events from Velocloud for edge {edge_identifier}'
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def notify_http_error_when_requesting_edge_events_from_velocloud_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        edge_identifier = EdgeIdentifier(**edge_full_id)

        uuid_ = uuid()

        edge_events_response_body = 'Got internal error from Velocloud'
        edge_events_response_status = 500
        edge_events_response = {
            'request_id': uuid(),
            'body': edge_events_response_body,
            'status': edge_events_response_status,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            await triage._notify_http_error_when_requesting_edge_events_from_velocloud(
                edge_full_id, edge_events_response
            )

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'Error while retrieving edge events for edge {edge_identifier} in '
                           f'{config.TRIAGE_CONFIG["environment"].upper()} environment: Error '
                           f'{edge_events_response_status} - {edge_events_response_body}'
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def notify_failing_rpc_request_for_appending_ticket_note_test(self):
        ticket_id = 12345
        ticket_note = 'This is a ticket note'

        uuid_ = uuid()

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            await triage._notify_failing_rpc_request_for_appending_ticket_note(ticket_id, ticket_note)

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'An error occurred when appending a ticket note to ticket {ticket_id}. '
                           f'Ticket note: {ticket_note}'
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def notify_triage_note_was_appended_to_ticket_test(self):
        ticket_id = 12345
        bruin_client_id = 12345

        uuid_ = uuid()

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        with patch.object(triage_module, 'uuid', return_value=uuid_):
            await triage._notify_triage_note_was_appended_to_ticket(ticket_id, bruin_client_id)

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'Triage appended to ticket {ticket_id} in '
                           f'{config.TRIAGE_CONFIG["environment"].upper()} environment. Details at '
                           f'https://app.bruin.com/helpdesk?clientId={bruin_client_id}&ticketId={ticket_id}'
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def process_tickets_without_triage_with_events_sorted_before_gathering_relevant_info_test(self):
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
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|67890|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|67890|',
        }

        edge_1_data = {'edge_id': edge_1_full_id, 'edge_status': edge_1_status}
        edge_2_data = {'edge_id': edge_2_full_id, 'edge_status': edge_2_status}
        edge_3_data = {'edge_id': edge_3_full_id, 'edge_status': edge_3_status}
        edges_data_by_serial = {
            edge_1_serial: edge_1_data,
            edge_2_serial: edge_2_data,
            edge_3_serial: edge_3_data,
        }

        ticket_id = 12345
        ticket_detail = {
            "detailID": 2746930,
            "detailValue": edge_1_serial,
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

        tickets = [ticket]

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
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(return_value=last_events_response)
        triage._gather_relevant_data_for_first_triage_note = Mock(return_value=relevant_data_for_triage_note)
        triage._send_email = CoroutineMock()
        triage._append_note_to_ticket = CoroutineMock()

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_tickets_without_triage(tickets, edges_data_by_serial)

        triage._get_last_events_for_edge.assert_awaited_once_with(edge_1_full_id, since=past_moment_for_events_lookup)
        triage._gather_relevant_data_for_first_triage_note.assert_called_once_with(
            edge_1_data, events_sorted_by_event_time
        )

    @pytest.mark.asyncio
    async def process_tickets_without_triage_with_dev_environment_test(self):
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
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|67890|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|67890|',
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
            "detailID": 2746931,
            "detailValue": edge_2_serial,
        }
        ticket_2_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-04-30T06:38:13.503-05:00',
        }
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_detail': ticket_2_detail,
            'ticket_notes': [ticket_2_note]
        }

        tickets = [ticket_1, ticket_2]

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
        events_1 = [event_1]
        events_2 = [event_2]

        last_events_response_1 = {'body': events_1, 'status': 200}
        last_events_response_2 = {'body': events_2, 'status': 200}

        relevant_data_for_triage_note_1 = {
            'data-1': 'some-data-1',
            'data-2': 'some-more-data-1',
            'data-3': 42,
            'data-4': 'Travis Touchdown',
        }
        relevant_data_for_triage_note_2 = {
            'data-1': 'some-data-2',
            'data-2': 'some-more-data-2',
            'data-3': 42,
            'data-4': 'Yagami Light',
        }

        email_body_1 = {'request_id': uuid(), 'email_data': {'subject': 'some-subject', 'html': 'some-html'}}
        email_body_2 = {'request_id': uuid(), 'email_data': {'subject': 'some-subject2', 'html': 'some-html2'}}

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()

        template_renderer = Mock()
        template_renderer.compose_email_object = Mock(side_effect=[email_body_1, email_body_2])

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(side_effect=[last_events_response_1, last_events_response_2])
        triage._gather_relevant_data_for_first_triage_note = Mock(side_effect=[
            relevant_data_for_triage_note_1,
            relevant_data_for_triage_note_2,
        ])
        triage._send_email = CoroutineMock()
        triage._append_note_to_ticket = CoroutineMock()

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_tickets_without_triage(tickets, edges_data_by_serial)

        triage._get_last_events_for_edge.assert_has_awaits([
            call(edge_1_full_id, since=past_moment_for_events_lookup),
            call(edge_2_full_id, since=past_moment_for_events_lookup),
        ])
        triage._gather_relevant_data_for_first_triage_note.assert_has_calls([
            call(edge_1_data, events_1),
            call(edge_2_data, events_2),
        ])
        template_renderer.compose_email_object.assert_has_calls([
            call(relevant_data_for_triage_note_1),
            call(relevant_data_for_triage_note_2),
        ])
        triage._send_email.assert_has_awaits([
            call(email_body_1), call(email_body_2),
        ])
        triage._append_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_without_triage_with_production_environment_test(self):
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
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|67890|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|67890|',
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
            "detailID": 2746931,
            "detailValue": edge_2_serial,
        }
        ticket_2_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-04-30T06:38:13.503-05:00',
        }
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_detail': ticket_2_detail,
            'ticket_notes': [ticket_2_note]
        }

        tickets = [ticket_1, ticket_2]

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
        events_1 = [event_1]
        events_2 = [event_2]

        last_events_response_1 = {'body': events_1, 'status': 200}
        last_events_response_2 = {'body': events_2, 'status': 200}

        relevant_data_for_triage_note_1 = {
            'data-1': 'some-data-1',
            'data-2': 'some-more-data-1',
            'data-3': 42,
            'data-4': 'Travis Touchdown',
        }
        relevant_data_for_triage_note_2 = {
            'data-1': 'some-data-2',
            'data-2': 'some-more-data-2',
            'data-3': 42,
            'data-4': 'Yagami Light',
        }

        ticket_note_1 = 'This is the first ticket note'
        ticket_note_2 = 'This is the second ticket note'

        append_note_1_to_ticket_response = {
            'body': 'Note appended with success',
            'status': 200,
        }
        append_note_2_to_ticket_response = {
            'body': 'Note appended with success',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(side_effect=[last_events_response_1, last_events_response_2])
        triage._gather_relevant_data_for_first_triage_note = Mock(side_effect=[
            relevant_data_for_triage_note_1,
            relevant_data_for_triage_note_2,
        ])
        triage._transform_relevant_data_into_ticket_note = Mock(side_effect=[ticket_note_1, ticket_note_2])
        triage._send_triage_info_via_email = CoroutineMock()
        triage._append_note_to_ticket = CoroutineMock(side_effect=[
            append_note_1_to_ticket_response,
            append_note_2_to_ticket_response,
        ])

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_tickets_without_triage(tickets, edges_data_by_serial)

        triage._get_last_events_for_edge.assert_has_awaits([
            call(edge_1_full_id, since=past_moment_for_events_lookup),
            call(edge_2_full_id, since=past_moment_for_events_lookup),
        ])
        triage._gather_relevant_data_for_first_triage_note.assert_has_calls([
            call(edge_1_data, events_1),
            call(edge_2_data, events_2),
        ])
        triage._transform_relevant_data_into_ticket_note.assert_has_calls([
            call(relevant_data_for_triage_note_1),
            call(relevant_data_for_triage_note_2),
        ])
        triage._append_note_to_ticket.assert_has_awaits([
            call(ticket_1_id, ticket_note_1),
            call(ticket_2_id, ticket_note_2),
        ])
        triage._send_triage_info_via_email.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_without_triage_with_unknown_environment_test(self):
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
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|67890|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|67890|',
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
            "detailID": 2746931,
            "detailValue": edge_2_serial,
        }
        ticket_2_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-04-30T06:38:13.503-05:00',
        }
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_detail': ticket_2_detail,
            'ticket_notes': [ticket_2_note]
        }

        tickets = [ticket_1, ticket_2]

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
        events_1 = [event_1]
        events_2 = [event_2]

        last_events_response_1 = {'body': events_1, 'status': 200}
        last_events_response_2 = {'body': events_2, 'status': 200}

        relevant_data_for_triage_note_1 = {
            'data-1': 'some-data-1',
            'data-2': 'some-more-data-1',
            'data-3': 42,
            'data-4': 'Travis Touchdown',
        }
        relevant_data_for_triage_note_2 = {
            'data-1': 'some-data-2',
            'data-2': 'some-more-data-2',
            'data-3': 42,
            'data-4': 'Yagami Light',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(side_effect=[last_events_response_1, last_events_response_2])
        triage._gather_relevant_data_for_first_triage_note = Mock(side_effect=[
            relevant_data_for_triage_note_1,
            relevant_data_for_triage_note_2,
        ])
        triage._send_triage_info_via_email = CoroutineMock()
        triage._append_note_to_ticket = CoroutineMock()

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'unknown'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_tickets_without_triage(tickets, edges_data_by_serial)

        triage._get_last_events_for_edge.assert_has_awaits([
            call(edge_1_full_id, since=past_moment_for_events_lookup),
            call(edge_2_full_id, since=past_moment_for_events_lookup),
        ])
        triage._gather_relevant_data_for_first_triage_note.assert_has_calls([
            call(edge_1_data, events_1),
            call(edge_2_data, events_2),
        ])
        triage._append_note_to_ticket.assert_not_awaited()
        triage._send_triage_info_via_email.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_tickets_without_triage_with_edge_events_request_failing_test(self):
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
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|67890|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|67890|',
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
            "detailID": 2746931,
            "detailValue": edge_2_serial,
        }
        ticket_2_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-04-30T06:38:13.503-05:00',
        }
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_detail': ticket_2_detail,
            'ticket_notes': [ticket_2_note]
        }

        tickets = [ticket_1, ticket_2]

        event_1 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        events_1 = [event_1]

        last_events_response_1 = {'body': events_1, 'status': 200}

        relevant_data_for_triage_note_1 = {
            'data-1': 'some-data-1',
            'data-2': 'some-more-data-1',
            'data-3': 42,
            'data-4': 'Travis Touchdown',
        }

        ticket_note_1 = 'This is the first ticket note'

        append_note_1_to_ticket_response = {
            'body': 'Note appended with success',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(side_effect=[last_events_response_1, Exception])
        triage._gather_relevant_data_for_first_triage_note = Mock(return_value=relevant_data_for_triage_note_1)
        triage._transform_relevant_data_into_ticket_note = Mock(return_value=ticket_note_1)
        triage._send_triage_info_via_email = CoroutineMock()
        triage._append_note_to_ticket = CoroutineMock(return_value=append_note_1_to_ticket_response)
        triage._notify_failing_rpc_request_for_edge_events = CoroutineMock()

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_tickets_without_triage(tickets, edges_data_by_serial)

        triage._get_last_events_for_edge.assert_has_awaits([
            call(edge_1_full_id, since=past_moment_for_events_lookup),
            call(edge_2_full_id, since=past_moment_for_events_lookup),
        ])
        triage._gather_relevant_data_for_first_triage_note.assert_called_once_with(edge_1_data, events_1)
        triage._transform_relevant_data_into_ticket_note.assert_called_once_with(relevant_data_for_triage_note_1)
        triage._append_note_to_ticket.assert_awaited_once_with(ticket_1_id, ticket_note_1)
        triage._notify_failing_rpc_request_for_edge_events.assert_awaited_once_with(edge_2_full_id)

    @pytest.mark.asyncio
    async def process_tickets_without_triage_with_edge_events_request_not_having_2XX_status_test(self):
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
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|67890|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|67890|',
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
            "detailID": 2746931,
            "detailValue": edge_2_serial,
        }
        ticket_2_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-04-30T06:38:13.503-05:00',
        }
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_detail': ticket_2_detail,
            'ticket_notes': [ticket_2_note]
        }

        tickets = [ticket_1, ticket_2]

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
        events_1 = [event_1]
        events_2 = [event_2]

        last_events_response_1 = {'body': events_1, 'status': 200}
        last_events_response_2 = {'body': events_2, 'status': 500}

        relevant_data_for_triage_note_1 = {
            'data-1': 'some-data-1',
            'data-2': 'some-more-data-1',
            'data-3': 42,
            'data-4': 'Travis Touchdown',
        }

        ticket_note_1 = 'This is the first ticket note'

        append_note_1_to_ticket_response = {
            'body': 'Note appended with success',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(side_effect=[last_events_response_1, last_events_response_2])
        triage._gather_relevant_data_for_first_triage_note = Mock(return_value=relevant_data_for_triage_note_1)
        triage._transform_relevant_data_into_ticket_note = Mock(return_value=ticket_note_1)
        triage._send_triage_info_via_email = CoroutineMock()
        triage._append_note_to_ticket = CoroutineMock(return_value=append_note_1_to_ticket_response)
        triage._notify_http_error_when_requesting_edge_events_from_velocloud = CoroutineMock()

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_tickets_without_triage(tickets, edges_data_by_serial)

        triage._get_last_events_for_edge.assert_has_awaits([
            call(edge_1_full_id, since=past_moment_for_events_lookup),
            call(edge_2_full_id, since=past_moment_for_events_lookup),
        ])
        triage._gather_relevant_data_for_first_triage_note.assert_called_once_with(edge_1_data, events_1)
        triage._transform_relevant_data_into_ticket_note.assert_called_once_with(relevant_data_for_triage_note_1)
        triage._append_note_to_ticket.assert_awaited_once_with(ticket_1_id, ticket_note_1)
        triage._notify_http_error_when_requesting_edge_events_from_velocloud.assert_awaited_once_with(
            edge_2_full_id, last_events_response_2
        )

    @pytest.mark.asyncio
    async def process_tickets_without_triage_with_edge_events_request_returning_no_events_test(self):
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
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|67890|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|67890|',
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
            "detailID": 2746931,
            "detailValue": edge_2_serial,
        }
        ticket_2_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-04-30T06:38:13.503-05:00',
        }
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_detail': ticket_2_detail,
            'ticket_notes': [ticket_2_note]
        }

        tickets = [ticket_1, ticket_2]

        event_1 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        events_1 = [event_1]
        events_2 = []

        last_events_response_1 = {'body': events_1, 'status': 200}
        last_events_response_2 = {'body': events_2, 'status': 200}

        relevant_data_for_triage_note_1 = {
            'data-1': 'some-data-1',
            'data-2': 'some-more-data-1',
            'data-3': 42,
            'data-4': 'Travis Touchdown',
        }

        ticket_note_1 = 'This is the first ticket note'

        append_note_1_to_ticket_response = {
            'body': 'Note appended with success',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(side_effect=[last_events_response_1, last_events_response_2])
        triage._gather_relevant_data_for_first_triage_note = Mock(return_value=relevant_data_for_triage_note_1)
        triage._transform_relevant_data_into_ticket_note = Mock(return_value=ticket_note_1)
        triage._send_triage_info_via_email = CoroutineMock()
        triage._append_note_to_ticket = CoroutineMock(return_value=append_note_1_to_ticket_response)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_tickets_without_triage(tickets, edges_data_by_serial)

        triage._get_last_events_for_edge.assert_has_awaits([
            call(edge_1_full_id, since=past_moment_for_events_lookup),
            call(edge_2_full_id, since=past_moment_for_events_lookup),
        ])
        triage._gather_relevant_data_for_first_triage_note.assert_called_once_with(edge_1_data, events_1)
        triage._transform_relevant_data_into_ticket_note.assert_called_once_with(relevant_data_for_triage_note_1)
        triage._append_note_to_ticket.assert_awaited_once_with(ticket_1_id, ticket_note_1)

    @pytest.mark.asyncio
    async def process_tickets_without_triage_with_request_to_append_note_to_tickets_failing_test(self):
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
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|67890|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|67890|',
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
            "detailID": 2746931,
            "detailValue": edge_2_serial,
        }
        ticket_2_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-04-30T06:38:13.503-05:00',
        }
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_detail': ticket_2_detail,
            'ticket_notes': [ticket_2_note]
        }

        tickets = [ticket_1, ticket_2]

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
        events_1 = [event_1]
        events_2 = [event_2]

        last_events_response_1 = {'body': events_1, 'status': 200}
        last_events_response_2 = {'body': events_2, 'status': 200}

        relevant_data_for_triage_note_1 = {
            'data-1': 'some-data-1',
            'data-2': 'some-more-data-1',
            'data-3': 42,
            'data-4': 'Travis Touchdown',
        }
        relevant_data_for_triage_note_2 = {
            'data-1': 'some-data-2',
            'data-2': 'some-more-data-2',
            'data-3': 42,
            'data-4': 'Travis Touchdown',
        }

        ticket_note_1 = 'This is the first ticket note'
        ticket_note_2 = 'This is the second ticket note'

        append_note_2_to_ticket_response = {
            'body': 'Note appended with success',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(side_effect=[last_events_response_1, last_events_response_2])
        triage._gather_relevant_data_for_first_triage_note = Mock(side_effect=[
            relevant_data_for_triage_note_1, relevant_data_for_triage_note_2
        ])
        triage._transform_relevant_data_into_ticket_note = Mock(side_effect=[
            ticket_note_1, ticket_note_2
        ])
        triage._send_triage_info_via_email = CoroutineMock()
        triage._append_note_to_ticket = CoroutineMock(side_effect=[Exception, append_note_2_to_ticket_response])
        triage._notify_failing_rpc_request_for_appending_ticket_note = CoroutineMock()

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_tickets_without_triage(tickets, edges_data_by_serial)

        triage._get_last_events_for_edge.assert_has_awaits([
            call(edge_1_full_id, since=past_moment_for_events_lookup),
            call(edge_2_full_id, since=past_moment_for_events_lookup),
        ])
        triage._gather_relevant_data_for_first_triage_note.assert_has_calls([
            call(edge_1_data, events_1),
            call(edge_2_data, events_2),
        ])
        triage._transform_relevant_data_into_ticket_note.assert_has_calls([
            call(relevant_data_for_triage_note_1),
            call(relevant_data_for_triage_note_2),
        ])
        triage._append_note_to_ticket.assert_has_awaits([
            call(ticket_1_id, ticket_note_1),
            call(ticket_2_id, ticket_note_2),
        ])
        triage._notify_failing_rpc_request_for_appending_ticket_note.assert_awaited_once_with(
            ticket_1_id, ticket_note_1
        )

    @pytest.mark.asyncio
    async def process_tickets_without_triage_with_append_note_request_not_having_2XX_status_test(self):
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
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|67890|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|67890|',
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
            "detailID": 2746931,
            "detailValue": edge_2_serial,
        }
        ticket_2_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-04-30T06:38:13.503-05:00',
        }
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_detail': ticket_2_detail,
            'ticket_notes': [ticket_2_note]
        }

        tickets = [ticket_1, ticket_2]

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
        events_1 = [event_1]
        events_2 = [event_2]

        last_events_response_1 = {'body': events_1, 'status': 200}
        last_events_response_2 = {'body': events_2, 'status': 200}

        relevant_data_for_triage_note_1 = {
            'data-1': 'some-data-1',
            'data-2': 'some-more-data-1',
            'data-3': 42,
            'data-4': 'Travis Touchdown',
        }
        relevant_data_for_triage_note_2 = {
            'data-1': 'some-data-2',
            'data-2': 'some-more-data-2',
            'data-3': 42,
            'data-4': 'Travis Touchdown',
        }

        ticket_note_1 = 'This is the first ticket note'
        ticket_note_2 = 'This is the second ticket note'

        append_note_1_to_ticket_response = {
            'body': 'Note appended with success',
            'status': 200,
        }
        append_note_2_to_ticket_response = {
            'body': 'Error appending note to ticket',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(side_effect=[last_events_response_1, last_events_response_2])
        triage._gather_relevant_data_for_first_triage_note = Mock(side_effect=[
            relevant_data_for_triage_note_1, relevant_data_for_triage_note_2
        ])
        triage._transform_relevant_data_into_ticket_note = Mock(side_effect=[
            ticket_note_1, ticket_note_2
        ])
        triage._send_triage_info_via_email = CoroutineMock()
        triage._append_note_to_ticket = CoroutineMock(side_effect=[
            append_note_1_to_ticket_response,
            append_note_2_to_ticket_response,
        ])
        triage._notify_http_error_when_appending_note_to_ticket = CoroutineMock()
        triage._notify_failing_rpc_request_for_appending_ticket_note = CoroutineMock()

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_tickets_without_triage(tickets, edges_data_by_serial)

        triage._get_last_events_for_edge.assert_has_awaits([
            call(edge_1_full_id, since=past_moment_for_events_lookup),
            call(edge_2_full_id, since=past_moment_for_events_lookup),
        ])
        triage._gather_relevant_data_for_first_triage_note.assert_has_calls([
            call(edge_1_data, events_1),
            call(edge_2_data, events_2),
        ])
        triage._transform_relevant_data_into_ticket_note.assert_has_calls([
            call(relevant_data_for_triage_note_1),
            call(relevant_data_for_triage_note_2),
        ])
        triage._append_note_to_ticket.assert_has_awaits([
            call(ticket_1_id, ticket_note_1),
            call(ticket_2_id, ticket_note_2),
        ])
        triage._notify_http_error_when_appending_note_to_ticket.assert_awaited_once_with(
            ticket_2_id, append_note_2_to_ticket_response
        )

    @pytest.mark.asyncio
    async def process_tickets_without_triage_with_rpc_request_for_sending_email_failing_test(self):
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
        }
        edge_2_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_2_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|67890|',
        }
        edge_3_status = {
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
            'links': [
                {'linkId': 1234, 'link': {'state': 'STABLE', 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
            ],
            'enterprise_name': f'EVIL-CORP|67890|',
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
            "detailID": 2746931,
            "detailValue": edge_2_serial,
        }
        ticket_2_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket\nTimeStamp: 2019-04-30T06:38:13.503-05:00',
            "createdDate": '2019-04-30T06:38:13.503-05:00',
        }
        ticket_2 = {
            'ticket_id': ticket_2_id,
            'ticket_detail': ticket_2_detail,
            'ticket_notes': [ticket_2_note]
        }

        tickets = [ticket_1, ticket_2]

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
        events_1 = [event_1]
        events_2 = [event_2]

        last_events_response_1 = {'body': events_1, 'status': 200}
        last_events_response_2 = {'body': events_2, 'status': 200}

        relevant_data_for_triage_note_1 = {
            'data-1': 'some-data-1',
            'data-2': 'some-more-data-1',
            'data-3': 42,
            'data-4': 'Travis Touchdown',
        }
        relevant_data_for_triage_note_2 = {
            'data-1': 'some-data-2',
            'data-2': 'some-more-data-2',
            'data-3': 42,
            'data-4': 'Yagami Light',
        }

        email_body_1 = {'request_id': uuid(), 'email_data': {'subject': 'some-subject', 'html': 'some-html'}}
        email_body_2 = {'request_id': uuid(), 'email_data': {'subject': 'some-subject2', 'html': 'some-html2'}}

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()

        template_renderer = Mock()
        template_renderer.compose_email_object = Mock(side_effect=[email_body_1, email_body_2])

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)
        triage._get_last_events_for_edge = CoroutineMock(side_effect=[last_events_response_1, last_events_response_2])
        triage._gather_relevant_data_for_first_triage_note = Mock(side_effect=[
            relevant_data_for_triage_note_1,
            relevant_data_for_triage_note_2,
        ])
        triage._send_email = CoroutineMock(side_effect=[Exception, None])
        triage._append_note_to_ticket = CoroutineMock()

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                with patch.object(triage_module, 'utc', new=Mock()):
                    await triage._process_tickets_without_triage(tickets, edges_data_by_serial)

        triage._get_last_events_for_edge.assert_has_awaits([
            call(edge_1_full_id, since=past_moment_for_events_lookup),
            call(edge_2_full_id, since=past_moment_for_events_lookup),
        ])
        triage._gather_relevant_data_for_first_triage_note.assert_has_calls([
            call(edge_1_data, events_1),
            call(edge_2_data, events_2),
        ])
        template_renderer.compose_email_object.assert_has_calls([
            call(relevant_data_for_triage_note_1),
            call(relevant_data_for_triage_note_2),
        ])
        triage._send_email.assert_has_awaits([
            call(email_body_1), call(email_body_2),
        ])
        logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def gather_relevant_data_for_first_triage_note_with_no_missing_data_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 100, 'edge_id': 200}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567', 'name': 'Travis Touchdown'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1', 'displayName': 'Solid Snake'}},
                {'linkId': 9012, 'link': {'state': 'STABLE', 'interface': 'GE7', 'displayName': 'Big Boss'}},
                {'linkId': 3456, 'link': {'state': 'STABLE', 'interface': 'INTERNET3', 'displayName': 'Otacon'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_data = {'edge_id': edge_full_id, 'edge_status': edge_status}

        event_1 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 00:40:00+00:00',
            'message': 'Link GE7 is now DEAD'
        }
        event_2 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 01:40:00+00:00',
            'message': 'Link GE1 is now DEAD'
        }
        event_3 = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 02:40:00+00:00',
            'message': 'Link GE1 is no longer DEAD'
        }
        event_4 = {
            'event': 'EDGE_NEW_DEVICE',
            'category': 'EDGE',
            'eventTime': '2019-07-30 03:40:00+00:00',
            'message': 'New or updated client device'
        }
        event_5 = {
            'event': 'EDGE_INTERFACE_UP',
            'category': 'SYSTEM',
            'eventTime': '2019-07-29 04:40:00+00:00',
            'message': 'Interface GE1 is up'
        }
        event_6 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-31 05:40:00+00:00',
            'message': 'Link GE7 is now DEAD'
        }
        event_7 = {
            'event': 'EDGE_INTERFACE_DOWN',
            'category': 'SYSTEM',
            'eventTime': '2019-07-28 06:40:00+00:00',
            'message': 'Interface GE7 is down'
        }
        event_8 = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-01 07:40:00+00:00',
            'message': 'Link GE7 is no longer DEAD'
        }
        event_9 = {
            'event': 'EDGE_INTERFACE_UP',
            'category': 'NETWORK',
            'eventTime': '2019-08-01 08:40:00+00:00',
            'message': 'Interface INTERNET3 is up'
        }
        event_10 = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-08-01 09:40:00+00:00',
            'message': 'Link INTERNET3 is no longer DEAD'
        }
        event_11 = {
            'event': 'EDGE_UP',
            'category': 'EDGE',
            'eventTime': '2019-08-01 10:40:00+00:00',
            'message': 'Edge is up'
        }
        event_12 = {
            'event': 'EDGE_DOWN',
            'category': 'EDGE',
            'eventTime': '2019-08-01 11:40:00+00:00',
            'message': 'Edge is down'
        }
        event_13 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-08-01 12:40:00+00:00',
            'message': 'Link INTERNET3 is now DEAD'
        }
        events = [
            event_1, event_2, event_3, event_4, event_5,
            event_6, event_7, event_8, event_9, event_10,
            event_11, event_12, event_13,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['timezone'] = 'UTC'

        current_datetime = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                relevant_info = triage._gather_relevant_data_for_first_triage_note(edge_data, events)

        assert relevant_info == OrderedDict({
            'Orchestrator Instance': 'some-host',
            'Edge Name': 'Travis Touchdown',
            'Links': {
                'Edge': 'https://some-host/#!/operator/customer/100/monitor/edge/200/',
                'QoE': 'https://some-host/#!/operator/customer/100/monitor/edge/200/qoe/',
                'Transport': 'https://some-host/#!/operator/customer/100/monitor/edge/200/links/',
                'Events': 'https://some-host/#!/operator/customer/100/monitor/events/',
            },
            'Edge Status': 'OFFLINE',
            'Serial': 'VC1234567',
            'Interface GE1': empty_str,
            'Interface GE1 Label': 'Solid Snake',
            'Interface GE1 Status': 'DISCONNECTED',
            'Interface GE7': empty_str,
            'Interface GE7 Label': 'Big Boss',
            'Interface GE7 Status': 'STABLE',
            'Interface INTERNET3': empty_str,
            'Interface INTERNET3 Label': 'Otacon',
            'Interface INTERNET3 Status': 'STABLE',
            'Last Edge Online': parse('2019-08-01 10:40:00+00:00').astimezone(timezone('UTC')),
            'Last Edge Offline': parse('2019-08-01 11:40:00+00:00').astimezone(timezone('UTC')),
            'Last GE1 Interface Online': parse('2019-07-30 02:40:00+00:00').astimezone(timezone('UTC')),
            'Last GE1 Interface Offline': parse('2019-07-30 01:40:00+00:00').astimezone(timezone('UTC')),
            'Last GE7 Interface Online': parse('2019-07-01 07:40:00+00:00').astimezone(timezone('UTC')),
            'Last GE7 Interface Offline': parse('2019-07-30 00:40:00+00:00').astimezone(timezone('UTC')),
            'Last INTERNET3 Interface Online': parse('2019-08-01 09:40:00+00:00').astimezone(timezone('UTC')),
            'Last INTERNET3 Interface Offline': parse('2019-08-01 12:40:00+00:00').astimezone(timezone('UTC')),
        })

    @pytest.mark.asyncio
    async def gather_relevant_data_for_first_triage_note_with_missing_data_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 100, 'edge_id': 200}
        edge_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567', 'name': 'Travis Touchdown'},
            'links': [
                {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1', 'displayName': 'Solid Snake'}},
                {'linkId': 3456, 'link': None},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }
        edge_data = {'edge_id': edge_full_id, 'edge_status': edge_status}
        events = [
            {
                'event': 'LINK_DEAD',
                'category': 'NETWORK',
                'eventTime': '2019-08-01 12:40:00+00:00',
                'message': 'Link INTERNET3 is now DEAD'
            }
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['timezone'] = 'UTC'

        current_datetime = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(triage_module, 'datetime', new=datetime_mock):
                relevant_info = triage._gather_relevant_data_for_first_triage_note(edge_data, events)

        assert relevant_info == OrderedDict({
            'Orchestrator Instance': 'some-host',
            'Edge Name': 'Travis Touchdown',
            'Links': {
                'Edge': 'https://some-host/#!/operator/customer/100/monitor/edge/200/',
                'QoE': 'https://some-host/#!/operator/customer/100/monitor/edge/200/qoe/',
                'Transport': 'https://some-host/#!/operator/customer/100/monitor/edge/200/links/',
                'Events': 'https://some-host/#!/operator/customer/100/monitor/events/',
            },
            'Edge Status': 'OFFLINE',
            'Serial': 'VC1234567',
            'Interface GE1': empty_str,
            'Interface GE1 Label': 'Solid Snake',
            'Interface GE1 Status': 'DISCONNECTED',
            'Last Edge Online': None,
            'Last Edge Offline': None,
            'Last GE1 Interface Online': None,
            'Last GE1 Interface Offline': None,
        })

    @pytest.mark.asyncio
    async def send_email_test(self):
        email_data = {
            'request_id': uuid(),
            'email_data': {
                'subject': f'Service outage triage',
                'recipient': 'some-recipient',
                'text': 'this is the accessible text for the email',
                'html': '<html><head>some-data</head><body>some-more-data</body></html>',
                'images': [],
                'attachments': []
            }
        }

        email_response = {'status': 200}

        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=email_response)

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        result = await triage._send_email(email_data)

        event_bus.rpc_request.assert_awaited_once_with("notification.email.request", email_data, timeout=10)
        assert result == email_response

    def transform_relevant_data_into_ticket_note_test(self):
        relevant_data = OrderedDict({
            'Orchestrator Instance': 'some-host',
            'Edge Name': 'Travis Touchdown',
            'Links': {
                'Edge': 'https://some-host/#!/operator/customer/100/monitor/edge/200/',
                'QoE': 'https://some-host/#!/operator/customer/100/monitor/edge/200/qoe/',
                'Transport': 'https://some-host/#!/operator/customer/100/monitor/edge/200/links/',
                'Events': 'https://some-host/#!/operator/customer/100/monitor/events/',
            },
            'Edge Status': 'OFFLINE',
            'Serial': 'VC1234567',
            'Interface GE1': empty_str,
            'Interface GE1 Label': 'Solid Snake',
            'Interface GE1 Status': 'DISCONNECTED',
            'Interface GE2': empty_str,
            'Interface GE2 Label': None,
            'Interface GE2 Status': 'Interface GE2 not available',
            'Interface INTERNET3': empty_str,
            'Interface INTERNET3 Label': 'Otacon',
            'Interface INTERNET3 Status': 'STABLE',
            'Interface GE10': empty_str,
            'Interface GE10 Label': 'Big Boss',
            'Interface GE10 Status': 'STABLE',
            'Last Edge Online': parse('2019-08-01 10:40:00+00:00'),
            'Last Edge Offline': parse('2019-08-01 11:40:00+00:00'),
            'Last GE1 Interface Online': parse('2019-07-30 02:40:00+00:00'),
            'Last GE1 Interface Offline': parse('2019-07-30 01:40:00+00:00'),
            'Last GE2 Interface Online': parse('2019-07-01 07:40:00+00:00'),
            'Last GE2 Interface Offline': parse('2019-07-30 00:40:00+00:00'),
            'Last INTERNET3 Interface Online': parse('2019-08-01 09:40:00+00:00'),
            'Last INTERNET3 Interface Offline': None,
            'Last GE10 Interface Online': None,
            'Last GE10 Interface Offline': None,
        })

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        result = triage._transform_relevant_data_into_ticket_note(relevant_data)

        assert result == os.linesep.join([
            '#*Automation Engine*#',
            'Triage',
            'Orchestrator Instance: some-host',
            'Edge Name: Travis Touchdown',
            'Links: [Edge|https://some-host/#!/operator/customer/100/monitor/edge/200/] - '
            '[QoE|https://some-host/#!/operator/customer/100/monitor/edge/200/qoe/] - '
            '[Transport|https://some-host/#!/operator/customer/100/monitor/edge/200/links/] - '
            '[Events|https://some-host/#!/operator/customer/100/monitor/events/]',
            'Edge Status: OFFLINE',
            'Serial: VC1234567',
            'Interface GE1',
            'Interface GE1 Label: Solid Snake',
            'Interface GE1 Status: DISCONNECTED',
            'Interface GE2',
            'Interface GE2 Label: None',
            'Interface GE2 Status: Interface GE2 not available',
            'Interface INTERNET3',
            'Interface INTERNET3 Label: Otacon',
            'Interface INTERNET3 Status: STABLE',
            'Interface GE10',
            'Interface GE10 Label: Big Boss',
            'Interface GE10 Status: STABLE',
            'Last Edge Online: 2019-08-01 10:40:00+00:00',
            'Last Edge Offline: 2019-08-01 11:40:00+00:00',
            'Last GE1 Interface Online: 2019-07-30 02:40:00+00:00',
            'Last GE1 Interface Offline: 2019-07-30 01:40:00+00:00',
            'Last GE2 Interface Online: 2019-07-01 07:40:00+00:00',
            'Last GE2 Interface Offline: 2019-07-30 00:40:00+00:00',
            'Last INTERNET3 Interface Online: 2019-08-01 09:40:00+00:00',
            'Last INTERNET3 Interface Offline: None',
            'Last GE10 Interface Online: None',
            'Last GE10 Interface Offline: None',
        ])

    def extract_client_id_with_match_found_test(self):
        client_id = 12345
        enterprise_name = f'EVIL-CORP|{client_id}|'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        result_client_id = triage._extract_client_id(enterprise_name)
        assert result_client_id == client_id

    def extract_client_id_with_no_match_found_test(self):
        enterprise_name = f'EVIL-CORP'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        outage_repository = Mock()

        triage = Triage(event_bus, logger, scheduler, config, template_renderer, outage_repository)

        result_client_id = triage._extract_client_id(enterprise_name)
        assert result_client_id == 9994

    def get_first_element_matching_with_match_test(self):
        payload = range(0, 11)

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = Triage._get_first_element_matching(iterable=payload, condition=cond)
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

        result = Triage._get_first_element_matching(iterable=payload, condition=cond, fallback=fallback_value)

        assert result == fallback_value
