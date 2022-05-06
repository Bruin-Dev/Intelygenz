import os
from datetime import datetime
from typing import Callable, Pattern, List

from dateutil.parser import parse
from pytz import utc

from application import REOPEN_NOTE_REGEX


class UtilsRepository:
    @staticmethod
    def get_first_element_matching(iterable, condition: Callable, fallback=None):
        try:
            return next(elem for elem in iterable if condition(elem))
        except StopIteration:
            return fallback

    def get_last_element_matching(self, iterable, condition: Callable, fallback=None):
        return self.get_first_element_matching(reversed(iterable), condition, fallback)

    def has_last_event_happened_recently(self, ticket_notes: list, documentation_cycle_start_date: str,
                                         max_seconds_since_last_event: int, note_regex: Pattern[str]) -> bool:
        current_datetime = datetime.now(utc)

        notes_sorted_by_date_asc = sorted(ticket_notes, key=lambda note: note['createdDate'])
        last_event_note = self.get_last_element_matching(
            notes_sorted_by_date_asc,
            lambda note: note_regex.match(note['noteValue'])
        )
        if last_event_note:
            note_creation_date = parse(last_event_note['createdDate']).astimezone(utc)
            seconds_elapsed_since_last_event = (current_datetime - note_creation_date).total_seconds()
            return seconds_elapsed_since_last_event <= max_seconds_since_last_event

        documentation_cycle_start_datetime = parse(documentation_cycle_start_date).replace(tzinfo=utc)
        seconds_elapsed_since_last_event = (current_datetime - documentation_cycle_start_datetime).total_seconds()
        return seconds_elapsed_since_last_event <= max_seconds_since_last_event

    def get_notes_appended_since_latest_reopen_or_ticket_creation(self, ticket_notes: List[dict]) -> List[dict]:
        ticket_notes_sorted_by_date_asc = sorted(ticket_notes, key=lambda note: note['createdDate'])
        latest_reopen = self.get_last_element_matching(
            ticket_notes_sorted_by_date_asc,
            lambda note: REOPEN_NOTE_REGEX.search(note['noteValue'])
        )
        if not latest_reopen:
            # If there's no re-open, all notes in the ticket are the ones posted since the last outage
            return ticket_notes

        latest_reopen_position = ticket_notes.index(latest_reopen)
        return ticket_notes[latest_reopen_position:]

    def build_reminder_note(self) -> str:
        note_lines = [
            "#*MetTel's IPA*#",
            'Client Reminder'
        ]

        return os.linesep.join(note_lines)
