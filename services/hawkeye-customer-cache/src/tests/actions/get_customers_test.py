from unittest.mock import Mock

import pytest
from application.actions.get_customers import GetCustomers
from application.repositories.utils_repository import to_json_bytes
from config import testconfig
from nats.aio.msg import Msg


class TestGetCustomers:
    def instance_test(self):
        config = testconfig
        storage_repo = Mock()

        get_customers = GetCustomers(config, storage_repo)

        assert get_customers._config == config
        assert get_customers._storage_repository == storage_repo

    @pytest.mark.asyncio
    async def get_customers_200_test(self, get_customer, cache_probes_now, default_call_with_params):
        get_customer._storage_repository.get_hawkeye_cache = Mock(return_value=cache_probes_now)

        response_payload = {"body": cache_probes_now, "status": 200}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(default_call_with_params)

        await get_customer(request_msg)

        get_customer._storage_repository.get_hawkeye_cache.assert_called_once()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_payload))

    @pytest.mark.asyncio
    async def get_customers_not_found_probes_for_filter_test(
        self, get_customer, default_call_with_params, response_not_found_message, cache_probes_now
    ):
        get_customer._storage_repository.get_hawkeye_cache = Mock(return_value=cache_probes_now)
        default_call_with_params["body"]["last_contact_filter"] = "2200-11-16 10:55:45.711761"

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(default_call_with_params)

        await get_customer(request_msg)

        get_customer._storage_repository.get_hawkeye_cache.assert_called_once()

        response_not_found_message["body"] = response_not_found_message["body"].format(
            filters=default_call_with_params["body"]
        )
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_not_found_message))

    @pytest.mark.asyncio
    async def get_customers_no_body_test(self, get_customer, default_call_with_params, response_not_body_message):
        get_customer._storage_repository.get_hawkeye_cache = Mock(return_value=[])
        del default_call_with_params["body"]

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(default_call_with_params)

        await get_customer(request_msg)

        get_customer._storage_repository.get_hawkeye_cache.assert_not_called()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_not_body_message))

    @pytest.mark.asyncio
    async def get_customers_no_body_test(self, get_customer, default_call_with_params, response_not_body_message):
        get_customer._storage_repository.get_hawkeye_cache = Mock(return_value=[])
        del default_call_with_params["body"]

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(default_call_with_params)

        await get_customer(request_msg)

        get_customer._storage_repository.get_hawkeye_cache.assert_not_called()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_not_body_message))

    @pytest.mark.asyncio
    async def get_customers_no_cache_test(
        self, get_customer, default_call_with_params, response_building_cache_message
    ):
        get_customer._storage_repository.get_hawkeye_cache = Mock(return_value=[])

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(default_call_with_params)

        await get_customer(request_msg)

        get_customer._storage_repository.get_hawkeye_cache.assert_called()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_building_cache_message))
