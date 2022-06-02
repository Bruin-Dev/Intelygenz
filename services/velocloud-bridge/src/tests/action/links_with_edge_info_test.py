from unittest.mock import Mock

import pytest
from application.actions.links_with_edge_info import LinksWithEdgeInfo
from asynctest import CoroutineMock
from shortuuid import uuid

uuid_ = uuid()


class TestLinksWithEdgeInfo:
    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        velocloud_repository = Mock()

        actions = LinksWithEdgeInfo(event_bus, logger, velocloud_repository)

        assert actions._event_bus is event_bus
        assert actions._logger is logger
        assert actions._velocloud_repository is velocloud_repository

    @pytest.mark.asyncio
    async def get_links_with_edge_info_ok_test(self):
        velocloud_host = "mettel.velocloud.net"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        request = {
            "request_id": uuid_,
            "response_topic": response_topic,
            "body": {
                "host": velocloud_host,
            },
        }

        repository_result = {
            "body": [
                {
                    "host": velocloud_host,
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
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=repository_result)

        action = LinksWithEdgeInfo(event_bus, logger, velocloud_repository)

        await action.get_links_with_edge_info(request)

        velocloud_repository.get_links_with_edge_info.assert_awaited_once_with(velocloud_host)
        event_bus.publish_message.assert_awaited_once_with(response_topic, response)

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_missing_body_in_request_test(self):
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
        velocloud_repository.get_links_with_edge_info = CoroutineMock()

        action = LinksWithEdgeInfo(event_bus, logger, velocloud_repository)

        await action.get_links_with_edge_info(request)

        velocloud_repository.get_links_with_edge_info.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic, response)

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_missing_host_in_body_test(self):
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        request = {
            "request_id": uuid_,
            "response_topic": response_topic,
            "body": {},
        }

        response = {
            "request_id": uuid_,
            "body": 'Must include "host" in the body of the request',
            "status": 400,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock()

        action = LinksWithEdgeInfo(event_bus, logger, velocloud_repository)

        await action.get_links_with_edge_info(request)

        velocloud_repository.get_links_with_edge_info.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic, response)
