from typing import Callable


class UtilsRepository:
    FULL_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f %Z%z'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S %Z'

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
        if datetime_1 > datetime_2:
            td = datetime_1 - datetime_2
        else:
            td = datetime_2 - datetime_1
        td_mins = float(round(td.total_seconds() / 60, 2))
        td_hours = td_mins / 60
        return round(td_hours, 2)

    @staticmethod
    def in_range(number: float, start: float, end: float):
        return start <= number < end

    @staticmethod
    def find_note(ticket_notes, watermark):
        return UtilsRepository.get_first_element_matching(
            iterable=ticket_notes,
            condition=lambda note: watermark in note.get('noteValue'),
            fallback=None
        )

    @staticmethod
    def find_dispatch_number_watermark(dispatch_number_note, dispatch_number, watermark):
        if dispatch_number_note and dispatch_number_note.get('noteValue'):
            lines = dispatch_number_note.get('noteValue').splitlines()
            for line in lines:
                if watermark in line:
                    dispatch_number_line = line.replace(
                        f"{watermark} ", "").strip().replace(" ", "")
                    if dispatch_number in dispatch_number_line:
                        return dispatch_number_line
        return ''
