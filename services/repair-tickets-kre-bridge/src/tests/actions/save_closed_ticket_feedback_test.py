from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.save_closed_ticket_feedback import SaveClosedTicketFeedback
from application.repositories.utils_repository import to_json_bytes


class TestSaveClosedTicketFeedback:
    def instance_test(self):
        kre_repository = Mock()

        instance = SaveClosedTicketFeedback(kre_repository)

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
        msg_published_in_topic = {"request_id": request_id, "body": body_in_topic}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        kre_repository = Mock()
        kre_repository.save_closed_ticket_feedback = AsyncMock()

        closed_ticket_action = SaveClosedTicketFeedback(kre_repository)

        await closed_ticket_action(request_msg)

        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "request_id": request_id,
                    "body": f"You must use correct format in the request",
                    "status": 400,
                }
            ),
        )
        closed_ticket_action._kre_repository.save_closed_ticket_feedback.assert_not_awaited()

    @pytest.mark.asyncio
    async def save_closed_ticket_feedback_test(
        self, valid_closed_ticket_request__resolved, valid_closed_ticket_response
    ):
        request_id = 123
        msg_published_in_topic = {
            "request_id": request_id,
            "body": valid_closed_ticket_request__resolved,
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        kre_repository = Mock()
        kre_repository.save_closed_ticket_feedback = AsyncMock(return_value=valid_closed_ticket_response)

        closed_ticket_action = SaveClosedTicketFeedback(kre_repository)

        await closed_ticket_action(request_msg)

        closed_ticket_action._kre_repository.save_closed_ticket_feedback.assert_awaited_once_with(
            valid_closed_ticket_request__resolved
        )
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "request_id": request_id,
                    **valid_closed_ticket_response,
                }
            ),
        )
