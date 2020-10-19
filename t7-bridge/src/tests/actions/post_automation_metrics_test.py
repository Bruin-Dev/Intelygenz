import json
from unittest.mock import Mock

import pytest
from application.actions.post_automation_metrics import PostAutomationMetrics
from asynctest import CoroutineMock


class TestPostAutomationMetrics:

    def instance_test(self):
        config = Mock()
        logger = Mock()
        event_bus = Mock()
        t7_repository = Mock()
        t7_kre_repository = Mock()

        automation_metrics = PostAutomationMetrics(logger, config, event_bus, t7_repository, t7_kre_repository)

        assert automation_metrics._config == config
        assert automation_metrics._logger == logger
        assert automation_metrics._event_bus == event_bus
        assert automation_metrics._t7_repository == t7_repository
        assert automation_metrics._t7_kre_repository == t7_kre_repository

    @pytest.mark.asyncio
    async def post_automation_metrics_with_no_body_in_request_message_test(self):
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        msg_published_in_topic = {
            'request_id': request_id,
            'response_topic': response_topic,
        }

        config = Mock()
        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        t7_repository = Mock()
        t7_repository.post_automation_metrics = Mock()

        t7_kre_repository = Mock()
        t7_kre_repository.post_automation_metrics = Mock()

        automation_metrics = PostAutomationMetrics(logger, config, event_bus, t7_repository, t7_kre_repository)

        await automation_metrics.post_automation_metrics(msg_published_in_topic)

        t7_repository.post_automation_metrics.assert_not_called()
        event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': 'You must specify {.."body": {"ticket_id": "...", "ticket_rows";[...]}..} in the request',
                'status': 400,
            }
        )

    @pytest.mark.asyncio
    async def post_automation_metrics_with_no_ticket_id_in_request_message_test(self):
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        params = {"ticket_rows": []}

        msg_published_in_topic = {
            'request_id': request_id,
            'body': params,
            'response_topic': response_topic,
        }

        config = Mock()
        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        t7_repository = Mock()
        t7_repository.post_automation_metrics = Mock()

        t7_kre_repository = Mock()
        t7_kre_repository.post_automation_metrics = Mock()

        automation_metrics = PostAutomationMetrics(logger, config, event_bus, t7_repository, t7_kre_repository)

        await automation_metrics.post_automation_metrics(msg_published_in_topic)

        t7_repository.post_automation_metrics.assert_not_called()
        event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': 'You must specify {"ticket_id": "...", "ticket_rows";[...]} in the body',
                'status': 400,
            }
        )

    @pytest.mark.asyncio
    async def post_automation_metrics_with_no_ticket_rows_in_request_message_test(self):
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        params = {"ticket_id": 123}

        msg_published_in_topic = {
            'request_id': request_id,
            'body': params,
            'response_topic': response_topic,
        }

        config = Mock()
        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        t7_repository = Mock()
        t7_repository.post_automation_metrics = Mock()

        t7_kre_repository = Mock()
        t7_kre_repository.post_automation_metrics = Mock()

        automation_metrics = PostAutomationMetrics(logger, config, event_bus, t7_repository, t7_kre_repository)

        await automation_metrics.post_automation_metrics(msg_published_in_topic)

        t7_repository.post_automation_metrics.assert_not_called()
        event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': 'You must specify {"ticket_id": "...", "ticket_rows";[...]} in the body',
                'status': 400,
            }
        )

    @pytest.mark.asyncio
    async def post_automation_metrics_ok_test(self):
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        params = {"ticket_id": 123, "ticket_rows": []}

        msg_published_in_topic = {
            'request_id': request_id,
            'body': params,
            'response_topic': response_topic,
        }

        config = Mock()
        logger = Mock()
        logger.info = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        return_value = {
            "body": "No content",
            "status": 204
        }

        return_kre_value = {
            "body": "No kre content",
            "status": 200,
        }

        t7_repository = Mock()
        t7_repository.post_automation_metrics = Mock(return_value=return_value)

        t7_kre_repository = Mock()
        t7_kre_repository.post_automation_metrics = Mock(return_value=return_kre_value)

        automation_metrics = PostAutomationMetrics(logger, config, event_bus, t7_repository, t7_kre_repository)

        await automation_metrics.post_automation_metrics(msg_published_in_topic)

        t7_repository.post_automation_metrics.assert_called()
        event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': return_value['body'],
                'status': return_value['status']
            }
        )

        assert logger.info.call_count == 2

    @pytest.mark.asyncio
    async def post_automation_metrics_ok_kre_non_200_test(self):
        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        params = {"ticket_id": 123, "ticket_rows": []}

        msg_published_in_topic = {
            'request_id': request_id,
            'body': params,
            'response_topic': response_topic,
        }

        config = Mock()
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        return_value = {
            "body": "No content",
            "status": 204
        }

        return_kre_value = {
            "body": "kre error",
            "status": 500,
        }
        error_kre_msg = (
            f"ERROR on KRE post metric for ticket_id[{params['ticket_id']}]:"
            f"Body: {return_kre_value['body']}, Status: {return_kre_value['status']}"
        )

        t7_repository = Mock()
        t7_repository.post_automation_metrics = Mock(return_value=return_value)

        t7_kre_repository = Mock()
        t7_kre_repository.post_automation_metrics = Mock(return_value=return_kre_value)

        automation_metrics = PostAutomationMetrics(logger, config, event_bus, t7_repository, t7_kre_repository)

        await automation_metrics.post_automation_metrics(msg_published_in_topic)

        t7_repository.post_automation_metrics.assert_called()
        event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': return_value['body'],
                'status': return_value['status']
            }
        )

        assert logger.info.call_count == 1
        logger.error.assert_called_once_with(error_kre_msg)
