import os
from datetime import datetime
from typing import Callable

from pytz import timezone
from src.application import AffectingTroubles


class NotesRepository:
    def __init__(self, config, trouble_repository, utils_repository):
        self._config = config
        self._trouble_repository = trouble_repository
        self._utils_repository = utils_repository

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

    def build_latency_trouble_note(self, link_data: dict) -> str:
        edge_status = link_data["edge_status"]
        link_metrics = link_data["link_metrics"]

        edge_cached_info = link_data["cached_info"]
        links_configuration = edge_cached_info["links_configuration"]

        link_status = link_data["link_status"]
        link_interface = link_status["interface"]

        trouble = AffectingTroubles.LATENCY
        scan_interval = self._config.MONITOR_CONFIG["monitoring_minutes_per_trouble"][trouble]
        metrics_threshold = self._config.MONITOR_CONFIG["thresholds"][trouble]

        edge_full_id = edge_cached_info["edge"]
        velocloud_base_url = (
            f'https://{edge_full_id["host"]}/#!/operator/customer/{edge_full_id["enterprise_id"]}/monitor'
        )
        velocloud_edge_base_url = f'{velocloud_base_url}/edge/{edge_full_id["edge_id"]}'

        note_lines = [
            "#*MetTel's IPA*#",
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
            f'Serial Number: {edge_status["edgeSerialNumber"]}',
            f'Name: {link_status["displayName"]}',
            f'Interface: {link_status["interface"]}',
            f"Link Type: {link_interface_type}",
            "",
            f"Interval for Scan: {scan_interval} minutes",
            f"Threshold: {metrics_threshold} ms",
        ]

        if not self._trouble_repository.is_latency_rx_within_threshold(link_metrics):
            note_lines.append(f'Receive: {link_metrics["bestLatencyMsRx"]} ms')

        if not self._trouble_repository.is_latency_tx_within_threshold(link_metrics):
            note_lines.append(f'Transfer: {link_metrics["bestLatencyMsTx"]} ms')

        note_lines += [
            "",
            f"Scan Time: {datetime.now(timezone(self._config.TIMEZONE))}",
            (
                "Links: "
                f'<a href="{velocloud_edge_base_url}/">Edge</a> - '
                f'<a href="{velocloud_edge_base_url}/qoe/">QoE</a> - '
                f'<a href="{velocloud_edge_base_url}/links/">Transport</a> - '
                f'<a href="{velocloud_edge_base_url}/events/">Events</a>'
            ),
        ]
        return os.linesep.join(note_lines)

    def build_packet_loss_trouble_note(self, link_data: dict) -> str:
        edge_status = link_data["edge_status"]
        link_metrics = link_data["link_metrics"]

        edge_cached_info = link_data["cached_info"]
        links_configuration = edge_cached_info["links_configuration"]

        link_status = link_data["link_status"]
        link_interface = link_status["interface"]

        trouble = AffectingTroubles.PACKET_LOSS
        scan_interval = self._config.MONITOR_CONFIG["monitoring_minutes_per_trouble"][trouble]
        metrics_threshold = self._config.MONITOR_CONFIG["thresholds"][trouble]

        edge_full_id = edge_cached_info["edge"]
        velocloud_base_url = (
            f'https://{edge_full_id["host"]}/#!/operator/customer/{edge_full_id["enterprise_id"]}/monitor'
        )
        velocloud_edge_base_url = f'{velocloud_base_url}/edge/{edge_full_id["edge_id"]}'

        note_lines = [
            "#*MetTel's IPA*#",
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
            f'Serial Number: {edge_status["edgeSerialNumber"]}',
            f'Name: {link_status["displayName"]}',
            f'Interface: {link_status["interface"]}',
            f"Link Type: {link_interface_type}",
            "",
            f"Interval for Scan: {scan_interval} minutes",
            f"Threshold: {metrics_threshold} packets",
        ]

        if not self._trouble_repository.is_packet_loss_rx_within_threshold(link_metrics):
            note_lines.append(f'Receive: {link_metrics["bestLossPctRx"]} packets')

        if not self._trouble_repository.is_packet_loss_tx_within_threshold(link_metrics):
            note_lines.append(f'Transfer: {link_metrics["bestLossPctTx"]} packets')

        note_lines += [
            "",
            f"Scan Time: {datetime.now(timezone(self._config.TIMEZONE))}",
            (
                "Links: "
                f'<a href="{velocloud_edge_base_url}/">Edge</a> - '
                f'<a href="{velocloud_edge_base_url}/qoe/">QoE</a> - '
                f'<a href="{velocloud_edge_base_url}/links/">Transport</a> - '
                f'<a href="{velocloud_edge_base_url}/events/">Events</a>'
            ),
        ]
        return os.linesep.join(note_lines)

    def build_jitter_trouble_note(self, link_data: dict) -> str:
        edge_status = link_data["edge_status"]
        link_metrics = link_data["link_metrics"]

        edge_cached_info = link_data["cached_info"]
        links_configuration = edge_cached_info["links_configuration"]

        link_status = link_data["link_status"]
        link_interface = link_status["interface"]

        trouble = AffectingTroubles.JITTER
        scan_interval = self._config.MONITOR_CONFIG["monitoring_minutes_per_trouble"][trouble]
        metrics_threshold = self._config.MONITOR_CONFIG["thresholds"][trouble]

        edge_full_id = edge_cached_info["edge"]
        velocloud_base_url = (
            f'https://{edge_full_id["host"]}/#!/operator/customer/{edge_full_id["enterprise_id"]}/monitor'
        )
        velocloud_edge_base_url = f'{velocloud_base_url}/edge/{edge_full_id["edge_id"]}'

        note_lines = [
            "#*MetTel's IPA*#",
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
            f'Serial Number: {edge_status["edgeSerialNumber"]}',
            f'Name: {link_status["displayName"]}',
            f'Interface: {link_status["interface"]}',
            f"Link Type: {link_interface_type}",
            "",
            f"Interval for Scan: {scan_interval} minutes",
            f"Threshold: {metrics_threshold} ms",
        ]

        if not self._trouble_repository.is_jitter_rx_within_threshold(link_metrics):
            note_lines.append(f'Receive: {link_metrics["bestJitterMsRx"]} ms')

        if not self._trouble_repository.is_jitter_tx_within_threshold(link_metrics):
            note_lines.append(f'Transfer: {link_metrics["bestJitterMsTx"]} ms')

        note_lines += [
            "",
            f"Scan Time: {datetime.now(timezone(self._config.TIMEZONE))}",
            (
                "Links: "
                f'<a href="{velocloud_edge_base_url}/">Edge</a> - '
                f'<a href="{velocloud_edge_base_url}/qoe/">QoE</a> - '
                f'<a href="{velocloud_edge_base_url}/links/">Transport</a> - '
                f'<a href="{velocloud_edge_base_url}/events/">Events</a>'
            ),
        ]
        return os.linesep.join(note_lines)

    def build_bandwidth_trouble_note(self, link_data: dict) -> str:
        edge_status = link_data["edge_status"]
        link_metrics = link_data["link_metrics"]

        edge_cached_info = link_data["cached_info"]
        links_configuration = edge_cached_info["links_configuration"]

        link_status = link_data["link_status"]
        link_interface = link_status["interface"]

        trouble = AffectingTroubles.BANDWIDTH_OVER_UTILIZATION
        scan_interval = self._config.MONITOR_CONFIG["monitoring_minutes_per_trouble"][trouble]
        metrics_threshold = self._config.MONITOR_CONFIG["thresholds"][trouble]

        edge_full_id = edge_cached_info["edge"]
        velocloud_base_url = (
            f'https://{edge_full_id["host"]}/#!/operator/customer/{edge_full_id["enterprise_id"]}/monitor'
        )
        velocloud_edge_base_url = f'{velocloud_base_url}/edge/{edge_full_id["edge_id"]}'

        note_lines = [
            "#*MetTel's IPA*#",
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
            f'Serial Number: {edge_status["edgeSerialNumber"]}',
            f'Name: {link_status["displayName"]}',
            f'Interface: {link_status["interface"]}',
            f"Link Type: {link_interface_type}",
            "",
            f"Interval for Scan: {scan_interval} minutes",
        ]

        rx_bandwidth = link_metrics["bpsOfBestPathRx"]
        if self._trouble_repository.is_valid_bps_metric(rx_bandwidth):
            if not self._trouble_repository.is_bandwidth_rx_within_threshold(link_metrics, scan_interval):
                rx_throughput = self._trouble_repository.get_bandwidth_throughput_bps(
                    total_bytes=link_metrics["bytesRx"],
                    lookup_interval_minutes=scan_interval,
                )
                rx_threshold = (metrics_threshold / 100) * rx_bandwidth

                note_lines += [
                    f"Throughput (Receive): {self._utils_repository.humanize_bps(rx_throughput)}",
                    f"Bandwidth (Receive): {self._utils_repository.humanize_bps(rx_bandwidth)}",
                    f"Threshold (Receive): {metrics_threshold}% ({self._utils_repository.humanize_bps(rx_threshold)})",
                ]

        tx_bandwidth = link_metrics["bpsOfBestPathTx"]
        if self._trouble_repository.is_valid_bps_metric(tx_bandwidth):
            if not self._trouble_repository.is_bandwidth_tx_within_threshold(link_metrics, scan_interval):
                tx_throughput = self._trouble_repository.get_bandwidth_throughput_bps(
                    total_bytes=link_metrics["bytesTx"],
                    lookup_interval_minutes=scan_interval,
                )
                tx_threshold = (metrics_threshold / 100) * tx_bandwidth

                note_lines += [
                    f"Throughput (Transfer): {self._utils_repository.humanize_bps(tx_throughput)}",
                    f"Bandwidth (Transfer): {self._utils_repository.humanize_bps(tx_bandwidth)}",
                    f"Threshold (Transfer): {metrics_threshold}% ({self._utils_repository.humanize_bps(tx_threshold)})",
                ]

        note_lines += [
            "",
            f"Scan Time: {datetime.now(timezone(self._config.TIMEZONE))}",
            (
                "Links: "
                f'<a href="{velocloud_edge_base_url}/">Edge</a> - '
                f'<a href="{velocloud_edge_base_url}/qoe/">QoE</a> - '
                f'<a href="{velocloud_edge_base_url}/links/">Transport</a> - '
                f'<a href="{velocloud_edge_base_url}/events/">Events</a>'
            ),
        ]
        return os.linesep.join(note_lines)

    def build_bouncing_trouble_note(self, link_data: dict) -> str:
        edge_status = link_data["edge_status"]
        link_events = link_data["link_events"]

        edge_cached_info = link_data["cached_info"]
        links_configuration = edge_cached_info["links_configuration"]

        link_status = link_data["link_status"]
        link_interface = link_status["interface"]

        trouble = AffectingTroubles.BOUNCING
        scan_interval = self._config.MONITOR_CONFIG["monitoring_minutes_per_trouble"][trouble]
        metrics_threshold = self._config.MONITOR_CONFIG["thresholds"][trouble]

        edge_full_id = edge_cached_info["edge"]
        velocloud_base_url = (
            f'https://{edge_full_id["host"]}/#!/operator/customer/{edge_full_id["enterprise_id"]}/monitor'
        )
        velocloud_edge_base_url = f'{velocloud_base_url}/edge/{edge_full_id["edge_id"]}'

        note_lines = [
            "#*MetTel's IPA*#",
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
            f'Serial Number: {edge_status["edgeSerialNumber"]}',
            f'Name: {link_status["displayName"]}',
            f'Interface: {link_status["interface"]}',
            f"Link Type: {link_interface_type}",
            "",
            f"Interval for Scan: {scan_interval} minutes",
            f"Threshold: {metrics_threshold} events",
            f"Events: {len(link_events)}",
            "",
            f"Scan Time: {datetime.now(timezone(self._config.TIMEZONE))}",
            (
                "Links: "
                f'<a href="{velocloud_edge_base_url}/">Edge</a> - '
                f'<a href="{velocloud_edge_base_url}/qoe/">QoE</a> - '
                f'<a href="{velocloud_edge_base_url}/links/">Transport</a>'
            ),
        ]

        return os.linesep.join(note_lines)
