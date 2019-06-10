from igz.packages.eventbus.eventbus import EventBus
from ast import literal_eval


class Actions:
    _configs = None
    _event_bus = None
    _velocloud_repository = None
    _logger = None
    _prometheus_repository = None

    def __init__(self, config, event_bus: EventBus, velocloud_repository, logger, prometheus_repository):

        self._configs = config
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger
        self._prometheus_repository = prometheus_repository

    async def report_edge_list(self, msg):
        decoded_msg = msg.decode('utf-8')
        msg_dict = literal_eval(decoded_msg)
        self._logger.info("Sending edge status tasks")
        edges_by_enterprise = self._velocloud_repository.get_all_enterprises_edges_with_host(msg_dict)

        status = 200
        if edges_by_enterprise is None:
            status = 500

        edge_list_response = {"request_id": msg['request_id'], "edges": edges_by_enterprise, "status": status}
        await self._event_bus.publish_message("edge.list.response", repr(edge_list_response))
        self._logger.info("Edge status tasks sent")

    async def report_edge_status(self, msg):
        decoded_msg = msg.decode('utf-8')
        msg_dict = literal_eval(decoded_msg)
        request_id = msg_dict["request_id"]
        edgeids = msg_dict["edge"]
        self._logger.info(f'Processing edge with data {msg}')

        enterprise_name = self._velocloud_repository.get_enterprise_information(edgeids['host'],
                                                                                edgeids['enterpriseId'])

        edge_status = self._velocloud_repository.get_edge_information(edgeids['host'],
                                                                      edgeids['enterpriseId'],
                                                                      edgeids['id'])

        link_status = self._velocloud_repository.get_link_information(edgeids['host'],
                                                                      edgeids['enterpriseId'],
                                                                      edgeids['id'])
        status = 200
        if enterprise_name is None or edge_status is None or link_status is None:
            status = 500

        edge_status = {"enterprise_name": enterprise_name, "edges": edge_status, "links": link_status}
        msg_dict = {"request_id": request_id, "edge_info": edge_status, "status": status}
        await self._event_bus.publish_message("edge.status.response", repr(msg_dict))
