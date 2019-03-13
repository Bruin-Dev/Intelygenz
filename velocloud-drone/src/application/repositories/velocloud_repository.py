import velocloud
import logging
import sys
from igz.packages.Logger.logger_client import LoggerClient


class VelocloudRepository:
    _config = None
    _clients = None
    error_log = LoggerClient().create_logger('velocloud-repo-KO', sys.stderr, logging.ERROR)

    def __init__(self, config):
        self._config = config.VELOCLOUD_CONFIG
        self._clients = list()
        self._instantiate_and_connect_clients()

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

    def get_edge_information(self, host, enterpriseid, edgeid):
        target_host_client = [client
                              for client in self._clients
                              if host in
                              client.api_client.base_path][0]
        edgeids = {"enterpriseId": enterpriseid, "id": edgeid}
        try:
            edge_information = target_host_client.edgeGetEdge(body=edgeids)
            return edge_information
        except velocloud.rest.ApiException as e:
            self.error_log.exception(e)
