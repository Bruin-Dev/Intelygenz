import velocloud


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

    def get_edge_information(self, host, enterpriseid, edgeid):
        edge_information = self._velocloud_client.get_edge_information(self._clients, self._logger,
                                                                       host, enterpriseid, edgeid)
        return edge_information

    def get_link_information(self, host, enterpriseid, edgeid):
        link_information = self._velocloud_client.get_link_information(self._clients, self._logger,
                                                                       host, enterpriseid, edgeid)
        return link_information

    def get_enterprise_information(self, host, enterpriseid):
        enterprise_information = self._velocloud_client.get_enterprise_information(self._clients, self._logger,
                                                                                   host, enterpriseid)
        return enterprise_information
