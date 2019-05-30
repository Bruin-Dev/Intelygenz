from unittest.mock import Mock
from config import testconfig as config
from application.repositories.velocloud_repository import VelocloudRepository


class TestVelocloudRepository:

    def get_all_enterprises_edges_with_host_test(self):
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, test_velocloud_client)
        test_velocloud_client.get_all_enterprises_edges_with_host = Mock()
        edges_by_ent = vr.get_all_enterprises_edges_with_host()
        assert test_velocloud_client.get_all_enterprises_edges_with_host.called

    def get_all_hosts_edge_count_test(self):
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, test_velocloud_client)
        test_velocloud_client.get_all_hosts_edge_count = Mock()
        sum = vr.get_all_hosts_edge_count()
        assert test_velocloud_client.get_all_hosts_edge_count.called

    def connect_to_all_servers_test(self):
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, test_velocloud_client)
        test_velocloud_client.instantiate_and_connect_clients = Mock()
        vr.connect_to_all_servers()
        assert test_velocloud_client.instantiate_and_connect_clients.called
