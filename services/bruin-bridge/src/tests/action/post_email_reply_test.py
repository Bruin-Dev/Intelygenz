from logging import Logger
from typing import Any, Callable, Dict
from unittest.mock import ANY, Mock

import pytest
from application.actions.get_asset_topics import *
from application.actions.post_email_reply import BRUIN_PATH, PostBody, PostEmailReply, PostParams
from application.clients.bruin_client import BruinClient
from application.clients.bruin_session import BruinPostRequest, BruinResponse, BruinSession
from asynctest import CoroutineMock
from igz.packages.eventbus.eventbus import EventBus


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
        response = BruinResponse(status=HTTPStatus.OK, body="OK")

        expected_request = BruinPostRequest(
            path=BRUIN_PATH.format(email_id=parent_email_id),
            params=PostParams(isContentHTMLEncoded=False),
            body=PostBody(content=reply_body, email_id=parent_email_id),
        )
        post_email_reply.event_bus.publish_message = CoroutineMock()
        post_email_reply.bruin_client._bruin_session.post = CoroutineMock(
            side_effect=lambda request: response if request == expected_request else None
        )

        # When
        await post_email_reply.post_email_reply(message)

        # Then
        post_email_reply.event_bus.publish_message.assert_awaited_once_with(
            message.get("response_topic"),
            {"request_id": message.get("request_id"), "status": response.status, "body": response.body},
        )

    @pytest.mark.asyncio
    async def request_validation_errors_are_properly_handled_test(self, post_email_reply, make_email_reply_message):
        post_email_reply.event_bus.publish_message = CoroutineMock()

        # Mandatory ticket_id and subscription_type are missing
        await post_email_reply.post_email_reply(make_email_reply_message(body={}))

        post_email_reply.event_bus.publish_message.assert_awaited_once_with(
            ANY, {"request_id": ANY, "status": HTTPStatus.BAD_REQUEST, "body": ANY}
        )

    @pytest.mark.asyncio
    async def unauthorized_requests_are_properly_handled_test(self, post_email_reply, make_email_reply_message):
        post_email_reply.event_bus.publish_message = CoroutineMock()
        post_email_reply.bruin_client.login = CoroutineMock()
        post_email_reply.bruin_client._bruin_session.post = CoroutineMock(
            return_value=BruinResponse(status=HTTPStatus.UNAUTHORIZED)
        )

        await post_email_reply.post_email_reply(make_email_reply_message())

        post_email_reply.bruin_client.login.assert_awaited_once()
        post_email_reply.event_bus.publish_message.assert_awaited_once_with(
            ANY, {"request_id": ANY, "status": HTTPStatus.UNAUTHORIZED, "body": ANY}
        )


#
# Fixtures
#


@pytest.fixture()
def make_email_reply_message() -> Callable[..., Dict[str, Any]]:
    def builder(
        request_id: str = "any_request_id",
        response_topic: str = "any_response_topic",
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

        return {"request_id": request_id, "response_topic": response_topic, "body": body}

    return builder


@pytest.fixture
def post_email_reply() -> PostEmailReply:
    bruin_client = Mock(BruinClient)
    bruin_client._bruin_session = Mock(BruinSession)
    return PostEmailReply(Mock(Logger), Mock(EventBus), bruin_client)
