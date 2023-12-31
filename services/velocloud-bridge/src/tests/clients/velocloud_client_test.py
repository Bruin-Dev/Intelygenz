from unittest.mock import AsyncMock, Mock, patch

import pytest
from aiohttp import ClientConnectionError, ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytest import raises

from ...application.clients.velocloud_client import VelocloudClient
from ...config import testconfig as config


@pytest.fixture(scope="function")
def scheduler():
    return Mock(spec_set=AsyncIOScheduler)


@pytest.fixture(scope="function")
def velocloud_client(scheduler):
    client = VelocloudClient(config=config, scheduler=scheduler)
    client._session = Mock(spec_set=ClientSession)
    return client


class TestVelocloudClient:
    @pytest.mark.asyncio
    async def connect_to_all_hosts_test(self, velocloud_client):
        velocloud_client._login = AsyncMock()
        await velocloud_client._connect_to_all_hosts()
        velocloud_client._login.assert_called_once_with("some_host")

    @pytest.mark.asyncio
    async def schedule_connect_to_all_hosts_test(self, velocloud_client):
        await velocloud_client.schedule_connect_to_all_hosts()
        velocloud_client._scheduler.add_job.assert_called_once()

    @pytest.mark.asyncio
    async def get_all_event_information_test(self, velocloud_client):
        host = "some_host"
        edge_id = {"host": host, "enterprise_id": 19, "edge_id": 99}
        interval_start = "Some interval start time"
        interval_end = "Some interval end time"
        limit = "some_limit"
        events_status = "Some Enterprise Information"
        body = {
            "enterpriseId": edge_id["enterprise_id"],
            "interval": {"start": interval_start, "end": interval_end},
            "filter": {"limit": limit},
            "edgeId": [edge_id["edge_id"]],
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=events_status)
        response_mock.status = 200

        velocloud_client._json_return = Mock(return_value=response_mock.json())
        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)) as mock_post:
            events = await velocloud_client.get_all_events(host, body)

            mock_post.assert_called_once()
            assert edge_id["host"] in mock_post.call_args[0][0]
            assert mock_post.call_args[1]["json"] == body
            assert events["body"] == events_status

    @pytest.mark.asyncio
    async def get_get_all_event_information_error_500_test(self, velocloud_client):
        host = "some_host"
        edge_id = {"host": host, "enterprise_id": 19, "edge_id": 99}
        interval_start = "Some interval start time"
        interval_end = "Some interval end time"
        limit = "some_limit"
        body = {
            "enterpriseId": edge_id["enterprise_id"],
            "interval": {"start": interval_start, "end": interval_end},
            "filter": {"limit": limit},
            "edgeId": [edge_id["edge_id"]],
        }

        response_mock = Mock()
        response_mock.status = 500
        response_mock.json = AsyncMock(return_value={})

        velocloud_client._cookies = {host: "cookie"}
        velocloud_client._json_return = Mock(return_value=response_mock.json())

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)) as mock_post:
            events = await velocloud_client.get_all_events(host, body)

            assert events == {"body": "Got internal error from Velocloud", "status": 500}

    @pytest.mark.asyncio
    async def get_all_enterprise_names_test(self, velocloud_client):
        host = "some_host"
        monitoring_aggregates_return = {"body": {"enterprises": [{"id": 1, "name": "A name"}]}, "status": 200}

        velocloud_client.get_monitoring_aggregates = AsyncMock(return_value=monitoring_aggregates_return)
        velocloud_client._cookies = {host: "cookie"}

        enterprise_names = await velocloud_client.get_all_enterprise_names()

        velocloud_client.get_monitoring_aggregates.assert_called_once_with(host)
        assert enterprise_names["body"] == [{"enterprise_name": "A name"}]

    @pytest.mark.asyncio
    async def json_return_ok_test(self, velocloud_client):
        host = "some_host"
        response = {"error": {"message": "tokenError [expired session cookie]"}}
        velocloud_client._login = AsyncMock()

        with raises(Exception):
            json_return = await velocloud_client._json_return(response, host)

            velocloud_client._login.assert_called_once()
            assert json_return == ""

    @pytest.mark.asyncio
    async def json_return_ko_different_error_test(self, velocloud_client):
        host = "some_host"
        response = {"error": {"message": "another_error"}}
        velocloud_client._login = AsyncMock()
        json_return = await velocloud_client._json_return(response, host)
        assert json_return == response

    @pytest.mark.asyncio
    async def json_return_ko_no_error_test(self, velocloud_client):
        host = "some_host"
        response = {"edge_status": "ok"}
        velocloud_client._login = AsyncMock()
        json_return = await velocloud_client._json_return(response, host)
        assert json_return == response

    @pytest.mark.asyncio
    async def json_return_ko_list_test(self, velocloud_client):
        host = "some_host"
        response = ["List"]
        velocloud_client._login = AsyncMock()
        json_return = await velocloud_client._json_return(response, host)
        assert json_return == response

    @pytest.mark.asyncio
    async def get_links_with_edge_info_ok_test(self, velocloud_client):
        host = "some_host"

        links_status: list = [
            {
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
        ]
        http_status_code = 200

        expected_result = {
            "body": links_status,
            "status": http_status_code,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=links_status)
        response_mock.status = http_status_code

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_links_with_edge_info(host)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_response_having_status_400_test(self, velocloud_client):
        host = "some_host"

        response_body = {"error": {"code": -32600, "message": "An error occurred while processing your request"}}
        http_status_code = 400

        expected_result = {
            "body": response_body,
            "status": http_status_code,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=response_body)
        response_mock.status = http_status_code

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_links_with_edge_info(host)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_response_having_status_5xx_test(self, velocloud_client):
        host = "some_host"

        response_body = {"error": {"code": -32600, "message": "An error occurred while processing your request"}}
        http_status_code = 500

        expected_result = {
            "body": "Got internal error from Velocloud",
            "status": http_status_code,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=response_body)
        response_mock.status = http_status_code

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_links_with_edge_info(host)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_response_having_status_200_and_pointing_out_token_expiration_test(
        self, velocloud_client
    ):
        host = "some_host"

        response_body = {"error": {"code": -32000, "message": "tokenError [expired session cookie]"}}
        http_status_code = 200

        expected_result = {
            "body": response_body,
            "status": 401,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=response_body)
        response_mock.status = http_status_code
        response_mock.headers = {
            "Expires": "0",
        }

        velocloud_client._cookies = {host: "cookie"}
        velocloud_client._login = AsyncMock()

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_links_with_edge_info(host)

        velocloud_client._login.assert_awaited_once_with(host)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_cookie_missing_for_target_host_test(self, velocloud_client):
        host = "some_host"

        response_body = {"error": {"code": -32000, "message": "tokenError [expired session cookie]"}}
        http_status_code = 200

        expected_result = {
            "body": response_body,
            "status": 401,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=response_body)
        response_mock.status = http_status_code
        response_mock.headers = {
            "Expires": "0",
        }

        velocloud_client._login = AsyncMock()

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_links_with_edge_info(host)

        velocloud_client._login.assert_awaited_once_with(host)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_connection_raising_exception_test(self, velocloud_client):
        host = "some_host"

        expected_result = {
            "body": "Error while connecting to Velocloud API",
            "status": 500,
        }

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(side_effect=ClientConnectionError)):
            result = await velocloud_client.get_links_with_edge_info(host)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_metric_info_ok_test(self, velocloud_client):
        host = "some_host"
        interval = {
            "start": "2020-10-19T15:22:03.345Z",
            "end": "2020-10-19T16:22:03.345Z",
        }

        links_status: list = [
            {
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
        ]
        http_status_code = 200

        expected_result = {
            "body": links_status,
            "status": http_status_code,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=links_status)
        response_mock.status = http_status_code

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_links_metric_info(host, interval)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_metric_info_with_response_having_status_400_test(self, velocloud_client):
        host = "some_host"
        interval = {
            "start": "2020-10-19T15:22:03.345Z",
            "end": "2020-10-19T16:22:03.345Z",
        }

        response_body = {"error": {"code": -32600, "message": "An error occurred while processing your request"}}
        http_status_code = 400

        expected_result = {
            "body": response_body,
            "status": http_status_code,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=response_body)
        response_mock.status = http_status_code

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_links_metric_info(host, interval)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_metric_info_with_response_having_status_5xx_test(self, velocloud_client):
        host = "some_host"
        interval = {
            "start": "2020-10-19T15:22:03.345Z",
            "end": "2020-10-19T16:22:03.345Z",
        }

        response_body = {"error": {"code": -32600, "message": "An error occurred while processing your request"}}
        http_status_code = 500

        expected_result = {
            "body": "Got internal error from Velocloud",
            "status": http_status_code,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=response_body)
        response_mock.status = http_status_code

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_links_metric_info(host, interval)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_metric_info_with_response_having_status_200_and_pointing_out_token_expiration_test(
        self, velocloud_client
    ):
        host = "some_host"
        interval = {
            "start": "2020-10-19T15:22:03.345Z",
            "end": "2020-10-19T16:22:03.345Z",
        }

        response_body = {"error": {"code": -32000, "message": "tokenError [expired session cookie]"}}
        http_status_code = 200

        expected_result = {
            "body": response_body,
            "status": 401,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=response_body)
        response_mock.status = http_status_code
        response_mock.headers = {
            "Expires": "0",
        }

        velocloud_client._cookies = {host: "cookie"}
        velocloud_client._login = AsyncMock()

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_links_metric_info(host, interval)

        velocloud_client._login.assert_awaited_once_with(host)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_links_metric_info_with_connection_raising_exception_test(self, velocloud_client):
        host = "some_host"
        interval = {
            "start": "2020-10-19T15:22:03.345Z",
            "end": "2020-10-19T16:22:03.345Z",
        }

        expected_result = {
            "body": "Error while connecting to Velocloud API",
            "status": 500,
        }

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(side_effect=ClientConnectionError)):
            result = await velocloud_client.get_links_metric_info(host, interval)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_enterprise_edges_ok_test(self, velocloud_client):
        host = "some_host"
        enterprise_id = 115

        enterprise_edge_list = [
            {
                "id": 1579,
                "created": "2020-02-13T17:44:16.000Z",
                "enterpriseId": 115,
                "siteId": 1587,
                "activationKey": "KAVV-VGW9-K4AK-RXSM",
                "activationKeyExpires": "2020-03-14T17:44:16.000Z",
                "activationState": "ACTIVATED",
                "activationTime": "2020-02-13T17:56:17.000Z",
                "softwareVersion": "3.3.2",
                "buildNumber": "R332-20191219-P1-GA",
                "factorySoftwareVersion": "3.3.0",
                "factoryBuildNumber": "R330-MTHD-20190328-GA",
                "softwareUpdated": "2020-02-13T18:03:20.000Z",
                "selfMacAddress": "50:9a:4c:dc:9a:70",
                "deviceId": "BCAF1B7B-4E1B-418E-BEA2-18D1C0932F55",
                "logicalId": "0c1b1358-f8ff-4881-b74e-0208028d76f5",
                "serialNumber": "3SQFXC2",
                "modelNumber": "edge610",
                "deviceFamily": "EDGE6X0",
                "name": "610_Rahul",
                "dnsName": None,
                "description": None,
                "alertsEnabled": 1,
                "operatorAlertsEnabled": 1,
                "edgeState": "CONNECTED",
                "edgeStateTime": "2020-12-15T17:43:00.000Z",
                "isLive": 0,
                "systemUpSince": "2020-11-16T02:32:23.000Z",
                "serviceUpSince": "2020-11-16T02:33:18.000Z",
                "lastContact": "2021-01-07T21:52:12.000Z",
                "serviceState": "IN_SERVICE",
                "endpointPkiMode": "CERTIFICATE_DISABLED",
                "haState": "UNCONFIGURED",
                "haPreviousState": "UNCONFIGURED",
                "haLastContact": "0000-00-00 00:00:00",
                "haSerialNumber": None,
                "modified": "2021-01-07T21:52:12.000Z",
                "isHub": True,
                "links": [
                    {
                        "id": 3216,
                        "created": "2020-03-09T14:30:11.000Z",
                        "edgeId": 1579,
                        "logicalId": "82:b2:34:26:c6:b6:0000",
                        "internalId": "00000005-f8ff-4881-b74e-0208028d76f5",
                        "interface": "GE5",
                        "macAddress": None,
                        "ipAddress": "50.210.234.118",
                        "netmask": None,
                        "networkSide": "WAN",
                        "networkType": "ETHERNET",
                        "displayName": "50.210.234.118",
                        "isp": None,
                        "org": None,
                        "lat": 37.402866,
                        "lon": -122.117332,
                        "lastActive": "2020-03-11T18:10:11.000Z",
                        "state": "DISCONNECTED",
                        "backupState": "UNCONFIGURED",
                        "vpnState": "STABLE",
                        "lastEvent": "2020-03-11T18:18:50.000Z",
                        "lastEventState": "DISCONNECTED",
                        "alertsEnabled": 1,
                        "operatorAlertsEnabled": 1,
                        "serviceState": "IN_SERVICE",
                        "modified": "2020-03-11T18:19:45.000Z",
                        "effectiveState": "DISCONNECTED",
                    },
                    {
                        "id": 3062,
                        "created": "2020-02-13T18:03:09.000Z",
                        "edgeId": 1579,
                        "logicalId": "82:b2:34:26:c6:b6:0000",
                        "internalId": "00000006-f8ff-4881-b74e-0208028d76f5",
                        "interface": "GE6",
                        "macAddress": None,
                        "ipAddress": "50.210.234.115",
                        "netmask": None,
                        "networkSide": "WAN",
                        "networkType": "ETHERNET",
                        "displayName": "50.210.234.115",
                        "isp": None,
                        "org": None,
                        "lat": 37.402866,
                        "lon": -122.117332,
                        "lastActive": "2021-01-07T21:50:03.000Z",
                        "state": "STABLE",
                        "backupState": "UNCONFIGURED",
                        "vpnState": "STABLE",
                        "lastEvent": "2020-11-16T12:07:25.000Z",
                        "lastEventState": "STABLE",
                        "alertsEnabled": 1,
                        "operatorAlertsEnabled": 1,
                        "serviceState": "IN_SERVICE",
                        "modified": "2021-01-07T21:50:03.000Z",
                        "effectiveState": "STABLE",
                    },
                ],
            }
        ]
        http_status_code = 200

        expected_result = {
            "body": enterprise_edge_list,
            "status": http_status_code,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=enterprise_edge_list)
        response_mock.status = http_status_code

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_enterprise_edges(host, enterprise_id)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_enterprise_edges_400_test(self, velocloud_client):
        host = "some_host"
        enterprise_id = 115

        enterprise_edge_list = {"error": {"code": -32600, "message": "An error occurred while processing your request"}}
        http_status_code = 400

        expected_result = {
            "body": enterprise_edge_list,
            "status": http_status_code,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=enterprise_edge_list)
        response_mock.status = http_status_code

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_enterprise_edges(host, enterprise_id)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_enterprise_edges_5xx_test(self, velocloud_client):
        host = "some_host"
        enterprise_id = 115

        enterprise_edge_list = {"error": {"code": -32600, "message": "An error occurred while processing your request"}}
        http_status_code = 500

        expected_result = {
            "body": "Got internal error from Velocloud",
            "status": http_status_code,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=enterprise_edge_list)
        response_mock.status = http_status_code

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_enterprise_edges(host, enterprise_id)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_enterprise_edges_with_response_having_status_200_and_pointing_out_token_expiration_test(
        self, velocloud_client
    ):
        host = "some_host"
        enterprise_id = 115

        error_result = {"error": {"code": -32600, "message": "tokenError [expired session cookie]"}}
        http_status_code = 200

        expected_result = {
            "body": error_result,
            "status": 401,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=error_result)
        response_mock.status = http_status_code
        response_mock.headers = {
            "Expires": "0",
        }

        velocloud_client._cookies = {host: "cookie"}
        velocloud_client._login = AsyncMock()

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_enterprise_edges(host, enterprise_id)

        velocloud_client._login.assert_awaited_once_with(host)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_enterprise_edges_with_connection_raising_exception_test(self, velocloud_client):
        host = "some_host"
        enterprise_id = 115

        expected_result = {
            "body": "Error while connecting to Velocloud API",
            "status": 500,
        }

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(side_effect=ClientConnectionError)):
            result = await velocloud_client.get_enterprise_edges(host, enterprise_id)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_configuration_modules_test(self, velocloud_client):
        host = "some_host"
        enterprise_id = 113
        edge_id = 123
        body_response = {
            "WAN": {
                "version": "1619512204741",
                "schemaVersion": "3.3.2",
                "type": "ENTERPRISE",
                "data": {
                    "networks": [],
                    "links": [],
                },
            }
        }
        edge_full_id = {
            "host": host,
            "enterprise_id": enterprise_id,
            "edge_id": edge_id,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=body_response)
        response_mock.status = 200

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_edge_configuration_modules(edge_full_id)

        assert result["body"] == body_response
        assert result["status"] == 200

    @pytest.mark.asyncio
    async def get_configuration_modules_internal_error_test(self, velocloud_client):
        host = "some_host"
        enterprise_id = 113
        edge_id = 123
        body_response = "Got internal error from Velocloud"
        edge_full_id = {
            "host": host,
            "enterprise_id": enterprise_id,
            "edge_id": edge_id,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=body_response)
        response_mock.status = 500

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_edge_configuration_modules(edge_full_id)

        assert result["body"] == body_response
        assert result["status"] == 500

    @pytest.mark.asyncio
    async def get_configuration_modules_bad_status_test(self, velocloud_client):
        host = "some_host"
        enterprise_id = None
        edge_id = 123
        body_response = {"error": {"message": "invalid enterpriseId"}}
        edge_full_id = {
            "host": host,
            "enterprise_id": enterprise_id,
            "edge_id": edge_id,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=body_response)
        response_mock.status = 400

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_edge_configuration_modules(edge_full_id)

        assert (
            result["body"] == f"Got 400 from Velocloud -> {body_response['error']['message']} "
            f"for edge {edge_full_id}"
        )
        assert result["status"] == 400

    @pytest.mark.asyncio
    async def get_configuration_modules_exception_test(self, velocloud_client):
        host = "some_host"
        enterprise_id = 113
        edge_id = 123
        edge_full_id = {
            "host": host,
            "enterprise_id": enterprise_id,
            "edge_id": edge_id,
        }

        expected_result = {
            "body": "Error while connecting to Velocloud API",
            "status": 500,
        }

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(side_effect=ClientConnectionError)):
            result = await velocloud_client.get_edge_configuration_modules(edge_full_id)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_network_enterprises_test(self, velocloud_client, make_http_response, make_network_enterprises_body):
        host = "some_host"
        enterprise_ids = [113]

        velocloud_client._cookies = {host: "cookie"}

        body_response = make_network_enterprises_body(enterprise_ids=enterprise_ids, n_edges=1)
        response_mock = make_http_response(status=200, body=body_response)

        expected_response = {"body": body_response, "status": 200}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_network_enterprises(host, enterprise_ids)

        assert result == expected_response

    @pytest.mark.asyncio
    async def get_network_enterprises_invalid_request_test(self, velocloud_client, make_error_response):
        enterprise_ids = [1234]
        host = "some_host"

        velocloud_client._cookies = {host: "cookie"}

        error_message = "An error occurred while processing your request"
        error_response = make_error_response(status=400, error_code=-32600, message=error_message)

        expected_result = {
            "body": f"Got 400 from Velocloud --> {error_message} for enterprise ids: {enterprise_ids}",
            "status": 400,
        }

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=error_response)):
            result = await velocloud_client.get_network_enterprises(host, enterprise_ids)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_network_enterprises_server_error_test(self, velocloud_client, make_error_response):
        enterprise_ids = ["1234"]
        host = "some_host"
        error_message = "An error occurred while processing your request"

        velocloud_client._cookies = {host: "cookie"}

        error_response = make_error_response(status=500, error_code=-32600, message=error_message)

        expected_result = {
            "body": "Got internal error from Velocloud",
            "status": 500,
        }

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=error_response)):
            result = await velocloud_client.get_network_enterprises(host, enterprise_ids)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_network_enterprises_exception_test(self, velocloud_client):
        enterprise_ids = [1234]
        host = "some_host"

        velocloud_client._cookies = {host: "cookie"}

        expected_result = {
            "body": "Error while connecting to Velocloud API",
            "status": 500,
        }

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(side_effect=ClientConnectionError)):
            result = await velocloud_client.get_network_enterprises(host, enterprise_ids)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_network_gateways_ok_test(self, velocloud_client):
        host = "some_host"

        body = []
        http_status_code = 200

        expected_result = {
            "body": body,
            "status": http_status_code,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=body)
        response_mock.status = http_status_code

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_network_gateways(host)

        assert result == expected_result

    @pytest.mark.asyncio
    async def get_gateway_status_metrics_ok_test(self, velocloud_client):
        host = "some_host"
        gateway_id = 1
        interval = {}
        metrics = []

        body = {}
        http_status_code = 200

        expected_result = {
            "body": body,
            "status": http_status_code,
        }

        response_mock = Mock()
        response_mock.json = AsyncMock(return_value=body)
        response_mock.status = http_status_code

        velocloud_client._cookies = {host: "cookie"}

        velocloud_client._session.cookie_jar.filter_cookies = Mock(
            return_value={'velocloud.session': 'some_session_id'})

        with patch.object(velocloud_client._session, "post", new=AsyncMock(return_value=response_mock)):
            result = await velocloud_client.get_gateway_status_metrics(host, gateway_id, interval, metrics)

        assert result == expected_result
