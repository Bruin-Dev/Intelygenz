from unittest.mock import Mock
from asynctest import CoroutineMock

from config import testconfig as config
from application.repositories.velocloud_repository import VelocloudRepository
import pytest
from datetime import datetime, timedelta


class TestVelocloudRepository:

    @pytest.mark.asyncio
    async def get_all_edge_events_filter_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)

        events = {"body": {"data": [{'event': 'EDGE_UP'}, {'event': 'EDGE_GONE'}]},
                  "status": 200}
        filter_events_status_list = ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD']

        test_velocloud_client.get_all_edge_events = CoroutineMock(return_value=events)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        start = datetime.now() - timedelta(hours=24)
        end = datetime.now()
        limit = None
        edge_events = await vr.get_all_edge_events(edge, start, end, limit, filter_events_status_list)
        assert test_velocloud_client.get_all_edge_events.called
        assert edge_events == {"body": [{'event': 'EDGE_UP'}], "status": 200}

    @pytest.mark.asyncio
    async def get_all_edge_events_none_filter_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)

        events = {"body": {"data": [{'event': 'EDGE_UP'}, {'event': 'EDGE_GONE'}]},
                  "status": 200}
        filter_events_status_list = None

        test_velocloud_client.get_all_edge_events = CoroutineMock(return_value=events)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        start = datetime.now() - timedelta(hours=24)
        end = datetime.now()
        limit = None
        edge_events = await vr.get_all_edge_events(edge, start, end, limit, filter_events_status_list)
        assert test_velocloud_client.get_all_edge_events.called
        assert edge_events == {"body": [{'event': 'EDGE_UP'}, {'event': 'EDGE_GONE'}], "status": 200}

    @pytest.mark.asyncio
    async def get_all_edge_events_none_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)

        events = {"body": None,
                  "status": 500}
        filter_events_status_list = None

        test_velocloud_client.get_all_edge_events = CoroutineMock(return_value=events)
        edge = {"host": vr._config['servers'][0]['url'], "enterprise_id": 19, "edge_id": 99}
        start = datetime.now() - timedelta(hours=24)
        end = datetime.now()
        limit = None
        edge_events = await vr.get_all_edge_events(edge, start, end, limit, filter_events_status_list)
        assert test_velocloud_client.get_all_edge_events.called
        assert edge_events == {"body": None, "status": 500}

    @pytest.mark.asyncio
    async def connect_to_all_servers_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        test_velocloud_client.instantiate_and_connect_clients = CoroutineMock()
        await vr.connect_to_all_servers()
        assert test_velocloud_client.instantiate_and_connect_clients.called

    @pytest.mark.asyncio
    async def get_all_enterprise_names_with_filter_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        enterprises = {
            "body": [{"enterprise_name": "The Name"}],
            "status": 200
        }
        msg = {"request_id": "123", "filter": ["The Name"]}
        test_velocloud_client.get_all_enterprise_names = CoroutineMock(
            return_value=enterprises
        )
        enterprise_names = await vr.get_all_enterprise_names(msg)

        assert test_velocloud_client.get_all_enterprise_names.called
        assert enterprise_names["body"] == ["The Name"]

    @pytest.mark.asyncio
    async def get_all_enterprise_names_none_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        enterprises = {
            "body": None,
            "status": 500
        }
        msg = {"request_id": "123", "filter": []}
        test_velocloud_client.get_all_enterprise_names = CoroutineMock(
            return_value=enterprises
        )
        enterprise_names = await vr.get_all_enterprise_names(msg)

        assert enterprise_names == {"body": None, "status": 500}

    @pytest.mark.asyncio
    async def get_all_enterprise_names_without_filter_test(self):
        mock_logger = Mock()
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config, mock_logger, test_velocloud_client)
        enterprises = {
            "body": [{"enterprise_name": "The Name"}],
            "status": 200
        }
        msg = {"request_id": "123", "filter": []}
        test_velocloud_client.get_all_enterprise_names = CoroutineMock(
            return_value=enterprises
        )
        enterprise_names = await vr.get_all_enterprise_names(msg)

        assert test_velocloud_client.get_all_enterprise_names.called
        assert enterprise_names["body"] == ["The Name"]

    @pytest.mark.asyncio
    async def get_links_with_edge_info_ok_test(self):
        velocloud_host = 'mettel.velocloud.net'

        link_1 = {
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
        client_result = {
            'body': [
                link_1
            ],
            'status': 200,
        }

        expected_result = {
            'body': [
                {
                    'host': velocloud_host,
                    **link_1,
                },
            ],
            'status': 200,
        }

        logger = Mock()

        velocloud_client = Mock()
        velocloud_client.get_links_with_edge_info = CoroutineMock(return_value=client_result)

        velocloud_repository = VelocloudRepository(config, logger, velocloud_client)

        result = await velocloud_repository.get_links_with_edge_info(velocloud_host)

        velocloud_client.get_links_with_edge_info.assert_awaited_once_with(velocloud_host)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_response_having_non_2xx_status_test(self):
        velocloud_host = 'mettel.velocloud.net'

        client_result = {
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        logger = Mock()

        velocloud_client = Mock()
        velocloud_client.get_links_with_edge_info = CoroutineMock(return_value=client_result)

        velocloud_repository = VelocloudRepository(config, logger, velocloud_client)

        result = await velocloud_repository.get_links_with_edge_info(velocloud_host)

        velocloud_client.get_links_with_edge_info.assert_awaited_once_with(velocloud_host)
        assert result == client_result

    @pytest.mark.asyncio
    async def get_links_metric_info_ok_test(self):
        velocloud_host = 'mettel.velocloud.net'
        interval = {
            'start': '2020-10-19T15:22:03.345Z',
            'end': '2020-10-19T16:22:03.345Z',
        }

        link_1 = {
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
        client_result = {
            'body': [
                link_1
            ],
            'status': 200,
        }

        expected_link = link_1.copy()
        expected_link["link"]["host"] = velocloud_host
        expected_result = {
            'body': [
                {
                    **expected_link,
                },
            ],
            'status': 200,
        }

        logger = Mock()

        velocloud_client = Mock()
        velocloud_client.get_links_metric_info = CoroutineMock(return_value=client_result)

        velocloud_repository = VelocloudRepository(config, logger, velocloud_client)

        result = await velocloud_repository.get_links_metric_info(velocloud_host, interval)

        velocloud_client.get_links_metric_info.assert_awaited_once_with(velocloud_host, interval)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_metric_info_with_response_having_non_2xx_status_test(self):
        velocloud_host = 'mettel.velocloud.net'
        interval = {
            'start': '2020-10-19T15:22:03.345Z',
            'end': '2020-10-19T16:22:03.345Z',
        }

        client_result = {
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        logger = Mock()

        velocloud_client = Mock()
        velocloud_client.get_links_metric_info = CoroutineMock(return_value=client_result)

        velocloud_repository = VelocloudRepository(config, logger, velocloud_client)

        result = await velocloud_repository.get_links_metric_info(velocloud_host, interval)

        velocloud_client.get_links_metric_info.assert_awaited_once_with(velocloud_host, interval)
        assert result == client_result
