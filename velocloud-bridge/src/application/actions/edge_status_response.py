from igz.packages.eventbus.eventbus import EventBus
from datetime import datetime, timedelta, timezone


class ReportEdgeStatus:

    def __init__(self, config, event_bus: EventBus, velocloud_repository, logger):
        self._configs = config
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def report_edge_status(self, msg: dict):
        request_id = msg["request_id"]
        edgeids = msg["edge"]
        self._logger.info(f'Processing edge with data {msg}')

        enterprise_name = self._velocloud_repository.get_enterprise_information(edgeids)

        edge_status = self._velocloud_repository.get_edge_information(edgeids)

        interval = {
                    "start": (datetime.now() - timedelta(hours=8)).replace(tzinfo=timezone.utc).isoformat()
                   }
        if "interval" in msg.keys():
            interval = msg["interval"]
        link_status = self._velocloud_repository.get_link_information(edgeids, interval)
        status = 200
        if enterprise_name is None or edge_status is None or link_status is None:
            status = 204
        if isinstance(enterprise_name, Exception) or isinstance(edge_status, Exception) or isinstance(link_status,
                                                                                                      Exception):
            status = 500
        edge_status = {"enterprise_name": enterprise_name, "edges": edge_status, "links": link_status}
        edge_response = {"request_id": request_id, "edge_id": edgeids, "edge_info": edge_status, "status": status}
        await self._event_bus.publish_message(msg['response_topic'], edge_response)
