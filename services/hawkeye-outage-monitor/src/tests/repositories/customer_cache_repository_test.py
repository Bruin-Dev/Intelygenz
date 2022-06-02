from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from application import nats_error_response
from application.repositories import customer_cache_repository as customer_cache_repository_module
from application.repositories.customer_cache_repository import CustomerCacheRepository
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(customer_cache_repository_module, "uuid", return_value=uuid_)


class TestCustomerCacheRepository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        customer_cache_repository = CustomerCacheRepository(event_bus, logger, config, notifications_repository)

        assert customer_cache_repository._event_bus is event_bus
        assert customer_cache_repository._logger is logger
        assert customer_cache_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_cache_with_no_filters_specified_test(self):
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

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        customer_cache_repository = CustomerCacheRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await customer_cache_repository.get_cache()

        event_bus.rpc_request.assert_awaited_once_with("hawkeye.customer.cache.get", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_custom_filters_specified_test(self):
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

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        customer_cache_repository = CustomerCacheRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await customer_cache_repository.get_cache(last_contact_filter=last_contact_filter)

        event_bus.rpc_request.assert_awaited_once_with("hawkeye.customer.cache.get", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_rpc_request_failing_test(self):
        request = {
            "request_id": uuid_,
            "body": {},
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        customer_cache_repository = CustomerCacheRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await customer_cache_repository.get_cache()

        event_bus.rpc_request.assert_awaited_once_with("hawkeye.customer.cache.get", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_cache_with_rpc_request_returning_202_status_test(self):
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

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        customer_cache_repository = CustomerCacheRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await customer_cache_repository.get_cache()

        event_bus.rpc_request.assert_awaited_once_with("hawkeye.customer.cache.get", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_rpc_request_returning_non_2xx_status_test(self):
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

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        customer_cache_repository = CustomerCacheRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await customer_cache_repository.get_cache()

        event_bus.rpc_request.assert_awaited_once_with("hawkeye.customer.cache.get", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_for_outage_monitoring_test(self):
        current_datetime = datetime.now()
        last_contact_filter = str(current_datetime - timedelta(days=7))

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        customer_cache_repository = CustomerCacheRepository(event_bus, logger, config, notifications_repository)
        customer_cache_repository.get_cache = CoroutineMock()

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(customer_cache_repository_module, "datetime", new=datetime_mock):
            with uuid_mock:
                await customer_cache_repository.get_cache_for_outage_monitoring()

        customer_cache_repository.get_cache.assert_awaited_once_with(last_contact_filter=last_contact_filter)
