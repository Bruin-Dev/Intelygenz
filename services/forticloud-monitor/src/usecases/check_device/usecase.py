import logging
from dataclasses import dataclass

from .build_ticket import BuildTicket
from .device import DeviceId
from .get_device import GetDevice
from .store_ticket import StoreTicket

log = logging.getLogger(__name__)


@dataclass
class CheckDevice:
    get_device: GetDevice
    store_ticket: StoreTicket
    build_ticket: BuildTicket

    async def __call__(self, device_id: DeviceId):
        log.debug(f"check_device(device_id={device_id}")
        device = await self.get_device(device_id)

        if device.is_offline:
            log.debug("device.is_offline")
            ticket = self.build_ticket(device)
            await self.store_ticket(ticket)
