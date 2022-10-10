import logging
from datetime import datetime

from pytz import timezone

logger = logging.getLogger(__name__)


class CacheRepository:
    def __init__(self, scheduler, config, forticloud_repository, redis_repository, bruin_repository):
        self.scheduler = scheduler
        self.config = config
        self.forticloud_repository = forticloud_repository
        self.redis_repository = redis_repository
        self.bruin_repository = bruin_repository

    async def add_job_to_refresh_cache(self):
        logger.info("launched the task to refresh the forticloud cache!")
        self.scheduler.add_job(
            self.refresh_cache,
            "interval",
            seconds=self.config.FORTICLOUD_CACHE_CONFIGURATION["time_to_refresh_interval"],
            next_run_time=datetime.now(timezone(self.config.TIMEZONE)),
            replace_existing=False,
            id="refresh_forticloud_cache_task",
        )

    async def refresh_cache(self):
        id_networks_list = await self.forticloud_repository.get_list_networks_ids()

        list_of_switches = await self.get_switches(id_networks_list)
        list_of_access_points = await self.get_access_points(id_networks_list)

        await self.add_list_access_points_to_cache(list_of_access_points)
        await self.add_list_switches_to_cache(list_of_switches)
        logger.info("Updated Forticloud cache!")

    async def get_access_points(self, id_networks_list):
        access_points_list = await self.forticloud_repository.get_list_access_point(id_networks_list)
        list_of_access_points_with_client_id = await self.add_serial_client_id_to_device(access_points_list)
        return await self.get_devices_with_valid_management_status(list_of_access_points_with_client_id)

    async def get_switches(self, id_networks_list):
        switches_list = await self.forticloud_repository.get_list_switches(id_networks_list)
        list_of_switches_with_client_id = await self.add_serial_client_id_to_device(switches_list)
        return await self.get_devices_with_valid_management_status(list_of_switches_with_client_id)

    async def add_list_access_points_to_cache(self, list_of_access_points):
        await self.redis_repository.set_value_for_key(key="access_points", value=list_of_access_points)

    async def add_list_switches_to_cache(self, list_of_forticloud_switches):
        await self.redis_repository.set_value_for_key(key="switches", value=list_of_forticloud_switches)

    async def get_devices_with_valid_management_status(self, list_of_devices):
        list_of_devices_with_valid_management_status = []
        for device in list_of_devices:
            if (
                await self.bruin_repository.get_management_status_for_device(
                    client_id=device["client_id"], serial_number=device["serial_number"]
                )
                in self.config.MONITORABLE_MANAGEMENTS_STATUSES
            ):
                list_of_devices_with_valid_management_status.append(device)
        return list_of_devices_with_valid_management_status

    async def add_serial_client_id_to_device(self, list_of_devices):
        devices_with_serial = await self.bruin_repository.get_list_of_devices_with_client_id(
            list_of_devices=list_of_devices
        )
        return devices_with_serial

    def get_list_switches_of_cache(self):
        return self.redis_repository.get_value_if_exist(key="switches")

    def get_list_access_points_of_cache(self):
        return self.redis_repository.get_value_if_exist(key="access_points")
