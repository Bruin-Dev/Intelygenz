import logging
from dataclasses import dataclass

from .create_ticket import CreateTicket
from .device import DeviceId
from .get_device import GetDevice

log = logging.getLogger(__name__)


@dataclass
class CheckDevice:
    get_device: GetDevice
    create_ticket: CreateTicket

    async def __call__(self, device_id: DeviceId):
        log.debug(f"check_device(device_id={device_id}")
        device = await self.get_device(device_id)

        if device.is_offline:
            log.debug("device.is_offline")
            await self.create_ticket(device_id)
