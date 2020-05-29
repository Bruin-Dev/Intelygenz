import copy
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch
import pytest

from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import lit_repository as lit_repository_module
from application.repositories import nats_error_response
from application.repositories.lit_repository import LitRepository
from config import testconfig


uuid_ = uuid()
uuid_mock = patch.object(lit_repository_module, 'uuid', return_value=uuid_)


class TestLitRepository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        lit_repository = LitRepository(logger, config, event_bus, notifications_repository)

        assert lit_repository._event_bus is event_bus
        assert lit_repository._logger is logger
        assert lit_repository._config is config
        assert lit_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_all_dispatches_test(self, lit_repository, dispatch, dispatch_confirmed):
        request = {
            'request_id': uuid_,
            'body': {},
        }
        response = {
            'request_id': uuid_,
            'body': {
                "Status": "Success",
                "Message": "Total Number of Dispatches: 2",
                "DispatchList": [
                    dispatch,
                    dispatch_confirmed
                ]
            },
            'status': 200,
        }
        lit_repository._event_bus.rpc_request = CoroutineMock(return_value=response)
        with uuid_mock:
            result = await lit_repository.get_all_dispatches()
        lit_repository._event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def get_all_dispatches_with_rpc_request_failing_test(self, lit_repository):

        request = {
            'request_id': uuid_,
            'body': {},
        }

        lit_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)
        lit_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await lit_repository.get_all_dispatches()

        lit_repository._event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", request, timeout=30)
        lit_repository._notifications_repository.send_slack_message.assert_awaited_once()
        lit_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_all_dispatches_with_rpc_request_returning_non_2xx_status_test(self, lit_repository):
        request = {
            'request_id': uuid_,
            'body': {},
        }
        response = {
            'request_id': uuid_,
            'body': 'Got internal error from LIT',
            'status': 500,
        }

        lit_repository._event_bus.rpc_request = CoroutineMock(return_value=response)
        lit_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await lit_repository.get_all_dispatches()

        lit_repository._event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", request, timeout=30)
        lit_repository._notifications_repository.send_slack_message.assert_awaited_once()
        lit_repository._logger.error.assert_called_once()
        assert result == response

    def get_sms_to_test(self, dispatch):
        updated_dispatch = copy.deepcopy(dispatch)
        updated_dispatch['Job_Site_Contact_Name_and_Phone_Number'] = "Test Client on site +1 (987) 654 327"
        expected_phone = "+1987654327"
        assert LitRepository.get_sms_to(updated_dispatch) == expected_phone

    def get_sms_to_with_error_test(self, dispatch):
        updated_dispatch = copy.deepcopy(dispatch)
        updated_dispatch['Job_Site_Contact_Name_and_Phone_Number'] = None
        assert LitRepository.get_sms_to(updated_dispatch) is None

    def get_sms_to_with_error_number_test(self, dispatch):
        updated_dispatch = copy.deepcopy(dispatch)
        updated_dispatch['Job_Site_Contact_Name_and_Phone_Number'] = "no valid Number"
        assert LitRepository.get_sms_to(updated_dispatch) is None
