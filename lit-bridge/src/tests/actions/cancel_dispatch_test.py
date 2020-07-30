from unittest.mock import Mock

import pytest
from application.actions.cancel_dispatch import CancelDispatch
from asynctest import CoroutineMock

from config import testconfig as config


class TestCancelDispatch:

    def instance_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        lit_repo = Mock()

        create_dispatch = CancelDispatch(logger, configs, event_bus, lit_repo)

        assert create_dispatch._config == configs
        assert create_dispatch._logger == logger
        assert create_dispatch._event_bus == event_bus
        assert create_dispatch._lit_repository == lit_repo

    @pytest.mark.asyncio
    async def cancel_dispatch_200_ok_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        dispatch_number = "DIS12345"
        return_body = {
            "CancelDispatchServiceResponse": {
                "Status": "Success",
                "APIRequestID": "a130v000001tYVWAA2",
                "Message": f"Cancellation Request Submitted for {dispatch_number}"
            }
        }
        return_status = 200
        cancel_dispatch_return = {'body': return_body, 'status': return_status}
        cancel_request_body = {
            "CancelDispatchRequest": {
                "Dispatch_Number": dispatch_number,
                "Cancellation_Reason": "Test API cancel",
                "Cancellation_Requested_By": "API Tester"
            }
        }
        lit_repo = Mock()
        lit_repo.cancel_dispatch = Mock(return_value=cancel_dispatch_return)

        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': cancel_request_body
        }
        expected_return = {
            'request_id': request_id,
            'body': return_body,
            'status': return_status
        }
        cancel_dispatch_action = CancelDispatch(logger, configs, event_bus, lit_repo)
        await cancel_dispatch_action.cancel_dispatch(msg)

        lit_repo.cancel_dispatch.assert_called_once_with(msg['body'])
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def cancel_dispatch_no_body_response_ko_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        dispatch_number = "DIS12345"
        return_body = {
            "CancelDispatchServiceResponse": {
                "Status": "Success",
                "APIRequestID": "a130v000001tYVWAA2",
                "Message": f"Cancellation Request Submitted for {dispatch_number}"
            }
        }
        return_status = 400
        cancel_dispatch_return = {'body': return_body, 'status': return_status}
        cancel_request_body = {
            "CancelDispatchRequest": {
                "Missing_KEY": dispatch_number,
                "Cancellation_Reason": "Test API cancel",
                "Cancellation_Requested_By": "API Tester"
            }
        }
        lit_repo = Mock()
        lit_repo.cancel_dispatch = Mock(return_value=cancel_dispatch_return)

        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'NO_BODY': cancel_request_body
        }
        expected_return = {
            'request_id': request_id,
            'body': f'Must include "body" in request',
            'status': 400
        }
        cancel_dispatch_action = CancelDispatch(logger, configs, event_bus, lit_repo)
        await cancel_dispatch_action.cancel_dispatch(msg)

        lit_repo.cancel_dispatch.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def cancel_dispatch_400_ok_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        dispatch_number = "DIS12345"
        return_body = {
            "CancelDispatchServiceResponse": {
                "Status": "Success",
                "APIRequestID": "a130v000001tYVWAA2",
                "Message": f"Cancellation Request Submitted for {dispatch_number}"
            }
        }
        return_status = 400
        cancel_dispatch_return = {'body': return_body, 'status': return_status}
        cancel_request_body = {
            "CancelDispatchRequest": {
                "Dispatch_Number": dispatch_number,
                "Cancellation_Reason": "Test API cancel",
                "Cancellation_Requested_By": "API Tester"
            }
        }
        lit_repo = Mock()
        lit_repo.cancel_dispatch = Mock(return_value=cancel_dispatch_return)

        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': cancel_request_body
        }
        expected_return = {
            'request_id': request_id,
            'body': return_body,
            'status': return_status
        }
        cancel_dispatch_action = CancelDispatch(logger, configs, event_bus, lit_repo)
        await cancel_dispatch_action.cancel_dispatch(msg)

        lit_repo.cancel_dispatch.assert_called_once_with(msg['body'])
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def cancel_dispatch_missing_response_cancel_dispatch_request_ko_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        dispatch_number = "DIS12345"
        return_body = {
            "CancelDispatchServiceResponse": {
                "Status": "Success",
                "APIRequestID": "a130v000001tYVWAA2",
                "Message": f"Cancellation Request Submitted for {dispatch_number}"
            }
        }
        return_status = 400
        cancel_dispatch_return = {'body': return_body, 'status': return_status}
        cancel_request_body = {
            "NO_CancelDispatchRequest": {
                "Dispatch_Number": dispatch_number,
                "Cancellation_Reason": "Test API cancel",
                "Cancellation_Requested_By": "API Tester"
            }
        }
        lit_repo = Mock()
        lit_repo.cancel_dispatch = Mock(return_value=cancel_dispatch_return)

        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': cancel_request_body
        }
        expected_return = {
            'request_id': request_id,
            'body': f'Must include "CancelDispatchRequest" in request',
            'status': 400
        }
        cancel_dispatch_action = CancelDispatch(logger, configs, event_bus, lit_repo)
        await cancel_dispatch_action.cancel_dispatch(msg)

        lit_repo.cancel_dispatch.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def cancel_dispatch_missing_keys_ko_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        dispatch_number = "DIS12345"
        return_body = {
            "CancelDispatchServiceResponse": {
                "Status": "Success",
                "APIRequestID": "a130v000001tYVWAA2",
                "Message": f"Cancellation Request Submitted for {dispatch_number}"
            }
        }
        return_status = 400
        cancel_dispatch_return = {'body': return_body, 'status': return_status}
        cancel_request_body = {
            "CancelDispatchRequest": {
                "Missing_KEY": dispatch_number,
                "Cancellation_Reason": "Test API cancel",
                "Cancellation_Requested_By": "API Tester"
            }
        }
        dispatch_required_keys = ["Dispatch_Number", "Cancellation_Reason", "Cancellation_Requested_By"]
        lit_repo = Mock()
        lit_repo.cancel_dispatch = Mock(return_value=cancel_dispatch_return)

        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': cancel_request_body
        }
        expected_return = {
            'request_id': request_id,
            'body': f'Must include the following keys in request: {dispatch_required_keys}',
            'status': 400
        }
        cancel_dispatch_action = CancelDispatch(logger, configs, event_bus, lit_repo)
        await cancel_dispatch_action.cancel_dispatch(msg)

        lit_repo.cancel_dispatch.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)
