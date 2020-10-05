import asyncio

from shortuuid import uuid
from typing import Dict
from time import perf_counter
from datetime import datetime
from pytz import timezone
from apscheduler.util import undefined
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

    def start_prometheus_metrics_server(self):
        self._prometheus_repository.start_prometheus_metrics_server()

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
            edge_list_response = await self._velocloud_repository.get_all_links_with_edge_info()
            edge_list_response_status = edge_list_response['status']
            if edge_list_response_status not in range(200, 300):
                return
            edge_links_list = edge_list_response['body']
            self._logger.info(f'Edge list received from event bus')

            edges_with_links: Dict[EdgeIdentifier, dict] = \
                self._velocloud_repository.group_links_by_edge(edge_links_list)
            edge_identifiers = set(edges_with_links)
            self._prometheus_repository.set_cycle_total_edges(len(edge_identifiers))
            if self._edges_cache:
                edges_missing_set = self._edges_cache - edge_identifiers
                for edge in edges_missing_set:
                    self._prometheus_repository.dec(self._status_cache[edge]['cache_edge'])
            self._logger.info(f'Splitting and sending edges to the event bus')
            self._edges_cache = edge_identifiers

            tasks = [
                self._process_edge(edge_identifier, edge)
                for edge_identifier, edge in edges_with_links.items()
            ]
            start = perf_counter()
            await asyncio.gather(*tasks, return_exceptions=True)
            stop = perf_counter()

            self._logger.info(f"[_process_all_edges] Process edges in minutes: "
                              f"{round((stop - start) / 60, 2)}")
        except Exception as e:
            self._logger.error(f"Error: Exception in process all edges: {e}")

    async def _process_edge(self, edge_identifier, edge):
        try:
            async with self._semaphore:
                self._logger.info(f"Processing edge links: {edge_identifier} with {len(edge['links'])} links")
                if len(edge['links']) == 0:
                    self._logger.info(f"Edge with links: {edge_identifier} has not links")
                    return
                if edge_identifier not in self._status_cache:
                    self._prometheus_repository.inc(edge)
                else:
                    if self._status_cache[edge_identifier]['cache_edge']['edgeState'] != edge['edgeState']:
                        self._prometheus_repository.update_edge(edge, self._status_cache[edge_identifier]['cache_edge'])

                    for link, cache_link in zip(edge['links'],
                                                self._status_cache[edge_identifier]['cache_edge']['links']):
                        if link['linkState'] != cache_link['linkState']:
                            self._prometheus_repository.update_link(edge, link,
                                                                    self._status_cache[edge_identifier]['cache_edge'],
                                                                    cache_link)

                cache_data = {"cache_edge": edge}
                self._status_cache[edge_identifier] = cache_data

        except Exception as e:
            self._logger.error(f"Error: Exception in process one edge link: {e}")
