import velocloud


class VelocloudRepository:
    _config = None
    _clients = None
    _logger = None

    def __init__(self, config, logger):
        self._config = config.VELOCLOUD_CONFIG
        self._clients = list()
        self._instantiate_and_connect_clients()
        self._logger = logger

    def _instantiate_and_connect_clients(self):
        self._clients = [
            self._create_and_connect_client(cred_block['url'], cred_block['username'], cred_block['password']) for
            cred_block in self._config['servers']]

    def _create_and_connect_client(self, host, user, password):
        if self._config['verify_ssl'] is 'no':
            velocloud.configuration.verify_ssl = False
        client = velocloud.ApiClient(host=host)
        client.authenticate(user, password, operator=True)
        return velocloud.AllApi(client)

    def seek_host(self, host):
        host_client = [client
                       for client in self._clients
                       if host in
                       client.api_client.base_path][0]
        return host_client

    def get_edge_information(self, host, enterpriseid, edgeid):
        target_host_client = self.seek_host(host)
        edgeids = {"enterpriseId": enterpriseid, "id": edgeid}
        try:
            edge_information = target_host_client.edgeGetEdge(body=edgeids)
            return edge_information
        except velocloud.rest.ApiException as e:
            self._logger.exception(e)

    def get_link_information(self, host, enterpriseid, edgeid):
        target_host_client = self.seek_host(host)
        edgeids = {"enterpriseId": enterpriseid, "id": edgeid}
        try:
            link_information = target_host_client.metricsGetEdgeLinkMetrics(body=edgeids)
            return link_information
        except velocloud.rest.ApiException as e:
            self._logger.exception(e)
