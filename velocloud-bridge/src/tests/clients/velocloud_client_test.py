from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest
from application.clients.velocloud_client import VelocloudClient
from pytest import raises

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
        configs = testconfig
        logger = Mock()

        host = 'Some url'
        username = 'Some user'
        password = 'Some password'

        response_mock = Mock()

        response_mock.headers = {"Set-Cookie": "Somestring with velocloud.session=secret; "}
        response_mock.status_code = 200
        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            header = velocloud_client._create_headers_by_host(host, username, password)

            mock_post.assert_called_once()
            assert host in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['json'] == dict(username=username, password=password)
            assert header == {"Cookie": 'velocloud.session=secret',
                              "Content-Type": "application/json-patch+json",
                              "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached"
                              }

    def create_headers_by_host_failure_test(self):
        configs = testconfig
        logger = Mock()

        host = 'Some url'
        username = 'Some user'
        password = 'Some password'

        response_mock = Mock()

        response_mock.status_code = 302
        with patch.object(velocloud_client_module.requests, 'post', side_effect=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)

            with raises(Exception):
                header = velocloud_client._create_headers_by_host(host, username, password)
                mock_post.assert_called()
                assert header == ''

    def _get_header_by_host_test(self):
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
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        edge_status = "Some Edge Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = Mock(return_value=edge_status)

        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            velocloud_client._get_header_by_host = Mock(return_value=header)
            velocloud_client._json_return = Mock(return_value=response_mock.json())
            edge_info = velocloud_client.get_edge_information(edge_id)

            mock_post.assert_called_once()
            assert edge_id['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['json'] == {"enterpriseId": edge_id['enterprise_id'],
                                                      "id": edge_id['edge_id']}
            assert mock_post.call_args[1]['headers'] == header['headers']
            assert edge_info == edge_status

    def get_edge_information_ko_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        edge_status = "Some Edge Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = Mock(return_value=edge_status)

        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            velocloud_client._get_header_by_host = Mock(return_value=header)
            velocloud_client._json_return = Mock(return_value=Exception)
            with raises(Exception):
                edge_info = velocloud_client.get_edge_information(edge_id)
                mock_post.assert_called()
                assert edge_info == ''

    def get_link_information_test(self):
        configs = testconfig
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
            velocloud_client._json_return = Mock(return_value=response_mock.json())

            link_info = velocloud_client.get_link_information(edge_id, interval)

            mock_post.assert_called_once()
            assert edge_id['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['json'] == {'enterpriseId': edge_id['enterprise_id'],
                                                      'id': edge_id['edge_id'],
                                                      'interval': interval}
            assert mock_post.call_args[1]['headers'] == header['headers']
            assert link_info == link_status

    def get_link_information_ko_test(self):
        configs = testconfig
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
            velocloud_client._json_return = Mock(return_value=Exception)
            with raises(Exception):
                link_info = velocloud_client.get_link_information(edge_id, interval)
                mock_post.assert_called()
                assert link_info == ''

    def get_link_service_groups_information_test(self):
        configs = testconfig
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
            velocloud_client._json_return = Mock(return_value=response_mock.json())

            link_service_group_info = velocloud_client.get_link_service_groups_information(edge_id, interval)

            mock_post.assert_called_once()
            assert edge_id['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['json'] == {'enterpriseId': edge_id['enterprise_id'],
                                                      'id': edge_id['edge_id'],
                                                      'interval': interval}
            assert mock_post.call_args[1]['headers'] == header['headers']
            assert link_service_group_info == link_service_groups

    def get_link_service_groups_information_ko_test(self):
        configs = testconfig
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
            velocloud_client._json_return = Mock(return_value=Exception)

            with raises(Exception):
                link_service_group_info = velocloud_client.get_link_service_groups_information(edge_id, interval)
                mock_post.assert_called()
                assert link_service_group_info == ''

    def get_enterprise_information_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        enterprise_status = "Some Enterprise Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = Mock(return_value=enterprise_status)

        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            velocloud_client._get_header_by_host = Mock(return_value=header)
            velocloud_client._json_return = Mock(return_value=response_mock.json())

            enterprise_info = velocloud_client.get_enterprise_information(edge_id)

            mock_post.assert_called_once()
            assert edge_id['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['json'] == {'enterpriseId': edge_id['enterprise_id']}
            assert mock_post.call_args[1]['headers'] == header['headers']
            assert enterprise_info == enterprise_status

    def get_enterprise_information_ko_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        enterprise_status = "Some Enterprise Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = Mock(return_value=enterprise_status)

        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            velocloud_client._get_header_by_host = Mock(return_value=header)
            velocloud_client._json_return = Mock(return_value=Exception)

            with raises(Exception):
                enterprise_info = velocloud_client.get_enterprise_information(edge_id)
                mock_post.assert_called()
                assert enterprise_info == ''

    def get_all_event_information_test(self):
        configs = testconfig
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
            velocloud_client._json_return = Mock(return_value=response_mock.json())

            events = velocloud_client.get_all_edge_events(edge_id, interval_start, interval_end, limit)

            mock_post.assert_called_once()
            assert edge_id['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['json'] == {'enterpriseId': edge_id['enterprise_id'],
                                                      'interval': {'start': interval_start, 'end': interval_end},
                                                      'filter': {'limit': limit},
                                                      'edgeId': [edge_id['edge_id']]}
            assert mock_post.call_args[1]['headers'] == header['headers']
            assert events == events_status

    def get_all_event_information_ko_test(self):
        configs = testconfig
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
            velocloud_client._json_return = Mock(return_value=Exception)

            with raises(Exception):
                events = velocloud_client.get_all_edge_events(edge_id, interval_start, interval_end, limit)
                mock_post.assert_called()
                assert events == ''

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

    @pytest.mark.asyncio
    async def get_all_enterprise_edges_with_host_by_serial_haserial_test(self):
        configs = Mock()
        logger = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'}]
        monitoring_aggregates_return = {'enterprises': [{'id': 1}]}
        enterprise_edges_by_id_return = [{'id': 25, 'enterpriseId': 1, 'serialNumber': 'VC0123',
                                          'haSerialNumber': 'VC0234'}]

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client.get_monitoring_aggregates = Mock(return_value=monitoring_aggregates_return)
        velocloud_client.get_all_enterprises_edges_by_id = Mock(return_value=enterprise_edges_by_id_return)
        velocloud_client._clients = clients

        edge_ids_by_serial = await velocloud_client.get_all_enterprises_edges_with_host_by_serial()

        velocloud_client.get_monitoring_aggregates.assert_called_once_with(clients[0])
        velocloud_client.get_all_enterprises_edges_by_id.assert_called_once_with(clients[0], 1)
        assert edge_ids_by_serial == {'VC0123': [{'host': clients[0]['host'],
                                                  'enterprise_id': 1,
                                                  'edge_id': 25}],
                                      'VC0234': [{'host': clients[0]['host'],
                                                  'enterprise_id': 1,
                                                  'edge_id': 25}]
                                      }

    @pytest.mark.asyncio
    async def get_all_enterprise_edges_with_host_by_serial_none_haSerial_test(self):
        configs = Mock()
        logger = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'}]
        monitoring_aggregates_return = {'enterprises': [{'id': 1}]}
        enterprise_edges_by_id_return = [{'id': 25, 'enterpriseId': 1, 'serialNumber': 'VC0123',
                                          'haSerialNumber': None}]

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client.get_monitoring_aggregates = Mock(return_value=monitoring_aggregates_return)
        velocloud_client.get_all_enterprises_edges_by_id = Mock(return_value=enterprise_edges_by_id_return)
        velocloud_client._clients = clients

        edge_ids_by_serial = await velocloud_client.get_all_enterprises_edges_with_host_by_serial()

        velocloud_client.get_monitoring_aggregates.assert_called_once_with(clients[0])
        velocloud_client.get_all_enterprises_edges_by_id.assert_called_once_with(clients[0], 1)
        assert edge_ids_by_serial == {'VC0123': [{'host': clients[0]['host'],
                                                  'enterprise_id': 1,
                                                  'edge_id': 25}, ]
                                      }

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
        configs = testconfig
        logger = Mock()

        clients = {'host': 'some_host2', 'headers': 'some header dict'}
        monitoring_aggregates_return = {'enterprises': [{'id': 1}]}

        response_mock = Mock()
        response_mock.json = Mock(return_value=monitoring_aggregates_return)

        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            velocloud_client._json_return = Mock(return_value=response_mock.json())

            monitoring_aggregates = velocloud_client.get_monitoring_aggregates(clients)

            mock_post.assert_called_once()
            assert clients['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['headers'] == clients['headers']
            assert monitoring_aggregates == monitoring_aggregates_return

    def get_monitoring_aggregates_ko_test(self):
        configs = testconfig
        logger = Mock()

        clients = {'host': 'some_host2', 'headers': 'some header dict'}
        monitoring_aggregates_return = {'enterprises': [{'id': 1}]}

        response_mock = Mock()
        response_mock.json = Mock(return_value=monitoring_aggregates_return)

        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            velocloud_client._json_return = Mock(return_value=response_mock.json())

            with raises(Exception):
                monitoring_aggregates = velocloud_client.get_monitoring_aggregates(clients)
                mock_post.assert_called()
                assert monitoring_aggregates == ''

    def get_all_enterprises_edges_by_id_test(self):
        configs = testconfig
        logger = Mock()

        clients = {'host': 'some_host2', 'headers': 'some header dict'}
        enterprise_id = 42
        enterprise_edge_return = "some list of edges"

        response_mock = Mock()
        response_mock.json = Mock(return_value=enterprise_edge_return)

        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            velocloud_client._json_return = Mock(return_value=response_mock.json())

            list_of_enterprise_edges = velocloud_client.get_all_enterprises_edges_by_id(clients, enterprise_id)

            mock_post.assert_called_once()
            assert mock_post.call_args[1]["json"] == {'enterpriseId': enterprise_id}
            assert clients['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['headers'] == clients['headers']
            assert list_of_enterprise_edges == enterprise_edge_return

    def get_all_enterprises_edges_by_id_ko_test(self):
        configs = testconfig
        logger = Mock()

        clients = {'host': 'some_host2', 'headers': 'some header dict'}
        enterprise_id = 42
        enterprise_edge_return = "some list of edges"

        response_mock = Mock()
        response_mock.json = Mock(return_value=enterprise_edge_return)

        with patch.object(velocloud_client_module.requests, 'post', return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            velocloud_client._json_return = Mock(return_value=response_mock.json())

            with raises(Exception):
                list_of_enterprise_edges = velocloud_client.get_all_enterprises_edges_by_id(clients, enterprise_id)
                mock_post.assert_called()
                assert list_of_enterprise_edges == ''

    def get_all_enterprise_names_test(self):
        configs = Mock()
        logger = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'}]
        monitoring_aggregates_return = {'enterprises': [{'id': 1, 'name': 'A name'}]}

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client.get_monitoring_aggregates = Mock(return_value=monitoring_aggregates_return)
        velocloud_client._clients = clients

        enterprise_names = velocloud_client.get_all_enterprise_names()

        velocloud_client.get_monitoring_aggregates.assert_called_once_with(clients[0])
        assert enterprise_names == [{'enterprise_name': 'A name'}]

    def json_return_ok_test(self):
        configs = testconfig
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()

        response = {'error': {'message': 'tokenError [expired session cookie]'}}
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client.instantiate_and_connect_clients = Mock()

        with raises(Exception):
            json_return = velocloud_client._json_return(response)
            logger.info.assert_called_once()
            velocloud_client.instantiate_and_connect_clients.assert_called_once()
            assert json_return == ''

    def json_return_ko_different_error_test(self):
        configs = testconfig
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()

        response = {'error': {'message': 'another_error'}}
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client.instantiate_and_connect_clients = Mock()
        json_return = velocloud_client._json_return(response)
        logger.error.assert_called_once()
        assert json_return == response

    def json_return_ko_no_error_test(self):
        configs = testconfig
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()

        response = {'edge_status': 'ok'}
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client.instantiate_and_connect_clients = Mock()
        json_return = velocloud_client._json_return(response)
        assert json_return == response

    def json_return_ko_list_test(self):
        configs = testconfig
        logger = Mock()

        response = ['List']
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client.instantiate_and_connect_clients = Mock()
        json_return = velocloud_client._json_return(response)
        assert json_return == response
