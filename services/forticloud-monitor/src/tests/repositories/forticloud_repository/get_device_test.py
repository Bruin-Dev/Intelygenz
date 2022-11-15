from copy import deepcopy
from unittest.mock import ANY, AsyncMock, Mock

import pytest
from application.models.device import Device, DeviceStatus, DeviceType
from application.repositories import (
    DEFAULT_RETRY_CONFIG,
    ForticloudRepository,
    UnexpectedResponseError,
    UnexpectedStatusError,
    UnknownStatusError,
)
from forticloud_client.client import ForticloudClient
from tenacity import stop_after_attempt
from tenacity.stop import stop_base


async def a_forticloud_repository_is_built_with_a_default_ap_retry_config_test():
    assert ForticloudRepository(Mock()).ap_retry_config == DEFAULT_RETRY_CONFIG


async def a_forticloud_repository_is_built_with_a_default_switch_retry_config_test():
    assert ForticloudRepository(Mock()).switch_retry_config == DEFAULT_RETRY_CONFIG


async def ap_devices_are_properly_queried_test(any_forticloud_repository, any_ap_response, any_device_id):
    # given
    any_device_id.type = DeviceType.AP
    get_device_info = AsyncMock(return_value=any_ap_response)
    forticloud_repository = any_forticloud_repository(get_device_info=get_device_info)

    # when
    await forticloud_repository.get_device(any_device_id)

    # then
    get_device_info.assert_awaited_once_with(
        network_id=any_device_id.network_id,
        device="access_points",
        serial_number=f"{any_device_id.id}/",
    )


@pytest.mark.parametrize(
    ["forticloud_body", "expected_device"],
    [
        (
            {"result": {"connection_state": "connected"}},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="unknown",
                type="unknown",
                serial="unknown",
            ),
        ),
        (
            {"result": {"connection_state": "connected"}, "any_field": "any_value"},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="unknown",
                type="unknown",
                serial="unknown",
            ),
        ),
        (
            {"result": {"connection_state": "connected", "any_field": "any_value"}},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="unknown",
                type="unknown",
                serial="unknown",
            ),
        ),
        (
            {
                "result": {
                    "connection_state": "connected",
                    "name": "any_name",
                    "disc_type": "any_type",
                    "serial": "any_serial",
                }
            },
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="any_name",
                type="any_type",
                serial="any_serial",
            ),
        ),
        (
            {"result": {"connection_state": "connected", "name": {}, "disc_type": {}, "serial": {}}},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="unknown",
                type="unknown",
                serial="unknown",
            ),
        ),
    ],
    ids=[
        "partial data",
        "extra root fields",
        "extra result fields",
        "full data",
        "wrong data types",
    ],
)
async def ap_responses_are_properly_parsed_test(
    any_forticloud_repository,
    forticloud_body,
    expected_device,
    any_device_id,
):
    # given
    any_device_id.type = DeviceType.AP
    forticloud_repository = any_forticloud_repository(
        get_device_info=AsyncMock(return_value={"status": 200, "body": forticloud_body})
    )

    # then
    assert await forticloud_repository.get_device(any_device_id) == expected_device


@pytest.mark.parametrize(
    ["forticloud_ap_status", "expected_device_status"],
    [
        ("connected", DeviceStatus.ONLINE),
        ("Connected", DeviceStatus.ONLINE),
        ("connecting", DeviceStatus.ONLINE),
        ("Connecting", DeviceStatus.ONLINE),
        ("disconnected", DeviceStatus.OFFLINE),
        ("Disconnected", DeviceStatus.OFFLINE),
    ],
    ids=["connected", "Connected", "connecting", "Connecting", "disconnected", "Disconnected"],
)
async def ap_statuses_are_properly_parsed_test(
    any_forticloud_repository,
    forticloud_ap_status,
    expected_device_status,
    any_device_id,
):
    # given
    any_device_id.type = DeviceType.AP
    forticloud_repository = any_forticloud_repository(
        get_device_info=AsyncMock(
            return_value={"status": 200, "body": {"result": {"connection_state": forticloud_ap_status}}}
        )
    )

    # when
    device = await forticloud_repository.get_device(any_device_id)

    # then
    assert device.status == expected_device_status


