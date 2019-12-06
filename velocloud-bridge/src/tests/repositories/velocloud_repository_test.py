from unittest.mock import Mock
from config import testconfig as config
from application.repositories.velocloud_repository import VelocloudRepository
import pytest
from datetime import datetime, timedelta


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

    def get_link_information_ok_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        link_status = [{"link_data": "STABLE", "linkId": "123", 'link': {'backupState': 'UNCONFIGURED'}}]
        link_service_group = [{"linkId": "123", "serviceGroups": ["PUBLIC_WIRED"]}]
        link_info_return = [{"link_data": "STABLE", "linkId": "123", 'link': {'backupState': 'UNCONFIGURED'},
                             "serviceGroups": ["PUBLIC_WIRED"]}]
        test_velocloud_client.get_link_information = Mock(return_value=link_status)
        test_velocloud_client.get_link_service_groups_information = Mock(return_value=link_service_group)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        interval = "some Interval"
        link_info = vr.get_link_information(edge, interval)
        assert test_velocloud_client.get_link_information.called
        assert test_velocloud_client.get_link_service_groups_information.called
        assert link_info == link_info_return

    def get_link_information_ko_wrong_id_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        link_status = [{"link_data": "STABLE", "linkId": "123", 'link': {'backupState': 'UNCONFIGURED'}}]
        link_service_group = [{"linkId": "143", "serviceGroups": ["PUBLIC_WIRED"]}]
        link_info_return = [{"link_data": "STABLE", "linkId": "123", 'link': {'backupState': 'UNCONFIGURED'}}]
        test_velocloud_client.get_link_information = Mock(return_value=link_status)
        test_velocloud_client.get_link_service_groups_information = Mock(return_value=link_service_group)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        interval = "some Interval"
        link_info = vr.get_link_information(edge, interval)
        assert test_velocloud_client.get_link_information.called
        assert test_velocloud_client.get_link_service_groups_information.called
        assert link_info == link_info_return

    def get_link_information_ko_different_backup_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        link_status = [{"link_data": "STABLE", "linkId": "123", 'link': {'backupState': 'STABLE'}}]
        link_service_group = [{"linkId": "123", "serviceGroups": ["PUBLIC_WIRED"]}]
        link_info_return = [{"link_data": "STABLE", "linkId": "143", 'link': {'backupState': 'UNCONFIGURED'},
                             "serviceGroups": ["PUBLIC_WIRED"]}]
        test_velocloud_client.get_link_information = Mock(return_value=link_status)
        test_velocloud_client.get_link_service_groups_information = Mock(return_value=link_service_group)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        interval = "some Interval"
        link_info = vr.get_link_information(edge, interval)
        assert test_velocloud_client.get_link_information.called
        assert test_velocloud_client.get_link_service_groups_information.called
        assert link_info == []

    def get_link_information_ko_none_link_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        link_status = None
        link_service_group = [{"linkId": "123", "serviceGroups": ["PUBLIC_WIRED"]}]
        test_velocloud_client.get_link_information = Mock(return_value=link_status)
        test_velocloud_client.get_link_service_groups_information = Mock(return_value=link_service_group)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        interval = "some Interval"
        link_info = vr.get_link_information(edge, interval)
        assert test_velocloud_client.get_link_information.called
        assert test_velocloud_client.get_link_service_groups_information.called
        assert link_info is None

    def get_link_information_ko_exception_link_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        link_status = Exception()
        link_service_group = [{"linkId": "123", "serviceGroups": ["PUBLIC_WIRED"]}]
        test_velocloud_client.get_link_information = Mock(return_value=link_status)
        test_velocloud_client.get_link_service_groups_information = Mock(return_value=link_service_group)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        interval = "some Interval"
        link_info = vr.get_link_information(edge, interval)
        assert test_velocloud_client.get_link_information.called
        assert test_velocloud_client.get_link_service_groups_information.called
        assert link_info == link_status

    def get_enterprise_information_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        test_velocloud_client.get_enterprise_information = Mock(return_value={'name': 'test'})
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        enterprise_info = vr.get_enterprise_information(edge)
        assert test_velocloud_client.get_enterprise_information.called
        assert enterprise_info == 'test'

    def get_enterprise_information_ko_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        test_velocloud_client.get_enterprise_information = Mock(return_value=Exception())
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        enterprise_info = vr.get_enterprise_information(edge)
        assert test_velocloud_client.get_enterprise_information.called
        assert isinstance(enterprise_info, Exception)

    def get_all_edge_events_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)

        events = {"data": [{'event': 'EDGE_UP'}, {'event': 'EDGE_GONE'}]}

        test_velocloud_client.get_all_edge_events = Mock(return_value=events)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        start = datetime.now() - timedelta(hours=24)
        end = datetime.now()
        limit = None
        edge_events = vr.get_all_edge_events(edge, start, end, limit)
        assert test_velocloud_client.get_all_edge_events.called
        assert edge_events == [{'event': 'EDGE_UP'}]

    def connect_to_all_servers_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        test_velocloud_client.instantiate_and_connect_clients = Mock()
        vr.connect_to_all_servers()
        assert test_velocloud_client.instantiate_and_connect_clients.called
