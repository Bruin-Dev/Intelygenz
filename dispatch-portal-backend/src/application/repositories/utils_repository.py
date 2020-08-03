from typing import Callable


class UtilsRepository:
    FULL_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f %Z%z'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M %Z'

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
