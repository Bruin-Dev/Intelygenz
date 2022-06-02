from unittest.mock import Mock

import pytest
from application.actions.enterprise_edge_list import EnterpriseEdgeList
from asynctest import CoroutineMock
from shortuuid import uuid

uuid_ = uuid()


class TestEnterpriseEdgeList:
    def instance_test(self):
        event_bus = Mock()
        velocloud_repo = Mock()
        logger = Mock()

        enterprise_edge_list = EnterpriseEdgeList(event_bus, velocloud_repo, logger)

        assert enterprise_edge_list._event_bus == event_bus
        assert enterprise_edge_list._velocloud_repository == velocloud_repo
        assert enterprise_edge_list._logger == logger

    @pytest.mark.asyncio
    async def enterprise_edge_list_test(self):
        velocloud_host = "mettel.velocloud.net"
        enterprise_id = 115
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"

        request = {
            "request_id": uuid_,
            "response_topic": response_topic,
            "body": {
                "host": velocloud_host,
                "enterprise_id": enterprise_id,
            },
        }
        enterprise_edge_list_results = {"body": ["List of Enterprise Edges"], "status": 200}
        response = {
            "request_id": uuid_,
            **enterprise_edge_list_results,
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        velocloud_repo = Mock()
        velocloud_repo.get_enterprise_edges = CoroutineMock(return_value=enterprise_edge_list_results)
        logger = Mock()

        enterprise_edge_list = EnterpriseEdgeList(event_bus, velocloud_repo, logger)

        await enterprise_edge_list.enterprise_edge_list(request)
        velocloud_repo.get_enterprise_edges.assert_awaited_once_with(velocloud_host, enterprise_id)
        event_bus.publish_message.assert_awaited_once_with(response_topic, response)

    @pytest.mark.asyncio
    async def enterprise_edge_list_no_body_test(self):
        velocloud_host = "mettel.velocloud.net"
        enterprise_id = 115
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"

        request = {
            "request_id": uuid_,
            "response_topic": response_topic,
        }

        response = {"request_id": uuid_, "body": 'Must include "body" in request', "status": 400}

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        velocloud_repo = Mock()
        velocloud_repo.get_enterprise_edges = CoroutineMock()
        logger = Mock()

        enterprise_edge_list = EnterpriseEdgeList(event_bus, velocloud_repo, logger)

        await enterprise_edge_list.enterprise_edge_list(request)
        velocloud_repo.get_enterprise_edges.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic, response)

    @pytest.mark.asyncio
    async def enterprise_edge_list_missing_body_keys_test(self):
        velocloud_host = "mettel.velocloud.net"
        enterprise_id = 115
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"

        request = {"request_id": uuid_, "response_topic": response_topic, "body": {}}

        response = {
            "request_id": uuid_,
            "body": 'Must include "host" and "enterprise_id" in request "body"',
            "status": 400,
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        velocloud_repo = Mock()
        velocloud_repo.get_enterprise_edges = CoroutineMock()
        logger = Mock()

        enterprise_edge_list = EnterpriseEdgeList(event_bus, velocloud_repo, logger)

        await enterprise_edge_list.enterprise_edge_list(request)
        velocloud_repo.get_enterprise_edges.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic, response)
