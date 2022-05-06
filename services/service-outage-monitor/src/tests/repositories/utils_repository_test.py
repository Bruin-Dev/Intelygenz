import os
from datetime import timedelta

from tests.fixtures._constants import CURRENT_DATETIME


class TestUtilsRepository:
    def get_first_element_matching_with_match_test(self, utils_repository):
        payload = range(0, 11)
        expected = 5

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = utils_repository.get_first_element_matching(iterable=payload, condition=cond)

        assert result == expected

    def get_first_element_matching_with_no_match_test(self, utils_repository):
        payload = [0] * 10
        fallback_value = 42

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = utils_repository.get_first_element_matching(iterable=payload, condition=cond, fallback=fallback_value)

        assert result == fallback_value

    def get_last_element_matching_with_match_test(self, utils_repository):
        payload = range(0, 11)
        expected = 10

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = utils_repository.get_last_element_matching(iterable=payload, condition=cond)

        assert result == expected

    def get_last_element_matching_with_no_match_test(self, utils_repository):
        payload = [0] * 10
        fallback_value = 42

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = utils_repository.get_last_element_matching(iterable=payload, condition=cond, fallback=fallback_value)

        assert result == fallback_value

    def build_reminder_note_test(self, utils_repository):
        expected = os.linesep.join([
            "#*MetTel's IPA*#",
            'Client Reminder'
        ])

        result = utils_repository.build_reminder_note()

        assert result == expected

    def get_notes_appended_since_latest_reopen_or_ticket_creation__no_reopen_note_found_test(
        self, utils_repository, make_ticket_note, make_list_of_ticket_notes
    ):
        note_1 = make_ticket_note(text="Dummy note")
        note_2 = make_ticket_note(text=f"#*MetTel's IPA*#\nAuto-resolving task for serial: VC1234567")
        notes = make_list_of_ticket_notes(note_1, note_2)

        result = utils_repository.get_notes_appended_since_latest_reopen_or_ticket_creation(notes)

        assert result is notes

    def get_notes_appended_since_latest_reopen_or_ticket_creation__reopen_note_found_test(
        self, utils_repository, make_ticket_note, make_list_of_ticket_notes
    ):
        current_datetime = CURRENT_DATETIME
        note_1 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime - timedelta(seconds=10)))
        note_2 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nRe-opening ticket.\nTrouble: Latency",
            creation_date=str(current_datetime),
        )
        notes = make_list_of_ticket_notes(note_1, note_2)

        result = utils_repository.get_notes_appended_since_latest_reopen_or_ticket_creation(notes)

        assert result == [note_2]

        note_1 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime - timedelta(seconds=20)))
        note_2 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nRe-opening ticket.\nTrouble: Latency",
            creation_date=str(current_datetime - timedelta(seconds=10)),
        )
        note_3 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime))
        notes = make_list_of_ticket_notes(note_1, note_2, note_3)

        result = utils_repository.get_notes_appended_since_latest_reopen_or_ticket_creation(notes)

        assert result == [note_2, note_3]

        note_1 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime - timedelta(seconds=40)))
        note_2 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nRe-opening ticket.\nTrouble: Latency",
            creation_date=str(current_datetime - timedelta(seconds=30)),
        )
        note_3 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime - timedelta(seconds=20)))
        note_4 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nRe-opening ticket.\nTrouble: Latency",
            creation_date=str(current_datetime - timedelta(seconds=10)),
        )
        note_5 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime))
        note_6 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime))
        note_7 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime))
        notes = make_list_of_ticket_notes(note_1, note_2, note_3, note_4, note_5, note_6, note_7)

        result = utils_repository.get_notes_appended_since_latest_reopen_or_ticket_creation(notes)

        assert result == [note_4, note_5, note_6, note_7]
