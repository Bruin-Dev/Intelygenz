from igz.packages.eventbus.eventbus import EventBus
from apscheduler.util import undefined
from datetime import datetime


class Actions:

    def __init__(self, event_bus: EventBus, velocloud_repository, logger, prometheus_repository, scheduler):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger
        self._prometheus_repository = prometheus_repository
        self._scheduler = scheduler

    async def _send_edge_status_tasks(self):
        edges_by_enterprise = self._velocloud_repository.get_all_enterprises_edges_with_host()
        for edge in edges_by_enterprise:
            self._logger.info(f'Edge discovered with data {edge}! Sending it to NATS edge.status.task queue')
            await self._event_bus.publish_message("edge.status.task", repr(edge))

    def set_edge_status_job(self, seconds, exec_on_start=True):
        self._logger.info(f'Scheduled task: send edge status configured to run each {seconds} seconds')
        self._logger.info(f'It will be executed when start = {exec_on_start}')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now()
        self._scheduler.add_job(self._edge_status_job, 'interval', seconds=seconds, next_run_time=next_run_time)

    async def _edge_status_job(self):
        self._prometheus_repository.set_cycle_total_edges(self._sum_edges_all_hosts())
        self._logger.info("Executing scheduled task: send edge status tasks")
        await self._send_edge_status_tasks()
        self._logger.info("Executed scheduled task: send edge status tasks")

    def _sum_edges_all_hosts(self):
        return self._velocloud_repository.get_all_hosts_edge_count()

    def start_prometheus_metrics_server(self):
        self._prometheus_repository.start_prometheus_metrics_server()
