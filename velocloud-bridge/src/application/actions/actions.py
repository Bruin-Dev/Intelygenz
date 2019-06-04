from igz.packages.eventbus.eventbus import EventBus
import velocloud
import json
from ast import literal_eval
from http import HTTPStatus


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

    async def _send_edge_status_tasks(self, msg):
        edges_by_enterprise = self._velocloud_repository.get_all_enterprises_edges_with_host()
        msg_dict = {"request_id": msg['request_id'], "edges": edges_by_enterprise, "status": HTTPStatus.OK}
        await self._event_bus.publish_message("edge.list.response", repr(msg_dict))

    async def report_edge_list(self, msg):
        decoded_msg = msg.decode('utf-8')
        msg_dict = literal_eval(decoded_msg)
        self._prometheus_repository.set_cycle_total_edges(self._sum_edges_all_hosts())
        self._logger.info("Executing scheduled task: send edge status tasks")
        await self._send_edge_status_tasks(msg_dict)
        self._logger.info("Executed scheduled task: send edge status tasks")

    def _sum_edges_all_hosts(self):
        return self._velocloud_repository.get_all_hosts_edge_count()

    def _process_edge(self, edgeids):
        edge_status = None
        try:
            edge_status = self._velocloud_repository.get_edge_information(edgeids['host'],
                                                                          edgeids['enterpriseId'],
                                                                          edgeids['id'])
        except velocloud.rest.ApiException as e:
            self._logger.exception(e)
        return edge_status

    def _process_link(self, edgeids):
        link_status = None
        try:
            link_status = self._velocloud_repository.get_link_information(edgeids['host'],
                                                                          edgeids['enterpriseId'],
                                                                          edgeids['id'])
        except velocloud.rest.ApiException as e:
            self._logger.exception(e)
        return link_status

    async def report_edge_status(self, msg):
        request_id = json.loads(msg['request_id'].decode("utf-8").replace("\\", ' ').replace("'", '"'))
        edgeids = json.loads(msg['edge'].decode("utf-8").replace("\\", ' ').replace("'", '"'))
        self._logger.info(f'Processing edge with data {msg}')
        edge_status = self._process_edge(edgeids)
        enterprise_info = self._velocloud_repository.get_enterprise_information(edgeids['host'],
                                                                                edgeids['enterpriseId'])

        link_status = self._process_link(edgeids)

        self._prometheus_repository.inc(edgeids['enterpriseId'], enterprise_info._name, edge_status._edgeState,
                                        link_status)
        edge_status = {"edges": edge_status, "links": link_status}
        msg_dict = {"request_id": request_id, "edge_info": edge_status, "status": HTTPStatus.OK}
        await self._event_bus.publish_message("edge.status.response", repr(msg_dict))

    def start_prometheus_metrics_server(self):
        self._prometheus_repository.start_prometheus_metrics_server()

    async def reset_counter(self):
        await self._prometheus_repository.reset_counter()
