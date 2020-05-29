from typing import Callable


class UtilsRepository:
    @staticmethod
    def get_first_element_matching(iterable, condition: Callable, fallback=None):
        try:
            return next(elem for elem in iterable if condition(elem))
        except StopIteration:
            return fallback

    @staticmethod
    def get_last_element_matching(iterable, condition: Callable, fallback=None):
        return UtilsRepository.get_first_element_matching(reversed(iterable), condition, fallback)

    @staticmethod
    def get_diff_hours_between_datetimes(datetime_1, datetime_2):
        diff = datetime_1 - datetime_2

        days, seconds = diff.days, diff.seconds
        hours = days * 24 + seconds // 3600
        return hours

    @staticmethod
    def find_note(ticket_notes, watermark):
        return UtilsRepository.get_first_element_matching(
            iterable=ticket_notes,
            condition=lambda note: watermark in note.get('noteValue'),
            fallback=None
        )
