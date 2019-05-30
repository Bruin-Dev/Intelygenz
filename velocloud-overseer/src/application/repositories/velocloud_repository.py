class VelocloudRepository:
    _config = None
    _clients = None
    _velocloud_client = None
    _logger = None

    def __init__(self, config, velocloud_client):
        self._config = config.VELOCLOUD_CONFIG
        self._velocloud_client = velocloud_client

    def connect_to_all_servers(self):
        self._velocloud_client.instantiate_and_connect_clients()

    def get_all_enterprises_edges_with_host(self):
        return self._velocloud_client.get_all_enterprises_edges_with_host()

    def get_all_hosts_edge_count(self):
        return self._velocloud_client.get_all_hosts_edge_count()
