from unittest.mock import Mock

import pytest
from application.actions.save_closed_ticket_feedback import SaveClosedTicketFeedback
from asynctest import CoroutineMock


class TestSaveClosedTicketFeedback:
    def instance_test(self):
        config = Mock()
        logger = Mock()
        event_bus = Mock()
        kre_repository = Mock()

        instance = SaveClosedTicketFeedback(logger, config, event_bus, kre_repository)

        assert instance._config == config
        assert instance._logger == logger
        assert instance._event_bus == event_bus
        assert instance._kre_repository == kre_repository

    @pytest.mark.parametrize(
        "body_in_topic",
        [
            {},
            ({"some-key": "some-data"}),
        ],
        ids=[
            "without_body",
            "without_params",
        ],
    )
    @pytest.mark.asyncio
    async def save_closed_ticket_feedback_error_400_test(self, body_in_topic):
        request_id = 123
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg_published_in_topic = {"request_id": request_id, "response_topic": response_topic, "body": body_in_topic}
        config = Mock()
        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        kre_repository = Mock()
        kre_repository.save_closed_ticket_feedback = CoroutineMock()

        closed_ticket_action = SaveClosedTicketFeedback(logger, config, event_bus, kre_repository)

        await closed_ticket_action.save_closed_ticket_feedback(msg_published_in_topic)

        logger.error.assert_called_once()
        closed_ticket_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                "request_id": request_id,
                "body": f"You must use correct format in the request",
                "status": 400,
            },
        )
        closed_ticket_action._kre_repository.save_closed_ticket_feedback.assert_not_awaited()
        logger.info.assert_not_called()

    @pytest.mark.asyncio
    async def save_closed_ticket_feedback_test(
        self, valid_closed_ticket_request__resolved, valid_closed_ticket_response
    ):
        config = Mock()
        logger = Mock()

        request_id = 123
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg_published_in_topic = {
            "request_id": request_id,
            "body": valid_closed_ticket_request__resolved,
            "response_topic": response_topic,
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        kre_repository = Mock()
        kre_repository.save_closed_ticket_feedback = CoroutineMock(return_value=valid_closed_ticket_response)

        closed_ticket_action = SaveClosedTicketFeedback(logger, config, event_bus, kre_repository)

        await closed_ticket_action.save_closed_ticket_feedback(msg_published_in_topic)

        closed_ticket_action._kre_repository.save_closed_ticket_feedback.assert_awaited_once_with(
            valid_closed_ticket_request__resolved
        )
        closed_ticket_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {
                "request_id": request_id,
                **valid_closed_ticket_response,
            },
        )
        logger.info.assert_called_once()
