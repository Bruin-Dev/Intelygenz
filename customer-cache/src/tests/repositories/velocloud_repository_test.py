from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from application.repositories import nats_error_response
from application.repositories import velocloud_repository as velocloud_repository_module
from application.repositories.velocloud_repository import VelocloudRepository
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid
from unittest.mock import call

uuid_ = uuid()
uuid_mock = patch.object(velocloud_repository_module, 'uuid', return_value=uuid_)


class TestVelocloudRepository:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig

        velocloud_repository = VelocloudRepository(config, logger, event_bus)

        assert velocloud_repository._event_bus is event_bus
        assert velocloud_repository._logger is logger
        assert velocloud_repository._config is config

    @pytest.mark.asyncio
    async def get_edges_with_default_rpc_timeout_test(self, instance_velocloud_repository, instance_velocloud_request,
                                                      instance_velocloud_response):
        instance_velocloud_request['request_id'] = uuid_
        instance_velocloud_response['request_id'] = uuid_
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=instance_velocloud_response)
        with uuid_mock:
            result = await instance_velocloud_repository.get_edges_links_by_host('mettel.velocloud.net')

        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with("get.links.with.edge.info",
                                                                                      instance_velocloud_request,
                                                                                      timeout=300)
        assert result == instance_velocloud_response

    @pytest.mark.asyncio
    async def get_edges_with_custom_rpc_timeout_test(self, instance_velocloud_repository, instance_velocloud_request,
                                                     instance_velocloud_response):
        instance_velocloud_request['request_id'] = uuid_
        instance_velocloud_response['request_id'] = uuid_
        rpc_timeout = 1000
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=instance_velocloud_response)
        with uuid_mock:
            result = await instance_velocloud_repository.get_edges_links_by_host('mettel.velocloud.net',
                                                                                 rpc_timeout=rpc_timeout)

        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with("get.links.with.edge.info",
                                                                                      instance_velocloud_request,
                                                                                      timeout=rpc_timeout)
        assert result == instance_velocloud_response

    @pytest.mark.asyncio
    async def get_all_enterprise_edges_failed_rpc_test(self, instance_velocloud_repository,
                                                       instance_enterprise_velocloud_request):
        instance_enterprise_velocloud_request['request_id'] = uuid_
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)
        instance_velocloud_repository._notify_error = CoroutineMock()

        host = 'mettel.velocloud.net'
        enterprise_id = '123'
        with uuid_mock:
            result = await instance_velocloud_repository._get_all_enterprise_edges(host, enterprise_id)

        instance_velocloud_repository._notify_error.assert_awaited_once()
        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "request.enterprises.edges", instance_enterprise_velocloud_request, timeout=300)
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_all_enterprise_edges_non_2xx_test(self, instance_velocloud_repository,
                                                    instance_enterprise_velocloud_request,
                                                    instance_enterprise_edge_response):

        instance_enterprise_velocloud_request['request_id'] = uuid_
        instance_enterprise_edge_response['request_id'] = uuid_
        instance_enterprise_edge_response['body'] = 'Failed'
        instance_enterprise_edge_response['status'] = 400

        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(
            return_value=instance_enterprise_edge_response)
        instance_velocloud_repository._notify_error = CoroutineMock()

        host = 'mettel.velocloud.net'
        enterprise_id = '123'
        with uuid_mock:
            result = await instance_velocloud_repository._get_all_enterprise_edges(host, enterprise_id)

        instance_velocloud_repository._notify_error.assert_awaited_once()
        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "request.enterprises.edges", instance_enterprise_velocloud_request, timeout=300)
        assert result == instance_enterprise_edge_response

    @pytest.mark.asyncio
    async def notify_error_test(self, instance_velocloud_repository):
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock()
        error_dict = {'request_id': uuid_,
                      'message': 'Failed'}
        with uuid_mock:
            await instance_velocloud_repository._notify_error('Failed')
        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with("notification.slack.request",
                                                                                      error_dict,
                                                                                      timeout=10)

    @pytest.mark.asyncio
    async def get_all_velo_test(self, instance_velocloud_repository, instance_velocloud_response,
                                instance_enterprise_edge_response):
        wrong_request = {
            'body': [],
            'status': 400
        }
        host1 = testconfig.VELOCLOUD_HOST[0]
        host2 = testconfig.VELOCLOUD_HOST[1]
        host3 = testconfig.VELOCLOUD_HOST[2]
        host4 = testconfig.VELOCLOUD_HOST[3]
        instance_velocloud_repository._notify_error = CoroutineMock()
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(
            side_effect=[instance_velocloud_response, wrong_request, wrong_request, wrong_request,
                         instance_enterprise_edge_response])
        with uuid_mock:
            edges_with_serial = await instance_velocloud_repository.get_all_velo_edges()
        instance_velocloud_repository._event_bus.rpc_request.assert_has_awaits([
            call('get.links.with.edge.info', {'request_id': uuid_, 'body': {'host': host1}}, timeout=300),
            call('get.links.with.edge.info', {'request_id': uuid_, 'body': {'host': host2}}, timeout=300),
            call('get.links.with.edge.info', {'request_id': uuid_, 'body': {'host': host3}}, timeout=300),
            call('get.links.with.edge.info', {'request_id': uuid_, 'body': {'host': host4}}, timeout=300),
            call('request.enterprises.edges', {'request_id': uuid_, 'body': {'host': host1, 'enterprise_id': 1}},
                 timeout=90)
        ])
        assert len(edges_with_serial) == 2

    @pytest.mark.asyncio
    async def get_all_special_values_velo_test(self, instance_velocloud_repository,
                                               instance_special_velocloud_response,
                                               instance_enterprise_edge_response):
        wrong_request = {
            'body': [],
            'status': 400
        }
        host1 = testconfig.VELOCLOUD_HOST[0]
        host2 = testconfig.VELOCLOUD_HOST[1]
        host3 = testconfig.VELOCLOUD_HOST[2]
        host4 = testconfig.VELOCLOUD_HOST[3]
        instance_velocloud_repository._notify_error = CoroutineMock()
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(
            side_effect=[instance_special_velocloud_response, wrong_request, wrong_request, Exception,
                         instance_enterprise_edge_response])
        with uuid_mock:
            edges_with_serial = await instance_velocloud_repository.get_all_velo_edges()
        instance_velocloud_repository._event_bus.rpc_request.assert_has_awaits([
            call('get.links.with.edge.info', {'request_id': uuid_, 'body': {'host': host1}}, timeout=300),
            call('get.links.with.edge.info', {'request_id': uuid_, 'body': {'host': host2}}, timeout=300),
            call('get.links.with.edge.info', {'request_id': uuid_, 'body': {'host': host3}}, timeout=300),
            call('get.links.with.edge.info', {'request_id': uuid_, 'body': {'host': host4}}, timeout=300),
            call('request.enterprises.edges', {'request_id': uuid_, 'body': {'host': host1, 'enterprise_id': 1}},
                 timeout=90)

        ])
        assert len(edges_with_serial) == 0
