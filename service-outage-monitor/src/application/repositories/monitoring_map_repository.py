import time
from datetime import datetime

import asyncio
from application.repositories import EdgeIdentifier
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone
from shortuuid import uuid
from tenacity import retry, wait_exponential, stop_after_delay


class MonitoringMapRepository:

    def __init__(self, config, scheduler, event_bus, logger, metrics_repository):
        self._logger = logger
        self._config = config
        self._scheduler = scheduler
        self._event_bus = event_bus
        self._logger = logger
        self._metrics_repository = metrics_repository

        self._monitoring_map_cache = {}
        self._temp_monitoring_map = {}
        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_MAP_CONFIG['semaphore'])
        self._blacklisted_edges = self._config.MONITOR_MAP_CONFIG['blacklisted_edges']

    async def start_create_monitoring_map_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: map_bruin_client_ids_to_edges_serials_and_statuses'
                          f' configured to run every'
                          f' {self._config.MONITOR_MAP_CONFIG["refresh_map_time"]} minutes')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.MONITOR_MAP_CONFIG['timezone']))
            self._logger.info(f'It will be executed now')
        try:
            self._scheduler.add_job(self.map_bruin_client_ids_to_edges_serials_and_statuses, 'interval',
                                    minutes=self._config.MONITOR_MAP_CONFIG["refresh_map_time"],
                                    next_run_time=next_run_time,
                                    replace_existing=False, id='_create_client_id_to_dict_of_serials_dict')
        except ConflictingIdError:
            self._logger.info(f'There is a recheck job scheduled for creating monitoring map already. No new job '
                              'is going to be scheduled.')

    def get_monitoring_map_cache(self):
        return self._monitoring_map_cache.copy()

    async def map_bruin_client_ids_to_edges_serials_and_statuses(self):
        self._temp_monitoring_map = {}
        self._logger.info('[triage_build_cache] Building cache...')
        try:
            edge_list_response = await self._get_edges_for_monitoring()
        except Exception:
            await self._notify_failing_rpc_request_for_edge_list()
            raise
        edge_list_response_body = edge_list_response['body']
        edge_list_response_status = edge_list_response['status']

        if edge_list_response_status not in range(200, 300):
            await self._notify_http_error_when_requesting_edge_list_from_velocloud(edge_list_response)
            raise Exception

        tasks = [
            self._process_edge_and_tickets(edge_full_id)
            for edge_full_id in edge_list_response_body
            if edge_full_id not in self._blacklisted_edges
        ]
        start_time = time.time()
        self._logger.info(f"[triage_build_cache] Processing {len(edge_list_response_body)} edges")

        await asyncio.gather(*tasks, return_exceptions=True)

        self._monitoring_map_cache = self._temp_monitoring_map
        self._temp_monitoring_map = {}

        self._logger.info(f"[triage_build_cache] Mapping finished for {len(tasks)} edges "
                          f"took {time.time() - start_time} seconds")

    async def _process_edge_and_tickets(self, edge_full_id):
        @retry(wait=wait_exponential(multiplier=self._config.MONITOR_MAP_CONFIG['multiplier'],
                                     min=self._config.MONITOR_MAP_CONFIG['min']),
               stop=stop_after_delay(self._config.MONITOR_MAP_CONFIG['stop_delay']))
        async def process_edge_and_tickets():
            async with self._semaphore:
                total_start_time = time.time()
                start_time = time.time()
                self._logger.info(f"[map-bruin-client-to-edges]Processing edge {edge_full_id}")
                edge_identifier = EdgeIdentifier(**edge_full_id)
                edge_status_response = await self._get_edge_status_by_id(edge_full_id)
                self._logger.info(f"[map-bruin-client-to-edges]Edge status retrieved {edge_full_id} "
                                  f"took {time.time() - start_time} seconds")

                edge_status_response_body = edge_status_response['body']
                edge_status_response_status = edge_status_response['status']

                if edge_status_response_status not in range(200, 300):
                    await self._notify_http_error_when_requesting_edge_status_from_velocloud(
                        edge_full_id, edge_status_response
                    )
                    return
                edge_status_data = edge_status_response_body['edge_info']

                serial_number = edge_status_data['edges']['serialNumber']

                if not serial_number:
                    self._logger.info(
                        f"[map-bruin-client-to-edges] Edge {edge_identifier} "
                        f"doesn't have any serial associated. Skipping... "
                        f"took {time.time() - start_time} seconds")
                    return

                self._logger.info(f'[map-bruin-client-to-edges] '
                                  f'Claiming Bruin client info for serial {serial_number}...')
                start_time = time.time()
                bruin_client_info_response = await self._get_bruin_client_info_by_serial(serial_number)

                self._logger.info(f'[map-bruin-client-to-edges] '
                                  f'Got Bruin client info for serial {serial_number} -> '
                                  f'{bruin_client_info_response}.'
                                  f' took {time.time() - start_time} seconds')

                bruin_client_info_response_body = bruin_client_info_response['body']
                bruin_client_info_response_status = bruin_client_info_response['status']
                if bruin_client_info_response_status not in range(200, 300):
                    err_msg = (f'Error trying to get Bruin client info from Bruin for serial {serial_number}: '
                               f'Error {bruin_client_info_response_status} - {bruin_client_info_response_body}')
                    self._logger.error(err_msg)

                    slack_message = {'request_id': uuid(), 'message': err_msg}
                    await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
                    return

                bruin_client_id = bruin_client_info_response_body.get('client_id', False)
                if not bruin_client_id:
                    self._logger.info(
                        f"[map-bruin-client-to-edges] Edge {edge_identifier} "
                        f"doesn't have any Bruin client ID associated. "
                        f'Skipping... took {time.time() - start_time} seconds')
                    return

                # Attach Bruin client info to edge_data
                edge_status_data['bruin_client_info'] = bruin_client_info_response_body

                self._logger.info(f'[map-bruin-client-to-edges]Getting management status for edge {edge_identifier}...')
                management_status_response = await self._get_management_status(edge_status_data)
                self._logger.info(f'[map-bruin-client-to-edges]Got management status for edge {edge_identifier} -> '
                                  f'{management_status_response}')

                management_status_response_body = management_status_response['body']
                management_status_response_status = management_status_response['status']
                if management_status_response_status not in range(200, 300):
                    self._logger.error(f"[map-bruin-client-to-edges]Management status is unknown for {edge_identifier}")
                    return

                if not self._is_management_status_active(management_status_response_body):
                    self._logger.info(
                        f'[map-bruin-client-to-edges]Management status is not active for {edge_identifier}. '
                        'Skipping process...')
                    return
                else:
                    self._logger.info(f'[map-bruin-client-to-edges]Management status for {edge_identifier}'
                                      ' seems active.')

                self._logger.info(
                    f"[map-bruin-client-to-edges]Edge with serial {serial_number} that belongs to Bruin customer "
                    f"{bruin_client_info_response_body} "
                    f"Has been added to the map of devices to monitor "
                    f"took {time.time() - total_start_time} seconds")

                self._temp_monitoring_map.setdefault(bruin_client_id, {})
                self._temp_monitoring_map[bruin_client_id][serial_number] = {
                    'edge_id': edge_full_id,
                    'edge_status': edge_status_data,
                }

        try:
            await process_edge_and_tickets()
        except Exception as ex:
            self._logger.error(f"Error: {edge_full_id}")
            self._metrics_repository.increment_monitoring_map_errors()

    async def _get_edges_for_monitoring(self):
        edge_list_request = {
            "request_id": uuid(),
            "body": {
                'filter': self._config.MONITOR_MAP_CONFIG['velo_filter'],
            },
        }

        edge_list = await self._event_bus.rpc_request("edge.list.request", edge_list_request, timeout=300)
        return edge_list

    async def _get_edge_status_by_id(self, edge_full_id):
        edge_status_request = {
            "request_id": uuid(),
            "body": edge_full_id,
        }

        edge_status = await self._event_bus.rpc_request("edge.status.request", edge_status_request, timeout=120)
        return edge_status

    async def _get_bruin_client_info_by_serial(self, serial_number):
        client_info_request = {
            "request_id": uuid(),
            "body": {
                "service_number": serial_number,
            },
        }

        client_info = await self._event_bus.rpc_request("bruin.customer.get.info", client_info_request, timeout=30)
        return client_info

    async def _notify_failing_rpc_request_for_edge_list(self):
        err_msg = 'Monitor Map process:An error occurred when requesting edge list from Velocloud'

        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    async def _notify_http_error_when_requesting_edge_list_from_velocloud(self, edge_list_response):
        edge_list_response_body = edge_list_response['body']
        edge_list_response_status = edge_list_response['status']

        err_msg = (
            f'Monitor Map process:Error while retrieving edge list '
            f'in {self._config.MONITOR_MAP_CONFIG["environment"].upper()} '
            f'environment:'
            f' Error {edge_list_response_status} - {edge_list_response_body}'
        )

        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    async def _notify_http_error_when_requesting_edge_status_from_velocloud(self, edge_full_id, edge_status_response):
        edge_status_response_body = edge_status_response['body']
        edge_status_response_status = edge_status_response['status']

        edge_identifier = EdgeIdentifier(**edge_full_id)
        err_msg = (
            f'Monitor Map process:Error while retrieving edge status for edge {edge_identifier} in '
            f'{self._config.MONITOR_MAP_CONFIG["environment"].upper()} environment: '
            f'Error {edge_status_response_status} - {edge_status_response_body}'
        )

        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    async def _get_management_status(self, edge_status):
        bruin_client_id = edge_status['bruin_client_info']['client_id']
        serial_number = edge_status['edges']['serialNumber']
        management_request = {
            "request_id": uuid(),
            "body": {
                "client_id": bruin_client_id,
                "status": "A",
                "service_number": serial_number
            }
        }

        management_status = await self._event_bus.rpc_request("bruin.inventory.management.status",
                                                              management_request, timeout=30)

        return management_status

    def _is_management_status_active(self, management_status) -> bool:
        return management_status in {"Pending", "Active – Gold Monitoring", "Active – Platinum Monitoring"}
