from unittest.mock import Mock
from config import testconfig as config
from application.repositories.velocloud_repository import VelocloudRepository
from collections import namedtuple
import velocloud


class TestVelocloudRepository:

    def mock_velocloud(self):
        client = Mock()
        client.authenticate = Mock()
        velocloud.ApiClient = Mock(return_value=client)
        all_api_client = Mock()
        enterprises_res = namedtuple("enterprise_res", [])
        enterprise = namedtuple("enterprise", [])
        enterprise._id = 1
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

    def create_one_and_connect_clients_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        vr = VelocloudRepository(config, mock_logger)
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

    def get_all_enterprises_edges_with_host_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        vr = VelocloudRepository(config, mock_logger)
        edges_by_ent = vr.get_all_enterprises_edges_with_host()
        assert edges_by_ent == [{"host": "someurl", "enterpriseId": 1, "id": 19},
                                {"host": "someurl", "enterpriseId": 1, "id": 77}]

    def chatching_velocloud_exception_test(self):
        mock_logger = Mock()
        self.mock_velocloud()
        vr = VelocloudRepository(config, mock_logger)
        vr._logger.exception = Mock()
        vr._clients[0].monitoringGetAggregates = Mock(side_effect=velocloud.rest.ApiException())
        edges_by_ent = vr.get_all_enterprises_edges_with_host()
        assert len(edges_by_ent) is 0
        assert vr._logger.exception.called
