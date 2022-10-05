from unittest.mock import AsyncMock, Mock

import pytest

from application.repositories.cache_repository import CacheRepository
from config import testconfig

ID_NETWORKS_LIST = [1, 2, 3, 4]
LIST_OF_SWITCHES = [{"serial_number": "serial_number_test", "client_id": 1}]
LIST_OF_ACCESS_POINTS = [{"serial_number": "serial_number_test", "client_id": 1}]
MANAGEMENT_STATUS = "test"
BAD_MANAGEMENT_STATUS = "fake_management"


@pytest.fixture(scope="function")
def cache_repository_instance():
    cache_repository_instance = CacheRepository(
        config=testconfig,
        scheduler=Mock(),
        redis_repository=Mock(),
        forticloud_repository=Mock(),
        bruin_repository=Mock(),
    )
    cache_repository_instance.forticloud_repository = AsyncMock()
    cache_repository_instance.forticloud_repository.get_list_networks_ids = AsyncMock(return_value=ID_NETWORKS_LIST)
    cache_repository_instance.get_switches = AsyncMock(return_value=LIST_OF_SWITCHES)
    cache_repository_instance.get_access_points = AsyncMock(return_value=LIST_OF_ACCESS_POINTS)
    cache_repository_instance.add_list_access_points_to_cache = AsyncMock()
    cache_repository_instance.add_list_switches_to_cache = AsyncMock()
    cache_repository_instance.add_serial_client_id_to_device = AsyncMock()
    return cache_repository_instance


@pytest.fixture(scope="function")
def cache_repository_instance_basic():
    cache_repository_instance = CacheRepository(
        config=testconfig,
        scheduler=Mock(),
        redis_repository=Mock(),
        forticloud_repository=Mock(),
        bruin_repository=Mock(),
    )
    cache_repository_instance.forticloud_repository = AsyncMock()
    cache_repository_instance_basic.redis_repository = AsyncMock()
    return cache_repository_instance


async def add_job_to_refresh_cache_return_none_test(cache_repository_instance):
    result = await cache_repository_instance.add_job_to_refresh_cache()
    assert result is None


async def add_job_to_refresh_cache_add_job_to_schedule_test(cache_repository_instance):
    await cache_repository_instance.add_job_to_refresh_cache()
    cache_repository_instance.scheduler.add_job.assert_called()


async def refresh_cache_not_return_nothing_test(cache_repository_instance):
    result_refresh_cache = await cache_repository_instance.refresh_cache()
    assert result_refresh_cache is None


async def refresh_cache_call_get_networks_ids_test(cache_repository_instance):
    await cache_repository_instance.refresh_cache()
    cache_repository_instance.forticloud_repository.get_list_networks_ids.assert_called()


async def refresh_cache_call_get_switches_test(cache_repository_instance):
    await cache_repository_instance.refresh_cache()
    cache_repository_instance.get_switches.assert_called()


async def refresh_cache_call_get_access_points_test(cache_repository_instance):
    await cache_repository_instance.refresh_cache()
    cache_repository_instance.get_access_points.assert_called()


async def refresh_cache_call_add_switches_to_cache_test(cache_repository_instance):
    await cache_repository_instance.refresh_cache()
    cache_repository_instance.add_list_switches_to_cache.assert_called()


async def refresh_cache_call_add_access_points_to_cache_test(cache_repository_instance):
    await cache_repository_instance.refresh_cache()
    cache_repository_instance.add_list_access_points_to_cache.assert_called()


async def get_access_points_return_not_none_test(cache_repository_instance_basic):
    cache_repository_instance_basic.forticloud_repository.get_list_access_point = AsyncMock(
        return_value=LIST_OF_ACCESS_POINTS
    )
    cache_repository_instance_basic.add_serial_client_id_to_device = AsyncMock(return_value=LIST_OF_ACCESS_POINTS)
    cache_repository_instance_basic.get_devices_with_valid_management_status = AsyncMock(
        return_value=LIST_OF_ACCESS_POINTS
    )
    access_points = await cache_repository_instance_basic.get_access_points(ID_NETWORKS_LIST)
    assert access_points is not None


async def get_access_points_return_list_test(cache_repository_instance_basic):
    cache_repository_instance_basic.forticloud_repository.get_list_access_point = AsyncMock(
        return_value=LIST_OF_ACCESS_POINTS
    )
    cache_repository_instance_basic.add_serial_client_id_to_device = AsyncMock(return_value=LIST_OF_ACCESS_POINTS)
    cache_repository_instance_basic.get_devices_with_valid_management_status = AsyncMock(
        return_value=LIST_OF_ACCESS_POINTS
    )
    access_points = await cache_repository_instance_basic.get_access_points(ID_NETWORKS_LIST)
    assert type(access_points) is list


