from application.repositories.utils_repository import UtilsRepository


class TestUtilsRepository:
    def get_first_element_matching_with_match_test(self):
        payload = range(0, 11)

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = UtilsRepository.get_first_element_matching(iterable=payload, condition=cond)
        expected = 5

        assert result == expected

    def get_first_element_matching_with_no_match_test(self):
        payload = [0] * 10
        fallback_value = 42

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = UtilsRepository.get_first_element_matching(iterable=payload, condition=cond, fallback=fallback_value)

        assert result == fallback_value

    def get_last_element_matching_with_match_test(self):
        payload = range(0, 11)

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = UtilsRepository.get_last_element_matching(iterable=payload, condition=cond)
        expected = 10

        assert result == expected

    def get_last_element_matching_with_no_match_test(self):
        payload = [0] * 10
        fallback_value = 42

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = UtilsRepository.get_last_element_matching(iterable=payload, condition=cond, fallback=fallback_value)

        assert result == fallback_value

    def truncate_float_test(self):
        float_ = 1.0
        result = UtilsRepository.truncate_float(float_, decimals=0)
        expected = 1.0
        assert result == expected

        float_ = 1.0
        result = UtilsRepository.truncate_float(float_, decimals=3)
        expected = 1.0
        assert result == expected

        float_ = 1.03865346785687
        result = UtilsRepository.truncate_float(float_, decimals=6)
        expected = 1.038653
        assert result == expected

        float_ = 1.03800000005687
        result = UtilsRepository.truncate_float(float_, decimals=6)
        expected = 1.038
        assert result == expected
