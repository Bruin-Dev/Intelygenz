from unittest.mock import Mock
from velocloud_client.config import testconfig as config
from velocloud_client.client.velocloud_client import VelocloudClient
import velocloud
from collections import namedtuple


class TestVelocloudClient:

    def mock_velocloud(self):
        client = Mock()
        client.authenticate = Mock()
        velocloud.ApiClient = Mock(return_value=client)
        all_api_client = Mock()
        enterprises_res = namedtuple("enterprise_res", [])
        enterprise = namedtuple("enterprise", [])
        enterprise._id = 1
        enterprises_res._edgeCount = 123
        enterprises_res._enterprises = [enterprise]
        all_api_client.monitoringGetAggregates = Mock(return_value=enterprises_res)
        edge1 = namedtuple("edge", [])
        edge2 = namedtuple("edge", [])
        edge1._id = 19
        edge2._id = 77
        edges_res = [edge1, edge2]
        all_api_client.enterpriseGetEnterpriseEdges = Mock(return_value=edges_res)
        all_api_client.edgeGetEdge = Mock(return_value="Some Edge Information")
        all_api_client.metricsGetEdgeLinkMetrics = Mock(return_value="Some Link Information")
        all_api_client.enterpriseGetEnterprise = Mock(return_value="Some Enterprise Information")
        all_api_client.api_client.base_path = config.VELOCLOUD_CONFIG['servers'][0]['url']
        velocloud.AllApi = Mock(return_value=all_api_client)

    def create_one_and_connect_clients_test(self):
        self.mock_velocloud()
        vc = VelocloudClient(config)
        vc.instantiate_and_connect_clients()
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
            ],
            'multiplier': 5,
            'min': 5,
            'max': 300,
            'total': 8,
            'backoff_factor': 2
        }
        vc = VelocloudClient(mock_config)
        vc.instantiate_and_connect_clients()
        assert len(vc._clients) is len(mock_config.VELOCLOUD_CONFIG['servers'])

    def get_edge_information_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config, mock_logger)
        test_velocloud_client.instantiate_and_connect_clients()
        edge_info = test_velocloud_client.get_edge_information(test_velocloud_client._config['servers'][0]['url'],
                                                               19, 99)
        assert edge_info == "Some Edge Information"

    def get_edge_information_ko_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config, mock_logger)
        test_velocloud_client.instantiate_and_connect_clients()
        test_velocloud_client._logger.exception = Mock()
        test_velocloud_client._logger.error = Mock()
        exception = velocloud.rest.ApiException()
        exception.status = 400
        test_velocloud_client._clients[0].edgeGetEdge = Mock(side_effect=exception)
        edge_info = test_velocloud_client.get_edge_information(test_velocloud_client._config['servers'][0]['url'],
                                                               19, 99)
        assert edge_info is None
        assert test_velocloud_client._logger.exception.called
        assert test_velocloud_client._logger.error.called is False
        exception.status = 0
        edge_info = test_velocloud_client.get_edge_information(test_velocloud_client._config['servers'][0]['url'],
                                                               19, 99)
        assert test_velocloud_client._logger.error.called

    def get_link_information_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config, mock_logger)
        test_velocloud_client.instantiate_and_connect_clients()
        link_info = test_velocloud_client.get_link_information(test_velocloud_client._config['servers'][0]['url'],
                                                               19, 99)
        assert link_info == "Some Link Information"

    def get_link_information_ko_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config, mock_logger)
        test_velocloud_client.instantiate_and_connect_clients()
        test_velocloud_client._logger.exception = Mock()
        test_velocloud_client._logger.error = Mock()
        exception = velocloud.rest.ApiException()
        exception.status = 400
        test_velocloud_client._clients[0].metricsGetEdgeLinkMetrics = Mock(side_effect=exception)
        link_info = test_velocloud_client.get_link_information(test_velocloud_client._config['servers'][0]['url'],
                                                               19, 99)
        assert link_info is None
        assert test_velocloud_client._logger.exception.called
        assert test_velocloud_client._logger.error.called is False
        exception.status = 0
        link_info = test_velocloud_client.get_link_information(test_velocloud_client._config['servers'][0]['url'],
                                                               19, 99)
        assert test_velocloud_client._logger.error.called

    def get_enterprise_information_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config, mock_logger)
        test_velocloud_client.instantiate_and_connect_clients()
        enterprise_info = test_velocloud_client.get_enterprise_information(test_velocloud_client._config['servers'][0]
                                                                           ['url'],
                                                                           19)
        assert enterprise_info == "Some Enterprise Information"

    def get_enterprise_information_ko_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config, mock_logger)
        test_velocloud_client.instantiate_and_connect_clients()
        test_velocloud_client._logger.exception = Mock()
        test_velocloud_client._logger.error = Mock()
        exception = velocloud.rest.ApiException()
        exception.status = 400
        test_velocloud_client._clients[0].enterpriseGetEnterprise = Mock(side_effect=exception)
        enterprise_info = test_velocloud_client.get_enterprise_information(test_velocloud_client._config['servers'][0]
                                                                           ['url'],
                                                                           19)
        assert enterprise_info is None
        assert test_velocloud_client._logger.exception.called
        assert test_velocloud_client._logger.error.called is False
        exception.status = 0
        enterprise_info = test_velocloud_client.get_enterprise_information(test_velocloud_client._config['servers'][0]
                                                                           ['url'],
                                                                           19)
        assert test_velocloud_client._logger.error.called

    def get_all_enterprises_edges_with_host_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config, mock_logger)
        test_velocloud_client.instantiate_and_connect_clients()
        edges_by_ent = test_velocloud_client.get_all_enterprises_edges_with_host()
        assert edges_by_ent == [{"host": "someurl", "enterpriseId": 1, "id": 19},
                                {"host": "someurl", "enterpriseId": 1, "id": 77}]

    def catching_velocloud_exception_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config, mock_logger)
        test_velocloud_client.instantiate_and_connect_clients()
        test_velocloud_client._logger.exception = Mock()
        test_velocloud_client._logger.error = Mock()
        exception = velocloud.rest.ApiException()
        exception.status = 400
        test_velocloud_client._clients[0].monitoringGetAggregates = Mock(side_effect=exception)
        edges_by_ent = test_velocloud_client.get_all_enterprises_edges_with_host()
        assert len(edges_by_ent) is 0
        assert test_velocloud_client._logger.exception.called
        assert test_velocloud_client._logger.error.called is False
        exception.status = 0
        edges_by_ent = test_velocloud_client.get_all_enterprises_edges_with_host()
        assert test_velocloud_client._logger.error.called

    def get_all_hosts_edge_count_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config, mock_logger)
        test_velocloud_client.instantiate_and_connect_clients()
        sum = test_velocloud_client.get_all_hosts_edge_count()
        assert sum == 123

    def get_all_hosts_edge_count_KO_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config, mock_logger)
        test_velocloud_client.instantiate_and_connect_clients()
        test_velocloud_client._logger.exception = Mock()
        test_velocloud_client._logger.error = Mock()
        exception = velocloud.rest.ApiException()
        exception.status = 400
        test_velocloud_client._clients[0].monitoringGetAggregates = Mock(side_effect=exception)
        sum = test_velocloud_client.get_all_hosts_edge_count()
        assert sum is 0
        assert test_velocloud_client._logger.exception.called
        assert test_velocloud_client._logger.error.called is False
        exception.status = 0
        sum = test_velocloud_client.get_all_hosts_edge_count()
        assert test_velocloud_client._logger.error.called
