class VelocloudRepository:
    _config = None
    _clients = None
    _velocloud_client = None
    _logger = None

    def __init__(self, config, logger, velocloud_client):
        self._config = config.VELOCLOUD_CONFIG
        self._clients = list()
        self._velocloud_client = velocloud_client
        self._logger = logger

    def connect_to_all_servers(self):
        self._clients = self._velocloud_client.instantiate_and_connect_clients()

    def get_all_enterprises_edges_with_host(self):
        edges_by_enterprise_and_host = self._velocloud_client.get_all_enterprises_edges_with_host(self._clients,
                                                                                                  self._logger)
        return edges_by_enterprise_and_host

    def get_all_hosts_edge_count(self):
        sum = self._velocloud_client.get_all_hosts_edge_count(self._clients, self._logger)
        return sum
