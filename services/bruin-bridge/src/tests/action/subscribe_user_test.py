from logging import Logger
from typing import Callable, Dict, Any
from unittest.mock import Mock, ANY

import pytest
from asynctest import CoroutineMock
from igz.packages.eventbus.eventbus import EventBus

from application.actions.get_asset_topics import *
from application.actions.subscribe_user import SubscribeUser, BRUIN_PATH, PostBody, PostBodyUser
from application.clients.bruin_client import BruinClient
from application.clients.bruin_session import BruinSession, BruinPostRequest, BruinResponse


class TestSubscribeUser:
    @pytest.mark.asyncio
    async def messages_are_properly_handled_test(self, subscribe_user, make_subscribe_user_message):
        # Given
        ticket_id = hash("any_ticket_id")
        user_email = "any_user_email"
        subscription_type = "any_subscription_type"
        message = make_subscribe_user_message(ticket_id=ticket_id,
                                              user_email=user_email,
                                              subscription_type=subscription_type)
        response = BruinResponse(status=HTTPStatus.OK, body="OK")

        subscribe_user.event_bus.publish_message = CoroutineMock()
        subscribe_user.bruin_client._bruin_session.post = CoroutineMock(
            side_effect=lambda request: response
            if request == BruinPostRequest(
                path=BRUIN_PATH.format(ticket_id=ticket_id),
                body=PostBody(subscription_type=subscription_type, user=PostBodyUser(email=user_email)))
            else None)

        # When
        await subscribe_user.subscribe_user(message)

        # Then
        subscribe_user.event_bus.publish_message.assert_awaited_once_with(message.get("response_topic"), {
            "request_id": message.get("request_id"),
            "status": response.status,
            "body": response.body
        })

    @pytest.mark.asyncio
    async def request_validation_errors_are_properly_handled_test(
        self,
        subscribe_user,
        make_subscribe_user_message
    ):
        subscribe_user.event_bus.publish_message = CoroutineMock()

        # Mandatory ticket_id and subscription_type are missing
        await subscribe_user.subscribe_user(make_subscribe_user_message(body={"user_email": "any_user_email"}))

        subscribe_user.event_bus.publish_message.assert_awaited_once_with(ANY, {
            "request_id": ANY,
            "status": HTTPStatus.BAD_REQUEST,
            "body": ANY
        })

    @pytest.mark.asyncio
    async def unauthorized_requests_are_properly_handled_test(
        self,
        subscribe_user,
        make_subscribe_user_message
    ):
        subscribe_user.event_bus.publish_message = CoroutineMock()
        subscribe_user.bruin_client.login = CoroutineMock()
        subscribe_user.bruin_client._bruin_session.post = CoroutineMock(
            return_value=BruinResponse(status=HTTPStatus.UNAUTHORIZED))

        await subscribe_user.subscribe_user(make_subscribe_user_message())

        subscribe_user.bruin_client.login.assert_awaited_once()
        subscribe_user.event_bus.publish_message.assert_awaited_once_with(ANY, {
            "request_id": ANY,
            "status": HTTPStatus.UNAUTHORIZED,
            "body": ANY
        })


#
# Fixtures
#

@pytest.fixture()
def make_subscribe_user_message() -> Callable[..., Dict[str, Any]]:
    def builder(
        request_id: str = "any_request_id",
        response_topic: str = "any_response_topic",
        body: Dict[str, Any] = None,
        ticket_id: str = hash("any_ticket_id"),
        user_email: str = "any_user_email",
        subscription_type: str = "any_subscription_type"
    ) -> Dict[str, Any]:
        if body is None:
            body = {
                "ticket_id": ticket_id,
                "user_email": user_email,
                "subscription_type": subscription_type,
            }

        return {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": body
        }

    return builder


@pytest.fixture
def subscribe_user() -> SubscribeUser:
    bruin_client = Mock(BruinClient)
    bruin_client._bruin_session = Mock(BruinSession)
    return SubscribeUser(Mock(Logger), Mock(EventBus), bruin_client)
