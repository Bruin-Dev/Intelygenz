from unittest.mock import Mock
from config import testconfig as config
from application.repositories.velocloud_repository import VelocloudRepository
import pytest


class TestVelocloudRepository:

    def get_all_enterprises_edges_with_host_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        edges = [{"host": "some.host", "enterprise_id": 19, "edge_id": 99}]
        msg = {"request_id": "123", "filter": []}
        test_velocloud_client.get_all_enterprises_edges_with_host = Mock(return_value=edges)
        edges_by_ent = vr.get_all_enterprises_edges_with_host(msg)
        assert test_velocloud_client.get_all_enterprises_edges_with_host.called
        assert edges_by_ent == edges

    @pytest.mark.asyncio
    async def send_edge_status_filter_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        edges = [{"host": "some.host", "enterprise_id": 19, "edge_id": 99},
                 {"host": "some.host", "enterprise_id": 32, "edge_id": 99},
                 {"host": "some.host2", "enterprise_id": 42, "edge_id": 99}]
        test_velocloud_client.get_all_enterprises_edges_with_host = Mock(return_value=edges)
        msg = {"request_id": "123", "filter": [{"host": "some.host", "enterprise_ids": [19]},
                                               {"host": "some.host2", "enterprise_ids": []}]}
        edges_by_ent = vr.get_all_enterprises_edges_with_host(msg)
        assert edges_by_ent == [edges[0], edges[2]]

    def get_edge_information_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        test_velocloud_client.get_edge_information = Mock()
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        edge_info = vr.get_edge_information(edge)
        assert test_velocloud_client.get_edge_information.called

    def get_link_information_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        test_velocloud_client.get_link_information = Mock()
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        link_info = vr.get_link_information(edge)
        assert test_velocloud_client.get_link_information.called

    def get_enterprise_information_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        test_velocloud_client.get_enterprise_information = Mock()
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        enterprise_info = vr.get_enterprise_information(edge)
        assert test_velocloud_client.get_enterprise_information.called

    def connect_to_all_servers_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        test_velocloud_client.instantiate_and_connect_clients = Mock()
        vr.connect_to_all_servers()
        assert test_velocloud_client.instantiate_and_connect_clients.called
