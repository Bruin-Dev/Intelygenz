from unittest.mock import Mock

import pytest
from application.actions.get_dispatch import GetDispatch

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
    async def get_dispatch_ok_test(self, instance_get_dispatch, msg, return_msg):
        return_body = {'Dispatch': {'Dispatch_Number': 123}}
        return_status = 200
        instance_get_dispatch._lit_repository.get_dispatch = Mock(
            return_value={'body': return_body, 'status': return_status})

        dispatch_number = '123'
        msg['body'] = {'dispatch_number': dispatch_number}
        return_msg['status'] = return_status
        return_msg['body'] = return_body

        await instance_get_dispatch.get_dispatch(msg)
        instance_get_dispatch._lit_repository.get_dispatch.assert_called_once_with(dispatch_number)
        instance_get_dispatch._event_bus.publish_message.assert_called_once_with('some.response.topic', return_msg)

    @pytest.mark.asyncio
    async def get_dispatch_no_body_ko_test(self, instance_get_dispatch, msg, return_msg):
        del msg['body']
        return_msg['status'] = 400
        return_msg['body'] = 'Must include "body" in request'
        await instance_get_dispatch.get_dispatch(msg)
        instance_get_dispatch._lit_repository.get_dispatch.assert_not_called()
        instance_get_dispatch._event_bus.publish_message.assert_called_once_with('some.response.topic', return_msg)

    @pytest.mark.asyncio
    async def get_dispatch_no_dispatch_number_ok_test(self, instance_get_dispatch, msg, return_msg):
        return_body = {'DispatchList': [{'Dispatch_Number': 123}]}
        return_status = 200

        instance_get_dispatch._lit_repository.get_all_dispatches = Mock(
            return_value={'body': return_body, 'status': return_status})

        msg['body'] = {}
        return_msg['status'] = return_status
        return_msg['body'] = return_body

        await instance_get_dispatch.get_dispatch(msg)

        instance_get_dispatch._lit_repository.get_dispatch.assert_not_called()
        instance_get_dispatch._lit_repository.get_all_dispatches.assert_called_once()

    @pytest.mark.asyncio
    async def get_dispatch_with_igz_dispatches_only_true_test(self, instance_get_dispatch, msg, return_msg):
        return_body = {'DispatchList': [{'Dispatch_Number': 123}], 'igz_dispatches_only': True}
        return_status = 200

        instance_get_dispatch._lit_repository.get_all_dispatches = Mock(
            return_value={'body': return_body, 'status': return_status})

        msg['body'] = return_body
        return_msg['status'] = return_status
        return_msg['body'] = return_body

        await instance_get_dispatch.get_dispatch(msg)

        instance_get_dispatch._lit_repository.get_dispatch.assert_not_called()
        instance_get_dispatch._lit_repository.get_all_dispatches.assert_called_once()

    @pytest.mark.asyncio
    async def get_dispatch_with_igz_dispatches_only_false_test(self, instance_get_dispatch, msg, return_msg):
        return_body = {'DispatchList': [{'Dispatch_Number': 123}], 'igz_dispatches_only': False}
        return_status = 400

        instance_get_dispatch._lit_repository.get_all_dispatches = Mock(
            return_value={'body': return_body, 'status': return_status})

        msg['body'] = return_body
        return_msg['status'] = return_status
        return_msg['body'] = return_body

        await instance_get_dispatch.get_dispatch(msg)

        instance_get_dispatch._lit_repository.get_dispatch.assert_not_called()
        instance_get_dispatch._lit_repository.get_all_dispatches.assert_called_once()