async def get_access_points_return_not_empty_list_test(cache_repository_instance_basic):
    cache_repository_instance_basic.forticloud_repository.get_list_access_point = AsyncMock(
        return_value=LIST_OF_ACCESS_POINTS
    )
    cache_repository_instance_basic.add_serial_client_id_to_device = AsyncMock(return_value=LIST_OF_ACCESS_POINTS)
    cache_repository_instance_basic.get_devices_with_valid_management_status = AsyncMock(
        return_value=LIST_OF_ACCESS_POINTS
    )
    access_points = await cache_repository_instance_basic.get_access_points(ID_NETWORKS_LIST)
    assert len(access_points) > 0


async def get_access_points_call_get_list_access_points_test(cache_repository_instance_basic):
    cache_repository_instance_basic.forticloud_repository.get_list_access_point = AsyncMock(
        return_value=LIST_OF_ACCESS_POINTS
    )
    cache_repository_instance_basic.add_serial_client_id_to_device = AsyncMock(return_value=LIST_OF_ACCESS_POINTS)
    cache_repository_instance_basic.get_devices_with_valid_management_status = AsyncMock(
        return_value=LIST_OF_ACCESS_POINTS
    )
    await cache_repository_instance_basic.get_access_points(ID_NETWORKS_LIST)
    cache_repository_instance_basic.forticloud_repository.get_list_access_point.assert_called()


async def get_access_points_call_add_serial_client_id_to_device_test(cache_repository_instance_basic):
    cache_repository_instance_basic.forticloud_repository.get_list_access_point = AsyncMock(
        return_value=LIST_OF_ACCESS_POINTS
    )
    cache_repository_instance_basic.add_serial_client_id_to_device = AsyncMock(return_value=LIST_OF_ACCESS_POINTS)
    cache_repository_instance_basic.get_devices_with_valid_management_status = AsyncMock(
        return_value=LIST_OF_ACCESS_POINTS
    )
    await cache_repository_instance_basic.get_access_points(ID_NETWORKS_LIST)
    cache_repository_instance_basic.add_serial_client_id_to_device.assert_called()


async def get_switches_return_not_none_test(cache_repository_instance_basic):
    cache_repository_instance_basic.forticloud_repository.get_list_switches = AsyncMock(return_value=LIST_OF_SWITCHES)
    cache_repository_instance_basic.add_serial_client_id_to_device = AsyncMock(return_value=LIST_OF_SWITCHES)
    cache_repository_instance_basic.get_devices_with_valid_management_status = AsyncMock(return_value=LIST_OF_SWITCHES)
    access_points = await cache_repository_instance_basic.get_switches(ID_NETWORKS_LIST)
    assert access_points is not None


async def get_switches_return_list_test(cache_repository_instance_basic):
    cache_repository_instance_basic.forticloud_repository.get_list_switches = AsyncMock(return_value=LIST_OF_SWITCHES)
    cache_repository_instance_basic.add_serial_client_id_to_device = AsyncMock(return_value=LIST_OF_SWITCHES)
    cache_repository_instance_basic.get_devices_with_valid_management_status = AsyncMock(return_value=LIST_OF_SWITCHES)
    access_points = await cache_repository_instance_basic.get_switches(ID_NETWORKS_LIST)
    assert type(access_points) is list


async def get_switches_return_not_empty_list_test(cache_repository_instance_basic):
    cache_repository_instance_basic.forticloud_repository.get_list_switches = AsyncMock(return_value=LIST_OF_SWITCHES)
    cache_repository_instance_basic.add_serial_client_id_to_device = AsyncMock(return_value=LIST_OF_SWITCHES)
    cache_repository_instance_basic.get_devices_with_valid_management_status = AsyncMock(return_value=LIST_OF_SWITCHES)
    access_points = await cache_repository_instance_basic.get_switches(ID_NETWORKS_LIST)
    assert len(access_points) > 0


async def get_switches_call_get_list_access_points_test(cache_repository_instance_basic):
    cache_repository_instance_basic.forticloud_repository.get_list_switches = AsyncMock(return_value=LIST_OF_SWITCHES)
    cache_repository_instance_basic.add_serial_client_id_to_device = AsyncMock(return_values=LIST_OF_SWITCHES)
    cache_repository_instance_basic.get_devices_with_valid_management_status = AsyncMock(return_value=LIST_OF_SWITCHES)
    await cache_repository_instance_basic.get_switches(ID_NETWORKS_LIST)
    cache_repository_instance_basic.forticloud_repository.get_list_switches.assert_called()


async def get_switches_call_add_serial_client_id_to_device_test(cache_repository_instance_basic):
    cache_repository_instance_basic.forticloud_repository.get_list_switches = AsyncMock(return_value=LIST_OF_SWITCHES)
    cache_repository_instance_basic.add_serial_client_id_to_device = AsyncMock(return_value=LIST_OF_SWITCHES)
    cache_repository_instance_basic.get_devices_with_valid_management_status = AsyncMock(return_value=LIST_OF_SWITCHES)
    await cache_repository_instance_basic.get_switches(ID_NETWORKS_LIST)
    cache_repository_instance_basic.add_serial_client_id_to_device.assert_called()