@pytest.mark.parametrize(
    "forticloud_ap_status",
    ["", {}, "unknown", None],
    ids=["empty string", "wrong type", "unknown status", "None"],
)
async def unknown_ap_statuses_raise_a_proper_exception_test(
    any_forticloud_repository,
    forticloud_ap_status,
    any_device_id,
):
    # given
    any_device_id.type = DeviceType.AP
    forticloud_repository = any_forticloud_repository(
        get_device_info=AsyncMock(
            return_value={"status": 200, "body": {"result": {"connection_state": forticloud_ap_status}}}
        )
    )

    # then
    with pytest.raises(UnknownStatusError):
        await forticloud_repository.get_device(any_device_id)


async def switch_devices_are_properly_queried_test(any_forticloud_repository, any_switch_response, any_device_id):
    # given
    any_device_id.type = DeviceType.SWITCH
    get_device_info = AsyncMock(return_value=any_switch_response)
    forticloud_repository = any_forticloud_repository(get_device_info=get_device_info)

    # when
    await forticloud_repository.get_device(any_device_id)

    # then
    get_device_info.assert_awaited_once_with(
        network_id=any_device_id.network_id,
        device="switches",
        serial_number=f"{any_device_id.id}/",
    )


@pytest.mark.parametrize(
    ["forticloud_body", "expected_device"],
    [
        (
            {"conn_status": {"status": "online"}},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="unknown",
                type="unknown",
                serial="unknown",
            ),
        ),
        (
            {"conn_status": {"status": "online"}, "system": {"status": {"hostname": "any_hostname"}}},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="any_hostname",
                type="unknown",
                serial="unknown",
            ),
        ),
        (
            {"conn_status": {"status": "online"}, "any_field": "any_value"},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="unknown",
                type="unknown",
                serial="unknown",
            ),
        ),
        (
            {"conn_status": {"status": "online", "any_field": "any_value"}},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="unknown",
                type="unknown",
                serial="unknown",
            ),
        ),
        (
            {
                "conn_status": {"status": "online"},
                "system": {"status": {"hostname": "any_name", "model": "any_type", "serial_number": "any_serial"}},
            },
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="any_name",
                type="any_type",
                serial="any_serial",
            ),
        ),
        (
            {"conn_status": {"status": "online"}, "system": "any_system"},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="unknown",
                type="unknown",
                serial="unknown",
            ),
        ),
        (
            {"conn_status": {"status": "online"}, "system": {"status": "any_status"}},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="unknown",
                type="unknown",
                serial="unknown",
            ),
        ),
        (
            {
                "conn_status": {"status": "online"},
                "system": {"status": {"hostname": {}, "model": {}, "sn": {}}},
            },
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="unknown",
                type="unknown",
                serial="unknown",
            ),
        ),
    ],
    ids=[
        "partial data",
        "partial system status data",
        "extra root fields",
        "extra conn_status fields",
        "full data",
        "wrong system type",
        "wrong system status type",
        "wrong system status types",
    ],
)
async def switch_responses_are_properly_parsed_test(
    any_forticloud_repository,
    forticloud_body,
    expected_device,
    any_device_id,
):
    # given
    any_device_id.type = DeviceType.SWITCH
    forticloud_repository = any_forticloud_repository(
        get_device_info=AsyncMock(return_value={"status": 200, "body": forticloud_body})
    )

    # then
    assert await forticloud_repository.get_device(any_device_id) == expected_device


