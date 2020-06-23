from unittest.mock import Mock

import pytest
from application.actions.create_dispatch import CreateDispatch
from asynctest import CoroutineMock

from config import testconfig as config


class TestCreateDispatch:

    def instance_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        cts_repo = Mock()

        create_dispatch = CreateDispatch(logger, configs, event_bus, cts_repo)

        assert create_dispatch._config == configs
        assert create_dispatch._logger == logger
        assert create_dispatch._event_bus == event_bus
        assert create_dispatch._cts_repository == cts_repo

    @pytest.mark.asyncio
    async def create_dispatch_200_ok_test(self, cts_repository, new_dispatch):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        return_body = {}
        return_status = 200
        create_dispatch_return = {'body': return_body, 'status': return_status}
        cts_repository.create_dispatch = Mock(return_value=create_dispatch_return)

        dipatch_contents = new_dispatch
        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': dipatch_contents
        }
        expected_return = {
            'request_id': request_id,
            'body': return_body,
            'status': return_status
        }
        create_dispatch_action = CreateDispatch(logger, configs, event_bus, cts_repository)
        await create_dispatch_action.create_dispatch(msg)

        cts_repository.create_dispatch.assert_called_once_with(dipatch_contents)
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def create_dispatch_400_ok_test(self, cts_repository, new_dispatch):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        return_body = {'status': 'Error'}
        return_status = 400
        create_dispatch_return = {'body': return_body, 'status': return_status}
        cts_repository.create_dispatch = Mock(return_value=create_dispatch_return)

        dipatch_contents = new_dispatch
        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
                'request_id': request_id,
                'response_topic': response_topic,
                'body': dipatch_contents
        }
        expected_return = {
                            'request_id': request_id,
                            'body': return_body,
                            'status': return_status

        }
        create_dispatch_action = CreateDispatch(logger, configs, event_bus, cts_repository)
        await create_dispatch_action.create_dispatch(msg)

        cts_repository.create_dispatch.assert_called_once_with(dipatch_contents)
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def create_dispatch_missing_keys_ko_test(self, cts_repository, dispatch_required_keys):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        dipatch_contents = {
            "date_of_dispatch": 'fake'
        }

        request_id = '123'
        response_topic = 'some.response.topic'
        return_body = {'status': 'Error'}
        return_status = 400
        create_dispatch_return = {'body': return_body, 'status': return_status}
        msg = {
                'request_id': request_id,
                'response_topic': response_topic,
                'body': dipatch_contents
        }

        expected_return = {
            'request_id': request_id,
            'body': f'Must include the following keys in request: {dispatch_required_keys}',
            'status': 400
        }
        create_dispatch_action = CreateDispatch(logger, configs, event_bus, cts_repository)
        cts_repository.create_dispatch = Mock(return_value=create_dispatch_return)
        await create_dispatch_action.create_dispatch(msg)

        cts_repository.create_dispatch.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def create_dispatch_missing_request_dispatch_ko_test(self, cts_repository, dispatch_required_keys):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        request_id = '123'
        response_topic = 'some.response.topic'

        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': {}
        }

        expected_return = {
            'request_id': request_id,
            'body': f"Must include the following keys in request: {dispatch_required_keys}",
            'status': 400
        }
        create_dispatch_action = CreateDispatch(logger, configs, event_bus, cts_repository)
        cts_repository.create_dispatch = Mock(return_value=expected_return)
        await create_dispatch_action.create_dispatch(msg)

        cts_repository.create_dispatch.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def create_dispatch_missing_body_ko_test(self, cts_repository):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

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
        create_dispatch_action = CreateDispatch(logger, configs, event_bus, cts_repository)
        cts_repository.create_dispatch = Mock(return_value=expected_return)
        await create_dispatch_action.create_dispatch(msg)

        cts_repository.create_dispatch.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)
