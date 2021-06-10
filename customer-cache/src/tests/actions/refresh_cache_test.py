from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from asynctest import CoroutineMock
from shortuuid import uuid
from tenacity import retry
from tenacity import stop_after_attempt

from application.actions import refresh_cache as refresh_cache_module
from application.actions.refresh_cache import RefreshCache
from application.repositories import EdgeIdentifier
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(refresh_cache_module, 'uuid', return_value=uuid_)


# Drops the random nature of some retry calls, this is more convenient when testing
def retry_mock(attempts):
    def inner(*args, **kwargs):
        return retry(stop=stop_after_attempt(attempts), reraise=True)

    return inner


class TestRefreshCache:

    def instance_test(self):
        config = testconfig
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        storage_repository = Mock()
        velocloud_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()

        refresh_cache = RefreshCache(config, event_bus, logger, scheduler, storage_repository,
                                     bruin_repository, velocloud_repository, notifications_repository)

        assert refresh_cache._config == config
        assert refresh_cache._event_bus == event_bus
        assert refresh_cache._logger == logger
        assert refresh_cache._scheduler == scheduler
        assert refresh_cache._storage_repository == storage_repository
        assert refresh_cache._velocloud_repository == velocloud_repository
        assert refresh_cache._bruin_repository == bruin_repository
        assert refresh_cache._notifications_repository == notifications_repository

    @pytest.mark.asyncio
    async def schedule_cache_refresh_job_test(self, instance_refresh_cache):
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(refresh_cache_module, 'datetime', new=datetime_mock):
            with patch.object(refresh_cache_module, 'timezone', new=Mock()):
                await instance_refresh_cache.schedule_cache_refresh()

        instance_refresh_cache._scheduler.add_job.assert_called_once_with(
            instance_refresh_cache._refresh_cache, 'interval',
            minutes=instance_refresh_cache._config.REFRESH_CONFIG['refresh_map_minutes'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_refresh_cache',
        )

    @pytest.mark.asyncio
    async def schedule_cache_refresh_job_with_job_id_already_executing_test(self, instance_refresh_cache):
        instance_refresh_cache._scheduler.add_job = Mock(side_effect=ConflictingIdError('some-duplicated-id'))

        try:
            await instance_refresh_cache.schedule_cache_refresh()
        except ConflictingIdError:
            instance_refresh_cache._scheduler.add_job.assert_called_once_with(
                instance_refresh_cache._refresh_cache, 'interval',
                minutes=instance_refresh_cache._config.REFRESH_CONFIG['refresh_map_minutes'],
                next_run_time=undefined,
                replace_existing=False,
                id='_refresh_cache',
            )

    @pytest.mark.asyncio
    async def refresh_cache_edge_test(self, instance_refresh_cache, instance_cache_edges):

        instance_refresh_cache._event_bus.rpc_request = CoroutineMock()
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        instance_refresh_cache._logger.error = Mock()
        instance_refresh_cache._velocloud_repository.get_all_velo_edges = CoroutineMock(
            return_value=instance_cache_edges)

        instance_refresh_cache._partial_refresh_cache = CoroutineMock()

        tenacity_retry_mock = patch.object(refresh_cache_module, 'retry', side_effect=retry_mock(attempts=1))
        with patch.object(refresh_cache_module, 'datetime', new=datetime_mock):
            with uuid_mock, tenacity_retry_mock:
                await instance_refresh_cache._refresh_cache()

        instance_refresh_cache._partial_refresh_cache.assert_awaited_once_with('some host',
                                                                               instance_cache_edges)

    @pytest.mark.asyncio
    async def refresh_cache_edge_list_failed_test(self, instance_refresh_cache):
        error = "Couldn't find any edge to refresh the cache"
        err_msg_refresh_cache = f"Maximum retries happened while while refreshing the cache cause of error was {error}"
        instance_refresh_cache._event_bus.rpc_request = CoroutineMock()

        instance_refresh_cache._logger.error = Mock()
        instance_refresh_cache._velocloud_repository.get_all_velo_edges = CoroutineMock(return_value=None)

        instance_refresh_cache._partial_refresh_cache = CoroutineMock()
        instance_refresh_cache._notifications_repository.send_slack_message = CoroutineMock()

        tenacity_retry_mock = patch.object(refresh_cache_module, 'retry', side_effect=retry_mock(attempts=1))
        with uuid_mock, tenacity_retry_mock:
            await instance_refresh_cache._refresh_cache()

        instance_refresh_cache._partial_refresh_cache.assert_not_awaited()
        instance_refresh_cache._notifications_repository.send_slack_message.assert_awaited_with(
            err_msg_refresh_cache
        )

    @pytest.mark.asyncio
    async def refresh_cache_edge_list_failed_with_several_consecutive_failures_test(self, instance_refresh_cache,
                                                                                    instance_err_msg_refresh_cache):
        instance_err_msg_refresh_cache['request_id'] = uuid_
        instance_refresh_cache._event_bus.rpc_request = CoroutineMock()

        instance_refresh_cache._logger.error = Mock()

        instance_refresh_cache._velocloud_repository.get_all_velo_edges = CoroutineMock(return_value=None)

        instance_refresh_cache._partial_refresh_cache = CoroutineMock()
        instance_refresh_cache._notifications_repository.send_slack_message = CoroutineMock()

        retry_mock_fn = retry_mock(attempts=instance_refresh_cache._config.REFRESH_CONFIG['attempts_threshold'])
        tenacity_retry_mock = patch.object(refresh_cache_module, 'retry', side_effect=retry_mock_fn)
        with uuid_mock, tenacity_retry_mock:
            await instance_refresh_cache._refresh_cache()

        instance_refresh_cache._partial_refresh_cache.assert_not_awaited()
        instance_refresh_cache._notifications_repository.send_slack_message.assert_awaited()

    @pytest.mark.asyncio
    async def partial_refresh_cache_with_edges_and_not_invalid_edges_test(self, instance_refresh_cache):
        # Scenario: Bruin returns all management statuses correctly
        edge_from_bruin_1 = {
            'edge': {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': "VCO191919",
            'bruin_client_info': {"client_id": 1991, "client_name": "Tet Corporation"}
        }
        edge_from_bruin_1_with_config = {
            'edge': {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': "VCO191919",
            'bruin_client_info': {"client_id": 1991, "client_name": "Tet Corporation"},
            'links_configuration':
                [
                    {
                        'interfaces': ['GE1'],
                        'internal_id': '00000001-ac48-47a0-81a7-80c8c320f486',
                        'mode': 'PUBLIC',
                        'type': 'WIRED',
                        'last_active': '2020-09-29T04:45:15.000Z'
                    }
                ]
        }
        edge_from_bruin_2 = {
            'edge': {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 2020},
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': "VCO202020",
            'bruin_client_info': {"client_id": 1991, "client_name": "Tet Corporation"}
        }
        edge_from_bruin_2_with_config = {
            'edge': {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': "VCO191919",
            'bruin_client_info': {"client_id": 1991, "client_name": "Tet Corporation"},
            'links_configuration':
                [
                    {
                        'interfaces': ['GE2'],
                        'internal_id': '00000001-ac48-47a0-81a7-80c8c320f485',
                        'mode': 'PUBLIC',
                        'type': 'WIRED',
                        'last_active': '2020-09-29T04:45:15.000Z'
                    }
                ]
        }
        edge_list = [{"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
                     {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1991}]
        stored_cache = [edge_from_bruin_1, edge_from_bruin_2]
        new_cache = [edge_from_bruin_1_with_config, edge_from_bruin_2_with_config]

        instance_refresh_cache._invalid_edges = {
            'mettel.velocloud.net': []
        }
        instance_refresh_cache._filter_edge_list = CoroutineMock(side_effect=[
            edge_from_bruin_1_with_config,
            edge_from_bruin_2_with_config,
        ])
        send_email_res = {"request_id": "asjkdhaskj8", "status": 200}
        instance_refresh_cache._event_bus.rpc_request = CoroutineMock(return_value=send_email_res)
        instance_refresh_cache._storage_repository.get_cache = Mock(return_value=stored_cache)
        instance_refresh_cache._cross_stored_cache_and_new_cache = Mock(return_value=new_cache)
        instance_refresh_cache._storage_repository.set_cache = Mock()
        instance_refresh_cache._velocloud_repository.add_edge_config = CoroutineMock(
            side_effect=[edge_from_bruin_1_with_config, edge_from_bruin_2_with_config])

        await instance_refresh_cache._partial_refresh_cache("mettel.velocloud.net", edge_list)

        instance_refresh_cache._filter_edge_list.assert_awaited()
        instance_refresh_cache._cross_stored_cache_and_new_cache.assert_called_once_with(
            stored_cache=stored_cache, new_cache=new_cache
        )
        instance_refresh_cache._storage_repository.set_cache.assert_called_once()

    @pytest.mark.asyncio
    async def partial_refresh_cache_with_edges_and_invalid_edges_test(self, instance_refresh_cache):
        # Scenario: Bruin returns most management statuses correctly
        host = "mettel.velocloud.net"

        edge_from_bruin_1_with_config = {
            'edge': {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': "VCO191919",
            'bruin_client_info': {"client_id": 1991, "client_name": "Tet Corporation"},
            'links_configuration':
                {
                    'interfaces': ['GE1'],
                    'internal_id': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'mode': 'PUBLIC',
                    'type': 'WIRED',
                    'last_active': '2020-09-29T04:45:15.000Z'
                }
        }
        edge_from_bruin_2_with_config = {
            'edge': {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1920},
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': "VCO191919",
            'bruin_client_info': {"client_id": 1991, "client_name": "Tet Corporation"},
            'links_configuration':
                {
                    'interfaces': ['GE2'],
                    'internal_id': '00000001-ac48-47a0-81a7-80c8c320f485',
                    'mode': 'PUBLIC',
                    'type': 'WIRED',
                    'last_active': '2020-09-29T04:45:15.000Z'
                }
        }
        edge_list = [{"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
                     {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1991}]
        stored_cache = [edge_from_bruin_1_with_config, edge_from_bruin_2_with_config]
        new_cache = [edge_from_bruin_1_with_config]
        crossed_cache = [edge_from_bruin_1_with_config, edge_from_bruin_2_with_config]
        final_cache = [edge_from_bruin_1_with_config]

        instance_refresh_cache._filter_edge_list = CoroutineMock(side_effect=[
            edge_from_bruin_1_with_config,
            None,
        ])
        instance_refresh_cache._invalid_edges = {
            host: [
                EdgeIdentifier(**edge_from_bruin_2_with_config['edge'])
            ]
        }
        send_email_res = {"request_id": "asjkdhaskj8", "status": 200}
        instance_refresh_cache._event_bus.rpc_request = CoroutineMock(return_value=send_email_res)
        instance_refresh_cache._storage_repository.get_cache = Mock(return_value=stored_cache)
        instance_refresh_cache._cross_stored_cache_and_new_cache = Mock(return_value=crossed_cache)
        instance_refresh_cache._storage_repository.set_cache = Mock()
        instance_refresh_cache._velocloud_repository.add_edge_config = CoroutineMock(
            side_effect=[edge_from_bruin_1_with_config, edge_from_bruin_2_with_config])

        await instance_refresh_cache._partial_refresh_cache(host, edge_list)

        instance_refresh_cache._filter_edge_list.assert_awaited()
        instance_refresh_cache._cross_stored_cache_and_new_cache.assert_called_once_with(
            stored_cache=stored_cache, new_cache=new_cache
        )
        instance_refresh_cache._storage_repository.set_cache.assert_called_once_with(host, final_cache)

    @pytest.mark.asyncio
    async def partial_refresh_cache_with_no_edges_test(self, instance_refresh_cache, instance_err_msg_refresh_cache):
        # Scenario: Bruin is having issues, no management status can be retrieved for any edge in a host
        edge_from_bruin = None
        edge_list = [{"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
                     {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1991}]
        instance_err_msg_refresh_cache['request_id'] = uuid_

        instance_refresh_cache._event_bus.rpc_request = CoroutineMock()
        instance_refresh_cache._filter_edge_list = CoroutineMock(return_value=edge_from_bruin)
        instance_refresh_cache._storage_repository.get_cache = Mock()
        instance_refresh_cache._cross_stored_cache_and_new_cache = Mock()
        instance_refresh_cache._storage_repository.set_cache = Mock()

        await instance_refresh_cache._partial_refresh_cache("mettel.velocloud.net", edge_list)

        instance_refresh_cache._filter_edge_list.assert_awaited()
        instance_refresh_cache._cross_stored_cache_and_new_cache.assert_not_called()
        instance_refresh_cache._storage_repository.set_cache.assert_not_called()
        instance_refresh_cache._event_bus.rpc_request.assert_awaited_once()

    def cross_stored_cache_and_new_cache_with_both_caches_empty_test(self):
        stored_cache = []
        new_cache = []

        result = RefreshCache._cross_stored_cache_and_new_cache(stored_cache=stored_cache, new_cache=new_cache)
        assert result == []

    def cross_stored_cache_and_new_cache_with_empty_stored_cache_test(self):
        stored_cache = []

        device_info_1 = {
            'edge': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 19,
                "edge_id": 1919
            },
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': "VC1919191",
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }
        device_info_2 = {
            'edge': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 20,
                "edge_id": 2020
            },
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "9567-dh87-teg4-i75k",
            'serial_number': "VC1919192",
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }
        new_cache = [
            device_info_1,
            device_info_2,
        ]

        result = RefreshCache._cross_stored_cache_and_new_cache(stored_cache=stored_cache, new_cache=new_cache)
        assert result == new_cache

    def cross_stored_cache_and_new_cache_with_empty_new_cache_test(self):
        device_info_1 = {
            'edge': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 19,
                "edge_id": 1919
            },
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': "VC1919191",
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }
        device_info_2 = {
            'edge': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 20,
                "edge_id": 2020
            },
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "9567-dh87-teg4-i75k",
            'serial_number': "VC1919192",
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }
        stored_cache = [
            device_info_1,
            device_info_2,
        ]

        new_cache = []

        result = RefreshCache._cross_stored_cache_and_new_cache(stored_cache=stored_cache, new_cache=new_cache)
        assert result == stored_cache

    def cross_stored_cache_and_new_cache_with_no_common_devices_in_both_caches_test(self):
        device_info_1 = {
            'edge': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 19,
                "edge_id": 1919
            },
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': "VC1919191",
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }
        device_info_2 = {
            'edge': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 20,
                "edge_id": 2020
            },
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "9567-dh87-teg4-i75k",
            'serial_number': "VC1919192",
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }

        stored_cache = [
            device_info_1,
        ]
        new_cache = [
            device_info_2,
        ]

        result = RefreshCache._cross_stored_cache_and_new_cache(stored_cache=stored_cache, new_cache=new_cache)
        expected = [
            device_info_1,
            device_info_2,
        ]
        assert result == expected

    def cross_stored_cache_and_new_cache_with_common_devices_in_both_caches_test(self):
        edge_full_id_1 = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 19,
            "edge_id": 1919,
        }
        edge_full_id_2 = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 20,
            "edge_id": 2020,
        }
        edge_full_id_3 = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 21,
            "edge_id": 2121,
        }

        serial_number_1 = 'VC1919191'
        serial_number_2 = 'VC1919192'
        serial_number_3 = 'VC1919193'

        device_info_1_stored_cache = {
            'edge': edge_full_id_1,
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': serial_number_1,
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }
        device_info_1_new_cache = {
            'edge': edge_full_id_1,
            'last_contact': "2021-03-05 12:35:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': serial_number_1,
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }
        device_info_2 = {
            'edge': edge_full_id_2,
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "9567-dh87-teg4-i75k",
            'serial_number': serial_number_2,
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }
        device_info_3_stored_cache = {
            'edge': edge_full_id_3,
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "0678-ei98-ufh5-j86l",
            'serial_number': serial_number_3,
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }
        device_info_3_new_cache = {
            'edge': edge_full_id_3,
            'last_contact': "2021-03-05 12:35:00",
            'logical_ids': "0678-ei98-ufh5-j86l",
            'serial_number': serial_number_3,
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }

        stored_cache = [
            device_info_1_stored_cache,
            device_info_2,
            device_info_3_stored_cache,
        ]
        new_cache = [
            device_info_1_new_cache,
            device_info_2,
            device_info_3_new_cache,
        ]

        result = RefreshCache._cross_stored_cache_and_new_cache(stored_cache=stored_cache, new_cache=new_cache)
        expected = [
            device_info_1_new_cache,
            device_info_2,
            device_info_3_new_cache,
        ]
        assert result == expected

    def cross_stored_cache_and_new_cache_with_common_devices_in_both_caches_and_some_devices_only_in_one_cache_test(
            self):
        edge_full_id_1 = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 19,
            "edge_id": 1919,
        }
        edge_full_id_2 = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 20,
            "edge_id": 2020,
        }
        edge_full_id_3 = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 21,
            "edge_id": 2121,
        }
        edge_full_id_4 = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 22,
            "edge_id": 2222,
        }
        edge_full_id_5 = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 23,
            "edge_id": 2323,
        }

        serial_number_1 = 'VC1919191'
        serial_number_2 = 'VC1919192'
        serial_number_3 = 'VC1919193'
        serial_number_4 = 'VC1919194'
        serial_number_5 = 'VC1919195'

        device_info_1 = {
            'edge': edge_full_id_1,
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': serial_number_1,
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }
        device_info_2 = {
            'edge': edge_full_id_2,
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "9567-dh87-teg4-i75k",
            'serial_number': serial_number_2,
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }
        device_info_3_stored_cache = {
            'edge': edge_full_id_3,
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "0678-ei98-ufh5-j86l",
            'serial_number': serial_number_3,
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }
        device_info_3_new_cache = {
            'edge': edge_full_id_3,
            'last_contact': "2021-03-05 12:35:00",
            'logical_ids': "0678-ei98-ufh5-j86l",
            'serial_number': serial_number_3,
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }
        device_info_4 = {
            'edge': edge_full_id_4,
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "1789-hj09-vgi6-k97m",
            'serial_number': serial_number_4,
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }
        device_info_5 = {
            'edge': edge_full_id_5,
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "2890-ik10-whj7-l08n",
            'serial_number': serial_number_5,
            'bruin_client_info': {
                "client_id": 1991,
                "client_name": "Sarif Industries",
            }
        }

        stored_cache = [
            device_info_1,
            device_info_2,
            device_info_3_stored_cache,
            device_info_4,
        ]
        new_cache = [
            device_info_3_new_cache,
            device_info_4,
            device_info_5,
        ]

        result = RefreshCache._cross_stored_cache_and_new_cache(stored_cache=stored_cache, new_cache=new_cache)
        expected = [
            device_info_1,
            device_info_2,
            device_info_3_new_cache,
            device_info_4,
            device_info_5,
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def filter_edge_list_ok_test(self, instance_refresh_cache,
                                       instance_cache_edges, instance_edges_refresh_cache):
        last_contact = str(datetime.now())
        bruin_client_info = {'client_id': 'some client info'}
        instance_edges_refresh_cache[0]['last_contact'] = last_contact
        instance_edges_refresh_cache[0]['serial_number'] = 'VC01'
        instance_cache_edges[0]['edge']['host'] = 'metvco02.mettel.net'
        instance_cache_edges[0]['last_contact'] = last_contact
        instance_edges_refresh_cache[0]['bruin_client_info'] = bruin_client_info
        links_configuration = [
            {
                'interfaces': ['GE1'],
                'internal_id': '00000001-ac48-47a0-81a7-80c8c320f486',
                'mode': 'PUBLIC',
                'type': 'WIRED',
                'last_active': '2020-09-29T04:45:15.000Z'
            }
        ]
        instance_edges_refresh_cache[0]['links_configuration'] = links_configuration
        instance_cache_edges[0]['links_configuration'] = links_configuration

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': bruin_client_info, 'status': 200})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 200})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=True)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._filter_edge_list(instance_edges_refresh_cache[0])

        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_called()

        assert cache_return == instance_cache_edges[0]
        assert instance_refresh_cache._invalid_edges == {}

    @pytest.mark.asyncio
    async def filter_edge_list_exception_test(self, instance_refresh_cache, instance_edges_refresh_cache):
        last_contact = str(datetime.now())
        instance_edges_refresh_cache[0]['last_contact'] = last_contact
        instance_edges_refresh_cache[0]['edgeLastContact'] = last_contact
        instance_edges_refresh_cache[0]['edgeSerialNumber'] = 'VC01'

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': None, 'status': 200})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 200})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=True)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._filter_edge_list(instance_edges_refresh_cache[0])
        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_not_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_not_called()

        instance_refresh_cache._logger.error.assert_called_once()

        assert cache_return is None
        assert instance_refresh_cache._invalid_edges == {}

    @pytest.mark.asyncio
    async def filter_edge_list_no_client_info_test(self, instance_refresh_cache, instance_edges_refresh_cache):
        last_contact = str(datetime.now())

        instance_edges_refresh_cache[0]['last_contact'] = last_contact
        instance_edges_refresh_cache[0]['edgeLastContact'] = last_contact
        instance_edges_refresh_cache[0]['edgeSerialNumber'] = 'VC01'

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': {}, 'status': 200})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 200})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=True)
        instance_refresh_cache._storage_repository.set_cache = Mock()
        instance_refresh_cache._invalid_edges = {
            instance_edges_refresh_cache[0]['edge']['host']: []
        }

        cache_return = await instance_refresh_cache._filter_edge_list(instance_edges_refresh_cache[0])
        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_not_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_not_called()

        assert cache_return is None
        assert instance_refresh_cache._invalid_edges == {
            instance_edges_refresh_cache[0]['edge']['host']: [
                EdgeIdentifier(**instance_edges_refresh_cache[0]['edge'])
            ]
        }

    @pytest.mark.asyncio
    async def filter_edge_list_client_info_status_non_2XX_test(self, instance_refresh_cache,
                                                               instance_edges_refresh_cache):
        last_contact = str(datetime.now())

        instance_edges_refresh_cache[0]['last_contact'] = last_contact
        instance_edges_refresh_cache[0]['edgeLastContact'] = last_contact
        instance_edges_refresh_cache[0]['edgeSerialNumber'] = 'VC01'

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': {'client_id': 'some client info'}, 'status': 400})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 200})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=True)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._filter_edge_list(instance_edges_refresh_cache[0])
        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_not_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_not_called()

        assert cache_return is None
        assert instance_refresh_cache._invalid_edges == {}

    @pytest.mark.asyncio
    async def filter_edge_list_no_management_status_test(self, instance_refresh_cache, instance_edges_refresh_cache):
        last_contact = str(datetime.now())

        instance_edges_refresh_cache[0]['last_contact'] = last_contact
        instance_edges_refresh_cache[0]['edgeLastContact'] = last_contact
        instance_edges_refresh_cache[0]['edgeSerialNumber'] = 'VC01'

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': {'client_id': 'some client info'}, 'status': 200})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 400})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=True)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._filter_edge_list(instance_edges_refresh_cache[0])
        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_not_called()

        assert cache_return is None
        assert instance_refresh_cache._invalid_edges == {}

    @pytest.mark.asyncio
    async def filter_edge_list_unactive_management_status_test(self, instance_refresh_cache,
                                                               instance_edges_refresh_cache):
        last_contact = str(datetime.now())

        instance_edges_refresh_cache[0]['last_contact'] = last_contact
        instance_edges_refresh_cache[0]['edgeLastContact'] = last_contact
        instance_edges_refresh_cache[0]['edgeSerialNumber'] = 'VC01'

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': {'client_id': 'some client info'}, 'status': 200})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 200})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=False)
        instance_refresh_cache._storage_repository.set_cache = Mock()
        instance_refresh_cache._invalid_edges = {
            instance_edges_refresh_cache[0]['edge']['host']: []
        }

        cache_return = await instance_refresh_cache._filter_edge_list(instance_edges_refresh_cache[0])
        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_called()

        assert cache_return is None
        assert instance_refresh_cache._invalid_edges == {
            instance_edges_refresh_cache[0]['edge']['host']: [
                EdgeIdentifier(**instance_edges_refresh_cache[0]['edge'])
            ]
        }
