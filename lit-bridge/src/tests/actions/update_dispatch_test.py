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
        lit_repo = Mock()

        update_dispatch = UpdateDispatch(logger, configs, event_bus, lit_repo)

        assert update_dispatch._config == configs
        assert update_dispatch._logger == logger
        assert update_dispatch._event_bus == event_bus
        assert update_dispatch._lit_repository == lit_repo

    @pytest.mark.asyncio
    async def update_dispatch_200_ok_test(self, instance_update_dispatch, msg, return_msg):
        dispatch_number = 123
        return_body = {'Dispatch': {'Dispatch_Number': dispatch_number}}
        return_status = 200
        instance_update_dispatch._lit_repository.update_dispatch = Mock(
            return_value={'body': return_body, 'status': return_status})

        dipatch_contents = {
            "RequestDispatch": {
                "dispatch_number": dispatch_number,
                "information_for_tech": "test",
                "special_materials_needed_for_dispatch": "test"
            }
        }
        request_id = '123'
        response_topic = 'some.response.topic'
        msg['request_id'] = request_id
        msg['response_topic'] = response_topic
        msg['body'] = dipatch_contents
        return_msg['request_id'] = request_id
        return_msg['status'] = return_status
        return_msg['body'] = return_body

        await instance_update_dispatch.update_dispatch(msg)

        instance_update_dispatch._lit_repository.update_dispatch.assert_called_once_with(dipatch_contents)
        instance_update_dispatch._event_bus.publish_message.assert_called_once_with(response_topic, return_msg)

    @pytest.mark.asyncio
    async def update_dispatch_no_dispatch_number_ko_test(self, instance_update_dispatch, msg, return_msg):
        msg['body'] = {
            "RequestDispatch": {
                "information_for_tech": "test",
                "special_materials_needed_for_dispatch": "test"
            }
        }
        return_msg['status'] = 400
        return_msg['body'] = 'Must include "Dispatch_Number" in request'
        await instance_update_dispatch.update_dispatch(msg)

        instance_update_dispatch._lit_repository.update_dispatch.assert_not_called()
        instance_update_dispatch._event_bus.publish_message.assert_called_once_with('some.response.topic', return_msg)

    @pytest.mark.asyncio
    async def update_dispatch_no_dispatch_ko_test(self, instance_update_dispatch, msg, return_msg):
        msg['body'] = {}
        return_msg['status'] = 400
        return_msg['body'] = 'Must include "RequestDispatch" in request'
        await instance_update_dispatch.update_dispatch(msg)

        instance_update_dispatch._lit_repository.update_dispatch.assert_not_called()
        instance_update_dispatch._event_bus.publish_message.assert_called_once_with('some.response.topic', return_msg)

    @pytest.mark.asyncio
    async def update_dispatch_no_body_ko_test(self, instance_update_dispatch, msg, return_msg):
        del msg['body']
        return_msg['status'] = 400
        return_msg['body'] = 'Must include "body" in request'

        await instance_update_dispatch.update_dispatch(msg)

        instance_update_dispatch._lit_repository.update_dispatch.assert_not_called()
        instance_update_dispatch._event_bus.publish_message.assert_called_once_with('some.response.topic', return_msg)
