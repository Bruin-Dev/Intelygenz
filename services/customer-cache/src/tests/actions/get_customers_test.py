from datetime import datetime, timedelta
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
    async def get_customers_200_test(self, instance_get_customer, instance_cache_edges, instance_request_message):
        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(instance_request_message)

        await instance_get_customer(request_msg)

        instance_get_customer._storage_repository.get_cache.assert_called_once()
        request_msg.respond.assert_awaited_once_with(to_json_bytes({"body": instance_cache_edges, "status": 200}))

    @pytest.mark.asyncio
    async def get_customers_200_enterprise_filter_test(
        self, instance_get_customer, instance_cache_edges, instance_request_message
    ):
        instance_request_message["body"]["filter"]["mettel.velocloud.com"] = [1]

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(instance_request_message)

        await instance_get_customer(request_msg)

        instance_get_customer._storage_repository.get_cache.assert_called_once()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": [instance_cache_edges[1]], "status": 200}),
        )

    @pytest.mark.asyncio
    async def get_customers_200_last_contact_filter_test(
        self, instance_get_customer_with_last_contact, instance_cache_edges_with_last_contact, instance_request_message
    ):
        instance_request_message["body"]["last_contact_filter"] = str(datetime.now() - timedelta(days=7))

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(instance_request_message)

        await instance_get_customer_with_last_contact(request_msg)

        instance_get_customer_with_last_contact._storage_repository.get_cache.assert_called_once()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": [instance_cache_edges_with_last_contact[0]], "status": 200}),
        )

    @pytest.mark.asyncio
    async def get_customers_200_last_contact_filter_no_results_test(
        self, instance_get_customer_with_last_contact, instance_request_message
    ):
        instance_request_message["body"]["last_contact_filter"] = str(datetime.now() + timedelta(days=7))

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(instance_request_message)

        await instance_get_customer_with_last_contact(request_msg)

        instance_get_customer_with_last_contact._storage_repository.get_cache.assert_called_once()

        filters_request = {
            "filter": instance_request_message["body"]["filter"],
            "last_contact_filter": instance_request_message["body"]["last_contact_filter"],
        }
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": f"No edges were found for the specified filters: {filters_request}", "status": 404}),
        )

    @pytest.mark.asyncio
    async def get_customers_202_test(
        self, instance_get_customer_with_empty_cache, instance_request_message, instance_response_message
    ):
        instance_request_message["body"]["last_contact_filter"] = None

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(instance_request_message)

        await instance_get_customer_with_empty_cache(request_msg)

        instance_get_customer_with_empty_cache._storage_repository.get_cache.assert_called_once()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(instance_response_message))

    @pytest.mark.asyncio
    async def get_customers_no_body_test(
        self, instance_get_customer_with_empty_cache, instance_request_message, instance_response_message
    ):
        del instance_request_message["body"]
        instance_response_message["body"] = 'You must specify {.."body":{"filter":[...]}} in the request'
        instance_response_message["status"] = 400

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(instance_request_message)

        await instance_get_customer_with_empty_cache(request_msg)

        instance_get_customer_with_empty_cache._storage_repository.get_cache.assert_not_called()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(instance_response_message))

    @pytest.mark.asyncio
    async def get_customers_no_filter_test(
        self, instance_get_customer_with_empty_cache, instance_request_message, instance_response_message
    ):
        instance_request_message["body"] = {}
        instance_response_message["body"] = 'You must specify "filter" in the body'
        instance_response_message["status"] = 400

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(instance_request_message)

        await instance_get_customer_with_empty_cache(request_msg)

        instance_get_customer_with_empty_cache._storage_repository.get_cache.assert_not_called()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(instance_response_message))

    @pytest.mark.asyncio
    async def get_customers_empty_filter_test(
        self, instance_get_customer_with_empty_cache, instance_request_message, instance_response_message
    ):
        instance_request_message["body"] = {}
        instance_request_message["body"]["filter"] = {}
        instance_request_message["status"] = 200
        instance_response_message["body"] = (
            "Cache is still being built for host(s): "
            "mettel.velocloud.net, metvco02.mettel.net, metvco03.mettel.net, metvco04.mettel.net"
        )

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(instance_request_message)

        await instance_get_customer_with_empty_cache(request_msg)

        instance_get_customer_with_empty_cache._storage_repository.get_cache.assert_called()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(instance_response_message))
