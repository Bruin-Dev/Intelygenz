import json
from igz.packages.eventbus.eventbus import EventBus


class ReportEdgeList:

    def __init__(self, config, event_bus: EventBus, velocloud_repository, logger):
        self._configs = config
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def report_edge_list(self, msg):
        msg_dict = json.loads(msg)
        self._logger.info("Sending edge list")
        edges_by_enterprise = self._velocloud_repository.get_all_enterprises_edges_with_host(msg_dict)

        status = 200
        if edges_by_enterprise is None:
            status = 500

        edge_list_response = {"request_id": msg_dict['request_id'], "edges": edges_by_enterprise, "status": status}
        await self._event_bus.publish_message("edge.list.response", json.dumps(edge_list_response))
        self._logger.info("Edge list sent")
