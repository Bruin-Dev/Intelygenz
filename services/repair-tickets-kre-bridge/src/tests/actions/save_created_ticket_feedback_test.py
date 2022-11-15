from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.save_created_ticket_feedback import SaveCreatedTicketFeedback
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestSaveCreatedTicketFeedback:
    def instance_test(self):
        kre_repository = Mock()

        instance = SaveCreatedTicketFeedback(kre_repository)

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
    async def save_created_ticket_feedback_error_400_test(self, body_in_topic):
        request_id = 123
        msg_published_in_topic = {"request_id": request_id, "body": body_in_topic}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        kre_repository = Mock()
        kre_repository.save_created_ticket_feedback = AsyncMock()

        created_ticket_action = SaveCreatedTicketFeedback(kre_repository)

        await created_ticket_action(request_msg)

        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "request_id": request_id,
                    "body": f"You must use correct format in the request",
                    "status": 400,
                }
            ),
        )
        created_ticket_action._kre_repository.save_created_ticket_feedback.assert_not_awaited()

    @pytest.mark.asyncio
    async def save_created_ticket_feedback_test(self, valid_created_ticket_request, valid_created_ticket_response):
        request_id = 123
        msg_published_in_topic = {
            "request_id": request_id,
            "body": valid_created_ticket_request,
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        kre_repository = Mock()
        kre_repository.save_created_ticket_feedback = AsyncMock(return_value=valid_created_ticket_response)

        created_ticket_action = SaveCreatedTicketFeedback(kre_repository)

        await created_ticket_action(request_msg)

        created_ticket_action._kre_repository.save_created_ticket_feedback.assert_awaited_once_with(
            valid_created_ticket_request
        )
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "request_id": request_id,
                    **valid_created_ticket_response,
                }
            ),
        )
