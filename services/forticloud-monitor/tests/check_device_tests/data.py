from dataclasses import dataclass, field

from check_device.device import Device, DeviceId, DeviceStatus, DeviceType
from check_device.ticket import Ticket
from check_device.ticket_repository import Request


@dataclass
class AnyDeviceId(DeviceId):
    id: str = "any_id"
    network_id: str = "any_network_id"
    client_id: str = str(hash("any_client_id"))
    service_number: str = str(hash("any_service_number"))
    type: DeviceType = DeviceType.AP


@dataclass
class AnyDevice(Device):
    id: DeviceId = field(default_factory=lambda: AnyDeviceId())
    status: DeviceStatus = DeviceStatus.ONLINE


@dataclass
class AnyTicket(Ticket):
    client_id: str = str(hash("any_client_id"))
    service_number: str = str(hash("any_service_number"))
