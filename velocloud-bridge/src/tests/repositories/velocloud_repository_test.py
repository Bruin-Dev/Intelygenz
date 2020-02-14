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
        edges = {"body": [{"host": "some.host", "enterprise_id": 19, "edge_id": 99}],
                 "status_code": 200}
        msg = {"request_id": "123", "filter": []}
        test_velocloud_client.get_all_enterprises_edges_with_host = Mock(return_value=edges)
        edges_by_ent = vr.get_all_enterprises_edges_with_host(msg)
        assert test_velocloud_client.get_all_enterprises_edges_with_host.called
        assert edges_by_ent == edges

    def get_all_enterprises_edges_with_host__error_500_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        edges = {"body": None,
                 "status_code": 500}
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
        edges = {
            "body":
                [
                    {"host": "some.host", "enterprise_id": 19, "edge_id": 99},
                    {"host": "some.host", "enterprise_id": 32, "edge_id": 99},
                    {"host": "some.host2", "enterprise_id": 42, "edge_id": 99}
                ],
            "status_code": 200
        }
        test_velocloud_client.get_all_enterprises_edges_with_host = Mock(return_value=edges)
        msg = {"request_id": "123", "filter": [{"host": "some.host", "enterprise_ids": [19]},
                                               {"host": "some.host2", "enterprise_ids": []}]}
        edges_by_ent = vr.get_all_enterprises_edges_with_host(msg)
        assert edges_by_ent["body"] == [edges["body"][0], edges["body"][2]]

    def get_edge_information_OK_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        mock_response = {"status_code": 200, "body": "info"}
        test_velocloud_client.get_edge_information = Mock(return_value=mock_response)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        edge_info = vr.get_edge_information(edge)

        assert test_velocloud_client.get_edge_information.called
        assert edge_info == mock_response

    def get_edge_information_KO_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        mock_response = {"status_code": 500, "body": "error"}
        test_velocloud_client.get_edge_information = Mock(return_value=mock_response)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        edge_info = vr.get_edge_information(edge)

        assert test_velocloud_client.get_edge_information.called
        assert edge_info == mock_response

    def get_link_information_ok_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        link_status = {
            "body": [{"link_data": "STABLE", "linkId": "123", 'link': {'backupState': 'UNCONFIGURED'}}],
            "status_code": 200
        }
        link_service_group = {
            "body": [{"linkId": "123", "serviceGroups": ["PUBLIC_WIRED"]}],
            "status_code": 200
        }
        link_info_return = [{"link_data": "STABLE", "linkId": "123", 'link': {'backupState': 'UNCONFIGURED'},
                             "serviceGroups": ["PUBLIC_WIRED"]}]
        test_velocloud_client.get_link_information = Mock(return_value=link_status)
        test_velocloud_client.get_link_service_groups_information = Mock(return_value=link_service_group)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        interval = "some Interval"
        link_info = vr.get_link_information(edge, interval)
        assert test_velocloud_client.get_link_information.called
        assert test_velocloud_client.get_link_service_groups_information.called
        assert link_info["body"] == link_info_return

    def get_link_information_ko_wrong_id_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        link_status = {
            "body": [{"link_data": "STABLE", "linkId": "123", 'link': {'backupState': 'UNCONFIGURED'}}],
            "status_code": 200
        }
        link_service_group = {
            "body": [{"linkId": "123", "serviceGroups": ["PUBLIC_WIRED"]}],
            "status_code": 200
        }
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

    def get_link_information_ko_different_backup_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        link_status = {"body": [{"link_data": "STABLE", "linkId": "123", 'link': {'backupState': 'STABLE'}}],
                       "status_code": 200}
        link_service_group = {
            "body": [{"linkId": "123", "serviceGroups": ["PUBLIC_WIRED"]}],
            "status_code": 200
        }

        test_velocloud_client.get_link_information = Mock(return_value=link_status)
        test_velocloud_client.get_link_service_groups_information = Mock(return_value=link_service_group)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        interval = "some Interval"
        link_info = vr.get_link_information(edge, interval)
        assert test_velocloud_client.get_link_information.called
        assert test_velocloud_client.get_link_service_groups_information.called
        assert link_info["body"] == []

    def get_link_information_ko_none_link_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        link_status = {"body": None,
                       "status_code": 200}
        link_service_group = {
            "body": [{"linkId": "123", "serviceGroups": ["PUBLIC_WIRED"]}],
            "status_code": 200
        }
        test_velocloud_client.get_link_information = Mock(return_value=link_status)
        test_velocloud_client.get_link_service_groups_information = Mock(return_value=link_service_group)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        interval = "some Interval"
        link_info = vr.get_link_information(edge, interval)

        assert link_info["body"] == []

    def get_link_information_ko_none_link_service_groups_information_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        link_status = {"body": None,
                       "status_code": 200}
        link_service_group = {
            "body": None,
            "status_code": 500
        }
        test_velocloud_client.get_link_information = Mock(return_value=link_status)
        test_velocloud_client.get_link_service_groups_information = Mock(return_value=link_service_group)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        interval = "some Interval"
        link_info = vr.get_link_information(edge, interval)

        assert link_info["body"] == []

    def get_link_information_ko_link_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        link_status = {
            "body": "Got internal error from Velocloud",
            "status_code": 500
        }

        test_velocloud_client.get_link_information = Mock(return_value=link_status)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        interval = "some Interval"
        link_info = vr.get_link_information(edge, interval)

        assert link_info["body"] == "Got internal error from Velocloud"

    def get_enterprise_information_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        enterprise_info = {"body": {"name": "test"},
                           "status_code": 200}
        test_velocloud_client.get_enterprise_information = Mock(return_value=enterprise_info)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        enterprise_info = vr.get_enterprise_information(edge)
        assert test_velocloud_client.get_enterprise_information.called
        assert enterprise_info["body"] == 'test'

    def get_enterprise_information_ko_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        enterprise_info = {"body": None,
                           "status_code": 500}
        test_velocloud_client.get_enterprise_information = Mock(return_value=enterprise_info)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        enterprise_info = vr.get_enterprise_information(edge)
        assert test_velocloud_client.get_enterprise_information.called
        assert enterprise_info["body"] is None

    def get_enterprise_information_without_name_key_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        enterprise_info = {"body": None,
                           "status_code": 200}
        test_velocloud_client.get_enterprise_information = Mock(return_value=enterprise_info)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        enterprise_info = vr.get_enterprise_information(edge)
        assert test_velocloud_client.get_enterprise_information.called
        assert enterprise_info["body"] is None

    def get_all_edge_events_filter_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)

        events = {"body": {"data": [{'event': 'EDGE_UP'}, {'event': 'EDGE_GONE'}]},
                  "status_code": 200}
        filter_events_status_list = ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD']

        test_velocloud_client.get_all_edge_events = Mock(return_value=events)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        start = datetime.now() - timedelta(hours=24)
        end = datetime.now()
        limit = None
        edge_events = vr.get_all_edge_events(edge, start, end, limit, filter_events_status_list)
        assert test_velocloud_client.get_all_edge_events.called
        assert edge_events == {"body": [{'event': 'EDGE_UP'}], "status_code": 200}

    def get_all_edge_events_none_filter_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)

        events = {"body": {"data": [{'event': 'EDGE_UP'}, {'event': 'EDGE_GONE'}]},
                  "status_code": 200}
        filter_events_status_list = None

        test_velocloud_client.get_all_edge_events = Mock(return_value=events)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        start = datetime.now() - timedelta(hours=24)
        end = datetime.now()
        limit = None
        edge_events = vr.get_all_edge_events(edge, start, end, limit, filter_events_status_list)
        assert test_velocloud_client.get_all_edge_events.called
        assert edge_events == {"body": [{'event': 'EDGE_UP'}, {'event': 'EDGE_GONE'}], "status_code": 200}

    def get_all_edge_events_none_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)

        events = {"body": None,
                  "status_code": 500}
        filter_events_status_list = None

        test_velocloud_client.get_all_edge_events = Mock(return_value=events)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        start = datetime.now() - timedelta(hours=24)
        end = datetime.now()
        limit = None
        edge_events = vr.get_all_edge_events(edge, start, end, limit, filter_events_status_list)
        assert test_velocloud_client.get_all_edge_events.called
        assert edge_events == {"body": None, "status_code": 500}

    def connect_to_all_servers_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        test_velocloud_client.instantiate_and_connect_clients = Mock()
        vr.connect_to_all_servers()
        assert test_velocloud_client.instantiate_and_connect_clients.called

    def get_all_enterprise_names_with_filter_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        enterprises = {
            "body": [{"enterprise_name": "The Name"}],
            "status_code": 200
        }
        msg = {"request_id": "123", "filter": ["The Name"]}
        test_velocloud_client.get_all_enterprise_names = Mock(
            return_value=enterprises
        )
        enterprise_names = vr.get_all_enterprise_names(msg)

        assert test_velocloud_client.get_all_enterprise_names.called
        assert enterprise_names["body"] == ["The Name"]

    def get_all_enterprise_names_none_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        enterprises = {
            "body": None,
            "status_code": 500
        }
        msg = {"request_id": "123", "filter": []}
        test_velocloud_client.get_all_enterprise_names = Mock(
            return_value=enterprises
        )
        enterprise_names = vr.get_all_enterprise_names(msg)

        assert enterprise_names == {"body": None, "status_code": 500}

    def get_all_enterprise_names_without_filter_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        enterprises = {
            "body": [{"enterprise_name": "The Name"}],
            "status_code": 200
        }
        msg = {"request_id": "123", "filter": []}
        test_velocloud_client.get_all_enterprise_names = Mock(
            return_value=enterprises
        )
        enterprise_names = vr.get_all_enterprise_names(msg)

        assert test_velocloud_client.get_all_enterprise_names.called
        assert enterprise_names["body"] == ["The Name"]
