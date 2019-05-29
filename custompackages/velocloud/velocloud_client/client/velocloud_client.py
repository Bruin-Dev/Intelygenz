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

    def _instantiate_and_connect_clients(self):
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

    def _get_edge_information(self, client, logger, host, enterpriseid, edgeid):
        target_host_client = self._get_client_by_host(client, host)
        edgeids = {"enterpriseId": enterpriseid, "id": edgeid}
        try:
            edge_information = target_host_client.edgeGetEdge(body=edgeids)
            return edge_information
        except velocloud.rest.ApiException as e:
            logger.exception(e)
            if e.status == 0:
                logger.error('Error, could not authenticate')

    def _get_link_information(self, client, logger, host, enterpriseid, edgeid):
        target_host_client = self._get_client_by_host(client, host)
        edgeids = {"enterpriseId": enterpriseid, "id": edgeid}
        try:
            link_information = target_host_client.metricsGetEdgeLinkMetrics(body=edgeids)
            return link_information
        except velocloud.rest.ApiException as e:
            logger.exception(e)
            if e.status == 0:
                logger.error('Error, could not authenticate')

    def _get_enterprise_information(self, client, logger, host, enterpriseid):
        target_host_client = self._get_client_by_host(client, host)
        body = {"enterpriseId": enterpriseid}
        try:
            enterprise_information = target_host_client.enterpriseGetEnterprise(body=body)
            return enterprise_information
        except velocloud.rest.ApiException as e:
            logger.exception(e)
            if e.status == 0:
                logger.error('Error, could not authenticate')
