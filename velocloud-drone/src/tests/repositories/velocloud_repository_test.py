from unittest.mock import Mock
from config import testconfig as config
from application.repositories.velocloud_repository import VelocloudRepository
import velocloud
from velocloud_client.client.velocloud_client import VelocloudClient


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

    def get_edge_information_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config)
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        edge_info = vr.get_edge_information(vr._config['servers'][0]['url'], 19, 99)
        assert edge_info == "Some Edge Information"

    def get_edge_information_ko_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config)
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        vr._logger.exception = Mock()
        vr._clients[0].edgeGetEdge = Mock(side_effect=velocloud.rest.ApiException())
        edge_info = vr.get_edge_information(vr._config['servers'][0]['url'], 19, 99)
        assert edge_info is None
        assert vr._logger.exception.called

    def get_link_information_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config)
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        link_info = vr.get_link_information(vr._config['servers'][0]['url'], 19, 99)
        assert link_info == "Some Link Information"

    def get_link_information_ko_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config)
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        vr._logger.exception = Mock()
        vr._clients[0].metricsGetEdgeLinkMetrics = Mock(side_effect=velocloud.rest.ApiException())
        link_info = vr.get_link_information(vr._config['servers'][0]['url'], 19, 99)
        assert link_info is None
        assert vr._logger.exception.called

    def get_enterprise_information_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config)
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        enterprise_info = vr.get_enterprise_information(vr._config['servers'][0]['url'], 19)
        assert enterprise_info == "Some Enterprise Information"

    def get_enterprise_information_ko_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config)
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        vr._logger.exception = Mock()
        vr._clients[0].enterpriseGetEnterprise = Mock(side_effect=velocloud.rest.ApiException())
        enterprise_info = vr.get_enterprise_information(vr._config['servers'][0]['url'], 19)
        assert enterprise_info is None
        assert vr._logger.exception.called
