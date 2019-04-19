import asyncio
from igz.packages.eventbus.eventbus import EventBus


class Actions:
    _event_bus = None
    _velocloud_repository = None
    _logger = None
    _edge_gauge = None

    def __init__(self, event_bus: EventBus, velocloud_repository, logger, edge_gauge):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger
        self._edge_gauge = edge_gauge

    async def _send_edge_status_tasks(self):
        edges_by_enterprise = self._velocloud_repository.get_all_enterprises_edges_with_host()
        for edge in edges_by_enterprise:
            self._edge_gauge.inc()
            self._logger.info(f'Edge discovered with data {edge}! Sending it to NATS edge.status.task queue')
            await self._event_bus.publish_message("edge.status.task", repr(edge))

    async def send_edge_status_task_interval(self, seconds, exec_on_start=True):
        self._logger.info(f'Scheduled task: send edge status configured to run each {seconds} seconds')
        self._logger.info(f'It will be executed when start = {exec_on_start}')
        if not exec_on_start:
            await asyncio.sleep(seconds)
        while True:
            self._logger.info("Executing scheduled task: send edge status tasks")
            await self._send_edge_status_tasks()
            self._logger.info("Executed scheduled task: send edge status tasks")
            await asyncio.sleep(seconds)
            self._edge_gauge.set(0)
