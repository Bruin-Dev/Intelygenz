from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from nats.aio.msg import Msg
from shortuuid import uuid

from application import nats_error_response
from application.repositories import customer_cache_repository as customer_cache_repository_module
from application.repositories.utils_repository import to_json_bytes

uuid_ = uuid()
uuid_mock = patch.object(customer_cache_repository_module, "uuid", return_value=uuid_)


class TestCustomerCacheRepository:
    def instance_test(self, customer_cache_repository, nats_client, notifications_repository):
        assert customer_cache_repository._nats_client is nats_client
        assert customer_cache_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_cache_with_no_filters_specified_test(self, customer_cache_repository, customer_cache):
        request = {
            "request_id": uuid_,
            "body": {},
        }
        response = {
            "request_id": uuid_,
            "body": customer_cache,
            "status": 200,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        customer_cache_repository._nats_client.request.return_value = response_msg

        with uuid_mock:
            result = await customer_cache_repository.get_cache()

        customer_cache_repository._nats_client.request.assert_awaited_once_with(
            "hawkeye.customer.cache.get", to_json_bytes(request), timeout=60
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_custom_filters_specified_test(self, customer_cache_repository, customer_cache):
        last_contact_filter = "2020-01-16T14:50:00.000Z"

        request = {
            "request_id": uuid_,
            "body": {
                "last_contact_filter": last_contact_filter,
            },
        }
        response = {
            "request_id": uuid_,
            "body": customer_cache,
            "status": 200,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        customer_cache_repository._nats_client.request.return_value = response_msg

        with uuid_mock:
            result = await customer_cache_repository.get_cache(last_contact_filter=last_contact_filter)

        customer_cache_repository._nats_client.request.assert_awaited_once_with(
            "hawkeye.customer.cache.get", to_json_bytes(request), timeout=60
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_request_failing_test(self, customer_cache_repository):
        request = {
            "request_id": uuid_,
            "body": {},
        }

        customer_cache_repository._nats_client.request.side_effect = Exception
        customer_cache_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await customer_cache_repository.get_cache()

        customer_cache_repository._nats_client.request.assert_any_await(
            "hawkeye.customer.cache.get", to_json_bytes(request), timeout=60
        )
        customer_cache_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_cache_with_request_returning_202_status_test(
        self, customer_cache_repository, get_customer_cache_202_response
    ):
        request = {
            "request_id": uuid_,
            "body": {},
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(get_customer_cache_202_response)
        customer_cache_repository._nats_client.request.return_value = response_msg
        customer_cache_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await customer_cache_repository.get_cache()

        customer_cache_repository._nats_client.request.assert_any_await(
            "hawkeye.customer.cache.get", to_json_bytes(request), timeout=60
        )
        customer_cache_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == get_customer_cache_202_response

    @pytest.mark.asyncio
    async def get_cache_with_request_returning_non_2xx_status_test(
        self, customer_cache_repository, get_customer_cache_404_response
    ):
        request = {
            "request_id": uuid_,
            "body": {},
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(get_customer_cache_404_response)
        customer_cache_repository._nats_client.request.return_value = response_msg
        customer_cache_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await customer_cache_repository.get_cache()

        customer_cache_repository._nats_client.request.assert_any_await(
            "hawkeye.customer.cache.get", to_json_bytes(request), timeout=60
        )
        customer_cache_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == get_customer_cache_404_response

    @pytest.mark.asyncio
    async def get_cache_for_affecting_monitoring_test(self, customer_cache_repository):
        current_datetime = datetime.now()
        last_contact_filter = str(current_datetime - timedelta(days=7))

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(customer_cache_repository_module, "datetime", new=datetime_mock):
            with uuid_mock:
                await customer_cache_repository.get_cache_for_affecting_monitoring()

        customer_cache_repository.get_cache.assert_awaited_once_with(last_contact_filter=last_contact_filter)
