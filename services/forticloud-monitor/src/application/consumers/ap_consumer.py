import logging
from dataclasses import dataclass

from framework.nats.models import Subscription
from nats.aio.msg import Msg
from pydantic import BaseModel

from application.actions.check_device import CheckDevice
from application.models.device import DeviceId, DeviceType

from .consumer_settings import ConsumerSettings

log = logging.getLogger(__name__)


class ApMessage(BaseModel):
    device_id: str
    device_network_id: str
    client_id: str
    service_number: str


@dataclass
class ApConsumer:
    settings: ConsumerSettings
    check_device: CheckDevice

    async def __call__(self, msg: Msg):
        log.debug(f"(msg={msg})")
        try:
            device_message = ApMessage.parse_raw(msg.data)
            device_id = to_device_id(device_message)
            await self.check_device(device_id)
        except Exception:
            log.exception(f"Error consuming message")

    def subscription(self) -> Subscription:
        return Subscription(queue=self.settings.queue, subject=self.settings.subject, cb=self)


def to_device_id(ap_message: ApMessage) -> DeviceId:
    log.debug(f"to_device_id(ap_message={ap_message})")
    return DeviceId(
        ap_message.device_id,
        ap_message.device_network_id,
        ap_message.client_id,
        ap_message.service_number,
        DeviceType.AP,
    )
