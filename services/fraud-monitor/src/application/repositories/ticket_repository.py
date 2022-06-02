import re
from typing import List

FRAUD_NOTE_REGEX = re.compile(r"^#\*MetTel's IPA\*#\nPossible Fraud Warning")
REOPEN_NOTE_REGEX = re.compile(r"^#\*MetTel's IPA\*#\nRe-opening ticket")
MSG_UID_REGEX = re.compile(r"Email UID: (?P<uid>\d+)")


class TicketRepository:
    def __init__(self, utils_repository):
        self._utils_repository = utils_repository

    @staticmethod
    def is_task_resolved(ticket_task: dict) -> bool:
        return ticket_task["detailStatus"] == "R"

    def is_fraud_ticket(self, ticket_notes: List[dict]) -> bool:
        if not ticket_notes:
            return True

        fraud_note = self._utils_repository.get_first_element_matching(
            ticket_notes, lambda note: FRAUD_NOTE_REGEX.search(note["noteValue"])
        )

        return fraud_note is not None

    def find_task(self, ticket_tasks: List[dict], service_number: str) -> dict:
        return self._utils_repository.get_first_element_matching(
            ticket_tasks,
            lambda detail: detail["detailValue"] == service_number,
        )

    def get_latest_notes(self, ticket_notes: List[dict]) -> List[dict]:
        ticket_notes_sorted_by_date_asc = sorted(ticket_notes, key=lambda note: note["createdDate"])

        latest_reopen_note = self._utils_repository.get_last_element_matching(
            ticket_notes_sorted_by_date_asc, lambda note: REOPEN_NOTE_REGEX.search(note["noteValue"])
        )

        if not latest_reopen_note:
            return ticket_notes

        latest_reopen_index = ticket_notes.index(latest_reopen_note)
        return ticket_notes[latest_reopen_index:]

    @staticmethod
    def note_already_exists(ticket_notes: List[dict], msg_uid: str) -> bool:
        for ticket_note in ticket_notes:
            msg_uid_match = MSG_UID_REGEX.search(ticket_note["noteValue"])

            if msg_uid_match and msg_uid_match.group("uid") == msg_uid:
                return True

        return False
