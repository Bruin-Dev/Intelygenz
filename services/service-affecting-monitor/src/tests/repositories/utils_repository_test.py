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

        utils_repository = UtilsRepository()

        result = utils_repository.get_last_element_matching(iterable=payload, condition=cond)
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

        utils_repository = UtilsRepository()

        result = utils_repository.get_last_element_matching(iterable=payload, condition=cond, fallback=fallback_value)

        assert result == fallback_value

    def humanize_bps_test(self):
        bps = 0
        result = UtilsRepository.humanize_bps(bps)
        expected = '0 bps'
        assert result == expected

        bps = int(10e0)
        result = UtilsRepository.humanize_bps(bps)
        expected = '10 bps'
        assert result == expected

        bps = int(10e2)
        result = UtilsRepository.humanize_bps(bps)
        expected = '1.0 Kbps'
        assert result == expected

        bps = int(10e5)
        result = UtilsRepository.humanize_bps(bps)
        expected = '1.0 Mbps'
        assert result == expected

        bps = int(10e8)
        result = UtilsRepository.humanize_bps(bps)
        expected = '1.0 Gbps'
        assert result == expected

        bps = int(10e14)
        result = UtilsRepository.humanize_bps(bps)
        expected = '1000000.0 Gbps'
        assert result == expected

    def get_interface_from_event_test(self):
        event = {'message': 'Link GE1 is now DEAD'}
        result = UtilsRepository.get_interface_from_event(event)
        expected = 'GE1'
        assert result == expected

        event = {'message': 'Interface GE1 is down'}
        result = UtilsRepository.get_interface_from_event(event)
        expected = 'GE1'
        assert result == expected

    def is_ip_address_test(self):
        result = UtilsRepository.is_ip_address('Some random text')
        expected = False
        assert result == expected

        result = UtilsRepository.is_ip_address('127.0.0.1')
        expected = True
        assert result == expected
