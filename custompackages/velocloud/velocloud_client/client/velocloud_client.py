import velocloud
import urllib3


class VelocloudClient:

    def __init__(self, config):
        self._config = config.VELOCLOUD_CONFIG
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
