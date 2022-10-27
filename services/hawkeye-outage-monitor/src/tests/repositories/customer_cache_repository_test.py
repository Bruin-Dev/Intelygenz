import json
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from nats.aio.msg import Msg
from shortuuid import uuid

from application import nats_error_response
from application.repositories import customer_cache_repository as customer_cache_repository_module
from application.repositories.customer_cache_repository import CustomerCacheRepository

uuid_ = uuid()
uuid_mock = patch.object(customer_cache_repository_module, "uuid", return_value=uuid_)


@pytest.fixture(scope="function")
def customer_cache_repository_instance():
    return CustomerCacheRepository(
        nats_client=Mock(),
        notifications_repository=Mock(),
    )


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


class TestCustomerCacheRepository:
    def instance_test(self):
        nats_client = Mock()
        notifications_repository = Mock()

        customer_cache_repository = CustomerCacheRepository(nats_client, notifications_repository)

        assert customer_cache_repository._nats_client is nats_client
        assert customer_cache_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_cache_with_no_filters_specified_test(self, customer_cache_repository_instance):
        request = {
            "request_id": uuid_,
            "body": {},
        }
        response = {
            "request_id": uuid_,
            "body": [
                {
                    "serial_number": "B827EB76A8DE",
                    "last_contact": "2020-01-16T14:59:56.245Z",
                    "bruin_client_info": {
                        "client_id": 9994,
                        "client_name": "METTEL/NEW YORK",
                    },
                }
            ],
            "status": 200,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        customer_cache_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await customer_cache_repository_instance.get_cache()

        customer_cache_repository_instance._nats_client.request.assert_awaited_once_with(
            "hawkeye.customer.cache.get", to_json_bytes(request), timeout=120
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_custom_filters_specified_test(self, customer_cache_repository_instance):
        last_contact_filter = "2020-01-16T14:50:00.000Z"

        request = {
            "request_id": uuid_,
            "body": {
                "last_contact_filter": last_contact_filter,
            },
        }
        response = {
            "request_id": uuid_,
            "body": [
                {
                    "serial_number": "B827EB76A8DE",
                    "last_contact": "2020-01-16T14:59:56.245Z",
                    "bruin_client_info": {
                        "client_id": 9994,
                        "client_name": "METTEL/NEW YORK",
                    },
                }
            ],
            "status": 200,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        customer_cache_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await customer_cache_repository_instance.get_cache(last_contact_filter=last_contact_filter)

        customer_cache_repository_instance._nats_client.request.assert_awaited_once_with(
            "hawkeye.customer.cache.get", to_json_bytes(request), timeout=120
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_rpc_request_failing_test(self, customer_cache_repository_instance):
        request = {
            "request_id": uuid_,
            "body": {},
        }

        customer_cache_repository_instance._nats_client.request = AsyncMock(side_effect=Exception)

        customer_cache_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await customer_cache_repository_instance.get_cache()

        customer_cache_repository_instance._nats_client.request.assert_awaited_once_with(
            "hawkeye.customer.cache.get", to_json_bytes(request), timeout=120
        )
        customer_cache_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_cache_with_rpc_request_returning_202_status_test(self, customer_cache_repository_instance):
        request = {
            "request_id": uuid_,
            "body": {},
        }

        response_msg = "Cache is still being built"
        response = {
            "request_id": uuid_,
            "body": response_msg,
            "status": 202,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        customer_cache_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        customer_cache_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await customer_cache_repository_instance.get_cache()

        customer_cache_repository_instance._nats_client.request.assert_awaited_once_with(
            "hawkeye.customer.cache.get", to_json_bytes(request), timeout=120
        )
        customer_cache_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_rpc_request_returning_non_2xx_status_test(self, customer_cache_repository_instance):
        request = {
            "request_id": uuid_,
            "body": {},
        }

        response_msg = "No devices were found for the specified filters"
        response = {
            "request_id": uuid_,
            "body": response_msg,
            "status": 404,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        customer_cache_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        customer_cache_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await customer_cache_repository_instance.get_cache()

        customer_cache_repository_instance._nats_client.request.assert_awaited_once_with(
            "hawkeye.customer.cache.get", to_json_bytes(request), timeout=120
        )
        customer_cache_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_for_outage_monitoring_test(self, customer_cache_repository_instance):
        current_datetime = datetime.now()
        last_contact_filter = str(current_datetime - timedelta(days=7))

        customer_cache_repository_instance.get_cache = AsyncMock()

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(customer_cache_repository_module, "datetime", new=datetime_mock):
            with uuid_mock:
                await customer_cache_repository_instance.get_cache_for_outage_monitoring()

        customer_cache_repository_instance.get_cache.assert_awaited_once_with(last_contact_filter=last_contact_filter)
