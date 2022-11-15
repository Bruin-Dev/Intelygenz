from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.post_note import PostNote
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestPostNote:
    def instance_test(self):
        bruin_repository = Mock()

        post_note = PostNote(bruin_repository)

        assert post_note._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def post_note_no_body_test(self):
        append_note_response = "Note appended"
        msg = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {"body": 'Must include "body" in request', "status": 400}

        bruin_repository = Mock()
        bruin_repository.post_ticket_note = AsyncMock(return_value=append_note_response)

        post_note = PostNote(bruin_repository)
        await post_note(request_msg)

        post_note._bruin_repository.post_ticket_note.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))

    @pytest.mark.asyncio
    async def post_note_no_ticket_id_or_note_test(self):
        append_note_response = "Note appended"
        msg = {
            "body": {},
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {
            "body": 'You must include "ticket_id" and "note" in the "body" field of the response request',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.post_ticket_note = AsyncMock(return_value=append_note_response)

        post_note = PostNote(bruin_repository)
        await post_note(request_msg)

        post_note._bruin_repository.post_ticket_note.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))

    @pytest.mark.asyncio
    async def post_note_200_test(self):
        append_note_response = {"body": "Note appended", "status": 200}
        ticket_id = 321
        note_contents = "Some Note"
        msg = {
            "body": {
                "ticket_id": ticket_id,
                "note": note_contents,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {"body": append_note_response["body"], "status": 200}

        bruin_repository = Mock()
        bruin_repository.post_ticket_note = AsyncMock(return_value=append_note_response)

        post_note = PostNote(bruin_repository)
        await post_note(request_msg)

        post_note._bruin_repository.post_ticket_note.assert_awaited_once_with(
            ticket_id, note_contents, service_numbers=None
        )
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))

    @pytest.mark.asyncio
    async def post_note_with_optional_service_numbers_list_test(self):
        ticket_id = 321
        note_contents = "Some Note"
        service_numbers = ["VC1234567"]

        append_note_response = {"body": "Note appended", "status": 200}

        msg = {
            "body": {
                "ticket_id": ticket_id,
                "note": note_contents,
                "service_numbers": service_numbers,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {"body": append_note_response["body"], "status": 200}

        bruin_repository = Mock()
        bruin_repository.post_ticket_note = AsyncMock(return_value=append_note_response)

        post_note = PostNote(bruin_repository)
        await post_note(request_msg)

        post_note._bruin_repository.post_ticket_note.assert_awaited_once_with(
            ticket_id, note_contents, service_numbers=service_numbers
        )
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))
