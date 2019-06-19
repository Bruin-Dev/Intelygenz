import json
from igz.packages.eventbus.eventbus import EventBus


class EdgesForAlert:

    def __init__(self, event_bus: EventBus, velocloud_repository, logger):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def report_edge_list(self, msg):
        msg_dict = json.loads(msg)
        self._logger.info("Sending edge list for alerts")
        edges_by_enterprise = self._velocloud_repository.get_all_enterprises_edges_with_host(msg_dict)

        status = 200
        if edges_by_enterprise is None:
            status = 500

        edge_list_response = dict(request_id=msg_dict['request_id'], edges=[], status=status)

        for edge_id in edges_by_enterprise:
            edge = self._velocloud_repository.get_edge_information(edge_id).to_dict()
            enterprise = self._velocloud_repository.get_enterprise_information(edge_id)
            list_item = dict(edge=edge, enterprise=enterprise)
            edge_list_response["edges"].append(list_item)
        await self._event_bus.publish_message("alert.response.all.edges", json.dumps(edge_list_response, default=str))
