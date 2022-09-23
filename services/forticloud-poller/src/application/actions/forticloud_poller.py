import logging
import time
from datetime import datetime
from typing import Dict, List

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone

logger = logging.getLogger(__name__)


class ForticloudPoller:
    def __init__(
        self,
        nats_client,
        scheduler,
        config,
        redis_repository,
        notifications_repository,
    ):
        self._nats_client = nats_client
        self._scheduler = scheduler
        self._config = config
        self._redis_repository = redis_repository
        self._notifications_repository = notifications_repository

    async def start_forticloud_poller(self, exec_on_start: bool = False):
        logger.info("Scheduling Forticloud Poller job...")
        next_run_time = undefined

        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.TIMEZONE))
            logger.info("Forticloud Poller job is going to be executed immediately")

        try:
            self._scheduler.add_job(
                self._forticloud_poller_process,
                "interval",
                minutes=self._config.MONITOR_CONFIG["monitoring_minutes_interval"],
                next_run_time=next_run_time,
                replace_existing=False,
                id="_forticloud_poller_process",
            )
        except ConflictingIdError as conflict:
            logger.error(f"Skipping start of Forticloud Poller job. Reason: {conflict}")

    async def _forticloud_poller_process(self):
        logger.info(f"Starting Forticloud Poller process now...")
        start_time = time.time()

        access_points_data = self._redis_repository.get_list_access_points_of_redis()
        if access_points_data and type(access_points_data) == list:
            await self._process_data(access_points_data, target="aps")
        else:
            error_msg = "Error: APS Forticloud MALFORMED DATA"
            logger.error(error_msg)
            await self._notifications_repository.send_slack_message(error_msg)

        switches_points_data = self._redis_repository.get_list_switches_of_redis()
        if switches_points_data and type(access_points_data) == list:
            await self._process_data(switches_points_data, target="switches")
        else:
            error_msg = "Error: Switches Forticloud MALFORMED DATA"
            logger.error(error_msg)
            await self._notifications_repository.send_slack_message(error_msg)

        logger.info(f"Finished processing! Took {round((time.time() - start_time) / 60, 2)} minutes")

    async def _process_data(self, data: List, target: str):
        for device in data:
            await self._publish_forticloud_data(device, target)

    async def _publish_forticloud_data(self, data: Dict, target: str):
        logger.info(f"Publishing {target} forticloud data in NATS")
        msg = {"data": data}
        await self._nats_client.publish_message(f"forticloud.{target}", msg)
