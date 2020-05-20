from unittest.mock import Mock

import pytest
from asynctest import CoroutineMock

from application.actions.post_multiple_notes import PostMultipleNotes


class TestPostMultipleNotes:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        post_multiple_notes = PostMultipleNotes(logger, event_bus, bruin_repository)

        assert post_multiple_notes._logger is logger
        assert post_multiple_notes._event_bus is event_bus
        assert post_multiple_notes._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def post_multiple_notes_with_all_conditions_met_test(self):
        ticket_id = 12345
        notes = [
            {
                'text': 'Test note 1',
                'service_number': 'VC1234567',
            },
            {
                'text': 'Test note 2',
                'detail_id': 999,
            },
        ]
        response_topic = "some.topic"
        request_id = 19
        request = {
            "request_id": request_id,
            "body": {
                'ticket_id': ticket_id,
                'notes': notes,
            },
            "response_topic": response_topic,
        }

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
            'request_id': request_id,
            **post_multiple_notes_response,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_multiple_ticket_notes = Mock(return_value=post_multiple_notes_response)

        post_multiple_notes = PostMultipleNotes(logger, event_bus, bruin_repository)

        await post_multiple_notes.post_multiple_notes(request)

        bruin_repository.post_multiple_ticket_notes.assert_called_once_with(ticket_id, notes)
        event_bus.publish_message.assert_awaited_once_with(response_topic, event_bus_response)

    @pytest.mark.asyncio
    async def post_multiple_notes_with_missing_body_in_request_test(self):
        response_topic = "some.topic"
        request_id = 19
        request = {
            "request_id": request_id,
            "response_topic": response_topic,
        }

        event_bus_response = {
            'request_id': request_id,
            'body': 'Must include "body" in request',
            'status': 400,
        }

        logger = Mock()
        bruin_repository = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        post_multiple_notes = PostMultipleNotes(logger, event_bus, bruin_repository)

        await post_multiple_notes.post_multiple_notes(request)

        bruin_repository.post_multiple_ticket_notes.assert_not_called()
        event_bus.publish_message.assert_awaited_once_with(response_topic, event_bus_response)

    @pytest.mark.asyncio
    async def post_multiple_notes_with_mandatory_keys_missing_in_body_test(self):
        notes = [
            {
                'text': 'Test note 1',
                'service_number': 'VC1234567',
            },
            {
                'text': 'Test note 2',
                'detail_id': 999,
            },
        ]
        response_topic = "some.topic"
        request_id = 19
        request = {
            "request_id": request_id,
            "body": {
                'notes': notes,
            },
            "response_topic": response_topic,
        }

        event_bus_response = {
            'request_id': request_id,
            'body': 'You must include "ticket_id" and "notes" in the body of the request',
            'status': 400,
        }

        logger = Mock()
        bruin_repository = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        post_multiple_notes = PostMultipleNotes(logger, event_bus, bruin_repository)

        await post_multiple_notes.post_multiple_notes(request)

        bruin_repository.post_multiple_ticket_notes.assert_not_called()
        event_bus.publish_message.assert_awaited_once_with(response_topic, event_bus_response)

    @pytest.mark.asyncio
    async def post_multiple_notes_with_at_least_one_note_not_having_text_test(self):
        ticket_id = 12345
        notes = [
            {
                'service_number': 'VC1234567',
            },
            {
                'text': 'Test note 2',
                'detail_id': 999,
            },
        ]
        response_topic = "some.topic"
        request_id = 19
        request = {
            "request_id": request_id,
            "body": {
                'ticket_id': ticket_id,
                'notes': notes,
            },
            "response_topic": response_topic,
        }

        event_bus_response = {
            'request_id': request_id,
            'body': 'You must include "text" and any of "service_number" and "detail_id" for every '
                    'note in the "notes" field',
            'status': 400,
        }

        logger = Mock()
        bruin_repository = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        post_multiple_notes = PostMultipleNotes(logger, event_bus, bruin_repository)

        await post_multiple_notes.post_multiple_notes(request)

        bruin_repository.post_multiple_ticket_notes.assert_not_called()
        event_bus.publish_message.assert_awaited_once_with(response_topic, event_bus_response)

    @pytest.mark.asyncio
    async def post_multiple_notes_with_at_least_one_note_not_having_detail_id_or_service_number_test(self):
        ticket_id = 12345
        notes = [
            {
                'text': 'Test note 1',
            },
            {
                'text': 'Test note 2',
                'detail_id': 999,
            },
        ]
        response_topic = "some.topic"
        request_id = 19
        request = {
            "request_id": request_id,
            "body": {
                'ticket_id': ticket_id,
                'notes': notes,
            },
            "response_topic": response_topic,
        }

        event_bus_response = {
            'request_id': request_id,
            'body': 'You must include "text" and any of "service_number" and "detail_id" for every '
                    'note in the "notes" field',
            'status': 400,
        }

        logger = Mock()
        bruin_repository = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        post_multiple_notes = PostMultipleNotes(logger, event_bus, bruin_repository)

        await post_multiple_notes.post_multiple_notes(request)

        bruin_repository.post_multiple_ticket_notes.assert_not_called()
        event_bus.publish_message.assert_awaited_once_with(response_topic, event_bus_response)

    @pytest.mark.asyncio
    async def post_multiple_notes_with_notes_having_service_number_or_detail_id_or_both_test(self):
        ticket_id = 12345
        notes = [
            {
                'text': 'Test note 1',
                'service_number': 'VC1234567',
            },
            {
                'text': 'Test note 2',
                'detail_id': 999,
            },
            {
                'text': 'Test note 3',
                'service_number': 'VC99999999',
                'detail_id': 888,
            },
        ]
        response_topic = "some.topic"
        request_id = 19
        request = {
            "request_id": request_id,
            "body": {
                'ticket_id': ticket_id,
                'notes': notes,
            },
            "response_topic": response_topic,
        }

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
            'request_id': request_id,
            **post_multiple_notes_response,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_multiple_ticket_notes = Mock(return_value=post_multiple_notes_response)

        post_multiple_notes = PostMultipleNotes(logger, event_bus, bruin_repository)

        await post_multiple_notes.post_multiple_notes(request)

        bruin_repository.post_multiple_ticket_notes.assert_called_once_with(ticket_id, notes)
        event_bus.publish_message.assert_awaited_once_with(response_topic, event_bus_response)
