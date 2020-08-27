from unittest.mock import Mock

import pytest
from application.actions.get_customers import GetCustomers
from datetime import datetime, timedelta

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
    async def get_customers_200_test(self, instance_get_customer, instance_cache_edges, instance_request_message):
        await instance_get_customer.get_customers(instance_request_message)

        instance_get_customer._storage_repository.get_cache.assert_called_once()
        instance_get_customer._event_bus.publish_message.assert_awaited_once_with(
            instance_request_message['response_topic'],
            dict(request_id='1111',
                 body=instance_cache_edges,
                 status=200))

    @pytest.mark.asyncio
    async def get_customers_200_enterprise_filter_test(self, instance_get_customer, instance_cache_edges,
                                                       instance_request_message):
        instance_request_message["body"]["filter"]["mettel.velocloud.com"] = [1]

        await instance_get_customer.get_customers(instance_request_message)

        instance_get_customer._storage_repository.get_cache.assert_called_once()
        instance_get_customer._event_bus.publish_message.assert_awaited_once_with(
            instance_request_message['response_topic'],
            dict(request_id='1111',
                 body=[instance_cache_edges[1]],
                 status=200))

    @pytest.mark.asyncio
    async def get_customers_200_last_contact_filter_test(self, instance_get_customer_with_last_contact,
                                                         instance_cache_edges_with_last_contact,
                                                         instance_request_message):
        instance_request_message["body"]["last_contact_filter"] = str(datetime.now() - timedelta(days=7))

        await instance_get_customer_with_last_contact.get_customers(instance_request_message)

        instance_get_customer_with_last_contact._storage_repository.get_cache.assert_called_once()
        instance_get_customer_with_last_contact._event_bus.publish_message.assert_awaited_once_with(
            instance_request_message['response_topic'],
            dict(request_id='1111', body=[instance_cache_edges_with_last_contact[0]], status=200))

    @pytest.mark.asyncio
    async def get_customers_200_last_contact_filter_no_results_test(self, instance_get_customer_with_last_contact,
                                                                    instance_cache_edges_with_last_contact,
                                                                    instance_request_message):
        instance_request_message["body"]["last_contact_filter"] = str(datetime.now() + timedelta(days=7))

        await instance_get_customer_with_last_contact.get_customers(instance_request_message)

        instance_get_customer_with_last_contact._storage_repository.get_cache.assert_called_once()
        instance_get_customer_with_last_contact._event_bus.publish_message.assert_awaited_once_with(
            instance_request_message['response_topic'],
            dict(request_id='1111', body='No edges were found for the specified filters', status=404))

    @pytest.mark.asyncio
    async def get_customers_202_test(self, instance_get_customer_with_empty_cache, instance_request_message,
                                     instance_response_message):
        instance_request_message["body"]["last_contact_filter"] = None

        await instance_get_customer_with_empty_cache.get_customers(instance_request_message)

        instance_get_customer_with_empty_cache._storage_repository.get_cache.assert_called_once()
        instance_get_customer_with_empty_cache._event_bus.publish_message.assert_awaited_once_with(
            instance_request_message['response_topic'],
            instance_response_message)

    @pytest.mark.asyncio
    async def get_customers_no_body_test(self, instance_get_customer_with_empty_cache, instance_request_message,
                                         instance_response_message):
        del instance_request_message["body"]
        instance_response_message["body"] = 'You must specify {.."body":{"filter":[...]}} in the request'
        instance_response_message["status"] = 400

        await instance_get_customer_with_empty_cache.get_customers(instance_request_message)

        instance_get_customer_with_empty_cache._storage_repository.get_cache.assert_not_called()
        instance_get_customer_with_empty_cache._event_bus.publish_message.assert_awaited_once_with(
            instance_request_message['response_topic'],
            instance_response_message)

    @pytest.mark.asyncio
    async def get_customers_no_filter_test(self, instance_get_customer_with_empty_cache, instance_request_message,
                                           instance_response_message):
        instance_request_message["body"] = {}
        instance_response_message["body"] = 'You must specify "filter" in the body'
        instance_response_message["status"] = 400
        await instance_get_customer_with_empty_cache.get_customers(instance_request_message)

        instance_get_customer_with_empty_cache._storage_repository.get_cache.assert_not_called()
        instance_get_customer_with_empty_cache._event_bus.publish_message.assert_awaited_once_with(
            instance_request_message['response_topic'],
            instance_response_message)

    @pytest.mark.asyncio
    async def get_customers_empty_filter_test(self, instance_get_customer_with_empty_cache, instance_request_message,
                                              instance_response_message):
        instance_request_message["body"] = {}
        instance_request_message["body"]["filter"] = {}
        instance_request_message["status"] = 200
        instance_response_message[
            "body"] = "Cache is still being built for host(s): " \
                      "mettel.velocloud.net, metvco02.mettel.net, metvco03.mettel.net, metvco04.mettel.net"
        await instance_get_customer_with_empty_cache.get_customers(instance_request_message)

        instance_get_customer_with_empty_cache._storage_repository.get_cache.assert_called()
        instance_get_customer_with_empty_cache._event_bus.publish_message.assert_awaited_once_with(
            instance_request_message['response_topic'],
            instance_response_message)
