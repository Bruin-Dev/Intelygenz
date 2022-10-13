from http import HTTPStatus
from typing import Any, Callable, Dict
from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.subscribe_user import BRUIN_PATH, PostBody, PostBodyUser, SubscribeUser
from application.clients.bruin_client import BruinClient
from application.clients.bruin_session import BruinPostRequest, BruinResponse, BruinSession
from application.repositories.utils_repository import to_json_bytes


class TestSubscribeUser:
    @pytest.mark.asyncio
    async def messages_are_properly_handled_test(self, subscribe_user, make_subscribe_user_message):
        # Given
        ticket_id = hash("any_ticket_id")
        user_email = "any_user_email"
        subscription_type = "any_subscription_type"
        message = make_subscribe_user_message(
            ticket_id=ticket_id, user_email=user_email, subscription_type=subscription_type
        )

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(message)

        response = BruinResponse(status=HTTPStatus.OK, body="OK")

        subscribe_user.bruin_client._bruin_session.post = AsyncMock(
            side_effect=lambda request: response
            if request
            == BruinPostRequest(
                path=BRUIN_PATH.format(ticket_id=ticket_id),
                body=PostBody(subscription_type=subscription_type, user=PostBodyUser(email=user_email)),
            )
            else None
        )

        # When
        await subscribe_user(request_msg)

        # Then
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"status": response.status, "body": response.body}),
        )

    @pytest.mark.asyncio
    async def request_validation_errors_are_properly_handled_test(self, subscribe_user, make_subscribe_user_message):
        message = make_subscribe_user_message(body={"user_email": "any_user_email"})

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(message)

        # Mandatory ticket_id and subscription_type are missing
        await subscribe_user(request_msg)

        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "status": HTTPStatus.BAD_REQUEST,
                    "body": [
                        {"loc": ["ticket_id"], "msg": "field required", "type": "value_error.missing"},
                        {"loc": ["subscription_type"], "msg": "field required", "type": "value_error.missing"},
                    ],
                }
            )
        )

    @pytest.mark.asyncio
    async def unauthorized_requests_are_properly_handled_test(self, subscribe_user, make_subscribe_user_message):
        message = make_subscribe_user_message()

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(message)

        subscribe_user.bruin_client.login = AsyncMock()
        subscribe_user.bruin_client._bruin_session.post = AsyncMock(
            return_value=BruinResponse(status=HTTPStatus.UNAUTHORIZED)
        )

        await subscribe_user(request_msg)

        subscribe_user.bruin_client.login.assert_awaited_once()
        request_msg.respond.assert_awaited_once_with(to_json_bytes({"status": HTTPStatus.UNAUTHORIZED, "body": None}))


#
# Fixtures
#


@pytest.fixture()
def make_subscribe_user_message() -> Callable[..., Dict[str, Any]]:
    def builder(
        body: Dict[str, Any] = None,
        ticket_id: str = hash("any_ticket_id"),
        user_email: str = "any_user_email",
        subscription_type: str = "any_subscription_type",
    ) -> Dict[str, Any]:
        if body is None:
            body = {
                "ticket_id": ticket_id,
                "user_email": user_email,
                "subscription_type": subscription_type,
            }

        return {"body": body}

    return builder


@pytest.fixture
def subscribe_user() -> SubscribeUser:
    bruin_client = Mock(BruinClient)
    bruin_client._bruin_session = Mock(BruinSession)
    return SubscribeUser(bruin_client)
