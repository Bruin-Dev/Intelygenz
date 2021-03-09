from unittest.mock import Mock
from unittest.mock import patch

import pytest
from application.repositories.bruin_repository import BruinRepository
from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import bruin_repository as bruin_repository_module
from application import nats_error_response
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, 'uuid', return_value=uuid_)


class TestBruinRepository:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        assert bruin_repository._event_bus is event_bus
        assert bruin_repository._logger is logger
        assert bruin_repository._config is config
        assert bruin_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_client_info_test(self, bruin_repository, request_message_without_topic,
                                   response_building_cache_message):
        service_number = 'VC1234567'
        request_message_without_topic['request_id'] = uuid_
        request_message_without_topic['body'] = {'service_number': service_number}
        response_building_cache_message['request_id'] = uuid_
        response_building_cache_message['body'] = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }
        response_building_cache_message['status'] = 200

        bruin_repository._event_bus.rpc_request = CoroutineMock(return_value=response_building_cache_message)

        with uuid_mock:
            result = await bruin_repository.get_client_info(service_number)

        bruin_repository._event_bus.rpc_request. \
            assert_awaited_once_with("bruin.customer.get.info", request_message_without_topic, timeout=30)
        assert result == response_building_cache_message

    @pytest.mark.asyncio
    async def get_client_info_with_rpc_request_failing_test(self, bruin_repository,
                                                            request_message_without_topic):
        service_number = 'VC1234567'

        request_message_without_topic['request_id'] = uuid_
        request_message_without_topic['body'] = {'service_number': service_number}

        bruin_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        bruin_repository._notify_error = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_client_info(service_number)

        bruin_repository._notify_error.assert_awaited_once()
        bruin_repository._event_bus. \
            rpc_request.assert_awaited_once_with("bruin.customer.get.info", request_message_without_topic,
                                                 timeout=30)
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_client_info_with_rpc_request_returning_non_2xx_status_test(self, bruin_repository,
                                                                             request_message_without_topic,
                                                                             response_building_cache_message):
        service_number = 'VC1234567'
        request_message_without_topic['request_id'] = uuid_
        request_message_without_topic['body'] = {'service_number': service_number}
        response_building_cache_message['request_id'] = uuid_
        response_building_cache_message['body'] = 'Got internal error from Bruin'
        response_building_cache_message['status'] = 500
        bruin_repository._event_bus.rpc_request = CoroutineMock(return_value=response_building_cache_message)

        bruin_repository._notify_error = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_client_info(service_number)

        bruin_repository._event_bus. \
            rpc_request.assert_awaited_once_with("bruin.customer.get.info", request_message_without_topic,
                                                 timeout=30)
        bruin_repository._notify_error.assert_awaited_once()
        assert result == response_building_cache_message

    @pytest.mark.asyncio
    async def get_management_status_test(self, bruin_repository, request_message_without_topic,
                                         response_building_cache_message):
        service_number = 'VC1234567'
        client_id = 9994
        request_message_without_topic['request_id'] = uuid_
        request_message_without_topic['body'] = {
            'client_id': client_id,
            'service_number': service_number,
            'status': 'A',
        }
        response_building_cache_message['request_id'] = uuid_
        response_building_cache_message['body'] = 'Active – Gold Monitoring'
        response_building_cache_message['status'] = 200
        bruin_repository._event_bus.rpc_request = CoroutineMock(return_value=response_building_cache_message)

        with uuid_mock:
            result = await bruin_repository.get_management_status(client_id, service_number)

        bruin_repository._event_bus. \
            rpc_request.assert_awaited_once_with("bruin.inventory.management.status",
                                                 request_message_without_topic, timeout=30)
        assert result == response_building_cache_message

    @pytest.mark.asyncio
    async def get_management_status_with_rpc_request_failing_test(self, bruin_repository,
                                                                  request_message_without_topic):
        service_number = 'VC1234567'
        client_id = 9994
        request_message_without_topic['request_id'] = uuid_
        request_message_without_topic['body'] = {
            'client_id': client_id,
            'service_number': service_number,
            'status': 'A',
        }
        bruin_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        bruin_repository._notify_error = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_management_status(client_id, service_number)

        bruin_repository._event_bus. \
            rpc_request.assert_awaited_once_with("bruin.inventory.management.status",
                                                 request_message_without_topic, timeout=30)
        bruin_repository._notify_error.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def management_status_with_rpc_request_returning_non_2xx_status_test(self, bruin_repository,
                                                                               request_message_without_topic,
                                                                               response_building_cache_message):
        service_number = 'VC1234567'
        client_id = 9994
        request_message_without_topic['request_id'] = uuid_
        request_message_without_topic['body'] = {
            'client_id': client_id,
            'service_number': service_number,
            'status': 'A',
        }
        response_building_cache_message['request_id'] = uuid_
        response_building_cache_message['body'] = 'Got internal error from Bruin'
        response_building_cache_message['status'] = 500
        bruin_repository._event_bus.rpc_request = CoroutineMock(return_value=response_building_cache_message)
        bruin_repository._notify_error = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_management_status(client_id, service_number)

        bruin_repository._event_bus. \
            rpc_request.assert_awaited_once_with("bruin.inventory.management.status",
                                                 request_message_without_topic, timeout=30)
        bruin_repository._notify_error.assert_awaited_once()
        assert result == response_building_cache_message

    def is_management_status_active_test(self, bruin_repository):
        management_status = "Pending"
        result = bruin_repository.is_management_status_active(management_status)
        assert result is True

        management_status = "Active – Gold Monitoring"
        result = bruin_repository.is_management_status_active(management_status)
        assert result is True

        management_status = "Active – Platinum Monitoring"
        result = bruin_repository.is_management_status_active(management_status)
        assert result is True

        management_status = "Fake status"
        result = bruin_repository.is_management_status_active(management_status)
        assert result is False

    @pytest.mark.asyncio
    async def notify_error_test(self, bruin_repository):
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()
        error_message = 'Failed'

        with uuid_mock:
            await bruin_repository._notify_error(error_message)
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once_with(error_message)

    @pytest.mark.asyncio
    async def filter_probes_list_test(self, bruin_repository, probes_example, response_bruin_get_client_ok,
                                      response_bruin_management_status_ok, cache_probes):
        probe = probes_example[0]
        bruin_repository.get_client_info = CoroutineMock(return_value=response_bruin_get_client_ok)
        bruin_repository.get_management_status = CoroutineMock(return_value=response_bruin_management_status_ok)

        result = await bruin_repository.filter_probe(probe)
        assert result == cache_probes[0]

    @pytest.mark.asyncio
    async def filter_probes_list_400_client_info_test(self, bruin_repository, probes_example,
                                                      response_bruin_get_client_ok):
        probe = probes_example[0]
        response_bruin_get_client_ok['status'] = 400
        bruin_repository.get_client_info = CoroutineMock(return_value=response_bruin_get_client_ok)

        result = await bruin_repository.filter_probe(probe)
        assert result is None

    @pytest.mark.asyncio
    async def filter_probes_list_not_client_id_test(self, bruin_repository, probes_example,
                                                    response_bruin_get_client_ok):
        probe = probes_example[0]
        response_bruin_get_client_ok['body'] = {}
        bruin_repository.get_client_info = CoroutineMock(return_value=response_bruin_get_client_ok)

        result = await bruin_repository.filter_probe(probe)
        assert result is None

    @pytest.mark.asyncio
    async def filter_probes_list_400_get_management_status_test(self, bruin_repository, probes_example,
                                                                response_bruin_get_client_ok,
                                                                response_bruin_management_status_ok):
        probe = probes_example[0]
        bruin_repository.get_client_info = CoroutineMock(return_value=response_bruin_get_client_ok)
        response_bruin_management_status_ok['status'] = 400
        bruin_repository.get_management_status = CoroutineMock(return_value=response_bruin_management_status_ok)

        result = await bruin_repository.filter_probe(probe)
        assert result is None

    @pytest.mark.asyncio
    async def filter_probes_list_not_valid_get_management_status_test(self, bruin_repository, probes_example,
                                                                      response_bruin_get_client_ok,
                                                                      response_bruin_management_status_ok):
        probe = probes_example[0]
        bruin_repository.get_client_info = CoroutineMock(return_value=response_bruin_get_client_ok)
        response_bruin_management_status_ok['body'] = 'not valid status'
        bruin_repository.get_management_status = CoroutineMock(return_value=response_bruin_management_status_ok)

        result = await bruin_repository.filter_probe(probe)
        assert result is None

    @pytest.mark.asyncio
    async def filter_probes_exception_test(self, bruin_repository, probes_example):
        probe = probes_example[0]
        bruin_repository.get_client_info = CoroutineMock(return_value=Exception)

        result = await bruin_repository.filter_probe(probe)
        assert result is None
