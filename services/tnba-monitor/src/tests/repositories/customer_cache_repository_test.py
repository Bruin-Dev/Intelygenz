from unittest.mock import AsyncMock, Mock, patch

import pytest
from application.repositories import customer_cache_repository as customer_cache_repository_module
from application.repositories import nats_error_response
from application.repositories.utils_repository import to_json_bytes
from config import testconfig
from nats.aio.msg import Msg
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(customer_cache_repository_module, "uuid", return_value=uuid_)


class TestCustomerCacheRepository:
    def instance_test(self, customer_cache_repository, nats_client, notifications_repository):
        assert customer_cache_repository._nats_client is nats_client
        assert customer_cache_repository._config is testconfig
        assert customer_cache_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_cache_with_no_filter_specified_test(
        self, customer_cache_repository, make_rpc_request, make_rpc_response, edge_cached_info_1, edge_cached_info_2
    ):
        filter_ = {}

        request = make_rpc_request(request_id=uuid_, filter=filter_)
        response = make_rpc_response(request_id=uuid_, body=[edge_cached_info_1, edge_cached_info_2], status=200)

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        customer_cache_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await customer_cache_repository.get_cache()

        customer_cache_repository._nats_client.request.assert_awaited_once_with(
            "customer.cache.get", to_json_bytes(request), timeout=120
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_custom_filter_specified_test(
        self, customer_cache_repository, make_rpc_request, make_rpc_response, edge_cached_info_1, edge_cached_info_2
    ):
        filter_ = {"mettel.velocloud.net": []}

        request = make_rpc_request(request_id=uuid_, filter=filter_)
        response = make_rpc_response(request_id=uuid_, body=[edge_cached_info_1, edge_cached_info_2], status=200)

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        customer_cache_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await customer_cache_repository.get_cache(filter_)

        customer_cache_repository._nats_client.request.assert_awaited_once_with(
            "customer.cache.get", to_json_bytes(request), timeout=120
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_rpc_request_failing_test(self, customer_cache_repository, make_rpc_request):
        filter_ = {"mettel.velocloud.net": []}
        request = make_rpc_request(request_id=uuid_, filter=filter_)

        customer_cache_repository._nats_client.request.side_effect = Exception
        customer_cache_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await customer_cache_repository.get_cache(filter_)

        customer_cache_repository._nats_client.request.assert_awaited_once_with(
            "customer.cache.get", to_json_bytes(request), timeout=120
        )
        customer_cache_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_cache_with_rpc_request_returning_202_status_test(
        self, customer_cache_repository, make_rpc_request, make_rpc_response
    ):
        filter_ = {
            "mettel.velocloud.net": [],
            "metvco03.mettel.net": [],
        }

        request = make_rpc_request(request_id=uuid_, filter=filter_)
        response = make_rpc_response(
            request_id=uuid_,
            body="Cache is still being built for host(s): mettel_velocloud.net, metvco03.mettel.net",
            status=202,
        )

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        customer_cache_repository._nats_client.request = AsyncMock(return_value=response_msg)
        customer_cache_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await customer_cache_repository.get_cache(filter_)

        customer_cache_repository._nats_client.request.assert_awaited_once_with(
            "customer.cache.get", to_json_bytes(request), timeout=120
        )
        customer_cache_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_for_tnba_monitoring_test(self, customer_cache_repository):
        filter_ = testconfig.MONITOR_CONFIG["velo_filter"]

        customer_cache_repository.get_cache = AsyncMock()

        with uuid_mock:
            await customer_cache_repository.get_cache_for_tnba_monitoring()

        customer_cache_repository.get_cache.assert_awaited_once_with(filter_=filter_)
