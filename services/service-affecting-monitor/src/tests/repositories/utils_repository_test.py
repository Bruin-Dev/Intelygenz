import re
from datetime import datetime

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
        expected = "0 bps"
        assert result == expected

        bps = int(10e0)
        result = UtilsRepository.humanize_bps(bps)
        expected = "10 bps"
        assert result == expected

        bps = int(10e2)
        result = UtilsRepository.humanize_bps(bps)
        expected = "1.0 Kbps"
        assert result == expected

        bps = int(10e5)
        result = UtilsRepository.humanize_bps(bps)
        expected = "1.0 Mbps"
        assert result == expected

        bps = int(10e8)
        result = UtilsRepository.humanize_bps(bps)
        expected = "1.0 Gbps"
        assert result == expected

        bps = int(10e14)
        result = UtilsRepository.humanize_bps(bps)
        expected = "1000000.0 Gbps"
        assert result == expected

    def convert_bytes_to_bps_test(self):
        time = 86400
        byte = 0
        result = UtilsRepository.convert_bytes_to_bps(byte, time)
        expected = 0
        assert result == expected

        byte = 10800
        result = UtilsRepository.convert_bytes_to_bps(byte, time)
        expected = 1
        assert result == expected

        byte = 86400
        result = UtilsRepository.convert_bytes_to_bps(byte, time)
        expected = 8
        assert result == expected

    def get_interface_from_event_test(self):
        event = {"message": "Link GE1 is now DEAD"}
        result = UtilsRepository.get_interface_from_event(event)
        expected = "GE1"
        assert result == expected

        event = {"message": "Interface GE1 is down"}
        result = UtilsRepository.get_interface_from_event(event)
        expected = "GE1"
        assert result == expected

    def is_ip_address_test(self):
        result = UtilsRepository.is_ip_address("Some random text")
        expected = False
        assert result == expected

        result = UtilsRepository.is_ip_address("127.0.0.1")
        expected = True
        assert result == expected

    def has_last_event_happened_recently_test(self, make_ticket_note, make_list_of_ticket_notes):
        ticket_creation_date = datetime.now()
        note_1 = make_ticket_note(text="Dummy note")
        note_2 = make_ticket_note(text="Dummy note 2")
        notes = make_list_of_ticket_notes(note_1, note_2)
        utils_repository = UtilsRepository()

        result = utils_repository.has_last_event_happened_recently(
            notes, ticket_creation_date, max_seconds_since_last_event=3600, regex=re.compile(r"(^Dummy)")
        )

        assert result is True

    def get_is_wireless_link_test(self):
        interface = "GE1"
        links_configuration = [{"interfaces": ["GE1"], "type": "WIRELESS"}]
        result = UtilsRepository.get_is_wireless_link(interface, links_configuration)
        expected = True
        assert result == expected

        interface = "GE1"
        links_configuration = [{"interfaces": ["GE1"], "type": "WIRED"}]
        result = UtilsRepository.get_is_wireless_link(interface, links_configuration)
        expected = False
        assert result == expected

    def threshold_metric_to_use_test(self):
        is_wireless_link = True
        result = UtilsRepository.threshold_metric_to_use(is_wireless_link)
        expected = "wireless_thresholds"
        assert result == expected

        is_wireless_link = False
        result = UtilsRepository.threshold_metric_to_use(is_wireless_link)
        expected = "thresholds"
        assert result == expected
