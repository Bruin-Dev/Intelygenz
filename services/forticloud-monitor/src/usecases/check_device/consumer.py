import logging
from dataclasses import dataclass
from typing import Literal

from framework.nats.models import Subscription
from nats.aio.msg import Msg
from pydantic import BaseModel, BaseSettings

from .device import DeviceId, DeviceType
from .usecase import Usecase

log = logging.getLogger(__name__)


class Settings(BaseSettings):
    queue: str = "forticloud-producer"
    subject: str = "forticloud-producer.monitored-devices"


class DeviceMessage(BaseModel):
    device_id: str
    device_network_id: str
    client_id: str
    service_number: str
    type: Literal["AP", "SWITCH"]


@dataclass
class Consumer:
    settings: Settings
    usecase: Usecase

    async def __call__(self, msg: Msg):
        log.debug(f"(msg={msg})")
        try:
            device_message = DeviceMessage.parse_raw(msg.data)
            device_id = to_device_id(device_message)
            await self.usecase(device_id)
        except:
            log.exception("Error consuming message")

    @property
    def subscription(self) -> Subscription:
        return Subscription(queue=self.settings.queue, subject=self.settings.subject, cb=self)


def to_device_id(device_message: DeviceMessage):
    log.debug(f"to_device_id(device_message={device_message})")
    return DeviceId(
        device_message.device_id,
        device_message.device_network_id,
        device_message.client_id,
        device_message.service_number,
        DeviceType[device_message.type],
    )
