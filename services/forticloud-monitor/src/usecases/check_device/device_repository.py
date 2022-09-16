import logging
from dataclasses import dataclass

from .device import Device, DeviceId, DeviceStatus

log = logging.getLogger(__name__)


@dataclass
class DeviceRepository:
    async def get(self, device_id: DeviceId) -> Device:  # pragma: no cover
        log.debug(f"get(device_id={device_id}")
        return Device(id=device_id, status=DeviceStatus.ONLINE)
