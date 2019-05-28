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
        self._clients = self._velocloud_client._instantiate_and_connect_clients()

    def get_client_by_host(self, host):
        host_client = [client
                       for client in self._clients
                       if host in
                       client.api_client.base_path][0]
        return host_client

    def get_edge_information(self, host, enterpriseid, edgeid):
        target_host_client = self.get_client_by_host(host)
        edgeids = {"enterpriseId": enterpriseid, "id": edgeid}
        try:
            edge_information = target_host_client.edgeGetEdge(body=edgeids)
            return edge_information
        except velocloud.rest.ApiException as e:
            self._logger.exception(e)
            if e.status == 0:
                self._logger.error('Error, could not authenticate')

    def get_link_information(self, host, enterpriseid, edgeid):
        target_host_client = self.get_client_by_host(host)
        edgeids = {"enterpriseId": enterpriseid, "id": edgeid}
        try:
            link_information = target_host_client.metricsGetEdgeLinkMetrics(body=edgeids)
            return link_information
        except velocloud.rest.ApiException as e:
            self._logger.exception(e)
            if e.status == 0:
                self._logger.error('Error, could not authenticate')

    def get_enterprise_information(self, host, enterpriseid):
        target_host_client = self.get_client_by_host(host)
        body = {"enterpriseId": enterpriseid}
        try:
            enterprise_information = target_host_client.enterpriseGetEnterprise(body=body)
            return enterprise_information
        except velocloud.rest.ApiException as e:
            self._logger.exception(e)
            if e.status == 0:
                self._logger.error('Error, could not authenticate')
