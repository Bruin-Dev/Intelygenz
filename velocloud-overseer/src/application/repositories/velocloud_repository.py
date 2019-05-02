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

    def get_all_enterprises_edges_with_host(self):
        edges_by_enterprise_and_host = list()
        try:
            for client in self._clients:
                res = client.monitoringGetAggregates(body={})
                for enterprise in res._enterprises:
                    edges_by_enterprise = client.enterpriseGetEnterpriseEdges({"enterpriseId": enterprise._id})
                    for edge in edges_by_enterprise:
                        edges_by_enterprise_and_host.append(
                            {"host": client.api_client.base_path.replace("/portal/rest", "").replace("https://", ""),
                             "enterpriseId": enterprise._id,
                             "id": edge._id})

        except velocloud.rest.ApiException as e:
            self._logger.exception(f'Error, exception ocurred getting all velocloud '
                                   f'enterprises from all velocloud clusters: {e}')
        return edges_by_enterprise_and_host

    def get_all_hosts_edge_count(self):
        sum = 0
        try:
            for client in self._clients:
                res = client.monitoringGetAggregates(body={})
                sum += res._edgeCount
        except velocloud.rest.ApiException as e:
            self._logger.exception(f'Error, exception ocurred getting all velocloud '
                                   f'enterprises from all velocloud clusters: {e}')

        return sum
