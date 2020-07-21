import json
import asyncio

from time import perf_counter
from datetime import datetime
from pytz import timezone
from apscheduler.util import undefined
from shortuuid import uuid
from application.repositories import EdgeIdentifier

from igz.packages.eventbus.eventbus import EventBus


class EdgeMonitoring:

    def __init__(self, event_bus: EventBus, logger, prometheus_repository, scheduler, velocloud_repository, config):
        self._event_bus = event_bus
        self._logger = logger
        self._prometheus_repository = prometheus_repository
        self._scheduler = scheduler
        self._config = config
        self._semaphore = asyncio.BoundedSemaphore(self._config.SITES_MONITOR_CONFIG['semaphore'])
        self._edges_cache = set()
        self._status_cache = dict()
        self._velocloud_repository = velocloud_repository

    async def _edge_monitoring_process(self):
        self._logger.info("Starting velocloud edge monitoring process")
        await self._process_all_edges()

    async def start_edge_monitor_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: edge monitoring process configured to run each '
                          f'{self._config.SITES_MONITOR_CONFIG["monitoring_seconds"]} seconds')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.SITES_MONITOR_CONFIG['timezone']))
            self._logger.info(f'It will be executed now')

        self._scheduler.add_job(self._edge_monitoring_process, 'interval',
                                seconds=self._config.SITES_MONITOR_CONFIG['monitoring_seconds'],
                                next_run_time=next_run_time,
                                replace_existing=False, id='_edge_monitoring_process')

    async def _process_all_edges(self):
        try:
            edge_list_response = await self._velocloud_repository.get_edges()
            edge_list_response_status = edge_list_response['status']
            if edge_list_response_status not in range(200, 300):
                return
            edge_list = edge_list_response['body']
            self._logger.info(f'Edge list received from event bus')
            edge_status_requests = [
                {'request_id': edge_list_response["request_id"], 'body': edge} for edge in edge_list]
            self._prometheus_repository.set_cycle_total_edges(len(edge_status_requests))
            edge_set = {EdgeIdentifier(**edge) for edge in edge_list}
            if self._edges_cache:
                edges_missing_set = self._edges_cache - edge_set
                for edge in edges_missing_set:
                    self._prometheus_repository.dec(self._status_cache[edge]['cache_edge'])
            self._logger.info(f'Splitting and sending edges to the event bus')
            self._edges_cache = edge_set
            tasks = [
                self._process_edge(request)
                for request in edge_status_requests
            ]

            start = perf_counter()
            await asyncio.gather(*tasks, return_exceptions=True)
            stop = perf_counter()

            self._logger.info(f"[_process_all_edges] Process edges in minutes: "
                              f"{(stop - start) // 60}")
        except Exception as e:
            self._logger.error(f"Error: Exception in process all edges: {e}")

    async def _process_edge(self, request):
        try:
            async with self._semaphore:
                self._logger.info(f"Getting edge status for request: {request}")
                edge = await self._event_bus.rpc_request("edge.status.request", request, timeout=10)
                self._logger.info(f'Edge received from event bus: {edge}')
                if edge["status"] not in range(200, 300):
                    self._logger.info(f"Not edge status for {request}")
                    return
                self._logger.info(f"Process call edge: {edge}")

                edge_identifier = EdgeIdentifier(**edge['body']['edge_id'])
                if edge_identifier not in self._status_cache:
                    self._prometheus_repository.inc(edge['body']['edge_info'])
                else:
                    if self._status_cache[edge_identifier]['cache_edge']['edges']['edgeState'] != \
                            edge['body']['edge_info']['edges']['edgeState']:
                        self._prometheus_repository.update_edge(edge['body']['edge_info'],
                                                                self._status_cache[edge_identifier]['cache_edge'])

                    for link, cache_link in zip(edge['body']['edge_info']['links'],
                                                self._status_cache[edge_identifier]['cache_edge']['links']):
                        if link['link']['state'] != cache_link['link']['state']:
                            self._prometheus_repository.update_link(edge['body']['edge_info'], link,
                                                                    self._status_cache[edge_identifier]['cache_edge'],
                                                                    cache_link)

                cache_data = {"request_id": edge["request_id"], "cache_edge": edge['body']['edge_info']}
                self._status_cache[edge_identifier] = cache_data
        except Exception as e:
            self._logger.error(f"Error: Exception in process one edge: {e}")

    def start_prometheus_metrics_server(self):
        self._prometheus_repository.start_prometheus_metrics_server()
