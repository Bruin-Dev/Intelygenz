import os
from unittest.mock import Mock, patch

import pytest

from application.models.device import Device, DeviceStatus
from application.repositories import REOPEN_HEADER, TRIAGE_HEADER, build_note


@pytest.mark.parametrize(
    ["is_reopen_note", "expected_header"],
    [
        (False, TRIAGE_HEADER),
        (True, REOPEN_HEADER),
    ],
    ids=["triage header", "reopen header"],
)
def note_headers_are_properly_built_test(any_device, is_reopen_note, expected_header):
    assert os.linesep.join(expected_header) in build_note(any_device, is_reopen_note=is_reopen_note)


@pytest.mark.parametrize(
    ["device_status", "expected_event"],
    [
        (DeviceStatus.OFFLINE, "Event: Device Down"),
        (DeviceStatus.ONLINE, "Event: Device Up"),
    ],
    ids=["device down event", "device up event"],
)
def note_events_are_properly_built_test(any_device, device_status, expected_event):
    # given
    any_device.status = device_status

    # then
    assert expected_event in build_note(any_device)


@patch("application.repositories.forticloud_repository.datetime")
def notes_are_properly_built_test(datetime_mock, any_device_id):
    # given
    datetime_mock.utcnow = Mock(return_value="any_date")
    device = Device(
        id=any_device_id,
        status=DeviceStatus.OFFLINE,
        name="any_name",
        type="any_type",
        serial="any_serial",
    )

    # then
    assert build_note(device) == os.linesep.join(
        [
            "#*MetTel's IPA*#",
            "Forticloud triage.",
            "",
            "FortiLAN Instance: unknown",
            "Device Name: any_name",
            "Device Type: any_type",
            "Serial Number: any_serial",
            "Event: Device Down",
            "TimeStamp: any_date",
        ]
    )
