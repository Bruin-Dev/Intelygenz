from unittest.mock import Mock

import pytest
from application.actions.update_dispatch import UpdateDispatch
from asynctest import CoroutineMock

from config import testconfig as config


class TestUpdateDispatch:

    def instance_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        cts_repo = Mock()

        update_dispatch = UpdateDispatch(logger, configs, event_bus, cts_repo)

        assert update_dispatch._config == configs
        assert update_dispatch._logger == logger
        assert update_dispatch._event_bus == event_bus
        assert update_dispatch._cts_repository == cts_repo

    @pytest.mark.asyncio
    async def update_dispatch_200_ok_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        dispatch_number = 123
        return_body = {'Dispatch': {'Dispatch_Number': dispatch_number}}
        return_status = 200
        update_dispatch_return = {'body': return_body, 'status': return_status}
        cts_repo = Mock()
        cts_repo.update_dispatch = Mock(return_value=update_dispatch_return)

        dipatch_contents = {
            "dispatch_id": dispatch_number,
            "payload": {
                "information_for_tech": "test",
                "special_materials_needed_for_dispatch": "test"
            }
        }
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
        update_dispatch_action = UpdateDispatch(logger, configs, event_bus, cts_repo)
        await update_dispatch_action.update_dispatch(msg)

        cts_repo.update_dispatch.assert_called_once_with(dispatch_number, dipatch_contents['payload'])
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def update_dispatch_no_dispatch_number_ko_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        cts_repo = Mock()

        dipatch_contents = {
            "payload": {
                "information_for_tech": "test",
                "special_materials_needed_for_dispatch": "test"
            }
        }
        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': dipatch_contents
        }
        expected_return = {
            'request_id': request_id,
            'body': 'Must include "dispatch_id" in request',
            'status': 400

        }
        update_dispatch_action = UpdateDispatch(logger, configs, event_bus, cts_repo)
        await update_dispatch_action.update_dispatch(msg)

        cts_repo.update_dispatch.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def update_dispatch_no_payload_ko_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        cts_repo = Mock()
        dispatch_number = 123

        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': {"dispatch_id": dispatch_number}
        }
        expected_return = {
            'request_id': request_id,
            'body': 'Must include "payload" in request',
            'status': 400

        }
        update_dispatch_action = UpdateDispatch(logger, configs, event_bus, cts_repo)
        await update_dispatch_action.update_dispatch(msg)

        cts_repo.update_dispatch.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def update_dispatch_no_body_ko_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        cts_repo = Mock()

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
        update_dispatch_action = UpdateDispatch(logger, configs, event_bus, cts_repo)
        await update_dispatch_action.update_dispatch(msg)

        cts_repo.update_dispatch.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)
