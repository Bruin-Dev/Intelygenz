import logging
from dataclasses import dataclass
from enum import IntEnum

log = logging.getLogger(__name__)


class DeviceType(IntEnum):
    AP = 1
    SWITCH = 2


class DeviceStatus(IntEnum):
    ONLINE = 1
    OFFLINE = 2


@dataclass
class DeviceId:
    id: str
    network_id: str
    client_id: str
    service_number: str
    type: DeviceType


@dataclass
class Device:
    id: DeviceId
    status: DeviceStatus

    @property
    def is_offline(self):
        return self.status == DeviceStatus.OFFLINE


@dataclass
class GetDevice:
    def __call__(self, device_id: DeviceId) -> Device:  # pragma: no cover
        log.debug(f"get(device_id={device_id}")
        return Device(id=device_id, status=DeviceStatus.OFFLINE)
