from unittest.mock import Mock

import pytest
from application.actions.save_created_ticket_feedback import SaveCreatedTicketFeedback
from asynctest import CoroutineMock


class TestSaveCreatedTicketFeedback:

    def instance_test(self):
        config = Mock()
        logger = Mock()
        event_bus = Mock()
        kre_repository = Mock()

        instance = SaveCreatedTicketFeedback(logger, config, event_bus, kre_repository)

        assert instance._config == config
        assert instance._logger == logger
        assert instance._event_bus == event_bus
        assert instance._kre_repository == kre_repository

    @pytest.mark.parametrize(
        'body_in_topic', [
            {},
            ({'some-key': 'some-data'}),
        ], ids=[
            'without_body',
            'without_params',
        ]
    )
    @pytest.mark.asyncio
    async def save_created_ticket_feedback_error_400_test(self, body_in_topic):
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
        kre_repository.save_created_ticket_feedback = CoroutineMock()

        created_ticket_action = SaveCreatedTicketFeedback(logger, config, event_bus, kre_repository)

        await created_ticket_action.save_created_ticket_feedback(msg_published_in_topic)

        logger.error.assert_called_once()
        created_ticket_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                'body': f'You must use correct format in the request',
                'status': 400,
            }
        )
        created_ticket_action._kre_repository.save_created_ticket_feedback.assert_not_awaited()
        logger.info.assert_not_called()

    @pytest.mark.asyncio
    async def save_created_ticket_feedback_test(self, valid_created_ticket_request, valid_created_ticket_response):
        config = Mock()
        logger = Mock()

        request_id = 123
        response_topic = '_INBOX.2007314fe0fcb2cdc2a2914c1'
        msg_published_in_topic = {
            'request_id': request_id,
            'body': valid_created_ticket_request,
            'response_topic': response_topic,
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        kre_repository = Mock()
        kre_repository.save_created_ticket_feedback = CoroutineMock(return_value=valid_created_ticket_response)

        created_ticket_action = SaveCreatedTicketFeedback(logger, config, event_bus, kre_repository)

        await created_ticket_action.save_created_ticket_feedback(msg_published_in_topic)

        created_ticket_action._kre_repository.save_created_ticket_feedback.\
            assert_awaited_once_with(valid_created_ticket_request)
        created_ticket_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                'request_id': request_id,
                **valid_created_ticket_response,
            }
        )
        logger.info.assert_called_once()
