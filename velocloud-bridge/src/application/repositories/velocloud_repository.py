class VelocloudRepository:
    _config = None
    _clients = None
    _velocloud_client = None
    _logger = None

    def __init__(self, config, logger, velocloud_client):
        self._config = config.VELOCLOUD_CONFIG
        self._logger = logger
        self._velocloud_client = velocloud_client

    def connect_to_all_servers(self):
        self._logger.info('Instantiating and connecting clients in velocloud bridge')
        self._velocloud_client.instantiate_and_connect_clients()

    def get_all_enterprises_edges_with_host(self, msg):
        self._logger.info('Getting all enterprises edges with host')
        edges_by_enterprise = self._velocloud_client.get_all_enterprises_edges_with_host()
        if len(msg['filter']) > 0:
            edges_by_enterprise = [edge for edge in edges_by_enterprise
                                   for filter_edge in msg['filter']
                                   if edge['host'] == filter_edge['host']
                                   if edge['enterprise_id'] in filter_edge['enterprise_ids'] or len(
                                    filter_edge['enterprise_ids']) is 0]

        return edges_by_enterprise

    def get_edge_information(self, edge):
        return self._velocloud_client.get_edge_information(edge)

    def get_link_information(self, edge):
        self._logger.info(f'Getting link information from edge:{edge["edge_id"]} in '
                          f'enterprise:{edge["enterprise_id"]} from host:{edge["host"]}')
        return self._velocloud_client.get_link_information(edge)

    def get_enterprise_information(self, edge):
        return self._velocloud_client.get_enterprise_information(edge)._name

    def get_alert_information(self, edge):
        return {
            "host": edge['host'],
            "edge": self._velocloud_client.get_edge_information(edge).to_dict(),
            "enterprise": self._velocloud_client.get_enterprise_information(edge)._name
        }
