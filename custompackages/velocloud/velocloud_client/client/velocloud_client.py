import velocloud
from tenacity import retry, wait_exponential


class VelocloudClient:

    _config = None

    def __init__(self, config):
        self._config = config.VELOCLOUD_CONFIG

    def _instantiate_and_connect_clients(self):
        _clients = [
            self._create_and_connect_client(cred_block['url'], cred_block['username'], cred_block['password']) for
            cred_block in self._config['servers']]
        return _clients

    def _create_and_connect_client(self, host, user, password):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min'],
                                     max=self._config['max']))
        def _create_and_connect_client(host, user, password):
            if self._config['verify_ssl'] is 'no':
                velocloud.configuration.verify_ssl = False
            client = velocloud.ApiClient(host=host)
            client.authenticate(user, password, operator=True)
            return velocloud.AllApi(client)

        _create_and_connect_client(host, user, password)
