from datetime import timedelta
from unittest.mock import Mock, patch

from application.repositories import trouble_repository as trouble_repository_module
from config import testconfig
from dateutil.parser import parse
from pytz import utc


class TestTroubleRepository:
    def instance_test(self, trouble_repository, utils_repository):
        assert trouble_repository._utils_repository is utils_repository
        assert trouble_repository._config is testconfig

    def is_latency_rx_within_threshold_test(self, trouble_repository, make_metrics):
        metrics = make_metrics(best_latency_ms_rx=139)
        result = trouble_repository.is_latency_rx_within_threshold(metrics)
        assert result is True

        metrics = make_metrics(best_latency_ms_rx=140)
        result = trouble_repository.is_latency_rx_within_threshold(metrics)
        assert result is False

    def is_latency_tx_within_threshold_test(self, trouble_repository, make_metrics):
        metrics = make_metrics(best_latency_ms_tx=139)
        result = trouble_repository.is_latency_tx_within_threshold(metrics)
        assert result is True

        metrics = make_metrics(best_latency_ms_tx=140)
        result = trouble_repository.is_latency_tx_within_threshold(metrics)
        assert result is False

    def are_latency_metrics_within_threshold_test(self, trouble_repository, make_metrics):
        metrics = make_metrics(best_latency_ms_tx=139, best_latency_ms_rx=139)
        result = trouble_repository.are_latency_metrics_within_threshold(metrics)
        assert result is True

        metrics = make_metrics(best_latency_ms_tx=140, best_latency_ms_rx=139)
        result = trouble_repository.are_latency_metrics_within_threshold(metrics)
        assert result is False

        metrics = make_metrics(best_latency_ms_tx=139, best_latency_ms_rx=140)
        result = trouble_repository.are_latency_metrics_within_threshold(metrics)
        assert result is False

        metrics = make_metrics(best_latency_ms_tx=140, best_latency_ms_rx=140)
        result = trouble_repository.are_latency_metrics_within_threshold(metrics)
        assert result is False

    def is_packet_loss_rx_within_threshold_test(self, trouble_repository, make_metrics):
        metrics = make_metrics(best_packet_loss_rx=7)
        result = trouble_repository.is_packet_loss_rx_within_threshold(metrics)
        assert result is True

        metrics = make_metrics(best_packet_loss_rx=8)
        result = trouble_repository.is_packet_loss_rx_within_threshold(metrics)
        assert result is False

    def is_packet_loss_tx_within_threshold_test(self, trouble_repository, make_metrics):
        metrics = make_metrics(best_packet_loss_tx=7)
        result = trouble_repository.is_packet_loss_tx_within_threshold(metrics)
        assert result is True

        metrics = make_metrics(best_packet_loss_tx=8)
        result = trouble_repository.is_packet_loss_tx_within_threshold(metrics)
        assert result is False

    def are_packet_loss_metrics_within_threshold_test(self, trouble_repository, make_metrics):
        metrics = make_metrics(best_packet_loss_tx=7, best_packet_loss_rx=7)
        result = trouble_repository.are_packet_loss_metrics_within_threshold(metrics)
        assert result is True

        metrics = make_metrics(best_packet_loss_tx=8, best_packet_loss_rx=7)
        result = trouble_repository.are_packet_loss_metrics_within_threshold(metrics)
        assert result is False

        metrics = make_metrics(best_packet_loss_tx=7, best_packet_loss_rx=8)
        result = trouble_repository.are_packet_loss_metrics_within_threshold(metrics)
        assert result is False

        metrics = make_metrics(best_packet_loss_tx=8, best_packet_loss_rx=8)
        result = trouble_repository.are_packet_loss_metrics_within_threshold(metrics)
        assert result is False

    def is_jitter_rx_within_threshold_test(self, trouble_repository, make_metrics):
        metrics = make_metrics(best_jitter_ms_rx=49)
        result = trouble_repository.is_jitter_rx_within_threshold(metrics)
        assert result is True

        metrics = make_metrics(best_jitter_ms_rx=50)
        result = trouble_repository.is_jitter_rx_within_threshold(metrics)
        assert result is False

    def is_jitter_tx_within_threshold_test(self, trouble_repository, make_metrics):
        metrics = make_metrics(best_jitter_ms_tx=49)
        result = trouble_repository.is_jitter_tx_within_threshold(metrics)
        assert result is True

        metrics = make_metrics(best_jitter_ms_tx=50)
        result = trouble_repository.is_jitter_tx_within_threshold(metrics)
        assert result is False

    def are_jitter_metrics_within_threshold_test(self, trouble_repository, make_metrics):
        metrics = make_metrics(best_jitter_ms_tx=49, best_jitter_ms_rx=49)
        result = trouble_repository.are_jitter_metrics_within_threshold(metrics)
        assert result is True

        metrics = make_metrics(best_jitter_ms_tx=50, best_jitter_ms_rx=49)
        result = trouble_repository.are_jitter_metrics_within_threshold(metrics)
        assert result is False

        metrics = make_metrics(best_jitter_ms_tx=49, best_jitter_ms_rx=50)
        result = trouble_repository.are_jitter_metrics_within_threshold(metrics)
        assert result is False

        metrics = make_metrics(best_jitter_ms_tx=50, best_jitter_ms_rx=50)
        result = trouble_repository.are_jitter_metrics_within_threshold(metrics)
        assert result is False

    def get_bandwidth_throughput_bps_test(self, trouble_repository):
        total_bytes = 300
        lookup_interval_minutes = 2

        result = trouble_repository.get_bandwidth_throughput_bps(total_bytes, lookup_interval_minutes)
        expected = 20.0
        assert result == expected

    def get_consumed_bandwidth_percentage_test(self, trouble_repository):
        throughput = 20.0
        bandwidth = 200

        result = trouble_repository.get_consumed_bandwidth_percentage(throughput, bandwidth)
        expected = 10.0
        assert result == expected

    def is_bandwidth_rx_within_threshold_test(self, trouble_repository, make_metrics):
        lookup_interval_minutes = 30

        metrics = make_metrics(bytes_rx=1, bps_of_best_path_rx=100)
        result = trouble_repository.is_bandwidth_rx_within_threshold(metrics, lookup_interval_minutes)
        assert result is True

        metrics = make_metrics(bytes_rx=1000000000, bps_of_best_path_rx=100)
        result = trouble_repository.is_bandwidth_rx_within_threshold(metrics, lookup_interval_minutes)
        assert result is False

    def is_bandwidth_tx_within_threshold_test(self, trouble_repository, make_metrics):
        lookup_interval_minutes = 30

        metrics = make_metrics(bytes_tx=1, bps_of_best_path_tx=100)
        result = trouble_repository.is_bandwidth_tx_within_threshold(metrics, lookup_interval_minutes)
        assert result is True

        metrics = make_metrics(bytes_tx=1000000000, bps_of_best_path_tx=100)
        result = trouble_repository.is_bandwidth_tx_within_threshold(metrics, lookup_interval_minutes)
        assert result is False

    def is_valid_bps_metric_test(self, trouble_repository):
        metric = 100
        result = trouble_repository.is_valid_bps_metric(metric)
        assert result is True

        metric = 0
        result = trouble_repository.is_valid_bps_metric(metric)
        assert result is False

    def are_bps_metrics_valid_test(self, trouble_repository, make_metrics):
        metrics = make_metrics(bps_of_best_path_tx=100, bps_of_best_path_rx=100)
        result = trouble_repository.are_bps_metrics_valid(metrics)
        assert result is True

        metrics = make_metrics(bps_of_best_path_tx=0, bps_of_best_path_rx=100)
        result = trouble_repository.are_bps_metrics_valid(metrics)
        assert result is False

        metrics = make_metrics(bps_of_best_path_tx=100, bps_of_best_path_rx=0)
        result = trouble_repository.are_bps_metrics_valid(metrics)
        assert result is False

        metrics = make_metrics(bps_of_best_path_tx=0, bps_of_best_path_rx=0)
        result = trouble_repository.are_bps_metrics_valid(metrics)
        assert result is False

    def are_bandwidth_metrics_within_threshold_test(self, trouble_repository, make_metrics):
        lookup_interval_minutes = 30

        metrics = make_metrics(
            bytes_tx=1,
            bps_of_best_path_tx=100,
            bytes_rx=1,
            bps_of_best_path_rx=100,
        )
        result = trouble_repository.are_bandwidth_metrics_within_threshold(metrics, lookup_interval_minutes)
        assert result is True

        metrics = make_metrics(
            bytes_tx=1000000000,
            bps_of_best_path_tx=100,
            bytes_rx=1,
            bps_of_best_path_rx=100,
        )
        result = trouble_repository.are_bandwidth_metrics_within_threshold(metrics, lookup_interval_minutes)
        assert result is False

        metrics = make_metrics(
            bytes_tx=1,
            bps_of_best_path_tx=100,
            bytes_rx=1000000000,
            bps_of_best_path_rx=100,
        )
        result = trouble_repository.are_bandwidth_metrics_within_threshold(metrics, lookup_interval_minutes)
        assert result is False

        metrics = make_metrics(
            bytes_tx=1000000000,
            bps_of_best_path_tx=100,
            bytes_rx=1000000000,
            bps_of_best_path_rx=100,
        )
        result = trouble_repository.are_bandwidth_metrics_within_threshold(metrics, lookup_interval_minutes)
        assert result is False

    def are_bouncing_events_within_threshold_test(self, trouble_repository, make_event):
        events = [make_event()] * 3
        result = trouble_repository.are_bouncing_events_within_threshold(events)
        assert result is True

        events = [make_event()] * 5
        result = trouble_repository.are_bouncing_events_within_threshold(events)
        assert result is False

    def are_all_metrics_within_thresholds_test(
        self,
        trouble_repository,
        make_metrics,
        make_link_metrics_and_events_object,
        make_list_link_metrics_and_events_objects,
    ):

        metrics = make_metrics(
            best_latency_ms_tx=139,
            best_latency_ms_rx=139,
            best_packet_loss_tx=7,
            best_packet_loss_rx=7,
            best_jitter_ms_tx=49,
            best_jitter_ms_rx=49,
            bytes_tx=1,
            bps_of_best_path_tx=100,
            bytes_rx=1,
            bps_of_best_path_rx=100,
        )
        link_metrics_and_events_object = make_link_metrics_and_events_object(metrics=metrics)
        link_metrics_and_events_objects = make_list_link_metrics_and_events_objects(link_metrics_and_events_object)
        result = trouble_repository.are_all_metrics_within_thresholds(
            link_metrics_and_events_objects,
        )
        assert result is True

        metrics = make_metrics(
            best_latency_ms_tx=140,
            best_latency_ms_rx=139,
            best_packet_loss_tx=7,
            best_packet_loss_rx=7,
            best_jitter_ms_tx=49,
            best_jitter_ms_rx=49,
            bytes_tx=1000000000,
            bps_of_best_path_tx=100,
            bytes_rx=1000000000,
            bps_of_best_path_rx=100,
        )
        link_metrics_and_events_object = make_link_metrics_and_events_object(metrics=metrics)
        link_metrics_and_events_objects = make_list_link_metrics_and_events_objects(link_metrics_and_events_object)
        result = trouble_repository.are_all_metrics_within_thresholds(
            link_metrics_and_events_objects,
        )
        assert result is False

    def are_all_metrics_within_thresholds__invalid_bandwidth_metrics_taken_into_account_test(
        self,
        trouble_repository,
        make_metrics,
        make_link_metrics_and_events_object,
        make_list_link_metrics_and_events_objects,
    ):

        metrics = make_metrics(
            best_latency_ms_tx=140,
            best_latency_ms_rx=139,
            best_packet_loss_tx=7,
            best_packet_loss_rx=7,
            best_jitter_ms_tx=49,
            best_jitter_ms_rx=49,
            bytes_tx=1000000000,
            bps_of_best_path_tx=0,
            bytes_rx=1000000000,
            bps_of_best_path_rx=0,
        )
        link_metrics_and_events_object = make_link_metrics_and_events_object(metrics=metrics)
        link_metrics_and_events_objects = make_list_link_metrics_and_events_objects(link_metrics_and_events_object)
        result = trouble_repository.are_all_metrics_within_thresholds(
            link_metrics_and_events_objects,
        )
        assert result is False
