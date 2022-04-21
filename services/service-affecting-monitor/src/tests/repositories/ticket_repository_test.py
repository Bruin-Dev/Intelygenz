import os

from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import patch

from application import AffectingTroubles
from application.repositories import ticket_repository as ticket_repository_module
from config import testconfig


class TestTicketRepository:
    def instance_test(self, ticket_repository, trouble_repository, utils_repository):
        assert ticket_repository._trouble_repository is trouble_repository
        assert ticket_repository._utils_repository is utils_repository
        assert ticket_repository._config is testconfig

    def is_task_resolved_test(self, ticket_repository, make_detail_item):
        detail_item = make_detail_item(status='I')
        result = ticket_repository.is_task_resolved(detail_item)
        assert result is False

        detail_item = make_detail_item(status='R')
        result = ticket_repository.is_task_resolved(detail_item)
        assert result is True

    def was_ticket_created_by_automation_engine_test(self, ticket_repository, make_ticket):
        ticket = make_ticket(created_by='Travis Touchdown')
        result = ticket_repository.was_ticket_created_by_automation_engine(ticket)
        assert result is False

        ticket = make_ticket(created_by='Intelygenz Ai')
        result = ticket_repository.was_ticket_created_by_automation_engine(ticket)
        assert result is True

    def is_autoresolve_threshold_maxed_out_test(self, ticket_repository, make_ticket_note, make_list_of_ticket_notes):
        note = make_ticket_note(text=f"#*MetTel's IPA*#\nAuto-resolving task for serial: VC1234567")

        notes = make_list_of_ticket_notes(note)
        result = ticket_repository.is_autoresolve_threshold_maxed_out(notes)
        assert result is False

        notes = make_list_of_ticket_notes(note, note)
        result = ticket_repository.is_autoresolve_threshold_maxed_out(notes)
        assert result is False

        notes = make_list_of_ticket_notes(note, note, note)
        result = ticket_repository.is_autoresolve_threshold_maxed_out(notes)
        assert result is True

    def get_notes_appended_since_latest_reopen_or_ticket_creation__no_reopen_note_found_test(
            self, ticket_repository, make_ticket_note, make_list_of_ticket_notes):
        note_1 = make_ticket_note(text="Dummy note")
        note_2 = make_ticket_note(text=f"#*MetTel's IPA*#\nAuto-resolving task for serial: VC1234567")
        notes = make_list_of_ticket_notes(note_1, note_2)

        result = ticket_repository.get_notes_appended_since_latest_reopen_or_ticket_creation(notes)
        assert result is notes

    def get_notes_appended_since_latest_reopen_or_ticket_creation__reopen_note_found_test(
            self, ticket_repository, make_ticket_note, make_list_of_ticket_notes):
        current_datetime = datetime.now()

        note_1 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime - timedelta(seconds=10)))
        note_2 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nRe-opening ticket.\nTrouble: Latency",
            creation_date=str(current_datetime),
        )
        notes = make_list_of_ticket_notes(note_1, note_2)
        result = ticket_repository.get_notes_appended_since_latest_reopen_or_ticket_creation(notes)
        assert result == [note_2]

        note_1 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime - timedelta(seconds=20)))
        note_2 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nRe-opening ticket.\nTrouble: Latency",
            creation_date=str(current_datetime - timedelta(seconds=10)),
        )
        note_3 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime))
        notes = make_list_of_ticket_notes(note_1, note_2, note_3)
        result = ticket_repository.get_notes_appended_since_latest_reopen_or_ticket_creation(notes)
        assert result == [note_2, note_3]

        note_1 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime - timedelta(seconds=40)))
        note_2 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nRe-opening ticket.\nTrouble: Latency",
            creation_date=str(current_datetime - timedelta(seconds=30)),
        )
        note_3 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime - timedelta(seconds=20)))
        note_4 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nRe-opening ticket.\nTrouble: Latency",
            creation_date=str(current_datetime - timedelta(seconds=10)),
        )
        note_5 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime))
        note_6 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime))
        note_7 = make_ticket_note(text="Dummy note", creation_date=str(current_datetime))
        notes = make_list_of_ticket_notes(note_1, note_2, note_3, note_4, note_5, note_6, note_7)
        result = ticket_repository.get_notes_appended_since_latest_reopen_or_ticket_creation(notes)
        assert result == [note_4, note_5, note_6, note_7]

    def find_task_by_serial_number_test(self, ticket_repository, make_detail_item, make_list_of_detail_items):
        serial_number = 'VC1234567'

        detail_item_1 = make_detail_item(value='VC0000000')
        detail_items = make_list_of_detail_items(detail_item_1)
        result = ticket_repository.find_task_by_serial_number(detail_items, serial_number)
        assert result is None

        detail_item_1 = make_detail_item(value=serial_number)
        detail_items = make_list_of_detail_items(detail_item_1)
        result = ticket_repository.find_task_by_serial_number(detail_items, serial_number)
        assert result is detail_item_1

    def is_ticket_used_for_reoccurring_affecting_troubles_test(self, ticket_repository, make_ticket_note):
        note = make_ticket_note(text=f"#*MetTel's IPA*#\nTrouble: Latency")
        result = ticket_repository.is_ticket_used_for_reoccurring_affecting_troubles([note])
        assert result is True

        note = make_ticket_note(text="Dummy note")
        result = ticket_repository.is_ticket_used_for_reoccurring_affecting_troubles([note])
        assert result is False

    def is_there_any_note_for_trouble_test(self, ticket_repository, make_ticket_note, make_list_of_ticket_notes):
        trouble = AffectingTroubles.LATENCY

        note_1 = make_ticket_note(text="Dummy note")
        note_2 = make_ticket_note(text="Dummy note 2")
        notes = make_list_of_ticket_notes(note_1, note_2)
        result = ticket_repository.is_there_any_note_for_trouble(notes, trouble)
        assert result is False

        note_1 = make_ticket_note(text="Dummy note")
        note_2 = make_ticket_note(text=f"#*MetTel's IPA*#\nTrouble: Packet Loss")
        notes = make_list_of_ticket_notes(note_1, note_2)
        result = ticket_repository.is_there_any_note_for_trouble(notes, trouble)
        assert result is False

        note_1 = make_ticket_note(text="Dummy note")
        note_2 = make_ticket_note(text=f"#*MetTel's IPA*#\nTrouble: Latency")
        notes = make_list_of_ticket_notes(note_1, note_2)
        result = ticket_repository.is_there_any_note_for_trouble(notes, trouble)
        assert result is True

        note_1 = make_ticket_note(text="Dummy note")
        note_2 = make_ticket_note(text=f"#*MetTel's IPA*#\nTrouble: Packet Loss")
        note_3 = make_ticket_note(text=f"#*MetTel's IPA*#\nTrouble: Latency")
        notes = make_list_of_ticket_notes(note_1, note_2, note_3)
        result = ticket_repository.is_there_any_note_for_trouble(notes, trouble)
        assert result is True

    def are_there_any_other_troubles_test(self, ticket_repository, make_ticket_note):
        trouble = AffectingTroubles.BOUNCING

        note = make_ticket_note(text=f"#*MetTel's IPA*#\nTrouble: Latency")
        result = ticket_repository.are_there_any_other_troubles(ticket_notes=[note], observed_trouble=trouble)
        assert result is True

        note = make_ticket_note(text=f"#*MetTel's IPA*#\nTrouble: Circuit Instability")
        result = ticket_repository.are_there_any_other_troubles(ticket_notes=[note], observed_trouble=trouble)
        assert result is False

        note = make_ticket_note(text="Dummy note")
        result = ticket_repository.are_there_any_other_troubles(ticket_notes=[note], observed_trouble=trouble)
        assert result is False

    def get_build_note_fn_by_trouble_test(self, ticket_repository):
        trouble = AffectingTroubles.LATENCY
        result = ticket_repository.get_build_note_fn_by_trouble(trouble)
        assert result is ticket_repository.build_latency_trouble_note

        trouble = AffectingTroubles.PACKET_LOSS
        result = ticket_repository.get_build_note_fn_by_trouble(trouble)
        assert result is ticket_repository.build_packet_loss_trouble_note

        trouble = AffectingTroubles.JITTER
        result = ticket_repository.get_build_note_fn_by_trouble(trouble)
        assert result is ticket_repository.build_jitter_trouble_note

        trouble = AffectingTroubles.BANDWIDTH_OVER_UTILIZATION
        result = ticket_repository.get_build_note_fn_by_trouble(trouble)
        assert result is ticket_repository.build_bandwidth_trouble_note

        trouble = AffectingTroubles.BOUNCING
        result = ticket_repository.get_build_note_fn_by_trouble(trouble)
        assert result is ticket_repository.build_bouncing_trouble_note

    def build_latency_trouble_note_test(
            self, ticket_repository, frozen_datetime, make_edge_full_id, make_cached_edge, make_links_configuration,
            make_list_of_links_configurations, make_edge, make_link, make_metrics, make_structured_metrics_object,
            make_structured_metrics_object_with_cache_and_contact_info):
        edge = make_edge(name='Travis Touchdown')

        edge_full_id = make_edge_full_id(host='mettel.velocloud.net', enterprise_id=1, edge_id=1)
        links_configuration = make_links_configuration(
            interfaces=['REX', 'RAY'],
            mode='PUBLIC',
            type_='WIRELESS',
        )
        links_configurations = make_list_of_links_configurations(links_configuration)
        edge_cache_info = make_cached_edge(
            full_id=edge_full_id,
            links_configuration=links_configurations,
        )

        link = make_link(interface='REX', display_name='Metal Gear REX', ip_address='34.56.3.1')
        link_metrics = make_metrics(best_latency_ms_tx=101010, best_latency_ms_rx=202020)

        structured_metrics = make_structured_metrics_object(edge_info=edge, link_info=link, metrics=link_metrics)
        link_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=structured_metrics,
            cache_info=edge_cache_info,
        )

        current_datetime = frozen_datetime.now()
        with patch.multiple(ticket_repository_module, datetime=frozen_datetime, timezone=Mock()):
            result = ticket_repository.build_latency_trouble_note(link_complete_info)
            expected = os.linesep.join([
                "#*MetTel's IPA*#",
                "Trouble: Latency",
                "",
                "Edge Name: Travis Touchdown",
                "Name: Metal Gear REX",
                "Interface: REX",
                "IP Address: 34.56.3.1",
                "Link Type: Public Wireless",
                "",
                "Interval for Scan: 30 minutes",
                "Threshold: 140 ms",
                "Receive: 202020 ms",
                "Transfer: 101010 ms",
                "",
                f"Scan Time: {str(current_datetime)}",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/links/] - "
                "[Events|https://mettel.velocloud.net/#!/operator/customer/1/monitor/events/]",
            ])
            assert result == expected

            result = ticket_repository.build_latency_trouble_note(link_complete_info, is_reopen_note=True)
            expected = os.linesep.join([
                "#*MetTel's IPA*#",
                "Re-opening ticket.",
                "",
                "Trouble: Latency",
                "",
                "Edge Name: Travis Touchdown",
                "Name: Metal Gear REX",
                "Interface: REX",
                "IP Address: 34.56.3.1",
                "Link Type: Public Wireless",
                "",
                "Interval for Scan: 30 minutes",
                "Threshold: 140 ms",
                "Receive: 202020 ms",
                "Transfer: 101010 ms",
                "",
                f"Scan Time: {str(current_datetime)}",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/links/] - "
                "[Events|https://mettel.velocloud.net/#!/operator/customer/1/monitor/events/]",
            ])
            assert result == expected

    def build_packet_loss_trouble_note_test(
            self, ticket_repository, frozen_datetime, make_edge_full_id, make_cached_edge, make_links_configuration,
            make_list_of_links_configurations, make_edge, make_link, make_metrics, make_structured_metrics_object,
            make_structured_metrics_object_with_cache_and_contact_info):
        edge = make_edge(name='Travis Touchdown')

        edge_full_id = make_edge_full_id(host='mettel.velocloud.net', enterprise_id=1, edge_id=1)
        links_configuration = make_links_configuration(
            interfaces=['REX', 'RAY'],
            mode='PUBLIC',
            type_='WIRELESS',
        )
        links_configurations = make_list_of_links_configurations(links_configuration)
        edge_cache_info = make_cached_edge(
            full_id=edge_full_id,
            links_configuration=links_configurations,
        )

        link = make_link(interface='REX', display_name='Metal Gear REX', ip_address='34.56.3.1')
        link_metrics = make_metrics(best_packet_loss_tx=101010, best_packet_loss_rx=202020)

        structured_metrics = make_structured_metrics_object(edge_info=edge, link_info=link, metrics=link_metrics)
        link_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=structured_metrics,
            cache_info=edge_cache_info,
        )

        current_datetime = frozen_datetime.now()
        with patch.multiple(ticket_repository_module, datetime=frozen_datetime, timezone=Mock()):
            result = ticket_repository.build_packet_loss_trouble_note(link_complete_info)
            expected = os.linesep.join([
                "#*MetTel's IPA*#",
                "Trouble: Packet Loss",
                "",
                "Edge Name: Travis Touchdown",
                "Name: Metal Gear REX",
                "Interface: REX",
                "IP Address: 34.56.3.1",
                "Link Type: Public Wireless",
                "",
                "Interval for Scan: 30 minutes",
                "Threshold: 8 packets",
                "Receive: 202020 packets",
                "Transfer: 101010 packets",
                "",
                f"Scan Time: {str(current_datetime)}",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/links/] - "
                "[Events|https://mettel.velocloud.net/#!/operator/customer/1/monitor/events/]",
            ])
            assert result == expected

            result = ticket_repository.build_packet_loss_trouble_note(link_complete_info, is_reopen_note=True)
            expected = os.linesep.join([
                "#*MetTel's IPA*#",
                "Re-opening ticket.",
                "",
                "Trouble: Packet Loss",
                "",
                "Edge Name: Travis Touchdown",
                "Name: Metal Gear REX",
                "Interface: REX",
                "IP Address: 34.56.3.1",
                "Link Type: Public Wireless",
                "",
                "Interval for Scan: 30 minutes",
                "Threshold: 8 packets",
                "Receive: 202020 packets",
                "Transfer: 101010 packets",
                "",
                f"Scan Time: {str(current_datetime)}",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/links/] - "
                "[Events|https://mettel.velocloud.net/#!/operator/customer/1/monitor/events/]",
            ])
            assert result == expected

    def build_jitter_trouble_note_test(
            self, ticket_repository, frozen_datetime, make_edge_full_id, make_cached_edge, make_links_configuration,
            make_list_of_links_configurations, make_edge, make_link, make_metrics, make_structured_metrics_object,
            make_structured_metrics_object_with_cache_and_contact_info):
        edge = make_edge(name='Travis Touchdown')

        edge_full_id = make_edge_full_id(host='mettel.velocloud.net', enterprise_id=1, edge_id=1)
        links_configuration = make_links_configuration(
            interfaces=['REX', 'RAY'],
            mode='PUBLIC',
            type_='WIRELESS',
        )
        links_configurations = make_list_of_links_configurations(links_configuration)
        edge_cache_info = make_cached_edge(
            full_id=edge_full_id,
            links_configuration=links_configurations,
        )

        link = make_link(interface='REX', display_name='Metal Gear REX', ip_address='34.56.3.1')
        link_metrics = make_metrics(best_jitter_ms_tx=101010, best_jitter_ms_rx=202020)

        structured_metrics = make_structured_metrics_object(edge_info=edge, link_info=link, metrics=link_metrics)
        link_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=structured_metrics,
            cache_info=edge_cache_info,
        )

        current_datetime = frozen_datetime.now()
        with patch.multiple(ticket_repository_module, datetime=frozen_datetime, timezone=Mock()):
            result = ticket_repository.build_jitter_trouble_note(link_complete_info)
            expected = os.linesep.join([
                "#*MetTel's IPA*#",
                "Trouble: Jitter",
                "",
                "Edge Name: Travis Touchdown",
                "Name: Metal Gear REX",
                "Interface: REX",
                "IP Address: 34.56.3.1",
                "Link Type: Public Wireless",
                "",
                "Interval for Scan: 30 minutes",
                "Threshold: 50 ms",
                "Receive: 202020 ms",
                "Transfer: 101010 ms",
                "",
                f"Scan Time: {str(current_datetime)}",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/links/] - "
                "[Events|https://mettel.velocloud.net/#!/operator/customer/1/monitor/events/]",
            ])
            assert result == expected

            result = ticket_repository.build_jitter_trouble_note(link_complete_info, is_reopen_note=True)
            expected = os.linesep.join([
                "#*MetTel's IPA*#",
                "Re-opening ticket.",
                "",
                "Trouble: Jitter",
                "",
                "Edge Name: Travis Touchdown",
                "Name: Metal Gear REX",
                "Interface: REX",
                "IP Address: 34.56.3.1",
                "Link Type: Public Wireless",
                "",
                "Interval for Scan: 30 minutes",
                "Threshold: 50 ms",
                "Receive: 202020 ms",
                "Transfer: 101010 ms",
                "",
                f"Scan Time: {str(current_datetime)}",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/links/] - "
                "[Events|https://mettel.velocloud.net/#!/operator/customer/1/monitor/events/]",
            ])
            assert result == expected

    def build_bandwidth_trouble_note_test(
            self, ticket_repository, frozen_datetime, make_edge_full_id, make_cached_edge, make_links_configuration,
            make_list_of_links_configurations, make_edge, make_link, make_metrics, make_structured_metrics_object,
            make_structured_metrics_object_with_cache_and_contact_info):
        edge = make_edge(name='Travis Touchdown')

        edge_full_id = make_edge_full_id(host='mettel.velocloud.net', enterprise_id=1, edge_id=1)
        links_configuration = make_links_configuration(
            interfaces=['REX', 'RAY'],
            mode='PUBLIC',
            type_='WIRELESS',
        )
        links_configurations = make_list_of_links_configurations(links_configuration)
        edge_cache_info = make_cached_edge(
            full_id=edge_full_id,
            links_configuration=links_configurations,
        )

        link = make_link(interface='REX', display_name='Metal Gear REX', ip_address='34.56.3.1')
        link_metrics = make_metrics(
            bytes_tx=101010, bytes_rx=202020,
            bps_of_best_path_tx=1, bps_of_best_path_rx=1,
        )

        structured_metrics = make_structured_metrics_object(edge_info=edge, link_info=link, metrics=link_metrics)
        link_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=structured_metrics,
            cache_info=edge_cache_info,
        )

        current_datetime = frozen_datetime.now()
        with patch.multiple(ticket_repository_module, datetime=frozen_datetime, timezone=Mock()):
            result = ticket_repository.build_bandwidth_trouble_note(link_complete_info)
            expected = os.linesep.join([
                "#*MetTel's IPA*#",
                "Trouble: Bandwidth Over Utilization",
                "",
                "Edge Name: Travis Touchdown",
                "Name: Metal Gear REX",
                "Interface: REX",
                "IP Address: 34.56.3.1",
                "Link Type: Public Wireless",
                "",
                "Interval for Scan: 30 minutes",
                "Throughput (Receive): 897.867 bps",
                "Bandwidth (Receive): 1 bps",
                "Threshold (Receive): 90% (0.9 bps)",
                "Throughput (Transfer): 448.933 bps",
                "Bandwidth (Transfer): 1 bps",
                "Threshold (Transfer): 90% (0.9 bps)",
                "",
                f"Scan Time: {str(current_datetime)}",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/links/] - "
                "[Events|https://mettel.velocloud.net/#!/operator/customer/1/monitor/events/]",
            ])
            assert result == expected

            result = ticket_repository.build_bandwidth_trouble_note(link_complete_info, is_reopen_note=True)
            expected = os.linesep.join([
                "#*MetTel's IPA*#",
                "Re-opening ticket.",
                "",
                "Trouble: Bandwidth Over Utilization",
                "",
                "Edge Name: Travis Touchdown",
                "Name: Metal Gear REX",
                "Interface: REX",
                "IP Address: 34.56.3.1",
                "Link Type: Public Wireless",
                "",
                "Interval for Scan: 30 minutes",
                "Throughput (Receive): 897.867 bps",
                "Bandwidth (Receive): 1 bps",
                "Threshold (Receive): 90% (0.9 bps)",
                "Throughput (Transfer): 448.933 bps",
                "Bandwidth (Transfer): 1 bps",
                "Threshold (Transfer): 90% (0.9 bps)",
                "",
                f"Scan Time: {str(current_datetime)}",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/links/] - "
                "[Events|https://mettel.velocloud.net/#!/operator/customer/1/monitor/events/]",
            ])
            assert result == expected

    def build_bouncing_trouble_note_test(
            self, ticket_repository, frozen_datetime, make_edge_full_id, make_cached_edge, make_links_configuration,
            make_list_of_links_configurations, make_edge, make_link, make_metrics, make_event,
            make_structured_metrics_object_with_events, make_structured_metrics_object_with_cache_and_contact_info):
        edge = make_edge(name='Travis Touchdown')

        edge_full_id = make_edge_full_id(host='mettel.velocloud.net', enterprise_id=1, edge_id=1)
        links_configuration = make_links_configuration(
            interfaces=['REX', 'RAY'],
            mode='PUBLIC',
            type_='WIRELESS',
        )
        links_configurations = make_list_of_links_configurations(links_configuration)
        edge_cache_info = make_cached_edge(
            full_id=edge_full_id,
            links_configuration=links_configurations,
        )

        link = make_link(interface='REX', display_name='Metal Gear REX', ip_address='34.56.3.1')
        link_metrics = make_metrics(best_latency_ms_tx=101010, best_latency_ms_rx=202020)
        event = make_event()
        events = [event] * 12

        structured_metrics = make_structured_metrics_object_with_events(edge_info=edge, link_info=link,
                                                                        metrics=link_metrics, events=events)
        link_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=structured_metrics,
            cache_info=edge_cache_info,
        )

        current_datetime = frozen_datetime.now()
        with patch.multiple(ticket_repository_module, datetime=frozen_datetime, timezone=Mock()):
            result = ticket_repository.build_bouncing_trouble_note(link_complete_info)
            expected = os.linesep.join([
                "#*MetTel's IPA*#",
                "Trouble: Circuit Instability",
                "",
                "Edge Name: Travis Touchdown",
                "Name: Metal Gear REX",
                "Interface: REX",
                "IP Address: 34.56.3.1",
                "Link Type: Public Wireless",
                "",
                "Interval for Scan: 60 minutes",
                "Threshold: 10 events",
                "Events: 12",
                "",
                f"Scan Time: {str(current_datetime)}",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/links/]"
            ])
            assert result == expected

            result = ticket_repository.build_bouncing_trouble_note(link_complete_info, is_reopen_note=True)
            expected = os.linesep.join([
                "#*MetTel's IPA*#",
                "Re-opening ticket.",
                "",
                "Trouble: Circuit Instability",
                "",
                "Edge Name: Travis Touchdown",
                "Name: Metal Gear REX",
                "Interface: REX",
                "IP Address: 34.56.3.1",
                "Link Type: Public Wireless",
                "",
                "Interval for Scan: 60 minutes",
                "Threshold: 10 events",
                "Events: 12",
                "",
                f"Scan Time: {str(current_datetime)}",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/1/monitor/edge/1/links/]"
            ])
            assert result == expected

    def is_ticket_task_in_ipa_queue__in_ipa_test(self, ticket_repository, make_detail_item):
        ticket_id = '432532'
        serial_number = 'VC1234567'
        current_task_name = 'IPA Investigate'
        detail_item = make_detail_item(id_=ticket_id, value=serial_number, current_task_name=current_task_name)

        result = ticket_repository.is_ticket_task_in_ipa_queue(detail_item)

        assert result

    def is_ticket_task_in_ipa_queue__not_in_ipa_test(self, ticket_repository, make_detail_item):
        ticket_id = '432532'
        serial_number = 'VC1234567'
        current_task_name = 'Task Investigate'
        detail_item = make_detail_item(id_=ticket_id, value=serial_number, current_task_name=current_task_name)

        result = ticket_repository.is_ticket_task_in_ipa_queue(detail_item)

        assert not result

    def build_reminder_note_test(self, ticket_repository):
        expected = os.linesep.join([
            "#*MetTel's IPA*#",
            'Client Reminder'
        ])

        result = ticket_repository.build_reminder_note()

        assert result == expected
