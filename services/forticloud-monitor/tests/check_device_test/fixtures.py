from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

from check_device.device import Device, DeviceId, DeviceStatus, DeviceType
from check_device.nats_client import NatsResponse
from check_device.ticket import Ticket


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


class AnyNatsResponse(NatsResponse[Any]):
    status: int = hash("any_status")
    body: Any = "any_body"


class AnyBaseModel(BaseModel):
    a_string: str
    an_int: int


class CustomException(Exception):
    pass
