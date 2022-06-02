from typing import List

import pytest


# Factories
@pytest.fixture(scope="session")
def make_detail_item_with_notes_and_ticket_info(make_ticket, make_detail_item):
    def _inner(*, detail_item: dict = None, notes: List[dict] = None, ticket_info: dict = None):
        detail_item = detail_item or make_detail_item()
        ticket_info = ticket_info or make_ticket()
        notes = notes or []

        return {
            "ticket_overview": ticket_info,
            "ticket_task": detail_item,
            "ticket_notes": notes,
        }

    return _inner


@pytest.fixture(scope="session")
def make_list_of_ticket_notes():
    def _inner(*ticket_notes: List[dict]):
        return list(ticket_notes)

    return _inner
