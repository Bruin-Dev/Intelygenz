from http import HTTPStatus
from typing import Any, Callable, Dict
from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.post_email_reply import BRUIN_PATH, PostBody, PostEmailReply, PostParams
from application.clients.bruin_client import BruinClient
from application.clients.bruin_session import BruinPostRequest, BruinResponse, BruinSession
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestPostEmailReply:
    @pytest.mark.asyncio
    async def messages_are_properly_handled_test(self, post_email_reply, make_email_reply_message):
        # Given
        parent_email_id = str(hash("any_parent_email_id"))
        reply_body = "any_reply_body"
        message = make_email_reply_message(
            parent_email_id=parent_email_id,
            reply_body=reply_body,
            html_reply_body=False,
        )

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(message)

        response = BruinResponse(status=HTTPStatus.OK, body="OK")

        expected_request = BruinPostRequest(
            path=BRUIN_PATH.format(email_id=parent_email_id),
            params=PostParams(isContentHTMLEncoded=False),
            body=PostBody(content=reply_body, email_id=parent_email_id),
        )
        post_email_reply.bruin_client._bruin_session.post = AsyncMock(
            side_effect=lambda request: response if request == expected_request else None
        )

        # When
        await post_email_reply(request_msg)

        # Then
        request_msg.respond.assert_awaited_once_with(to_json_bytes({"status": response.status, "body": response.body}))

    @pytest.mark.asyncio
    async def request_validation_errors_are_properly_handled_test(self, post_email_reply, make_email_reply_message):
        # Mandatory ticket_id and subscription_type are missing
        message = make_email_reply_message(body={})

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(message)

        await post_email_reply(request_msg)

        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "status": HTTPStatus.BAD_REQUEST,
                    "body": [
                        {"loc": ["parent_email_id"], "msg": "field required", "type": "value_error.missing"},
                        {"loc": ["reply_body"], "msg": "field required", "type": "value_error.missing"},
                    ],
                }
            )
        )

    @pytest.mark.asyncio
    async def unauthorized_requests_are_properly_handled_test(self, post_email_reply, make_email_reply_message):
        message = make_email_reply_message()

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(message)

        post_email_reply.bruin_client.login = AsyncMock()
        post_email_reply.bruin_client._bruin_session.post = AsyncMock(
            return_value=BruinResponse(status=HTTPStatus.UNAUTHORIZED)
        )

        await post_email_reply(request_msg)

        post_email_reply.bruin_client.login.assert_awaited_once()
        request_msg.respond.assert_awaited_once_with(to_json_bytes({"status": HTTPStatus.UNAUTHORIZED, "body": None}))


#
# Fixtures
#


@pytest.fixture()
def make_email_reply_message() -> Callable[..., Dict[str, Any]]:
    def builder(
        body: Dict[str, Any] = None,
        parent_email_id: str = str(hash("any_parent_email_id")),
        reply_body: str = "any_reply_body",
        html_reply_body: bool = True,
    ) -> Dict[str, Any]:
        if body is None:
            body = {
                "parent_email_id": parent_email_id,
                "reply_body": reply_body,
                "html_reply_body": html_reply_body,
            }

        return {"body": body}

    return builder


@pytest.fixture
def post_email_reply() -> PostEmailReply:
    bruin_client = Mock(BruinClient)
    bruin_client._bruin_session = Mock(BruinSession)
    return PostEmailReply(bruin_client)
