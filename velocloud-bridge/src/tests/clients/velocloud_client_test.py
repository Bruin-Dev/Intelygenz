from unittest.mock import Mock
from asynctest import CoroutineMock
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

    @pytest.mark.asyncio
    async def instantiate_and_connect_client_test(self):
        configs = testconfig
        logger = Mock()

        server_block = testconfig.VELOCLOUD_CONFIG['servers'][0]
        client = {'host': 'some_host', 'headers': 'some header dict'}
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._create_and_connect_client = CoroutineMock(return_value=client)

        await velocloud_client.instantiate_and_connect_clients()

        velocloud_client._create_and_connect_client.assert_called_once_with(server_block['url'],
                                                                            server_block['username'],
                                                                            server_block['password'])
        assert velocloud_client._clients == [client]

    @pytest.mark.asyncio
    async def create_and_connect_client_ok_test(self):
        configs = Mock()
        logger = Mock()

        host = 'Some url'
        username = 'Some user'
        password = 'Some password'

        headers = {
            "body": {'Cookie': 'some test cookie'},
            "status": 200
        }

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._create_headers_by_host = CoroutineMock(return_value=headers)

        client = await velocloud_client._create_and_connect_client(host, username, password)

        velocloud_client._create_headers_by_host.assert_called_once_with(host, username, password)
        assert client == {'host': host, 'headers': headers['body']}

    @pytest.mark.asyncio
    async def create_and_connect_client_ko_test(self):
        configs = Mock()
        logger = Mock()

        host = 'Some url'
        username = 'Some user'
        password = 'Some password'

        headers = {
            "body": f"Got internal error from Velocloud",
            "status": 500
        }

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._create_headers_by_host = CoroutineMock(return_value=headers)

        client = await velocloud_client._create_and_connect_client(host, username, password)

        velocloud_client._create_headers_by_host.assert_called_once_with(host, username, password)
        assert client is None

    @pytest.mark.asyncio
    async def create_headers_by_host_test(self):
        configs = testconfig
        logger = Mock()

        host = 'Some url'
        username = 'Some user'
        password = 'Some password'

        response_mock = CoroutineMock()
        response_mock.headers = {"Set-Cookie": "Somestring with velocloud.session=secret;"}
        response_mock.status = 200

        velocloud_client = VelocloudClient(configs, logger)
        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            header = await velocloud_client._create_headers_by_host(host, username, password)

            mock_post.assert_called_once()
            assert host in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['json'] == dict(username=username, password=password)
            assert header["body"]["Content-Type"] == "application/json-patch+json"
            assert header["body"]["Cache-control"] == "no-cache, no-store, no-transform, max-age=0, only-if-cached"
            assert header["body"]["Cookie"] == 'velocloud.session=secret'

    @pytest.mark.asyncio
    async def create_headers_by_host_error_401_test(self):
        configs = testconfig
        logger = Mock()

        host = 'Some url'
        username = 'Some user'
        password = 'Some password'

        response_mock = Mock()
        expected_header = {
            "body": f"Token Error",
            "status": 302
        }

        response_mock.status_code = 302
        response_mock.json = CoroutineMock(return_value={})
        velocloud_client = VelocloudClient(configs, logger)
        with patch.object(velocloud_client._session, 'post', return_value=response_mock) as mock_post:
            velocloud_client.instantiate_and_connect_clients = Mock()
            with pytest.raises(Exception):
                header = velocloud_client._create_headers_by_host(host, username, password)
                velocloud_client.instantiate_and_connect_clients.assert_called()
                mock_post.assert_called()
                assert header == expected_header

    @pytest.mark.asyncio
    async def relogin_client_test(self):
        configs = testconfig
        logger = Mock()

        host = 'someurl'
        client = {'host': 'someurl', 'headers': 'new header'}
        initial_clients = [{'host': 'some_host2', 'headers': 'some header dict'},
                           {'host': 'someurl', 'headers': 'some header dict'}]
        final_clients = [{'host': 'some_host2', 'headers': 'some header dict'},
                         client]
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._create_and_connect_client = CoroutineMock(return_value=client)
        velocloud_client._clients = initial_clients

        await velocloud_client._relogin_client(host)

        assert velocloud_client._clients == final_clients

    @pytest.mark.asyncio
    async def relogin_client_host_not_in_initial_clients_list_test(self):
        configs = testconfig
        logger = Mock()

        host = 'someurl'
        client = {'host': 'someurl', 'headers': 'new header'}
        initial_clients = [{'host': 'some_host2', 'headers': 'some header dict'}]
        final_clients = [{'host': 'some_host2', 'headers': 'some header dict'},
                         client]
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._create_and_connect_client = CoroutineMock(return_value=client)
        velocloud_client._clients = initial_clients

        await velocloud_client._relogin_client(host)

        assert velocloud_client._clients == final_clients

    @pytest.mark.asyncio
    async def _get_header_by_host_test(self):
        configs = Mock()
        logger = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'},
                   {'host': 'some_host', 'headers': 'some header dict'}]

        host = 'some_host'
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._clients = clients

        client = velocloud_client._get_header_by_host(host)

        assert client == clients[1]

    @pytest.mark.asyncio
    async def _get_header_by_host_no_client_found_test(self):
        configs = Mock()
        logger = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'},
                   {'host': 'some_host', 'headers': 'some header dict'}]

        host = 'some_host3'
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._clients = clients

        client = velocloud_client._get_header_by_host(host)

        assert client is None

    @pytest.mark.asyncio
    async def get_edge_information_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        edge_status = "Some Edge Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=edge_status)
        response_mock.status = 200
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=header)
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            edge_info = await velocloud_client.get_edge_information(edge_id)

            mock_post.assert_called_once()
            assert edge_id['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['json'] == {"enterpriseId": edge_id['enterprise_id'],
                                                      "id": edge_id['edge_id']}
            assert mock_post.call_args[1]['headers'] == header['headers']
            assert edge_info["body"] == edge_status
            assert edge_info["status"] == 200

    @pytest.mark.asyncio
    async def get_edge_information_error_400_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        edge_status = "Some Edge Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=edge_status)
        response_mock.status = 400

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=header)
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            edge_info = await velocloud_client.get_edge_information(edge_id)

            mock_post.assert_called_once()
            assert edge_info == {"body": edge_status, "status": 400}

    @pytest.mark.asyncio
    async def get_edge_information_error_404_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        edge_status = "Some Edge Information"

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=edge_status)
        response_mock.status = 400

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._relogin_client = CoroutineMock()
        velocloud_client._get_header_by_host = Mock(return_value=None)
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            edge_info = await velocloud_client.get_edge_information(edge_id)

            mock_post.assert_not_called()
            velocloud_client._relogin_client.assert_awaited_once()
            assert edge_info["body"] == f'Cannot find a client to connect to {edge_id["host"]}'
            assert edge_info["status"] == 404

    @pytest.mark.asyncio
    async def get_edge_information_error_500_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}

        response_mock = Mock()
        response_mock.status = 500
        response_mock.json = CoroutineMock(return_value={})
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._relogin_client = CoroutineMock()
        velocloud_client._get_header_by_host = Mock(return_value={"headers": ""})

        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            edge_information = await velocloud_client.get_edge_information(edge_id)
            assert edge_information == {"body": 'Got internal error from Velocloud', "status": 500}

    @pytest.mark.asyncio
    async def get_link_information_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval = "Some interval"
        link_status = "Some Link Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=link_status)
        response_mock.status = 200

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=header)
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            link_info = await velocloud_client.get_link_information(edge_id, interval)

            mock_post.assert_called_once()

            assert edge_id['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['json'] == {'enterpriseId': edge_id['enterprise_id'],
                                                      'id': edge_id['edge_id'],
                                                      'interval': interval}
            assert mock_post.call_args[1]['headers'] == header['headers']
            assert link_info["body"] == link_status

    @pytest.mark.asyncio
    async def get_link_information_error_400_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval = "Some interval"
        link_status = "error"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=link_status)
        response_mock.status = 400

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=header)

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            link_info = await velocloud_client.get_link_information(edge_id, interval)
            mock_post.assert_called_once()

            assert link_info["status"] == 400
            assert link_info["body"] == link_status

    @pytest.mark.asyncio
    async def get_link_information_error_404_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval = "Some interval"
        link_status = "error"

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=link_status)
        response_mock.status = 400

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=None)
        velocloud_client._relogin_client = CoroutineMock()

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            link_info = await velocloud_client.get_link_information(edge_id, interval)
            mock_post.assert_not_called()
            velocloud_client._relogin_client.assert_awaited_once()

            assert link_info["status"] == 404
            assert link_info["body"] == f'Cannot find a client to connect to {edge_id["host"]}'

    @pytest.mark.asyncio
    async def get_link_information_error_500_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval = "Some interval"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.status = 500

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=header)

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            link_info = await velocloud_client.get_link_information(edge_id, interval)
            mock_post.assert_called()
            assert link_info["status"] == 500
            assert link_info["body"] == "Got internal error from Velocloud"

    @pytest.mark.asyncio
    async def get_link_information_ko_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval = "Some interval"
        link_status = "Some Link Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=link_status)

        with patch.object(velocloud_client_module.aiohttp.ClientSession(), 'post',
                          return_value=response_mock) as mock_post:
            velocloud_client = VelocloudClient(configs, logger)
            velocloud_client._get_header_by_host = Mock(return_value=header)
            velocloud_client._json_return = Mock(return_value=Exception)
            with raises(Exception):
                link_info = velocloud_client.get_link_information(edge_id, interval)
                mock_post.assert_called()
                assert link_info == ''

    @pytest.mark.asyncio
    async def get_link_service_groups_information_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval = "Some interval"
        link_service_groups = "Some Link service group Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=link_service_groups)
        response_mock.status = 200

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=header)

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            velocloud_client._json_return = Mock(return_value=response_mock.json())

            link_service_group_info = await velocloud_client.get_link_service_groups_information(edge_id, interval)

            mock_post.assert_called_once()
            assert edge_id['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['json'] == {'enterpriseId': edge_id['enterprise_id'],
                                                      'id': edge_id['edge_id'],
                                                      'interval': interval}
            assert mock_post.call_args[1]['headers'] == header['headers']
            assert link_service_group_info["body"] == link_service_groups

    @pytest.mark.asyncio
    async def get_link_service_groups_information_error_400_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval = "Some interval"
        edge_status = "Some Edge Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=edge_status)
        response_mock.status = 400

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=header)
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            link_service_group_info = await velocloud_client.get_link_service_groups_information(edge_id, interval)

            mock_post.assert_called_once()
            assert link_service_group_info == {"body": edge_status, "status": 400}

    @pytest.mark.asyncio
    async def get_link_service_groups_information_error_404_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval = "Some interval"
        edge_status = "Some Edge Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=edge_status)
        response_mock.status = 400

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=None)
        velocloud_client._json_return = Mock(return_value=response_mock.json())
        velocloud_client._relogin_client = CoroutineMock()

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            link_service_group_info = await velocloud_client.get_link_service_groups_information(edge_id, interval)

            mock_post.assert_not_called()
            velocloud_client._relogin_client.assert_awaited_once()

            assert link_service_group_info["status"] == 404
            assert link_service_group_info["body"] == f'Cannot find a client to connect to {edge_id["host"]}'

    @pytest.mark.asyncio
    async def get_link_service_groups_information_error_500_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval = "Some interval"

        response_mock = Mock()
        response_mock.status = 500
        response_mock.json = CoroutineMock(return_value={})
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._relogin_client = CoroutineMock()
        velocloud_client._get_header_by_host = Mock(return_value={"headers": ""})
        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            link_service_group_info = await velocloud_client.get_link_service_groups_information(edge_id, interval)
            assert link_service_group_info == {"body": 'Got internal error from Velocloud', "status": 500}

    @pytest.mark.asyncio
    async def get_link_service_groups_information_ko_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval = "Some interval"
        link_service_groups = "Some Link service group Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=link_service_groups)

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=header)
        velocloud_client._json_return = Mock(return_value=Exception)

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            with raises(Exception):
                link_service_group_info = await velocloud_client.get_link_service_groups_information(edge_id, interval)
                mock_post.assert_called()
                assert link_service_group_info == ''

    @pytest.mark.asyncio
    async def get_enterprise_information_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        enterprise_status = "Some Enterprise Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=enterprise_status)
        response_mock.status = 200

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=header)
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            enterprise_info = await velocloud_client.get_enterprise_information(edge_id)

            mock_post.assert_called_once()
            assert edge_id['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['json'] == {'enterpriseId': edge_id['enterprise_id']}
            assert mock_post.call_args[1]['headers'] == header['headers']
            assert enterprise_info["body"] == enterprise_status

    @pytest.mark.asyncio
    async def get_enterprise_information_error_400_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        edge_status = "Some Edge Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=edge_status)
        response_mock.status = 400

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=header)
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            edge_info = await velocloud_client.get_enterprise_information(edge_id)

            mock_post.assert_called_once()
            assert edge_info == {"body": edge_status, "status": 400}

    @pytest.mark.asyncio
    async def get_enterprise_information_error_404_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        edge_status = "Some Edge Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=edge_status)
        response_mock.status = 400

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=None)
        velocloud_client._json_return = Mock(return_value=response_mock.json())
        velocloud_client._relogin_client = CoroutineMock()

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            edge_info = await velocloud_client.get_enterprise_information(edge_id)

            mock_post.assert_not_called()
            velocloud_client._relogin_client.assert_awaited_once()

            assert edge_info["status"] == 404
            assert edge_info["body"] == f'Cannot find a client to connect to {edge_id["host"]}'

    @pytest.mark.asyncio
    async def get_enterprise_information_error_500_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}

        response_mock = Mock()
        response_mock.status = 500
        response_mock.json = CoroutineMock(return_value={})
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._relogin_client = CoroutineMock()
        velocloud_client._get_header_by_host = Mock(return_value={"headers": ""})
        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            edge_information = await velocloud_client.get_enterprise_information(edge_id)
            assert edge_information == {"body": 'Got internal error from Velocloud', "status": 500}

    @pytest.mark.asyncio
    async def get_all_event_information_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval_start = "Some interval start time"
        interval_end = "Some interval end time"
        limit = "some_limit"
        events_status = "Some Enterprise Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=events_status)
        response_mock.status = 200

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=header)
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            events = await velocloud_client.get_all_edge_events(edge_id, interval_start, interval_end, limit)

            mock_post.assert_called_once()
            assert edge_id['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['json'] == {'enterpriseId': edge_id['enterprise_id'],
                                                      'interval': {'start': interval_start, 'end': interval_end},
                                                      'filter': {'limit': limit},
                                                      'edgeId': [edge_id['edge_id']]}
            assert mock_post.call_args[1]['headers'] == header['headers']
            assert events["body"] == events_status

    @pytest.mark.asyncio
    async def get_all_event_information_error_400_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval_start = "Some interval start time"
        interval_end = "Some interval end time"
        limit = "some_limit"
        events_status = "Some Enterprise Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=events_status)
        response_mock.status = 400

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=header)
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            events = await velocloud_client.get_all_edge_events(edge_id, interval_start, interval_end, limit)

            mock_post.assert_called_once()
            assert events["body"] == events_status

    @pytest.mark.asyncio
    async def get_all_event_information_error_404_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval_start = "Some interval start time"
        interval_end = "Some interval end time"
        limit = "some_limit"
        events_status = "Some Enterprise Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=events_status)
        response_mock.status = 400

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=None)
        velocloud_client._json_return = Mock(return_value=response_mock.json())
        velocloud_client._relogin_client = CoroutineMock()

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            events = await velocloud_client.get_all_edge_events(edge_id, interval_start, interval_end, limit)

            mock_post.assert_not_called()
            velocloud_client._relogin_client.assert_awaited_once()

            assert events["status"] == 404
            assert events["body"] == f'Cannot find a client to connect to {edge_id["host"]}'

    @pytest.mark.asyncio
    async def get_get_all_event_information_error_500_test(self):
        configs = testconfig
        logger = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval_start = "Some interval start time"
        interval_end = "Some interval end time"
        limit = "some_limit"
        events_status = "Some Enterprise Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.status = 500
        response_mock.json = CoroutineMock(return_value={})

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._get_header_by_host = Mock(return_value=header)
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            events = await velocloud_client.get_all_edge_events(edge_id, interval_start, interval_end, limit)

            assert events == {"body": 'Got internal error from Velocloud', "status": 500}

    @pytest.mark.asyncio
    async def get_all_enterprise_edges_with_host_test(self):
        configs = Mock()
        logger = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'},
                   {'host': 'some_host3', 'headers': 'some header dict3'},
                   {'host': 'some_host4', 'headers': 'some header dict4'}]
        monitoring_aggregates_return = [
            {
                "body": {'enterprises': [{'id': 1}]},
                "status": 200
            },
            {
                "body": {'enterprises': []},
                "status": 200
            },
            {
                "body": {'enterprises': [{'id': 2}]},
                "status": 200
            }

        ]
        enterprise_edges_by_id_return = [{
            "body": [{'id': 25}],
            "status": 200
        },
            {
                "body": [{'id': 26}],
                "status": 200
            }
        ]

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client.get_monitoring_aggregates = CoroutineMock(side_effect=monitoring_aggregates_return)
        velocloud_client.get_all_enterprises_edges_by_id = CoroutineMock(side_effect=enterprise_edges_by_id_return)
        velocloud_client._clients = clients

        edge_ids = await velocloud_client.get_all_enterprises_edges_with_host(filter=dict())

        velocloud_client.get_monitoring_aggregates.assert_has_calls([call(clients[0]), call(clients[1]),
                                                                     call(clients[2])])
        velocloud_client.get_all_enterprises_edges_by_id.assert_has_calls([call(clients[0], 1)])
        assert edge_ids["body"] == [{'host': clients[0]['host'], 'enterprise_id': 1, 'edge_id': 25},
                                    {'host': clients[2]['host'], 'enterprise_id': 2, 'edge_id': 26}]

    @pytest.mark.asyncio
    async def get_all_enterprise_edges_with_host_by_serial_haserial_test(self):
        configs = Mock()
        logger = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'}]
        monitoring_aggregates_return = {
            "body": {'enterprises': [{'id': 1}]},
            "status": 200
        }
        enterprise_edges_by_id_return = {
            "body": [{'id': 25, 'enterpriseId': 1, 'serialNumber': 'VC0123',
                      'haSerialNumber': 'VC0234'}],
            "status": 200}

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client.get_monitoring_aggregates = CoroutineMock(return_value=monitoring_aggregates_return)
        velocloud_client.get_all_enterprises_edges_by_id = CoroutineMock(return_value=enterprise_edges_by_id_return)
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
        monitoring_aggregates_return = {
            "body": {'enterprises': [{'id': 1}]},
            "status": 200
        }
        enterprise_edges_by_id_return = {
            "body": [{'id': 25, 'enterpriseId': 1, 'serialNumber': 'VC0123',
                      'haSerialNumber': None}],
            "status": 200
        }

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client.get_monitoring_aggregates = CoroutineMock(return_value=monitoring_aggregates_return)
        velocloud_client.get_all_enterprises_edges_by_id = CoroutineMock(return_value=enterprise_edges_by_id_return)
        velocloud_client._clients = clients

        edge_ids_by_serial = await velocloud_client.get_all_enterprises_edges_with_host_by_serial()

        velocloud_client.get_monitoring_aggregates.assert_called_once_with(clients[0])
        velocloud_client.get_all_enterprises_edges_by_id.assert_called_once_with(clients[0], 1)
        assert edge_ids_by_serial == {'VC0123': [{'host': clients[0]['host'],
                                                  'enterprise_id': 1,
                                                  'edge_id': 25}, ]
                                      }

    @pytest.mark.asyncio
    async def get_all_hosts_count_test(self):
        configs = Mock()
        logger = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'},
                   {'host': 'some_host', 'headers': 'some header dict'}]
        monitoring_aggregates1 = {
            "body": {"edgeCount": 25},
            "status": 200
        }
        monitoring_aggregates2 = {
            "body": {"edgeCount": 24},
            "status": 200
        }

        monitoring_aggregates_return = [monitoring_aggregates1, monitoring_aggregates2]
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client.get_monitoring_aggregates = CoroutineMock(side_effect=monitoring_aggregates_return)
        velocloud_client._clients = clients

        sum_of_edges = await velocloud_client.get_all_hosts_edge_count()

        velocloud_client.get_monitoring_aggregates.assert_has_calls([
            call(clients[0]),
            call(clients[1])])
        assert sum_of_edges == 49

    @pytest.mark.asyncio
    async def get_all_hosts_count_0_result_test(self):
        configs = Mock()
        logger = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'},
                   {'host': 'some_host', 'headers': 'some header dict'}]
        monitoring_aggregates1 = {
            "body": None,
            "status": 500
        }
        monitoring_aggregates2 = {
            "body": None,
            "status": 500
        }

        monitoring_aggregates_return = [monitoring_aggregates1, monitoring_aggregates2]
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client.get_monitoring_aggregates = CoroutineMock(side_effect=monitoring_aggregates_return)
        velocloud_client._clients = clients

        sum_of_edges = await velocloud_client.get_all_hosts_edge_count()

        velocloud_client.get_monitoring_aggregates.assert_has_calls([
            call(clients[0]),
            call(clients[1])])
        assert sum_of_edges == 0

    @pytest.mark.asyncio
    async def get_monitoring_aggregates_test(self):
        configs = testconfig
        logger = Mock()

        clients = {'host': 'some_host2', 'headers': 'some header dict'}
        monitoring_aggregates_return = {'enterprises': [{'id': 1}]}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=monitoring_aggregates_return)
        response_mock.status = 200

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            monitoring_aggregates = await velocloud_client.get_monitoring_aggregates(clients)

            mock_post.assert_called_once()
            assert clients['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['headers'] == clients['headers']
            assert monitoring_aggregates["body"] == monitoring_aggregates_return

    @pytest.mark.asyncio
    async def get_monitoring_aggregates_error_400_test(self):
        configs = testconfig
        logger = Mock()

        clients = {'host': 'some_host2', 'headers': 'some header dict'}
        monitoring_aggregates_return = "some value"

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=monitoring_aggregates_return)
        response_mock.status = 400

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            monitoring_aggregates = await velocloud_client.get_monitoring_aggregates(clients)

            mock_post.assert_called_once()

            assert monitoring_aggregates == {"body": monitoring_aggregates_return,
                                             "status": 400}

    @pytest.mark.asyncio
    async def get_monitoring_aggregates_error_500_test(self):
        configs = testconfig
        logger = Mock()

        clients = {'host': 'some_host2', 'headers': 'some header dict'}
        monitoring_aggregates_return = "some value"

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=monitoring_aggregates_return)
        response_mock.status = 500

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            monitoring_aggregates = await velocloud_client.get_monitoring_aggregates(clients)

            assert monitoring_aggregates == {"body": "Got internal error from Velocloud", "status": 500}

    @pytest.mark.asyncio
    async def get_all_enterprises_edges_by_id_test(self):
        configs = testconfig
        logger = Mock()

        clients = {'host': 'some_host2', 'headers': 'some header dict'}
        enterprise_id = 42
        enterprise_edge_return = "some list of edges"

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=enterprise_edge_return)
        response_mock.status = 200

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            list_of_enterprise_edges = await velocloud_client.get_all_enterprises_edges_by_id(clients, enterprise_id)

            mock_post.assert_called_once()
            assert mock_post.call_args[1]["json"] == {'enterpriseId': enterprise_id}
            assert clients['host'] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]['headers'] == clients['headers']
            assert list_of_enterprise_edges["body"] == enterprise_edge_return

    @pytest.mark.asyncio
    async def get_all_enterprises_edges_by_id_error_400_test(self):
        configs = testconfig
        logger = Mock()

        clients = {'host': 'some_host2', 'headers': 'some header dict'}
        enterprise_id = 42
        enterprise_edge_return = "some list of edges"

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=enterprise_edge_return)
        response_mock.status = 400

        velocloud_client = VelocloudClient(configs, logger)
        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            list_of_enterprise_edges = await velocloud_client.get_all_enterprises_edges_by_id(clients, enterprise_id)
            mock_post.assert_called_once()

            assert list_of_enterprise_edges == {"body": enterprise_edge_return, "status": 400}

    @pytest.mark.asyncio
    async def get_all_enterprises_edges_by_id_error_500_test(self):
        configs = testconfig
        logger = Mock()

        clients = {'host': 'some_host2', 'headers': 'some header dict'}
        enterprise_id = 42
        enterprise_edge_return = "some list of edges"

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=enterprise_edge_return)
        response_mock.status = 500
        velocloud_client = VelocloudClient(configs, logger)

        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            list_of_enterprise_edges = await velocloud_client.get_all_enterprises_edges_by_id(clients, enterprise_id)

            assert list_of_enterprise_edges == {"body": 'Got internal error from Velocloud', "status": 500}

    @pytest.mark.asyncio
    async def get_all_enterprise_names_test(self):
        configs = Mock()
        logger = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'}]
        monitoring_aggregates_return = {
            "body": {'enterprises': [{'id': 1, 'name': 'A name'}]},
            "status": 200
        }

        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client.get_monitoring_aggregates = CoroutineMock(return_value=monitoring_aggregates_return)
        velocloud_client._clients = clients

        enterprise_names = await velocloud_client.get_all_enterprise_names()

        velocloud_client.get_monitoring_aggregates.assert_called_once_with(clients[0])
        assert enterprise_names["body"] == [{'enterprise_name': 'A name'}]

    @pytest.mark.asyncio
    async def json_return_ok_test(self):
        configs = testconfig
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()

        host = 'some_host'
        response = {'error': {'message': 'tokenError [expired session cookie]'}}
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._relogin_client = CoroutineMock()

        with raises(Exception):
            json_return = await velocloud_client._json_return(response, host)
            logger.info.assert_called_once()
            velocloud_client._relogin_client.assert_called_once()
            assert json_return == ''

    @pytest.mark.asyncio
    async def json_return_ko_different_error_test(self):
        configs = testconfig
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()

        host = 'some_host'
        response = {'error': {'message': 'another_error'}}
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._relogin_client = CoroutineMock()
        json_return = await velocloud_client._json_return(response, host)
        logger.error.assert_called_once()
        assert json_return == response

    @pytest.mark.asyncio
    async def json_return_ko_no_error_test(self):
        configs = testconfig
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()

        host = 'some_host'
        response = {'edge_status': 'ok'}
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._relogin_client = CoroutineMock()
        json_return = await velocloud_client._json_return(response, host)
        assert json_return == response

    @pytest.mark.asyncio
    async def json_return_ko_list_test(self):
        configs = testconfig
        logger = Mock()

        host = 'some_host'
        response = ['List']
        velocloud_client = VelocloudClient(configs, logger)
        velocloud_client._relogin_client = CoroutineMock()
        json_return = await velocloud_client._json_return(response, host)
        assert json_return == response
