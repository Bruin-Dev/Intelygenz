import json
from unittest.mock import Mock

import pytest
from application.actions.save_outputs import SaveOutputs
from asynctest import CoroutineMock

from config import testconfig


class TestPostAutomationMetrics:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        kre_repository = Mock()

        save_outputs = SaveOutputs(logger, testconfig, event_bus, kre_repository)

        assert save_outputs._config == testconfig
        assert save_outputs._logger == logger
        assert save_outputs._event_bus == event_bus
        assert save_outputs._kre_repository == kre_repository

    @pytest.mark.parametrize(
        "body_in_topic", [
            ({}),
        ], ids=[
            'no_body',
        ]
    )
    @pytest.mark.asyncio
    async def save_outputs_error_400_test(self, body_in_topic):
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        msg_published_in_topic = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': body_in_topic
        }

        config = Mock()
        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        kre_repository = Mock()
        kre_repository.save_outputs = CoroutineMock()

        save_outputs = SaveOutputs(logger, config, event_bus, kre_repository)

        await save_outputs.save_outputs(msg_published_in_topic)

        kre_repository.save_outputs.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': 'You must specify body in the request',
                'status': 400,
            }
        )

    @pytest.mark.asyncio
    async def save_outputs_ok_test(self, valid_output_request):
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        msg_published_in_topic = {
            'request_id': request_id,
            'body': valid_output_request,
            'response_topic': response_topic,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        return_value = {
            "body": "No content",
            "status": 204
        }

        kre_repository = Mock()
        kre_repository.save_outputs = CoroutineMock(return_value=return_value)

        save_outputs = SaveOutputs(logger, testconfig, event_bus, kre_repository)

        await save_outputs.save_outputs(msg_published_in_topic)

        kre_repository.save_outputs.assert_awaited_once()
        event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': return_value['body'],
                'status': return_value['status']
            }
        )

        assert logger.info.call_count == 1
