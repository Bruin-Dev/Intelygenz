from unittest.mock import ANY, AsyncMock, Mock

import pytest
from forticloud_client.client import ForticloudClient

from application.models.device import Device, DeviceStatus, DeviceType
from application.repositories import (
    ForticloudRepository,
    UnexpectedResponseError,
    UnexpectedStatusError,
    UnknownStatusError,
)


async def ap_devices_are_properly_queried_test(any_forticloud_repository, any_ap_response, any_device_id):
    # given
    any_device_id.type = DeviceType.AP
    get_device_info = AsyncMock(return_value=any_ap_response)
    forticloud_repository = any_forticloud_repository(get_device_info=get_device_info)

    # when
    await forticloud_repository.get_device(any_device_id)

    # then
    get_device_info.assert_awaited_once_with("access_points", any_device_id.network_id, any_device_id.id)


@pytest.mark.parametrize(
    ["forticloud_body", "expected_device"],
    [
        (
            {"connection_state": "connected"},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="unknown",
                type="unknown",
                serial="unknown",
            ),
        ),
        (
            {"connection_state": "connected", "any_field": "any_value"},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="unknown",
                type="unknown",
                serial="unknown",
            ),
        ),
        (
            {"connection_state": "connected", "name": "any_name", "disc_type": "any_type", "serial": "any_serial"},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="any_name",
                type="any_type",
                serial="any_serial",
            ),
        ),
        (
            {"connection_state": "connected", "name": {}, "disc_type": {}, "serial": {}},
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
        ("disconnected", DeviceStatus.OFFLINE),
        ("Disconnected", DeviceStatus.OFFLINE),
    ],
    ids=["connected", "Connected", "disconnected", "Disconnected"],
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
        get_device_info=AsyncMock(return_value={"status": 200, "body": {"connection_state": forticloud_ap_status}})
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
        get_device_info=AsyncMock(return_value={"status": 200, "body": {"status": forticloud_ap_status}})
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
    get_device_info.assert_awaited_once_with("switches", any_device_id.network_id, any_device_id.id)


@pytest.mark.parametrize(
    ["forticloud_body", "expected_device"],
    [
        (
            {"status": "online"},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="unknown",
                type="unknown",
                serial="unknown",
            ),
        ),
        (
            {"status": "online", "any_field": "any_value"},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="unknown",
                type="unknown",
                serial="unknown",
            ),
        ),
        (
            {"status": "online", "hostname": "any_name", "model": "any_type", "sn": "any_serial"},
            Device(
                id=ANY,
                status=DeviceStatus.ONLINE,
                name="any_name",
                type="any_type",
                serial="any_serial",
            ),
        ),
        (
            {"status": "online", "hostname": {}, "model": {}, "sn": {}},
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
        "full data",
        "wrong data types",
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
        ("offline", DeviceStatus.OFFLINE),
    ],
    ids=["connected", "offline"],
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
        get_device_info=AsyncMock(return_value={"status": 200, "body": {"status": forticloud_switch_status}})
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
        get_device_info=AsyncMock(return_value={"status": 200, "body": {"status": forticloud_switch_status}})
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
    "forticloud_response",
    [
        "non_json_response",
        {},
        {"any_unexpected_field": "any_value"},
        {"status": 200, "body": "non_dict_body"},
        {"status": "any_string", "body": {}},
    ],
    ids=[
        "string response",
        "empty response",
        "unexpected fields",
        "wrong body type",
        "wrong status type",
    ],
)
async def unparseable_ap_responses_raise_a_proper_exception_test(
    any_forticloud_repository,
    any_device_id,
    forticloud_response,
):
    # given
    any_device_id.type = DeviceType.AP
    forticloud_repository = any_forticloud_repository(get_device_info=AsyncMock(return_value=forticloud_response))

    # then
    with pytest.raises(UnexpectedResponseError):
        await forticloud_repository.get_device(any_device_id)


@pytest.mark.parametrize(
    "forticloud_response",
    [
        "non_json_response",
        {},
        {"any_unexpected_field": "any_value"},
        {"status": 200, "body": "non_dict_body"},
        {"status": "any_string", "body": {}},
    ],
    ids=[
        "string response",
        "empty response",
        "unexpected fields",
        "wrong body type",
        "wrong status type",
    ],
)
async def unparseable_switch_responses_raise_a_proper_exception_test(
    any_forticloud_repository,
    any_device_id,
    forticloud_response,
):
    # given
    any_device_id.type = DeviceType.SWITCH
    forticloud_repository = any_forticloud_repository(get_device_info=AsyncMock(return_value=forticloud_response))

    # then
    with pytest.raises(UnexpectedResponseError):
        await forticloud_repository.get_device(any_device_id)


@pytest.fixture
def any_forticloud_repository():
    def builder(get_device_info: AsyncMock):
        forticloud_client = Mock(ForticloudClient)
        forticloud_client.get_device_info = get_device_info
        return ForticloudRepository(forticloud_client=forticloud_client)

    return builder


@pytest.fixture
def any_ap_response():
    return {"status": 200, "body": {"connection_state": "connected"}}


@pytest.fixture
def any_switch_response():
    return {"status": 200, "body": {"status": "online"}}
