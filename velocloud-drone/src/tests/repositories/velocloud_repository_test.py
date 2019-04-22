from unittest.mock import Mock
from config import testconfig as config
from application.repositories.velocloud_repository import VelocloudRepository
import velocloud


class TestVelocloudRepository:

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
        mock_logger = Mock()
        self.mock_velocloud()
        vr = VelocloudRepository(config, mock_logger)
        if vr._config['verify_ssl'] is 'no':
            assert not velocloud.configuration.verify_ssl
        else:
            assert velocloud.configuration.verify_ssl
        assert vr._logger is mock_logger
        assert velocloud.ApiClient.called
        assert velocloud.ApiClient.call_args[1] == dict(host=vr._config['servers'][0]['url'])
        assert velocloud.ApiClient().authenticate.called
        assert velocloud.ApiClient().authenticate.call_args[0] == (vr._config['servers'][0]['username'],
                                                                   vr._config['servers'][0]['password'])

        assert velocloud.ApiClient().authenticate.call_args[1] == dict(operator=True)
        assert velocloud.AllApi.called

    def create_and_connect_all_clients_test(self):
        mock_logger = Mock()
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
        vr = VelocloudRepository(mock_config, mock_logger)
        assert len(vr._clients) is len(mock_config.VELOCLOUD_CONFIG['servers'])

    def get_edge_information_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        vr = VelocloudRepository(config, mock_logger)
        edge_info = vr.get_edge_information(vr._config['servers'][0]['url'], 19, 99)
        assert edge_info == "Some Edge Information"

    def get_edge_information_ko_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        vr = VelocloudRepository(config, mock_logger)
        vr._logger.exception = Mock()
        vr._clients[0].edgeGetEdge = Mock(side_effect=velocloud.rest.ApiException())
        edge_info = vr.get_edge_information(vr._config['servers'][0]['url'], 19, 99)
        assert edge_info is None
        assert vr._logger.exception.called

    def get_link_information_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        vr = VelocloudRepository(config, mock_logger)
        link_info = vr.get_link_information(vr._config['servers'][0]['url'], 19, 99)
        assert link_info == "Some Link Information"

    def get_link_information_ko_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        vr = VelocloudRepository(config, mock_logger)
        vr._logger.exception = Mock()
        vr._clients[0].metricsGetEdgeLinkMetrics = Mock(side_effect=velocloud.rest.ApiException())
        link_info = vr.get_link_information(vr._config['servers'][0]['url'], 19, 99)
        assert link_info is None
        assert vr._logger.exception.called

    def get_enterprise_information_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        vr = VelocloudRepository(config, mock_logger)
        enterprise_info = vr.get_enterprise_information(vr._config['servers'][0]['url'], 19)
        assert enterprise_info == "Some Enterprise Information"

    def get_enterprise_information_ko_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        vr = VelocloudRepository(config, mock_logger)
        vr._logger.exception = Mock()
        vr._clients[0].enterpriseGetEnterprise = Mock(side_effect=velocloud.rest.ApiException())
        enterprise_info = vr.get_enterprise_information(vr._config['servers'][0]['url'], 19)
        assert enterprise_info is None
        assert vr._logger.exception.called
