from typing import List
from collections import defaultdict

import pytest


# Model-as-dict generators
def __generate_ticket_object(*, ticket_id: int = None, ticket_creation_date: str = None, ticket_topic: str = None,
                             ticket_creator: str = None, ticket_details: List[dict] = None,
                             ticket_notes: List[dict] = None, ticket_status: str = None):
    ticket_id = ticket_id or 12345
    ticket_creation_date = ticket_creation_date or "1/03/2021 10:08:13 AM"
    ticket_topic = ticket_topic or 'VOO'
    ticket_creator = ticket_creator or 'Intelygenz Ai'
    ticket_details = ticket_details or []
    ticket_notes = ticket_notes or []
    ticket_status = ticket_status or 'In-Progress'

    return {
        'ticket_id': ticket_id,
        'ticket_creation_date': ticket_creation_date,
        'ticket_status': ticket_status,
        'ticket_topic': ticket_topic,
        'ticket_creator': ticket_creator,
        'ticket_details': ticket_details,
        'ticket_notes': ticket_notes,
    }


def __generate_detail_object(*, ticket_id: int = None, ticket_creation_date: str = None, ticket_topic: str = None,
                             ticket_creator: str = None, ticket_detail: dict = None, ticket_notes: List[dict] = None,
                             ticket_status: str = None):
    ticket_id = ticket_id or 12345
    ticket_creation_date = ticket_creation_date or "1/03/2021 10:08:13 AM"
    ticket_topic = ticket_topic or 'VOO'
    ticket_creator = ticket_creator or 'Intelygenz Ai'
    ticket_detail = ticket_detail or {}
    ticket_notes = ticket_notes or []
    ticket_status = ticket_status or 'In-Progress'

    return {
        'ticket_id': ticket_id,
        'ticket_creation_date': ticket_creation_date,
        'ticket_status': ticket_status,
        'ticket_topic': ticket_topic,
        'ticket_creator': ticket_creator,
        'ticket_detail': ticket_detail,
        'ticket_notes': ticket_notes,
    }


# Factories
@pytest.fixture(scope='session')
def make_ticket_object():
    def _inner(*, ticket_id: int = None, ticket_creation_date: str = None, ticket_topic: str = None,
               ticket_creator: str = None, ticket_details: List[dict] = None, ticket_notes: List[dict] = None,
               ticket_status: str = None):
        return __generate_ticket_object(
            ticket_id=ticket_id,
            ticket_creation_date=ticket_creation_date,
            ticket_status=ticket_status,
            ticket_topic=ticket_topic,
            ticket_creator=ticket_creator,
            ticket_details=ticket_details,
            ticket_notes=ticket_notes
        )

    return _inner


@pytest.fixture(scope='session')
def make_detail_object():
    def _inner(*, ticket_id: int = None, ticket_creation_date: str = None, ticket_topic: str = None,
               ticket_creator: str = None, ticket_detail: dict = None, ticket_notes: List[dict] = None,
               ticket_status: str = None):
        return __generate_detail_object(
            ticket_id=ticket_id,
            ticket_creation_date=ticket_creation_date,
            ticket_status=ticket_status,
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
               ticket_detail_predictions: List[dict] = None, ticket_status: str = None):
        ticket_detail_predictions = ticket_detail_predictions or []

        detail_object = make_detail_object(
            ticket_id=ticket_id,
            ticket_creation_date=ticket_creation_date,
            ticket_status=ticket_status,
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


@pytest.fixture(scope='session')
def make_list_of_ticket_notes():
    def _inner(*ticket_notes: List[dict]):
        return list(ticket_notes)

    return _inner


@pytest.fixture(scope='session')
def make_link_metrics_and_events_object(make_metrics):
    def _inner(*, metrics: dict = None, events: list = None,):
        metrics = metrics or make_metrics()
        events = events or []
        return {
                'link_events': events,
                'link_metrics': metrics,
        }

    return _inner


@pytest.fixture(scope='session')
def make_list_link_metrics_and_events_objects():
    def _inner(*link_metrics_and_events_objects: List[dict]):
        return list(link_metrics_and_events_objects)

    return _inner


@pytest.fixture(scope='session')
def make_serial_to_link_metrics_and_events_interface(make_link_status_and_metrics_object):
    def _inner(*, serials: list = None, interfaces: list = None, **kwargs):
        serials = serials or []
        interfaces = interfaces or []
        make_link_status_and_metrics = defaultdict(lambda: defaultdict(dict))

        for serial in serials:
            for interface in interfaces:
                make_link_status_and_metrics_object[serial].append(make_link_metrics_and_events_object(**kwargs))

        return make_link_status_and_metrics

    return _inner


@pytest.fixture(scope='session')
def make_events_by_serial_and_interface():
    def _inner(*, serials: list = None, interfaces: list = None):
        serials = serials or []
        interfaces = interfaces or []
        events = defaultdict(lambda: defaultdict(list))

        for serial in serials:
            for interface in interfaces:
                events[serial][interface] = []

        return events

    return _inner
