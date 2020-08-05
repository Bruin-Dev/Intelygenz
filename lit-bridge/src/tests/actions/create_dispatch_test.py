from unittest.mock import Mock

import pytest
from application.actions.create_dispatch import CreateDispatch

from config import testconfig as config


class TestCreateDispatch:

    def instance_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        lit_repo = Mock()

        create_dispatch = CreateDispatch(logger, configs, event_bus, lit_repo)

        assert create_dispatch._config == configs
        assert create_dispatch._logger == logger
        assert create_dispatch._event_bus == event_bus
        assert create_dispatch._lit_repository == lit_repo

    @pytest.mark.asyncio
    async def create_dispatch_200_ok_2_test(self, instance_dispatch, dispatch, msg, return_msg):
        return_body = {'Dispatch': {'Dispatch_Number': 123}}
        return_status = 200
        create_dispatch_return = {'body': return_body, 'status': return_status}

        instance_dispatch._lit_repository.create_dispatch = Mock(return_value=create_dispatch_return)

        msg['body'] = dispatch
        await instance_dispatch.create_dispatch(msg)

        instance_dispatch._lit_repository.create_dispatch.assert_called_once_with(dispatch)
        return_msg['status'] = return_status
        return_msg['body'] = return_body
        instance_dispatch._event_bus.publish_message.assert_called_once_with('some.response.topic', return_msg)

    @pytest.mark.asyncio
    async def create_dispatch_400_ok_test(self, instance_dispatch, dispatch, msg, return_msg):
        return_body = {'status': 'Error'}
        return_status = 400
        create_dispatch_return = {'body': return_body, 'status': return_status}

        instance_dispatch._lit_repository.create_dispatch = Mock(return_value=create_dispatch_return)

        msg['body'] = dispatch
        await instance_dispatch.create_dispatch(msg)

        instance_dispatch._lit_repository.create_dispatch.assert_called_once_with(dispatch)
        return_msg['status'] = return_status
        return_msg['body'] = return_body
        instance_dispatch._event_bus.publish_message.assert_called_once_with('some.response.topic', return_msg)

    @pytest.mark.asyncio
    async def create_dispatch_missing_keys_ko_test(self, instance_dispatch, required_dispatch_keys, msg, return_msg):
        msg['body'] = {
            "RequestDispatch": {
                "Special_Materials_Needed_for_Dispatch": "test"
            }
        }

        await instance_dispatch.create_dispatch(msg=msg)

        return_msg['status'] = 400
        return_msg['body'] = f'Must include the following keys in request: {required_dispatch_keys}'

        instance_dispatch._lit_repository.create_dispatch.assert_not_called()
        instance_dispatch._event_bus.publish_message.assert_called_once_with('some.response.topic', return_msg)

    @pytest.mark.asyncio
    async def create_dispatch_missing_request_dispatch_ko_test(self, instance_dispatch, msg, return_msg):
        msg['body'] = {}

        await instance_dispatch.create_dispatch(msg)

        return_msg['status'] = 400
        return_msg['body'] = 'Must include "RequestDispatch" in request'

        instance_dispatch._lit_repository.create_dispatch.assert_not_called()
        instance_dispatch._event_bus.publish_message.assert_called_once_with('some.response.topic', return_msg)

    @pytest.mark.asyncio
    async def create_dispatch_missing_body_ko_test(self, instance_dispatch, msg, return_msg):
        del msg['body']

        await instance_dispatch.create_dispatch(msg)

        return_msg['status'] = 400
        return_msg['body'] = 'Must include "body" in request'

        instance_dispatch._lit_repository.create_dispatch.assert_not_called()
        instance_dispatch._event_bus.publish_message.assert_called_once_with('some.response.topic', return_msg)
