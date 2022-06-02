from unittest.mock import Mock

import pytest
from application.actions.get_customers import GetCustomers
from config import testconfig


class TestGetCustomers:
    def instance_test(self):
        config = testconfig
        logger = Mock()
        storage_repo = Mock()
        event_bus = Mock()

        get_customers = GetCustomers(config, logger, storage_repo, event_bus)

        assert get_customers._config == config
        assert get_customers._logger == logger
        assert get_customers._storage_repository == storage_repo
        assert get_customers._event_bus == event_bus

    @pytest.mark.asyncio
    async def get_customers_200_test(self, get_customer, cache_probes_now, default_call_with_params):
        get_customer._storage_repository.get_hawkeye_cache = Mock(return_value=cache_probes_now)
        await get_customer.get_customers(default_call_with_params)

        get_customer._storage_repository.get_hawkeye_cache.assert_called_once()
        get_customer._event_bus.publish_message.assert_awaited_once_with(
            default_call_with_params["response_topic"], dict(request_id="1234", body=cache_probes_now, status=200)
        )

    @pytest.mark.asyncio
    async def get_customers_not_found_probes_for_filter_test(
        self, get_customer, default_call_with_params, response_not_found_message, cache_probes_now
    ):
        get_customer._storage_repository.get_hawkeye_cache = Mock(return_value=cache_probes_now)
        default_call_with_params["body"]["last_contact_filter"] = "2200-11-16 10:55:45.711761"

        await get_customer.get_customers(default_call_with_params)

        get_customer._storage_repository.get_hawkeye_cache.assert_called_once()
        get_customer._event_bus.publish_message.assert_awaited_once_with(
            default_call_with_params["response_topic"], response_not_found_message
        )

    @pytest.mark.asyncio
    async def get_customers_no_body_test(self, get_customer, default_call_with_params, response_not_body_message):
        get_customer._storage_repository.get_hawkeye_cache = Mock(return_value=[])
        del default_call_with_params["body"]

        await get_customer.get_customers(default_call_with_params)

        get_customer._storage_repository.get_hawkeye_cache.assert_not_called()
        get_customer._event_bus.publish_message.assert_awaited_once_with(
            default_call_with_params["response_topic"], response_not_body_message
        )

    @pytest.mark.asyncio
    async def get_customers_no_body_test(self, get_customer, default_call_with_params, response_not_body_message):
        get_customer._storage_repository.get_hawkeye_cache = Mock(return_value=[])
        del default_call_with_params["body"]

        await get_customer.get_customers(default_call_with_params)

        get_customer._storage_repository.get_hawkeye_cache.assert_not_called()
        get_customer._event_bus.publish_message.assert_awaited_once_with(
            default_call_with_params["response_topic"], response_not_body_message
        )

    @pytest.mark.asyncio
    async def get_customers_no_cache_test(
        self, get_customer, default_call_with_params, response_building_cache_message
    ):
        get_customer._storage_repository.get_hawkeye_cache = Mock(return_value=[])

        await get_customer.get_customers(default_call_with_params)

        get_customer._storage_repository.get_hawkeye_cache.assert_called()
        get_customer._event_bus.publish_message.assert_awaited_once_with(
            default_call_with_params["response_topic"], response_building_cache_message
        )
