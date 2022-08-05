from datetime import datetime, timedelta
from http import HTTPStatus
from unittest.mock import AsyncMock, Mock

import pytest

from ...application.clients.velocloud_client import VelocloudClient
from ...application.repositories.utils_repository import GenericResponse
from ...application.repositories.velocloud_repository import VelocloudRepository
from ...config import testconfig as config


@pytest.fixture(scope="function")
def velocloud_client():
    return Mock(spec_set=VelocloudClient)


@pytest.fixture(scope="function")
def velocloud_repository(velocloud_client):
    return VelocloudRepository(config=config, velocloud_client=velocloud_client)


class TestVelocloudRepository:
    @pytest.mark.asyncio
    async def get_all_edge_events_filter_test(self):
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config=config, velocloud_client=test_velocloud_client)

        events_response = {"body": {"data": [{"event": "EDGE_UP"}]}, "status": 200}
        edge_events_response = {"body": [{"event": "EDGE_UP"}], "status": 200}
        filter_events_status_list = ["EDGE_UP", "EDGE_DOWN", "LINK_ALIVE", "LINK_DEAD"]

        test_velocloud_client.get_all_events = AsyncMock(return_value=events_response)
        edge = {"host": vr._config.VELOCLOUD_CONFIG["servers"][0]["url"], "enterprise_id": 19, "edge_id": 99}
        start = datetime.now() - timedelta(hours=24)
        end = datetime.now()
        limit = None
        body = {
            "enterpriseId": edge["enterprise_id"],
            "interval": {"start": start, "end": end},
            "edgeId": [edge["edge_id"]],
            "filter": {"limit": limit, "rules": [{"field": "event", "op": "is", "values": filter_events_status_list}]},
        }
        edge_events = await vr.get_all_edge_events(edge, start, end, limit, filter_events_status_list)
        test_velocloud_client.get_all_events.assert_awaited_once_with(edge["host"], body)
        assert edge_events == edge_events_response

    @pytest.mark.asyncio
    async def get_all_edge_events_none_filter_test(self):
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config=config, velocloud_client=test_velocloud_client)

        events_response = {"body": {"data": [{"event": "EDGE_UP"}, {"event": "EDGE_GONE"}]}, "status": 200}
        edge_events_response = {"body": [{"event": "EDGE_UP"}, {"event": "EDGE_GONE"}], "status": 200}
        filter_events_status_list = None

        test_velocloud_client.get_all_events = AsyncMock(return_value=events_response)
        edge = {"host": vr._config.VELOCLOUD_CONFIG["servers"][0]["url"], "enterprise_id": 19, "edge_id": 99}
        start = datetime.now() - timedelta(hours=24)
        end = datetime.now()
        limit = None
        body = {
            "enterpriseId": edge["enterprise_id"],
            "interval": {"start": start, "end": end},
            "edgeId": [edge["edge_id"]],
            "filter": {
                "limit": limit,
            },
        }
        edge_events = await vr.get_all_edge_events(edge, start, end, limit, filter_events_status_list)
        test_velocloud_client.get_all_events.assert_awaited_once_with(edge["host"], body)
        assert edge_events == edge_events_response

    @pytest.mark.asyncio
    async def get_all_edge_events_non_2xx_status_test(self):
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config=config, velocloud_client=test_velocloud_client)

        events_response = {"body": "Failed", "status": 400}
        filter_events_status_list = None

        test_velocloud_client.get_all_events = AsyncMock(return_value=events_response)
        edge = {"host": vr._config.VELOCLOUD_CONFIG["servers"][0]["url"], "enterprise_id": 19, "edge_id": 99}
        start = datetime.now() - timedelta(hours=24)
        end = datetime.now()
        limit = None
        body = {
            "enterpriseId": edge["enterprise_id"],
            "interval": {"start": start, "end": end},
            "edgeId": [edge["edge_id"]],
            "filter": {
                "limit": limit,
            },
        }
        edge_events = await vr.get_all_edge_events(edge, start, end, limit, filter_events_status_list)
        test_velocloud_client.get_all_events.assert_awaited_once_with(edge["host"], body)
        assert edge_events == events_response

    @pytest.mark.asyncio
    async def get_all_enterprise_events_filter_test(self):
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config=config, velocloud_client=test_velocloud_client)

        events_response = {"body": {"data": [{"event": "EDGE_UP"}]}, "status": 200}
        enterprise_events_response = {"body": [{"event": "EDGE_UP"}], "status": 200}
        filter_events_status_list = ["EDGE_UP", "EDGE_DOWN", "LINK_ALIVE", "LINK_DEAD"]

        test_velocloud_client.get_all_events = AsyncMock(return_value=events_response)
        host = vr._config.VELOCLOUD_CONFIG["servers"][0]["url"]
        enterprise_id = 19
        start = datetime.now() - timedelta(hours=24)
        end = datetime.now()
        limit = None
        body = {
            "enterpriseId": enterprise_id,
            "interval": {"start": start, "end": end},
            "filter": {"limit": limit, "rules": [{"field": "event", "op": "is", "values": filter_events_status_list}]},
        }
        enterprise_events = await vr.get_all_enterprise_events(
            enterprise_id, host, start, end, limit, filter_events_status_list
        )
        test_velocloud_client.get_all_events.assert_awaited_once_with(host, body)
        assert enterprise_events == enterprise_events_response

    @pytest.mark.asyncio
    async def get_all_enterprise_events_no_filter_test(self):
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config=config, velocloud_client=test_velocloud_client)

        events_response = {"body": {"data": [{"event": "EDGE_UP"}, {"event": "EDGE_GONE"}]}, "status": 200}
        enterprise_events_response = {"body": [{"event": "EDGE_UP"}, {"event": "EDGE_GONE"}], "status": 200}
        filter_events_status_list = None

        test_velocloud_client.get_all_events = AsyncMock(return_value=events_response)
        host = vr._config.VELOCLOUD_CONFIG["servers"][0]["url"]
        enterprise_id = 19
        start = datetime.now() - timedelta(hours=24)
        end = datetime.now()
        limit = None
        body = {
            "enterpriseId": enterprise_id,
            "interval": {"start": start, "end": end},
            "filter": {
                "limit": limit,
            },
        }
        enterprise_events = await vr.get_all_enterprise_events(
            enterprise_id, host, start, end, limit, filter_events_status_list
        )
        test_velocloud_client.get_all_events.assert_awaited_once_with(host, body)
        assert enterprise_events == enterprise_events_response

    @pytest.mark.asyncio
    async def get_all_enterprise_events_non_2xx_status_test(self):
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config=config, velocloud_client=test_velocloud_client)

        events_response = {"body": "Failed", "status": 400}

        filter_events_status_list = None

        test_velocloud_client.get_all_events = AsyncMock(return_value=events_response)
        host = vr._config.VELOCLOUD_CONFIG["servers"][0]["url"]
        enterprise_id = 19
        start = datetime.now() - timedelta(hours=24)
        end = datetime.now()
        limit = None
        body = {
            "enterpriseId": enterprise_id,
            "interval": {"start": start, "end": end},
            "filter": {
                "limit": limit,
            },
        }
        enterprise_events = await vr.get_all_enterprise_events(
            enterprise_id, host, start, end, limit, filter_events_status_list
        )
        test_velocloud_client.get_all_events.assert_awaited_once_with(host, body)
        assert enterprise_events == events_response

    @pytest.mark.asyncio
    async def connect_to_all_servers_test(self):
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config=config, velocloud_client=test_velocloud_client)
        test_velocloud_client.instantiate_and_connect_clients = AsyncMock()
        await vr.connect_to_all_servers()
        assert test_velocloud_client.instantiate_and_connect_clients.called

    @pytest.mark.asyncio
    async def get_all_enterprise_names_with_filter_test(self):
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config=config, velocloud_client=test_velocloud_client)
        enterprises = {"body": [{"enterprise_name": "The Name"}], "status": 200}
        msg = {"request_id": "123", "filter": ["The Name"]}
        test_velocloud_client.get_all_enterprise_names = AsyncMock(return_value=enterprises)
        enterprise_names = await vr.get_all_enterprise_names(msg)

        assert test_velocloud_client.get_all_enterprise_names.called
        assert enterprise_names["body"] == ["The Name"]

    @pytest.mark.asyncio
    async def get_all_enterprise_names_none_test(self):
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config=config, velocloud_client=test_velocloud_client)
        enterprises = {"body": None, "status": 500}
        msg = {"request_id": "123", "filter": []}
        test_velocloud_client.get_all_enterprise_names = AsyncMock(return_value=enterprises)
        enterprise_names = await vr.get_all_enterprise_names(msg)

        assert enterprise_names == {"body": None, "status": 500}

    @pytest.mark.asyncio
    async def get_all_enterprise_names_without_filter_test(self):
        test_velocloud_client = Mock()
        vr = VelocloudRepository(config=config, velocloud_client=test_velocloud_client)
        enterprises = {"body": [{"enterprise_name": "The Name"}], "status": 200}
        msg = {"request_id": "123", "filter": []}
        test_velocloud_client.get_all_enterprise_names = AsyncMock(return_value=enterprises)
        enterprise_names = await vr.get_all_enterprise_names(msg)

        assert test_velocloud_client.get_all_enterprise_names.called
        assert enterprise_names["body"] == ["The Name"]

    @pytest.mark.asyncio
    async def get_links_with_edge_info_ok_test(self):
        velocloud_host = "mettel.velocloud.net"

        link_1 = {
            "enterpriseName": "Militaires Sans Frontières",
            "enterpriseId": 2,
            "enterpriseProxyId": None,
            "enterpriseProxyName": None,
            "edgeName": "Big Boss",
            "edgeState": "CONNECTED",
            "edgeSystemUpSince": "2020-09-14T05:07:40.000Z",
            "edgeServiceUpSince": "2020-09-14T05:08:22.000Z",
            "edgeLastContact": "2020-09-29T04:48:55.000Z",
            "edgeId": 4206,
            "edgeSerialNumber": "VC05200048223",
            "edgeHASerialNumber": None,
            "edgeModelNumber": "edge520",
            "edgeLatitude": None,
            "edgeLongitude": None,
            "displayName": "70.59.5.185",
            "isp": None,
            "interface": "REX",
            "internalId": "00000001-ac48-47a0-81a7-80c8c320f486",
            "linkState": "STABLE",
            "linkLastActive": "2020-09-29T04:45:15.000Z",
            "linkVpnState": "STABLE",
            "linkId": 5293,
            "linkIpAddress": "70.59.5.185",
        }
        client_result = {
            "body": [link_1],
            "status": 200,
        }

        expected_result = {
            "body": [
                {
                    "host": velocloud_host,
                    **link_1,
                },
            ],
            "status": 200,
        }

        logger = Mock()

        velocloud_client = Mock()
        velocloud_client.get_links_with_edge_info = AsyncMock(return_value=client_result)

        velocloud_repository = VelocloudRepository(config=config, velocloud_client=velocloud_client)

        result = await velocloud_repository.get_links_with_edge_info(velocloud_host)

        velocloud_client.get_links_with_edge_info.assert_awaited_once_with(velocloud_host)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_response_having_non_2xx_status_test(self):
        velocloud_host = "mettel.velocloud.net"

        client_result = {
            "body": "Got internal error from Velocloud",
            "status": 500,
        }

        logger = Mock()

        velocloud_client = Mock()
        velocloud_client.get_links_with_edge_info = AsyncMock(return_value=client_result)

        velocloud_repository = VelocloudRepository(config=config, velocloud_client=velocloud_client)

        result = await velocloud_repository.get_links_with_edge_info(velocloud_host)

        velocloud_client.get_links_with_edge_info.assert_awaited_once_with(velocloud_host)
        assert result == client_result

    @pytest.mark.asyncio
    async def get_links_metric_info_ok_test(self):
        velocloud_host = "mettel.velocloud.net"
        interval = {
            "start": "2020-10-19T15:22:03.345Z",
            "end": "2020-10-19T16:22:03.345Z",
        }

        link_1 = {
            "linkId": 12,
            "bytesTx": 289334426,
            "bytesRx": 164603350,
            "packetsTx": 1682073,
            "packetsRx": 1610536,
            "totalBytes": 453937776,
            "totalPackets": 3292609,
            "p1BytesRx": 20936271,
            "p1BytesTx": 62441238,
            "p1PacketsRx": 54742,
            "p1PacketsTx": 92015,
            "p2BytesRx": 46571112,
            "p2BytesTx": 119887124,
            "p2PacketsRx": 195272,
            "p2PacketsTx": 246338,
            "p3BytesRx": 2990392,
            "p3BytesTx": 2273566,
            "p3PacketsRx": 3054,
            "p3PacketsTx": 5523,
            "controlBytesRx": 94105575,
            "controlBytesTx": 104732498,
            "controlPacketsRx": 1357468,
            "controlPacketsTx": 1338197,
            "bpsOfBestPathRx": 682655000,
            "bpsOfBestPathTx": 750187000,
            "bestJitterMsRx": 0,
            "bestJitterMsTx": 0,
            "bestLatencyMsRx": 0,
            "bestLatencyMsTx": 0,
            "bestLossPctRx": 0,
            "bestLossPctTx": 0,
            "scoreTx": 4.400000095367432,
            "scoreRx": 4.400000095367432,
            "signalStrength": 0,
            "state": 0,
            "name": "GE1",
            "link": {
                "enterpriseName": "Signet Group Services Inc|86937|",
                "enterpriseId": 2,
                "enterpriseProxyId": None,
                "enterpriseProxyName": None,
                "edgeName": "LAB09910VC",
                "edgeState": "CONNECTED",
                "edgeSystemUpSince": "2020-09-23T04:59:12.000Z",
                "edgeServiceUpSince": "2020-09-23T05:00:03.000Z",
                "edgeLastContact": "2020-09-29T05:09:24.000Z",
                "edgeId": 4,
                "edgeSerialNumber": "VC05200005831",
                "edgeHASerialNumber": None,
                "edgeModelNumber": "edge520",
                "edgeLatitude": 41.139999,
                "edgeLongitude": -81.612999,
                "displayName": "198.70.201.220",
                "isp": "Frontier Communications",
                "interface": "GE1",
                "internalId": "00000001-a028-4037-a4bc-4d0488f4c9f9",
                "linkState": "STABLE",
                "linkLastActive": "2020-09-29T05:05:23.000Z",
                "linkVpnState": "STABLE",
                "linkId": 12,
                "linkIpAddress": "198.70.201.220",
            },
        }
        client_result = {
            "body": [link_1],
            "status": 200,
        }

        expected_link = link_1.copy()
        expected_link["link"]["host"] = velocloud_host
        expected_result = {
            "body": [
                {
                    **expected_link,
                },
            ],
            "status": 200,
        }

        logger = Mock()

        velocloud_client = Mock()
        velocloud_client.get_links_metric_info = AsyncMock(return_value=client_result)

        velocloud_repository = VelocloudRepository(config=config, velocloud_client=velocloud_client)

        result = await velocloud_repository.get_links_metric_info(velocloud_host, interval)

        velocloud_client.get_links_metric_info.assert_awaited_once_with(velocloud_host, interval)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_metric_info_with_response_having_non_2xx_status_test(self):
        velocloud_host = "mettel.velocloud.net"
        interval = {
            "start": "2020-10-19T15:22:03.345Z",
            "end": "2020-10-19T16:22:03.345Z",
        }

        client_result = {
            "body": "Got internal error from Velocloud",
            "status": 500,
        }

        logger = Mock()

        velocloud_client = Mock()
        velocloud_client.get_links_metric_info = AsyncMock(return_value=client_result)

        velocloud_repository = VelocloudRepository(config=config, velocloud_client=velocloud_client)

        result = await velocloud_repository.get_links_metric_info(velocloud_host, interval)

        velocloud_client.get_links_metric_info.assert_awaited_once_with(velocloud_host, interval)
        assert result == client_result

    @pytest.mark.asyncio
    async def get_enterprise_edge_test(self):
        host = "some.host"
        enterprise_id = 113

        enterprise_list = ["List of enterprise edges"]

        logger = Mock()

        velocloud_client = Mock()
        velocloud_client.get_enterprise_edges = AsyncMock(return_value=enterprise_list)

        velocloud_repository = VelocloudRepository(config=config, velocloud_client=velocloud_client)

        results = await velocloud_repository.get_enterprise_edges(host, enterprise_id)

        velocloud_client.get_enterprise_edges.assert_awaited_once_with(host, enterprise_id)
        assert results == enterprise_list

    @pytest.mark.asyncio
    async def get_links_configuration_test(self):
        edge_full_id = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 1,
            "edge_id": 1,
        }

        links_configuration = [
            {
                "logicalId": "08:bd:43:f8:8a:97:0000",
                "internalId": "00a0c8dc-5674-0000-0000-000000000000",
                "discovery": "AUTO_DISCOVERED",
                "mode": "PUBLIC",
                "type": "WIRED",
                "name": "Comcast ( MetTel-BCB.112134 )",
                "isp": "Comcast Cable",
                "publicIpAddress": "98.253.7.215",
                "interfaces": ["INTERNET2"],
                # Some fields omitted for simplicity
            },
        ]
        config_stack_response = {
            "body": {
                "WAN": {
                    "version": "1619512204741",
                    "schemaVersion": "3.3.2",
                    "type": "ENTERPRISE",
                    "data": {
                        "networks": [],
                        "links": links_configuration,
                    },
                },
            },
            "status": 200,
        }

        logger = Mock()

        velocloud_client = Mock()
        velocloud_client.get_edge_configuration_modules = AsyncMock(return_value=config_stack_response)

        velocloud_repository = VelocloudRepository(config=config, velocloud_client=velocloud_client)

        response = await velocloud_repository.get_links_configuration(edge_full_id)

        velocloud_client.get_edge_configuration_modules.assert_awaited_once_with(edge_full_id)

        expected = {
            "body": links_configuration,
            "status": 200,
        }
        assert response == expected

    @pytest.mark.asyncio
    async def get_links_configuration_with_config_modules_response_having_non_2xx_status_test(self):
        edge_full_id = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 1,
            "edge_id": 1,
        }

        config_modules_response = {
            "body": "Got internal error from Velocloud",
            "status": 500,
        }

        logger = Mock()

        velocloud_client = Mock()
        velocloud_client.get_edge_configuration_modules = AsyncMock(return_value=config_modules_response)

        velocloud_repository = VelocloudRepository(config=config, velocloud_client=velocloud_client)

        response = await velocloud_repository.get_links_configuration(edge_full_id)

        velocloud_client.get_edge_configuration_modules.assert_awaited_once_with(edge_full_id)
        assert response == config_modules_response

    @pytest.mark.asyncio
    async def get_links_configuration_with_WAN_module_missing_in_edge_specific_config_test(self):
        edge_full_id = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 1,
            "edge_id": 1,
        }

        config_modules_response = {
            "body": {
                "QOS": {
                    "version": "1619512204741",
                    "schemaVersion": "3.3.2",
                    "type": "ENTERPRISE",
                    "data": {
                        "segments": [
                            {
                                "segment": {"segmentId": 0, "name": "Global Segment", "type": "REGULAR"},
                                "cosMapping": {
                                    "lsInputType": "weight",
                                    "realtime": {
                                        "high": {"value": 35, "ratelimit": False},
                                        "normal": {"value": 15, "ratelimit": False},
                                        "low": {"value": 1, "ratelimit": False},
                                    },
                                },
                            },
                        ],
                    },
                },
            },
            "status": 200,
        }

        logger = Mock()

        velocloud_client = Mock()
        velocloud_client.get_edge_configuration_modules = AsyncMock(return_value=config_modules_response)

        velocloud_repository = VelocloudRepository(config=config, velocloud_client=velocloud_client)

        response = await velocloud_repository.get_links_configuration(edge_full_id)

        velocloud_client.get_edge_configuration_modules.assert_awaited_once_with(edge_full_id)

        expected = {
            "body": f"No WAN module was found for edge {edge_full_id}",
            "status": 404,
        }
        assert response == expected

    @pytest.mark.asyncio
    async def get_links_configuration_with_no_links_in_WAN_module_test(self):
        edge_full_id = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 1,
            "edge_id": 1,
        }

        config_modules_response = {
            "body": {
                "WAN": {
                    "version": "1619512204741",
                    "schemaVersion": "3.3.2",
                    "type": "ENTERPRISE",
                    "data": {},
                },
            },
            "status": 200,
        }

        logger = Mock()

        velocloud_client = Mock()
        velocloud_client.get_edge_configuration_modules = AsyncMock(return_value=config_modules_response)

        velocloud_repository = VelocloudRepository(config=config, velocloud_client=velocloud_client)

        response = await velocloud_repository.get_links_configuration(edge_full_id)

        velocloud_client.get_edge_configuration_modules.assert_awaited_once_with(edge_full_id)

        expected = {
            "body": f"No links configuration was found in WAN module of edge {edge_full_id}",
            "status": 404,
        }
        assert response == expected

    @pytest.mark.asyncio
    async def get_edge_links_series_test(self, velocloud_repository):
        velocloud_host = "test.velocloud.com"
        payload = {}

        velocloud_repository._velocloud_client.get_edge_links_series = AsyncMock()
        await velocloud_repository.get_edge_links_series(velocloud_host, payload)
        velocloud_repository._velocloud_client.get_edge_links_series.assert_awaited_once_with(velocloud_host, payload)

    @pytest.mark.asyncio
    async def get_network_enterprise_edges_test(self, velocloud_repository, make_network_enterprises_body):
        velocloud_host = "test.velocloud.com"
        enterprise_ids = [3]

        client_response_body = make_network_enterprises_body(enterprise_ids=enterprise_ids, n_edges=2)
        client_response = {"body": client_response_body, "status": 200}

        get_network_enterprises_mock = AsyncMock(return_value=client_response)
        velocloud_repository._velocloud_client.get_network_enterprises = get_network_enterprises_mock

        response = await velocloud_repository.get_network_enterprise_edges(velocloud_host, enterprise_ids)

        get_network_enterprises_mock.assert_awaited_once_with(velocloud_host, enterprise_ids)

        expected_body = client_response_body[0].get("edges")

        expected = {
            "body": expected_body,
            "status": 200,
        }

        assert all("host" in edge.keys() for edge in expected_body)
        assert response == expected
        assert response["body"][0]["host"] == velocloud_host

    @pytest.mark.asyncio
    async def get_network_enterprise_edges_non_200_status_test(self, velocloud_repository):
        velocloud_host = "test.velocloud.com"
        enterprise_ids = [3]
        client_error_response = {
            "body": "Error while connecting to Velocloud API",
            "status": 500,
        }

        get_network_enterprises_mock = AsyncMock(return_value=client_error_response)
        velocloud_repository._velocloud_client.get_network_enterprises = get_network_enterprises_mock

        response = await velocloud_repository.get_network_enterprise_edges(velocloud_host, enterprise_ids)

        get_network_enterprises_mock.assert_awaited_once_with(velocloud_host, enterprise_ids)

        assert response == client_error_response

    @pytest.mark.asyncio
    async def get_network_enterprise_edges_404_status_test(self, velocloud_repository, make_network_enterprises_body):
        velocloud_host = "test.velocloud.com"
        enterprise_ids = [3]
        client_response_body = make_network_enterprises_body(enterprise_ids=enterprise_ids, n_edges=0)
        client_no_edges_response = {"body": client_response_body, "status": 200}

        get_network_enterprises_mock = AsyncMock(return_value=client_no_edges_response)
        velocloud_repository._velocloud_client.get_network_enterprises = get_network_enterprises_mock

        response = await velocloud_repository.get_network_enterprise_edges(velocloud_host, enterprise_ids)

        get_network_enterprises_mock.assert_awaited_once_with(velocloud_host, enterprise_ids)

        expected = {
            "status": 404,
            "body": f"No edges found for host {velocloud_host} and enterprise ids {enterprise_ids}",
        }

        assert response == expected

    @pytest.mark.asyncio
    async def get_network_gateways_test(self, velocloud_repository, make_network_gateways_body):
        velocloud_host = "test.velocloud.com"
        response_body = make_network_gateways_body(host=velocloud_host)
        response = {"body": response_body, "status": 200}

        velocloud_repository._velocloud_client.get_network_gateways = AsyncMock(return_value=response)
        await velocloud_repository.get_network_gateways(velocloud_host)
        velocloud_repository._velocloud_client.get_network_gateways.assert_awaited_once_with(velocloud_host)

    @pytest.mark.asyncio
    async def get_gateway_status_metrics_test(self, velocloud_repository):
        velocloud_host = "test.velocloud.com"
        gateway_id = 1
        interval = {"start": "2022-01-01T11:00:00Z", "end": "2022-01-01T12:00:00Z"}
        metrics = []

        velocloud_repository._velocloud_client.get_gateway_status_metrics = AsyncMock()
        await velocloud_repository.get_gateway_status_metrics(velocloud_host, gateway_id, interval, metrics)
        velocloud_repository._velocloud_client.get_gateway_status_metrics.assert_awaited_once_with(
            velocloud_host, gateway_id, interval, metrics
        )
