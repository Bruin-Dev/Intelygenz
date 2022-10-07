import logging
from dataclasses import dataclass

from framework.nats.models import Subscription
from nats.aio.msg import Msg
from pydantic import BaseModel

from application.actions.check_device import CheckDevice
from application.models.device import DeviceId, DeviceType

from .consumer_settings import ConsumerSettings

log = logging.getLogger(__name__)


class SwitchMessage(BaseModel):
    serial_number: str
    network_id: str
    client_id: str


@dataclass
class SwitchConsumer:
    settings: ConsumerSettings
    check_device: CheckDevice

    async def __call__(self, msg: Msg):
        log.debug(f"(msg={msg})")
        try:
            device_message = SwitchMessage.parse_raw(msg.data)
            device_id = to_device_id(device_message)
            await self.check_device(device_id)
            log.debug(f"The device {device_id} was properly consumed")
        except Exception:
            log.exception("Error consuming message")

    def subscription(self) -> Subscription:
        return Subscription(queue=self.settings.queue, subject=self.settings.subject, cb=self)


def to_device_id(switch_message: SwitchMessage) -> DeviceId:
    log.debug(f"to_device_id(switch_message={switch_message})")
    return DeviceId(
        id=switch_message.serial_number,
        network_id=switch_message.network_id,
        client_id=switch_message.client_id,
        service_number=switch_message.serial_number,
        type=DeviceType.SWITCH,
    )
