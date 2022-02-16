from collections import defaultdict
from typing import List

import pytest


# Factories
@pytest.fixture(scope='session')
def make_edge_full_id():
    def _inner(*, host: str = '', enterprise_id: int = 0, edge_id: int = 0):
        return {
            'host': host,
            'enterprise_id': enterprise_id,
            'edge_id': edge_id,
        }

    return _inner


@pytest.fixture(scope='session')
def make_link_with_edge_info(make_edge, make_link):
    def _inner(*, link_info: dict = None, edge_info: dict = None):
        link_info = link_info or make_link()
        edge_info = edge_info or make_edge()

        return {
            **edge_info,
            **link_info,
        }

    return _inner


@pytest.fixture(scope='session')
def make_edge_with_links_info(make_edge):
    def _inner(*, edge_info: dict = None, links_info: List[dict] = None):
        links_info = links_info or []
        edge_info = edge_info or make_edge()

        return {
            **edge_info,
            'links': links_info,
        }

    return _inner


@pytest.fixture(scope='session')
def make_link_with_metrics(make_link, make_metrics):
    def _inner(*, link_info: dict = None, metrics: dict = None):
        link_info = link_info or make_link()
        metrics = metrics or make_metrics()

        return {
            **metrics,
            'link': link_info,
        }

    return _inner


@pytest.fixture(scope='session')
def make_list_of_links_with_metrics():
    def _inner(*links_with_metrics: List[dict]):
        return list(links_with_metrics)

    return _inner


@pytest.fixture(scope='session')
def make_structured_metrics_object(make_edge, make_link, make_metrics):
    def _inner(*, edge_info: dict = None, link_info: dict = None, metrics: dict = None):
        edge_info = edge_info or make_edge()
        link_info = link_info or make_link()
        metrics = metrics or make_metrics()

        return {
            'edge_status': edge_info,
            'link_status': link_info,
            'link_metrics': metrics,
        }

    return _inner


@pytest.fixture(scope='session')
def make_list_of_structured_metrics_objects():
    def _inner(*structured_metrics_objects: List[dict]):
        return list(structured_metrics_objects)

    return _inner


@pytest.fixture(scope='session')
def make_structured_metrics_object_with_events(make_structured_metrics_object):
    def _inner(*, events: list = None, **kwargs):
        result = make_structured_metrics_object(**kwargs)
        result['link_events'] = events or []
        return result

    return _inner


@pytest.fixture(scope='session')
def make_structured_metrics_object_with_cache_and_contact_info(make_structured_metrics_object, make_cached_edge):
    def _inner(*, metrics_object: dict = None, cache_info: dict = None, contact_info: dict = None):
        cache_info = cache_info or make_cached_edge()
        metrics_object = metrics_object or make_structured_metrics_object()
        contact_info = contact_info or {}

        return {
            'cached_info': cache_info,
            'contact_info': contact_info,
            **metrics_object,
        }

    return _inner


@pytest.fixture(scope='session')
def make_structured_metrics_object_with_cache_with_events_and_contact_info(make_structured_metrics_object_with_events,
                                                                           make_cached_edge):
    def _inner(*, metrics_object: dict = None, cache_info: dict = None, contact_info: dict = None):
        cache_info = cache_info or make_cached_edge()
        metrics_object = metrics_object or make_structured_metrics_object_with_events()
        contact_info = contact_info or {}

        return {
            'cached_info': cache_info,
            'contact_info': contact_info,
            **metrics_object,
        }

    return _inner


@pytest.fixture(scope='session')
def make_list_of_structured_metrics_objects_with_cache_and_contact_info():
    def _inner(*structured_metrics_objects: List[dict]):
        return list(structured_metrics_objects)

    return _inner


@pytest.fixture(scope='session')
def make_link_status_and_metrics_object(make_link, make_metrics):
    def _inner(*, link_info: dict = None, metrics: dict = None):
        link_info = link_info or make_link()
        metrics = metrics or make_metrics()

        return {
            'link_status': link_info,
            'link_metrics': metrics,
        }

    return _inner


@pytest.fixture(scope='session')
def make_link_status_and_metrics_object_with_events(make_link_status_and_metrics_object):
    def _inner(*, events: list = None, **kwargs):
        result = make_link_status_and_metrics_object(**kwargs)
        result['link_events'] = events or []
        return result

    return _inner


@pytest.fixture(scope='session')
def make_list_of_link_status_and_metrics_objects():
    def _inner(*link_status_and_metrics_objects: List[dict]):
        return list(link_status_and_metrics_objects)

    return _inner


@pytest.fixture(scope='session')
def make_links_by_edge_object(make_edge, make_cached_edge):
    def _inner(*, edge_info: dict = None, cache_info: dict = None, contact_info: dict = None, links: List[dict] = None):
        edge_info = edge_info or make_edge()
        cache_info = cache_info or make_cached_edge()
        contact_info = contact_info or {}
        links = links or []

        return {
            'cached_info': cache_info,
            'contact_info': contact_info,
            'edge_status': edge_info,
            'links': links,
        }

    return _inner


@pytest.fixture(scope='session')
def make_list_of_links_by_edge_objects():
    def _inner(*links_by_edge_objects: List[dict]):
        return list(links_by_edge_objects)

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


@pytest.fixture(scope='session')
def make_detail_item_with_notes_and_ticket_info(make_ticket, make_detail_item):
    def _inner(*, detail_item: dict = None, notes: List[dict] = None, ticket_info: dict = None):
        detail_item = detail_item or make_detail_item()
        ticket_info = ticket_info or make_ticket()
        notes = notes or []

        return {
            'ticket_overview': ticket_info,
            'ticket_task': detail_item,
            'ticket_notes': notes,
        }

    return _inner


@pytest.fixture(scope='session')
def make_list_of_tickets():
    def _inner(*tickets: List[dict]):
        return list(tickets)

    return _inner


@pytest.fixture(scope='session')
def make_list_of_detail_items():
    def _inner(*detail_items: List[dict]):
        return list(detail_items)

    return _inner


@pytest.fixture(scope='session')
def make_list_of_ticket_notes():
    def _inner(*ticket_notes: List[dict]):
        return list(ticket_notes)

    return _inner
