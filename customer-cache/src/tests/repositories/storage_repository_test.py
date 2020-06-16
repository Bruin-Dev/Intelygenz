import json
import pytest
from unittest.mock import Mock
from asynctest import CoroutineMock
from datetime import datetime

from application.repositories.storage_repository import StorageRepository

from config import testconfig


class TestStorageRepository:

    def instance_test(self):
        config = testconfig
        logger = Mock()
        redis = Mock()
        bruin_repository = Mock()

        storage_repo = StorageRepository(config, logger, redis)

        assert storage_repo._config == config
        assert storage_repo._logger == logger
        assert storage_repo._redis == redis

    def get_cache_key_exist_test(self, instance_storage_repository):
        redis_key = "VCO1"
        redis_cache = ["Edge list"]

        instance_storage_repository._redis.exists = Mock(return_value=True)
        instance_storage_repository._redis.get = Mock(return_value=json.dumps(redis_cache))

        cache = instance_storage_repository.get_cache(redis_key)

        assert cache == redis_cache

    def get_cache_key_doesnt_exist_test(self, instance_storage_repository):
        redis_key = "VCO1"
        redis_cache = ["Edge list"]

        instance_storage_repository._redis.exists = Mock(return_value=False)
        instance_storage_repository._redis.get = Mock(return_value=json.dumps(redis_cache))

        cache = instance_storage_repository.get_cache(redis_key)

        assert cache == []

    def set_cache_test(self, instance_storage_repository):
        redis_key = "VCO1"
        redis_cache = ["Edge list"]

        instance_storage_repository._redis.set = Mock()

        instance_storage_repository.set_cache(redis_key, redis_cache)

        instance_storage_repository._redis.set.assert_called_with(redis_key, json.dumps(redis_cache))

    @pytest.mark.asyncio
    async def partial_refresh_cache_test(self, instance_refresh_cache, instance_edges_refresh_cache,
                                         instance_cache_edges):
        host = 'metvco02.mettel.net'
        instance_edges_refresh_cache = [instance_edges_refresh_cache[0]]

        instance_refresh_cache._storage_repository.set_cache = Mock()

        instance_refresh_cache._bruin_repository.filter_edge_list = CoroutineMock(
            return_value=instance_cache_edges[0])

        await instance_refresh_cache._partial_refresh_cache(host, instance_edges_refresh_cache)
        instance_refresh_cache._bruin_repository.filter_edge_list.assert_awaited()
        instance_refresh_cache._storage_repository.set_cache.assert_called_once_with(host, [
            instance_cache_edges[0]])

    @pytest.mark.asyncio
    async def filter_edge_list_ok_test(self, instance_refresh_cache, instance_edges_refresh_cache,
                                       instance_cache_edges):
        last_contact = str(datetime.now())
        bruin_client_info = {'client_id': 'some client info'}
        instance_edges_refresh_cache[0]['last_contact'] = last_contact
        instance_cache_edges[0]['edge']['host'] = 'metvco02.mettel.net'
        instance_cache_edges[0]['last_contact'] = last_contact
        instance_cache_edges[0]['bruin_client_info'] = bruin_client_info
        instance_edges_refresh_cache[0]['bruin_client_info'] = bruin_client_info

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': bruin_client_info, 'status': 200})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 200})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=True)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._bruin_repository.filter_edge_list(
            instance_edges_refresh_cache[0])

        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_called()

        assert cache_return == instance_cache_edges[0]

    @pytest.mark.asyncio
    async def filter_edge_list_exception_test(self, instance_refresh_cache, instance_edges_refresh_cache):
        last_contact = str(datetime.now())
        instance_edges_refresh_cache[0]['last_contact'] = last_contact

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': None, 'status': 200})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 200})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=True)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._bruin_repository.filter_edge_list(
            instance_edges_refresh_cache[0])
        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_not_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_not_called()

        instance_refresh_cache._logger.error.assert_called_once()

        assert cache_return is None

    @pytest.mark.asyncio
    async def filter_edge_list_no_client_info_test(self, instance_refresh_cache, instance_edges_refresh_cache):
        last_contact = str(datetime.now())

        instance_edges_refresh_cache[0]['last_contact'] = last_contact

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': {}, 'status': 200})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 200})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=True)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._bruin_repository.filter_edge_list(
            instance_edges_refresh_cache[0])
        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_not_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_not_called()

        assert cache_return is None

    @pytest.mark.asyncio
    async def filter_edge_list_client_info_status_non_2XX_test(self, instance_refresh_cache,
                                                               instance_edges_refresh_cache):
        last_contact = str(datetime.now())

        instance_edges_refresh_cache[0]['last_contact'] = last_contact

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': {'client_id': 'some client info'}, 'status': 400})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 200})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=True)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._bruin_repository.filter_edge_list(
            instance_edges_refresh_cache[0])
        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_not_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_not_called()

        assert cache_return is None

    @pytest.mark.asyncio
    async def filter_edge_list_no_management_status_test(self, instance_refresh_cache, instance_edges_refresh_cache):
        last_contact = str(datetime.now())

        instance_edges_refresh_cache[0]['last_contact'] = last_contact

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': {'client_id': 'some client info'}, 'status': 200})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 400})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=True)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._bruin_repository.filter_edge_list(
            instance_edges_refresh_cache[0])
        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_not_called()

        assert cache_return is None

    @pytest.mark.asyncio
    async def filter_edge_list_unactive_management_status_test(self, instance_refresh_cache,
                                                               instance_edges_refresh_cache):
        last_contact = str(datetime.now())

        instance_edges_refresh_cache[0]['last_contact'] = last_contact

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': {'client_id': 'some client info'}, 'status': 200})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 200})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=False)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._bruin_repository.filter_edge_list(
            instance_edges_refresh_cache[0])
        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_called()

        assert cache_return is None
