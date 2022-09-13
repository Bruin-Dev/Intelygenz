import logging
from dataclasses import dataclass

from .device import DeviceId
from .device_repository import DeviceRepository
from .ticket_repository import TicketRepository
from .ticket_service import TicketService

log = logging.getLogger(__name__)


@dataclass
class CheckDevice:
    device_repository: DeviceRepository
    ticket_repository: TicketRepository
    ticket_service: TicketService

    async def __call__(self, device_id: DeviceId):
        log.debug(f"check_device(device_id={device_id}")
        device = await self.device_repository.get(device_id)

        if device.is_offline:
            ticket = self.ticket_service.build_ticket_for(device)
            await self.ticket_repository.store(ticket)
