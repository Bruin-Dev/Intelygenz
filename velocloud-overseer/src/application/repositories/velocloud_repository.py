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

    def get_all_enterprises_edges_with_host(self):
        edges_by_enterprise_and_host = list()
        try:
            for client in self._clients:
                res = client.monitoringGetAggregates(body={})
                for enterprise in res._enterprises:
                    edges_by_enterprise = client.enterpriseGetEnterpriseEdges({"enterpriseId": enterprise._id})
                    for edge in edges_by_enterprise:
                        edges_by_enterprise_and_host.append(
                            {"host": client.api_client.base_path.replace("/portal/rest", "").replace
                             ("https://", ""),
                             "enterpriseId": enterprise._id,
                             "id": edge._id})

        except velocloud.rest.ApiException as e:
            self._logger.exception(f'Error, exception ocurred getting all velocloud '
                                   f'enterprises from all velocloud clusters: {e}')
            if e.status == 0:
                self._logger.error('Error, bad credentials')

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
            if e.status == 0:
                self._logger.error('Error, bad credentials')
        return sum
