import os
from datetime import datetime
from typing import Callable
from typing import List

from pytz import timezone

from application import AUTORESOLVE_NOTE_REGEX
from application import NOTE_REGEX_BY_TROUBLE
from application import REOPEN_NOTE_REGEX
from application import AffectingTroubles


class TicketRepository:
    def __init__(self, config, trouble_repository, utils_repository):
        self._config = config
        self._trouble_repository = trouble_repository
        self._utils_repository = utils_repository

    @staticmethod
    def is_task_resolved(ticket_task: dict) -> bool:
        return ticket_task['detailStatus'] == 'R'

    @staticmethod
    def was_ticket_created_by_automation_engine(ticket: dict) -> bool:
        return ticket['createdBy'] == 'Intelygenz Ai'

    def is_autoresolve_threshold_maxed_out(self, ticket_notes: list) -> bool:
        autoresolve_notes = [
            note
            for note in ticket_notes
            if AUTORESOLVE_NOTE_REGEX.match(note['noteValue'])
        ]
        return len(autoresolve_notes) >= self._config.MONITOR_CONFIG['autoresolve']['max_autoresolves']

    def get_notes_appended_since_latest_reopen_or_ticket_creation(self, ticket_notes: List[dict]) -> List[dict]:
        ticket_notes_sorted_by_date_asc = sorted(ticket_notes, key=lambda note: note['createdDate'])
        latest_reopen = self._utils_repository.get_last_element_matching(
            ticket_notes_sorted_by_date_asc,
            lambda note: REOPEN_NOTE_REGEX.search(note['noteValue'])
        )
        if not latest_reopen:
            # If there's no re-open, all notes in the ticket are the ones posted since the last Affecting trouble
            return ticket_notes

        latest_reopen_position = ticket_notes.index(latest_reopen)
        return ticket_notes[latest_reopen_position:]

    def find_task_by_serial_number(self, ticket_tasks: List[dict], serial_number: str) -> dict:
        return self._utils_repository.get_first_element_matching(
            ticket_tasks,
            lambda detail: detail['detailValue'] == serial_number,
        )

    def is_there_any_note_for_trouble(self, ticket_notes: List[dict], trouble: AffectingTroubles) -> bool:
        affecting_trouble_note = self._utils_repository.get_first_element_matching(
            ticket_notes,
            lambda note: NOTE_REGEX_BY_TROUBLE[trouble].search(note['noteValue'])
        )
        return affecting_trouble_note is not None

    def get_build_note_fn_by_trouble(self, trouble: AffectingTroubles) -> Callable:
        if trouble is AffectingTroubles.LATENCY:
            return self.build_latency_trouble_note
        elif trouble is AffectingTroubles.PACKET_LOSS:
            return self.build_packet_loss_trouble_note
        elif trouble is AffectingTroubles.JITTER:
            return self.build_jitter_trouble_note
        elif trouble is AffectingTroubles.BANDWIDTH_OVER_UTILIZATION:
            return self.build_bandwidth_trouble_note

    def build_latency_trouble_note(self, link_data: dict, *, is_reopen_note: bool = False) -> str:
        edge_status = link_data["edge_status"]
        link_metrics = link_data["link_metrics"]

        edge_cached_info = link_data["cached_info"]
        links_configuration = edge_cached_info['links_configuration']

        link_status = link_data["link_status"]
        link_interface = link_status['interface']

        trouble = AffectingTroubles.LATENCY
        scan_interval = self._config.MONITOR_CONFIG['monitoring_minutes_per_trouble'][trouble]
        metrics_threshold = self._config.MONITOR_CONFIG['thresholds'][trouble]

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
                'Re-opening ticket.',
                '',
            ]

        link_config = self._utils_repository.get_first_element_matching(
            links_configuration,
            lambda config: link_interface in config['interfaces'],
        )
        if link_config:
            link_interface_type = f"{link_config['mode'].capitalize()} {link_config['type'].capitalize()}"
        else:
            link_interface_type = "Unknown"

        note_lines += [
            f'Trouble: {trouble.value}',
            '',
            f'Edge Name: {edge_status["edgeName"]}',
            f'Name: {link_status["displayName"]}',
            f'Interface: {link_status["interface"]}',
            f'Link Type: {link_interface_type}',
            '',
            f'Interval for Scan: {scan_interval} minutes',
            f'Threshold: {metrics_threshold} ms',
        ]

        if not self._trouble_repository.is_latency_rx_within_threshold(link_metrics):
            note_lines.append(f'Receive: {link_metrics["bestLatencyMsRx"]} ms')

        if not self._trouble_repository.is_latency_tx_within_threshold(link_metrics):
            note_lines.append(f'Transfer: {link_metrics["bestLatencyMsTx"]} ms')

        note_lines += [
            '',
            f'Scan Time: {datetime.now(timezone(self._config.MONITOR_CONFIG["timezone"]))}',
            (
                'Links: '
                f'[Edge|{velocloud_edge_base_url}/] - [QoE|{velocloud_edge_base_url}/qoe/] - '
                f'[Transport|{velocloud_edge_base_url}/links/] - [Events|{velocloud_base_url}/events/]'
            ),
        ]
        return os.linesep.join(note_lines)

    def build_packet_loss_trouble_note(self, link_data: dict, *, is_reopen_note: bool = False) -> str:
        edge_status = link_data["edge_status"]
        link_metrics = link_data["link_metrics"]

        edge_cached_info = link_data["cached_info"]
        links_configuration = edge_cached_info['links_configuration']

        link_status = link_data["link_status"]
        link_interface = link_status['interface']

        trouble = AffectingTroubles.PACKET_LOSS
        scan_interval = self._config.MONITOR_CONFIG['monitoring_minutes_per_trouble'][trouble]
        metrics_threshold = self._config.MONITOR_CONFIG['thresholds'][trouble]

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
                'Re-opening ticket.',
                '',
            ]

        link_config = self._utils_repository.get_first_element_matching(
            links_configuration,
            lambda config: link_interface in config['interfaces'],
        )
        if link_config:
            link_interface_type = f"{link_config['mode'].capitalize()} {link_config['type'].capitalize()}"
        else:
            link_interface_type = "Unknown"

        note_lines += [
            f'Trouble: {trouble.value}',
            '',
            f'Edge Name: {edge_status["edgeName"]}',
            f'Name: {link_status["displayName"]}',
            f'Interface: {link_status["interface"]}',
            f'Link Type: {link_interface_type}',
            '',
            f'Interval for Scan: {scan_interval} minutes',
            f'Threshold: {metrics_threshold} packets',
        ]

        if not self._trouble_repository.is_packet_loss_rx_within_threshold(link_metrics):
            note_lines.append(f'Receive: {link_metrics["bestLossPctRx"]} packets')

        if not self._trouble_repository.is_packet_loss_tx_within_threshold(link_metrics):
            note_lines.append(f'Transfer: {link_metrics["bestLossPctTx"]} packets')

        note_lines += [
            '',
            f'Scan Time: {datetime.now(timezone(self._config.MONITOR_CONFIG["timezone"]))}',
            (
                'Links: '
                f'[Edge|{velocloud_edge_base_url}/] - [QoE|{velocloud_edge_base_url}/qoe/] - '
                f'[Transport|{velocloud_edge_base_url}/links/] - [Events|{velocloud_base_url}/events/]'
            ),
        ]
        return os.linesep.join(note_lines)

    def build_jitter_trouble_note(self, link_data: dict, *, is_reopen_note: bool = False) -> str:
        edge_status = link_data["edge_status"]
        link_metrics = link_data["link_metrics"]

        edge_cached_info = link_data["cached_info"]
        links_configuration = edge_cached_info['links_configuration']

        link_status = link_data["link_status"]
        link_interface = link_status['interface']

        trouble = AffectingTroubles.JITTER
        scan_interval = self._config.MONITOR_CONFIG['monitoring_minutes_per_trouble'][trouble]
        metrics_threshold = self._config.MONITOR_CONFIG['thresholds'][trouble]

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
                'Re-opening ticket.',
                '',
            ]

        link_config = self._utils_repository.get_first_element_matching(
            links_configuration,
            lambda config: link_interface in config['interfaces'],
        )
        if link_config:
            link_interface_type = f"{link_config['mode'].capitalize()} {link_config['type'].capitalize()}"
        else:
            link_interface_type = "Unknown"

        note_lines += [
            f'Trouble: {trouble.value}',
            '',
            f'Edge Name: {edge_status["edgeName"]}',
            f'Name: {link_status["displayName"]}',
            f'Interface: {link_status["interface"]}',
            f'Link Type: {link_interface_type}',
            '',
            f'Interval for Scan: {scan_interval} minutes',
            f'Threshold: {metrics_threshold} ms',
        ]

        if not self._trouble_repository.is_jitter_rx_within_threshold(link_metrics):
            note_lines.append(f'Receive: {link_metrics["bestJitterMsRx"]} ms')

        if not self._trouble_repository.is_jitter_tx_within_threshold(link_metrics):
            note_lines.append(f'Transfer: {link_metrics["bestJitterMsTx"]} ms')

        note_lines += [
            '',
            f'Scan Time: {datetime.now(timezone(self._config.MONITOR_CONFIG["timezone"]))}',
            (
                'Links: '
                f'[Edge|{velocloud_edge_base_url}/] - [QoE|{velocloud_edge_base_url}/qoe/] - '
                f'[Transport|{velocloud_edge_base_url}/links/] - [Events|{velocloud_base_url}/events/]'
            ),
        ]
        return os.linesep.join(note_lines)

    def build_bandwidth_trouble_note(self, link_data: dict, *, is_reopen_note: bool = False) -> str:
        edge_status = link_data["edge_status"]
        link_metrics = link_data["link_metrics"]

        edge_cached_info = link_data["cached_info"]
        links_configuration = edge_cached_info['links_configuration']

        link_status = link_data["link_status"]
        link_interface = link_status['interface']

        trouble = AffectingTroubles.BANDWIDTH_OVER_UTILIZATION
        scan_interval = self._config.MONITOR_CONFIG['monitoring_minutes_per_trouble'][trouble]
        metrics_threshold = self._config.MONITOR_CONFIG['thresholds'][trouble]

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
                'Re-opening ticket.',
                '',
            ]

        link_config = self._utils_repository.get_first_element_matching(
            links_configuration,
            lambda config: link_interface in config['interfaces'],
        )
        if link_config:
            link_interface_type = f"{link_config['mode'].capitalize()} {link_config['type'].capitalize()}"
        else:
            link_interface_type = "Unknown"

        note_lines += [
            f'Trouble: {trouble.value}',
            '',
            f'Edge Name: {edge_status["edgeName"]}',
            f'Name: {link_status["displayName"]}',
            f'Interface: {link_status["interface"]}',
            f'Link Type: {link_interface_type}',
            '',
            f'Interval for Scan: {scan_interval} minutes',
        ]

        rx_bandwidth = link_metrics['bpsOfBestPathRx']
        if rx_bandwidth > 0:
            if not self._trouble_repository.is_bandwidth_rx_within_threshold(link_metrics, scan_interval):
                rx_throughput = self._trouble_repository.get_bandwidth_throughput_bps(
                    total_bytes=link_metrics['bytesRx'],
                    lookup_interval_minutes=scan_interval,
                )
                rx_threshold = (metrics_threshold / 100) * rx_bandwidth

                note_lines += [
                    f'Throughput (Receive): {self._utils_repository.humanize_bps(rx_throughput)}',
                    f'Bandwidth (Receive): {self._utils_repository.humanize_bps(rx_bandwidth)}',
                    f'Threshold (Receive): {metrics_threshold}% ({self._utils_repository.humanize_bps(rx_threshold)})',
                ]

        tx_bandwidth = link_metrics['bpsOfBestPathTx']
        if tx_bandwidth > 0:
            if not self._trouble_repository.is_bandwidth_tx_within_threshold(link_metrics, scan_interval):
                tx_throughput = self._trouble_repository.get_bandwidth_throughput_bps(
                    total_bytes=link_metrics['bytesTx'],
                    lookup_interval_minutes=scan_interval,
                )
                tx_threshold = (metrics_threshold / 100) * tx_bandwidth

                note_lines += [
                    f'Throughput (Transfer): {self._utils_repository.humanize_bps(tx_throughput)}',
                    f'Bandwidth (Transfer): {self._utils_repository.humanize_bps(tx_bandwidth)}',
                    f'Threshold (Transfer): {metrics_threshold}% ({self._utils_repository.humanize_bps(tx_threshold)})',
                ]

        note_lines += [
            '',
            f'Scan Time: {datetime.now(timezone(self._config.MONITOR_CONFIG["timezone"]))}',
            (
                'Links: '
                f'[Edge|{velocloud_edge_base_url}/] - [QoE|{velocloud_edge_base_url}/qoe/] - '
                f'[Transport|{velocloud_edge_base_url}/links/] - [Events|{velocloud_base_url}/events/]'
            ),
        ]
        return os.linesep.join(note_lines)