async def add_list_switches_to_cache_return_none_test(cache_repository_instance_basic):
    cache_repository_instance_basic.redis_repository.set_value_for_key = AsyncMock()
    result_to_add_switches_to_cache = await cache_repository_instance_basic.add_list_switches_to_cache(LIST_OF_SWITCHES)
    assert result_to_add_switches_to_cache is None


async def add_list_switches_to_cache_return_calls_to_set_values_in_redis_test(cache_repository_instance_basic):
    cache_repository_instance_basic.redis_repository.set_value_for_key = AsyncMock()
    await cache_repository_instance_basic.add_list_switches_to_cache(LIST_OF_SWITCHES)
    cache_repository_instance_basic.redis_repository.set_value_for_key.assert_called()


async def add_list_access_point_to_cache_return_calls_to_set_values_in_redis_test(cache_repository_instance_basic):
    cache_repository_instance_basic.redis_repository.set_value_for_key = AsyncMock()
    await cache_repository_instance_basic.add_list_access_points_to_cache(LIST_OF_ACCESS_POINTS)
    cache_repository_instance_basic.redis_repository.set_value_for_key.assert_called()


async def get_list_switches_of_cache_return_not_none_test(cache_repository_instance_basic):
    cache_repository_instance_basic.redis_repository.get_value_if_exist = AsyncMock(return_value=[])
    result_get_list_switches_of_cache = await cache_repository_instance_basic.get_list_switches_of_cache()
    assert result_get_list_switches_of_cache is not None


async def get_list_access_points_of_cache_return_not_none_test(cache_repository_instance_basic):
    cache_repository_instance_basic.redis_repository.get_value_if_exist = AsyncMock(return_value=[])
    result_get_list_access_points_of_cache = await cache_repository_instance_basic.get_list_access_points_of_cache()
    assert result_get_list_access_points_of_cache is not None


async def add_serial_client_id_to_device_return_not_none_test(cache_repository_instance_basic):
    cache_repository_instance_basic.bruin_repository.get_list_of_devices_with_client_id = AsyncMock(
        return_value=LIST_OF_SWITCHES
    )
    devices_with_serial = await cache_repository_instance_basic.add_serial_client_id_to_device(LIST_OF_SWITCHES)
    assert devices_with_serial is not None


async def add_serial_client_id_to_device_return_list_test(cache_repository_instance_basic):
    cache_repository_instance_basic.bruin_repository.get_list_of_devices_with_client_id = AsyncMock(
        return_value=LIST_OF_SWITCHES
    )
    devices_with_serial = await cache_repository_instance_basic.add_serial_client_id_to_device(LIST_OF_SWITCHES)
    assert type(devices_with_serial) is list


async def add_serial_client_id_to_device_return_not_empty_list_test(cache_repository_instance_basic):
    cache_repository_instance_basic.bruin_repository.get_list_of_devices_with_client_id = AsyncMock(
        return_value=LIST_OF_SWITCHES
    )
    devices_with_serial = await cache_repository_instance_basic.add_serial_client_id_to_device(LIST_OF_SWITCHES)
    assert len(devices_with_serial) > 0


async def get_devices_with_valid_management_status_return_not_none_test(cache_repository_instance_basic):
    cache_repository_instance_basic.bruin_repository.get_management_status_for_device = AsyncMock(
        return_value=MANAGEMENT_STATUS
    )
    devices_with_management_status = await cache_repository_instance_basic.get_devices_with_valid_management_status(
        LIST_OF_SWITCHES
    )
    assert devices_with_management_status is not None


async def get_devices_with_valid_management_status_return_list_test(cache_repository_instance_basic):
    cache_repository_instance_basic.bruin_repository.get_management_status_for_device = AsyncMock(
        return_value=MANAGEMENT_STATUS
    )
    devices_with_management_status = await cache_repository_instance_basic.get_devices_with_valid_management_status(
        LIST_OF_SWITCHES
    )
    assert type(devices_with_management_status) is list


async def get_devices_with_valid_management_status_return_not_empty_list_test(cache_repository_instance_basic):
    cache_repository_instance_basic.bruin_repository.get_management_status_for_device = AsyncMock(
        return_value=MANAGEMENT_STATUS
    )
    devices_with_management_status = await cache_repository_instance_basic.get_devices_with_valid_management_status(
        LIST_OF_SWITCHES
    )
    assert len(devices_with_management_status) > 0


async def get_devices_with_valid_management_status_return_empty_list_with_invalid_status_test(
    cache_repository_instance_basic,
):
    cache_repository_instance_basic.bruin_repository.get_management_status_for_device = AsyncMock(
        return_value=BAD_MANAGEMENT_STATUS
    )
    devices_with_management_status = await cache_repository_instance_basic.get_devices_with_valid_management_status(
        LIST_OF_SWITCHES
    )
    assert len(devices_with_management_status) == 0
