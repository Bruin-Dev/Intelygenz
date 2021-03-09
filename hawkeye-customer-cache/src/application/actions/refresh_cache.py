from datetime import datetime

from apscheduler.jobstores.base import ConflictingIdError
from pytz import timezone
from shortuuid import uuid
from tenacity import retry
from tenacity import wait_random


class RefreshCache:

    def __init__(self, config, event_bus, logger, scheduler, storage_repository, bruin_repository,
                 hawkeye_repository, notifications_repository):
        self._config = config
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._storage_repository = storage_repository
        self._bruin_repository = bruin_repository
        self._hawkeye_repository = hawkeye_repository
        self._notifications_repository = notifications_repository

    async def _refresh_cache(self):
        @retry(wait=wait_random(min=120, max=300), reraise=True)
        async def _refresh_cache():
            self._logger.info("Starting job to refresh the cache of hawkeye...")

            self._logger.info("Claiming all probes from Hawkeye...")
            probes_response = await self._hawkeye_repository.get_probes()
            if probes_response['status'] not in range(200, 300):
                self._logger.error(
                    f"Bad status calling get_probes. Error: {probes_response['status']}. Re-trying job...")
                probes_list = None
            else:
                self._logger.info("Got all probes from Hawkeye!")
                probes_list = probes_response['body']

            if not probes_list:
                refresh_attempts_count = _refresh_cache.retry.statistics['attempt_number']
                if refresh_attempts_count >= self._config.REFRESH_CONFIG['attempts_threshold']:
                    error_message = "[hawkeye-customer-cache] Too many consecutive failures happened while trying " \
                                    "to claim the list of probes of hawkeye"
                    await self._notifications_repository.send_slack_message(error_message)

                    self._logger.error(
                        f"Couldn't find any probe to refresh the cache. Error: {error_message}. Re-trying job...")
                err_msg = "Couldn't find any probe to refresh the cache"
                raise Exception(err_msg)

            self._logger.info(f"Got {len(probes_list)} probes from Hawkeye")

            self._logger.info("Refreshing cache for hawkeye")
            cache = []
            for device in probes_list:
                filter_device = await self._bruin_repository.filter_probe(device)
                if filter_device:
                    cache.append(filter_device)

            self._logger.info(f"Finished filtering probes for hawkeye")
            self._logger.info(f"Storing cache of {len(cache)} devices to Redis for hawkeye")
            self._storage_repository.set_hawkeye_cache(cache)
            self._logger.info("Finished refreshing hawkeye cache!")
        try:
            await _refresh_cache()
        except Exception as e:
            self._logger.error(f"An error occurred while refreshing the hawkeye cache -> {e}")
            slack_message = f"Maximum retries happened while while refreshing the cache cause of error was {e}"
            await self._notifications_repository.send_slack_message(slack_message)

    async def schedule_cache_refresh(self):
        self._logger.info(
            f"Scheduled to refresh cache every {self._config.REFRESH_CONFIG['refresh_map_minutes'] // 60} hours"
        )

        try:
            self._scheduler.add_job(self._refresh_cache, 'interval',
                                    minutes=self._config.REFRESH_CONFIG['refresh_map_minutes'],
                                    next_run_time=datetime.now(timezone(self._config.REFRESH_CONFIG['timezone'])),
                                    replace_existing=False, id='_refresh_cache')
        except ConflictingIdError:
            self._logger.info(f'There is a job scheduled for refreshing the cache already. No new job '
                              'is going to be scheduled.')
