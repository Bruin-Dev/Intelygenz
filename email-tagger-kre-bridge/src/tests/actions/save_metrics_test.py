import json
from unittest.mock import Mock

import pytest
from application.actions.save_metrics import SaveMetrics
from asynctest import CoroutineMock

from config import testconfig


class TestPostAutomationMetrics:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        kre_repository = Mock()

        save_metrics = SaveMetrics(logger, testconfig, event_bus, kre_repository)

        assert save_metrics._config == testconfig
        assert save_metrics._logger == logger
        assert save_metrics._event_bus == event_bus
        assert save_metrics._kre_repository == kre_repository

    @pytest.mark.parametrize(
        "body_in_topic", [
            None,
            ({'some-key': 'some-data'}),
            ({'email_id': 12345}),
        ], ids=[
            'without_body',
            'without_params',
            'without_email_data',
        ]
    )
    @pytest.mark.asyncio
    async def save_metrics_error_400_test(self, body_in_topic):
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
        kre_repository.save_metrics = CoroutineMock()

        save_metrics = SaveMetrics(logger, config, event_bus, kre_repository)

        await save_metrics.save_metrics(msg_published_in_topic)

        kre_repository.save_metrics.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': 'You must specify {.."body": {"original_email": {...}, "ticket": {...}}} in the request',
                'status': 400,
            }
        )

    @pytest.mark.asyncio
    async def save_metrics_ok_test(self):
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        params = {
            "original_email": {
                "email": {
                    "email_id": "2726244",
                    "date": "2016-08-29T09:12:33:001Z",
                    "subject": "email_subject",
                    "body": "email_body",
                    "parent_id": "2726243",
                },
                "tag_ids": ["4", "3", "2"]
            },
            "ticket": {
                "ticket_id": "123456",
                "call_type": "chg",
                "category": "aac",
                "creation_date": "2016-08-29T09:12:33:001Z"
            }
        }

        msg_published_in_topic = {
            'request_id': request_id,
            'body': params,
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
        kre_repository.save_metrics = CoroutineMock(return_value=return_value)

        save_metrics = SaveMetrics(logger, testconfig, event_bus, kre_repository)

        await save_metrics.save_metrics(msg_published_in_topic)

        kre_repository.save_metrics.assert_awaited_once()
        event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': return_value['body'],
                'status': return_value['status']
            }
        )

        assert logger.info.call_count == 1
