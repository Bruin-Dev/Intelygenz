from datetime import datetime
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest

from aiohttp import ClientConnectionError
from apscheduler.jobstores.base import ConflictingIdError
from asynctest import CoroutineMock
from pytest import raises

from application.clients import velocloud_client as velocloud_client_module
from application.clients.velocloud_client import VelocloudClient
from config import testconfig


class TestVelocloudClient:

    def instance_test(self):
        configs = testconfig
        logger = Mock()
        scheduler = Mock()
        velocloud_client = VelocloudClient(configs, logger, scheduler)
        assert velocloud_client._config == configs.VELOCLOUD_CONFIG
        assert velocloud_client._logger == logger
        assert velocloud_client._scheduler == scheduler
        assert isinstance(velocloud_client._clients, list)

    @pytest.mark.asyncio
    async def instantiate_and_connect_client_test(self):
        configs = testconfig
        logger = Mock()
        scheduler = Mock()

        server_block = testconfig.VELOCLOUD_CONFIG['servers'][0]
        client = {'host': 'some_host', 'headers': 'some header dict'}
        velocloud_client = VelocloudClient(configs, logger, scheduler)
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
        scheduler = Mock()

        host = 'Some url'
        username = 'Some user'
        password = 'Some password'

        headers = {
            "body": {'Cookie': 'some test cookie'},
            "status": 200
        }

        velocloud_client = VelocloudClient(configs, logger, scheduler)
        velocloud_client._create_headers_by_host = CoroutineMock(return_value=headers)

        client = await velocloud_client._create_and_connect_client(host, username, password)

        velocloud_client._create_headers_by_host.assert_called_once_with(host, username, password)
        assert client == {'host': host, 'headers': headers['body']}

    @pytest.mark.asyncio
    async def create_and_connect_client_ko_test(self):
        configs = Mock()
        logger = Mock()
        scheduler = Mock()

        host = 'Some url'
        username = 'Some user'
        password = 'Some password'

        headers = {
            "body": f"Got internal error from Velocloud",
            "status": 500
        }

        expected_client = {
            'headers': {},
            'host': 'Some url'
        }

        velocloud_client = VelocloudClient(configs, logger, scheduler)
        velocloud_client._create_headers_by_host = CoroutineMock(return_value=headers)

        client = await velocloud_client._create_and_connect_client(host, username, password)

        velocloud_client._create_headers_by_host.assert_called_once_with(host, username, password)
        assert client == expected_client

    @pytest.mark.asyncio
    async def create_headers_by_host_test(self):
        configs = testconfig
        logger = Mock()
        scheduler = Mock()

        host = 'Some url'
        username = 'Some user'
        password = 'Some password'

        response_mock = CoroutineMock()
        response_mock.headers = {"Set-Cookie": "Somestring with velocloud.session=secret;"}
        response_mock.status = 200

        velocloud_client = VelocloudClient(configs, logger, scheduler)
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
        scheduler = Mock()

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
        velocloud_client = VelocloudClient(configs, logger, scheduler)
        with patch.object(velocloud_client._session, 'post', return_value=response_mock) as mock_post:
            velocloud_client.instantiate_and_connect_clients = Mock()
            with pytest.raises(Exception):
                header = velocloud_client._create_headers_by_host(host, username, password)
                velocloud_client.instantiate_and_connect_clients.assert_called()
                mock_post.assert_called()
                assert header == expected_header

    @pytest.mark.asyncio
    async def start_relogin_job_ok_test(self):
        configs = testconfig
        logger = Mock()
        scheduler = Mock()

        host = 'someurl'
        params = {'host': host}
        velocloud_client = VelocloudClient(configs, logger, scheduler)
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(velocloud_client_module, 'datetime', new=datetime_mock):
            with patch.object(velocloud_client_module, 'timezone', new=Mock()):
                await velocloud_client._start_relogin_job(host)

        scheduler.add_job.assert_called_once_with(
            velocloud_client._relogin_client,
            'date',
            run_date=next_run_time,
            replace_existing=False, misfire_grace_time=9999,
            id=f'_relogin_client{host}',
            kwargs=params)

    @pytest.mark.asyncio
    async def start_relogin_job_already_executing_test(self):
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        configs = testconfig
        logger = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        host = 'someurl'
        params = {'host': host}
        velocloud_client = VelocloudClient(configs, logger, scheduler)
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)

        try:
            await velocloud_client._start_relogin_job(host)
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                velocloud_client._relogin_client,
                'date',
                run_date=next_run_time,
                replace_existing=False, misfire_grace_time=9999,
                id=f'_relogin_client{host}',
                kwargs=params)

    @pytest.mark.asyncio
    async def relogin_client_test(self):
        configs = testconfig
        logger = Mock()
        scheduler = Mock()

        host = 'someurl'
        client = {'host': 'someurl', 'headers': 'new header'}
        initial_clients = [{'host': 'some_host2', 'headers': 'some header dict'},
                           {'host': 'someurl', 'headers': 'some header dict'}]
        final_clients = [{'host': 'some_host2', 'headers': 'some header dict'},
                         client]
        velocloud_client = VelocloudClient(configs, logger, scheduler)
        velocloud_client._create_and_connect_client = CoroutineMock(return_value=client)
        velocloud_client._clients = initial_clients

        await velocloud_client._relogin_client(host)

        assert velocloud_client._clients == final_clients

    @pytest.mark.asyncio
    async def _get_header_by_host_test(self):
        configs = Mock()
        logger = Mock()
        scheduler = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'},
                   {'host': 'some_host', 'headers': 'some header dict'}]

        host = 'some_host'
        velocloud_client = VelocloudClient(configs, logger, scheduler)
        velocloud_client._clients = clients

        client = velocloud_client._get_header_by_host(host)

        assert client == clients[1]

    @pytest.mark.asyncio
    async def _get_header_by_host_no_client_found_test(self):
        configs = Mock()
        logger = Mock()
        scheduler = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'},
                   {'host': 'some_host', 'headers': 'some header dict'}]

        host = 'some_host3'
        velocloud_client = VelocloudClient(configs, logger, scheduler)
        velocloud_client._clients = clients

        client = velocloud_client._get_header_by_host(host)

        assert client is None

    @pytest.mark.asyncio
    async def get_all_event_information_test(self):
        configs = testconfig
        logger = Mock()
        scheduler = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval_start = "Some interval start time"
        interval_end = "Some interval end time"
        limit = "some_limit"
        events_status = "Some Enterprise Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=events_status)
        response_mock.status = 200

        velocloud_client = VelocloudClient(configs, logger, scheduler)
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
        scheduler = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval_start = "Some interval start time"
        interval_end = "Some interval end time"
        limit = "some_limit"
        events_status = "Some Enterprise Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=events_status)
        response_mock.status = 400

        velocloud_client = VelocloudClient(configs, logger, scheduler)
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
        scheduler = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval_start = "Some interval start time"
        interval_end = "Some interval end time"
        limit = "some_limit"
        events_status = "Some Enterprise Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=events_status)
        response_mock.status = 400

        velocloud_client = VelocloudClient(configs, logger, scheduler)
        velocloud_client._get_header_by_host = Mock(return_value=None)
        velocloud_client._json_return = Mock(return_value=response_mock.json())
        velocloud_client._start_relogin_job = CoroutineMock()

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            events = await velocloud_client.get_all_edge_events(edge_id, interval_start, interval_end, limit)

            mock_post.assert_not_called()
            velocloud_client._start_relogin_job.assert_awaited_once()

            assert events["status"] == 404
            assert events["body"] == f'Cannot find a client to connect to {edge_id["host"]}'

    @pytest.mark.asyncio
    async def get_get_all_event_information_error_500_test(self):
        configs = testconfig
        logger = Mock()
        scheduler = Mock()

        edge_id = {"host": 'some_host', "enterprise_id": 19, "edge_id": 99}
        interval_start = "Some interval start time"
        interval_end = "Some interval end time"
        limit = "some_limit"
        events_status = "Some Enterprise Information"
        header = {'host': 'some_host', 'headers': 'some header dict'}

        response_mock = Mock()
        response_mock.status = 500
        response_mock.json = CoroutineMock(return_value={})

        velocloud_client = VelocloudClient(configs, logger, scheduler)
        velocloud_client._get_header_by_host = Mock(return_value=header)
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        with patch.object(velocloud_client._session, 'post',
                          new=CoroutineMock(return_value=response_mock)) as mock_post:
            events = await velocloud_client.get_all_edge_events(edge_id, interval_start, interval_end, limit)

            assert events == {"body": 'Got internal error from Velocloud', "status": 500}

    @pytest.mark.asyncio
    async def get_all_enterprise_names_test(self):
        configs = Mock()
        logger = Mock()
        scheduler = Mock()

        clients = [{'host': 'some_host2', 'headers': 'some header dict'}]
        monitoring_aggregates_return = {
            "body": {'enterprises': [{'id': 1, 'name': 'A name'}]},
            "status": 200
        }

        velocloud_client = VelocloudClient(configs, logger, scheduler)
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
        scheduler = Mock()

        host = 'some_host'
        response = {'error': {'message': 'tokenError [expired session cookie]'}}
        velocloud_client = VelocloudClient(configs, logger, scheduler)
        velocloud_client._start_relogin_job = CoroutineMock()

        with raises(Exception):
            json_return = await velocloud_client._json_return(response, host)
            logger.info.assert_called_once()
            velocloud_client._start_relogin_job.assert_called_once()
            assert json_return == ''

    @pytest.mark.asyncio
    async def json_return_ko_different_error_test(self):
        configs = testconfig
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()
        scheduler = Mock()

        host = 'some_host'
        response = {'error': {'message': 'another_error'}}
        velocloud_client = VelocloudClient(configs, logger, scheduler)
        velocloud_client._start_relogin_job = CoroutineMock()
        json_return = await velocloud_client._json_return(response, host)
        logger.error.assert_called_once()
        assert json_return == response

    @pytest.mark.asyncio
    async def json_return_ko_no_error_test(self):
        configs = testconfig
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()
        scheduler = Mock()

        host = 'some_host'
        response = {'edge_status': 'ok'}
        velocloud_client = VelocloudClient(configs, logger, scheduler)
        velocloud_client._start_relogin_job = CoroutineMock()
        json_return = await velocloud_client._json_return(response, host)
        assert json_return == response

    @pytest.mark.asyncio
    async def json_return_ko_list_test(self):
        configs = testconfig
        logger = Mock()
        scheduler = Mock()

        host = 'some_host'
        response = ['List']
        velocloud_client = VelocloudClient(configs, logger, scheduler)
        velocloud_client._start_relogin_job = CoroutineMock()
        json_return = await velocloud_client._json_return(response, host)
        assert json_return == response

    @pytest.mark.asyncio
    async def get_links_with_edge_info_ok_test(self):
        velocloud_host = 'mettel.velocloud.net'
        velocloud_headers = {
            'some': 'header',
        }
        clients_by_host = [
            {'host': velocloud_host, 'headers': velocloud_headers}
        ]

        links_status: list = [
            {
                'enterpriseName': 'Militaires Sans Frontières',
                'enterpriseId': 2,
                'enterpriseProxyId': None,
                'enterpriseProxyName': None,
                'edgeName': 'Big Boss',
                'edgeState': 'CONNECTED',
                'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
                'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
                'edgeLastContact': '2020-09-29T04:48:55.000Z',
                'edgeId': 4206,
                'edgeSerialNumber': 'VC05200048223',
                'edgeHASerialNumber': None,
                'edgeModelNumber': 'edge520',
                'edgeLatitude': None,
                'edgeLongitude': None,
                'displayName': '70.59.5.185',
                'isp': None,
                'interface': 'REX',
                'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                'linkState': 'STABLE',
                'linkLastActive': '2020-09-29T04:45:15.000Z',
                'linkVpnState': 'STABLE',
                'linkId': 5293,
                'linkIpAddress': '70.59.5.185',
            }
        ]
        http_status_code = 200

        expected_result = {
            'body': links_status,
            'status': http_status_code,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=links_status)
        response_mock.status = http_status_code

        velocloud_client = VelocloudClient(config, logger, scheduler)
        velocloud_client._clients = clients_by_host

        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            result = await velocloud_client.get_links_with_edge_info(velocloud_host)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_response_having_status_400_test(self):
        velocloud_host = 'mettel.velocloud.net'
        velocloud_headers = {
            'some': 'header',
        }
        clients_by_host = [
            {'host': velocloud_host, 'headers': velocloud_headers}
        ]

        response_body = {
            "error": {
                "code": -32600,
                "message": "An error occurred while processing your request"
            }
        }
        http_status_code = 400

        expected_result = {
            'body': response_body,
            'status': http_status_code,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=response_body)
        response_mock.status = http_status_code

        velocloud_client = VelocloudClient(config, logger, scheduler)
        velocloud_client._clients = clients_by_host

        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            result = await velocloud_client.get_links_with_edge_info(velocloud_host)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_response_having_status_5xx_test(self):
        velocloud_host = 'mettel.velocloud.net'
        velocloud_headers = {
            'some': 'header',
        }
        clients_by_host = [
            {'host': velocloud_host, 'headers': velocloud_headers}
        ]

        response_body = {
            "error": {
                "code": -32600,
                "message": "An error occurred while processing your request"
            }
        }
        http_status_code = 500

        expected_result = {
            'body': 'Got internal error from Velocloud',
            'status': http_status_code,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=response_body)
        response_mock.status = http_status_code

        velocloud_client = VelocloudClient(config, logger, scheduler)
        velocloud_client._clients = clients_by_host

        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            result = await velocloud_client.get_links_with_edge_info(velocloud_host)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_response_having_status_200_and_pointing_out_token_expiration_test(self):
        velocloud_host = 'mettel.velocloud.net'
        velocloud_headers = {
            'some': 'header',
        }
        clients_by_host = [
            {'host': velocloud_host, 'headers': velocloud_headers}
        ]

        response_body = {
            'error': {
                'code': -32000,
                'message': 'tokenError [expired session cookie]'
            }
        }
        http_status_code = 200

        token_expired_msg = f'Auth token expired for host {velocloud_host}'
        expected_result = {
            'body': token_expired_msg,
            'status': 401,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=token_expired_msg)
        response_mock.status = http_status_code
        response_mock.headers = {
            'Expires': '0',
        }

        velocloud_client = VelocloudClient(config, logger, scheduler)
        velocloud_client._clients = clients_by_host
        velocloud_client._start_relogin_job = CoroutineMock()

        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            result = await velocloud_client.get_links_with_edge_info(velocloud_host)

        velocloud_client._start_relogin_job.assert_awaited_once_with(velocloud_host)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_headers_missing_for_target_host_test(self):
        velocloud_host = 'mettel.velocloud.net'
        velocloud_headers = {
            'some': 'header',
        }
        clients_by_host = [
            {'host': 'some-host', 'headers': velocloud_headers}
        ]

        expected_result = {
            'body': f'Cannot find a client to connect to host {velocloud_host}',
            'status': 404,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig

        velocloud_client = VelocloudClient(config, logger, scheduler)
        velocloud_client._clients = clients_by_host
        velocloud_client._start_relogin_job = CoroutineMock()

        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(side_effect=ClientConnectionError)):
            result = await velocloud_client.get_links_with_edge_info(velocloud_host)

        velocloud_client._start_relogin_job.assert_awaited_once_with(velocloud_host)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_connection_raising_exception_test(self):
        velocloud_host = 'mettel.velocloud.net'
        velocloud_headers = {
            'some': 'header',
        }
        clients_by_host = [
            {'host': velocloud_host, 'headers': velocloud_headers}
        ]

        expected_result = {
            'body': 'Error while connecting to Velocloud API',
            'status': 500,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig

        velocloud_client = VelocloudClient(config, logger, scheduler)
        velocloud_client._clients = clients_by_host

        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(side_effect=ClientConnectionError)):
            result = await velocloud_client.get_links_with_edge_info(velocloud_host)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_metric_info_ok_test(self):
        velocloud_host = 'mettel.velocloud.net'
        interval = {
            'start': '2020-10-19T15:22:03.345Z',
            'end': '2020-10-19T16:22:03.345Z',
        }

        velocloud_headers = {
            'some': 'header',
        }
        clients_by_host = [
            {'host': velocloud_host, 'headers': velocloud_headers}
        ]

        links_status: list = [
            {
                'linkId': 12,
                'bytesTx': 289334426,
                'bytesRx': 164603350,
                'packetsTx': 1682073,
                'packetsRx': 1610536,
                'totalBytes': 453937776,
                'totalPackets': 3292609,
                'p1BytesRx': 20936271,
                'p1BytesTx': 62441238,
                'p1PacketsRx': 54742,
                'p1PacketsTx': 92015,
                'p2BytesRx': 46571112,
                'p2BytesTx': 119887124,
                'p2PacketsRx': 195272,
                'p2PacketsTx': 246338,
                'p3BytesRx': 2990392,
                'p3BytesTx': 2273566,
                'p3PacketsRx': 3054,
                'p3PacketsTx': 5523,
                'controlBytesRx': 94105575,
                'controlBytesTx': 104732498,
                'controlPacketsRx': 1357468,
                'controlPacketsTx': 1338197,
                'bpsOfBestPathRx': 682655000,
                'bpsOfBestPathTx': 750187000,
                'bestJitterMsRx': 0,
                'bestJitterMsTx': 0,
                'bestLatencyMsRx': 0,
                'bestLatencyMsTx': 0,
                'bestLossPctRx': 0,
                'bestLossPctTx': 0,
                'scoreTx': 4.400000095367432,
                'scoreRx': 4.400000095367432,
                'signalStrength': 0,
                'state': 0,
                'name': 'GE1',
                'link': {
                    'enterpriseName': 'Signet Group Services Inc|86937|',
                    'enterpriseId': 2,
                    'enterpriseProxyId': None,
                    'enterpriseProxyName': None,
                    'edgeName': 'LAB09910VC',
                    'edgeState': 'CONNECTED',
                    'edgeSystemUpSince': '2020-09-23T04:59:12.000Z',
                    'edgeServiceUpSince': '2020-09-23T05:00:03.000Z',
                    'edgeLastContact': '2020-09-29T05:09:24.000Z',
                    'edgeId': 4,
                    'edgeSerialNumber': 'VC05200005831',
                    'edgeHASerialNumber': None,
                    'edgeModelNumber': 'edge520',
                    'edgeLatitude': 41.139999,
                    'edgeLongitude': -81.612999,
                    'displayName': '198.70.201.220',
                    'isp': 'Frontier Communications',
                    'interface': 'GE1',
                    'internalId': '00000001-a028-4037-a4bc-4d0488f4c9f9',
                    'linkState': 'STABLE',
                    'linkLastActive': '2020-09-29T05:05:23.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 12,
                    'linkIpAddress': '198.70.201.220',
                }
            }
        ]
        http_status_code = 200

        expected_result = {
            'body': links_status,
            'status': http_status_code,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=links_status)
        response_mock.status = http_status_code

        velocloud_client = VelocloudClient(config, logger, scheduler)
        velocloud_client._clients = clients_by_host

        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            result = await velocloud_client.get_links_metric_info(velocloud_host, interval)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_metric_info_with_response_having_status_400_test(self):
        velocloud_host = 'mettel.velocloud.net'
        interval = {
            'start': '2020-10-19T15:22:03.345Z',
            'end': '2020-10-19T16:22:03.345Z',
        }

        velocloud_headers = {
            'some': 'header',
        }
        clients_by_host = [
            {'host': velocloud_host, 'headers': velocloud_headers}
        ]

        response_body = {
            "error": {
                "code": -32600,
                "message": "An error occurred while processing your request"
            }
        }
        http_status_code = 400

        expected_result = {
            'body': response_body,
            'status': http_status_code,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=response_body)
        response_mock.status = http_status_code

        velocloud_client = VelocloudClient(config, logger, scheduler)
        velocloud_client._clients = clients_by_host

        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            result = await velocloud_client.get_links_metric_info(velocloud_host, interval)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_metric_info_with_response_having_status_5xx_test(self):
        velocloud_host = 'mettel.velocloud.net'
        interval = {
            'start': '2020-10-19T15:22:03.345Z',
            'end': '2020-10-19T16:22:03.345Z',
        }

        velocloud_headers = {
            'some': 'header',
        }
        clients_by_host = [
            {'host': velocloud_host, 'headers': velocloud_headers}
        ]

        response_body = {
            "error": {
                "code": -32600,
                "message": "An error occurred while processing your request"
            }
        }
        http_status_code = 500

        expected_result = {
            'body': 'Got internal error from Velocloud',
            'status': http_status_code,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=response_body)
        response_mock.status = http_status_code

        velocloud_client = VelocloudClient(config, logger, scheduler)
        velocloud_client._clients = clients_by_host

        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            result = await velocloud_client.get_links_metric_info(velocloud_host, interval)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_metric_info_with_response_having_status_200_and_pointing_out_token_expiration_test(self):
        velocloud_host = 'mettel.velocloud.net'
        interval = {
            'start': '2020-10-19T15:22:03.345Z',
            'end': '2020-10-19T16:22:03.345Z',
        }

        velocloud_headers = {
            'some': 'header',
        }
        clients_by_host = [
            {'host': velocloud_host, 'headers': velocloud_headers}
        ]

        response_body = {
            'error': {
                'code': -32000,
                'message': 'tokenError [expired session cookie]'
            }
        }
        http_status_code = 200

        token_expired_msg = f'Auth token expired for host {velocloud_host}'
        expected_result = {
            'body': token_expired_msg,
            'status': 401,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=token_expired_msg)
        response_mock.status = http_status_code
        response_mock.headers = {
            'Expires': '0',
        }

        velocloud_client = VelocloudClient(config, logger, scheduler)
        velocloud_client._clients = clients_by_host
        velocloud_client._start_relogin_job = CoroutineMock()

        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            result = await velocloud_client.get_links_metric_info(velocloud_host, interval)

        velocloud_client._start_relogin_job.assert_awaited_once_with(velocloud_host)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_metric_info_with_headers_missing_for_target_host_test(self):
        velocloud_host = 'mettel.velocloud.net'
        interval = {
            'start': '2020-10-19T15:22:03.345Z',
            'end': '2020-10-19T16:22:03.345Z',
        }

        velocloud_headers = {
            'some': 'header',
        }
        clients_by_host = [
            {'host': 'some-host', 'headers': velocloud_headers}
        ]

        expected_result = {
            'body': f'Cannot find a client to connect to host {velocloud_host}',
            'status': 404,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig

        velocloud_client = VelocloudClient(config, logger, scheduler)
        velocloud_client._clients = clients_by_host
        velocloud_client._start_relogin_job = CoroutineMock()

        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(side_effect=ClientConnectionError)):
            result = await velocloud_client.get_links_metric_info(velocloud_host, interval)

        velocloud_client._start_relogin_job.assert_awaited_once_with(velocloud_host)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_metric_info_with_connection_raising_exception_test(self):
        velocloud_host = 'mettel.velocloud.net'
        interval = {
            'start': '2020-10-19T15:22:03.345Z',
            'end': '2020-10-19T16:22:03.345Z',
        }

        velocloud_headers = {
            'some': 'header',
        }
        clients_by_host = [
            {'host': velocloud_host, 'headers': velocloud_headers}
        ]

        expected_result = {
            'body': 'Error while connecting to Velocloud API',
            'status': 500,
        }

        logger = Mock()
        scheduler = Mock()
        config = testconfig

        velocloud_client = VelocloudClient(config, logger, scheduler)
        velocloud_client._clients = clients_by_host

        with patch.object(velocloud_client._session, 'post', new=CoroutineMock(side_effect=ClientConnectionError)):
            result = await velocloud_client.get_links_metric_info(velocloud_host, interval)

        assert result == expected_result
