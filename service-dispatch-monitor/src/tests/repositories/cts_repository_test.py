import copy
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch
import pytest

from asynctest import CoroutineMock
from pytz import timezone
from shortuuid import uuid

from application.repositories import cts_repository as cts_repository_module
from application.repositories import nats_error_response
from application.repositories.cts_repository import CtsRepository
from config import testconfig


uuid_ = uuid()
uuid_mock = patch.object(cts_repository_module, 'uuid', return_value=uuid_)


class TestCtsRepository:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        redis_client = Mock()

        cts_repository = CtsRepository(logger, config, event_bus, notifications_repository, redis_client)

        assert cts_repository._event_bus is event_bus
        assert cts_repository._logger is logger
        assert cts_repository._config is config
        assert cts_repository._notifications_repository is notifications_repository
        assert cts_repository._redis_client is redis_client

    @pytest.mark.asyncio
    async def get_all_dispatches_test(self, cts_repository, cts_dispatch, cts_dispatch_confirmed):
        request = {
            'request_id': uuid_,
            'body': {},
        }
        response = {
            'request_id': uuid_,
            'body': {
                "done": True,
                "totalSize": 2,
                "records": [
                    cts_dispatch,
                    cts_dispatch_confirmed
                ]
            },
            'status': 200,
        }
        cts_repository._event_bus.rpc_request = CoroutineMock(return_value=response)
        with uuid_mock:
            result = await cts_repository.get_all_dispatches()
        cts_repository._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def get_all_dispatches_with_rpc_request_failing_test(self, cts_repository):

        request = {
            'request_id': uuid_,
            'body': {},
        }

        cts_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)
        cts_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await cts_repository.get_all_dispatches()

        cts_repository._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", request, timeout=30)
        cts_repository._notifications_repository.send_slack_message.assert_awaited_once()
        cts_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_all_dispatches_error_non_2xx_status_test(self, cts_repository, cts_dispatch, cts_dispatch_confirmed):
        request = {
            'request_id': uuid_,
            'body': {},
        }
        response = {
            'request_id': uuid_,
            'body': 'Error',
            'status': 500,
        }
        cts_repository._event_bus.rpc_request = CoroutineMock(return_value=response)
        cts_repository._notifications_repository.send_slack_message = CoroutineMock()
        with uuid_mock:
            result = await cts_repository.get_all_dispatches()
        cts_repository._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", request, timeout=30)
        cts_repository._notifications_repository.send_slack_message.assert_awaited_once()
        cts_repository._logger.error.assert_called_once()
        assert result == response

    def get_sms_to_test(self, cts_dispatch_confirmed):
        updated_dispatch = copy.deepcopy(cts_dispatch_confirmed)
        expected_phone = '+12027723610'
        assert CtsRepository.get_sms_to(updated_dispatch) == expected_phone

    def get_sms_to_error_no_contact_test(self, cts_dispatch_confirmed_no_contact):
        updated_dispatch = copy.deepcopy(cts_dispatch_confirmed_no_contact)
        expected_phone = None
        assert CtsRepository.get_sms_to(updated_dispatch) == expected_phone

    def get_sms_to_error_number_test(self, cts_dispatch_confirmed_error_number):
        updated_dispatch = copy.deepcopy(cts_dispatch_confirmed_error_number)
        expected_phone = None
        assert CtsRepository.get_sms_to(updated_dispatch) == expected_phone

    def is_valid_ticket_id_test(self, lit_dispatch_monitor):
        valid_ticket_id = '4663397'
        invalid_ticket_id_1 = '4663397|IW24654081'
        invalid_ticket_id_2 = '712637/IW76236'
        invalid_ticket_id_3 = '123-3123'
        invalid_ticket_id_4 = '4485610(Order)/4520284(Port)'
        assert CtsRepository.is_valid_ticket_id(ticket_id=valid_ticket_id) is True
        assert CtsRepository.is_valid_ticket_id(ticket_id=invalid_ticket_id_1) is False
        assert CtsRepository.is_valid_ticket_id(ticket_id=invalid_ticket_id_2) is False
        assert CtsRepository.is_valid_ticket_id(ticket_id=invalid_ticket_id_3) is False
        assert CtsRepository.is_valid_ticket_id(ticket_id=invalid_ticket_id_4) is False
