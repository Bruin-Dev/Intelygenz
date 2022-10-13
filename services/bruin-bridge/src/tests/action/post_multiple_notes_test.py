from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.post_multiple_notes import PostMultipleNotes
from application.repositories.utils_repository import to_json_bytes


class TestPostMultipleNotes:
    def instance_test(self):
        bruin_repository = Mock()

        post_multiple_notes = PostMultipleNotes(bruin_repository)

        assert post_multiple_notes._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def post_multiple_notes_with_all_conditions_met_test(self):
        ticket_id = 12345
        notes = [
            {
                "text": "Test note 1",
                "service_number": "VC1234567",
            },
            {
                "text": "Test note 2",
                "detail_id": 999,
            },
        ]
        request = {
            "body": {
                "ticket_id": ticket_id,
                "notes": notes,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request)

        post_multiple_notes_response = {
            "body": [
                {
                    "noteID": 70646090,
                    "noteType": "ADN",
                    "noteValue": "Test note 1",
                    "actionID": None,
                    "detailID": 5002307,
                    "enteredBy": 442301,
                    "enteredDate": "2020-05-20T06:00:38.803-04:00",
                    "lastViewedBy": None,
                    "lastViewedDate": None,
                    "refNoteID": None,
                    "noteStatus": None,
                    "noteText": None,
                    "childNotes": None,
                    "documents": None,
                    "alerts": None,
                    "taggedUserDirIDs": None,
                },
                {
                    "noteID": 70646091,
                    "noteType": "ADN",
                    "noteValue": "Test note 2",
                    "actionID": None,
                    "detailID": 999,
                    "enteredBy": 442301,
                    "enteredDate": "2020-05-20T06:00:38.803-04:00",
                    "lastViewedBy": None,
                    "lastViewedDate": None,
                    "refNoteID": None,
                    "noteStatus": None,
                    "noteText": None,
                    "childNotes": None,
                    "documents": None,
                    "alerts": None,
                    "taggedUserDirIDs": None,
                },
            ],
            "status": 200,
        }
        event_bus_response = {
            **post_multiple_notes_response,
        }

        bruin_repository = Mock()
        bruin_repository.post_multiple_ticket_notes = AsyncMock(return_value=post_multiple_notes_response)

        post_multiple_notes = PostMultipleNotes(bruin_repository)

        await post_multiple_notes(request_msg)

        bruin_repository.post_multiple_ticket_notes.assert_awaited_once_with(ticket_id, notes)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def post_multiple_notes_with_missing_body_in_request_test(self):
        request = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request)

        event_bus_response = {
            "body": 'Must include "body" in request',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.post_multiple_ticket_notes = AsyncMock()

        post_multiple_notes = PostMultipleNotes(bruin_repository)

        await post_multiple_notes(request_msg)

        bruin_repository.post_multiple_ticket_notes.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def post_multiple_notes_with_mandatory_keys_missing_in_body_test(self):
        notes = [
            {
                "text": "Test note 1",
                "service_number": "VC1234567",
            },
            {
                "text": "Test note 2",
                "detail_id": 999,
            },
        ]
        request = {
            "body": {
                "notes": notes,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request)

        event_bus_response = {
            "body": 'You must include "ticket_id" and "notes" in the body of the request',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.post_multiple_ticket_notes = AsyncMock()

        post_multiple_notes = PostMultipleNotes(bruin_repository)

        await post_multiple_notes(request_msg)

        bruin_repository.post_multiple_ticket_notes.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def post_multiple_notes_with_at_least_one_note_not_having_text_test(self):
        ticket_id = 12345
        notes = [
            {
                "service_number": "VC1234567",
            },
            {
                "text": "Test note 2",
                "detail_id": 999,
            },
        ]
        request = {
            "body": {
                "ticket_id": ticket_id,
                "notes": notes,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request)

        event_bus_response = {
            "body": 'You must include "text" and any of "service_number" and "detail_id" for every '
            'note in the "notes" field',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.post_multiple_ticket_notes = AsyncMock()

        post_multiple_notes = PostMultipleNotes(bruin_repository)

        await post_multiple_notes(request_msg)

        bruin_repository.post_multiple_ticket_notes.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def post_multiple_notes_with_at_least_one_note_not_having_detail_id_or_service_number_test(self):
        ticket_id = 12345
        notes = [
            {
                "text": "Test note 1",
            },
            {
                "text": "Test note 2",
                "detail_id": 999,
            },
        ]
        request = {
            "body": {
                "ticket_id": ticket_id,
                "notes": notes,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request)

        event_bus_response = {
            "body": 'You must include "text" and any of "service_number" and "detail_id" for every '
            'note in the "notes" field',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.post_multiple_ticket_notes = AsyncMock()

        post_multiple_notes = PostMultipleNotes(bruin_repository)

        await post_multiple_notes(request_msg)

        bruin_repository.post_multiple_ticket_notes.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def post_multiple_notes_with_notes_having_service_number_or_detail_id_or_both_test(self):
        ticket_id = 12345
        notes = [
            {
                "text": "Test note 1",
                "service_number": "VC1234567",
            },
            {
                "text": "Test note 2",
                "detail_id": 999,
            },
            {
                "text": "Test note 3",
                "service_number": "VC99999999",
                "detail_id": 888,
            },
        ]
        request = {
            "body": {
                "ticket_id": ticket_id,
                "notes": notes,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request)

        post_multiple_notes_response = {
            "body": [
                {
                    "noteID": 70646090,
                    "noteType": "ADN",
                    "noteValue": "Test note 1",
                    "actionID": None,
                    "detailID": 5002307,
                    "enteredBy": 442301,
                    "enteredDate": "2020-05-20T06:00:38.803-04:00",
                    "lastViewedBy": None,
                    "lastViewedDate": None,
                    "refNoteID": None,
                    "noteStatus": None,
                    "noteText": None,
                    "childNotes": None,
                    "documents": None,
                    "alerts": None,
                    "taggedUserDirIDs": None,
                },
                {
                    "noteID": 70646091,
                    "noteType": "ADN",
                    "noteValue": "Test note 2",
                    "actionID": None,
                    "detailID": 999,
                    "enteredBy": 442301,
                    "enteredDate": "2020-05-20T06:00:38.803-04:00",
                    "lastViewedBy": None,
                    "lastViewedDate": None,
                    "refNoteID": None,
                    "noteStatus": None,
                    "noteText": None,
                    "childNotes": None,
                    "documents": None,
                    "alerts": None,
                    "taggedUserDirIDs": None,
                },
                {
                    "noteID": 70646091,
                    "noteType": "ADN",
                    "noteValue": "Test note 3",
                    "actionID": None,
                    "detailID": 888,
                    "enteredBy": 442301,
                    "enteredDate": "2020-05-20T06:00:38.803-04:00",
                    "lastViewedBy": None,
                    "lastViewedDate": None,
                    "refNoteID": None,
                    "noteStatus": None,
                    "noteText": None,
                    "childNotes": None,
                    "documents": None,
                    "alerts": None,
                    "taggedUserDirIDs": None,
                },
            ],
            "status": 200,
        }
        event_bus_response = {
            **post_multiple_notes_response,
        }

        bruin_repository = Mock()
        bruin_repository.post_multiple_ticket_notes = AsyncMock(return_value=post_multiple_notes_response)

        post_multiple_notes = PostMultipleNotes(bruin_repository)

        await post_multiple_notes(request_msg)

        bruin_repository.post_multiple_ticket_notes.assert_awaited_once_with(ticket_id, notes)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))
