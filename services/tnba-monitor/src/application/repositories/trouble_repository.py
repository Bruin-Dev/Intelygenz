from datetime import datetime

from dateutil.parser import parse
from pytz import utc

from application import AffectingTroubles


class TroubleRepository:
    def __init__(self, config, utils_repository):
        self._config = config
        self._utils_repository = utils_repository

    def is_latency_rx_within_threshold(self, link_metrics: dict) -> bool:
        trouble = AffectingTroubles.LATENCY
        return link_metrics['bestLatencyMsRx'] < self._config.MONITOR_CONFIG['service_affecting']['thresholds'][trouble]

    def is_latency_tx_within_threshold(self, link_metrics: dict) -> bool:
        trouble = AffectingTroubles.LATENCY
        return link_metrics['bestLatencyMsTx'] < self._config.MONITOR_CONFIG['service_affecting']['thresholds'][trouble]

    def are_latency_metrics_within_threshold(self, link_metrics: dict) -> bool:
        return (
            self.is_latency_rx_within_threshold(link_metrics) and self.is_latency_tx_within_threshold(link_metrics)
        )

    def is_packet_loss_rx_within_threshold(self, link_metrics: dict) -> bool:
        trouble = AffectingTroubles.PACKET_LOSS
        return link_metrics['bestLossPctRx'] < self._config.MONITOR_CONFIG['service_affecting']['thresholds'][trouble]

    def is_packet_loss_tx_within_threshold(self, link_metrics: dict) -> bool:
        trouble = AffectingTroubles.PACKET_LOSS
        return link_metrics['bestLossPctTx'] < self._config.MONITOR_CONFIG['service_affecting']['thresholds'][trouble]

    def are_packet_loss_metrics_within_threshold(self, link_metrics: dict) -> bool:
        return (
            self.is_packet_loss_rx_within_threshold(link_metrics) and self.is_packet_loss_tx_within_threshold(
                                                                        link_metrics)
        )

    def is_jitter_rx_within_threshold(self, link_metrics: dict) -> bool:
        trouble = AffectingTroubles.JITTER
        return link_metrics['bestJitterMsRx'] < self._config.MONITOR_CONFIG['service_affecting']['thresholds'][trouble]

    def is_jitter_tx_within_threshold(self, link_metrics: dict) -> bool:
        trouble = AffectingTroubles.JITTER
        return link_metrics['bestJitterMsTx'] < self._config.MONITOR_CONFIG['service_affecting']['thresholds'][trouble]

    def are_jitter_metrics_within_threshold(self, link_metrics: dict) -> bool:
        return (
            self.is_jitter_rx_within_threshold(link_metrics) and self.is_jitter_tx_within_threshold(link_metrics)
        )

    @staticmethod
    def get_bandwidth_throughput_bps(total_bytes: int, lookup_interval_minutes: int) -> float:
        return (total_bytes * 8) / (lookup_interval_minutes * 60)

    @staticmethod
    def get_consumed_bandwidth_percentage(throughput: float, bandwidth: int) -> float:
        return (throughput / bandwidth) * 100

    def __is_bandwidth_within_threshold(self, total_bytes: int, bandwidth: int, lookup_interval_minutes: int) -> bool:
        trouble = AffectingTroubles.BANDWIDTH_OVER_UTILIZATION
        threshold = self._config.MONITOR_CONFIG['service_affecting']['thresholds'][trouble]

        throughput = self.get_bandwidth_throughput_bps(total_bytes, lookup_interval_minutes)
        consumed_bandwidth = self.get_consumed_bandwidth_percentage(throughput, bandwidth)
        return consumed_bandwidth < threshold

    def is_bandwidth_rx_within_threshold(self, link_metrics: dict, lookup_interval_minutes: int) -> bool:
        rx_bytes = link_metrics['bytesRx']
        rx_bandwidth = link_metrics['bpsOfBestPathRx']
        return self.__is_bandwidth_within_threshold(rx_bytes, rx_bandwidth, lookup_interval_minutes)

    def is_bandwidth_tx_within_threshold(self, link_metrics: dict, lookup_interval_minutes: int) -> bool:
        tx_bytes = link_metrics['bytesTx']
        tx_bandwidth = link_metrics['bpsOfBestPathTx']
        return self.__is_bandwidth_within_threshold(tx_bytes, tx_bandwidth, lookup_interval_minutes)

    @staticmethod
    def is_valid_bps_metric(metric: int) -> bool:
        return metric > 0

    def are_bps_metrics_valid(self, link_metrics: dict) -> bool:
        is_tx_bandwidth_valid = self.is_valid_bps_metric(link_metrics['bpsOfBestPathTx'])
        is_rx_bandwidth_valid = self.is_valid_bps_metric(link_metrics['bpsOfBestPathRx'])
        return is_tx_bandwidth_valid and is_rx_bandwidth_valid

    def are_bandwidth_metrics_within_threshold(self, link_metrics: dict, lookup_interval_minutes: int) -> bool:
        return (
            self.is_bandwidth_rx_within_threshold(link_metrics,
                                                  lookup_interval_minutes) and self.is_bandwidth_tx_within_threshold(
                                                                                link_metrics, lookup_interval_minutes)
        )

    def are_bouncing_events_within_threshold(self, events):
        trouble = AffectingTroubles.BOUNCING

        threshold = self._config.MONITOR_CONFIG['service_affecting']['thresholds'][trouble]

        return len(events) < threshold

    # Intake serial to metrics list and serial to event_list
    def are_all_metrics_within_thresholds(self, serial_to_link_metrics_and_events) -> bool:
        all_metrics_within_thresholds = True
        lookup_interval_minutes = self._config.MONITOR_CONFIG['service_affecting']['metrics_lookup_interval_minutes']

        for link in serial_to_link_metrics_and_events:
            # Get link metrics
            metrics = link['link_metrics']
            # get link event
            events = link['link_events']

            checks = [
                self.are_latency_metrics_within_threshold(metrics),
                self.are_packet_loss_metrics_within_threshold(metrics),
                self.are_jitter_metrics_within_threshold(metrics),
                self.are_bouncing_events_within_threshold(events)
            ]

            if self.are_bps_metrics_valid(metrics):
                checks.append(self.are_bandwidth_metrics_within_threshold(metrics, lookup_interval_minutes))

            all_metrics_within_thresholds &= all(checks)

        return all_metrics_within_thresholds
