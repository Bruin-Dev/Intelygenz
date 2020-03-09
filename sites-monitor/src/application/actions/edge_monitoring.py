import json
from datetime import datetime
from apscheduler.util import undefined
from pytz import timezone
from shortuuid import uuid

from igz.packages.eventbus.eventbus import EventBus


class EdgeMonitoring:

    def __init__(self, event_bus: EventBus, logger, prometheus_repository, scheduler, edge_repository,
                 status_repository, config):
        self._event_bus = event_bus
        self._logger = logger
        self._prometheus_repository = prometheus_repository
        self._scheduler = scheduler
        self._edge_repository = edge_repository
        self._status_repository = status_repository
        self._config = config

    async def _edge_monitoring_process(self):
        self._logger.info("Starting velocloud edge monitoring process")
        if "PROCESSING_VELOCLOUD_EDGES" in self._status_repository.get_status():
            edges_processed = self._status_repository.get_edges_processed()
            edges_to_process = self._status_repository.get_edges_to_process()
            self._logger.error(f'There\'s still edges to be processed: {edges_processed} / {edges_to_process}')

            cycle_seconds = self._config.SITES_MONITOR_CONFIG['monitoring_seconds']
            current_cycle_timestamp = self._status_repository.get_current_cycle_timestamp()

            if datetime.timestamp(datetime.now()) - current_cycle_timestamp > cycle_seconds:
                self._status_repository.set_status("IDLE")
                self._logger.info('Time since current cycle exceeds threshold, triggering process again')
            else:
                self._logger.error('Edge monitoring process won\'t be triggered again')
        if "IDLE" in self._status_repository.get_status():
            self._logger.info("IDLE status: asking edge list. Sites Monitor status = REQUESTING_VELOCLOUD_EDGES...")
            self._status_repository.set_status("REQUESTING_VELOCLOUD_EDGES")
            self._status_repository.set_edges_processed(0)
            self._status_repository.set_current_cycle_timestamp(datetime.timestamp(datetime.now()))
            await self._process_all_edges(uuid())
            self._logger.info("Sending edge status tasks. Sites Monitor status = PROCESSING_VELOCLOUD_EDGES...")
            self._status_repository.set_status("PROCESSING_VELOCLOUD_EDGES")

    async def start_edge_monitor_job(self, exec_on_start=False):
        seconds = self._config.SITES_MONITOR_CONFIG['monitoring_seconds']
        self._logger.info(f'Scheduled task: edge monitoring process configured to run each {seconds} seconds')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.SITES_MONITOR_CONFIG['timezone']))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._edge_monitoring_process, 'interval', seconds=seconds, next_run_time=next_run_time,
                                replace_existing=True, id='_edge_monitoring_process')

    async def _process_all_edges(self, request_id):
        msg = {
            'request_id': request_id,
            'body': {'filter': {}}
        }
        self._status_repository.set_current_cycle_request_id(request_id)

        edge_list = await self._event_bus.rpc_request("edge.list.request", msg, timeout=200)
        self._logger.info(f'Edge list received from event bus')
        edge_status_requests = [
            {'request_id': edge_list["request_id"], 'body': edge} for edge in edge_list["body"]]
        self._prometheus_repository.set_cycle_total_edges(len(edge_status_requests))
        self._status_repository.set_edges_to_process(len(edge_status_requests))

        cache_edge_list = self._edge_repository.get_last_edge_list()
        if cache_edge_list is not None:
            decoded_cache_edge_list = json.loads(cache_edge_list)
            if len(decoded_cache_edge_list) != len(edge_list["body"]):
                for cache_edge in decoded_cache_edge_list:
                    if cache_edge not in edge_list['body']:
                        cache_edge_info = json.loads(self._edge_repository.get_edge(str(cache_edge)))
                        self._prometheus_repository.dec(cache_edge_info["cache_edge"])

        self._edge_repository.set_current_edge_list(json.dumps(edge_list["body"]))

        self._logger.info(f'Splitting and sending edges to the event bus')

        for request in edge_status_requests:
            edge = await self._event_bus.rpc_request("edge.status.request", request, timeout=10)
            if edge["status"] in range(200, 300):
                await self._process_edge(edge)
                self._logger.info(f'Requests sent')
            else:
                self._logger.info(f"Not edge status for {request}")

    async def _process_edge(self, edge):
        self._logger.info(f'Edge received from event bus')
        edges_processed = self._status_repository.get_edges_processed()
        edges_to_process = self._status_repository.get_edges_to_process()
        edges_processed = edges_processed + 1
        self._status_repository.set_edges_processed(edges_processed)

        cache_edge = self._edge_repository.get_edge(str(edge['body']['edge_id']))
        if cache_edge is None:
            self._prometheus_repository.inc(edge['body']['edge_info'])
        else:
            cache_edge_data = json.loads(cache_edge)
            if cache_edge_data['cache_edge']['edges']['edgeState'] != edge['body']['edge_info']['edges']['edgeState']:
                self._prometheus_repository.update_edge(edge['body']['edge_info'], cache_edge_data['cache_edge'])

            for link, cache_link in zip(edge['body']['edge_info']['links'], cache_edge_data['cache_edge']['links']):
                if link['link']['state'] != cache_link['link']['state']:
                    self._prometheus_repository.update_link(edge['body']['edge_info'], link,
                                                            cache_edge_data['cache_edge'], cache_link)

        cache_data = {"request_id": edge["request_id"], "cache_edge": edge['body']['edge_info']}
        self._edge_repository.set_edge(edge['body']['edge_id'], json.dumps(cache_data))
        self._logger.info(f'Edges processed: {edges_processed} / {edges_to_process}')
        if edges_processed == edges_to_process:
            self._logger.info("All edges processed, starting the cycle again")
            self._status_repository.set_status("IDLE")
            await self._edge_monitoring_process()

    def start_prometheus_metrics_server(self):
        self._prometheus_repository.start_prometheus_metrics_server()
