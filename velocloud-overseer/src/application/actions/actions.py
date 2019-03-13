import asyncio
import logging
import sys
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus


class Actions:
    _event_bus = None
    _velocloud_repository = None
    info_log = LoggerClient().create_logger('overseer_action_OK', sys.stdout, logging.INFO)

    def __init__(self, event_bus: EventBus, velocloud_repository):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository

    async def _send_edge_status_tasks(self):
        edges_by_enterprise = self._velocloud_repository.get_all_enterprises_edges_with_host()
        for edge in edges_by_enterprise:
            self.info_log.info(f'Edge discovered with data {edge}! Sending it to NATS edge.status.task queue')
            await self._event_bus.publish_message("edge.status.task", repr(edge))

    async def send_edge_status_task_interval(self, seconds, exec_on_start=True):
        self.info_log.info(f'Scheduled task: send edge status configured to run each {seconds} seconds')
        self.info_log.info(f'It will be executed when start = {exec_on_start}')
        if not exec_on_start:
            await asyncio.sleep(seconds)
        while True:
            self.info_log.info("Executing scheduled task: send edge status tasks")
            await self._send_edge_status_tasks()
            self.info_log.info("Executed scheduled task: send edge status tasks")
            await asyncio.sleep(seconds)
