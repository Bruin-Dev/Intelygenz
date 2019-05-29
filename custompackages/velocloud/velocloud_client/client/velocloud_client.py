import velocloud
import urllib3


class VelocloudClient:

    def __init__(self, config):
        self._config = config.VELOCLOUD_CONFIG
        # Have to add POST method to a urlibs method_whitelist due to velocloud's api using only POST calls
        self.whitelist = frozenset(['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE', 'POST'])
        urllib3.util.retry.Retry.DEFAULT = urllib3.util.retry.Retry(total=self._config['total'],
                                                                    backoff_factor=self._config['backoff_factor'],
                                                                    method_whitelist=self.whitelist)

    def instantiate_and_connect_clients(self):
        _clients = [
            self._create_and_connect_client(cred_block['url'], cred_block['username'], cred_block['password']) for
            cred_block in self._config['servers']]
        return _clients

    def _create_and_connect_client(self, host, user, password):
        if self._config['verify_ssl'] is 'no':
            velocloud.configuration.verify_ssl = False
        client = velocloud.ApiClient(host=host)
        client.authenticate(user, password, operator=True)
        return velocloud.AllApi(client)

    def _get_client_by_host(self, clients, host):
        host_client = [client
                       for client in clients
                       if host in
                       client.api_client.base_path][0]
        return host_client

    def get_edge_information(self, client, logger, host, enterpriseid, edgeid):
        target_host_client = self._get_client_by_host(client, host)
        edgeids = {"enterpriseId": enterpriseid, "id": edgeid}
        try:
            edge_information = target_host_client.edgeGetEdge(body=edgeids)
            return edge_information
        except velocloud.rest.ApiException as e:
            logger.exception(e)
            if e.status == 0:
                logger.error('Error, could not authenticate')

    def get_link_information(self, client, logger, host, enterpriseid, edgeid):
        target_host_client = self._get_client_by_host(client, host)
        edgeids = {"enterpriseId": enterpriseid, "id": edgeid}
        try:
            link_information = target_host_client.metricsGetEdgeLinkMetrics(body=edgeids)
            return link_information
        except velocloud.rest.ApiException as e:
            logger.exception(e)
            if e.status == 0:
                logger.error('Error, could not authenticate')

    def get_enterprise_information(self, client, logger, host, enterpriseid):
        target_host_client = self._get_client_by_host(client, host)
        body = {"enterpriseId": enterpriseid}
        try:
            enterprise_information = target_host_client.enterpriseGetEnterprise(body=body)
            return enterprise_information
        except velocloud.rest.ApiException as e:
            logger.exception(e)
            if e.status == 0:
                logger.error('Error, could not authenticate')

    def get_all_enterprises_edges_with_host(self, clients, logger):
        edges_by_enterprise_and_host = list()
        try:
            for client in clients:
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
            logger.exception(f'Error, exception ocurred getting all velocloud '
                             f'enterprises from all velocloud clusters: {e}')
            if e.status == 0:
                logger.error('Error, could not authenticate')

        return edges_by_enterprise_and_host

    def get_all_hosts_edge_count(self, clients, logger):
        sum = 0
        try:
            for client in clients:
                res = client.monitoringGetAggregates(body={})
                sum += res._edgeCount
        except velocloud.rest.ApiException as e:
            logger.exception(f'Error, exception ocurred getting all velocloud '
                             f'enterprises from all velocloud clusters: {e}')
            if e.status == 0:
                logger.error('Error, could not authenticate')
        return sum
