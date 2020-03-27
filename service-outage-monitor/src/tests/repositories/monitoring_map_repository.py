import os
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest

from apscheduler.util import undefined
from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import monitoring_map_repository as monitoring_map_repository_module
from application.repositories.monitoring_map_repository import MonitoringMapRepository
from config import testconfig


class TestMonitoringMapRepository:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        monitoring_map_cache = {}

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, logger)

        assert monitoring_map_repository._monitoring_map_cache == monitoring_map_cache
        assert monitoring_map_repository._event_bus is event_bus
        assert monitoring_map_repository._logger is logger
        assert monitoring_map_repository._scheduler is scheduler
        assert monitoring_map_repository._config is config

    @pytest.mark.asyncio
    async def start_create_monitoring_map_job_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, logger)

        await monitoring_map_repository.start_create_monitoring_map_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            monitoring_map_repository._map_bruin_client_ids_to_edges_serials_and_statuses,
            'interval',
            minutes=config.MONITOR_MAP_CONFIG["refresh_map_time"],
            next_run_time=undefined,
            replace_existing=True,
            id='_create_client_id_to_dict_of_serials_dict',
        )

    def get_monitoring_map_cache_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, logger)

        monitoring_map_cache = {}

        assert monitoring_map_repository.get_monitoring_map_cache() is not monitoring_map_cache
        assert id(monitoring_map_repository.get_monitoring_map_cache()) != id(monitoring_map_cache)

    @pytest.mark.asyncio
    async def map_bruin_client_ids_to_edges_serials_and_statuses_test(self):
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

        bruin_client_2 = 54321
        edge_2_serial = 'VC7654321'
        bruin_client_2_request_id = uuid_3

        bruin_client_info_2_response_body = {
            'client_id': bruin_client_2,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_2_response = {
            'body': bruin_client_info_2_response_body,
            'status': 200,
        }

        event_bus = Mock()

        event_bus.rpc_request = CoroutineMock(return_value=edge_list_response)

        logger = Mock()
        scheduler = Mock()
        config = testconfig

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, logger)
        monitoring_map_repository._notify_failing_rpc_request_for_edge_list = CoroutineMock()
        monitoring_map_repository._notify_http_error_when_requesting_edge_list_from_velocloud = CoroutineMock()

        monitoring_map_repository._get_edges_for_monitoring = \
            CoroutineMock(return_value=edge_list_response)

        monitoring_map_repository._get_edge_status_by_id = CoroutineMock(side_effects=[
            edge_1_status_response, edge_2_status_response, edge_3_status_response
        ])

        monitoring_map_repository._get_bruin_client_info_by_serial = \
            CoroutineMock(return_value=bruin_client_info_2_response)

        await monitoring_map_repository._map_bruin_client_ids_to_edges_serials_and_statuses()

        assert monitoring_map_repository._monitoring_map_cache is not edge_list_response
        assert id(monitoring_map_repository._monitoring_map_cache) != id(edge_list_response)

    @pytest.mark.asyncio
    async def get_edges_for_monitoring_test(self):
        uuid_ = uuid()

        edge_list_response = {
            'request_id': uuid_,
            'body': [
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1},
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2},
            ],
            'status': 200,
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=edge_list_response)
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, logger)

        with patch.object(monitoring_map_repository_module, 'uuid', return_value=uuid_):
            result = await monitoring_map_repository._get_edges_for_monitoring()

        event_bus.rpc_request.assert_awaited_once_with(
            'edge.list.request',
            {'request_id': uuid_, 'body': {'filter': config.MONITOR_MAP_CONFIG['velo_filter']}},
            timeout=300,
        )
        assert result == edge_list_response

    @pytest.mark.asyncio
    async def get_edge_status_by_id_test(self):
        uuid_ = uuid()
        bruin_client_1 = 12345
        edge_1_serial = 'VC1234567'
        edge_1_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
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

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=edge_1_status_response)
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, logger)

        with patch.object(monitoring_map_repository_module, 'uuid', return_value=uuid_):
            result = await monitoring_map_repository._get_edge_status_by_id(edge_1_full_id)

        event_bus.rpc_request.assert_awaited_once_with(
            'edge.status.request',
            {'request_id': uuid_, 'body': edge_1_full_id},
            timeout=120,
        )
        assert result == edge_1_status_response

    @pytest.mark.asyncio
    async def get_bruin_client_info_by_serial_test(self):
        uuid_ = uuid()
        edge_1_serial = 'VC1234567'

        bruin_info_response = {
            'request_id': uuid_,
            'body': {},
            'status': 200,
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=bruin_info_response)
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, logger)

        with patch.object(monitoring_map_repository_module, 'uuid', return_value=uuid_):
            result = await monitoring_map_repository._get_bruin_client_info_by_serial(edge_1_serial)

        event_bus.rpc_request.assert_awaited_once_with(
            'bruin.customer.get.info',
            {'request_id': uuid_, 'body': {"service_number": edge_1_serial}},
            timeout=30,
        )
        assert result == bruin_info_response

    @pytest.mark.asyncio
    async def notify_failing_rpc_request_for_edge_list_test(self):
        uuid_ = uuid()

        error_message = 'An error occurred when requesting edge list from Velocloud'
        bruin_info_response = {
            'request_id': uuid_,
            'message': error_message,
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=bruin_info_response)
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, logger)

        with patch.object(monitoring_map_repository_module, 'uuid', return_value=uuid_):
            await monitoring_map_repository._notify_failing_rpc_request_for_edge_list()

        event_bus.rpc_request.assert_awaited_once_with(
            'notification.slack.request',
            {'request_id': uuid_, 'message': error_message},
            timeout=10,
        )

    @pytest.mark.asyncio
    async def notify_http_error_when_requesting_edge_list_from_velocloud_test(self):
        uuid_ = uuid()

        error_message = 'An error occurred when requesting edge list from Velocloud'
        bruin_info_response = {
            'request_id': uuid_,
            'message': error_message,
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=bruin_info_response)
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, logger)

        with patch.object(monitoring_map_repository_module, 'uuid', return_value=uuid_):
            await monitoring_map_repository._notify_failing_rpc_request_for_edge_list()

        event_bus.rpc_request.assert_awaited_once_with(
            'notification.slack.request',
            {'request_id': uuid_, 'message': error_message},
            timeout=10,
        )
