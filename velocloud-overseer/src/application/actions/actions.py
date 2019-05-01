import asyncio
from igz.packages.eventbus.eventbus import EventBus


class Actions:
    _event_bus = None
    _velocloud_repository = None
    _logger = None
    _prometheus_repository = None

    def __init__(self, event_bus: EventBus, velocloud_repository, logger, prometheus_repository):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger
        self._prometheus_repository = prometheus_repository

    async def _send_edge_status_tasks(self):
        edges_by_enterprise = self._velocloud_repository.get_all_enterprises_edges_with_host()
        for edge in edges_by_enterprise:
            self._logger.info(f'Edge discovered with data {edge}! Sending it to NATS edge.status.task queue')
            await self._event_bus.publish_message("edge.status.task", repr(edge))

    async def send_edge_status_task_interval(self, seconds, exec_on_start=True):
        self._logger.info(f'Scheduled task: send edge status configured to run each {seconds} seconds')
        self._logger.info(f'It will be executed when start = {exec_on_start}')
        if not exec_on_start:
            await asyncio.sleep(seconds)
        while True:
            self._prometheus_repository.inc()
            self._logger.info("Executing scheduled task: send edge status tasks")
            await self._send_edge_status_tasks()
            self._logger.info("Executed scheduled task: send edge status tasks")
            await asyncio.sleep(seconds)
            self._prometheus_repository.reset_counter()

    def start_prometheus_metrics_server(self):
        self._prometheus_repository.start_prometheus_metrics_server()
