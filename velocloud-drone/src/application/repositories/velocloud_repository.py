import velocloud
from tenacity import retry, wait_exponential


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

    def exception_call(self, exception):
        if exception.status == 0:
            self.connect_to_all_servers()
            raise exception
        if exception.status == 400:
            raise exception

    def get_edge_information(self, host, enterpriseid, edgeid):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min'],
                                     max=self._config['max']))
        def get_edge_information(host, enterpriseid, edgeid):
            target_host_client = self.get_client_by_host(host)
            edgeids = {"enterpriseId": enterpriseid, "id": edgeid}
            try:
                edge_information = target_host_client.edgeGetEdge(body=edgeids)
                return edge_information
            except velocloud.rest.ApiException as e:
                self._logger.exception(e)
                self.exception_call(e)

        edge_information = get_edge_information(host, enterpriseid, edgeid)
        return edge_information

    def get_link_information(self, host, enterpriseid, edgeid):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min'],
                                     max=self._config['max']))
        def get_link_information(host, enterpriseid, edgeid):
            target_host_client = self.get_client_by_host(host)
            edgeids = {"enterpriseId": enterpriseid, "id": edgeid}
            try:
                link_information = target_host_client.metricsGetEdgeLinkMetrics(body=edgeids)
                return link_information
            except velocloud.rest.ApiException as e:
                self._logger.exception(e)
                self.exception_call(e)

        link_information = get_link_information(host, enterpriseid, edgeid)
        return link_information

    def get_enterprise_information(self, host, enterpriseid):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min'],
                                     max=self._config['max']))
        def get_enterprise_information(host, enterpriseid):
            target_host_client = self.get_client_by_host(host)
            body = {"enterpriseId": enterpriseid}
            try:
                enterprise_information = target_host_client.enterpriseGetEnterprise(body=body)
                return enterprise_information
            except velocloud.rest.ApiException as e:
                self._logger.exception(e)
                self.exception_call(e)

        enterprise_information = get_enterprise_information(host, enterpriseid)
        return enterprise_information
