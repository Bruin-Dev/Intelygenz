import base64
import csv
import json
from datetime import datetime
from typing import List

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

            self._logger.info(f"Distinguishing {len(edge_list)} edges per Velocloud host...")
            split_host_dict = {}
            for edge_with_serial in edge_list:
                host_ = edge_with_serial['edge']['host']
                split_host_dict.setdefault(host_, [])
                split_host_dict[host_].append(edge_with_serial)

            self._logger.info("Refreshing cache for each of the hosts...")
            tasks = [
                self._partial_refresh_cache(host, split_host_dict[host])
                for host in split_host_dict
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
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
        tasks = [
            self._bruin_repository.filter_edge_list(edge)
            for edge in edge_list
        ]
        cache = [
            edge
            for edge in await asyncio.gather(*tasks)
            if edge is not None
        ]
        self._logger.info(f"Finished filtering edges for host {host}")

        if len(cache) == 0:
            error_msg = f"Cache for host {host} was empty after cross referencing with Bruin." \
                        f" Check if Bruin is returning errors when asking for management statuses of the host"
            self._logger.error(error_msg)
            await self._event_bus.rpc_request("notification.slack.request", error_msg, timeout=10)
        else:
            stored_cache = self._storage_repository.get_cache(host)

            self._logger.info(
                f'Crossing currently stored cache ({len(stored_cache)} edges) with new one ({len(cache)} edges)...'
            )
            crossed_cache = self._cross_stored_cache_and_new_cache(stored_cache=stored_cache, new_cache=cache)

            self._logger.info(f"Storing cache of {len(crossed_cache)} edges to Redis for host {host}")
            self._storage_repository.set_cache(host, crossed_cache)
            self._logger.info(f"Finished storing cache for host {host}")
            await self._send_email_snapshot(host=host, old_cache=stored_cache, new_cache=crossed_cache)

    @staticmethod
    def _cross_stored_cache_and_new_cache(stored_cache: List[dict], new_cache: List[dict]) -> List[dict]:
        stored_devices_by_serial = {
            edge['serial_number']: edge
            for edge in stored_cache
        }
        new_devices_by_serial = {
            edge['serial_number']: edge
            for edge in new_cache
        }

        # If a device is in both caches, its info in new_cache will overwrite stored_cache's
        # If a device is only in one of the caches, it will be added to the final cache
        crossed_cache = {
            **stored_devices_by_serial,
            **new_devices_by_serial,
        }
        return list(crossed_cache.values())

    async def _send_email_snapshot(self, host, old_cache, new_cache):
        self._logger.info("Sending email with snapshots of cache...")
        email_obj = self._format_email_object(host, old_cache, new_cache)
        response = await self._event_bus.rpc_request("notification.email.request", email_obj, timeout=60)
        self._logger.info(f"Response from sending email: {json.dumps(response)}")

    def _format_email_object(self, host, old_cache, new_cache):
        now = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
        old_cache_csv = self._generate_csv_bytes_from_cache("old_cache.csv", old_cache)
        new_cache_csv = self._generate_csv_bytes_from_cache("new_cache.csv", new_cache)
        return {
            'request_id': uuid(),
            'email_data': {
                'subject': f'Customer cache snapshots. Environment: {self._config.ENVIRONMENT_NAME}. Host: {host}. '
                           f'{now}',
                'recipient': self._config.REFRESH_CONFIG["email_recipient"],
                'text': 'this is the accessible text for the email',
                'html': f"In this email you will see attached 2 CSV files: the prior and current status of the "
                        f"customer cache for the host {host}. If the environment is not 'production' disregard this."
                        f"Please note that timestamps in the files and in the subject are in UTC.",
                'images': [],
                'attachments': [
                    {
                        'name': f"old_customer_cache_{host}_{now}.csv",
                        'data': old_cache_csv
                    },
                    {
                        'name': f"new_customer_cache_{host}_{now}.csv",
                        'data': new_cache_csv
                    }
                ]
            }
        }

    @staticmethod
    def _generate_csv_bytes_from_cache(file_name, cache):
        titles = ["Serial Number", "Bruin Client ID", "Bruin Client Name", "Velo Host", "Velo Enterprise ID",
                  "Velo Edge ID", "Last Contact", "Logical IDs"]
        rows = [[item["serial_number"], item["bruin_client_info"]["client_id"],
                 item["bruin_client_info"]["client_name"], item["edge"]["host"], item["edge"]["enterprise_id"],
                 item["edge"]["edge_id"], item["last_contact"], item["logical_ids"]]
                for item in cache]
        with open(f'./{file_name}', 'w', encoding='utf-8') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(titles)
            for row in rows:
                filewriter.writerow(row)
        with open(f'./{file_name}', 'r', encoding='utf-8') as csvfile:
            payload = csvfile.read()
            return base64.b64encode(payload.encode('utf-8')).decode('utf-8')
