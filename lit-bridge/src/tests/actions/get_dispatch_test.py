from unittest.mock import Mock

import pytest
from application.actions.get_dispatch import GetDispatch
from asynctest import CoroutineMock

from config import testconfig as config


class TestGetDispatch:

    def instance_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        lit_repo = Mock()

        get_dispatch = GetDispatch(logger, configs, event_bus, lit_repo)

        assert get_dispatch._config == configs
        assert get_dispatch._logger == logger
        assert get_dispatch._event_bus == event_bus
        assert get_dispatch._lit_repository == lit_repo

    @pytest.mark.asyncio
    async def get_dispatch_ok_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        return_body = {'Dispatch': {'Dispatch_Number': 123}}
        return_status = 200
        get_dispatch_return = {'body': return_body, 'status': return_status}
        lit_repo = Mock()
        lit_repo.get_dispatch = Mock(return_value=get_dispatch_return)

        request_id = '123'
        response_topic = 'some.response.topic'
        dispatch_number = '123'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': {'dispatch_number': dispatch_number}
        }
        expected_return = {
            'request_id': request_id,
            'body': return_body,
            'status': return_status

        }
        get_dispatch_action = GetDispatch(logger, configs, event_bus, lit_repo)
        await get_dispatch_action.get_dispatch(msg)
        lit_repo.get_dispatch.assert_called_once_with(dispatch_number)
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def get_dispatch_no_body_ko_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        lit_repo = Mock()

        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
        }
        expected_return = {
            'request_id': request_id,
            'body': 'Must include "body" in request',
            'status': 400

        }
        get_dispatch_action = GetDispatch(logger, configs, event_bus, lit_repo)
        await get_dispatch_action.get_dispatch(msg)
        lit_repo.get_dispatch.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def get_dispatch_no_dispatch_number_ko_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        lit_repo = Mock()

        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': {}
        }
        expected_return = {
            'request_id': request_id,
            'body': 'Must include "dispatch_number" in request',
            'status': 400

        }
        get_dispatch_action = GetDispatch(logger, configs, event_bus, lit_repo)
        await get_dispatch_action.get_dispatch(msg)
        lit_repo.get_dispatch.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)
