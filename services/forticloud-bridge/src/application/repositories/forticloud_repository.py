import logging

logger = logging.getLogger(__name__)


class ForticloudRepository:
    def __init__(self, forticloud_client):
        self._forticloud_client = forticloud_client

    async def get_ap_data(self, payload):
        return await self._forticloud_client.get_ap_data(payload)

    async def get_switches_data(self, payload):
        return await self._forticloud_client.get_switches_data(payload)
