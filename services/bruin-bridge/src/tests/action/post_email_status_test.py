from http import HTTPStatus
from typing import Any, Callable, Dict
from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.post_email_status import BRUIN_PATH, PostBody, PostEmailStatus
from application.clients.bruin_client import BruinClient
from application.clients.bruin_session import BruinPostRequest, BruinResponse, BruinSession
from application.repositories.utils_repository import to_json_bytes
from application.services.sentence_formatter import SentenceFormatter
from nats.aio.msg import Msg


@pytest.mark.asyncio
async def messages_are_properly_handled_test(make_post_email_status, make_message):
    # Given
    email_id = hash("any_email_id")
    email_status = "any_email_status"
    message = make_message(email_id=email_id, email_status=email_status)

    request_msg = Mock(spec_set=Msg)
    request_msg.data = to_json_bytes(message)

    sentence_subject = "any_subject"
    formatted_sentence = "any_formatted_sentence"
    sentence_formatter = SentenceFormatter(_subject=sentence_subject)
    sentence_formatter.email_marked_as = Mock(return_value=formatted_sentence)
    action = make_post_email_status(sentence_formatter=sentence_formatter)

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
    action.bruin_client._bruin_session.post = AsyncMock(
        side_effect=lambda request: ok_response if request == expected_request else None
    )

    # When
    await action(request_msg)

    # Then
    request_msg.respond.assert_awaited_once_with(
        to_json_bytes({"status": ok_response.status, "body": ok_response.body})
    )


@pytest.mark.asyncio
async def request_validation_errors_are_properly_handled_test(make_post_email_status, make_message):
    message = make_message(body={"email_status": "any"})

    request_msg = Mock(spec_set=Msg)
    request_msg.data = to_json_bytes(message)

    action = make_post_email_status()

    # Mandatory email_id is missing
    await action(request_msg)

    request_msg.respond.assert_awaited_once_with(
        to_json_bytes(
            {
                "status": HTTPStatus.BAD_REQUEST,
                "body": [{"loc": ["email_id"], "msg": "field required", "type": "value_error.missing"}],
            }
        )
    )


@pytest.mark.asyncio
async def unauthorized_requests_are_properly_handled_test(make_post_email_status, make_message):
    # Given ...
    message = make_message()

    request_msg = Mock(spec_set=Msg)
    request_msg.data = to_json_bytes(message)

    action = make_post_email_status()
    action.bruin_client.login = AsyncMock()

    unauthorized_response = BruinResponse(status=HTTPStatus.UNAUTHORIZED)
    action.bruin_client._bruin_session.post = AsyncMock(return_value=unauthorized_response)

    # When
    await action(request_msg)

    # Then
    action.bruin_client.login.assert_awaited_once()
    request_msg.respond.assert_awaited_once_with(to_json_bytes({"status": HTTPStatus.UNAUTHORIZED, "body": None}))


#
# Fixtures
#


@pytest.fixture()
def make_message() -> Callable[..., Dict[str, Any]]:
    def builder(
        body: Dict[str, Any] = None,
        email_id: int = hash("any_email_id"),
        email_status: str = "any_email_status",
    ) -> Dict[str, Any]:
        if body is None:
            body = {
                "email_id": email_id,
                "email_status": email_status,
            }

        return {"body": body}

    return builder


@pytest.fixture
def make_post_email_status() -> Callable[..., PostEmailStatus]:
    def builder(
        bruin_client: BruinClient = Mock(BruinClient),
        bruin_session: BruinSession = Mock(BruinSession),
        sentence_formatter: SentenceFormatter = SentenceFormatter(_subject="any_subject"),
    ) -> PostEmailStatus:
        bruin_client._bruin_session = bruin_session
        return PostEmailStatus(bruin_client, sentence_formatter)

    return builder
