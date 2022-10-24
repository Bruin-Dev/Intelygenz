import json
from typing import Any, Callable


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


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
