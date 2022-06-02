from unittest.mock import Mock

import pytest
from application.actions.links_metric_info import LinksMetricInfo
from asynctest import CoroutineMock
from shortuuid import uuid

uuid_ = uuid()


class TestLinksMetricInfo:
    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        velocloud_repository = Mock()

        actions = LinksMetricInfo(event_bus, logger, velocloud_repository)

        assert actions._event_bus is event_bus
        assert actions._logger is logger
        assert actions._velocloud_repository is velocloud_repository

    @pytest.mark.asyncio
    async def get_links_metric_info_ok_test(self):
        velocloud_host = "mettel.velocloud.net"
        interval = {
            "start": "2020-10-19T15:22:03.345Z",
            "end": "2020-10-19T16:22:03.345Z",
        }

        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        request = {
            "request_id": uuid_,
            "response_topic": response_topic,
            "body": {
                "host": velocloud_host,
                "interval": interval,
            },
        }

        repository_result = {
            "body": [
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
                        "host": velocloud_host,
                    },
                }
            ],
            "status": 200,
        }
        response = {
            "request_id": uuid_,
            **repository_result,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metric_info = CoroutineMock(return_value=repository_result)

        action = LinksMetricInfo(event_bus, logger, velocloud_repository)

        await action.get_links_metric_info(request)

        velocloud_repository.get_links_metric_info.assert_awaited_once_with(velocloud_host, interval)
        event_bus.publish_message.assert_awaited_once_with(response_topic, response)

    @pytest.mark.asyncio
    async def get_links_metric_info_with_missing_body_in_request_test(self):
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        request = {
            "request_id": uuid_,
            "response_topic": response_topic,
        }

        response = {
            "request_id": uuid_,
            "body": 'Must include "body" in the request',
            "status": 400,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metric_info = CoroutineMock()

        action = LinksMetricInfo(event_bus, logger, velocloud_repository)

        await action.get_links_metric_info(request)

        velocloud_repository.get_links_metric_info.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic, response)

    @pytest.mark.asyncio
    async def get_links_metric_info_with_missing_host_in_body_test(self):
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        request = {
            "request_id": uuid_,
            "response_topic": response_topic,
            "body": {
                "interval": {
                    "start": "2020-10-19T15:22:03.345Z",
                    "end": "2020-10-19T16:22:03.345Z",
                }
            },
        }

        response = {
            "request_id": uuid_,
            "body": 'Must include "host" and "interval" in the body of the request',
            "status": 400,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metric_info = CoroutineMock()

        action = LinksMetricInfo(event_bus, logger, velocloud_repository)

        await action.get_links_metric_info(request)

        velocloud_repository.get_links_metric_info.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic, response)

    @pytest.mark.asyncio
    async def get_links_metric_info_with_missing_interval_in_body_test(self):
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        request = {
            "request_id": uuid_,
            "response_topic": response_topic,
            "body": {"host": "mettel.velocloud.net"},
        }

        response = {
            "request_id": uuid_,
            "body": 'Must include "host" and "interval" in the body of the request',
            "status": 400,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metric_info = CoroutineMock()

        action = LinksMetricInfo(event_bus, logger, velocloud_repository)

        await action.get_links_metric_info(request)

        velocloud_repository.get_links_metric_info.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic, response)