@pytest.mark.parametrize(
    ["forticloud_switch_status", "expected_device_status"],
    [
        ("online", DeviceStatus.ONLINE),
        ("connected", DeviceStatus.ONLINE),
        ("Connected", DeviceStatus.ONLINE),
        ("connecting", DeviceStatus.ONLINE),
        ("Connecting", DeviceStatus.ONLINE),
        ("offline", DeviceStatus.OFFLINE),
        ("disconnected", DeviceStatus.OFFLINE),
        ("Disconnected", DeviceStatus.OFFLINE),
    ],
    ids=["online", "connected", "Connected", "connecting", "Connecting", "offline", "disconnected", "Disconnected"],
)
async def switch_statuses_are_properly_parsed_test(
    any_forticloud_repository,
    forticloud_switch_status,
    expected_device_status,
    any_device_id,
):
    # given
    any_device_id.type = DeviceType.SWITCH
    forticloud_repository = any_forticloud_repository(
        get_device_info=AsyncMock(
            return_value={"status": 200, "body": {"conn_status": {"status": forticloud_switch_status}}}
        )
    )

    # when
    device = await forticloud_repository.get_device(any_device_id)

    # then
    assert device.status == expected_device_status


@pytest.mark.parametrize(
    "forticloud_switch_status",
    ["", {}, "unknown", None],
    ids=["empty string", "wrong type", "unknown status", "None"],
)
async def unknown_switch_statuses_raise_a_proper_exception_test(
    any_forticloud_repository,
    forticloud_switch_status,
    any_device_id,
):
    # given
    any_device_id.type = DeviceType.SWITCH
    forticloud_repository = any_forticloud_repository(
        get_device_info=AsyncMock(
            return_value={"status": 200, "body": {"conn_status": {"status": forticloud_switch_status}}}
        )
    )

    # then
    with pytest.raises(UnknownStatusError):
        await forticloud_repository.get_device(any_device_id)


@pytest.mark.parametrize("device_type", [DeviceType.AP, DeviceType.SWITCH])
async def unexpected_forticloud_statuses_raise_a_proper_exception_test(
    any_forticloud_repository,
    any_device_id,
    device_type,
):
    # given
    any_device_id.type = device_type
    forticloud_repository = any_forticloud_repository(
        get_device_info=AsyncMock(return_value={"status": 500, "body": {}})
    )

    # then
    with pytest.raises(UnexpectedStatusError):
        await forticloud_repository.get_device(any_device_id)


@pytest.mark.parametrize(
    ["forticloud_response", "expected_exception"],
    [
        ("non_json_response", UnexpectedResponseError),
        ({}, UnexpectedResponseError),
        ({"any_unexpected_field": "any_value"}, UnexpectedResponseError),
        ({"status": "any_string", "body": {}}, UnexpectedResponseError),
        ({"status": 200, "body": "non_dict_body"}, UnknownStatusError),
        ({"status": 200, "body": {}}, UnknownStatusError),
        ({"status": 200, "body": []}, UnknownStatusError),
    ],
    ids=[
        "string_response",
        "empty_response",
        "unexpected_fields",
        "wrong_status_type",
        "wrong_body_type",
        "empty_dict_body",
        "empty_list_body",
    ],
)
async def unparseable_ap_responses_raise_a_proper_exception_test(
    any_forticloud_repository,
    any_device_id,
    forticloud_response,
    expected_exception,
):
    # given
    any_device_id.type = DeviceType.AP
    forticloud_repository = any_forticloud_repository(get_device_info=AsyncMock(return_value=forticloud_response))

    # then
    with pytest.raises(expected_exception):
        await forticloud_repository.get_device(any_device_id)


