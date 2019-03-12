import asyncio


class Actions:
    _event_bus = None
    _velocloud_repository = None

    def __init__(self, event_bus, velocloud_repository):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository

    async def _send_edge_status_tasks(self):
        edges_by_enterprise = self._velocloud_repository.get_all_enterprises_edges_with_host()
        for edge in edges_by_enterprise:
            print(f'Edge discovered with data {edge}! Sending it to NATS edge.status.task queue')
            await self._event_bus.publish_message("edge.status.task", repr(edge))

    async def send_edge_status_task_interval(self, seconds, exec_on_start=True):
        if not exec_on_start:
            await asyncio.sleep(seconds)
        while True:
            print("Executing scheduled task: send edge status tasks")
            await self._send_edge_status_tasks()
            await asyncio.sleep(seconds)
