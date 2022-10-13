import logging
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any, Dict

from forticloud_client.client import ForticloudClient
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_chain, wait_random

from config import config
from application.repositories.errors import UnexpectedStatusError

logger = logging.getLogger(__name__)

DEFAULT_RETRY_CONFIG = dict(
    reraise=config.MONITOR_RETRY_CONFIG["reraise"],
    stop=stop_after_attempt(config.MONITOR_RETRY_CONFIG["stop_after_attempt"]),
    wait=wait_chain(wait_random(min=1, max=3), wait_random(min=2, max=4), wait_random(min=3, max=5)),
    retry=retry_if_exception_type(UnexpectedStatusError),
)


@dataclass
class ForticloudClient:
    forticloud_client: ForticloudClient
    ap_retry_config: Dict[str, Any] = field(default_factory=lambda: DEFAULT_RETRY_CONFIG)
    network_retry_config: Dict[str, Any] = field(default_factory=lambda: DEFAULT_RETRY_CONFIG)
    switch_retry_config: Dict[str, Any] = field(default_factory=lambda: DEFAULT_RETRY_CONFIG)

    async def get_networks(self):
        logger.info("Getting FortiLAN networks...")
        attempts = AsyncRetrying(**self.network_retry_config)

        async for attempt in attempts:
            with attempt:
                get_networks_response = await self.forticloud_client.get_response_device(device="networks")
                if get_networks_response["status"] != HTTPStatus.OK:
                    raise UnexpectedStatusError(get_networks_response["status"])
                else:
                    list_of_networks = get_networks_response["body"]["result"]
                    logger.info(f"Got FortiLAN {len(list_of_networks)} networks!")
                    return list_of_networks

    async def get_switches(self, network_id: int):
        logger.info(f"Getting FortiLAN switches in network {network_id}...")
        attempts = AsyncRetrying(**self.switch_retry_config)

        async for attempt in attempts:
            with attempt:
                get_switches_response = await self.forticloud_client.get_response_device(
                    device="switches", network_id=network_id
                )
                if get_switches_response["status"] != HTTPStatus.OK:
                    raise UnexpectedStatusError(get_switches_response["status"])
                else:
                    list_of_switches = get_switches_response["body"]["result"]
                    logger.info(f"Got FortiLAN switches {len(list_of_switches)} in network {network_id}!")
                    return list_of_switches

    async def get_access_points(self, network_id: int):
        logger.info(f"Getting FortiLAN APs in network {network_id}...")
        attempts = AsyncRetrying(**self.ap_retry_config)

        async for attempt in attempts:
            with attempt:
                access_point_response = await self.forticloud_client.get_response_device(
                    device="access_points", network_id=network_id
                )
                if access_point_response["status"] != HTTPStatus.OK:
                    raise UnexpectedStatusError(access_point_response["status"])
                else:
                    list_of_access_points = access_point_response["body"]["result"]
                    logger.info(f"Got FortiLAN access points {len(list_of_access_points)} in network {network_id}!")
                    return list_of_access_points
