from igz.packages.eventbus.eventbus import EventBus
import velocloud
import json


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
        edgeids = json.loads(msg.decode("utf-8").replace("\\", ' ').replace("'", '"'))
        self._logger.info(f'Processing edge with data {msg}')
        edge_status = self._process_edge(edgeids)
        enterprise_info = self._velocloud_repository.get_enterprise_information(edgeids['host'],
                                                                                edgeids['enterpriseId'])

        link_status = self._process_link(edgeids)

        if edge_status._edgeState == 'CONNECTED':
            self._logger.info('Edge seems OK, sending it to topic edge.status.ok')
            topic = "edge.status.ok"
        else:
            self._logger.error('Edge seems KO, failure! Sending it to topic edge.status.ko')
            topic = "edge.status.ko"
        self._prometheus_repository.inc(edgeids['enterpriseId'], enterprise_info._name, edge_status._edgeState,
                                        link_status)
        edge_status = {"edges": edge_status, "links": link_status}

        await self._event_bus.publish_message(topic, repr(edge_status))

    def start_prometheus_metrics_server(self):
        self._prometheus_repository.start_prometheus_metrics_server()

    async def reset_counter(self):
        await self._prometheus_repository.reset_counter()
