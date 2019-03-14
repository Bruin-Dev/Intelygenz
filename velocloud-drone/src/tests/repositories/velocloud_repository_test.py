from unittest.mock import Mock
from config import testconfig as config
from application.repositories.velocloud_repository import VelocloudRepository
import velocloud


class TestVelocloudRepository:

    def mock_velocloud(self):
        client = Mock()
        client.authenticate = Mock()
        velocloud.ApiClient = Mock(return_value=client)
        velocloud.AllApi = Mock(return_value=Mock())

    def create_one_and_connect_clients_test(self):
        self.mock_velocloud()
        vr = VelocloudRepository(config)
        if vr._config['verify_ssl'] is 'no':
            assert not velocloud.configuration.verify_ssl
        else:
            assert velocloud.configuration.verify_ssl
        assert velocloud.ApiClient.called
        assert velocloud.ApiClient.call_args[1] == dict(host=vr._config['servers'][0]['url'])
        assert velocloud.ApiClient().authenticate.called
        assert velocloud.ApiClient().authenticate.call_args[0] == (vr._config['servers'][0]['username'],
                                                                   vr._config['servers'][0]['password'])

        assert velocloud.ApiClient().authenticate.call_args[1] == dict(operator=True)
        assert velocloud.AllApi.called

    def create_and_connect_various_clients_test(self):
        self.mock_velocloud()
        mock_config = Mock()
        mock_config.VELOCLOUD_CONFIG = {
            'verify_ssl': 'no',
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
        VelocloudRepository._create_and_connect_client = Mock(return_value=Mock())
        vr = VelocloudRepository(mock_config)
        assert len(vr._clients) is len(mock_config.VELOCLOUD_CONFIG['servers'])
        assert VelocloudRepository._create_and_connect_client.call_count is len(vr._clients)
