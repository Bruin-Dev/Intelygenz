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
    def truncate_float(num: float, decimals: int) -> float:
        num = str(num)
        floating_point_index = num.index('.')

        integer_part = num[0:floating_point_index]
        decimal_part_fixed = num[floating_point_index + 1: floating_point_index + decimals + 1]
        fixed_float = float(f'{integer_part}.{decimal_part_fixed}')
        return fixed_float
