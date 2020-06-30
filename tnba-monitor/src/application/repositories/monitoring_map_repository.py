import time
from datetime import datetime

import asyncio
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone
from tenacity import retry, wait_exponential, stop_after_delay

from application.repositories import EdgeIdentifier


class MonitoringMapRepository:

    def __init__(self, config, scheduler, event_bus, velocloud_repository, bruin_repository, logger):
        self._config = config
        self._scheduler = scheduler
        self._event_bus = event_bus
        self._logger = logger
        self._velocloud_repository = velocloud_repository
        self._bruin_repository = bruin_repository

        self._monitoring_map_cache = {}
        self._temp_monitoring_map = {}
        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['semaphore'])
        self._blacklisted_edges = self._config.MONITOR_CONFIG['blacklisted_edges']

    async def start_create_monitoring_map_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: map_bruin_client_ids_to_edges_serials_and_statuses'
                          f' configured to run every'
                          f' {self._config.MONITOR_CONFIG["refresh_map_time"]} minutes')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.TIMEZONE))
            self._logger.info(f'It will be executed now')
        try:
            self._scheduler.add_job(self.map_bruin_client_ids_to_edges_serials_and_statuses, 'interval',
                                    minutes=self._config.MONITOR_CONFIG["refresh_map_time"],
                                    next_run_time=next_run_time,
                                    replace_existing=False, id='_create_client_id_to_dict_of_serials_dict')
        except ConflictingIdError:
            self._logger.info(f'There is a recheck job scheduled for creating monitoring map already. No new job '
                              'is going to be scheduled.')

    def get_monitoring_map_cache(self):
        return self._monitoring_map_cache.copy()

    async def map_bruin_client_ids_to_edges_serials_and_statuses(self):
        self._temp_monitoring_map = {}

        edge_list_response = await self._velocloud_repository.get_edges_for_tnba_monitoring()
        edge_list_response_status = edge_list_response['status']
        if edge_list_response_status not in range(200, 300):
            return

        edge_list_response_body = edge_list_response['body']

        tasks = [
            self._process_edge_and_tickets(edge_full_id)
            for edge_full_id in edge_list_response_body
            if edge_full_id not in self._blacklisted_edges
        ]
        start_time = time.time()
        self._logger.info(f"Processing {len(edge_list_response_body)} edges")

        await asyncio.gather(*tasks, return_exceptions=True)

        self._monitoring_map_cache = self._temp_monitoring_map
        self._temp_monitoring_map = {}

        self._logger.info(f"Processing {len(tasks)} edges took {(time.time() - start_time) // 60} minutes")

    async def _process_edge_and_tickets(self, edge_full_id):
        edge_identifier = EdgeIdentifier(**edge_full_id)

        @retry(wait=wait_exponential(multiplier=self._config.NATS_CONFIG['multiplier'],
                                     min=self._config.NATS_CONFIG['min']),
               stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay']))
        async def process_edge_and_tickets():
            async with self._semaphore:
                edge_status_response = await self._velocloud_repository.get_edge_status(edge_full_id)
                edge_status_response_status = edge_status_response['status']
                if edge_status_response_status not in range(200, 300):
                    return

                edge_status_response_body = edge_status_response['body']
                edge_status_data = edge_status_response_body['edge_info']

                serial_number = edge_status_data['edges']['serialNumber']

                if not serial_number:
                    self._logger.info(
                        f"[map-bruin-client-to-edges] Edge {edge_identifier} "
                        f"doesn't have any serial associated. Skipping..."
                    )
                    return

                bruin_client_info_response = await self._bruin_repository.get_client_info(serial_number)
                self._logger.info(f"[map-bruin-client-to-edges]Bruin client info -> {bruin_client_info_response}")
                bruin_client_info_response_status = bruin_client_info_response['status']
                if bruin_client_info_response_status not in range(200, 300):
                    return

                bruin_client_info_response_body = bruin_client_info_response['body']
                bruin_client_id = bruin_client_info_response_body.get('client_id', False)
                if not bruin_client_id:
                    self._logger.info(
                        f"[map-bruin-client-to-edges] Edge {edge_identifier} "
                        f"doesn't have any Bruin client ID associated. Skipping...")
                    return

                # Attach Bruin client info to edge_data
                edge_status_data['bruin_client_info'] = bruin_client_info_response_body

                self._logger.info(f'[map-bruin-client-to-edges]Getting management status for edge {edge_identifier}...')
                management_status_response = await self._bruin_repository.get_management_status(bruin_client_id,
                                                                                                serial_number)
                self._logger.info(f'[map-bruin-client-to-edges]Got management status for edge {edge_identifier} -> '
                                  f'{management_status_response}')

                management_status_response_body = management_status_response['body']
                management_status_response_status = management_status_response['status']
                if management_status_response_status not in range(200, 300):
                    self._logger.error(f"[map-bruin-client-to-edges]Management status is unknown for {edge_identifier}")
                    return

                if not self._bruin_repository.is_management_status_active(management_status_response_body):
                    self._logger.info(
                        f'[map-bruin-client-to-edges]Management status is not active for {edge_identifier}. '
                        f'Skipping process...')
                    return
                else:
                    self._logger.info(f'[map-bruin-client-to-edges]Management status for {edge_identifier} '
                                      'seems active.')

                self._temp_monitoring_map.setdefault(bruin_client_id, {})
                self._temp_monitoring_map[bruin_client_id][serial_number] = {
                    'edge_id': edge_full_id,
                    'edge_status': edge_status_data,
                }

                self._logger.info(
                    f"[map-bruin-client-to-edges] Edge with serial {serial_number} that belongs to Bruin customer "
                    f"{bruin_client_info_response_body} has been added to the map of devices to monitor"
                )

        try:
            await process_edge_and_tickets()
        except Exception as e:
            self._logger.error(
                f"[map-bruin-client-to-edges] An error occurred while trying to process edge {edge_identifier} -> {e}"
            )
