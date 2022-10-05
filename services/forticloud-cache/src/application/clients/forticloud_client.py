import logging
from dataclasses import dataclass
from http import HTTPStatus

from forticloud_client.client import ForticloudClient

logger = logging.getLogger(__name__)


@dataclass
class ForticloudClient:
    forticloud_client: ForticloudClient

    async def get_networks(self):
        logger.info("Getting FortiLAN networks...")

        get_networks_response = await self.forticloud_client.get_response_device(device="networks")
        if get_networks_response["status"] != HTTPStatus.OK:
            return []
        else:
            list_of_networks = get_networks_response["body"]["result"]
            logger.info(f"Got FortiLAN {len(list_of_networks)} networks!")
            return list_of_networks

    async def get_switches(self, network_id: int):
        logger.info(f"Getting FortiLAN switches in network {network_id}...")

        get_switches_response = await self.forticloud_client.get_response_device(
            device="switches", network_id=network_id
        )
        if get_switches_response["status"] != HTTPStatus.OK:
            return []
        else:
            list_of_switches = get_switches_response["body"]["result"]
            logger.info(f"Got FortiLAN switches {len(list_of_switches)} in network {network_id}!")
            return list_of_switches

    async def get_access_points(self, network_id: int):
        logger.info(f"Getting FortiLAN APs in network {network_id}...")
        access_point_response = await self.forticloud_client.get_response_device(
            device="access_points", network_id=network_id
        )
        if access_point_response["status"] != HTTPStatus.OK:
            logger.info(f"Error {access_point_response['status']} getting FortiLAN APs in network {network_id}!")
            return []
        else:
            list_of_access_points = access_point_response["body"]["result"]
            logger.info(f"Got FortiLAN access points {len(list_of_access_points)} in network {network_id}!")
            return list_of_access_points
