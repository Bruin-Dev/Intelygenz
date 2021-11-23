from unittest.mock import patch

import pytest
from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import customer_cache_repository as customer_cache_repository_module
from application.repositories import nats_error_response
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(customer_cache_repository_module, 'uuid', return_value=uuid_)


class TestCustomerCacheRepository:
    def instance_test(self, customer_cache_repository, event_bus, logger, notifications_repository):
        assert customer_cache_repository._event_bus is event_bus
        assert customer_cache_repository._logger is logger
        assert customer_cache_repository._notifications_repository is notifications_repository
        assert customer_cache_repository._config is testconfig

    @pytest.mark.asyncio
    async def get_cache__no_filter_specified_test(
            self, customer_cache_repository, make_cached_edge, make_customer_cache, make_get_cache_request,
            make_rpc_response):
        edge_1_cache_info = make_cached_edge()
        edge_2_cache_info = make_cached_edge()
        customer_cache = make_customer_cache(edge_1_cache_info, edge_2_cache_info)

        request = make_get_cache_request(request_id=uuid_)
        response = make_rpc_response(
            request_id=uuid_,
            body=customer_cache,
            status=200,
        )

        customer_cache_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            result = await customer_cache_repository.get_cache()

        customer_cache_repository._event_bus.rpc_request.assert_awaited_once_with(
            "customer.cache.get", request, timeout=60
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_cache__filter_specified_test(
            self, customer_cache_repository, make_cached_edge, make_customer_cache, make_get_cache_request,
            make_rpc_response):
        filter_ = {'mettel.velocloud.net': []}

        edge_1_cache_info = make_cached_edge()
        edge_2_cache_info = make_cached_edge()
        customer_cache = make_customer_cache(edge_1_cache_info, edge_2_cache_info)

        request = make_get_cache_request(
            request_id=uuid_,
            filter_=filter_,
        )
        response = make_rpc_response(
            request_id=uuid_,
            body=customer_cache,
            status=200,
        )

        customer_cache_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            result = await customer_cache_repository.get_cache(velo_filter=filter_)

        customer_cache_repository._event_bus.rpc_request.assert_awaited_once_with(
            "customer.cache.get", request, timeout=60
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_cache__rpc_request_failing_test(
            self, customer_cache_repository, make_get_cache_request):
        request = make_get_cache_request(request_id=uuid_)

        customer_cache_repository._event_bus.rpc_request.side_effect = Exception
        customer_cache_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await customer_cache_repository.get_cache()

        customer_cache_repository._event_bus.rpc_request.assert_awaited_once_with(
            "customer.cache.get", request, timeout=60
        )
        customer_cache_repository._notifications_repository.send_slack_message.assert_awaited_once()
        customer_cache_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_cache__rpc_request_has_202_status_test(
            self, customer_cache_repository, make_get_cache_request, get_customer_cache_202_response):
        request = make_get_cache_request(request_id=uuid_)

        customer_cache_repository._event_bus.rpc_request.return_value = get_customer_cache_202_response
        customer_cache_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await customer_cache_repository.get_cache()

        customer_cache_repository._event_bus.rpc_request.assert_awaited_once_with(
            "customer.cache.get", request, timeout=60
        )
        customer_cache_repository._notifications_repository.send_slack_message.assert_awaited_once()
        customer_cache_repository._logger.error.assert_called_once()
        assert result == get_customer_cache_202_response

    @pytest.mark.asyncio
    async def get_cache_for_affecting_monitoring_test(self, customer_cache_repository):
        velocloud_host_1 = "mettel.velocloud.net"
        velocloud_host_2 = "metvco02.mettel.net"
        velocloud_host_1_enterprise_1_id = 100
        velocloud_host_1_enterprise_2_id = 10000
        velocloud_host_2_enterprise_1_id = 1000000

        filter_ = {
            velocloud_host_1: [
                velocloud_host_1_enterprise_1_id,
                velocloud_host_1_enterprise_2_id,
            ],
            velocloud_host_2: [
                velocloud_host_2_enterprise_1_id,
            ],
        }

        custom_monitor_config = customer_cache_repository._config.MONITOR_CONFIG.copy()
        custom_monitor_config['velo_filter'] = filter_
        with patch.dict(customer_cache_repository._config.MONITOR_CONFIG, custom_monitor_config):
            await customer_cache_repository.get_cache_for_affecting_monitoring()

        # This snippet makes sure that the enterprises filter is the same for each velocloud host, regardless of the
        # order in which they appear in both lists
        call_args, call_kwargs = customer_cache_repository.get_cache.await_args
        for velocloud_host, enterprises in call_kwargs['velo_filter'].items():
            assert set(enterprises) == set(filter_[velocloud_host])
