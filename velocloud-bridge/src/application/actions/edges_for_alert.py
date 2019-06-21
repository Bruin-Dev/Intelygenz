import json
from concurrent.futures import ThreadPoolExecutor

import asyncio

from igz.packages.eventbus.eventbus import EventBus


class EdgesForAlert:

    def __init__(self, event_bus: EventBus, velocloud_repository, logger):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def report_edge_list(self, msg):
        executor = ThreadPoolExecutor(max_workers=10)
        loop = asyncio.get_event_loop()
        futures = []

        msg_dict = json.loads(msg)
        self._logger.info("Sending edge list for alerts")
        edges_by_enterprise = self._velocloud_repository.get_all_enterprises_edges_with_host(msg_dict)
        for edge_id in edges_by_enterprise:
            futures.append(loop.run_in_executor(executor, self._velocloud_repository.get_alert_information, edge_id))
        asyncio.ensure_future(self._gather_and_send_edge_list(futures, msg_dict['request_id']), loop=loop)

    async def _gather_and_send_edge_list(self, futures_edges, request_id):
        data = await asyncio.wait(futures_edges)
        edges_data = []
        for edge_data in data[0]:
            edges_data.append(edge_data.result())
        status = 200
        if len(edges_data) == 0:
            status = 500
        edge_list_response = {"request_id": request_id,
                              "edges": edges_data,
                              "status": status}
        await self._event_bus.publish_message("alert.response.all.edges", json.dumps(edge_list_response, default=str))
        self._logger.info("Edges for alert sent")
