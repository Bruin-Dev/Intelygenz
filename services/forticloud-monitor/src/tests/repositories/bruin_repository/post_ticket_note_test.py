from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from bruin_client import BruinRequest, BruinResponse

from application.domain.note import Note
from application.repositories import UnexpectedStatusError


async def ticket_notes_are_properly_posted_test(any_bruin_repository, any_response):
    note = Note(ticket_id="any_ticket_id", service_number="any_service_number", text="any_text")
    send = AsyncMock(return_value=any_response)
    bruin_repository = any_bruin_repository(send=send)

    # when
    await bruin_repository.post_ticket_note(note)

    # then
    send.assert_awaited_once_with(
        BruinRequest(
            method="POST",
            path="/api/Ticket/any_ticket_id/notes",
            json={"note": "any_text", "serviceNumbers": ["any_service_number"]},
        )
    )


async def client_errors_are_properly_propagated_test(any_bruin_repository, any_exception, any_note):
    # given
    bruin_repository = any_bruin_repository(send=AsyncMock(side_effect=any_exception))

    # then
    with pytest.raises(any_exception):
        await bruin_repository.post_ticket_note(any_note)


async def unexpected_response_status_raise_an_exception_test(any_bruin_repository, any_response, any_note):
    # given
    any_response.status = HTTPStatus.BAD_REQUEST
    bruin_repository = any_bruin_repository(send=AsyncMock(return_value=any_response))

    # then
    with pytest.raises(UnexpectedStatusError):
        await bruin_repository.post_ticket_note(any_note)


@pytest.fixture
def any_response():
    return BruinResponse(status=HTTPStatus.OK, text='{"ticketNotes":[]}')
