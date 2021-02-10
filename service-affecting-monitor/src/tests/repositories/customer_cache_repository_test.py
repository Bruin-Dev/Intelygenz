from unittest.mock import Mock
from unittest.mock import patch

import pytest
from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import customer_cache_repository as customer_cache_repository_module
from application.repositories import nats_error_response
from application.repositories.customer_cache_repository import CustomerCacheRepository
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(customer_cache_repository_module, 'uuid', return_value=uuid_)


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
    async def get_cache_with_no_filter_specified_test(self):
        filter_ = {}

        request = {
            'request_id': uuid_,
            'body': {
                'filter': filter_,
            },
        }
        response = {
            'request_id': uuid_,
            'body': [
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1},
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2},
            ],
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        customer_cache_repository = CustomerCacheRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await customer_cache_repository.get_cache()

        event_bus.rpc_request.assert_awaited_once_with("customer.cache.get", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_custom_filter_specified_test(self):
        filter_ = {'mettel.velocloud.net': []}

        request = {
            'request_id': uuid_,
            'body': {
                'filter': filter_,
            },
        }
        response = {
            'request_id': uuid_,
            'body': [
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1},
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2},
            ],
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        customer_cache_repository = CustomerCacheRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await customer_cache_repository.get_cache(filter_)

        event_bus.rpc_request.assert_awaited_once_with("customer.cache.get", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_rpc_request_failing_test(self):
        filter_ = {'mettel.velocloud.net': []}

        request = {
            'request_id': uuid_,
            'body': {
                'filter': filter_,
            },
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        customer_cache_repository = CustomerCacheRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await customer_cache_repository.get_cache(filter_)

        event_bus.rpc_request.assert_awaited_once_with("customer.cache.get", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_cache_with_rpc_request_returning_202_status_test(self):
        filter_ = {
            'mettel.velocloud.net': [],
            'metvco03.mettel.net': [],
        }

        request = {
            'request_id': uuid_,
            'body': {
                'filter': filter_,
            },
        }

        response_msg = 'Cache is still being built for host(s): mettel_velocloud.net, metvco03.mettel.net'
        response = {
            'request_id': uuid_,
            'body': response_msg,
            'status': 202,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        customer_cache_repository = CustomerCacheRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await customer_cache_repository.get_cache(filter_)

        event_bus.rpc_request.assert_awaited_once_with("customer.cache.get", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_affecting_monitoring_test(self):
        response = {
            'request_id': uuid_,
            'body': [
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1},
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2},
            ],
            'status': 200,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        customer_cache_repository = CustomerCacheRepository(event_bus, logger, config, notifications_repository)
        customer_cache_repository.get_cache = CoroutineMock(return_value=response)

        with uuid_mock:
            result = await customer_cache_repository.get_cache_for_affecting_monitoring()

        assert result == response
