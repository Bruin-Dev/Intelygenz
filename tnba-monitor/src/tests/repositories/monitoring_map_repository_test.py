from datetime import datetime
from unittest.mock import Mock
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
        velocloud_repository = Mock()
        bruin_repository = Mock()

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, velocloud_repository,
                                                            bruin_repository, logger)

        assert monitoring_map_repository._event_bus is event_bus
        assert monitoring_map_repository._logger is logger
        assert monitoring_map_repository._scheduler is scheduler
        assert monitoring_map_repository._config is config
        assert monitoring_map_repository._velocloud_repository is velocloud_repository
        assert monitoring_map_repository._bruin_repository is bruin_repository

        assert monitoring_map_repository._monitoring_map_cache == {}

    @pytest.mark.asyncio
    async def start_create_monitoring_map_job_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        bruin_repository = Mock()

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, velocloud_repository,
                                                            bruin_repository, logger)

        await monitoring_map_repository.start_create_monitoring_map_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses,
            'interval',
            minutes=config.MONITOR_CONFIG["refresh_map_time"],
            next_run_time=undefined,
            replace_existing=False,
            id='_create_client_id_to_dict_of_serials_dict',
        )

    @pytest.mark.asyncio
    async def start_create_monitoring_map_job_with_exec_on_start_true_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        bruin_repository = Mock()

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, velocloud_repository,
                                                            bruin_repository, logger)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)

        with patch.object(monitoring_map_repository_module, 'datetime', new=datetime_mock):
            with patch.object(monitoring_map_repository_module, 'timezone', new=Mock()):
                await monitoring_map_repository.start_create_monitoring_map_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses,
            'interval',
            minutes=config.MONITOR_CONFIG["refresh_map_time"],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_create_client_id_to_dict_of_serials_dict',
        )

    def get_monitoring_map_cache_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        bruin_repository = Mock()

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, velocloud_repository,
                                                            bruin_repository, logger)

        assert monitoring_map_repository.get_monitoring_map_cache() == monitoring_map_repository._monitoring_map_cache
        assert monitoring_map_repository.get_monitoring_map_cache() is not \
            monitoring_map_repository._monitoring_map_cache

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
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1112223'

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_1_serial},
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
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
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

        bruin_client_info_1_response_body = {
            'client_id': bruin_client_1,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_1_response = {
            'body': bruin_client_info_1_response_body,
            'status': 200,
        }

        bruin_client_info_2_response_body = {
            'client_id': bruin_client_2,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_2_response = {
            'body': bruin_client_info_2_response_body,
            'status': 200,
        }

        bruin_client_info_3_response_body = {
            'client_id': bruin_client_2,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_3_response = {
            'body': bruin_client_info_3_response_body,
            'status': 200,
        }

        edge_1_status_with_bruin_client_info = {
            **edge_1_status,
            'bruin_client_info': bruin_client_info_1_response_body,
        }
        edge_2_status_with_bruin_client_info = {
            **edge_2_status,
            'bruin_client_info': bruin_client_info_2_response_body,
        }
        edge_3_status_with_bruin_client_info = {
            **edge_3_status,
            'bruin_client_info': bruin_client_info_3_response_body,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_tnba_monitoring = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response,
            edge_2_status_response,
            edge_3_status_response,
        ])

        bruin_repository = Mock()
        bruin_repository.get_client_info = CoroutineMock(side_effect=[
            bruin_client_info_1_response,
            bruin_client_info_2_response,
            bruin_client_info_3_response,
        ])
        management_status_response_body = 'Fake status'
        management_status_response = {
            "body": management_status_response_body,
            "status": 200,
        }
        bruin_repository.get_management_status = CoroutineMock(return_value=management_status_response)
        bruin_repository.is_management_status_active = Mock(return_value=True)
        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, velocloud_repository,
                                                            bruin_repository, logger)

        async def gather_mock(*args, **kwargs):
            await monitoring_map_repository._process_edge_and_tickets(edge_1_full_id)
            await monitoring_map_repository._process_edge_and_tickets(edge_2_full_id)
            await monitoring_map_repository._process_edge_and_tickets(edge_3_full_id)

        with patch.object(monitoring_map_repository_module.asyncio, "gather", return_value=gather_mock()):
            await monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses()

        expected_cache = {
            bruin_client_1: {
                edge_1_serial: {
                    'edge_id': edge_1_full_id,
                    'edge_status': edge_1_status_with_bruin_client_info,
                }
            },
            bruin_client_2: {
                edge_2_serial: {
                    'edge_id': edge_2_full_id,
                    'edge_status': edge_2_status_with_bruin_client_info,
                },
                edge_3_serial: {
                    'edge_id': edge_3_full_id,
                    'edge_status': edge_3_status_with_bruin_client_info,
                },
            }
        }
        assert monitoring_map_repository._monitoring_map_cache == expected_cache

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

        bruin_client_info_2_response_body = {
            'client_id': bruin_client_2,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_2_response = {
            'body': bruin_client_info_2_response_body,
            'status': 200,
        }

        edge_2_status_with_bruin_client_info = {
            **edge_2_status,
            'bruin_client_info': bruin_client_info_2_response_body,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_tnba_monitoring = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response, edge_2_status_response, edge_3_status_response
        ])

        bruin_repository = Mock()
        bruin_repository.get_client_info = CoroutineMock(return_value=bruin_client_info_2_response)
        management_status_response_body = 'Fake status'
        management_status_response = {
            "body": management_status_response_body,
            "status": 200,
        }
        bruin_repository.get_management_status = CoroutineMock(return_value=management_status_response)
        bruin_repository.is_management_status_active = Mock(return_value=True)

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, velocloud_repository,
                                                            bruin_repository, logger)

        async def gather_mock(*args, **kwargs):
            await monitoring_map_repository._process_edge_and_tickets(edge_1_full_id)
            await monitoring_map_repository._process_edge_and_tickets(edge_2_full_id)
            await monitoring_map_repository._process_edge_and_tickets(edge_3_full_id)

        with patch.object(monitoring_map_repository_module.asyncio, "gather", return_value=gather_mock()):
            await monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses()

        expected = {bruin_client_2: {edge_2_serial: {'edge_id': edge_2_full_id,
                                                     'edge_status': edge_2_status_with_bruin_client_info}}}

        assert monitoring_map_repository.get_monitoring_map_cache() == expected

        expected_cache = {
            bruin_client_2: {
                edge_2_serial: {
                    'edge_id': edge_2_full_id,
                    'edge_status': edge_2_status_with_bruin_client_info,
                },
            }
        }
        assert monitoring_map_repository._monitoring_map_cache == expected_cache

    @pytest.mark.asyncio
    async def map_bruin_client_ids_to_edges_serials_and_statuses_with_edge_list_request_not_having_2xx_status_test(
            self):
        uuid_1 = uuid()

        edge_list_response = {
            'request_id': uuid_1,
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_tnba_monitoring = CoroutineMock(return_value=edge_list_response)

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, velocloud_repository,
                                                            bruin_repository, logger)

        await monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses()

        assert monitoring_map_repository._monitoring_map_cache == {}

    @pytest.mark.asyncio
    async def map_bruin_client_ids_to_edges_serials_and_statuses_with_edge_status_request_not_having_2xx_status_test(
            self):
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

        bruin_client = 54321
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1111111'

        edge_1_status_response = {
            'request_id': uuid_2,
            'body': 'Got internal error from Velocloud',
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
            'request_id': uuid_3,
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
            'request_id': uuid_4,
            'body': {
                'edge_id': edge_3_full_id,
                'edge_info': edge_3_status,
            },
            'status': 200,
        }

        bruin_client_info_response_body = {
            'client_id': bruin_client,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_response = {
            'body': bruin_client_info_response_body,
            'status': 200,
        }

        edge_2_status_with_bruin_client_info = {
            **edge_2_status,
            'bruin_client_info': bruin_client_info_response_body,
        }
        edge_3_status_with_bruin_client_info = {
            **edge_3_status,
            'bruin_client_info': bruin_client_info_response_body,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_tnba_monitoring = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response, edge_2_status_response, edge_3_status_response,
        ])

        bruin_repository = Mock()
        bruin_repository.get_client_info = CoroutineMock(return_value=bruin_client_info_response)
        management_status_response_body = 'Fake status'
        management_status_response = {
            "body": management_status_response_body,
            "status": 200,
        }
        bruin_repository.get_management_status = CoroutineMock(return_value=management_status_response)
        bruin_repository.is_management_status_active = Mock(return_value=True)

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, velocloud_repository,
                                                            bruin_repository, logger)

        async def gather_mock(*args, **kwargs):
            await monitoring_map_repository._process_edge_and_tickets(edge_1_full_id)
            await monitoring_map_repository._process_edge_and_tickets(edge_2_full_id)
            await monitoring_map_repository._process_edge_and_tickets(edge_3_full_id)

        with patch.object(monitoring_map_repository_module.asyncio, "gather", return_value=gather_mock()):
            await monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses()

        expected = {
            bruin_client: {
                edge_3_serial: {'edge_id': edge_3_full_id, 'edge_status': edge_3_status_with_bruin_client_info},
                edge_2_serial: {'edge_id': edge_2_full_id, 'edge_status': edge_2_status_with_bruin_client_info},
            }
        }
        assert monitoring_map_repository._monitoring_map_cache == expected

    @pytest.mark.asyncio
    async def map_bruin_client_ids_to_edges_serials_and_statuses_with_client_info_request_not_having_2xx_status_test(
            self):
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

        bruin_client_info_bad_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        bruin_client_info_3_response_body = {
            'client_id': bruin_client_2,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_3_response = {
            'body': bruin_client_info_3_response_body,
            'status': 200,
        }

        edge_3_status_with_bruin_client_info = {
            **edge_3_status,
            'bruin_client_info': bruin_client_info_3_response_body,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_tnba_monitoring = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response, edge_2_status_response, edge_3_status_response,
        ])

        bruin_repository = Mock()
        bruin_repository.get_client_info = CoroutineMock(side_effect=[
            bruin_client_info_bad_response,
            bruin_client_info_bad_response,
            bruin_client_info_3_response,
        ])
        management_status_response_body = 'Fake status'
        management_status_response = {
            "body": management_status_response_body,
            "status": 200,
        }
        bruin_repository.get_management_status = CoroutineMock(return_value=management_status_response)
        bruin_repository.is_management_status_active = Mock(return_value=True)

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, velocloud_repository,
                                                            bruin_repository, logger)

        async def gather_mock(*args, **kwargs):
            await monitoring_map_repository._process_edge_and_tickets(edge_1_full_id)
            await monitoring_map_repository._process_edge_and_tickets(edge_2_full_id)
            await monitoring_map_repository._process_edge_and_tickets(edge_3_full_id)

        with patch.object(monitoring_map_repository_module.asyncio, "gather", return_value=gather_mock()):
            await monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses()

        expected = {
            bruin_client_2: {
                edge_3_serial: {
                    'edge_id': edge_3_full_id,
                    'edge_status': edge_3_status_with_bruin_client_info,
                },
            }
        }
        assert monitoring_map_repository._monitoring_map_cache == expected

    @pytest.mark.asyncio
    async def map_bruin_client_ids_to_edges_serials_and_statuses_with_bruin_client_info_having_null_client_id_test(
            self):
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

        bruin_client_info_1_response_body = {
            'client_id': None,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_1_response = {
            'body': bruin_client_info_1_response_body,
            'status': 200,
        }

        bruin_client_info_2_response_body = {
            'client_id': bruin_client_1,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_2_response = {
            'body': bruin_client_info_2_response_body,
            'status': 200,
        }

        bruin_client_info_3_response_body = {
            'client_id': bruin_client_2,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_3_response = {
            'body': bruin_client_info_3_response_body,
            'status': 200,
        }

        edge_2_status_with_bruin_client_info = {
            **edge_2_status,
            'bruin_client_info': bruin_client_info_2_response_body,
        }
        edge_3_status_with_bruin_client_info = {
            **edge_3_status,
            'bruin_client_info': bruin_client_info_3_response_body,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_tnba_monitoring = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response, edge_2_status_response, edge_3_status_response,
        ])

        bruin_repository = Mock()
        bruin_repository.get_client_info = CoroutineMock(side_effect=[
            bruin_client_info_1_response,
            bruin_client_info_2_response,
            bruin_client_info_3_response,
        ])
        management_status_response_body = 'Fake status'
        management_status_response = {
            "body": management_status_response_body,
            "status": 200,
        }
        bruin_repository.get_management_status = CoroutineMock(return_value=management_status_response)
        bruin_repository.is_management_status_active = Mock(return_value=True)

        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, velocloud_repository,
                                                            bruin_repository, logger)

        async def gather_mock(*args, **kwargs):
            await monitoring_map_repository._process_edge_and_tickets(edge_1_full_id)
            await monitoring_map_repository._process_edge_and_tickets(edge_2_full_id)
            await monitoring_map_repository._process_edge_and_tickets(edge_3_full_id)

        with patch.object(monitoring_map_repository_module.asyncio, "gather", return_value=gather_mock()):
            await monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses()

        expected = {
            bruin_client_1: {
                edge_2_serial: {'edge_id': edge_2_full_id, 'edge_status': edge_2_status_with_bruin_client_info},
            },
            bruin_client_2: {
                edge_3_serial: {'edge_id': edge_3_full_id, 'edge_status': edge_3_status_with_bruin_client_info},
            }
        }
        assert monitoring_map_repository._monitoring_map_cache == expected

    @pytest.mark.asyncio
    async def map_bruin_client_ids_to_edges_serials_and_statuses_management_status_non_2xx_test(self):
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
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1112223'

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_1_serial},
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
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
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

        bruin_client_info_1_response_body = {
            'client_id': bruin_client_1,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_1_response = {
            'body': bruin_client_info_1_response_body,
            'status': 200,
        }

        bruin_client_info_2_response_body = {
            'client_id': bruin_client_2,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_2_response = {
            'body': bruin_client_info_2_response_body,
            'status': 200,
        }

        bruin_client_info_3_response_body = {
            'client_id': bruin_client_2,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_3_response = {
            'body': bruin_client_info_3_response_body,
            'status': 200,
        }

        edge_1_status_with_bruin_client_info = {
            **edge_1_status,
            'bruin_client_info': bruin_client_info_1_response_body,
        }
        edge_2_status_with_bruin_client_info = {
            **edge_2_status,
            'bruin_client_info': bruin_client_info_2_response_body,
        }
        edge_3_status_with_bruin_client_info = {
            **edge_3_status,
            'bruin_client_info': bruin_client_info_3_response_body,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_tnba_monitoring = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response,
            edge_2_status_response,
            edge_3_status_response,
        ])

        bruin_repository = Mock()
        bruin_repository.get_client_info = CoroutineMock(side_effect=[
            bruin_client_info_1_response,
            bruin_client_info_2_response,
            bruin_client_info_3_response,
        ])
        management_status_response_body = 'Fake status'
        management_status_response = {
            "body": management_status_response_body,
            "status": 200,
        }
        management_status_fail_response = {
            "body": "failed",
            "status": 500,
        }
        bruin_repository.get_management_status = CoroutineMock(side_effect=[management_status_response,
                                                                            management_status_fail_response,
                                                                            management_status_response])
        bruin_repository.is_management_status_active = Mock(return_value=True)
        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, velocloud_repository,
                                                            bruin_repository, logger)

        async def gather_mock(*args, **kwargs):
            await monitoring_map_repository._process_edge_and_tickets(edge_1_full_id)
            await monitoring_map_repository._process_edge_and_tickets(edge_2_full_id)
            await monitoring_map_repository._process_edge_and_tickets(edge_3_full_id)

        with patch.object(monitoring_map_repository_module.asyncio, "gather", return_value=gather_mock()):
            await monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses()

        expected_cache = {
            bruin_client_1: {
                edge_1_serial: {
                    'edge_id': edge_1_full_id,
                    'edge_status': edge_1_status_with_bruin_client_info,
                }
            },
            bruin_client_2: {
                edge_3_serial: {
                    'edge_id': edge_3_full_id,
                    'edge_status': edge_3_status_with_bruin_client_info,
                },
            }
        }
        assert monitoring_map_repository._monitoring_map_cache == expected_cache

    @pytest.mark.asyncio
    async def map_bruin_client_ids_to_edges_serials_and_statuses_management_status_not_active_test(self):
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
        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC7654321'
        edge_3_serial = 'VC1112223'

        edge_1_status = {
            'edges': {'edgeState': 'OFFLINE', 'serialNumber': edge_1_serial},
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
            'edges': {'edgeState': 'CONNECTED', 'serialNumber': edge_3_serial},
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

        bruin_client_info_1_response_body = {
            'client_id': bruin_client_1,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_1_response = {
            'body': bruin_client_info_1_response_body,
            'status': 200,
        }

        bruin_client_info_2_response_body = {
            'client_id': bruin_client_2,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_2_response = {
            'body': bruin_client_info_2_response_body,
            'status': 200,
        }

        bruin_client_info_3_response_body = {
            'client_id': bruin_client_2,
            'client_name': 'METTEL/NEW YORK',
        }
        bruin_client_info_3_response = {
            'body': bruin_client_info_3_response_body,
            'status': 200,
        }

        edge_1_status_with_bruin_client_info = {
            **edge_1_status,
            'bruin_client_info': bruin_client_info_1_response_body,
        }
        edge_2_status_with_bruin_client_info = {
            **edge_2_status,
            'bruin_client_info': bruin_client_info_2_response_body,
        }
        edge_3_status_with_bruin_client_info = {
            **edge_3_status,
            'bruin_client_info': bruin_client_info_3_response_body,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        velocloud_repository = Mock()
        velocloud_repository.get_edges_for_tnba_monitoring = CoroutineMock(return_value=edge_list_response)
        velocloud_repository.get_edge_status = CoroutineMock(side_effect=[
            edge_1_status_response,
            edge_2_status_response,
            edge_3_status_response,
        ])

        bruin_repository = Mock()
        bruin_repository.get_client_info = CoroutineMock(side_effect=[
            bruin_client_info_1_response,
            bruin_client_info_2_response,
            bruin_client_info_3_response,
        ])
        management_status_response_body = 'Fake status'
        management_status_response = {
            "body": management_status_response_body,
            "status": 200,
        }
        bruin_repository.get_management_status = CoroutineMock(return_value=management_status_response)
        bruin_repository.is_management_status_active = Mock(side_effect=[False, True, True])
        monitoring_map_repository = MonitoringMapRepository(config, scheduler, event_bus, velocloud_repository,
                                                            bruin_repository, logger)

        async def gather_mock(*args, **kwargs):
            await monitoring_map_repository._process_edge_and_tickets(edge_1_full_id)
            await monitoring_map_repository._process_edge_and_tickets(edge_2_full_id)
            await monitoring_map_repository._process_edge_and_tickets(edge_3_full_id)

        with patch.object(monitoring_map_repository_module.asyncio, "gather", return_value=gather_mock()):
            await monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses()

        expected_cache = {
            bruin_client_2: {
                edge_2_serial: {
                    'edge_id': edge_2_full_id,
                    'edge_status': edge_2_status_with_bruin_client_info,
                },
                edge_3_serial: {
                    'edge_id': edge_3_full_id,
                    'edge_status': edge_3_status_with_bruin_client_info,
                },
            }
        }
        assert monitoring_map_repository._monitoring_map_cache == expected_cache
