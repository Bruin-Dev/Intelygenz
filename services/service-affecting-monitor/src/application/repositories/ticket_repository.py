import os
from datetime import datetime
from typing import Callable, List, Optional

from application import (
    AFFECTING_NOTE_REGEX,
    AUTORESOLVE_NOTE_REGEX,
    NOTE_REGEX_BY_TROUBLE,
    REOPEN_NOTE_REGEX,
    AffectingTroubles,
)
from pytz import timezone


class TicketRepository:
    def __init__(self, config, trouble_repository, utils_repository):
        self._config = config
        self._trouble_repository = trouble_repository
        self._utils_repository = utils_repository

    @staticmethod
    def is_task_resolved(ticket_task: dict) -> bool:
        return ticket_task["detailStatus"] == "R"

    def was_ticket_created_by_automation_engine(self, ticket: dict) -> bool:
        return ticket["createdBy"] == self._config.IPA_SYSTEM_USERNAME_IN_BRUIN

    def is_autoresolve_threshold_maxed_out(self, ticket_notes: list) -> bool:
        autoresolve_notes = [note for note in ticket_notes if AUTORESOLVE_NOTE_REGEX.match(note["noteValue"])]
        return len(autoresolve_notes) >= self._config.MONITOR_CONFIG["autoresolve"]["max_autoresolves"]

    def get_notes_appended_since_latest_reopen_or_ticket_creation(self, ticket_notes: List[dict]) -> List[dict]:
        ticket_notes_sorted_by_date_asc = sorted(ticket_notes, key=lambda note: note["createdDate"])
        latest_reopen = self._utils_repository.get_last_element_matching(
            ticket_notes_sorted_by_date_asc, lambda note: REOPEN_NOTE_REGEX.search(note["noteValue"])
        )
        if not latest_reopen:
            # If there's no re-open, all notes in the ticket are the ones posted since the last Affecting trouble
            return ticket_notes

        latest_reopen_position = ticket_notes.index(latest_reopen)
        return ticket_notes[latest_reopen_position:]

    def get_affecting_trouble_note(self, ticket_notes: List[dict]) -> Optional[dict]:
        return self._utils_repository.get_first_element_matching(
            ticket_notes, lambda note: AFFECTING_NOTE_REGEX.match(note["noteValue"])
        )

    def find_task_by_serial_number(self, ticket_tasks: List[dict], serial_number: str) -> dict:
        return self._utils_repository.get_first_element_matching(
            ticket_tasks,
            lambda detail: detail["detailValue"] == serial_number,
        )

    def is_ticket_used_for_reoccurring_affecting_troubles(self, ticket_notes: List[dict]) -> bool:
        affecting_trouble_note = self.get_affecting_trouble_note(ticket_notes)
        return affecting_trouble_note is not None

    def is_there_any_note_for_trouble(self, ticket_notes: List[dict], trouble: AffectingTroubles) -> bool:
        affecting_trouble_note = self._utils_repository.get_first_element_matching(
            ticket_notes, lambda note: NOTE_REGEX_BY_TROUBLE[trouble].search(note["noteValue"])
        )
        return affecting_trouble_note is not None

    def are_there_any_other_troubles(self, ticket_notes: list, observed_trouble: AffectingTroubles) -> bool:
        for trouble in AffectingTroubles:
            if trouble is observed_trouble:
                continue
            if self.is_there_any_note_for_trouble(ticket_notes, trouble):
                return True
        return False

    def get_build_note_fn_by_trouble(self, trouble: AffectingTroubles) -> Callable:
        if trouble is AffectingTroubles.LATENCY:
            return self.build_latency_trouble_note
        elif trouble is AffectingTroubles.PACKET_LOSS:
            return self.build_packet_loss_trouble_note
        elif trouble is AffectingTroubles.JITTER:
            return self.build_jitter_trouble_note
        elif trouble is AffectingTroubles.BANDWIDTH_OVER_UTILIZATION:
            return self.build_bandwidth_trouble_note
        elif trouble is AffectingTroubles.BOUNCING:
            return self.build_bouncing_trouble_note

    def build_latency_trouble_note(self, link_data: dict, is_wireless_link: bool,
                                   *, is_reopen_note: bool = False) -> str:
        edge_status = link_data["edge_status"]
        link_metrics = link_data["link_metrics"]

        edge_cached_info = link_data["cached_info"]
        links_configuration = edge_cached_info["links_configuration"]

        link_status = link_data["link_status"]
        link_interface = link_status["interface"]

        trouble = AffectingTroubles.LATENCY
        scan_interval = self._config.MONITOR_CONFIG[self._utils_repository.monitoring_minutes_per_trouble_metric_to_use(
            is_wireless_link)][trouble]
        metrics_threshold = self._config.MONITOR_CONFIG[self._utils_repository.threshold_metric_to_use(
            is_wireless_link)][trouble]

        edge_full_id = edge_cached_info["edge"]
        velocloud_base_url = (
            f'https://{edge_full_id["host"]}/#!/operator/customer/{edge_full_id["enterprise_id"]}/monitor'
        )
        velocloud_edge_base_url = f'{velocloud_base_url}/edge/{edge_full_id["edge_id"]}'

        note_lines = [
            "#*MetTel's IPA*#",
        ]

        if is_reopen_note:
            note_lines += [
                "Re-opening ticket.",
                "",
            ]

        link_config = self._utils_repository.get_first_element_matching(
            links_configuration,
            lambda config: link_interface in config["interfaces"],
        )
        if link_config:
            link_interface_type = f"{link_config['mode'].capitalize()} {link_config['type'].capitalize()}"
        else:
            link_interface_type = "Unknown"

        note_lines += [
            f"Trouble: {trouble.value}",
            "",
            f'Edge Name: {edge_status["edgeName"]}',
            f'Name: {link_status["displayName"]}',
            f'Interface: {link_status["interface"]}',
            f'IP Address: {link_status["linkIpAddress"]}',
            f"Link Type: {link_interface_type}",
            "",
            f"Interval for Scan: {scan_interval} minutes",
            f"Threshold: {metrics_threshold} ms",
        ]

        if not self._trouble_repository.is_latency_rx_within_threshold(link_metrics, is_wireless_link):
            note_lines.append(f'Receive: {link_metrics["bestLatencyMsRx"]} ms')

        if not self._trouble_repository.is_latency_tx_within_threshold(link_metrics, is_wireless_link):
            note_lines.append(f'Transfer: {link_metrics["bestLatencyMsTx"]} ms')

        note_lines += [
            "",
            f"Scan Time: {datetime.now(timezone(self._config.TIMEZONE))}",
            (
                "Links: "
                f"[Edge|{velocloud_edge_base_url}/] - [QoE|{velocloud_edge_base_url}/qoe/] - "
                f"[Transport|{velocloud_edge_base_url}/links/] - [Events|{velocloud_base_url}/events/]"
            ),
        ]
        return os.linesep.join(note_lines)

    def build_packet_loss_trouble_note(self, link_data: dict, is_wireless_link: bool,
                                       *, is_reopen_note: bool = False) -> str:
        edge_status = link_data["edge_status"]
        link_metrics = link_data["link_metrics"]

        edge_cached_info = link_data["cached_info"]
        links_configuration = edge_cached_info["links_configuration"]

        link_status = link_data["link_status"]
        link_interface = link_status["interface"]

        trouble = AffectingTroubles.PACKET_LOSS
        scan_interval = self._config.MONITOR_CONFIG[self._utils_repository.monitoring_minutes_per_trouble_metric_to_use(
            is_wireless_link)][trouble]
        metrics_threshold = self._config.MONITOR_CONFIG[self._utils_repository.threshold_metric_to_use(
            is_wireless_link)][trouble]

        edge_full_id = edge_cached_info["edge"]
        velocloud_base_url = (
            f'https://{edge_full_id["host"]}/#!/operator/customer/{edge_full_id["enterprise_id"]}/monitor'
        )
        velocloud_edge_base_url = f'{velocloud_base_url}/edge/{edge_full_id["edge_id"]}'

        note_lines = [
            "#*MetTel's IPA*#",
        ]

        if is_reopen_note:
            note_lines += [
                "Re-opening ticket.",
                "",
            ]

        link_config = self._utils_repository.get_first_element_matching(
            links_configuration,
            lambda config: link_interface in config["interfaces"],
        )
        if link_config:
            link_interface_type = f"{link_config['mode'].capitalize()} {link_config['type'].capitalize()}"
        else:
            link_interface_type = "Unknown"

        note_lines += [
            f"Trouble: {trouble.value}",
            "",
            f'Edge Name: {edge_status["edgeName"]}',
            f'Name: {link_status["displayName"]}',
            f'Interface: {link_status["interface"]}',
            f'IP Address: {link_status["linkIpAddress"]}',
            f"Link Type: {link_interface_type}",
            "",
            f"Interval for Scan: {scan_interval} minutes",
            f"Threshold: {metrics_threshold} packets",
        ]

        if not self._trouble_repository.is_packet_loss_rx_within_threshold(link_metrics, is_wireless_link):
            note_lines.append(f'Receive: {link_metrics["bestLossPctRx"]} packets')

        if not self._trouble_repository.is_packet_loss_tx_within_threshold(link_metrics, is_wireless_link):
            note_lines.append(f'Transfer: {link_metrics["bestLossPctTx"]} packets')

        note_lines += [
            "",
            f"Scan Time: {datetime.now(timezone(self._config.TIMEZONE))}",
            (
                "Links: "
                f"[Edge|{velocloud_edge_base_url}/] - [QoE|{velocloud_edge_base_url}/qoe/] - "
                f"[Transport|{velocloud_edge_base_url}/links/] - [Events|{velocloud_base_url}/events/]"
            ),
        ]
        return os.linesep.join(note_lines)

    def build_jitter_trouble_note(self, link_data: dict, is_wireless_link: bool,
                                  *, is_reopen_note: bool = False) -> str:
        edge_status = link_data["edge_status"]
        link_metrics = link_data["link_metrics"]

        edge_cached_info = link_data["cached_info"]
        links_configuration = edge_cached_info["links_configuration"]

        link_status = link_data["link_status"]
        link_interface = link_status["interface"]

        trouble = AffectingTroubles.JITTER
        scan_interval = self._config.MONITOR_CONFIG[self._utils_repository.monitoring_minutes_per_trouble_metric_to_use(
            is_wireless_link)][trouble]
        metrics_threshold = self._config.MONITOR_CONFIG[self._utils_repository.threshold_metric_to_use(
            is_wireless_link)][trouble]

        edge_full_id = edge_cached_info["edge"]
        velocloud_base_url = (
            f'https://{edge_full_id["host"]}/#!/operator/customer/{edge_full_id["enterprise_id"]}/monitor'
        )
        velocloud_edge_base_url = f'{velocloud_base_url}/edge/{edge_full_id["edge_id"]}'

        note_lines = [
            "#*MetTel's IPA*#",
        ]

        if is_reopen_note:
            note_lines += [
                "Re-opening ticket.",
                "",
            ]

        link_config = self._utils_repository.get_first_element_matching(
            links_configuration,
            lambda config: link_interface in config["interfaces"],
        )
        if link_config:
            link_interface_type = f"{link_config['mode'].capitalize()} {link_config['type'].capitalize()}"
        else:
            link_interface_type = "Unknown"

        note_lines += [
            f"Trouble: {trouble.value}",
            "",
            f'Edge Name: {edge_status["edgeName"]}',
            f'Name: {link_status["displayName"]}',
            f'Interface: {link_status["interface"]}',
            f'IP Address: {link_status["linkIpAddress"]}',
            f"Link Type: {link_interface_type}",
            "",
            f"Interval for Scan: {scan_interval} minutes",
            f"Threshold: {metrics_threshold} ms",
        ]

        if not self._trouble_repository.is_jitter_rx_within_threshold(link_metrics, is_wireless_link):
            note_lines.append(f'Receive: {link_metrics["bestJitterMsRx"]} ms')

        if not self._trouble_repository.is_jitter_tx_within_threshold(link_metrics, is_wireless_link):
            note_lines.append(f'Transfer: {link_metrics["bestJitterMsTx"]} ms')

        note_lines += [
            "",
            f"Scan Time: {datetime.now(timezone(self._config.TIMEZONE))}",
            (
                "Links: "
                f"[Edge|{velocloud_edge_base_url}/] - [QoE|{velocloud_edge_base_url}/qoe/] - "
                f"[Transport|{velocloud_edge_base_url}/links/] - [Events|{velocloud_base_url}/events/]"
            ),
        ]
        return os.linesep.join(note_lines)

    def build_bandwidth_trouble_note(self, link_data: dict, is_wireless_link: bool,
                                     *, is_reopen_note: bool = False) -> str:
        edge_status = link_data["edge_status"]
        link_metrics = link_data["link_metrics"]

        edge_cached_info = link_data["cached_info"]
        links_configuration = edge_cached_info["links_configuration"]

        link_status = link_data["link_status"]
        link_interface = link_status["interface"]

        trouble = AffectingTroubles.BANDWIDTH_OVER_UTILIZATION
        scan_interval = self._config.MONITOR_CONFIG[self._utils_repository.monitoring_minutes_per_trouble_metric_to_use(
            is_wireless_link)][trouble]
        metrics_threshold = self._config.MONITOR_CONFIG[self._utils_repository.threshold_metric_to_use(
            is_wireless_link)][trouble]

        edge_full_id = edge_cached_info["edge"]
        velocloud_base_url = (
            f'https://{edge_full_id["host"]}/#!/operator/customer/{edge_full_id["enterprise_id"]}/monitor'
        )
        velocloud_edge_base_url = f'{velocloud_base_url}/edge/{edge_full_id["edge_id"]}'

        note_lines = [
            "#*MetTel's IPA*#",
        ]

        if is_reopen_note:
            note_lines += [
                "Re-opening ticket.",
                "",
            ]

        link_config = self._utils_repository.get_first_element_matching(
            links_configuration,
            lambda config: link_interface in config["interfaces"],
        )
        if link_config:
            link_interface_type = f"{link_config['mode'].capitalize()} {link_config['type'].capitalize()}"
        else:
            link_interface_type = "Unknown"

        note_lines += [
            f"Trouble: {trouble.value}",
            "",
            f'Edge Name: {edge_status["edgeName"]}',
            f'Name: {link_status["displayName"]}',
            f'Interface: {link_status["interface"]}',
            f'IP Address: {link_status["linkIpAddress"]}',
            f"Link Type: {link_interface_type}",
            "",
            f"Interval for Scan: {scan_interval} minutes",
        ]

        rx_bandwidth = link_metrics["bpsOfBestPathRx"]
        if self._trouble_repository.is_valid_bps_metric(rx_bandwidth):
            if not self._trouble_repository.is_bandwidth_rx_within_threshold(
                    link_metrics, scan_interval, is_wireless_link):
                rx_throughput = self._trouble_repository.get_bandwidth_throughput_bps(
                    total_bytes=link_metrics["bytesRx"],
                    lookup_interval_minutes=scan_interval,
                )
                rx_threshold = (metrics_threshold / 100) * rx_bandwidth

                note_lines += [
                    f"Upload Throughput: {self._utils_repository.humanize_bps(rx_throughput)}",
                    f"Upload Bandwidth: {self._utils_repository.humanize_bps(rx_bandwidth)}",
                    f"Upload Threshold: {metrics_threshold}% ({self._utils_repository.humanize_bps(rx_threshold)})",
                ]

        tx_bandwidth = link_metrics["bpsOfBestPathTx"]
        if self._trouble_repository.is_valid_bps_metric(tx_bandwidth):
            if not self._trouble_repository.is_bandwidth_tx_within_threshold(
                    link_metrics, scan_interval, is_wireless_link):
                tx_throughput = self._trouble_repository.get_bandwidth_throughput_bps(
                    total_bytes=link_metrics["bytesTx"],
                    lookup_interval_minutes=scan_interval,
                )
                tx_threshold = (metrics_threshold / 100) * tx_bandwidth

                note_lines += [
                    f"Download Throughput: {self._utils_repository.humanize_bps(tx_throughput)}",
                    f"Download Bandwidth: {self._utils_repository.humanize_bps(tx_bandwidth)}",
                    f"Download Threshold: {metrics_threshold}% ({self._utils_repository.humanize_bps(tx_threshold)})",
                ]

        note_lines += [
            "",
            f"Scan Time: {datetime.now(timezone(self._config.TIMEZONE))}",
            (
                "Links: "
                f"[Edge|{velocloud_edge_base_url}/] - [QoE|{velocloud_edge_base_url}/qoe/] - "
                f"[Transport|{velocloud_edge_base_url}/links/] - [Events|{velocloud_base_url}/events/]"
            ),
        ]
        return os.linesep.join(note_lines)

    def build_bouncing_trouble_note(self, link_data: dict, is_wireless_link: bool,
                                    *, is_reopen_note: bool = False) -> str:
        edge_status = link_data["edge_status"]
        link_events = link_data["link_events"]

        edge_cached_info = link_data["cached_info"]
        links_configuration = edge_cached_info["links_configuration"]

        link_status = link_data["link_status"]
        link_interface = link_status["interface"]

        trouble = AffectingTroubles.BOUNCING
        scan_interval = self._config.MONITOR_CONFIG[self._utils_repository.monitoring_minutes_per_trouble_metric_to_use(
            is_wireless_link)][trouble]
        metrics_threshold = self._config.MONITOR_CONFIG[self._utils_repository.threshold_metric_to_use(
            is_wireless_link)][trouble]

        edge_full_id = edge_cached_info["edge"]
        velocloud_base_url = (
            f'https://{edge_full_id["host"]}/#!/operator/customer/{edge_full_id["enterprise_id"]}/monitor'
        )
        velocloud_edge_base_url = f'{velocloud_base_url}/edge/{edge_full_id["edge_id"]}'

        note_lines = [
            "#*MetTel's IPA*#",
        ]

        if is_reopen_note:
            note_lines += [
                "Re-opening ticket.",
                "",
            ]

        link_config = self._utils_repository.get_first_element_matching(
            links_configuration,
            lambda config: link_interface in config["interfaces"],
        )
        if link_config:
            link_interface_type = f"{link_config['mode'].capitalize()} {link_config['type'].capitalize()}"
        else:
            link_interface_type = "Unknown"

        note_lines += [
            f"Trouble: {trouble.value}",
            "",
            f'Edge Name: {edge_status["edgeName"]}',
            f'Name: {link_status["displayName"]}',
            f'Interface: {link_status["interface"]}',
            f'IP Address: {link_status["linkIpAddress"]}',
            f"Link Type: {link_interface_type}",
            "",
            f"Interval for Scan: {scan_interval} minutes",
            f"Threshold: {metrics_threshold} events",
            f"Events: {len(link_events)}",
            "",
            f"Scan Time: {datetime.now(timezone(self._config.TIMEZONE))}",
            (
                "Links: "
                f"[Edge|{velocloud_edge_base_url}/] - "
                f"[QoE|{velocloud_edge_base_url}/qoe/] - "
                f"[Transport|{velocloud_edge_base_url}/links/]"
            ),
        ]

        return os.linesep.join(note_lines)

    def build_reminder_note(self) -> str:
        note_lines = ["#*MetTel's IPA*#", "Client Reminder"]

        return os.linesep.join(note_lines)

    @staticmethod
    def is_ticket_task_in_ipa_queue(ticket_task: dict) -> bool:
        return ticket_task["currentTaskName"] == "IPA Investigate"

    @staticmethod
    def is_ticket_task_assigned(ticket_task: dict) -> bool:
        assigned_to = ticket_task["assignedToName"]
        return assigned_to and not assigned_to.isspace() and assigned_to != "0"
