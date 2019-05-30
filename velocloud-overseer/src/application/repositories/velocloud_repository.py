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
        self._logger.info('Instantiating and connecting clients in overseer')
        self._velocloud_client.instantiate_and_connect_clients()

    def get_all_enterprises_edges_with_host(self):
        self._logger.info('Getting all enterprises edges with host')
        return self._velocloud_client.get_all_enterprises_edges_with_host()

    def get_all_hosts_edge_count(self):
        self._logger.info('Getting edge count from host')
        return self._velocloud_client.get_all_hosts_edge_count()
