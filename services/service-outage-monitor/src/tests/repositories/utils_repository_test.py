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
