from unittest.mock import Mock

import pytest
from application.actions.upload_file import UploadFile
from asynctest import CoroutineMock

from config import testconfig as config


class TestUpdateDispatch:

    def instance_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        lit_repo = Mock()

        upload_file = UploadFile(logger, configs, event_bus, lit_repo)

        assert upload_file._config == configs
        assert upload_file._logger == logger
        assert upload_file._event_bus == event_bus
        assert upload_file._lit_repository == lit_repo

    @pytest.mark.asyncio
    async def upload_file_test_ok_test(self, instance_upload_dispatch, msg, return_msg):
        return_body = 'Sucessfully uploaded'
        return_status = 200

        instance_upload_dispatch._lit_repository.upload_file = Mock(
            return_value={'body': return_body, 'status': return_status})

        dispatch_number = '123'
        payload = 'some payload'
        file_name = 'test.pdf'

        msg['body'] = {
            'dispatch_number': '123',
            'payload': payload,
            'file_name': file_name}
        return_msg['status'] = return_status
        return_msg['body'] = return_body

        await instance_upload_dispatch.upload_file(msg)

        instance_upload_dispatch._lit_repository.upload_file.assert_called_once_with(dispatch_number, payload,
                                                                                     file_name,
                                                                                     "application/octet-stream")
        instance_upload_dispatch._event_bus.publish_message.assert_called_once_with('some.response.topic', return_msg)

    @pytest.mark.asyncio
    async def upload_file_test_file_content_provided_ok_test(self, instance_upload_dispatch, msg, return_msg):
        return_body = 'Sucessfully uploaded'
        return_status = 200

        instance_upload_dispatch._lit_repository.upload_file = Mock(
            return_value={'body': return_body, 'status': return_status})

        dispatch_number = '123'
        payload = 'some payload'
        file_name = 'test.pdf'
        content_type = "application/pdf"
        msg['body'] = {
            'dispatch_number': dispatch_number,
            'payload': payload,
            'file_name': file_name,
            'file_content_type': content_type}
        return_msg['status'] = return_status
        return_msg['body'] = return_body

        await instance_upload_dispatch.upload_file(msg)

        instance_upload_dispatch._lit_repository.upload_file.assert_called_once_with(dispatch_number, payload,
                                                                                     file_name, content_type)
        instance_upload_dispatch._event_bus.publish_message.assert_called_once_with('some.response.topic', return_msg)

    @pytest.mark.asyncio
    async def upload_file_test_missing_keys_ko_test(self, instance_upload_dispatch, msg, return_msg):
        dispatch_number = '123'
        file_name = 'test.pdf'

        msg['body'] = {
            'dispatch_number': dispatch_number,
            'file_name': file_name}
        return_msg['status'] = 400
        return_msg['body'] = f"Must include the following keys in request: ['dispatch_number', 'payload', 'file_name']"

        await instance_upload_dispatch.upload_file(msg)

        instance_upload_dispatch._lit_repository.upload_file.assert_not_called()
        instance_upload_dispatch._event_bus.publish_message.assert_called_once_with('some.response.topic', return_msg)

    @pytest.mark.asyncio
    async def upload_file_test_missing_body_ko_test(self, instance_upload_dispatch, msg, return_msg):
        del msg['body']
        return_msg['status'] = 400
        return_msg['body'] = 'Must include "body" in request'

        await instance_upload_dispatch.upload_file(msg)

        instance_upload_dispatch._lit_repository.upload_file.assert_not_called()
        instance_upload_dispatch._event_bus.publish_message.assert_called_once_with('some.response.topic', return_msg)
