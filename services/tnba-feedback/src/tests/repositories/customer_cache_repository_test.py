from unittest.mock import AsyncMock, Mock, patch

import pytest
from application.repositories import customer_cache_repository as customer_cache_repository_module
from application.repositories import nats_error_response
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.utils_repository import to_json_bytes
from config import testconfig
from nats.aio.msg import Msg
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(customer_cache_repository_module, "uuid", return_value=uuid_)


class TestCustomerCacheRepository:
    def instance_test(self):
        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        customer_cache_repository = CustomerCacheRepository(nats_client, config, notifications_repository)

        assert customer_cache_repository._nats_client is nats_client
        assert customer_cache_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_cache_with_no_filter_specified_test(self):
        filter_ = {}

        request = {
            "request_id": uuid_,
            "body": {
                "filter": filter_,
            },
        }
        response = {
            "request_id": uuid_,
            "body": [
                {"host": "some-host", "enterprise_id": 1, "edge_id": 1},
                {"host": "some-host", "enterprise_id": 1, "edge_id": 2},
            ],
            "status": 200,
        }

        config = testconfig
        notifications_repository = Mock()

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        customer_cache_repository = CustomerCacheRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await customer_cache_repository.get_cache()

        nats_client.request.assert_awaited_once_with("customer.cache.get", to_json_bytes(request), timeout=120)
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_custom_filter_specified_test(self):
        filter_ = {"mettel.velocloud.net": []}

        request = {
            "request_id": uuid_,
            "body": {
                "filter": filter_,
            },
        }
        response = {
            "request_id": uuid_,
            "body": [
                {"host": "some-host", "enterprise_id": 1, "edge_id": 1},
                {"host": "some-host", "enterprise_id": 1, "edge_id": 2},
            ],
            "status": 200,
        }

        config = testconfig
        notifications_repository = Mock()

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        customer_cache_repository = CustomerCacheRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await customer_cache_repository.get_cache(filter_)

        nats_client.request.assert_awaited_once_with("customer.cache.get", to_json_bytes(request), timeout=120)
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_request_failing_test(self):
        filter_ = {"mettel.velocloud.net": []}

        request = {
            "request_id": uuid_,
            "body": {
                "filter": filter_,
            },
        }

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        customer_cache_repository = CustomerCacheRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await customer_cache_repository.get_cache(filter_)

        nats_client.request.assert_awaited_once_with("customer.cache.get", to_json_bytes(request), timeout=120)
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_cache_with_request_returning_202_status_test(self):
        filter_ = {
            "mettel.velocloud.net": [],
            "metvco03.mettel.net": [],
        }

        request = {
            "request_id": uuid_,
            "body": {
                "filter": filter_,
            },
        }

        response_msg = "Cache is still being built for host(s): mettel_velocloud.net, metvco03.mettel.net"
        response = {
            "request_id": uuid_,
            "body": response_msg,
            "status": 202,
        }

        config = testconfig

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        customer_cache_repository = CustomerCacheRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await customer_cache_repository.get_cache(filter_)

        nats_client.request.assert_awaited_once_with("customer.cache.get", to_json_bytes(request), timeout=120)
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_for_feedback_process_test(self):
        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        filter_ = config.TNBA_FEEDBACK_CONFIG["velo_filter"]

        customer_cache_repository = CustomerCacheRepository(nats_client, config, notifications_repository)
        customer_cache_repository.get_cache = AsyncMock()

        with uuid_mock:
            await customer_cache_repository.get_cache_for_feedback_process()

        customer_cache_repository.get_cache.assert_awaited_once_with(filter_=filter_)
