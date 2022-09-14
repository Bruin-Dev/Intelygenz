import logging

from .device import Device
from .ticket import Ticket

log = logging.getLogger(__name__)


def build_ticket_for(device: Device) -> Ticket:
    log.debug(f"build_ticket_for(device={device})")
    return Ticket(device.id.client_id, device.id.service_number)
