import os
import re

from datetime import datetime
from datetime import timedelta
from typing import List

from dateutil.parser import parse
from pytz import utc


TNBA_NOTE_REGEX = re.compile(r'^#\*Automation Engine\*#\nTNBA')


class TicketRepository:
    def __init__(self, config, utils_repository):
        self._config = config
        self._utils_repository = utils_repository

    @staticmethod
    def is_detail_resolved(ticket_detail: dict) -> bool:
        return ticket_detail['detailStatus'] == 'R'

    @staticmethod
    def is_tnba_note(ticket_note: dict) -> bool:
        return bool(TNBA_NOTE_REGEX.match(ticket_note['noteValue']))

    def find_newest_tnba_note(self, ticket_notes: List[dict]) -> dict:
        # Ticket notes should have been sorted by "createdDate" already but let's make sure...
        ticket_notes = sorted(ticket_notes, key=lambda note: note['createdDate'])
        return self._utils_repository.get_last_element_matching(ticket_notes, self.is_tnba_note)

    @staticmethod
    def is_note_older_than(ticket_note: dict, age: timedelta) -> bool:
        current_datetime = datetime.now(utc)
        ticket_note_creation_datetime = parse(ticket_note['createdDate']).astimezone(utc)

        return (current_datetime - ticket_note_creation_datetime) >= age

    def is_tnba_note_old_enough(self, ticket_note: dict) -> bool:
        age = timedelta(minutes=self._config.MONITOR_CONFIG['tnba_notes_age_for_new_appends_in_minutes'])

        return self.is_note_older_than(ticket_note, age=age)

    @staticmethod
    def build_tnba_note_from_predictions(predictions: List[dict]) -> str:
        note_lines = [
            '#*Automation Engine*#',
            'TNBA',
            '',
            'The following are the next best actions for this ticket with corresponding confidence levels:',
        ]

        for index, prediction in enumerate(predictions):
            line = f'{index + 1}) {prediction["name"]} | Confidence: {prediction["probability"] * 100} %'
            note_lines.append(line)

        return os.linesep.join(note_lines)
