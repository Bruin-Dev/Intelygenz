from application import AFFECTING_NOTE_REGEX, AffectingTroubles
from datetime import datetime, timedelta
from pytz import utc


class TroubleRepository:
    def __init__(self, config, utils_repository):
        self._config = config
        self._utils_repository = utils_repository

    def was_last_trouble_detected_recently(
        self, ticket_notes: list, ticket_creation_date: str, *, max_seconds_since_last_trouble: int
    ) -> bool:
        trouble_regex = AFFECTING_NOTE_REGEX
        return self._utils_repository.has_last_event_happened_recently(
            ticket_notes,
            ticket_creation_date,
            max_seconds_since_last_event=max_seconds_since_last_trouble,
            regex=trouble_regex,
        )

    def is_latency_rx_within_threshold(self, link_metrics: dict, is_wireless_link: bool) -> bool:
        trouble = AffectingTroubles.LATENCY
        return (link_metrics["bestLatencyMsRx"]
                < self._config.MONITOR_CONFIG[self._utils_repository.threshold_metric_to_use(
                    is_wireless_link)][trouble])

    def is_latency_tx_within_threshold(self, link_metrics: dict, is_wireless_link: bool) -> bool:
        trouble = AffectingTroubles.LATENCY
        return (link_metrics["bestLatencyMsTx"]
                < self._config.MONITOR_CONFIG[self._utils_repository.threshold_metric_to_use(
                    is_wireless_link)][trouble])

    def are_latency_metrics_within_threshold(self, link_metrics: dict, is_wireless_link: bool) -> bool:
        return (self.is_latency_rx_within_threshold(link_metrics, is_wireless_link)
                and self.is_latency_tx_within_threshold(link_metrics, is_wireless_link))

    def is_packet_loss_rx_within_threshold(self, link_metrics: dict, is_wireless_link: bool) -> bool:
        trouble = AffectingTroubles.PACKET_LOSS
        return (link_metrics["bestLossPctRx"]
                < self._config.MONITOR_CONFIG[self._utils_repository.threshold_metric_to_use(
                    is_wireless_link)][trouble])

    def is_packet_loss_tx_within_threshold(self, link_metrics: dict, is_wireless_link: bool) -> bool:
        trouble = AffectingTroubles.PACKET_LOSS
        return (link_metrics["bestLossPctTx"]
                < self._config.MONITOR_CONFIG[self._utils_repository.threshold_metric_to_use(
                    is_wireless_link)][trouble])

    def are_packet_loss_metrics_within_threshold(self, link_metrics: dict, is_wireless_link: bool) -> bool:
        return (self.is_packet_loss_rx_within_threshold(link_metrics, is_wireless_link)
                and self.is_packet_loss_tx_within_threshold(link_metrics, is_wireless_link))

    def is_jitter_rx_within_threshold(self, link_metrics: dict, is_wireless_link: bool) -> bool:
        trouble = AffectingTroubles.JITTER
        return (link_metrics["bestJitterMsRx"]
                < self._config.MONITOR_CONFIG[self._utils_repository.threshold_metric_to_use(
                    is_wireless_link)][trouble])

    def is_jitter_tx_within_threshold(self, link_metrics: dict, is_wireless_link: bool) -> bool:
        trouble = AffectingTroubles.JITTER
        return (link_metrics["bestJitterMsTx"]
                < self._config.MONITOR_CONFIG[self._utils_repository.threshold_metric_to_use(
                    is_wireless_link)][trouble])

    def are_jitter_metrics_within_threshold(self, link_metrics: dict, is_wireless_link: bool) -> bool:
        return (self.is_jitter_rx_within_threshold(link_metrics, is_wireless_link)
                and self.is_jitter_tx_within_threshold(link_metrics, is_wireless_link))

    @staticmethod
    def get_bandwidth_throughput_bps(total_bytes: int, lookup_interval_minutes: int) -> float:
        return (total_bytes * 8) / (lookup_interval_minutes * 60)

    @staticmethod
    def get_consumed_bandwidth_percentage(throughput: float, bandwidth: int) -> float:
        return (throughput / bandwidth) * 100

    def __is_bandwidth_within_threshold(self, total_bytes: int, bandwidth: int, lookup_interval_minutes: int,
                                        is_wireless_link: bool) -> bool:
        trouble = AffectingTroubles.BANDWIDTH_OVER_UTILIZATION
        threshold = self._config.MONITOR_CONFIG[self._utils_repository.threshold_metric_to_use(
            is_wireless_link)][trouble]

        throughput = self.get_bandwidth_throughput_bps(total_bytes, lookup_interval_minutes)
        consumed_bandwidth = self.get_consumed_bandwidth_percentage(throughput, bandwidth)
        return consumed_bandwidth < threshold

    def is_bandwidth_rx_within_threshold(self, link_metrics: dict, lookup_interval_minutes: int,
                                         is_wireless_link: bool) -> bool:
        rx_bytes = link_metrics["bytesRx"]
        rx_bandwidth = link_metrics["bpsOfBestPathRx"]
        return self.__is_bandwidth_within_threshold(rx_bytes, rx_bandwidth, lookup_interval_minutes, is_wireless_link)

    def is_bandwidth_tx_within_threshold(self, link_metrics: dict, lookup_interval_minutes: int,
                                         is_wireless_link: bool) -> bool:
        tx_bytes = link_metrics["bytesTx"]
        tx_bandwidth = link_metrics["bpsOfBestPathTx"]
        return self.__is_bandwidth_within_threshold(tx_bytes, tx_bandwidth, lookup_interval_minutes, is_wireless_link)

    @staticmethod
    def is_valid_bps_metric(metric: int) -> bool:
        return metric > 0

    def are_bps_metrics_valid(self, link_metrics: dict) -> bool:
        is_tx_bandwidth_valid = self.is_valid_bps_metric(link_metrics["bpsOfBestPathTx"])
        is_rx_bandwidth_valid = self.is_valid_bps_metric(link_metrics["bpsOfBestPathRx"])
        return is_tx_bandwidth_valid and is_rx_bandwidth_valid

    def are_bandwidth_metrics_within_threshold(self, link_metrics: dict, lookup_interval_minutes: int,
                                               is_wireless_link: bool) -> bool:
        return self.is_bandwidth_rx_within_threshold(
            link_metrics, lookup_interval_minutes, is_wireless_link
        ) and self.is_bandwidth_tx_within_threshold(link_metrics, lookup_interval_minutes, is_wireless_link)

    def are_bouncing_events_within_threshold(self, events, is_wireless_link: bool, autoresolve=False):
        trouble = AffectingTroubles.BOUNCING

        if autoresolve:
            threshold = self._config.MONITOR_CONFIG["autoresolve"]["thresholds"][trouble]
        else:
            threshold = self._config.MONITOR_CONFIG[self._utils_repository.threshold_metric_to_use(
                is_wireless_link)][trouble]

        return len(events) < threshold

    def are_all_metrics_within_thresholds(
        self, edge_data: dict, *, lookup_interval_minutes: int,
        check_bandwidth_troubles: bool, links_configuration: list[dict]
    ) -> bool:
        all_metrics_within_thresholds = True

        for link in edge_data["links"]:
            metrics = link["link_metrics"]
            events = link["link_events"]
            interface = link["link_status"]["interface"]

            is_wireless_link = self._utils_repository.get_is_wireless_link(interface, links_configuration)

            checks = [
                self.are_latency_metrics_within_threshold(metrics, is_wireless_link),
                self.are_packet_loss_metrics_within_threshold(metrics, is_wireless_link),
                self.are_jitter_metrics_within_threshold(metrics, is_wireless_link),
                self.are_bouncing_events_within_threshold(events, is_wireless_link, autoresolve=True),
            ]

            if check_bandwidth_troubles and self.are_bps_metrics_valid(metrics):
                checks.append(
                    self.are_bandwidth_metrics_within_threshold(metrics, lookup_interval_minutes, is_wireless_link))

            all_metrics_within_thresholds &= all(checks)

        return all_metrics_within_thresholds

    def should_check_bandwidth_troubles(self, host, client_id) -> bool:
        return (host != "metvco04.mettel.net"
                and client_id not in self._config.MONITOR_CONFIG["customers_with_bandwidth_disabled"])
