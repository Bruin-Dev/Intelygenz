import re
from typing import Callable

EVENT_INTERFACE_REGEX = re.compile(
    r"(^Interface (?P<interface>[a-zA-Z0-9]+) is (up|down)$)|"
    r"(^Link (?P<link_interface>[a-zA-Z0-9]+) is (no longer|now) DEAD$)"
)


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
    def get_interface_from_event(event):
        match = EVENT_INTERFACE_REGEX.match(event["message"])
        return match.group("interface") or match.group("link_interface")
