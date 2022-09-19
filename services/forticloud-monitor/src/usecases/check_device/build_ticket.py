import logging

from .device import Device
from .ticket import Ticket

log = logging.getLogger(__name__)


class BuildTicket:
    def __call__(self, device: Device) -> Ticket:
        log.debug(f"build_ticket_for(device={device})")
        return Ticket(device.id.client_id, device.id.service_number)