@pytest.mark.parametrize(
    ["forticloud_response", "expected_exception"],
    [
        ("non_json_response", UnexpectedResponseError),
        ({}, UnexpectedResponseError),
        ({"any_unexpected_field": "any_value"}, UnexpectedResponseError),
        ({"status": "any_string", "body": {}}, UnexpectedResponseError),
        ({"status": 200, "body": "non_dict_body"}, UnknownStatusError),
        ({"status": 200, "body": {}}, UnknownStatusError),
        ({"status": 200, "body": []}, UnknownStatusError),
    ],
    ids=[
        "string_response",
        "empty_response",
        "unexpected_fields",
        "wrong_status_type",
        "wrong_body_type",
        "empty_dict_body",
        "empty_list_body",
    ],
)
async def unparseable_switch_responses_raise_a_proper_exception_test(
    any_forticloud_repository,
    any_device_id,
    forticloud_response,
    expected_exception,
):
    # given
    any_device_id.type = DeviceType.SWITCH
    forticloud_repository = any_forticloud_repository(get_device_info=AsyncMock(return_value=forticloud_response))

    # then
    with pytest.raises(expected_exception):
        await forticloud_repository.get_device(any_device_id)


@pytest.mark.parametrize("ap_attempts", [2, 3, 4])
async def unexpected_ap_statuses_are_properly_retried_test(
    any_forticloud_repository,
    any_device_id,
    ap_attempts,
):
    # given
    get_device_info = AsyncMock(return_value={"status": 500, "body": {}})
    any_device_id.type = DeviceType.AP
    forticloud_repository = any_forticloud_repository(
        get_device_info=get_device_info,
        ap_retry_stop=stop_after_attempt(ap_attempts),
    )

    # when
    with pytest.raises(UnexpectedStatusError):
        await forticloud_repository.get_device(any_device_id)

    # then
    assert get_device_info.await_count == ap_attempts


@pytest.mark.parametrize("switch_attempts", [2, 3, 4])
async def unexpected_switch_statuses_are_properly_retried_test(
    any_forticloud_repository,
    any_device_id,
    switch_attempts,
):
    # given
    get_device_info = AsyncMock(return_value={"status": 500, "body": {}})
    any_device_id.type = DeviceType.SWITCH
    forticloud_repository = any_forticloud_repository(
        get_device_info=get_device_info,
        switch_retry_stop=stop_after_attempt(switch_attempts),
    )

    # when
    with pytest.raises(UnexpectedStatusError):
        await forticloud_repository.get_device(any_device_id)

    # then
    assert get_device_info.await_count == switch_attempts


@pytest.mark.parametrize("forticloud_status", [500, 429])
async def unexpected_forticloud_statuses_are_properly_retried_test(
    any_forticloud_repository,
    any_device_id,
    forticloud_status,
):
    # given
    get_device_info = AsyncMock(return_value={"status": forticloud_status, "body": {}})
    any_device_id.type = DeviceType.AP
    forticloud_repository = any_forticloud_repository(
        get_device_info=get_device_info,
        ap_retry_stop=stop_after_attempt(3),
    )

    # when
    with pytest.raises(UnexpectedStatusError):
        await forticloud_repository.get_device(any_device_id)

    # then
    assert get_device_info.await_count == 3


@pytest.fixture
def any_forticloud_repository():
    def builder(
        get_device_info: AsyncMock,
        ap_retry_stop: stop_base = stop_after_attempt(1),
        switch_retry_stop: stop_base = stop_after_attempt(1),
    ):
        forticloud_client = Mock(ForticloudClient)
        forticloud_client.get_device_info = get_device_info

        ap_retry_config = deepcopy(DEFAULT_RETRY_CONFIG)
        ap_retry_config["stop"] = ap_retry_stop
        del ap_retry_config["wait"]

        switch_retry_config = deepcopy(DEFAULT_RETRY_CONFIG)
        switch_retry_config["stop"] = switch_retry_stop
        del switch_retry_config["wait"]

        return ForticloudRepository(
            forticloud_client=forticloud_client,
            ap_retry_config=ap_retry_config,
            switch_retry_config=switch_retry_config,
        )

    return builder


@pytest.fixture
def any_ap_response():
    return {"status": 200, "body": {"result": {"connection_state": "connected"}}}


@pytest.fixture
def any_switch_response():
    return {"status": 200, "body": {"conn_status": {"status": "online"}}}
