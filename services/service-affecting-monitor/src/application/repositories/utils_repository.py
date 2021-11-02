from ipaddress import ip_address
from typing import Callable

from application import EVENT_INTERFACE_REGEX


class UtilsRepository:
    @staticmethod
    def get_first_element_matching(iterable, condition: Callable, fallback=None):
        try:
            return next(elem for elem in iterable if condition(elem))
        except StopIteration:
            return fallback

    def get_last_element_matching(self, iterable, condition: Callable, fallback=None):
        return self.get_first_element_matching(reversed(iterable), condition, fallback)

    @staticmethod
    def humanize_bps(bps: int) -> str:
        if 1000 <= bps < 1000000:
            return f'{round((bps / 1000), 3)} Kbps'
        if 1000000 <= bps < 1000000000:
            return f'{round((bps / 1000000), 3)} Mbps'
        if bps >= 1000000000:
            return f'{round((bps / 1000000000), 3)} Gbps'

        return f'{round(bps, 3)} bps'

    @staticmethod
    def get_interface_from_event(event):
        match = EVENT_INTERFACE_REGEX.match(event['message'])
        return match.group('interface') or match.group('link_interface')

    @staticmethod
    def is_ip_address(string: str) -> bool:
        try:
            return bool(ip_address(string))
        except ValueError:
            return False
