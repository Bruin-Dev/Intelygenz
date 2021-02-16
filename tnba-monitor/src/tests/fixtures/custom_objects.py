from typing import List

import pytest


# Model-as-dict generators
def __generate_ticket_object(*, ticket_id: int = None, ticket_creation_date: str = None, ticket_topic: str = None,
                             ticket_creator: str = None, ticket_details: List[dict] = None,
                             ticket_notes: List[dict] = None):
    ticket_id = ticket_id or 12345
    ticket_creation_date = ticket_creation_date or "1/03/2021 10:08:13 AM"
    ticket_topic = ticket_topic or 'Service Outage Trouble'
    ticket_creator = ticket_creator or 'Intelygenz Ai'
    ticket_details = ticket_details or []
    ticket_notes = ticket_notes or []

    return {
        'ticket_id': ticket_id,
        'ticket_creation_date': ticket_creation_date,
        'ticket_topic': ticket_topic,
        'ticket_creator': ticket_creator,
        'ticket_details': ticket_details,
        'ticket_notes': ticket_notes,
    }


def __generate_detail_object(*, ticket_id: int = None, ticket_creation_date: str = None, ticket_topic: str = None,
                             ticket_creator: str = None, ticket_detail: dict = None, ticket_notes: List[dict] = None):
    ticket_id = ticket_id or 12345
    ticket_creation_date = ticket_creation_date or "1/03/2021 10:08:13 AM"
    ticket_topic = ticket_topic or 'Service Outage Trouble'
    ticket_creator = ticket_creator or 'Intelygenz Ai'
    ticket_detail = ticket_detail or {}
    ticket_notes = ticket_notes or []

    return {
        'ticket_id': ticket_id,
        'ticket_creation_date': ticket_creation_date,
        'ticket_topic': ticket_topic,
        'ticket_creator': ticket_creator,
        'ticket_detail': ticket_detail,
        'ticket_notes': ticket_notes,
    }


# Factories
@pytest.fixture(scope='session')
def make_ticket_object():
    def _inner(*, ticket_id: int = None, ticket_creation_date: str = None, ticket_topic: str = None,
               ticket_creator: str = None, ticket_details: List[dict] = None, ticket_notes: List[dict] = None):
        return __generate_ticket_object(
            ticket_id=ticket_id,
            ticket_creation_date=ticket_creation_date,
            ticket_topic=ticket_topic,
            ticket_creator=ticket_creator,
            ticket_details=ticket_details,
            ticket_notes=ticket_notes
        )

    return _inner


@pytest.fixture(scope='session')
def make_detail_object():
    def _inner(*, ticket_id: int = None, ticket_creation_date: str = None, ticket_topic: str = None,
               ticket_creator: str = None, ticket_detail: dict = None, ticket_notes: List[dict] = None):
        return __generate_detail_object(
            ticket_id=ticket_id,
            ticket_creation_date=ticket_creation_date,
            ticket_topic=ticket_topic,
            ticket_creator=ticket_creator,
            ticket_detail=ticket_detail,
            ticket_notes=ticket_notes
        )

    return _inner


@pytest.fixture(scope='session')
def make_detail_object_with_predictions(make_detail_object):
    def _inner(*, ticket_id: int = None, ticket_creation_date: str = None, ticket_topic: str = None,
               ticket_creator: str = None, ticket_detail: dict = None, ticket_notes: List[dict] = None,
               ticket_detail_predictions: List[dict] = None):
        ticket_detail_predictions = ticket_detail_predictions or []

        detail_object = make_detail_object(
            ticket_id=ticket_id,
            ticket_creation_date=ticket_creation_date,
            ticket_topic=ticket_topic,
            ticket_creator=ticket_creator,
            ticket_detail=ticket_detail,
            ticket_notes=ticket_notes
        )

        return {
            **detail_object,
            'ticket_detail_predictions': ticket_detail_predictions,
        }

    return _inner


@pytest.fixture(scope='session')
def make_payload_for_note_append_with_ticket_id(make_payload_for_note_append):
    def _inner(*, ticket_id: int, detail_id: int = None, serial_number: str = None, text: str):
        payload = make_payload_for_note_append(detail_id=detail_id, serial_number=serial_number, text=text)
        payload = {
            'ticket_id': ticket_id,
            **payload,
        }

        return payload

    return _inner


@pytest.fixture(scope='session')
def make_predictions_by_ticket_id_object():
    def _inner(*, ticket_id: int, predictions: List[dict] = None):
        predictions = predictions or []

        return {
            ticket_id: predictions,
        }

    return _inner
