from unittest.mock import Mock
from velocloud_client.config import testconfig as config
from velocloud_client.client.velocloud_client import VelocloudClient
import velocloud


class TestVelocloudClient:

    def mock_velocloud(self):
        client = Mock()
        client.authenticate = Mock()
        velocloud.ApiClient = Mock(return_value=client)
        all_api_client = Mock()
        all_api_client.edgeGetEdge = Mock(return_value="Some Edge Information")
        all_api_client.metricsGetEdgeLinkMetrics = Mock(return_value="Some Link Information")
        all_api_client.enterpriseGetEnterprise = Mock(return_value="Some Enterprise Information")
        all_api_client.api_client.base_path = config.VELOCLOUD_CONFIG['servers'][0]['url']
        velocloud.AllApi = Mock(return_value=all_api_client)

    def create_one_and_connect_clients_test(self):
        self.mock_velocloud()
        vc = VelocloudClient(config)
        vr_clients = vc._instantiate_and_connect_clients()
        if vc._config['verify_ssl'] is 'no':
            assert not velocloud.configuration.verify_ssl
        else:
            assert velocloud.configuration.verify_ssl
        assert velocloud.ApiClient.called
        assert velocloud.ApiClient.call_args[1] == dict(host=vc._config['servers'][0]['url'])
        assert velocloud.ApiClient().authenticate.called
        assert velocloud.ApiClient().authenticate.call_args[0] == (vc._config['servers'][0]['username'],
                                                                   vc._config['servers'][0]['password'])

        assert velocloud.ApiClient().authenticate.call_args[1] == dict(operator=True)
        assert velocloud.AllApi.called

    def create_and_connect_all_clients_test(self):
        self.mock_velocloud()
        mock_config = Mock()
        mock_config.VELOCLOUD_CONFIG = {
            'verify_ssl': 'yes',
            'servers': [
                {
                    'url': 'someurl',
                    'username': 'someusername',
                    'password': 'somepassword',

                },
                {
                    'url': 'someurl2',
                    'username': 'someusername2',
                    'password': 'somepassword2',

                }
            ]}
        vc = VelocloudClient(mock_config)
        vr_clients = vc._instantiate_and_connect_clients()
        assert len(vr_clients) is len(mock_config.VELOCLOUD_CONFIG['servers'])
