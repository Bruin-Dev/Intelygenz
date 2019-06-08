from igz.packages.eventbus.eventbus import EventBus
from apscheduler.util import undefined
from datetime import datetime
from shortuuid import uuid
from ast import literal_eval


class EdgeMonitoring:

    def __init__(self, event_bus: EventBus, logger, prometheus_repository, scheduler, edge_repository,
                 status_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._prometheus_repository = prometheus_repository
        self._scheduler = scheduler
        self._edge_repository = edge_repository
        self._status_repository = status_repository

    async def _edge_monitoring_process(self):
        self._logger.info("Starting velocloud edge monitoring process")
        # if "IDLE" in self._status_repository.get_status():
        self._logger.info("IDLE status: asking edge list. Orchestrator status = REQUESTING_VELOCLOUD_EDGES...")
        self._status_repository.set_status("REQUESTING_VELOCLOUD_EDGES")
        await self._request_edges(uuid())
        self._status_repository.set_edges_to_process(9000)
        self._logger.info("Sending edge status tasks. Orchestrator status = PROCESSING_VELOCLOUD_EDGES...")
        self._status_repository.set_status("PROCESSING_VELOCLOUD_EDGES")

    async def start_edge_monitor_job(self, seconds, exec_on_start=True):
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
        self._logger.info(f'{egde_status_requests}')
        self._logger.info(f'Sending them to the event bus')
        for request in egde_status_requests:
            await self._event_bus.publish_message("edge.status.request", repr(request))
        self._logger.info(f'Requests sent')

    def receive_edge(self, msg):
        self._logger.info(f'Edge received from event bus')
        decoded_msg = msg.decode('utf-8')
        self._logger.info(f'{decoded_msg}')

    def start_prometheus_metrics_server(self):
        self._prometheus_repository.start_prometheus_metrics_server()
