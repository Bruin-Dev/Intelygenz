from igz.packages.eventbus.eventbus import EventBus
from apscheduler.util import undefined
from datetime import datetime


class Actions:

    def __init__(self, event_bus: EventBus, logger, prometheus_repository, scheduler):
        self._event_bus = event_bus
        self._logger = logger
        self._prometheus_repository = prometheus_repository
        self._scheduler = scheduler

    def set_edge_status_job(self, seconds, exec_on_start=True):
        self._logger.info(f'Scheduled task: send edge status configured to run each {seconds} seconds')
        self._logger.info(f'It will be executed when start = {exec_on_start}')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now()
        self._scheduler.add_job(self._edge_status_job, 'interval', seconds=seconds, next_run_time=next_run_time,
                                replace_existing=True, id='edge_status_job')

    async def _edge_status_job(self):
        # self._prometheus_repository.set_cycle_total_edges(self._sum_edges_all_hosts())
        self._logger.info("Executing scheduled task: send edge status tasks")
        self._logger.info("Executed scheduled task: send edge status tasks")

    def start_prometheus_metrics_server(self):
        self._prometheus_repository.start_prometheus_metrics_server()
