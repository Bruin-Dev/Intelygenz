from unittest.mock import Mock

import pytest

from asynctest import CoroutineMock
from shortuuid import uuid

from application.actions.network_enterprise_edge_list import NetworkEnterpriseEdgeList

uuid_ = uuid()
response_topic_ = '_INBOX.2007314fe0fcb2cdc2a2914c1'


class TestNetworkEnterpriseEdges:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        velocloud_repository = Mock()

        actions = NetworkEnterpriseEdgeList(event_bus, velocloud_repository, logger)

        assert actions._event_bus is event_bus
        assert actions._logger is logger
        assert actions._velocloud_repository is velocloud_repository

    @pytest.mark.asyncio
    async def enterprise_edge_list_test(self,
                                        event_bus,
                                        make_rpc_request,
                                        make_network_enterprises_edges,
                                        network_enterprise_edge_list_action):
        velocloud_host = 'mettel.velocloud.net'
        enterprise_ids = [3]
        request_body = {
            'host': velocloud_host,
            'enterprise_ids': enterprise_ids
        }
        request = make_rpc_request(request_id=uuid_, response_topic=response_topic_, **request_body)

        repository_response = {
            'body': make_network_enterprises_edges(enterprise_id=3, n_edges=3),
            'status': 200,
        }
        response = {
            'request_id': uuid_,
            **repository_response,
        }

        action = network_enterprise_edge_list_action
        get_network_enterprise_edges_mock = CoroutineMock(return_value=repository_response)
        action._velocloud_repository.get_network_enterprise_edges = get_network_enterprise_edges_mock

        await action.get_enterprise_edge_list(request)

        get_network_enterprise_edges_mock.assert_awaited_once_with(velocloud_host, enterprise_ids)
        event_bus.publish_message.assert_awaited_once_with(response_topic_, response)

    @pytest.mark.asyncio
    async def get_enterprise_edge_list_missing_body_test(self,
                                                         event_bus,
                                                         make_rpc_request,
                                                         network_enterprise_edge_list_action):
        request = make_rpc_request(request_id=uuid_, response_topic=response_topic_)
        response = {
            'request_id': uuid_,
            'body': 'Must include "body" in request',
            'status': 400,
        }

        action = network_enterprise_edge_list_action

        await action.get_enterprise_edge_list(request)

        event_bus.publish_message.assert_awaited_once_with(response_topic_, response)

    @pytest.mark.asyncio
    async def get_enterprise_edge_list_missing_body_parameter_test(self,
                                                                   event_bus,
                                                                   make_rpc_request,
                                                                   network_enterprise_edge_list_action):
        request_body = {'host': 'mettel.velocloud.net'}

        request = make_rpc_request(request_id=uuid_, response_topic=response_topic_, **request_body)
        response = {
            'request_id': uuid_,
            'body': 'Must include "host" and "enterprise_ids" in request" "body"',
            'status': 400,
        }

        action = network_enterprise_edge_list_action
        await action.get_enterprise_edge_list(request)

        event_bus.publish_message.assert_awaited_once_with(response_topic_, response)

    @pytest.mark.asyncio
    async def get_enterprise_edge_list_empty_enterprise_ids(self,
                                                            event_bus,
                                                            make_rpc_request,
                                                            network_enterprise_edge_list_action):
        request_body = {'host': 'mettel.velocloud.net', 'enterprise_ids': []}
        request = make_rpc_request(request_id=uuid_, response_topic=response_topic_, **request_body)

        response = {
            'request_id': uuid_,
            'body': 'Must contain at least one element in "enterprise_ids"',
            'status': 400,
        }

        action = network_enterprise_edge_list_action

        await action.get_enterprise_edge_list(request)

        event_bus.publish_message.assert_awaited_once_with(response_topic_, response)
