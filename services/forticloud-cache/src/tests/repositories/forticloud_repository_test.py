from unittest.mock import AsyncMock

mock_network_example_1 = {"oid": 1, "name": "network_1"}
mock_network_example_2 = {"oid": 2, "name": "network_2"}
mock_list_of_networks = [mock_network_example_1, mock_network_example_2]
mock_id_networks_list = [1, 2, 3, 4]
mock_switch_1 = {"network": 1, "sn": "serial_number_test_1", "status": "offline"}
mock_switch_2 = {"network": 2, "sn": "serial_number_test_2", "status": "online"}
mock_list_of_switches = [mock_switch_1, mock_switch_2]
mock_access_point_1 = {"connection_state": "connected", "serial": "sn_2"}
mock_access_point_2 = {"connection_state": "disconnected", "serial": "sn_1"}
mock_list_of_access_point = [mock_access_point_1, mock_access_point_2]


async def get_list_networks_ids_return_not_none_test(forticloud_repository_instance):
    forticloud_repository_instance.forticloud_client.get_networks = AsyncMock(return_value=mock_list_of_networks)
    list_networks_ids = await forticloud_repository_instance.get_list_networks_ids()
    assert list_networks_ids is not None


async def get_list_networks_ids_return_empty_list_if_not_found_networks_test(forticloud_repository_instance):
    forticloud_repository_instance.forticloud_client.get_networks = AsyncMock(return_value=[])
    list_networks_ids = await forticloud_repository_instance.get_list_networks_ids()
    assert list_networks_ids == []


async def get_list_networks_ids_return_a_list_test(forticloud_repository_instance):
    forticloud_repository_instance.forticloud_client.get_networks = AsyncMock(return_value=mock_list_of_networks)
    list_networks_ids = await forticloud_repository_instance.get_list_networks_ids()
    assert type(list_networks_ids) is list


async def get_list_networks_ids_return_a_list_with_some_items_test(forticloud_repository_instance):
    forticloud_repository_instance.forticloud_client.get_networks = AsyncMock(return_value=mock_list_of_networks)
    list_networks_ids = await forticloud_repository_instance.get_list_networks_ids()
    assert len(list_networks_ids) > 0


async def get_list_switches_return_not_none_test(forticloud_repository_instance):
    forticloud_repository_instance.forticloud_client.get_switches = AsyncMock(return_value=mock_list_of_switches)
    list_of_switches = await forticloud_repository_instance.get_list_switches(mock_id_networks_list)
    assert list_of_switches is not None


async def get_list_switches_return_a_list_test(forticloud_repository_instance):
    forticloud_repository_instance.forticloud_client.get_switches = AsyncMock(return_value=mock_list_of_switches)
    list_of_switches = await forticloud_repository_instance.get_list_switches(mock_id_networks_list)
    assert type(list_of_switches) is list


async def get_list_switches_return_a_list_with_some_items_test(forticloud_repository_instance):
    forticloud_repository_instance.forticloud_client.get_switches = AsyncMock(return_value=mock_list_of_switches)
    list_of_switches = await forticloud_repository_instance.get_list_switches(mock_id_networks_list)
    assert len(list_of_switches) > 0


async def get_list_access_point_return_not_none_test(forticloud_repository_instance):
    forticloud_repository_instance.forticloud_client.get_access_points = AsyncMock(
        return_value=mock_list_of_access_point
    )
    list_of_access_points = await forticloud_repository_instance.get_list_access_point(mock_id_networks_list)
    assert list_of_access_points is not None


async def get_list_access_point_return_a_list_test(forticloud_repository_instance):
    forticloud_repository_instance.forticloud_client.get_access_points = AsyncMock(
        return_value=mock_list_of_access_point
    )
    list_of_access_points = await forticloud_repository_instance.get_list_access_point(mock_id_networks_list)
    assert type(list_of_access_points) is list


async def get_list_access_point_return_a_list_with_some_items_test(forticloud_repository_instance):
    forticloud_repository_instance.forticloud_client.get_access_points = AsyncMock(
        return_value=mock_list_of_access_point
    )
    list_of_access_points = await forticloud_repository_instance.get_list_access_point(mock_id_networks_list)
    assert len(list_of_access_points) > 0
