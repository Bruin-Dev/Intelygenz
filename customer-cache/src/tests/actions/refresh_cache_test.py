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

        refresh_cache = RefreshCache(config, event_bus, logger, scheduler, storage_repository,
                                     bruin_repository, velocloud_repository)

        assert refresh_cache._config == config
        assert refresh_cache._event_bus == event_bus
        assert refresh_cache._logger == logger
        assert refresh_cache._scheduler == scheduler
        assert refresh_cache._storage_repository == storage_repository
        assert refresh_cache._velocloud_repository == velocloud_repository
        assert refresh_cache._bruin_repository == bruin_repository

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
    async def refresh_cache_edge_list_failed_test(self, instance_refresh_cache, instance_err_msg_refresh_cache):
        error = "Couldn't find any edge to refresh the cache"
        instance_err_msg_refresh_cache['request_id'] = uuid_
        instance_err_msg_refresh_cache[
            'message'] = f"Maximum retries happened while while refreshing the cache cause of error was {error}"
        instance_refresh_cache._event_bus.rpc_request = CoroutineMock()

        instance_refresh_cache._logger.error = Mock()
        instance_refresh_cache._velocloud_repository.get_all_velo_edges = CoroutineMock(return_value=None)

        instance_refresh_cache._partial_refresh_cache = CoroutineMock()

        tenacity_retry_mock = patch.object(refresh_cache_module, 'retry', side_effect=retry_mock(attempts=1))
        with uuid_mock, tenacity_retry_mock:
            await instance_refresh_cache._refresh_cache()

        instance_refresh_cache._partial_refresh_cache.assert_not_awaited()
        instance_refresh_cache._event_bus.rpc_request.assert_awaited_once_with("notification.slack.request",
                                                                               instance_err_msg_refresh_cache,
                                                                               timeout=10)

    @pytest.mark.asyncio
    async def refresh_cache_edge_list_failed_with_several_consecutive_failures_test(self, instance_refresh_cache,
                                                                                    instance_err_msg_refresh_cache):
        instance_err_msg_refresh_cache['request_id'] = uuid_
        instance_refresh_cache._event_bus.rpc_request = CoroutineMock()

        instance_refresh_cache._logger.error = Mock()

        instance_refresh_cache._velocloud_repository.get_all_velo_edges = CoroutineMock(return_value=None)

        instance_refresh_cache._partial_refresh_cache = CoroutineMock()

        retry_mock_fn = retry_mock(attempts=instance_refresh_cache._config.REFRESH_CONFIG['attempts_threshold'])
        tenacity_retry_mock = patch.object(refresh_cache_module, 'retry', side_effect=retry_mock_fn)
        with uuid_mock, tenacity_retry_mock:
            await instance_refresh_cache._refresh_cache()

        instance_refresh_cache._partial_refresh_cache.assert_not_awaited()
        instance_refresh_cache._event_bus.rpc_request.assert_any_await("notification.slack.request",
                                                                       instance_err_msg_refresh_cache,
                                                                       timeout=10)

    @pytest.mark.asyncio
    async def partial_refresh_cache_with_edges_test(self, instance_refresh_cache, instance_err_msg_refresh_cache):
        # Scenario: Bruin returns all(or most) management statuses correctly
        edge_from_bruin = {
            'edge': {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': "VCO191919",
            'bruin_client_info': {"client_id": 1991, "client_name": "Tet Corporation"}
        }
        edge_list = [{"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
                     {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1991}]
        instance_refresh_cache._bruin_repository.filter_edge_list = CoroutineMock(return_value=edge_from_bruin)
        instance_refresh_cache._storage_repository.set_cache = Mock()
        await instance_refresh_cache._partial_refresh_cache("mettel.velocloud.net", edge_list)
        instance_refresh_cache._bruin_repository.filter_edge_list.assert_awaited()
        instance_refresh_cache._storage_repository.set_cache.assert_called_once()

    @pytest.mark.asyncio
    async def partial_refresh_cache_with_no_edges_test(self, instance_refresh_cache, instance_err_msg_refresh_cache):
        # Scenario: Bruin is having issues, no management status can be retrieved for any edge in a host
        edge_from_bruin = None
        edge_list = [{"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
                     {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1991}]
        instance_err_msg_refresh_cache['request_id'] = uuid_
        instance_refresh_cache._event_bus.rpc_request = CoroutineMock()
        instance_refresh_cache._bruin_repository.filter_edge_list = CoroutineMock(return_value=edge_from_bruin)
        instance_refresh_cache._storage_repository.set_cache = Mock()
        await instance_refresh_cache._partial_refresh_cache("mettel.velocloud.net", edge_list)
        instance_refresh_cache._bruin_repository.filter_edge_list.assert_awaited()
        instance_refresh_cache._storage_repository.set_cache.assert_not_called()
        instance_refresh_cache._event_bus.rpc_request.assert_awaited_once()
