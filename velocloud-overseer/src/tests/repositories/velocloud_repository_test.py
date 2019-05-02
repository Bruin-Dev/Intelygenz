from unittest.mock import Mock
from config import testconfig as config
from application.repositories.velocloud_repository import VelocloudRepository
from collections import namedtuple
import velocloud
from igz.packages.velocloud.velocloud_client import VelocloudClient


class TestVelocloudRepository:

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
        all_api_client.api_client.base_path = config.VELOCLOUD_CONFIG['servers'][0]['url']
        velocloud.AllApi = Mock(return_value=all_api_client)

    def get_all_enterprises_edges_with_host_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config)
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        edges_by_ent = vr.get_all_enterprises_edges_with_host()
        assert edges_by_ent == [{"host": "someurl", "enterpriseId": 1, "id": 19},
                                {"host": "someurl", "enterpriseId": 1, "id": 77}]

    def chatching_velocloud_exception_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config)
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        vr._logger.exception = Mock()
        vr._clients[0].monitoringGetAggregates = Mock(side_effect=velocloud.rest.ApiException())
        edges_by_ent = vr.get_all_enterprises_edges_with_host()
        assert len(edges_by_ent) is 0
        assert vr._logger.exception.called

    def get_all_hosts_edge_count_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config)
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        sum = vr.get_all_hosts_edge_count()
        print(sum)
        assert sum == 123

    def get_all_hosts_edge_count_KO_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        test_velocloud_client = VelocloudClient(config)
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        vr._logger.exception = Mock()
        vr._clients[0].monitoringGetAggregates = Mock(side_effect=velocloud.rest.ApiException())
        sum = vr.get_all_hosts_edge_count()
        assert sum is 0
        assert vr._logger.exception.called
