from dataclasses import dataclass
from enum import IntEnum


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
