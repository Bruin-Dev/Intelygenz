from typing import Dict
from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import patch
from unittest.mock import call

import pytest

from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import velocloud_repository as velocloud_repository_module
from application.repositories.velocloud_repository import VelocloudRepository
from application.repositories import EdgeIdentifier
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(velocloud_repository_module, 'uuid', return_value=uuid_)

nats_error_response = {'body': None, 'status': 503}


class TestVelocloudRepository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)

        assert velocloud_repository._event_bus is event_bus
        assert velocloud_repository._logger is logger
        assert velocloud_repository._config is config
        assert velocloud_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_edges_links_by_host_test(self, instance_server, link_1_host_1, link_1_host_2, link_1_host_3,
                                           link_1_host_4):
        expected = {
            'body': [
                link_1_host_1,
                link_1_host_2,
                link_1_host_3,
                link_1_host_4
            ],
            'status': 200
        }
        host = 'mettel.host'
        rpc_response_mock = {
            'body': [
                link_1_host_1,
                link_1_host_2,
                link_1_host_3,
                link_1_host_4
            ],
            'status': 200
        }
        rpc_responses_mock = [
            rpc_response_mock
        ]
        rpc_request = {
            "request_id": uuid_,
            "body": {
                'host': host
            },
        }
        instance_server._velocloud_repository._event_bus.rpc_request = CoroutineMock(side_effect=rpc_responses_mock)

        with uuid_mock:
            result = await instance_server._velocloud_repository.get_edges_links_by_host(host)

        assert expected == result
        instance_server._velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "get.links.with.edge.info", rpc_request, timeout=300)

    @pytest.mark.asyncio
    async def get_edges_links_by_host_with_exception_test(self, instance_server):
        expected = {
            'body': None,
            'status': 503
        }
        host = 'mettel.host'

        rpc_responses_mock = [
            Exception('Failed!'),
            None
        ]
        rpc_request = {
            "request_id": uuid_,
            "body": {
                'host': host
            },
        }
        err_msg = 'An error occurred when requesting edge list from Velocloud -> Failed!'
        instance_server._velocloud_repository._event_bus.rpc_request = CoroutineMock(side_effect=rpc_responses_mock)
        instance_server._velocloud_repository._notify_error = CoroutineMock()

        with uuid_mock:
            result = await instance_server._velocloud_repository.get_edges_links_by_host(host)

        assert expected == result
        instance_server._velocloud_repository._notify_error.assert_awaited_once_with(err_msg)
        instance_server._velocloud_repository._event_bus.rpc_request.assert_has_awaits([
            call("get.links.with.edge.info", rpc_request, timeout=300),
        ])

    @pytest.mark.asyncio
    async def get_edges_links_by_host_with_nats_error_test(self, instance_server):
        expected = {
            'body': None,
            'status': 503
        }
        host = 'mettel.host'

        rpc_responses_mock = [
            nats_error_response,
            None
        ]
        rpc_request = {
            "request_id": uuid_,
            "body": {
                'host': host
            },
        }
        err_msg = 'Error while retrieving edges links in DEV environment: Error 503 - None'
        instance_server._velocloud_repository._event_bus.rpc_request = CoroutineMock(side_effect=rpc_responses_mock)
        instance_server._velocloud_repository._notify_error = CoroutineMock()
        with uuid_mock:
            result = await instance_server._velocloud_repository.get_edges_links_by_host(host)

        assert expected == result
        instance_server._velocloud_repository._event_bus.rpc_request.assert_has_awaits([
            call("get.links.with.edge.info", rpc_request, timeout=300),
        ])
        instance_server._velocloud_repository._notify_error.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def get_all_links_with_edge_info_test(self, instance_server, links_host_1_response,
                                                links_host_2_response, links_host_3_response,
                                                links_host_4_response):
        all_links = links_host_1_response['body'] + links_host_2_response['body'] + \
                    links_host_3_response['body'] + links_host_4_response['body']
        expected = {
            'request_id': uuid_,
            'status': 200,
            'body': all_links
        }
        links_by_host_mock = [
            links_host_1_response,
            links_host_2_response,
            links_host_3_response,
            links_host_4_response
        ]
        instance_server._velocloud_repository.get_edges_links_by_host = CoroutineMock(side_effect=links_by_host_mock)

        with uuid_mock:
            result = await instance_server._velocloud_repository.get_all_links_with_edge_info()

        assert expected == result
        instance_server._velocloud_repository.get_edges_links_by_host.assert_has_awaits([
            call(host=instance_server._config.SITES_MONITOR_CONFIG['velo_servers'][0]),
            call(host=instance_server._config.SITES_MONITOR_CONFIG['velo_servers'][1]),
            call(host=instance_server._config.SITES_MONITOR_CONFIG['velo_servers'][2]),
            call(host=instance_server._config.SITES_MONITOR_CONFIG['velo_servers'][3])
        ])

    @pytest.mark.asyncio
    async def get_all_links_with_edge_info_with_one_error_test(self, instance_server, links_host_1_response,
                                                               links_host_2_response, links_host_3_response,
                                                               links_host_4_response_error):
        all_links = links_host_1_response['body'] + links_host_2_response['body'] + \
                    links_host_3_response['body']
        expected = {
            'request_id': uuid_,
            'status': 200,
            'body': all_links
        }
        links_by_host_mock = [
            links_host_1_response,
            links_host_2_response,
            links_host_3_response,
            links_host_4_response_error
        ]
        instance_server._velocloud_repository.get_edges_links_by_host = CoroutineMock(side_effect=links_by_host_mock)

        with uuid_mock:
            result = await instance_server._velocloud_repository.get_all_links_with_edge_info()

        assert expected == result
        instance_server._velocloud_repository.get_edges_links_by_host.assert_has_awaits([
            call(host=instance_server._config.SITES_MONITOR_CONFIG['velo_servers'][0]),
            call(host=instance_server._config.SITES_MONITOR_CONFIG['velo_servers'][1]),
            call(host=instance_server._config.SITES_MONITOR_CONFIG['velo_servers'][2]),
            call(host=instance_server._config.SITES_MONITOR_CONFIG['velo_servers'][3])
        ])

    def group_links_by_edge_test(self, instance_server, list_all_links_with_edge_info, edge_1_host_1, edge_2_host_1,
                                 edge_identifier_1_host_1, edge_identifier_2_host_1, edge_identifier_1_host_2,
                                 edge_1_host_2, edge_identifier_1_host_3, edge_1_host_3, edge_identifier_1_host_4,
                                 edge_1_host_4):
        expected: Dict[EdgeIdentifier, dict] = {
            edge_identifier_1_host_1: edge_1_host_1,
            edge_identifier_2_host_1: edge_2_host_1,
            edge_identifier_1_host_2: edge_1_host_2,
            edge_identifier_1_host_3: edge_1_host_3,
            edge_identifier_1_host_4: edge_1_host_4
        }
        result = instance_server._velocloud_repository.group_links_by_edge(list_all_links_with_edge_info['body'])
        assert expected == result

    @pytest.mark.asyncio
    async def notify_error_test(self, instance_server):
        instance_server._velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()
        error_msg = 'Failed'
        with uuid_mock:
            await instance_server._velocloud_repository._notify_error(error_msg)
        instance_server._velocloud_repository._notifications_repository.send_slack_message.assert_awaited_once_with(
            error_msg)
