import os
import re

from datetime import datetime
from datetime import timedelta
from functools import partial
from typing import List

from dateutil.parser import parse
from pytz import utc


TNBA_NOTE_REGEX = re.compile(r"^#\*(Automation Engine|MetTel's IPA)\*#\n(TNBA|AI)")


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

    def has_tnba_note(self, ticket_notes: List[dict]) -> bool:
        return bool(self._utils_repository.get_first_element_matching(ticket_notes, self.is_tnba_note))

    def __lookup_fn_for_newest_tnba_note(self, ticket_note: dict, service_number: str) -> bool:
        return self.is_tnba_note(ticket_note) and service_number in ticket_note['serviceNumber']

    def find_newest_tnba_note_by_service_number(self, ticket_notes: List[dict], service_number: str) -> dict:
        # Ticket notes should have been sorted by "createdDate" already but let's make sure...
        ticket_notes = [elem for elem in ticket_notes if elem['createdDate']]
        ticket_notes = sorted(ticket_notes, key=lambda note: note['createdDate'])
        lookup_fn = partial(self.__lookup_fn_for_newest_tnba_note, service_number=service_number)
        return self._utils_repository.get_last_element_matching(ticket_notes, lookup_fn)

    @staticmethod
    def is_note_older_than(ticket_note: dict, age: timedelta) -> bool:
        current_datetime = datetime.now(utc)
        ticket_note_creation_datetime = parse(ticket_note['createdDate']).astimezone(utc)

        return (current_datetime - ticket_note_creation_datetime) >= age

    def is_tnba_note_old_enough(self, ticket_note: dict) -> bool:
        age = timedelta(minutes=self._config.MONITOR_CONFIG['tnba_notes_age_for_new_appends_in_minutes'])

        return self.is_note_older_than(ticket_note, age=age)

    @staticmethod
    def is_detail_in_outage_ticket(ticket_detail: dict) -> bool:
        return ticket_detail['ticket_topic'] == 'VOO'

    @staticmethod
    def was_ticket_created_by_automation_engine(ticket_detail: dict) -> bool:
        return ticket_detail['ticket_creator'] == 'Intelygenz Ai'

    @staticmethod
    def build_tnba_note_from_prediction(prediction: dict, serial_number: str) -> str:
        note_lines = [
            "#*MetTel's IPA*#",
            'AI',
            '',
            f"MetTel's IPA AI indicates that the next best action for {serial_number} is: {prediction['name']}.",
            '',
            "MetTel's IPA is based on an AI model designed specifically for MetTel.",
        ]
        return os.linesep.join(note_lines)

    @staticmethod
    def build_tnba_note_for_AI_autoresolve(serial_number: str) -> str:
        note_lines = [
            "#*MetTel's IPA*#",
            'AI',
            '',
            f"MetTel's IPA AI is resolving the task for {serial_number}.",
            '',
            "MetTel's IPA is based on an AI model designed specifically for MetTel.",
        ]
        return os.linesep.join(note_lines)
