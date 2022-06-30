from typing import Callable


class UtilsRepository:
    @staticmethod
    def get_first_element_matching(iterable, condition: Callable, fallback=None):
        try:
            return next(elem for elem in iterable if condition(elem))
        except StopIteration:
            return fallback

    def get_last_element_matching(self, iterable, condition: Callable, fallback=None):
        return self.get_first_element_matching(reversed(iterable), condition, fallback)
