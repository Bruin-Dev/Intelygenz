from datetime import timedelta
from unittest.mock import Mock, patch

from application import AFFECTING_NOTE_REGEX
from application.repositories import utils_repository as utils_repository_module
from config import testconfig
from dateutil.parser import parse
from pytz import utc


class TestTroubleRepository:
    def instance_test(self, trouble_repository, utils_repository):
        assert trouble_repository._utils_repository is utils_repository
        assert trouble_repository._config is testconfig

    def was_last_trouble_detected_recently__no_trouble_note_found_test(
        self, trouble_repository, make_ticket_note, make_list_of_ticket_notes
    ):
        ticket_creation_date = "9/25/2020 6:31:54 AM"

        note_1 = make_ticket_note(text="Dummy note")
        note_2 = make_ticket_note(text="Dummy note 2")
        notes = make_list_of_ticket_notes(note_1, note_2)

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(minutes=59, seconds=59)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(utils_repository_module, "datetime", new=datetime_mock):
            result = trouble_repository.was_last_trouble_detected_recently(
                notes,
                ticket_creation_date,
                max_seconds_since_last_trouble=3600,
            )
            assert result is True

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(hours=1)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(utils_repository_module, "datetime", new=datetime_mock):
            result = trouble_repository.was_last_trouble_detected_recently(
                notes,
                ticket_creation_date,
                max_seconds_since_last_trouble=3600,
            )
            assert result is True

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(hours=1, seconds=1)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(utils_repository_module, "datetime", new=datetime_mock):
            result = trouble_repository.was_last_trouble_detected_recently(
                notes,
                ticket_creation_date,
                max_seconds_since_last_trouble=3600,
            )
            assert result is False

        trouble_repository._utils_repository.has_last_event_happened_recently.assert_called_with(
            notes, ticket_creation_date, max_seconds_since_last_event=3600, regex=AFFECTING_NOTE_REGEX
        )

    def was_last_trouble_detected_recently__standard_trouble_note_found_test(
        self, trouble_repository, make_ticket_note, make_list_of_ticket_notes
    ):
        ticket_creation_date = "9/25/2020 6:31:54 AM"
        trouble_note_timestamp = "2021-01-02T11:00:16.71-05:00"

        note_1 = make_ticket_note(
            text="Dummy note",
            creation_date=str(parse(trouble_note_timestamp) - timedelta(seconds=10)),
        )
        note_2 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nTrouble: Latency",
            creation_date=str(parse(trouble_note_timestamp)),
        )
        notes = make_list_of_ticket_notes(note_1, note_2)

        datetime_mock = Mock()

        new_now = parse(trouble_note_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(utils_repository_module, "datetime", new=datetime_mock):
            result = trouble_repository.was_last_trouble_detected_recently(
                notes,
                ticket_creation_date,
                max_seconds_since_last_trouble=3600,
            )
            assert result is True

        new_now = parse(trouble_note_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(utils_repository_module, "datetime", new=datetime_mock):
            result = trouble_repository.was_last_trouble_detected_recently(
                notes,
                ticket_creation_date,
                max_seconds_since_last_trouble=3600,
            )
            assert result is True

        new_now = parse(trouble_note_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(utils_repository_module, "datetime", new=datetime_mock):
            result = trouble_repository.was_last_trouble_detected_recently(
                notes,
                ticket_creation_date,
                max_seconds_since_last_trouble=3600,
            )
            assert result is False

        trouble_repository._utils_repository.has_last_event_happened_recently.assert_called_with(
            notes, ticket_creation_date, max_seconds_since_last_event=3600, regex=AFFECTING_NOTE_REGEX
        )

    def was_last_trouble_detected_recently__reopen_trouble_note_found_test(
        self, trouble_repository, make_ticket_note, make_list_of_ticket_notes
    ):
        ticket_creation_date = "9/25/2020 6:31:54 AM"
        trouble_note_timestamp = "2021-01-02T11:00:16.71-05:00"

        note_1 = make_ticket_note(
            text="Dummy note",
            creation_date=str(parse(trouble_note_timestamp) - timedelta(seconds=10)),
        )
        note_2 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nRe-opening ticket.\nTrouble: Latency",
            creation_date=str(parse(trouble_note_timestamp)),
        )
        notes = make_list_of_ticket_notes(note_1, note_2)

        datetime_mock = Mock()

        new_now = parse(trouble_note_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(utils_repository_module, "datetime", new=datetime_mock):
            result = trouble_repository.was_last_trouble_detected_recently(
                notes,
                ticket_creation_date,
                max_seconds_since_last_trouble=3600,
            )
            assert result is True

        new_now = parse(trouble_note_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(utils_repository_module, "datetime", new=datetime_mock):
            result = trouble_repository.was_last_trouble_detected_recently(
                notes,
                ticket_creation_date,
                max_seconds_since_last_trouble=3600,
            )
            assert result is True

        new_now = parse(trouble_note_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(utils_repository_module, "datetime", new=datetime_mock):
            result = trouble_repository.was_last_trouble_detected_recently(
                notes,
                ticket_creation_date,
                max_seconds_since_last_trouble=3600,
            )
            assert result is False

        trouble_repository._utils_repository.has_last_event_happened_recently.assert_called_with(
            notes, ticket_creation_date, max_seconds_since_last_event=3600, regex=AFFECTING_NOTE_REGEX
        )

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
        events = [make_event()] * 5
        result = trouble_repository.are_bouncing_events_within_threshold(events)
        assert result is True

        events = [make_event()] * 10
        result = trouble_repository.are_bouncing_events_within_threshold(events)
        assert result is False

        events = [make_event()] * 5
        result = trouble_repository.are_bouncing_events_within_threshold(events, autoresolve=True)
        assert result is False

    def are_all_metrics_within_thresholds__bandwidth_metrics_ignored_test(
        self,
        trouble_repository,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
    ):
        lookup_interval_minutes = 30

        metrics = make_metrics(
            best_latency_ms_tx=139,
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
        link_status_and_metrics_object = make_link_status_and_metrics_object_with_events(metrics=metrics)
        link_status_and_metrics_objects = make_list_of_link_status_and_metrics_objects(link_status_and_metrics_object)
        links_by_edge = make_links_by_edge_object(links=link_status_and_metrics_objects)
        result = trouble_repository.are_all_metrics_within_thresholds(
            links_by_edge,
            lookup_interval_minutes=lookup_interval_minutes,
            check_bandwidth_troubles=False,
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
        link_status_and_metrics_object = make_link_status_and_metrics_object_with_events(metrics=metrics)
        link_status_and_metrics_objects = make_list_of_link_status_and_metrics_objects(link_status_and_metrics_object)
        links_by_edge = make_links_by_edge_object(links=link_status_and_metrics_objects)
        result = trouble_repository.are_all_metrics_within_thresholds(
            links_by_edge,
            lookup_interval_minutes=lookup_interval_minutes,
            check_bandwidth_troubles=False,
        )
        assert result is False

    def are_all_metrics_within_thresholds__bandwidth_metrics_taken_into_account_test(
        self,
        trouble_repository,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
    ):
        lookup_interval_minutes = 30

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
        link_status_and_metrics_object = make_link_status_and_metrics_object_with_events(metrics=metrics)
        link_status_and_metrics_objects = make_list_of_link_status_and_metrics_objects(link_status_and_metrics_object)
        links_by_edge = make_links_by_edge_object(links=link_status_and_metrics_objects)
        result = trouble_repository.are_all_metrics_within_thresholds(
            links_by_edge,
            lookup_interval_minutes=lookup_interval_minutes,
            check_bandwidth_troubles=True,
        )
        assert result is True

        metrics = make_metrics(
            best_latency_ms_tx=139,
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
        link_status_and_metrics_object = make_link_status_and_metrics_object_with_events(metrics=metrics)
        link_status_and_metrics_objects = make_list_of_link_status_and_metrics_objects(link_status_and_metrics_object)
        links_by_edge = make_links_by_edge_object(links=link_status_and_metrics_objects)
        result = trouble_repository.are_all_metrics_within_thresholds(
            links_by_edge,
            lookup_interval_minutes=lookup_interval_minutes,
            check_bandwidth_troubles=True,
        )
        assert result is False

    def are_all_metrics_within_thresholds__invalid_bandwidth_metrics_taken_into_account_test(
        self,
        trouble_repository,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
    ):
        lookup_interval_minutes = 30

        metrics = make_metrics(
            best_latency_ms_tx=139,
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
        link_status_and_metrics_object = make_link_status_and_metrics_object_with_events(metrics=metrics)
        link_status_and_metrics_objects = make_list_of_link_status_and_metrics_objects(link_status_and_metrics_object)
        links_by_edge = make_links_by_edge_object(links=link_status_and_metrics_objects)
        result = trouble_repository.are_all_metrics_within_thresholds(
            links_by_edge,
            lookup_interval_minutes=lookup_interval_minutes,
            check_bandwidth_troubles=True,
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
            bps_of_best_path_tx=0,
            bytes_rx=1000000000,
            bps_of_best_path_rx=0,
        )
        link_status_and_metrics_object = make_link_status_and_metrics_object_with_events(metrics=metrics)
        link_status_and_metrics_objects = make_list_of_link_status_and_metrics_objects(link_status_and_metrics_object)
        links_by_edge = make_links_by_edge_object(links=link_status_and_metrics_objects)
        result = trouble_repository.are_all_metrics_within_thresholds(
            links_by_edge,
            lookup_interval_minutes=lookup_interval_minutes,
            check_bandwidth_troubles=True,
        )
        assert result is False
