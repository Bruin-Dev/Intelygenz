import velocloud


class VelocloudRepository:
    _config = None
    _clients = None

    def __init__(self, config):
        self._config = config.VELOCLOUD_CONFIG
        self._clients = list()
        self._instantiate_and_connect_clients()

    def _instantiate_and_connect_clients(self):
        self._clients = [
            self._create_and_connect_client(cred_block['url'], cred_block['username'], cred_block['password']) for
            cred_block in self._config['servers']]

    def _create_and_connect_client(self, host, user, password):
        if self._config is 'no':
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
            print(f'Error, exception ocurred getting all velocloud enterprises from all velocloud clusters: {e}')
        # Remove this limitation when we have a development environment with velocloud
        return edges_by_enterprise_and_host[0:250]
