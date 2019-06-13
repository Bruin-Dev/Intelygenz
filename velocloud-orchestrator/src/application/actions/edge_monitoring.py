from igz.packages.eventbus.eventbus import EventBus
from apscheduler.util import undefined
from datetime import datetime
from shortuuid import uuid
from ast import literal_eval
import json


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

            cycle_seconds = self._config.ORCHESTRATOR_CONFIG['monitoring_seconds']
            last_cycle_timestamp = self._status_repository.get_last_cycle_timestamp()

            if datetime.timestamp(datetime.now()) - last_cycle_timestamp > cycle_seconds:
                self._status_repository.set_status("IDLE")
                self._logger.info('Time since last cycle exceeds threshold, triggering process again')
            else:
                self._logger.error('Edge monitoring process won\'t be triggered again')
        if "IDLE" in self._status_repository.get_status():
            self._logger.info("IDLE status: asking edge list. Orchestrator status = REQUESTING_VELOCLOUD_EDGES...")
            self._status_repository.set_status("REQUESTING_VELOCLOUD_EDGES")
            self._status_repository.set_edges_processed(0)
            self._status_repository.set_last_cycle_timestamp(datetime.timestamp(datetime.now()))
            await self._request_edges(uuid())
            self._logger.info("Sending edge status tasks. Orchestrator status = PROCESSING_VELOCLOUD_EDGES...")
            self._status_repository.set_status("PROCESSING_VELOCLOUD_EDGES")

    async def start_edge_monitor_job(self, exec_on_start=True):
        seconds = self._config.ORCHESTRATOR_CONFIG['monitoring_seconds']
        self._logger.info(f'Scheduled task: edge monitoring process configured to run each {seconds} seconds')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now()
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._edge_monitoring_process, 'interval', seconds=seconds, next_run_time=next_run_time,
                                replace_existing=True, id='_edge_monitoring_process')

    async def _request_edges(self, request_id):
        msg = dict(request_id=request_id, filter=[])
        await self._event_bus.publish_message("edge.list.request", repr(msg))

    async def receive_edge_list(self, msg):
        self._logger.info(f'Edge list received from event bus')
        decoded_msg = literal_eval(msg.decode('utf-8'))
        egde_status_requests = [dict(request_id=decoded_msg["request_id"], edge=edge) for edge in decoded_msg["edges"]]
        self._status_repository.set_edges_to_process(len(egde_status_requests))
        self._logger.info(f'{egde_status_requests}')
        self._logger.info(f'Sending them to the event bus')
        for request in egde_status_requests:
            await self._event_bus.publish_message("edge.status.request", repr(request))
        self._logger.info(f'Requests sent')

    async def receive_edge(self, msg):
        self._logger.info(f'Edge received from event bus')
        edges_processed = self._status_repository.get_edges_processed()
        edges_to_process = self._status_repository.get_edges_to_process()
        edges_processed = edges_processed + 1
        self._status_repository.set_edges_processed(edges_processed)
        self._logger.info(f'Edges processed: {edges_processed} / {edges_to_process}')
        if edges_processed == edges_to_process:
            self._logger.info("All edges processed, starting the cycle again")
            self._status_repository.set_status("IDLE")
            await self._edge_monitoring_process()

    def start_prometheus_metrics_server(self):
        self._prometheus_repository.start_prometheus_metrics_server()
