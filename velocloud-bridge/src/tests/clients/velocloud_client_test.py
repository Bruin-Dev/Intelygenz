import json
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

from application.clients.velocloud_client import VelocloudClient

from application.clients import velocloud_client as velocloud_client_module
from config import testconfig


class TestVelocloudClient:

    def instance_test(self):
        configs = testconfig
        logger = Mock()
        velocloud_client = VelocloudClient(configs, logger)
        assert velocloud_client._config == configs.VELOCLOUD_CONFIG
        assert velocloud_client._logger == logger
        assert isinstance(velocloud_client._clients, list)

    def instantiate_and_connect_client_test(self):
        configs = testconfig
        logger = Mock()

        server_block = testconfig.VELOCLOUD_CONFIG['servers'][0]
        client = {'host': 'some_host', 'headers': 'some header dict'}
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._create_and_connect_client = Mock(return_value=client)

        velocloud_client.instantiate_and_connect_clients()

        velocloud_client._create_and_connect_client.assert_called_once_with(server_block['url'],
                                                                            server_block['username'],
                                                                            server_block['password'])
        assert velocloud_client._clients == [client]

    def create_and_connect_client_test(self):
        configs = Mock()
        logger = Mock()

        host = 'Some url'
        username = 'Some user'
        password = 'Some password'

        headers = {'Cookie': 'some test cookie'}

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._create_headers_by_host = Mock(return_value=headers)

        client = velocloud_client._create_and_connect_client(host, username, password)

        velocloud_client._create_headers_by_host.assert_called_once_with(host, username, password)
        assert client == {'host': host, 'headers': headers}

    def create_headers_by_host_test(self):
        configs = Mock()
        logger = Mock()

        host = 'Some url'
        username = 'Some user'
        password = 'Some password'

        response_mock = Mock()

        response_mock.headers = {"Set-Cookie": "Somestring with velocloud.session=secret; "}
        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            header = velocloud_client._create_headers_by_host(host, username, password)

            mock_post.assert_called_once()
            assert host in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['data'] == dict(username=username, password=password)
            assert header == {"Cookie": 'velocloud.session=secret',
                              "Content-Type": "application/json-patch+json",
                              "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached"
                              }

    def _get_header_by_host_ok_test(self):
        configs = Mock()
        logger = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'},
                   {'host': 'some_host', 'headers': 'some header dict'}]

        host = 'some_host'
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._clients = clients

        client = velocloud_client._get_header_by_host(host)

        assert client == clients[1]

    def get_edge_information_test(self):
        configs = Mock()
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        edge_status = "Some Edge Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = Mock(return_value=edge_status)

        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            velocloud_client._get_header_by_host = Mock(return_value=header)

            edge_info = velocloud_client.get_edge_information(edge_id)

            mock_post.assert_called_once()
            assert edge_id['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['data'] == json.dumps(dict(enterpriseId=edge_id['enterprise_id'],
                                                                     id=edge_id['edge_id']))
            assert mock_post.call_args[1]['headers'] == header['headers']
            assert edge_info == edge_status

    def get_link_information_test(self):
        configs = Mock()
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval = "Some interval"
        link_status = "Some Link Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = Mock(return_value=link_status)

        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            velocloud_client._get_header_by_host = Mock(return_value=header)

            link_info = velocloud_client.get_link_information(edge_id, interval)

            mock_post.assert_called_once()
            assert edge_id['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['data'] == json.dumps(dict(enterpriseId=edge_id['enterprise_id'],
                                                                     id=edge_id['edge_id'],
                                                                     interval=interval))
            assert mock_post.call_args[1]['headers'] == header['headers']
            assert link_info == link_status

    def get_link_service_groups_information_test(self):
        configs = Mock()
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval = "Some interval"
        link_service_groups = "Some Link service group Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = Mock(return_value=link_service_groups)

        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            velocloud_client._get_header_by_host = Mock(return_value=header)

            link_service_group_info = velocloud_client.get_link_service_groups_information(edge_id, interval)

            mock_post.assert_called_once()
            assert edge_id['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['data'] == json.dumps(dict(enterpriseId=edge_id['enterprise_id'],
                                                                     id=edge_id['edge_id'],
                                                                     interval=interval))
            assert mock_post.call_args[1]['headers'] == header['headers']
            assert link_service_group_info == link_service_groups

    def get_enterprise_information_test(self):
        configs = Mock()
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        enterprise_status = "Some Enterprise Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = Mock(return_value=enterprise_status)

        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            velocloud_client._get_header_by_host = Mock(return_value=header)

            enterprise_info = velocloud_client.get_enterprise_information(edge_id)

            mock_post.assert_called_once()
            assert edge_id['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['data'] == json.dumps(dict(enterpriseId=edge_id['enterprise_id']))
            assert mock_post.call_args[1]['headers'] == header['headers']
            assert enterprise_info == enterprise_status

    def get_all_event_information_test(self):
        configs = Mock()
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval_start = "Some interval start time"
        interval_end = "Some interval end time"
        limit = "some_limit"
        events_status = "Some Enterprise Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = Mock(return_value=events_status)

        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            velocloud_client._get_header_by_host = Mock(return_value=header)

            events = velocloud_client.get_all_edge_events(edge_id, interval_start, interval_end, limit)

            mock_post.assert_called_once()
            assert edge_id['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['data'] == json.dumps(dict(enterpriseId=edge_id['enterprise_id'],
                                                                     interval=dict(start=interval_start,
                                                                                   end=interval_end),
                                                                     filter=dict(limit=limit),
                                                                     edgeId=[edge_id['edge_id']]))
            assert mock_post.call_args[1]['headers'] == header['headers']
            assert events == events_status

    def get_all_enterprise_edges_with_host_test(self):
        configs = Mock()
        logger = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'}]
        monitoring_aggregates_return = {'enterprises': [{'id': 1}]}
        enterprise_edges_by_id_return = [{'id': 25}]

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client.get_monitoring_aggregates = Mock(return_value=monitoring_aggregates_return)
        velocloud_client.get_all_enterprises_edges_by_id = Mock(return_value=enterprise_edges_by_id_return)
        velocloud_client._clients = clients

        edge_ids = velocloud_client.get_all_enterprises_edges_with_host()

        velocloud_client.get_monitoring_aggregates.assert_called_once_with(clients[0])
        velocloud_client.get_all_enterprises_edges_by_id.assert_called_once_with(clients[0], 1)
        assert edge_ids == [{'host': clients[0]['host'],
                             'enterprise_id': 1,
                             'edge_id': 25}]

    def get_all_hosts_count_test(self):
        configs = Mock()
        logger = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'},
                   {'host': 'some_host', 'headers': 'some header dict'}]
        monitoring_aggregates_return = [{"edgeCount": 25}, {"edgeCount": 24}]

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client.get_monitoring_aggregates = Mock(side_effect=monitoring_aggregates_return)
        velocloud_client._clients = clients

        sum_of_edges = velocloud_client.get_all_hosts_edge_count()

        velocloud_client.get_monitoring_aggregates.assert_has_calls([
                                                                    call(clients[0]),
                                                                    call(clients[1])])
        assert sum_of_edges == 49

    def get_monitoring_aggregates_test(self):
        configs = Mock()
        logger = Mock()

        clients = {'host': 'some_host2', 'headers': 'some header dict'}
        monitoring_aggregates_return = {'enterprises': [{'id': 1}]}

        response_mock = Mock()
        response_mock.json = Mock(return_value=monitoring_aggregates_return)

        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)

            monitoring_aggregates = velocloud_client.get_monitoring_aggregates(clients)

            mock_post.assert_called_once()
            assert clients['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['headers'] == clients['headers']
            assert monitoring_aggregates == monitoring_aggregates_return

    def get_all_enterprises_edges_by_id_test(self):
        configs = Mock()
        logger = Mock()

        clients = {'host': 'some_host2', 'headers': 'some header dict'}
        enterprise_id = 42
        enterprise_edge_return = "some list of edges"

        response_mock = Mock()
        response_mock.json = Mock(return_value=enterprise_edge_return)

        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)

            list_of_enterprise_edges = velocloud_client.get_all_enterprises_edges_by_id(clients, 42)

            mock_post.assert_called_once()
            assert mock_post.call_args[1]["data"] == json.dumps(dict(enterpriseId=enterprise_id))
            assert clients['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['headers'] == clients['headers']
            assert list_of_enterprise_edges == enterprise_edge_return
