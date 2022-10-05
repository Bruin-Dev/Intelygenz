import logging
from dataclasses import dataclass

from application.clients.bruin_client import BruinClient
from application.repositories.assemblers.device_assembler import build_device_with_client_id

logger = logging.getLogger(__name__)


@dataclass
class BruinRepository:
    bruin_client: BruinClient

    async def get_list_of_devices_with_client_id(self, list_of_devices):
        devices_with_client_id = []
        for device in list_of_devices:
            device_with_client = build_device_with_client_id(
                device=device, client_id=await self.get_client_id_from_device(device)
            )
            if device_with_client:
                devices_with_client_id.append(device_with_client)
        return devices_with_client_id

    async def get_client_id_from_device(self, device: dict):
        customer_info_from_serial = await self.bruin_client.get_customer_info_from_serial(device["serial_number"])
        if customer_info_from_serial:
            return customer_info_from_serial[0]["client_id"]
        return None

    async def get_management_status_for_device(self, client_id, serial_number):
        return await self.bruin_client.get_management_status(client_id=client_id, serial_number=serial_number)
