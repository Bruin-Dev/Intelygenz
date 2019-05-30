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

    def get_edge_information(self, host, enterpriseid, edgeid):
        return self._velocloud_client.get_edge_information(host, enterpriseid, edgeid)

    def get_link_information(self, host, enterpriseid, edgeid):
        return self._velocloud_client.get_link_information(host, enterpriseid, edgeid)

    def get_enterprise_information(self, host, enterpriseid):
        return self._velocloud_client.get_enterprise_information(host, enterpriseid)
