from http import HTTPStatus
from logging import Logger
from typing import Any, Callable, Dict
from unittest.mock import ANY, Mock

import pytest
from application.actions.post_email_status import BRUIN_PATH, PostBody, PostEmailStatus
from application.clients.bruin_client import BruinClient
from application.clients.bruin_session import BruinPostRequest, BruinResponse, BruinSession
from application.services.sentence_formatter import SentenceFormatter
from asynctest import CoroutineMock
from igz.packages.eventbus.eventbus import EventBus


@pytest.mark.asyncio
async def messages_are_properly_handled_test(make_post_email_status, make_message):
    # Given
    email_id = hash("any_email_id")
    email_status = "any_email_status"
    message = make_message(email_id=email_id, email_status=email_status)

    sentence_subject = "any_subject"
    formatted_sentence = "any_formatted_sentence"
    sentence_formatter = SentenceFormatter(_subject=sentence_subject)
    sentence_formatter.email_marked_as = Mock(return_value=formatted_sentence)
    action = make_post_email_status(sentence_formatter=sentence_formatter)
    action.event_bus.publish_message = CoroutineMock()

    ok_response = BruinResponse(status=HTTPStatus.OK, body="OK")
    expected_request = BruinPostRequest(
        path=BRUIN_PATH,
        body=PostBody(
            email_id=email_id,
            status=email_status,
            resolution=formatted_sentence,
            updated_by=sentence_subject,
        ),
    )
    action.bruin_client._bruin_session.post = CoroutineMock(
        side_effect=lambda request: ok_response if request == expected_request else None
    )

    # When
    await action.post_email_status(message)

    # Then
    action.event_bus.publish_message.assert_awaited_once_with(
        message.get("response_topic"),
        {"request_id": message.get("request_id"), "status": ok_response.status, "body": ok_response.body},
    )


@pytest.mark.asyncio
async def request_validation_errors_are_properly_handled_test(make_post_email_status, make_message):
    action = make_post_email_status()
    action.event_bus.publish_message = CoroutineMock()

    # Mandatory email_id is missing
    await action.post_email_status(make_message(body={"email_status": "any"}))

    action.event_bus.publish_message.assert_awaited_once_with(
        ANY, {"request_id": ANY, "status": HTTPStatus.BAD_REQUEST, "body": ANY}
    )


@pytest.mark.asyncio
async def unauthorized_requests_are_properly_handled_test(make_post_email_status, make_message):
    # Given ...
    action = make_post_email_status()
    action.event_bus.publish_message = CoroutineMock()
    action.bruin_client.login = CoroutineMock()

    unauthorized_response = BruinResponse(status=HTTPStatus.UNAUTHORIZED)
    action.bruin_client._bruin_session.post = CoroutineMock(return_value=unauthorized_response)

    # When
    await action.post_email_status(make_message())

    # Then
    action.bruin_client.login.assert_awaited_once()
    action.event_bus.publish_message.assert_awaited_once_with(
        ANY, {"request_id": ANY, "status": HTTPStatus.UNAUTHORIZED, "body": ANY}
    )


#
# Fixtures
#


@pytest.fixture()
def make_message() -> Callable[..., Dict[str, Any]]:
    def builder(
        request_id: str = "any_request_id",
        response_topic: str = "any_response_topic",
        body: Dict[str, Any] = None,
        email_id: int = hash("any_email_id"),
        email_status: str = "any_email_status",
    ) -> Dict[str, Any]:
        if body is None:
            body = {
                "email_id": email_id,
                "email_status": email_status,
            }

        return {"request_id": request_id, "response_topic": response_topic, "body": body}

    return builder


@pytest.fixture
def make_post_email_status() -> Callable[..., PostEmailStatus]:
    def builder(
        logger: Logger = Mock(Logger),
        event_bus: EventBus = Mock(EventBus),
        bruin_client: BruinClient = Mock(BruinClient),
        bruin_session: BruinSession = Mock(BruinSession),
        sentence_formatter: SentenceFormatter = SentenceFormatter(_subject="any_subject"),
    ) -> PostEmailStatus:
        bruin_client._bruin_session = bruin_session
        return PostEmailStatus(logger, event_bus, bruin_client, sentence_formatter)

    return builder
