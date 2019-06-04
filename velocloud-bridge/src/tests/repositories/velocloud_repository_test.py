from unittest.mock import Mock
from config import testconfig as config
from application.repositories.velocloud_repository import VelocloudRepository


class TestVelocloudRepository:

    def get_all_enterprises_edges_with_host_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        test_velocloud_client.get_all_enterprises_edges_with_host = Mock()
        edges_by_ent = vr.get_all_enterprises_edges_with_host()
        assert test_velocloud_client.get_all_enterprises_edges_with_host.called

    def get_all_hosts_edge_count_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        test_velocloud_client.get_all_hosts_edge_count = Mock()
        sum = vr.get_all_hosts_edge_count()
        assert test_velocloud_client.get_all_hosts_edge_count.called

    def get_edge_information_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        test_velocloud_client.get_edge_information = Mock()
        edge_info = vr.get_edge_information(vr._config['servers'][0]['url'], 19, 99)
        assert test_velocloud_client.get_edge_information.called

    def get_link_information_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        test_velocloud_client.get_link_information = Mock()
        link_info = vr.get_link_information(vr._config['servers'][0]['url'], 19, 99)
        assert test_velocloud_client.get_link_information.called

    def get_enterprise_information_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        test_velocloud_client.get_enterprise_information = Mock()
        enterprise_info = vr.get_enterprise_information(vr._config['servers'][0]['url'], 19)
        assert test_velocloud_client.get_enterprise_information.called

    def connect_to_all_servers_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        test_velocloud_client.instantiate_and_connect_clients = Mock()
        vr.connect_to_all_servers()
        assert test_velocloud_client.instantiate_and_connect_clients.called
