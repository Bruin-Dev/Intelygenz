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
    async def upload_file_test_ok_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        return_body = 'Sucessfully uploaded'
        return_status = 200
        upload_file_return = {'body': return_body, 'status': return_status}

        lit_repo = Mock()
        lit_repo.upload_file = Mock(return_value=upload_file_return)

        dispatch_number = '123'
        payload = 'some payload'
        file_name = 'test.pdf'
        content_type = "application/octet-stream"
        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': {
                      'dispatch_number': dispatch_number,
                      'payload': payload,
                      'file_name': file_name}
        }
        expected_return = {
            'request_id': request_id,
            'body': return_body,
            'status': return_status

        }
        upload_file_action = UploadFile(logger, configs, event_bus, lit_repo)
        await upload_file_action.upload_file(msg)

        lit_repo.upload_file.assert_called_once_with(dispatch_number, payload, file_name, content_type)
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def upload_file_test_file_content_provided_ok_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        return_body = 'Sucessfully uploaded'
        return_status = 200
        upload_file_return = {'body': return_body, 'status': return_status}

        lit_repo = Mock()
        lit_repo.upload_file = Mock(return_value=upload_file_return)

        dispatch_number = '123'
        payload = 'some payload'
        file_name = 'test.pdf'
        content_type = "application/pdf"
        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': {
                      'dispatch_number': dispatch_number,
                      'payload': payload,
                      'file_name': file_name,
                      'file_content_type': content_type}
        }
        expected_return = {
            'request_id': request_id,
            'body': return_body,
            'status': return_status

        }
        upload_file_action = UploadFile(logger, configs, event_bus, lit_repo)
        await upload_file_action.upload_file(msg)

        lit_repo.upload_file.assert_called_once_with(dispatch_number, payload, file_name, content_type)
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def upload_file_test_missing_keys_ko_test(self):
        configs = config
        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        lit_repo = Mock()

        upload_file_required_keys = ["dispatch_number", "payload", "file_name"]

        dispatch_number = '123'
        payload = 'some payload'
        file_name = 'test.pdf'
        content_type = "application/octet-stream"

        request_id = '123'
        response_topic = 'some.response.topic'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': {
                      'dispatch_number': dispatch_number,
                      'file_name': file_name}
        }
        expected_return = {
            'request_id': request_id,
            'body': f'Must include the following keys in request: {upload_file_required_keys}',
            'status': 400

        }
        upload_file_action = UploadFile(logger, configs, event_bus, lit_repo)
        await upload_file_action.upload_file(msg)

        lit_repo.upload_file.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)

    @pytest.mark.asyncio
    async def upload_file_test_missing_body_ko_test(self):
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
        upload_file_action = UploadFile(logger, configs, event_bus, lit_repo)
        await upload_file_action.upload_file(msg)

        lit_repo.upload_file.assert_not_called()
        event_bus.publish_message.assert_called_once_with(response_topic, expected_return)
