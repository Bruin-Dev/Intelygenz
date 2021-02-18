import datetime

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

    def find_dispatch_number_watermark_ok_old_watermark_test(self, ticket_details):
        dispatch_number = "DIS37561"
        watermark = '#*Automation Engine*#'
        dispatch_note = ticket_details['body']["ticketNotes"][1]

        result = UtilsRepository.find_dispatch_number_watermark(dispatch_note, dispatch_number, watermark)

        assert result == dispatch_number

    def find_dispatch_number_watermark_ko_old_watermark_test(self, ticket_details):
        dispatch_number = "DIS37405"
        watermark = '#*Automation Engine*#'
        dispatch_note = ticket_details['body']["ticketNotes"][2]

        result = UtilsRepository.find_dispatch_number_watermark(dispatch_note, dispatch_number, watermark)

        assert result == ''

    def find_dispatch_number_wrong_dispatch_number_ko_old_watermark_test(self, ticket_details):
        dispatch_number = "DIS123"
        watermark = '#*Automation Engine*#'
        dispatch_note = ticket_details['body']["ticketNotes"][1]

        result = UtilsRepository.find_dispatch_number_watermark(dispatch_note, dispatch_number, watermark)

        assert result == ''

    def find_dispatch_number_watermark_ok_test(self, ticket_details):
        dispatch_number = "DIS37561"
        watermark = "#*MetTel's IPA*#"
        dispatch_note = ticket_details['body']["ticketNotes"][3]

        result = UtilsRepository.find_dispatch_number_watermark(dispatch_note, dispatch_number, watermark)

        assert result == dispatch_number

    def find_dispatch_number_watermark_ko_test(self, ticket_details):
        dispatch_number = "DIS37405"
        watermark = "#*MetTel's IPA*#"
        dispatch_note = ticket_details['body']["ticketNotes"][2]

        result = UtilsRepository.find_dispatch_number_watermark(dispatch_note, dispatch_number, watermark)

        assert result == ''

    def find_dispatch_number_wrong_dispatch_number_ko_test(self, ticket_details):
        dispatch_number = "DIS123"
        watermark = "#*MetTel's IPA*#"
        dispatch_note = ticket_details['body']["ticketNotes"][3]

        result = UtilsRepository.find_dispatch_number_watermark(dispatch_note, dispatch_number, watermark)

        assert result == ''
