from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from application.repositories.bruin_repository import BruinRepository
from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import bruin_repository as bruin_repository_module
from application.repositories import nats_error_response
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, 'uuid', return_value=uuid_)


class TestBruinRepository:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig

        bruin_repository = BruinRepository(config, logger, event_bus)

        assert bruin_repository._event_bus is event_bus
        assert bruin_repository._logger is logger
        assert bruin_repository._config is config

    @pytest.mark.asyncio
    async def get_client_info_test(self, instance_bruin_repository, instance_request_message_without_topic,
                                   instance_response_message):
        service_number = 'VC1234567'
        instance_request_message_without_topic['request_id'] = uuid_
        instance_request_message_without_topic['body'] = {'service_number': service_number}
        instance_response_message['request_id'] = uuid_
        instance_response_message['body'] = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }
        instance_response_message['status'] = 200

        instance_bruin_repository._event_bus.rpc_request = CoroutineMock(return_value=instance_response_message)

        with uuid_mock:
            result = await instance_bruin_repository.get_client_info(service_number)

        instance_bruin_repository._event_bus.rpc_request. \
            assert_awaited_once_with("bruin.customer.get.info", instance_request_message_without_topic, timeout=30)
        assert result == instance_response_message

    @pytest.mark.asyncio
    async def get_client_info_with_rpc_request_failing_test(self, instance_bruin_repository,
                                                            instance_request_message_without_topic):
        service_number = 'VC1234567'

        instance_request_message_without_topic['request_id'] = uuid_
        instance_request_message_without_topic['body'] = {'service_number': service_number}

        instance_bruin_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        instance_bruin_repository._notify_error = CoroutineMock()

        with uuid_mock:
            result = await instance_bruin_repository.get_client_info(service_number)

        instance_bruin_repository._notify_error.assert_awaited_once()
        instance_bruin_repository._event_bus. \
            rpc_request.assert_awaited_once_with("bruin.customer.get.info", instance_request_message_without_topic,
                                                 timeout=30)
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_client_info_with_rpc_request_returning_non_2xx_status_test(self, instance_bruin_repository,
                                                                             instance_request_message_without_topic,
                                                                             instance_response_message):
        service_number = 'VC1234567'
        instance_request_message_without_topic['request_id'] = uuid_
        instance_request_message_without_topic['body'] = {'service_number': service_number}
        instance_response_message['request_id'] = uuid_
        instance_response_message['body'] = 'Got internal error from Bruin'
        instance_response_message['status'] = 500
        instance_bruin_repository._event_bus.rpc_request = CoroutineMock(return_value=instance_response_message)

        instance_bruin_repository._notify_error = CoroutineMock()

        with uuid_mock:
            result = await instance_bruin_repository.get_client_info(service_number)

        instance_bruin_repository._event_bus. \
            rpc_request.assert_awaited_once_with("bruin.customer.get.info", instance_request_message_without_topic,
                                                 timeout=30)
        instance_bruin_repository._notify_error.assert_awaited_once()
        assert result == instance_response_message

    @pytest.mark.asyncio
    async def get_management_status_test(self, instance_bruin_repository, instance_request_message_without_topic,
                                         instance_response_message):
        service_number = 'VC1234567'
        client_id = 9994
        instance_request_message_without_topic['request_id'] = uuid_
        instance_request_message_without_topic['body'] = {
            'client_id': client_id,
            'service_number': service_number,
            'status': 'A',
        }
        instance_response_message['request_id'] = uuid_
        instance_response_message['body'] = 'Active – Gold Monitoring'
        instance_response_message['status'] = 200
        instance_bruin_repository._event_bus.rpc_request = CoroutineMock(return_value=instance_response_message)

        with uuid_mock:
            result = await instance_bruin_repository.get_management_status(client_id, service_number)

        instance_bruin_repository._event_bus. \
            rpc_request.assert_awaited_once_with("bruin.inventory.management.status",
                                                 instance_request_message_without_topic, timeout=30)
        assert result == instance_response_message

    @pytest.mark.asyncio
    async def get_management_status_with_rpc_request_failing_test(self, instance_bruin_repository,
                                                                  instance_request_message_without_topic):
        service_number = 'VC1234567'
        client_id = 9994
        instance_request_message_without_topic['request_id'] = uuid_
        instance_request_message_without_topic['body'] = {
            'client_id': client_id,
            'service_number': service_number,
            'status': 'A',
        }

        instance_bruin_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        instance_bruin_repository._notify_error = CoroutineMock()

        with uuid_mock:
            result = await instance_bruin_repository.get_management_status(client_id, service_number)

        instance_bruin_repository._event_bus. \
            rpc_request.assert_awaited_once_with("bruin.inventory.management.status",
                                                 instance_request_message_without_topic, timeout=30)
        instance_bruin_repository._notify_error.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def management_status_with_rpc_request_returning_non_2xx_status_test(self, instance_bruin_repository,
                                                                               instance_request_message_without_topic,
                                                                               instance_response_message):
        service_number = 'VC1234567'
        client_id = 9994
        instance_request_message_without_topic['request_id'] = uuid_
        instance_request_message_without_topic['body'] = {
            'client_id': client_id,
            'service_number': service_number,
            'status': 'A',
        }
        instance_response_message['request_id'] = uuid_
        instance_response_message['body'] = 'Got internal error from Bruin'
        instance_response_message['status'] = 500
        instance_bruin_repository._event_bus.rpc_request = CoroutineMock(return_value=instance_response_message)
        instance_bruin_repository._notify_error = CoroutineMock()

        with uuid_mock:
            result = await instance_bruin_repository.get_management_status(client_id, service_number)

        instance_bruin_repository._event_bus. \
            rpc_request.assert_awaited_once_with("bruin.inventory.management.status",
                                                 instance_request_message_without_topic, timeout=30)
        instance_bruin_repository._notify_error.assert_awaited_once()
        assert result == instance_response_message

    def is_management_status_active_test(self, instance_bruin_repository):
        management_status = "Pending"
        result = instance_bruin_repository.is_management_status_active(management_status)
        assert result is True

        management_status = "Active – Gold Monitoring"
        result = instance_bruin_repository.is_management_status_active(management_status)
        assert result is True

        management_status = "Active – Platinum Monitoring"
        result = instance_bruin_repository.is_management_status_active(management_status)
        assert result is True

        management_status = "Fake status"
        result = instance_bruin_repository.is_management_status_active(management_status)
        assert result is False

    @pytest.mark.asyncio
    async def notify_error_test(self, instance_bruin_repository):
        instance_bruin_repository._event_bus.rpc_request = CoroutineMock()
        error_message = 'Failed'
        error_dict = {'request_id': uuid_,
                      'message': error_message}
        with uuid_mock:
            await instance_bruin_repository._notify_error(error_message)
        instance_bruin_repository._event_bus.rpc_request.assert_awaited_once_with("notification.slack.request",
                                                                                  error_dict,
                                                                                  timeout=10)

    @pytest.mark.asyncio
    async def filter_edge_list_ok_test(self, instance_refresh_cache,
                                       instance_cache_edges, instance_edges_refresh_cache):
        last_contact = str(datetime.now())
        bruin_client_info = {'client_id': 'some client info'}
        instance_edges_refresh_cache[0]['last_contact'] = last_contact
        instance_edges_refresh_cache[0]['serial_number'] = 'VC01'
        instance_cache_edges[0]['edge']['host'] = 'metvco02.mettel.net'
        instance_cache_edges[0]['last_contact'] = last_contact
        instance_edges_refresh_cache[0]['bruin_client_info'] = bruin_client_info

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': bruin_client_info, 'status': 200})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 200})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=True)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._bruin_repository.filter_edge_list(
            instance_edges_refresh_cache[0])

        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_called()

        assert cache_return == instance_cache_edges[0]

    @pytest.mark.asyncio
    async def filter_edge_list_exception_test(self, instance_refresh_cache, instance_edges_refresh_cache):
        last_contact = str(datetime.now())
        instance_edges_refresh_cache[0]['last_contact'] = last_contact
        instance_edges_refresh_cache[0]['edgeLastContact'] = last_contact
        instance_edges_refresh_cache[0]['edgeSerialNumber'] = 'VC01'

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': None, 'status': 200})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 200})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=True)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._bruin_repository.filter_edge_list(
            instance_edges_refresh_cache[0])
        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_not_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_not_called()

        instance_refresh_cache._logger.error.assert_called_once()

        assert cache_return is None

    @pytest.mark.asyncio
    async def filter_edge_list_no_client_info_test(self, instance_refresh_cache, instance_edges_refresh_cache):
        last_contact = str(datetime.now())

        instance_edges_refresh_cache[0]['last_contact'] = last_contact
        instance_edges_refresh_cache[0]['edgeLastContact'] = last_contact
        instance_edges_refresh_cache[0]['edgeSerialNumber'] = 'VC01'

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': {}, 'status': 200})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 200})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=True)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._bruin_repository.filter_edge_list(
            instance_edges_refresh_cache[0])
        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_not_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_not_called()

        assert cache_return is None

    @pytest.mark.asyncio
    async def filter_edge_list_client_info_status_non_2XX_test(self, instance_refresh_cache,
                                                               instance_edges_refresh_cache):
        last_contact = str(datetime.now())

        instance_edges_refresh_cache[0]['last_contact'] = last_contact
        instance_edges_refresh_cache[0]['edgeLastContact'] = last_contact
        instance_edges_refresh_cache[0]['edgeSerialNumber'] = 'VC01'

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': {'client_id': 'some client info'}, 'status': 400})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 200})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=True)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._bruin_repository.filter_edge_list(
            instance_edges_refresh_cache[0])
        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_not_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_not_called()

        assert cache_return is None

    @pytest.mark.asyncio
    async def filter_edge_list_no_management_status_test(self, instance_refresh_cache, instance_edges_refresh_cache):
        last_contact = str(datetime.now())

        instance_edges_refresh_cache[0]['last_contact'] = last_contact
        instance_edges_refresh_cache[0]['edgeLastContact'] = last_contact
        instance_edges_refresh_cache[0]['edgeSerialNumber'] = 'VC01'

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': {'client_id': 'some client info'}, 'status': 200})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 400})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=True)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._bruin_repository.filter_edge_list(
            instance_edges_refresh_cache[0])
        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_not_called()

        assert cache_return is None

    @pytest.mark.asyncio
    async def filter_edge_list_unactive_management_status_test(self, instance_refresh_cache,
                                                               instance_edges_refresh_cache):
        last_contact = str(datetime.now())

        instance_edges_refresh_cache[0]['last_contact'] = last_contact
        instance_edges_refresh_cache[0]['edgeLastContact'] = last_contact
        instance_edges_refresh_cache[0]['edgeSerialNumber'] = 'VC01'

        instance_refresh_cache._bruin_repository.get_client_info = CoroutineMock(
            return_value={'body': {'client_id': 'some client info'}, 'status': 200})
        instance_refresh_cache._bruin_repository.get_management_status = CoroutineMock(
            return_value={'body': 'some management status', 'status': 200})
        instance_refresh_cache._bruin_repository.is_management_status_active = Mock(return_value=False)

        instance_refresh_cache._storage_repository.set_cache = Mock()

        cache_return = await instance_refresh_cache._bruin_repository.filter_edge_list(
            instance_edges_refresh_cache[0])
        instance_refresh_cache._bruin_repository.get_client_info.assert_awaited()
        instance_refresh_cache._bruin_repository.get_management_status.assert_awaited()
        instance_refresh_cache._bruin_repository.is_management_status_active.assert_called()

        assert cache_return is None
