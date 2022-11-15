from unittest.mock import AsyncMock

import pytest
from application.repositories.errors import UnexpectedStatusError
from tenacity import stop_after_attempt

correct_response = {
    "status": 200,
    "body": {"result": [{"id": 1}, {"id": 2}]},
}
bad_status = {"status": 500}
network_id = 1


async def get_networks_return_not_none_test(forticloud_client_instance):
    forticloud_client_instance = forticloud_client_instance()
    forticloud_client_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_networks = await forticloud_client_instance.get_networks()
    assert response_get_networks is not None


async def get_networks_return_list_test(forticloud_client_instance):
    forticloud_client_instance = forticloud_client_instance()
    forticloud_client_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_networks = await forticloud_client_instance.get_networks()
    assert type(response_get_networks) is list


async def get_networks_return_not_empty_list_test(forticloud_client_instance):
    forticloud_client_instance = forticloud_client_instance()
    forticloud_client_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_networks = await forticloud_client_instance.get_networks()
    assert len(response_get_networks) > 0


async def get_networks_raises_error_test(forticloud_client_instance):
    forticloud_client_instance = forticloud_client_instance()
    forticloud_client_instance.forticloud_client.get_response_device = AsyncMock(return_value=bad_status)
    with pytest.raises(UnexpectedStatusError):
        await forticloud_client_instance.get_networks()


async def get_switches_return_not_none_test(forticloud_client_instance):
    forticloud_client_instance = forticloud_client_instance()
    forticloud_client_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_switches = await forticloud_client_instance.get_switches(network_id)
    assert response_get_switches is not None


async def get_switches_return_list_test(forticloud_client_instance):
    forticloud_client_instance = forticloud_client_instance()
    forticloud_client_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_switches = await forticloud_client_instance.get_switches(network_id)
    assert type(response_get_switches) is list


async def get_switches_return_not_empty_list_test(forticloud_client_instance):
    forticloud_client_instance = forticloud_client_instance()
    forticloud_client_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_switches = await forticloud_client_instance.get_switches(network_id)
    assert len(response_get_switches) > 0


async def get_switches_raises_error_test(forticloud_client_instance):
    forticloud_client_instance = forticloud_client_instance()
    forticloud_client_instance.forticloud_client.get_response_device = AsyncMock(return_value=bad_status)
    with pytest.raises(UnexpectedStatusError):
        await forticloud_client_instance.get_switches(network_id)


async def get_access_points_return_not_none_test(forticloud_client_instance):
    forticloud_client_instance = forticloud_client_instance()
    forticloud_client_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_access_points = await forticloud_client_instance.get_access_points(network_id)
    assert response_get_access_points is not None


async def get_access_points_return_list_test(forticloud_client_instance):
    forticloud_client_instance = forticloud_client_instance()
    forticloud_client_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_access_points = await forticloud_client_instance.get_access_points(network_id)
    assert type(response_get_access_points) is list


async def get_access_points_return_not_empty_list_test(forticloud_client_instance):
    forticloud_client_instance = forticloud_client_instance()
    forticloud_client_instance.forticloud_client.get_response_device = AsyncMock(return_value=correct_response)
    response_get_access_points = await forticloud_client_instance.get_access_points(network_id)
    assert len(response_get_access_points) > 0


async def get_access_points_raises_error_test(forticloud_client_instance):
    forticloud_client_instance = forticloud_client_instance()
    forticloud_client_instance.forticloud_client.get_response_device = AsyncMock(return_value=bad_status)
    with pytest.raises(UnexpectedStatusError):
        await forticloud_client_instance.get_access_points(network_id)


@pytest.mark.parametrize("ap_attempts", [2, 3, 4])
async def unexpected_ap_statuses_are_properly_retried_test(
    forticloud_client_instance,
    ap_attempts,
):
    # given
    forticloud_client_instance = forticloud_client_instance(
        ap_retry_stop=stop_after_attempt(ap_attempts),
    )
    forticloud_client_instance.forticloud_client.get_response_device = AsyncMock(
        return_value={"status": 500, "body": {}}
    )

    # when
    with pytest.raises(UnexpectedStatusError):
        await forticloud_client_instance.get_access_points("network_example_1")

    # then
    method_awaited = forticloud_client_instance.forticloud_client.get_response_device
    assert method_awaited.await_count == ap_attempts


@pytest.mark.parametrize("switch_attempts", [2, 3, 4])
async def unexpected_switch_statuses_are_properly_retried_test(
    forticloud_client_instance,
    switch_attempts,
):
    # given
    forticloud_client_instance = forticloud_client_instance(
        switch_retry_stop=stop_after_attempt(switch_attempts),
    )
    forticloud_client_instance.forticloud_client.get_response_device = AsyncMock(
        return_value={"status": 500, "body": {}}
    )

    # when
    with pytest.raises(UnexpectedStatusError):
        await forticloud_client_instance.get_switches("network_example_1")

    # then
    method_awaited = forticloud_client_instance.forticloud_client.get_response_device
    assert method_awaited.await_count == switch_attempts


@pytest.mark.parametrize("network_attempts", [2, 3, 4])
async def unexpected_network_statuses_are_properly_retried_test(
    forticloud_client_instance,
    network_attempts,
):
    # given
    forticloud_client_instance = forticloud_client_instance(
        network_retry_stop=stop_after_attempt(network_attempts),
    )
    forticloud_client_instance.forticloud_client.get_response_device = AsyncMock(
        return_value={"status": 500, "body": {}}
    )

    # when
    with pytest.raises(UnexpectedStatusError):
        await forticloud_client_instance.get_networks()

    # then
    method_awaited = forticloud_client_instance.forticloud_client.get_response_device
    assert method_awaited.await_count == network_attempts
