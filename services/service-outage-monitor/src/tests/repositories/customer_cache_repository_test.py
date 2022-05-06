from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import customer_cache_repository as customer_cache_repository_module
from application.repositories import nats_error_response
from application.repositories.customer_cache_repository import CustomerCacheRepository
from config import testconfig
from tests.fixtures._constants import CURRENT_DATETIME

uuid_ = uuid()
uuid_mock = patch.object(customer_cache_repository_module, 'uuid', return_value=uuid_)


class TestCustomerCacheRepository:
    def instance_test(self, customer_cache_repository, event_bus, logger, notifications_repository):
        assert customer_cache_repository._event_bus is event_bus
        assert customer_cache_repository._logger is logger
        assert customer_cache_repository._notifications_repository is notifications_repository
        assert customer_cache_repository._config is testconfig

    @pytest.mark.asyncio
    async def get_cache_with_no_filters_specified_test(self, customer_cache_repository):
        velo_filter = {}
        last_contact_filter = None
        request = {
            'request_id': uuid_,
            'body': {
                'filter': velo_filter,
                'last_contact_filter': last_contact_filter,
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
        customer_cache_repository._event_bus.rpc_request = CoroutineMock(return_value=response)

        with uuid_mock:
            result = await customer_cache_repository.get_cache()

        customer_cache_repository._event_bus.rpc_request.assert_awaited_once_with(
            "customer.cache.get",
            request,
            timeout=60
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_custom_filters_specified_test(self, customer_cache_repository):
        velo_filter = {'mettel.velocloud.net': []}
        last_contact_filter = '2020-01-16T14:59:56.245Z'
        request = {
            'request_id': uuid_,
            'body': {
                'filter': velo_filter,
                'last_contact_filter': last_contact_filter,
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
        customer_cache_repository._event_bus.rpc_request = CoroutineMock(return_value=response)

        with uuid_mock:
            result = await customer_cache_repository.get_cache(
                velo_filter=velo_filter, last_contact_filter=last_contact_filter
            )

        customer_cache_repository._event_bus.rpc_request.assert_awaited_once_with(
            "customer.cache.get",
            request,
            timeout=60
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_with_rpc_request_failing_test(self, customer_cache_repository):
        velo_filter = {'mettel.velocloud.net': []}
        request = {
            'request_id': uuid_,
            'body': {
                'filter': velo_filter,
                'last_contact_filter': None,
            },
        }
        customer_cache_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)
        customer_cache_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await customer_cache_repository.get_cache(velo_filter=velo_filter)

        customer_cache_repository._event_bus.rpc_request.assert_awaited_once_with(
            "customer.cache.get",
            request,
            timeout=60
        )
        customer_cache_repository._notifications_repository.send_slack_message.assert_awaited_once()
        customer_cache_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_cache_with_rpc_request_returning_202_status_test(self, customer_cache_repository):
        velo_filter = {
            'mettel.velocloud.net': [],
            'metvco03.mettel.net': [],
        }
        request = {
            'request_id': uuid_,
            'body': {
                'filter': velo_filter,
                'last_contact_filter': None,
            },
        }
        response_msg = 'Cache is still being built for host(s): mettel_velocloud.net, metvco03.mettel.net'
        response = {
            'request_id': uuid_,
            'body': response_msg,
            'status': 202,
        }
        customer_cache_repository._event_bus.rpc_request = CoroutineMock(return_value=response)
        customer_cache_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await customer_cache_repository.get_cache(velo_filter=velo_filter)

        customer_cache_repository._event_bus.rpc_request.assert_awaited_once_with(
            "customer.cache.get",
            request,
            timeout=60
        )
        customer_cache_repository._notifications_repository.send_slack_message.assert_awaited_once()
        customer_cache_repository._logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_cache_for_triage_monitoring_test(self, customer_cache_repository):
        velo_filter = customer_cache_repository._config.TRIAGE_CONFIG['velo_filter']
        customer_cache_repository.get_cache = CoroutineMock()

        with uuid_mock:
            await customer_cache_repository.get_cache_for_triage_monitoring()

        customer_cache_repository.get_cache.assert_awaited_once_with(velo_filter=velo_filter)

    @pytest.mark.asyncio
    async def get_cache_for_outage_monitoring_test(self, customer_cache_repository):
        last_contact_filter = str(CURRENT_DATETIME - timedelta(days=7))
        velo_filter = customer_cache_repository._config.MONITOR_CONFIG['velocloud_instances_filter']
        customer_cache_repository.get_cache = CoroutineMock()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=CURRENT_DATETIME)

        with patch.object(customer_cache_repository_module, 'datetime', new=datetime_mock):
            with uuid_mock:
                await customer_cache_repository.get_cache_for_outage_monitoring()

        customer_cache_repository.get_cache.assert_awaited_once_with(
            velo_filter=velo_filter, last_contact_filter=last_contact_filter
        )
