import logging
import os
from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus

from forticloud_client.client import ForticloudClient
from pydantic import ValidationError

from application.models.device import Device, DeviceId, DeviceStatus, DeviceType
from application.repositories import UnexpectedResponseError, UnexpectedStatusError
from application.repositories.errors import UnknownStatusError
from application.repositories.forticloud_repository_models.get_device import (
    APResponseBody,
    ForticloudResponse,
    SwitchResponseBody,
)

log = logging.getLogger(__name__)

TRIAGE_HEADER = ["#*MetTel's IPA*#", "Forticloud triage.", ""]
REOPEN_HEADER = ["#*MetTel's IPA*#", "Re-opening ticket.", ""]
DEVICE_UP_EVENT = "Event: Device Up"
DEVICE_DOWN_EVENT = "Event: Device Down"


@dataclass
class ForticloudRepository:
    forticloud_client: ForticloudClient

    async def get_device(self, device_id: DeviceId) -> Device:  # pragma: no cover
        log.debug(f"get_device(device_id={device_id}")
        if device_id.type == DeviceType.AP:
            return await self._get_ap_device(device_id)
        else:
            return await self._get_switch_device(device_id)

    async def _get_ap_device(self, device_id: DeviceId) -> Device:
        log.debug(f"_get_ap_device(device_id={device_id}")
        response = await self.forticloud_client.get_device_info("access_points", device_id.network_id, device_id.id)
        log.debug(f"get_device_info(...) => {response}")

        try:
            forticloud_response = ForticloudResponse.parse_obj(response)
            if forticloud_response.status != HTTPStatus.OK:
                raise UnexpectedStatusError(forticloud_response.status)

            ap_response = APResponseBody.parse_obj(forticloud_response.body)

            ap_status = DeviceStatus.UNKNOWN
            match ap_response.connection_state:
                case "connected" | "Connected":
                    ap_status = DeviceStatus.ONLINE
                case "disconnected" | "Disconnected":
                    ap_status = DeviceStatus.OFFLINE

            if ap_status == DeviceStatus.UNKNOWN:
                raise UnknownStatusError(ap_response.connection_state)

            return Device(
                id=device_id,
                status=ap_status,
                name=ap_response.name or "unknown",
                type=ap_response.disc_type or "unknown",
                serial=ap_response.serial or "unknown",
            )

        except ValidationError as e:
            raise UnexpectedResponseError from e

    async def _get_switch_device(self, device_id: DeviceId) -> Device:
        log.debug(f"_get_switch_device(device_id={device_id}")
        response = await self.forticloud_client.get_device_info("switches", device_id.network_id, device_id.id)
        log.debug(f"get_device_info(...) => {response}")

        try:
            forticloud_response = ForticloudResponse.parse_obj(response)
            if forticloud_response.status != HTTPStatus.OK:
                raise UnexpectedStatusError(forticloud_response.status)

            switch_response = SwitchResponseBody.parse_obj(forticloud_response.body)

            switch_status = DeviceStatus.UNKNOWN
            match switch_response.status:
                case "online":
                    switch_status = DeviceStatus.ONLINE
                case "offline":
                    switch_status = DeviceStatus.OFFLINE

            if switch_status == DeviceStatus.UNKNOWN:
                raise UnknownStatusError(switch_response.status)

            return Device(
                id=device_id,
                status=switch_status,
                name=switch_response.hostname or "unknown",
                type=switch_response.model or "unknown",
                serial=switch_response.sn or "unknown",
            )

        except ValidationError as e:
            raise UnexpectedResponseError from e


def build_note(device: Device, is_reopen_note: bool = False) -> str:
    lines = []
    lines += REOPEN_HEADER if is_reopen_note else TRIAGE_HEADER
    lines += [
        f"FortiLAN Instance: unknown",
        f"Device Name: {device.name}",
        f"Device Type: {device.type}",
        f"Serial Number: {device.serial}",
        f"Event: {'Device Down' if device.is_offline else 'Device Up'}",
        f"TimeStamp: {datetime.utcnow()}",
    ]

    return os.linesep.join(lines)
