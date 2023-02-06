from datetime import datetime
from ipaddress import ip_address
from typing import Callable, Pattern

from application import EVENT_INTERFACE_REGEX
from dateutil.parser import parse
from pytz import utc


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
            return f"{round((bps / 1000), 3)} Kbps"
        if 1000000 <= bps < 1000000000:
            return f"{round((bps / 1000000), 3)} Mbps"
        if bps >= 1000000000:
            return f"{round((bps / 1000000000), 3)} Gbps"

        return f"{round(bps, 3)} bps"

    @staticmethod
    def humanize_bps_for_bandwidth_report(bps: int) -> str:
        return f"{round((bps / 1000000), 3):.3f} Mbps"

    @staticmethod
    def convert_bytes_to_bps(byte, time):
        return (byte * 8) / time

    @staticmethod
    def get_interface_from_event(event):
        match = EVENT_INTERFACE_REGEX.match(event["message"])
        return match.group("interface") or match.group("link_interface")

    @staticmethod
    def is_ip_address(string: str) -> bool:
        try:
            return bool(ip_address(string))
        except ValueError:
            return False

    def has_last_event_happened_recently(
        self,
        ticket_notes: list,
        documentation_cycle_start_date: str,
        max_seconds_since_last_event: int,
        regex: Pattern[str],
    ) -> bool:
        current_datetime = datetime.now(utc)

        notes_sorted_by_date_asc = sorted(ticket_notes, key=lambda note: note["createdDate"])

        last_event_note = self.get_last_element_matching(
            notes_sorted_by_date_asc, lambda note: regex.search(note["noteValue"])
        )
        if last_event_note:
            note_creation_date = parse(last_event_note["createdDate"]).astimezone(utc)
            seconds_elapsed_since_last_affecting_event = (current_datetime - note_creation_date).total_seconds()
            return seconds_elapsed_since_last_affecting_event <= max_seconds_since_last_event

        documentation_cycle_start_datetime = parse(documentation_cycle_start_date).replace(tzinfo=utc)
        seconds_elapsed_since_last_affecting_event = (
            current_datetime - documentation_cycle_start_datetime
        ).total_seconds()
        return seconds_elapsed_since_last_affecting_event <= max_seconds_since_last_event

    @staticmethod
    def get_is_wireless_link(interface: str, links_configuration: list[dict]) -> bool:
        link_interface_type = ""
        for link_configuration in links_configuration:
            if interface in link_configuration["interfaces"]:
                link_interface_type = link_configuration["type"]

        return link_interface_type == "WIRELESS"

    @staticmethod
    def threshold_metric_to_use(is_wireless_link: bool) -> str:
        return "wireless_thresholds" if is_wireless_link else "thresholds"

    @staticmethod
    def monitoring_minutes_per_trouble_metric_to_use(is_wireless_link: bool) -> str:
        return "wireless_monitoring_minutes_per_trouble" if is_wireless_link else "monitoring_minutes_per_trouble"
