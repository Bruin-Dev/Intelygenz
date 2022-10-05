from unittest.mock import AsyncMock

correct_response = {
    "status": 200,
    "body": {"result": [{"id": 1}, {"id": 2}]},
}
bad_status = {"status": 500}
network_id = 1


async def get_networks_return_not_none_test(forticloud_instance):
    forticloud_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_networks = await forticloud_instance.get_networks()
    assert response_get_networks is not None


async def get_networks_return_list_test(forticloud_instance):
    forticloud_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_networks = await forticloud_instance.get_networks()
    assert type(response_get_networks) is list


async def get_networks_return_not_empty_list_test(forticloud_instance):
    forticloud_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_networks = await forticloud_instance.get_networks()
    assert len(response_get_networks) > 0


async def get_networks_return_empty_list_with_bad_status_test(forticloud_instance):
    forticloud_instance.forticloud_client.get_response_device = AsyncMock(return_value=bad_status)
    response_get_networks = await forticloud_instance.get_networks()
    assert len(response_get_networks) == 0


async def get_switches_return_not_none_test(forticloud_instance):
    forticloud_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_switches = await forticloud_instance.get_switches(network_id)
    assert response_get_switches is not None


async def get_switches_return_list_test(forticloud_instance):
    forticloud_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_switches = await forticloud_instance.get_switches(network_id)
    assert type(response_get_switches) is list


async def get_switches_return_not_empty_list_test(forticloud_instance):
    forticloud_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_switches = await forticloud_instance.get_switches(network_id)
    assert len(response_get_switches) > 0


async def get_switches_return_empty_list_with_bad_status_test(forticloud_instance):
    forticloud_instance.forticloud_client.get_response_device = AsyncMock(return_value=bad_status)
    response_get_switches = await forticloud_instance.get_switches(network_id)
    assert len(response_get_switches) == 0


async def get_access_points_return_not_none_test(forticloud_instance):
    forticloud_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_access_points = await forticloud_instance.get_access_points(network_id)
    assert response_get_access_points is not None


async def get_access_points_return_list_test(forticloud_instance):
    forticloud_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_access_points = await forticloud_instance.get_access_points(network_id)
    assert type(response_get_access_points) is list


async def get_access_points_return_not_empty_list_test(forticloud_instance):
    forticloud_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_access_points = await forticloud_instance.get_access_points(network_id)
    assert len(response_get_access_points) > 0


async def get_access_points_return_empty_list_with_bad_status_test(forticloud_instance):
    forticloud_instance.forticloud_client.get_response_device = AsyncMock(return_value=bad_status)
    response_get_access_points = await forticloud_instance.get_access_points(network_id)
    assert len(response_get_access_points) == 0
