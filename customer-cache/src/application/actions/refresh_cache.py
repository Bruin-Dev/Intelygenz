from datetime import datetime

import asyncio
from apscheduler.jobstores.base import ConflictingIdError
from pytz import timezone
from shortuuid import uuid
from tenacity import retry
from tenacity import wait_random


class RefreshCache:

    def __init__(self, config, event_bus, logger, scheduler, storage_repository, bruin_repository,
                 velocloud_repository):
        self._config = config
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._storage_repository = storage_repository
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository

    async def _refresh_cache(self):
        @retry(wait=wait_random(min=120, max=300), reraise=True)
        async def _refresh_cache():
            velocloud_hosts = sum([list(filter_.keys()) for filter_ in self._config.REFRESH_CONFIG['velo_servers']], [])

            self._logger.info("Starting job to refresh the cache of edges...")
            self._logger.info(f"Velocloud hosts that are going to be cached: {', '.join(velocloud_hosts)}")

            self._logger.info("Claiming edges for the hosts specified in the config...")
            edge_list = await self._velocloud_repository.get_all_velo_edges()

            if not edge_list:
                refresh_attempts_count = _refresh_cache.retry.statistics['attempt_number']
                if refresh_attempts_count >= self._config.REFRESH_CONFIG['attempts_threshold']:
                    error_message = "[customer-cache] Too many consecutive failures happened while trying " \
                                    "to claim the list of edges from Velocloud"
                    msg = {
                        'request_id': uuid(),
                        'message': error_message
                    }
                    await self._event_bus.rpc_request("notification.slack.request", msg, timeout=10)

                    self._logger.error(
                        f"Couldn't find any edge to refresh the cache. Error: {error_message}. Re-trying job...")
                err_msg = "Couldn't find any edge to refresh the cache"
                raise Exception(err_msg)

            self._logger.info("Distinguishing edges per Velocloud host...")
            split_host_dict = {}
            for edge_with_serial in edge_list:
                split_host_dict.setdefault(edge_with_serial['edge']['host'], [])
                split_host_dict[edge_with_serial['edge']['host']].append(edge_with_serial)

            self._logger.info("Refreshing cache for each of the hosts...")
            # TODO: replace loop with asyncio.gather
            for host in split_host_dict:
                await self._partial_refresh_cache(host, split_host_dict[host])
            self._logger.info("Finished refreshing cache!")

        try:
            await _refresh_cache()
        except Exception as e:
            self._logger.error(f"An error occurred while refreshing the cache -> {e}")
            slack_message = f"Maximum retries happened while while refreshing the cache cause of error was {e}"
            message = {
                'request_id': uuid(),
                'message': slack_message,
            }
            await self._event_bus.rpc_request("notification.slack.request", message, timeout=10)

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

    async def _partial_refresh_cache(self, host, edge_list):
        self._logger.info(f"Filtering the list of edges for host {host}")

        # TODO: replace loop with asyncio.gather
        edges_filtered = []
        for edge in edge_list:
            edge_filtered = await self._bruin_repository.filter_edge_list(edge)
            edges_filtered.append(edge_filtered)

        cache = [
            edge
            for edge in edges_filtered
            if edge is not None
        ]
        self._logger.info(f"Finished filtering edges for host {host}")

        self._logger.info(f"Storing cache of {len(cache)} edges to Redis for host {host}")
        self._storage_repository.set_cache(host, cache)
        self._logger.info(f"Finished storing cache for host {host}")
