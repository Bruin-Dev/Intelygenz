import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from typing import Any, Dict

from forticloud_client.client import ForticloudClient
from pydantic import ValidationError
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_random

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

DEFAULT_RETRY_CONFIG = dict(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_random(min=1, max=2),
    retry=retry_if_exception_type(UnexpectedStatusError),
)


@dataclass
class ForticloudRepository:
    forticloud_client: ForticloudClient
    ap_retry_config: Dict[str, Any] = field(default_factory=lambda: DEFAULT_RETRY_CONFIG)
    switch_retry_config: Dict[str, Any] = field(default_factory=lambda: DEFAULT_RETRY_CONFIG)

    async def get_device(self, device_id: DeviceId) -> Device:  # pragma: no cover
        log.debug(f"get_device(device_id={device_id}")
        if device_id.type == DeviceType.AP:
            return await self._get_ap_device(device_id)
        else:
            return await self._get_switch_device(device_id)

    async def _get_ap_device(self, device_id: DeviceId) -> Device:
        log.debug(f"_get_ap_device(device_id={device_id}")

        attempts = AsyncRetrying(**self.ap_retry_config)
        async for attempt in attempts:
            with attempt:
                forticloud_response = await self._get_device("access_points", device_id.network_id, device_id.id)
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

    async def _get_switch_device(self, device_id: DeviceId) -> Device:
        log.debug(f"_get_switch_device(device_id={device_id}")

        attempts = AsyncRetrying(**self.switch_retry_config)
        async for attempt in attempts:
            with attempt:
                forticloud_response = await self._get_device("switches", device_id.network_id, device_id.id)
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

    async def _get_device(self, device_type: str, network_id: str, serial_number: str) -> ForticloudResponse:
        response = await self.forticloud_client.get_device_info(device_type, network_id, serial_number)
        log.debug(f"get_device_info(...) => {response}")
        try:
            return ForticloudResponse.parse_obj(response)
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
