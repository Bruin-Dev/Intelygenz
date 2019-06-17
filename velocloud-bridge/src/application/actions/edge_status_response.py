from igz.packages.eventbus.eventbus import EventBus
import json


class ReportEdgeStatus:

    def __init__(self, config, event_bus: EventBus, velocloud_repository, logger):
        self._configs = config
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def report_edge_status(self, msg):
        msg_dict = json.loads(msg)
        request_id = msg_dict["request_id"]
        edgeids = msg_dict["edge"]
        self._logger.info(f'Processing edge with data {msg_dict}')

        enterprise_name = self._velocloud_repository.get_enterprise_information(edgeids)

        edge_status = self._velocloud_repository.get_edge_information(edgeids).to_dict()

        link_status = self._velocloud_repository.get_link_information(edgeids).to_dict()
        status = 200
        if enterprise_name is None or edge_status is None or link_status is None:
            status = 500

        edge_status = {"enterprise_name": enterprise_name, "edges": edge_status, "links": link_status}
        msg_dict = {"request_id": request_id, "edge_info": edge_status, "status": status}
        await self._event_bus.publish_message("edge.status.response", json.dumps(msg_dict))
