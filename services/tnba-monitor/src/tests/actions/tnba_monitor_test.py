from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest

from apscheduler.util import undefined
from asynctest import CoroutineMock
from dateutil.parser import parse
from pytz import utc

from application.actions.tnba_monitor import TNBAMonitor
from application.actions import tnba_monitor as tnba_monitor_module
from config import testconfig


class TestTNBAMonitor:

    def instance_test(self, tnba_monitor, event_bus, logger, scheduler, metrics_repository, t7_repository,
                      customer_cache_repository, bruin_repository, velocloud_repository, ticket_repository,
                      prediction_repository, notifications_repository, utils_repository):
        assert tnba_monitor._event_bus is event_bus
        assert tnba_monitor._logger is logger
        assert tnba_monitor._scheduler is scheduler
        assert tnba_monitor._config is testconfig
        assert tnba_monitor._metrics_repository is metrics_repository
        assert tnba_monitor._t7_repository is t7_repository
        assert tnba_monitor._ticket_repository is ticket_repository
        assert tnba_monitor._customer_cache_repository is customer_cache_repository
        assert tnba_monitor._bruin_repository is bruin_repository
        assert tnba_monitor._velocloud_repository is velocloud_repository
        assert tnba_monitor._prediction_repository is prediction_repository
        assert tnba_monitor._notifications_repository is notifications_repository
        assert tnba_monitor._utils_repository is utils_repository

        assert tnba_monitor._customer_cache_by_serial == {}
        assert tnba_monitor._edge_status_by_serial == {}
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def start_tnba_automated_process_with_exec_on_start_test(self, tnba_monitor):
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            with patch.object(tnba_monitor_module, 'timezone', new=Mock()):
                await tnba_monitor.start_tnba_automated_process(exec_on_start=True)

        tnba_monitor._scheduler.add_job.assert_called_once_with(
            tnba_monitor._run_tickets_polling, 'interval',
            seconds=testconfig.MONITOR_CONFIG['monitoring_interval_seconds'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_run_tickets_polling',
        )

    @pytest.mark.asyncio
    async def start_tnba_automated_process_with_no_exec_on_start_test(self, tnba_monitor):
        await tnba_monitor.start_tnba_automated_process(exec_on_start=False)

        tnba_monitor._scheduler.add_job.assert_called_once_with(
            tnba_monitor._run_tickets_polling, 'interval',
            seconds=testconfig.MONITOR_CONFIG['monitoring_interval_seconds'],
            next_run_time=undefined,
            replace_existing=False,
            id='_run_tickets_polling',
        )

    @pytest.mark.asyncio
    async def run_tickets_polling_with_get_cache_request_having_202_status_test(self, tnba_monitor,
                                                                                make_rpc_response):
        get_cache_response = make_rpc_response(
            body='Cache is still being built for host(s): mettel_velocloud.net, metvco03.mettel.net',
            status=202,
        )

        tnba_monitor._customer_cache_repository.get_cache_for_tnba_monitoring.return_value = get_cache_response

        await tnba_monitor._run_tickets_polling()

        tnba_monitor._customer_cache_repository.get_cache_for_tnba_monitoring.assert_awaited_once()
        tnba_monitor._process_ticket_detail.assert_not_awaited()
        assert tnba_monitor._customer_cache_by_serial == {}

    @pytest.mark.asyncio
    async def run_tickets_polling_with_get_cache_request_having_non_2xx_status_and_different_from_202_test(
            self, tnba_monitor, make_rpc_response):
        get_cache_response = make_rpc_response(
            body='No edges were found for the specified filters',
            status=404,
        )

        tnba_monitor._customer_cache_repository.get_cache_for_tnba_monitoring.return_value = get_cache_response

        await tnba_monitor._run_tickets_polling()

        tnba_monitor._customer_cache_repository.get_cache_for_tnba_monitoring.assert_awaited_once()
        tnba_monitor._process_ticket_detail.assert_not_awaited()
        assert tnba_monitor._customer_cache_by_serial == {}

    @pytest.mark.asyncio
    async def run_tickets_polling_with_empty_list_of_edges_statuses_test(self, tnba_monitor, make_rpc_response,
                                                                         edge_cached_info_1, edge_cached_info_2):
        customer_cache = [
            edge_cached_info_1,
            edge_cached_info_2,
        ]
        get_cache_response = make_rpc_response(
            body=customer_cache,
            status=200,
        )

        edges_statuses = []

        tnba_monitor._customer_cache_repository.get_cache_for_tnba_monitoring.return_value = get_cache_response
        tnba_monitor._velocloud_repository.get_edges_for_tnba_monitoring.return_value = edges_statuses
        tnba_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await tnba_monitor._run_tickets_polling()

        tnba_monitor._customer_cache_repository.get_cache_for_tnba_monitoring.assert_awaited_once()
        tnba_monitor._velocloud_repository.get_edges_for_tnba_monitoring.assert_awaited_once()
        tnba_monitor._notifications_repository.send_slack_message.assert_awaited_once()
        tnba_monitor._process_ticket_detail.assert_not_awaited()
        assert tnba_monitor._customer_cache_by_serial == {}
        assert tnba_monitor._edge_status_by_serial == {}

    @pytest.mark.asyncio
    async def run_tickets_polling_no_link_metrics_test(
            self, tnba_monitor, make_edge_with_links_info, make_rpc_response, edge_cached_info_1, edge_cached_info_2,
            edge_1_connected, link_1_stable):
        customer_cache = [
            edge_cached_info_1,
            edge_cached_info_2,
        ]
        get_cache_response = make_rpc_response(
            body=customer_cache,
            status=200,
        )

        edge_with_links = make_edge_with_links_info(edge_info=edge_1_connected, links_info=[link_1_stable])
        edges_statuses = [
            edge_with_links,
        ]

        link_metrics = []

        link_metrics_return = {
            'body': link_metrics,
            'status': 200
        }
        tnba_monitor._customer_cache_repository.get_cache_for_tnba_monitoring.return_value = get_cache_response
        tnba_monitor._velocloud_repository.get_edges_for_tnba_monitoring.return_value = edges_statuses
        tnba_monitor._velocloud_repository.get_links_metrics_for_autoresolve.return_value = link_metrics_return

        tnba_monitor._filter_edges_in_customer_cache_and_edges_statuses = Mock(return_value=(
            customer_cache, edges_statuses
        ))
        tnba_monitor._filter_tickets_and_details_related_to_edges_under_monitoring.return_value = []
        tnba_monitor._map_ticket_details_with_predictions.return_value = []

        tnba_monitor._get_all_open_tickets_with_details_for_monitored_companies = CoroutineMock()
        tnba_monitor._filter_irrelevant_notes_in_tickets = Mock()
        tnba_monitor._get_predictions_by_ticket_id = CoroutineMock()
        tnba_monitor._remove_erroneous_predictions = Mock()
        tnba_monitor._transform_tickets_into_detail_objects = Mock(return_value=[])
        tnba_monitor._filter_resolved_ticket_details = Mock()
        tnba_monitor._filter_outage_ticket_details_based_on_last_outage = Mock()
        tnba_monitor._process_ticket_detail = CoroutineMock()
        tnba_monitor._append_tnba_notes = CoroutineMock()

        await tnba_monitor._run_tickets_polling()

        tnba_monitor._velocloud_repository.get_events_by_serial_and_interface.assert_not_awaited()
        tnba_monitor._velocloud_repository._structure_link_and_event_metrics.assert_not_called()
        assert tnba_monitor._link_metrics_and_events_by_serial == {}

    @pytest.mark.asyncio
    async def run_tickets_polling_with_customer_cache_ready_and_edge_statuses_received_and_no_notes_to_append_test(
            self, tnba_monitor, make_edge_with_links_info, make_rpc_response, edge_cached_info_1, edge_cached_info_2,
            edge_1_connected, link_1_stable, make_metrics, make_events_by_serial_and_interface):
        customer_cache = [
            edge_cached_info_1,
            edge_cached_info_2,
        ]
        get_cache_response = make_rpc_response(
            body=customer_cache,
            status=200,
        )

        edge_with_links = make_edge_with_links_info(edge_info=edge_1_connected, links_info=[link_1_stable])
        edges_statuses = [
            edge_with_links,
        ]
        link_metrics = make_metrics()

        link_metrics_return = {
            'body': link_metrics,
            'status': 200
        }
        events_return = make_events_by_serial_and_interface()

        link_and_event_metrics = {
            'some.serial': [{'link_metrics': link_metrics, 'link_events': []}]
        }

        tnba_monitor._customer_cache_repository.get_cache_for_tnba_monitoring.return_value = get_cache_response
        tnba_monitor._velocloud_repository.get_edges_for_tnba_monitoring.return_value = edges_statuses
        tnba_monitor._velocloud_repository.get_links_metrics_for_autoresolve.return_value = link_metrics_return
        tnba_monitor._velocloud_repository.get_events_by_serial_and_interface.return_value = events_return
        tnba_monitor._velocloud_repository._structure_link_and_event_metrics.return_value = link_and_event_metrics
        tnba_monitor._filter_edges_in_customer_cache_and_edges_statuses = Mock(return_value=(
            customer_cache, edges_statuses
        ))
        tnba_monitor._filter_tickets_and_details_related_to_edges_under_monitoring.return_value = []
        tnba_monitor._map_ticket_details_with_predictions.return_value = []

        # Skip most of the logic, since the relevant part is to check if TNBA notes are appended or not
        tnba_monitor._get_all_open_tickets_with_details_for_monitored_companies = CoroutineMock()
        tnba_monitor._filter_irrelevant_notes_in_tickets = Mock()
        tnba_monitor._get_predictions_by_ticket_id = CoroutineMock()
        tnba_monitor._remove_erroneous_predictions = Mock()
        tnba_monitor._transform_tickets_into_detail_objects = Mock(return_value=[])
        tnba_monitor._filter_resolved_ticket_details = Mock()
        tnba_monitor._filter_outage_ticket_details_based_on_last_outage = Mock()
        tnba_monitor._process_ticket_detail = CoroutineMock()
        tnba_monitor._append_tnba_notes = CoroutineMock()

        await tnba_monitor._run_tickets_polling()

        tnba_monitor._append_tnba_notes.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_tickets_polling_with_customer_cache_ready_and_edge_statuses_received_and_notes_to_append_test(
            self, tnba_monitor, make_edge_with_links_info, make_detail_object_with_predictions,
            make_payload_for_note_append_with_ticket_id, make_rpc_response, edge_cached_info_1, edge_cached_info_2,
            edge_1_connected, link_1_stable, make_metrics, make_events_by_serial_and_interface):
        customer_cache = [
            edge_cached_info_1,
            edge_cached_info_2,
        ]
        get_cache_response = make_rpc_response(
            body=customer_cache,
            status=200,
        )

        edge_with_links = make_edge_with_links_info(edge_info=edge_1_connected, links_info=[link_1_stable])
        edges_statuses = [
            edge_with_links,
        ]

        link_metrics = make_metrics()

        link_metrics_return = {
            'body': link_metrics,
            'status': 200
        }
        events_return = make_events_by_serial_and_interface()

        link_and_event_metrics = {
            'some.serial': [{'link_metrics': link_metrics, 'link_events': []}]
        }

        tnba_monitor._customer_cache_repository.get_cache_for_tnba_monitoring.return_value = get_cache_response
        tnba_monitor._velocloud_repository.get_edges_for_tnba_monitoring.return_value = edges_statuses
        tnba_monitor._velocloud_repository.get_links_metrics_for_autoresolve.return_value = link_metrics_return
        tnba_monitor._velocloud_repository.get_events_by_serial_and_interface.return_value = events_return
        tnba_monitor._velocloud_repository._structure_link_and_event_metrics.return_value = link_and_event_metrics
        tnba_monitor._filter_edges_in_customer_cache_and_edges_statuses = Mock(return_value=(
            customer_cache, edges_statuses
        ))
        tnba_monitor._filter_tickets_and_details_related_to_edges_under_monitoring.return_value = []

        # Skip most of the logic, since the relevant part is to check if TNBA notes are appended or not
        tnba_monitor._get_all_open_tickets_with_details_for_monitored_companies = CoroutineMock()
        tnba_monitor._filter_irrelevant_notes_in_tickets = Mock()
        tnba_monitor._get_predictions_by_ticket_id = CoroutineMock()
        tnba_monitor._remove_erroneous_predictions = Mock()
        tnba_monitor._transform_tickets_into_detail_objects = Mock(return_value=[])
        tnba_monitor._filter_resolved_ticket_details = Mock()
        tnba_monitor._filter_outage_ticket_details_based_on_last_outage = Mock()
        tnba_monitor._append_tnba_notes = CoroutineMock()

        # Let's simulate that, after processing some details, a few TNBA notes were created to be appended to a ticket
        detail_object = make_detail_object_with_predictions()
        tnba_monitor._map_ticket_details_with_predictions.return_value = [detail_object]

        tnba_note_1 = make_payload_for_note_append_with_ticket_id(ticket_id=1, text='This is TNBA note #1')
        tnba_note_2 = make_payload_for_note_append_with_ticket_id(ticket_id=2, text='This is TNBA note #2')
        tnba_notes = [
            tnba_note_1,
            tnba_note_2,
        ]

        def __fake_process_ticket_detail(*args, **kwargs):
            for note in tnba_notes:
                tnba_monitor._tnba_notes_to_append.append(note)

        tnba_monitor._process_ticket_detail = CoroutineMock(side_effect=__fake_process_ticket_detail)

        await tnba_monitor._run_tickets_polling()

        tnba_monitor._append_tnba_notes.assert_awaited_once()

    def filter_edges_in_customer_cache_and_edges_statuses_test(self, make_edge_with_links_info, edge_cached_info_1,
                                                               edge_cached_info_2, edge_1_connected, link_1_stable):
        customer_cache = [
            edge_cached_info_1,
            edge_cached_info_2,
        ]

        edge_1_with_links_info = make_edge_with_links_info(edge_info=edge_1_connected, links_info=[link_1_stable])
        edges_statuses = [
            edge_1_with_links_info,
        ]

        filtered_customer_cache, filtered_edges_statuses = \
            TNBAMonitor._filter_edges_in_customer_cache_and_edges_statuses(customer_cache, edges_statuses)

        assert filtered_customer_cache == [edge_cached_info_1]
        assert filtered_edges_statuses == [edge_1_with_links_info]

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_for_monitored_companies_test(self, tnba_monitor, edge_cached_info_1,
                                                                         edge_cached_info_2, serial_number_1,
                                                                         serial_number_2):
        customer_cache_by_serial = {
            serial_number_1: edge_cached_info_1,
            serial_number_2: edge_cached_info_2,
        }
        tnba_monitor._customer_cache_by_serial = customer_cache_by_serial
        tnba_monitor._get_open_tickets_with_details_by_client_id = CoroutineMock()

        await tnba_monitor._get_all_open_tickets_with_details_for_monitored_companies()

        bruin_client_ids = set(
            cached_info['bruin_client_info']['client_id']
            for cached_info in customer_cache_by_serial.values()
        )
        initial_tickets = []
        for client_id in bruin_client_ids:
            tnba_monitor._get_open_tickets_with_details_by_client_id.assert_any_await(client_id, initial_tickets)

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_test(self, tnba_monitor, make_in_progress_ticket_detail,
                                                              make_details_of_ticket, make_ticket_object,
                                                              make_rpc_response, open_affecting_ticket,
                                                              open_outage_ticket, serial_number_1, serial_number_2,
                                                              bruin_client_id):
        outage_tickets = [
            open_outage_ticket,
        ]
        affecting_tickets = [
            open_affecting_ticket,
        ]

        outage_ticket_1_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        outage_ticket_1_details = make_details_of_ticket(
            ticket_details=[outage_ticket_1_detail_1],
            ticket_notes=[],
        )

        affecting_ticket_1_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_2)
        affecting_ticket_1_details = make_details_of_ticket(
            ticket_details=[affecting_ticket_1_detail_1],
            ticket_notes=[],
        )

        get_open_outage_tickets_response = make_rpc_response(body=outage_tickets, status=200)
        get_open_affecting_tickets_response = make_rpc_response(body=affecting_tickets, status=200)

        get_ticket_1_details_response = make_rpc_response(body=outage_ticket_1_details, status=200)
        get_ticket_2_details_response = make_rpc_response(body=affecting_ticket_1_details, status=200)

        tnba_monitor._bruin_repository.get_open_outage_tickets.return_value = get_open_outage_tickets_response
        tnba_monitor._bruin_repository.get_open_affecting_tickets.return_value = get_open_affecting_tickets_response
        tnba_monitor._bruin_repository.get_ticket_details.side_effect = [
            get_ticket_1_details_response,
            get_ticket_2_details_response,
        ]

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        tnba_monitor._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        tnba_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(open_outage_ticket['ticketID']), call(open_affecting_ticket['ticketID'])
        ], any_order=True)

        expected_outage_ticket_object = make_ticket_object(
            ticket_id=open_outage_ticket['ticketID'],
            ticket_creation_date=open_outage_ticket['createDate'],
            ticket_topic=open_outage_ticket['category'],
            ticket_creator=open_outage_ticket['createdBy'],
            ticket_details=[outage_ticket_1_detail_1],
            ticket_notes=[],
        )
        expected_affecting_ticket_object = make_ticket_object(
            ticket_id=open_affecting_ticket['ticketID'],
            ticket_creation_date=open_affecting_ticket['createDate'],
            ticket_topic=open_affecting_ticket['category'],
            ticket_creator=open_affecting_ticket['createdBy'],
            ticket_details=[affecting_ticket_1_detail_1],
            ticket_notes=[],
        )
        expected = [
            expected_outage_ticket_object,
            expected_affecting_ticket_object,
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_with_open_outage_tickets_request_not_having_2xx_status_test(
            self, tnba_monitor, make_in_progress_ticket_detail, make_details_of_ticket, make_ticket_object,
            make_rpc_response, open_affecting_ticket, serial_number_1, bruin_client_id):
        affecting_tickets = [
            open_affecting_ticket,
        ]

        affecting_ticket_1_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        affecting_ticket_1_details = make_details_of_ticket(
            ticket_details=[affecting_ticket_1_detail_1],
            ticket_notes=[],
        )

        get_open_outage_tickets_response = make_rpc_response(
            body='Got internal error from Bruin',
            status=500,
        )
        get_open_affecting_tickets_response = make_rpc_response(body=affecting_tickets, status=200)

        get_ticket_1_details_response = make_rpc_response(body=affecting_ticket_1_details, status=200)

        tnba_monitor._bruin_repository.get_open_outage_tickets.return_value = get_open_outage_tickets_response
        tnba_monitor._bruin_repository.get_open_affecting_tickets.return_value = get_open_affecting_tickets_response
        tnba_monitor._bruin_repository.get_ticket_details.side_effect = [
            get_ticket_1_details_response,
        ]

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        tnba_monitor._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        tnba_monitor._bruin_repository.get_ticket_details.assert_awaited_once_with(open_affecting_ticket['ticketID'])

        expected_affecting_ticket_object = make_ticket_object(
            ticket_id=open_affecting_ticket['ticketID'],
            ticket_creation_date=open_affecting_ticket['createDate'],
            ticket_topic=open_affecting_ticket['category'],
            ticket_creator=open_affecting_ticket['createdBy'],
            ticket_details=[affecting_ticket_1_detail_1],
            ticket_notes=[],
        )
        expected = [
            expected_affecting_ticket_object,
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_with_open_affecting_tickets_request_not_having_2xx_status_test(
            self, tnba_monitor, make_in_progress_ticket_detail, make_details_of_ticket, make_ticket_object,
            make_rpc_response, open_outage_ticket, serial_number_1, bruin_client_id):
        outage_tickets = [
            open_outage_ticket,
        ]

        outage_ticket_1_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        outage_ticket_1_details = make_details_of_ticket(
            ticket_details=[outage_ticket_1_detail_1],
            ticket_notes=[],
        )

        get_open_outage_tickets_response = make_rpc_response(body=outage_tickets, status=200)
        get_open_affecting_tickets_response = make_rpc_response(
            body='Got internal error from Bruin',
            status=500,
        )

        get_ticket_1_details_response = make_rpc_response(body=outage_ticket_1_details, status=200)

        tnba_monitor._bruin_repository.get_open_outage_tickets.return_value = get_open_outage_tickets_response
        tnba_monitor._bruin_repository.get_open_affecting_tickets.return_value = get_open_affecting_tickets_response
        tnba_monitor._bruin_repository.get_ticket_details.side_effect = [
            get_ticket_1_details_response,
        ]

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        tnba_monitor._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        tnba_monitor._bruin_repository.get_ticket_details.assert_awaited_once_with(open_outage_ticket['ticketID'])

        expected_affecting_ticket_object = make_ticket_object(
            ticket_id=open_outage_ticket['ticketID'],
            ticket_creation_date=open_outage_ticket['createDate'],
            ticket_topic=open_outage_ticket['category'],
            ticket_creator=open_outage_ticket['createdBy'],
            ticket_details=[outage_ticket_1_detail_1],
            ticket_notes=[],
        )
        expected = [
            expected_affecting_ticket_object,
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_with_ticket_details_request_not_having_2xx_status_test(
            self, tnba_monitor, make_in_progress_ticket_detail, make_details_of_ticket, make_ticket_object,
            make_rpc_response, open_affecting_ticket, open_outage_ticket, serial_number_1, bruin_client_id):
        outage_tickets = [
            open_outage_ticket,
        ]
        affecting_tickets = [
            open_affecting_ticket,
        ]

        affecting_ticket_1_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        affecting_ticket_1_details = make_details_of_ticket(
            ticket_details=[affecting_ticket_1_detail_1],
            ticket_notes=[],
        )

        get_open_outage_tickets_response = make_rpc_response(body=outage_tickets, status=200)
        get_open_affecting_tickets_response = make_rpc_response(body=affecting_tickets, status=200)

        get_ticket_1_details_response = make_rpc_response(
            body='Got internal error from Bruin',
            status=500,
        )
        get_ticket_2_details_response = make_rpc_response(body=affecting_ticket_1_details, status=200)

        tnba_monitor._bruin_repository.get_open_outage_tickets.return_value = get_open_outage_tickets_response
        tnba_monitor._bruin_repository.get_open_affecting_tickets.return_value = get_open_affecting_tickets_response
        tnba_monitor._bruin_repository.get_ticket_details.side_effect = [
            get_ticket_1_details_response,
            get_ticket_2_details_response,
        ]

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        tnba_monitor._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        tnba_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(open_outage_ticket['ticketID']), call(open_affecting_ticket['ticketID'])
        ], any_order=True)

        expected_affecting_ticket_object = make_ticket_object(
            ticket_id=open_affecting_ticket['ticketID'],
            ticket_creation_date=open_affecting_ticket['createDate'],
            ticket_topic=open_affecting_ticket['category'],
            ticket_creator=open_affecting_ticket['createdBy'],
            ticket_details=[affecting_ticket_1_detail_1],
            ticket_notes=[],
        )
        expected = [
            expected_affecting_ticket_object,
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def get_open_tickets_with_details_by_client_id_with_ticket_details_not_having_details_actually_test(
            self, tnba_monitor, make_in_progress_ticket_detail, make_details_of_ticket, make_ticket_object,
            make_rpc_response, open_affecting_ticket, open_outage_ticket, serial_number_1, bruin_client_id):
        outage_tickets = [
            open_outage_ticket,
        ]
        affecting_tickets = [
            open_affecting_ticket,
        ]

        outage_ticket_1_details = make_details_of_ticket(
            ticket_details=[],
            ticket_notes=[],
        )

        affecting_ticket_1_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        affecting_ticket_1_details = make_details_of_ticket(
            ticket_details=[affecting_ticket_1_detail_1],
            ticket_notes=[],
        )

        get_open_outage_tickets_response = make_rpc_response(body=outage_tickets, status=200)
        get_open_affecting_tickets_response = make_rpc_response(body=affecting_tickets, status=200)

        get_ticket_1_details_response = make_rpc_response(body=outage_ticket_1_details, status=200)
        get_ticket_2_details_response = make_rpc_response(body=affecting_ticket_1_details, status=200)

        tnba_monitor._bruin_repository.get_open_outage_tickets.return_value = get_open_outage_tickets_response
        tnba_monitor._bruin_repository.get_open_affecting_tickets.return_value = get_open_affecting_tickets_response
        tnba_monitor._bruin_repository.get_ticket_details.side_effect = [
            get_ticket_1_details_response,
            get_ticket_2_details_response,
        ]

        result = []
        await tnba_monitor._get_open_tickets_with_details_by_client_id(bruin_client_id, result)

        tnba_monitor._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(bruin_client_id)
        tnba_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(open_outage_ticket['ticketID']), call(open_affecting_ticket['ticketID'])
        ], any_order=True)

        expected_affecting_ticket_object = make_ticket_object(
            ticket_id=open_affecting_ticket['ticketID'],
            ticket_creation_date=open_affecting_ticket['createDate'],
            ticket_topic=open_affecting_ticket['category'],
            ticket_creator=open_affecting_ticket['createdBy'],
            ticket_details=[affecting_ticket_1_detail_1],
            ticket_notes=[],
        )
        expected = [
            expected_affecting_ticket_object,
        ]
        assert result == expected

    def filter_tickets_and_details_related_to_edges_under_monitoring_test(self, tnba_monitor, make_ticket_object,
                                                                          make_in_progress_ticket_detail,
                                                                          edge_cached_info_1, edge_cached_info_2,
                                                                          serial_number_1, serial_number_2,
                                                                          serial_number_3):
        customer_cache_by_serial = {
            serial_number_1: edge_cached_info_1,
            serial_number_2: edge_cached_info_2,
        }

        ticket_1_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        ticket_1_detail_2 = make_in_progress_ticket_detail(serial_number=serial_number_3)
        ticket_1 = make_ticket_object(ticket_details=[ticket_1_detail_1, ticket_1_detail_2])

        ticket_2_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_3)
        ticket_2 = make_ticket_object(ticket_details=[ticket_2_detail_1])

        ticket_3_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        ticket_3_detail_2 = make_in_progress_ticket_detail(serial_number=serial_number_2)
        ticket_3_detail_3 = make_in_progress_ticket_detail(serial_number=serial_number_3)
        ticket_3 = make_ticket_object(ticket_details=[ticket_3_detail_1, ticket_3_detail_2, ticket_3_detail_3])

        tickets = [
            ticket_1,
            ticket_2,
            ticket_3,
        ]

        tnba_monitor._customer_cache_by_serial = customer_cache_by_serial

        result = tnba_monitor._filter_tickets_and_details_related_to_edges_under_monitoring(tickets)

        expected_ticket_1 = make_ticket_object(ticket_details=[ticket_1_detail_1])
        expected_ticket_3 = make_ticket_object(ticket_details=[ticket_3_detail_1, ticket_3_detail_2])
        expected = [
            expected_ticket_1,
            expected_ticket_3,
        ]
        assert result == expected

    def filter_irrelevant_notes_in_tickets_test(self, tnba_monitor, make_ticket_object, make_ticket_note,
                                                edge_cached_info_1, edge_cached_info_2, serial_number_1,
                                                serial_number_2, serial_number_3):
        customer_cache_by_serial = {
            serial_number_1: edge_cached_info_1,
            serial_number_2: edge_cached_info_2,
        }

        ticket_1_note_1 = make_ticket_note(serial_number=serial_number_1, text=None)
        ticket_1_note_2 = make_ticket_note(serial_number=serial_number_2, text='This is a note')
        ticket_1_note_3 = make_ticket_note(serial_number=serial_number_3, text='This is a note')
        ticket_1 = make_ticket_object(ticket_notes=[ticket_1_note_1, ticket_1_note_2, ticket_1_note_3])

        ticket_2_note_1 = make_ticket_note(serial_number=serial_number_3, text='This is a note')
        ticket_2 = make_ticket_object(ticket_notes=[ticket_2_note_1])

        ticket_3_note_1 = make_ticket_note(serial_number=serial_number_1, text='This is a note')
        ticket_3_note_2 = make_ticket_note(serial_number=serial_number_2, text='This is a note')
        ticket_3 = make_ticket_object(ticket_notes=[ticket_3_note_1, ticket_3_note_2])

        tickets = [
            ticket_1,
            ticket_2,
            ticket_3,
        ]
        tnba_monitor._customer_cache_by_serial = customer_cache_by_serial

        result = tnba_monitor._filter_irrelevant_notes_in_tickets(tickets)

        expected_ticket_1 = make_ticket_object(ticket_notes=[ticket_1_note_2])
        expected_ticket_2 = make_ticket_object(ticket_notes=[])
        expected_ticket_3 = make_ticket_object(ticket_notes=[ticket_3_note_1, ticket_3_note_2])
        expected = [
            expected_ticket_1,
            expected_ticket_2,
            expected_ticket_3,
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def get_predictions_by_ticket_id_ok_test(self, tnba_monitor, make_in_progress_ticket_detail,
                                                   make_ticket_object, make_task_history_item, make_task_history,
                                                   make_rpc_response, make_prediction_object,
                                                   make_predictions_by_ticket_id_object, serial_number_1,
                                                   serial_number_2, serial_number_3, holmdel_noc_prediction):
        ticket_id = 12345

        ticket_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        ticket_detail_2 = make_in_progress_ticket_detail(serial_number=serial_number_2)
        ticket_detail_3 = make_in_progress_ticket_detail(serial_number=serial_number_3)
        ticket_details = [
            ticket_detail_1,
            ticket_detail_2,
            ticket_detail_3,
        ]
        ticket_with_details = make_ticket_object(ticket_details=ticket_details)

        tickets = [
            ticket_with_details,
        ]

        task_history_item_1 = make_task_history_item(serial_number=serial_number_1)
        task_history = make_task_history(task_history_item_1)
        get_task_history_response = make_rpc_response(body=task_history, status=200)

        ticket_predictions_for_serial_1 = make_prediction_object(
            serial_number=serial_number_1,
            predictions=[holmdel_noc_prediction],
        )
        ticket_predictions_for_serial_2 = make_prediction_object(
            serial_number=serial_number_2,
            predictions=[holmdel_noc_prediction],
        )
        ticket_predictions = [
            ticket_predictions_for_serial_1,
            ticket_predictions_for_serial_2,
        ]
        get_predictions_response = make_rpc_response(body=ticket_predictions, status=200)

        assets_to_predict = [
            serial_number_1,
            serial_number_2,
            serial_number_3,
        ]

        tnba_monitor._bruin_repository.get_ticket_task_history.return_value = get_task_history_response
        tnba_monitor._t7_repository.get_prediction.return_value = get_predictions_response

        result = await tnba_monitor._get_predictions_by_ticket_id(tickets)

        tnba_monitor._bruin_repository.get_ticket_task_history.assert_awaited_once_with(ticket_id)
        tnba_monitor._t7_repository.get_prediction.assert_awaited_once_with(ticket_id, task_history, assets_to_predict)

        expected = make_predictions_by_ticket_id_object(ticket_id=ticket_id, predictions=ticket_predictions)
        assert result == expected

    @pytest.mark.asyncio
    async def get_predictions_by_ticket_id_with_retrieval_of_task_history_returning_non_2xx_status_test(
            self, tnba_monitor, make_in_progress_ticket_detail, make_ticket_object, make_rpc_response,
            serial_number_1, serial_number_2, serial_number_3):
        ticket_id = 12345

        ticket_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        ticket_detail_2 = make_in_progress_ticket_detail(serial_number=serial_number_2)
        ticket_detail_3 = make_in_progress_ticket_detail(serial_number=serial_number_3)
        ticket_details = [
            ticket_detail_1,
            ticket_detail_2,
            ticket_detail_3,
        ]
        ticket_with_details = make_ticket_object(ticket_details=ticket_details)

        tickets = [
            ticket_with_details,
        ]

        get_task_history_response = make_rpc_response(
            body='Got internal error from Bruin',
            status=500,
        )

        tnba_monitor._bruin_repository.get_ticket_task_history.return_value = get_task_history_response

        result = await tnba_monitor._get_predictions_by_ticket_id(tickets)

        tnba_monitor._bruin_repository.get_ticket_task_history.assert_awaited_once_with(ticket_id)
        tnba_monitor._t7_repository.get_prediction.assert_not_awaited()

        expected = {}
        assert result == expected

    @pytest.mark.asyncio
    async def get_predictions_by_ticket_id_with_not_a_single_valid_asset_in_task_history_test(
            self, tnba_monitor, make_in_progress_ticket_detail, make_ticket_object, make_task_history_item,
            make_task_history, make_rpc_response, serial_number_1, serial_number_2, serial_number_3):
        ticket_id = 12345

        ticket_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        ticket_detail_2 = make_in_progress_ticket_detail(serial_number=serial_number_2)
        ticket_detail_3 = make_in_progress_ticket_detail(serial_number=serial_number_3)
        ticket_details = [
            ticket_detail_1,
            ticket_detail_2,
            ticket_detail_3,
        ]
        ticket_with_details = make_ticket_object(ticket_details=ticket_details)

        tickets = [
            ticket_with_details,
        ]

        task_history_item_1 = make_task_history_item(serial_number=None)
        task_history = make_task_history(task_history_item_1)
        get_task_history_response = make_rpc_response(body=task_history, status=200)

        tnba_monitor._bruin_repository.get_ticket_task_history.return_value = get_task_history_response

        result = await tnba_monitor._get_predictions_by_ticket_id(tickets)

        tnba_monitor._bruin_repository.get_ticket_task_history.assert_awaited_once_with(ticket_id)
        tnba_monitor._t7_repository.get_prediction.assert_not_awaited()

        expected = {}
        assert result == expected

    @pytest.mark.asyncio
    async def get_predictions_by_ticket_id_with_retrieval_of_predictions_returning_non_2xx_status_test(
            self, tnba_monitor, make_in_progress_ticket_detail, make_ticket_object, make_task_history_item,
            make_task_history, make_rpc_response, serial_number_1, serial_number_2, serial_number_3):
        ticket_id = 12345

        ticket_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        ticket_detail_2 = make_in_progress_ticket_detail(serial_number=serial_number_2)
        ticket_detail_3 = make_in_progress_ticket_detail(serial_number=serial_number_3)
        ticket_details = [
            ticket_detail_1,
            ticket_detail_2,
            ticket_detail_3,
        ]
        ticket_with_details = make_ticket_object(ticket_details=ticket_details)

        tickets = [
            ticket_with_details,
        ]

        task_history_item_1 = make_task_history_item(serial_number=serial_number_1)
        task_history = make_task_history(task_history_item_1)
        get_task_history_response = make_rpc_response(body=task_history, status=200)

        get_predictions_response = make_rpc_response(
            body='Got internal error from T7',
            status=500,
        )

        assets_to_predict = [
            serial_number_1,
            serial_number_2,
            serial_number_3,
        ]

        tnba_monitor._bruin_repository.get_ticket_task_history.return_value = get_task_history_response
        tnba_monitor._t7_repository.get_prediction.return_value = get_predictions_response

        result = await tnba_monitor._get_predictions_by_ticket_id(tickets)

        tnba_monitor._bruin_repository.get_ticket_task_history.assert_awaited_once_with(ticket_id)
        tnba_monitor._t7_repository.get_prediction.assert_awaited_once_with(ticket_id, task_history, assets_to_predict)

        expected = {}
        assert result == expected

    @pytest.mark.asyncio
    async def get_predictions_by_ticket_id_with_no_predictions_found_for_ticket_test(
            self, tnba_monitor, make_in_progress_ticket_detail, make_ticket_object, make_task_history_item,
            make_task_history, make_rpc_response, serial_number_1, serial_number_2, serial_number_3):
        ticket_id = 12345

        ticket_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        ticket_detail_2 = make_in_progress_ticket_detail(serial_number=serial_number_2)
        ticket_detail_3 = make_in_progress_ticket_detail(serial_number=serial_number_3)
        ticket_details = [
            ticket_detail_1,
            ticket_detail_2,
            ticket_detail_3,
        ]
        ticket_with_details = make_ticket_object(ticket_details=ticket_details)

        tickets = [
            ticket_with_details,
        ]

        task_history_item_1 = make_task_history_item(serial_number=serial_number_1)
        task_history = make_task_history(task_history_item_1)
        get_task_history_response = make_rpc_response(body=task_history, status=200)

        get_predictions_response = make_rpc_response(body=[], status=200)

        assets_to_predict = [
            serial_number_1,
            serial_number_2,
            serial_number_3,
        ]

        tnba_monitor._bruin_repository.get_ticket_task_history.return_value = get_task_history_response
        tnba_monitor._t7_repository.get_prediction.return_value = get_predictions_response

        result = await tnba_monitor._get_predictions_by_ticket_id(tickets)

        tnba_monitor._bruin_repository.get_ticket_task_history.assert_awaited_once_with(ticket_id)
        tnba_monitor._t7_repository.get_prediction.assert_awaited_once_with(ticket_id, task_history, assets_to_predict)

        expected = {}
        assert result == expected

    @pytest.mark.asyncio
    async def remove_erroneous_predictions_with_some_predictions_being_erroneous_test(
            self, tnba_monitor, make_prediction_object, make_erroneous_prediction_object,
            make_predictions_by_ticket_id_object, serial_number_1, serial_number_2, serial_number_3):
        ticket_id = 12345
        ticket_prediction_object_1 = make_prediction_object(serial_number=serial_number_1)
        ticket_prediction_object_2 = make_erroneous_prediction_object(serial_number=serial_number_2)
        ticket_prediction_object_3 = make_prediction_object(serial_number=serial_number_3)
        predictions = [
            ticket_prediction_object_1,
            ticket_prediction_object_2,
            ticket_prediction_object_3,
        ]
        predictions_by_ticket_id = make_predictions_by_ticket_id_object(ticket_id=ticket_id, predictions=predictions)

        result = tnba_monitor._remove_erroneous_predictions(predictions_by_ticket_id)

        expected = make_predictions_by_ticket_id_object(
            ticket_id=ticket_id,
            predictions=[ticket_prediction_object_1, ticket_prediction_object_3],
        )
        assert result == expected

    @pytest.mark.asyncio
    async def remove_erroneous_predictions_with_all_predictions_being_erroneous_test(
            self, tnba_monitor, make_predictions_by_ticket_id_object, make_erroneous_prediction_object,
            serial_number_1, serial_number_2, serial_number_3):
        ticket_id = 12345
        ticket_prediction_object_1 = make_erroneous_prediction_object(serial_number=serial_number_1)
        ticket_prediction_object_2 = make_erroneous_prediction_object(serial_number=serial_number_2)
        ticket_prediction_object_3 = make_erroneous_prediction_object(serial_number=serial_number_3)
        predictions = [
            ticket_prediction_object_1,
            ticket_prediction_object_2,
            ticket_prediction_object_3,
        ]
        predictions_by_ticket_id = make_predictions_by_ticket_id_object(ticket_id=ticket_id, predictions=predictions)

        result = tnba_monitor._remove_erroneous_predictions(predictions_by_ticket_id)

        assert result == {}

    @pytest.mark.asyncio
    async def map_ticket_details_with_predictions_test(self, tnba_monitor, make_in_progress_ticket_detail,
                                                       make_detail_object, make_detail_object_with_predictions,
                                                       make_prediction_object, make_predictions_by_ticket_id_object,
                                                       serial_number_1, serial_number_2, serial_number_3,
                                                       holmdel_noc_prediction):
        ticket_1_id = 12345
        ticket_2_id = 67890

        prediction_set_1 = [
            holmdel_noc_prediction,
        ]
        prediction_object_1 = make_prediction_object(
            serial_number=serial_number_1,
            predictions=prediction_set_1,
        )

        prediction_set_2 = [
            holmdel_noc_prediction,
        ]
        prediction_object_2 = make_prediction_object(
            serial_number=serial_number_2,
            predictions=prediction_set_2,
        )
        predictions_by_ticket_id = make_predictions_by_ticket_id_object(
            ticket_id=ticket_1_id,
            predictions=[prediction_object_1, prediction_object_2],
        )

        ticket_1_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        ticket_1_detail_2 = make_in_progress_ticket_detail(serial_number=serial_number_2)
        ticket_1_detail_3 = make_in_progress_ticket_detail(serial_number=serial_number_3)
        ticket_2_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)

        ticket_1_detail_object_1 = make_detail_object(ticket_id=ticket_1_id, ticket_detail=ticket_1_detail_1)
        ticket_1_detail_object_2 = make_detail_object(ticket_id=ticket_1_id, ticket_detail=ticket_1_detail_2)
        ticket_1_detail_object_3 = make_detail_object(ticket_id=ticket_1_id, ticket_detail=ticket_1_detail_3)
        ticket_2_detail_object_1 = make_detail_object(ticket_id=ticket_2_id, ticket_detail=ticket_2_detail_1)
        ticket_detail_objects = [
            ticket_1_detail_object_1,
            ticket_1_detail_object_2,
            ticket_1_detail_object_3,
            ticket_2_detail_object_1,
        ]

        result = tnba_monitor._map_ticket_details_with_predictions(ticket_detail_objects, predictions_by_ticket_id)

        expected_detail_object_1 = make_detail_object_with_predictions(
            ticket_id=ticket_1_id,
            ticket_detail=ticket_1_detail_1,
            ticket_detail_predictions=prediction_set_1,
        )
        expected_detail_object_2 = make_detail_object_with_predictions(
            ticket_id=ticket_1_id,
            ticket_detail=ticket_1_detail_2,
            ticket_detail_predictions=prediction_set_2,
        )
        assert result == [
            expected_detail_object_1,
            expected_detail_object_2,
        ]

    def transform_tickets_into_detail_objects_test(self, make_in_progress_ticket_detail,
                                                   make_ticket_object, make_detail_object,
                                                   make_ticket_note, make_standard_tnba_note,
                                                   serial_number_1, serial_number_2, serial_number_3):
        ticket_1_id = 12345
        ticket_2_id = 11223

        ticket_1_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        ticket_1_detail_2 = make_in_progress_ticket_detail(serial_number=serial_number_2)
        ticket_1_detail_3 = make_in_progress_ticket_detail(serial_number=serial_number_3)
        ticket_1_note_1 = make_ticket_note(serial_number=serial_number_1, text='This is a note')
        ticket_1_note_2 = make_standard_tnba_note(serial_number=serial_number_2)
        ticket_1_note_3 = make_ticket_note(serial_number=serial_number_3, text='This is a note')
        ticket_1_with_details = make_ticket_object(
            ticket_id=ticket_1_id,
            ticket_details=[ticket_1_detail_1, ticket_1_detail_2, ticket_1_detail_3],
            ticket_notes=[ticket_1_note_1, ticket_1_note_2, ticket_1_note_3],
        )

        ticket_2_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        ticket_2_detail_2 = make_in_progress_ticket_detail(serial_number=serial_number_2)
        ticket_2_note_1 = make_standard_tnba_note(serial_number=serial_number_1)
        ticket_2_with_details = make_ticket_object(
            ticket_id=ticket_2_id,
            ticket_details=[ticket_2_detail_1, ticket_2_detail_2],
            ticket_notes=[ticket_2_note_1],
        )

        tickets = [
            ticket_1_with_details,
            ticket_2_with_details,
        ]

        detail_objects = TNBAMonitor._transform_tickets_into_detail_objects(tickets)

        expected_ticket_detail_1 = make_detail_object(
            ticket_id=ticket_1_id,
            ticket_detail=ticket_1_detail_1,
            ticket_notes=[ticket_1_note_1],
        )
        expected_ticket_detail_2 = make_detail_object(
            ticket_id=ticket_1_id,
            ticket_detail=ticket_1_detail_2,
            ticket_notes=[ticket_1_note_2],
        )
        expected_ticket_detail_3 = make_detail_object(
            ticket_id=ticket_1_id,
            ticket_detail=ticket_1_detail_3,
            ticket_notes=[ticket_1_note_3],
        )
        expected_ticket_detail_4 = make_detail_object(
            ticket_id=ticket_2_id,
            ticket_detail=ticket_2_detail_1,
            ticket_notes=[ticket_2_note_1],
        )
        expected_ticket_detail_5 = make_detail_object(
            ticket_id=ticket_2_id,
            ticket_detail=ticket_2_detail_2,
            ticket_notes=[],
        )
        assert detail_objects == [
            expected_ticket_detail_1,
            expected_ticket_detail_2,
            expected_ticket_detail_3,
            expected_ticket_detail_4,
            expected_ticket_detail_5,
        ]

    def filter_resolved_ticket_details_test(self, tnba_monitor, make_in_progress_ticket_detail,
                                            make_resolved_ticket_detail, make_detail_object, serial_number_1,
                                            serial_number_2, serial_number_3):
        ticket_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        ticket_detail_2 = make_resolved_ticket_detail(serial_number=serial_number_2)
        ticket_detail_3 = make_in_progress_ticket_detail(serial_number=serial_number_3)

        ticket_detail_object_1 = make_detail_object(ticket_detail=ticket_detail_1)
        ticket_detail_object_2 = make_detail_object(ticket_detail=ticket_detail_2)
        ticket_detail_object_3 = make_detail_object(ticket_detail=ticket_detail_3)
        detail_objects = [
            ticket_detail_object_1,
            ticket_detail_object_2,
            ticket_detail_object_3,
        ]

        filtered_detail_objects = tnba_monitor._filter_resolved_ticket_details(detail_objects)

        assert filtered_detail_objects == [
            ticket_detail_object_1,
            ticket_detail_object_3,
        ]

    def filter_outage_ticket_details_based_on_last_outage_with_affecting_ticket_details_test(
            self, tnba_monitor, make_in_progress_ticket_detail, make_detail_object, serial_number_1, serial_number_2):
        ticket_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        ticket_detail_object_1 = make_detail_object(
            ticket_topic='VAS',
            ticket_detail=ticket_detail_1,
        )

        ticket_detail_2 = make_in_progress_ticket_detail(serial_number=serial_number_2)
        ticket_detail_object_2 = make_detail_object(
            ticket_topic='VAS',
            ticket_detail=ticket_detail_2,
        )

        ticket_details = [
            ticket_detail_object_1,
            ticket_detail_object_2,
        ]

        result = tnba_monitor._filter_outage_ticket_details_based_on_last_outage(ticket_details)
        assert result == ticket_details

    def filter_outage_ticket_details_based_on_last_outage_with_outage_ticket_details_test(
            self, tnba_monitor, make_in_progress_ticket_detail, make_detail_object, serial_number_1, serial_number_2,
            serial_number_3):
        ticket_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        ticket_detail_object_1 = make_detail_object(
            ticket_topic='VOO',
            ticket_detail=ticket_detail_1,
        )

        ticket_detail_2 = make_in_progress_ticket_detail(serial_number=serial_number_2)
        ticket_detail_object_2 = make_detail_object(
            ticket_topic='VAS',
            ticket_detail=ticket_detail_2,
        )

        ticket_detail_3 = make_in_progress_ticket_detail(serial_number=serial_number_3)
        ticket_detail_object_3 = make_detail_object(
            ticket_topic='VOO',
            ticket_detail=ticket_detail_3,
        )

        ticket_details = [
            ticket_detail_object_1,
            ticket_detail_object_2,
            ticket_detail_object_3,
        ]

        is_last_outage_in_detail_1_too_recent = True
        is_last_outage_in_detail_3_too_recent = False
        tnba_monitor._was_last_outage_detected_recently.side_effect = [
            is_last_outage_in_detail_1_too_recent,
            is_last_outage_in_detail_3_too_recent,
        ]

        result = tnba_monitor._filter_outage_ticket_details_based_on_last_outage(ticket_details)
        expected = [
            ticket_detail_object_2,
            ticket_detail_object_3,
        ]
        assert result == expected

    def was_last_outage_detected_recently_with_reopen_note_not_found_and_triage_not_found_test(self, tnba_monitor):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        ticket_notes = []

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(minutes=59, seconds=59)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(hours=1)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(hours=1, seconds=1)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    def was_last_outage_detected_recently_with_reopen_note_found_test(self, tnba_monitor, make_reopen_note,
                                                                      make_triage_note, serial_number_1):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        reopen_timestamp = '2021-01-02T11:00:16.71-05:00'
        triage_timestamp = '2021-01-02T10:18:16.71-05:00'

        reopen_note = make_reopen_note(serial_number=serial_number_1, date=reopen_timestamp)
        triage_note = make_triage_note(serial_number=serial_number_1, date=triage_timestamp)
        ticket_notes = [
            reopen_note,
            triage_note,
        ]

        datetime_mock = Mock()

        new_now = parse(reopen_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    def was_last_outage_detected_recently_with_reopen_note_not_found_and_triage_note_found_test(self, tnba_monitor,
                                                                                                make_triage_note,
                                                                                                serial_number_1):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        triage_timestamp = '2021-01-02T10:18:16.71-05:00'

        triage_note = make_triage_note(serial_number=serial_number_1, date=triage_timestamp)
        ticket_notes = [
            triage_note,
        ]

        datetime_mock = Mock()
        new_now = parse(triage_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(tnba_monitor_module, 'datetime', new=datetime_mock):
            result = tnba_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    @pytest.mark.asyncio
    async def process_ticket_detail_with_tnba_note_found_and_tnba_note_being_too_recent_test(
            self, tnba_monitor, make_detail_object_with_predictions, make_in_progress_ticket_detail,
            make_standard_tnba_note, serial_number_1):
        tnba_note = make_standard_tnba_note(serial_number=serial_number_1)
        ticket_detail = make_in_progress_ticket_detail(serial_number=serial_number_1)
        detail_object = make_detail_object_with_predictions(
            ticket_detail=ticket_detail,
            ticket_notes=[tnba_note],
        )

        tnba_monitor._ticket_repository.is_tnba_note_old_enough.return_value = False

        await tnba_monitor._process_ticket_detail(detail_object)

        tnba_monitor._ticket_repository.is_tnba_note_old_enough.assert_called_once_with(tnba_note)
        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.assert_not_awaited()
        tnba_monitor._ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def process_ticket_detail_with_retrieval_of_next_results_returning_non_2xx_status_test(
            self, tnba_monitor, make_detail_object_with_predictions, make_in_progress_ticket_detail, make_rpc_response,
            serial_number_1, make_edge_with_links_info, edge_1_connected, link_1_stable, link_2_stable):
        ticket_id = 12345
        ticket_detail_id = 67890

        ticket_detail = make_in_progress_ticket_detail(detail_id=ticket_detail_id, serial_number=serial_number_1)
        detail_object = make_detail_object_with_predictions(ticket_id=ticket_id, ticket_detail=ticket_detail, )

        next_results_response = make_rpc_response(
            body='Got internal error from Bruin',
            status=500,
        )
        edge_status = make_edge_with_links_info(
            edge_info=edge_1_connected,
            links_info=[link_1_stable, link_2_stable],
        )
        edge_status_by_serial = {
            serial_number_1: edge_status,
        }
        tnba_monitor._edge_status_by_serial = edge_status_by_serial
        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.return_value = next_results_response

        await tnba_monitor._process_ticket_detail(detail_object)

        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number_1
        )
        tnba_monitor._prediction_repository.filter_predictions_in_next_results.assert_not_called()
        tnba_monitor._ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def process_ticket_detail_with_no_predictions_after_filtering_with_next_results_test(
            self, tnba_monitor, make_detail_object_with_predictions, make_in_progress_ticket_detail, make_rpc_response,
            make_next_result_item, make_next_results, holmdel_noc_prediction, confident_request_completed_prediction,
            confident_repair_completed_prediction, serial_number_1, make_edge_with_links_info, edge_1_connected,
            link_1_stable, link_2_stable):
        ticket_id = 12345
        ticket_detail_id = 1

        ticket_detail = make_in_progress_ticket_detail(detail_id=ticket_detail_id, serial_number=serial_number_1)
        ticket_detail_predictions = [confident_request_completed_prediction]
        detail_object = make_detail_object_with_predictions(
            ticket_id=ticket_id,
            ticket_detail=ticket_detail,
            ticket_detail_predictions=ticket_detail_predictions,
        )
        ticket_detail_predictions_with_mirrored_request_repair_completed = [
            confident_request_completed_prediction,
            confident_repair_completed_prediction,
        ]
        edge_status = make_edge_with_links_info(
            edge_info=edge_1_connected,
            links_info=[link_1_stable, link_2_stable],
        )
        edge_status_by_serial = {
            serial_number_1: edge_status,
        }
        tnba_monitor._edge_status_by_serial = edge_status_by_serial
        holmdel_noc_prediction_name = holmdel_noc_prediction['name']
        next_result_item_1 = make_next_result_item(result_name=holmdel_noc_prediction_name)
        next_results = make_next_results(next_result_item_1)
        next_results_list = next_results['nextResults']
        next_results_response = make_rpc_response(
            body=next_results,
            status=200,
        )

        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.return_value = next_results_response

        await tnba_monitor._process_ticket_detail(detail_object)

        tnba_monitor._prediction_repository.map_request_and_repair_completed_predictions.assert_called_once_with(
            ticket_detail_predictions
        )
        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number_1
        )
        tnba_monitor._prediction_repository.filter_predictions_in_next_results.assert_called_once_with(
            ticket_detail_predictions_with_mirrored_request_repair_completed, next_results_list
        )
        tnba_monitor._prediction_repository.get_best_prediction.assert_not_called()
        tnba_monitor._ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def process_ticket_detail_with_tnba_note_found_and_no_changes_since_the_last_best_prediction_test(
            self, tnba_monitor, make_detail_object_with_predictions, make_in_progress_ticket_detail, make_rpc_response,
            make_next_result_item, make_next_results, make_standard_tnba_note, holmdel_noc_prediction, serial_number_1,
            edge_1_connected, link_1_stable, link_2_stable, make_edge_with_links_info):
        holmdel_noc_prediction_name = holmdel_noc_prediction['name']
        ticket_id = 12345
        ticket_detail_id = 1

        ticket_detail = make_in_progress_ticket_detail(detail_id=ticket_detail_id, serial_number=serial_number_1)
        ticket_detail_predictions = [holmdel_noc_prediction]
        tnba_note = make_standard_tnba_note(serial_number=serial_number_1, prediction_name=holmdel_noc_prediction_name)
        detail_object = make_detail_object_with_predictions(
            ticket_id=ticket_id,
            ticket_detail=ticket_detail,
            ticket_notes=[tnba_note],
            ticket_detail_predictions=ticket_detail_predictions,
        )

        next_result_item_1 = make_next_result_item(result_name=holmdel_noc_prediction_name)
        next_results = make_next_results(next_result_item_1)
        next_results_list = next_results['nextResults']
        next_results_response = make_rpc_response(
            body=next_results,
            status=200,
        )
        edge_status = make_edge_with_links_info(
            edge_info=edge_1_connected,
            links_info=[link_1_stable, link_2_stable],
        )
        edge_status_by_serial = {
            serial_number_1: edge_status,
        }
        tnba_monitor._edge_status_by_serial = edge_status_by_serial
        tnba_monitor._ticket_repository.is_tnba_note_old_enough.return_value = True
        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.return_value = next_results_response

        await tnba_monitor._process_ticket_detail(detail_object)

        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number_1
        )
        tnba_monitor._prediction_repository.filter_predictions_in_next_results.assert_called_once_with(
            ticket_detail_predictions, next_results_list
        )
        tnba_monitor._prediction_repository.get_best_prediction.assert_called_once_with(
            ticket_detail_predictions
        )
        tnba_monitor._prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note. \
            assert_called_once_with(tnba_note, holmdel_noc_prediction)
        tnba_monitor._prediction_repository.is_request_or_repair_completed_prediction.assert_not_called()
        tnba_monitor._ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def process_ticket_detail_with_standard_prediction_and_dev_env_test(
            self, tnba_monitor, make_detail_object_with_predictions, make_in_progress_ticket_detail, make_rpc_response,
            make_next_result_item, make_next_results, holmdel_noc_prediction, serial_number_1, edge_1_connected,
            link_1_stable, link_2_stable, make_edge_with_links_info):
        ticket_id = 12345
        ticket_detail_id = 1

        ticket_detail = make_in_progress_ticket_detail(detail_id=ticket_detail_id, serial_number=serial_number_1)
        ticket_detail_predictions = [holmdel_noc_prediction]
        detail_object = make_detail_object_with_predictions(
            ticket_id=ticket_id,
            ticket_detail=ticket_detail,
            ticket_detail_predictions=ticket_detail_predictions,
        )

        holmdel_noc_prediction_name = holmdel_noc_prediction['name']
        next_result_item_1 = make_next_result_item(result_name=holmdel_noc_prediction_name)
        next_results = make_next_results(next_result_item_1)
        next_results_list = next_results['nextResults']
        next_results_response = make_rpc_response(
            body=next_results,
            status=200,
        )
        edge_status = make_edge_with_links_info(
            edge_info=edge_1_connected,
            links_info=[link_1_stable, link_2_stable],
        )
        edge_status_by_serial = {
            serial_number_1: edge_status,
        }
        tnba_monitor._edge_status_by_serial = edge_status_by_serial
        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.return_value = next_results_response

        with patch.object(testconfig, 'CURRENT_ENVIRONMENT', "dev"):
            await tnba_monitor._process_ticket_detail(detail_object)

        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number_1
        )
        tnba_monitor._prediction_repository.filter_predictions_in_next_results.assert_called_once_with(
            ticket_detail_predictions, next_results_list
        )
        tnba_monitor._prediction_repository.get_best_prediction.assert_called_once_with(
            ticket_detail_predictions
        )
        tnba_monitor._ticket_repository.build_tnba_note_from_prediction.assert_called_once_with(
            holmdel_noc_prediction, serial_number_1
        )
        tnba_monitor._notifications_repository.send_slack_message.assert_awaited_once()
        assert tnba_monitor._tnba_notes_to_append == []

    @pytest.mark.asyncio
    async def process_ticket_detail_with_standard_prediction_and_prod_env_test(
            self, tnba_monitor, make_detail_object_with_predictions, make_in_progress_ticket_detail, make_rpc_response,
            make_next_result_item, make_next_results, make_payload_for_note_append_with_ticket_id,
            holmdel_noc_prediction, serial_number_1, edge_1_connected, link_1_stable, link_2_stable,
            make_edge_with_links_info):
        ticket_id = 12345
        ticket_detail_id = 1

        ticket_detail = make_in_progress_ticket_detail(detail_id=ticket_detail_id, serial_number=serial_number_1)
        ticket_detail_predictions = [holmdel_noc_prediction]
        detail_object = make_detail_object_with_predictions(
            ticket_id=ticket_id,
            ticket_detail=ticket_detail,
            ticket_detail_predictions=ticket_detail_predictions,
        )

        holmdel_noc_prediction_name = holmdel_noc_prediction['name']
        next_result_item_1 = make_next_result_item(result_name=holmdel_noc_prediction_name)
        next_results = make_next_results(next_result_item_1)
        next_results_list = next_results['nextResults']
        next_results_response = make_rpc_response(
            body=next_results,
            status=200,
        )

        built_tnba_note = 'This is a TNBA note'
        edge_status = make_edge_with_links_info(
            edge_info=edge_1_connected,
            links_info=[link_1_stable, link_2_stable],
        )
        edge_status_by_serial = {
            serial_number_1: edge_status,
        }
        tnba_monitor._edge_status_by_serial = edge_status_by_serial
        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.return_value = next_results_response
        tnba_monitor._ticket_repository.build_tnba_note_from_prediction.return_value = built_tnba_note

        with patch.object(testconfig, 'CURRENT_ENVIRONMENT', "production"):
            await tnba_monitor._process_ticket_detail(detail_object)

        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number_1
        )
        tnba_monitor._prediction_repository.filter_predictions_in_next_results.assert_called_once_with(
            ticket_detail_predictions, next_results_list
        )
        tnba_monitor._prediction_repository.get_best_prediction.assert_called_once_with(
            ticket_detail_predictions
        )
        tnba_monitor._ticket_repository.build_tnba_note_from_prediction.assert_called_once_with(
            holmdel_noc_prediction, serial_number_1
        )

        expected_note_for_append = make_payload_for_note_append_with_ticket_id(
            ticket_id=ticket_id,
            detail_id=ticket_detail_id,
            serial_number=serial_number_1,
            text=built_tnba_note,
        )
        assert tnba_monitor._tnba_notes_to_append == [
            expected_note_for_append,
        ]

    @pytest.mark.asyncio
    async def process_ticket_detail_with_prod_env_and_request_repair_completed_prediction_and_autoresolve_failed_test(
            self, tnba_monitor, make_detail_object_with_predictions, make_in_progress_ticket_detail, make_rpc_response,
            make_next_result_item, make_payload_for_note_append_with_ticket_id, make_next_results,
            unconfident_request_completed_prediction, unconfident_repair_completed_prediction, serial_number_1,
            make_edge_with_links_info, edge_1_connected, link_1_stable, link_2_stable):
        ticket_id = 12345
        ticket_detail_id = 1

        ticket_detail = make_in_progress_ticket_detail(detail_id=ticket_detail_id, serial_number=serial_number_1)
        ticket_detail_predictions = [unconfident_request_completed_prediction]
        detail_object = make_detail_object_with_predictions(
            ticket_id=ticket_id,
            ticket_detail=ticket_detail,
            ticket_detail_predictions=ticket_detail_predictions,
        )
        ticket_detail_predictions_with_mirrored_request_repair_completed = [
            unconfident_request_completed_prediction,
            unconfident_repair_completed_prediction,
        ]
        edge_status = make_edge_with_links_info(
            edge_info=edge_1_connected,
            links_info=[link_1_stable, link_2_stable],
        )
        edge_status_by_serial = {
            serial_number_1: edge_status,
        }

        request_completed_prediction_name = unconfident_request_completed_prediction['name']
        next_result_item_1 = make_next_result_item(result_name=request_completed_prediction_name)
        next_results = make_next_results(next_result_item_1)
        next_results_list = next_results['nextResults']
        next_results_response = make_rpc_response(
            body=next_results,
            status=200,
        )

        built_tnba_note = 'This is a TNBA note'
        tnba_monitor._edge_status_by_serial = edge_status_by_serial
        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.return_value = next_results_response
        tnba_monitor._autoresolve_ticket_detail.return_value = tnba_monitor.AutoresolveTicketDetailStatus.SKIPPED
        tnba_monitor._ticket_repository.build_tnba_note_from_prediction.return_value = built_tnba_note

        with patch.object(testconfig, 'CURRENT_ENVIRONMENT', "production"):
            await tnba_monitor._process_ticket_detail(detail_object)

        tnba_monitor._prediction_repository.map_request_and_repair_completed_predictions.assert_called_once_with(
            ticket_detail_predictions
        )
        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number_1
        )
        tnba_monitor._prediction_repository.filter_predictions_in_next_results.assert_called_once_with(
            ticket_detail_predictions_with_mirrored_request_repair_completed, next_results_list
        )
        tnba_monitor._prediction_repository.get_best_prediction.assert_called_once_with(
            ticket_detail_predictions
        )
        tnba_monitor._prediction_repository.is_request_or_repair_completed_prediction.assert_called_once_with(
            unconfident_request_completed_prediction
        )
        tnba_monitor._autoresolve_ticket_detail.assert_awaited_once_with(
            detail_object=detail_object,
            best_prediction=unconfident_request_completed_prediction,
        )
        tnba_monitor._t7_repository.post_live_automation_metrics.assert_not_called()
        tnba_monitor._ticket_repository.build_tnba_note_from_prediction.assert_called_once_with(
            unconfident_request_completed_prediction, serial_number_1,
        )
        tnba_monitor._ticket_repository.build_tnba_note_for_AI_autoresolve.assert_not_called()

        expected_note_for_append = make_payload_for_note_append_with_ticket_id(
            ticket_id=ticket_id,
            detail_id=ticket_detail_id,
            serial_number=serial_number_1,
            text=built_tnba_note,
        )
        assert tnba_monitor._tnba_notes_to_append == [
            expected_note_for_append,
        ]

    @pytest.mark.asyncio
    async def process_ticket_detail_with_prod_env_and_repair_completed_prediction_and_autoresolve_bad_prediction_test(
            self, tnba_monitor, make_detail_object_with_predictions, make_in_progress_ticket_detail, make_rpc_response,
            make_next_result_item, make_next_results,
            unconfident_request_completed_prediction, unconfident_repair_completed_prediction, serial_number_1):
        ticket_id = 12345
        ticket_detail_id = 1

        ticket_detail = make_in_progress_ticket_detail(detail_id=ticket_detail_id, serial_number=serial_number_1)
        ticket_detail_predictions = [unconfident_request_completed_prediction]
        detail_object = make_detail_object_with_predictions(
            ticket_id=ticket_id,
            ticket_detail=ticket_detail,
            ticket_detail_predictions=ticket_detail_predictions,
        )
        ticket_detail_predictions_with_mirrored_request_repair_completed = [
            unconfident_request_completed_prediction,
            unconfident_repair_completed_prediction,
        ]

        request_completed_prediction_name = unconfident_request_completed_prediction['name']
        next_result_item_1 = make_next_result_item(result_name=request_completed_prediction_name)
        next_results = make_next_results(next_result_item_1)
        next_results_list = next_results['nextResults']
        next_results_response = make_rpc_response(
            body=next_results,
            status=200,
        )
        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.return_value = next_results_response
        tnba_monitor._autoresolve_ticket_detail.return_value = tnba_monitor.AutoresolveTicketDetailStatus.BAD_PREDICTION

        with patch.object(testconfig, 'CURRENT_ENVIRONMENT', "production"):
            await tnba_monitor._process_ticket_detail(detail_object)

        tnba_monitor._prediction_repository.map_request_and_repair_completed_predictions.assert_called_once_with(
            ticket_detail_predictions
        )
        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number_1
        )
        tnba_monitor._prediction_repository.filter_predictions_in_next_results.assert_called_once_with(
            ticket_detail_predictions_with_mirrored_request_repair_completed, next_results_list
        )
        tnba_monitor._prediction_repository.get_best_prediction.assert_called_once_with(
            ticket_detail_predictions
        )
        tnba_monitor._prediction_repository.is_request_or_repair_completed_prediction.assert_called_once_with(
            unconfident_request_completed_prediction
        )
        tnba_monitor._autoresolve_ticket_detail.assert_awaited_once_with(
            detail_object=detail_object,
            best_prediction=unconfident_request_completed_prediction,
        )
        tnba_monitor._t7_repository.post_live_automation_metrics.assert_called_once_with(
            ticket_id, serial_number_1, automated_successfully=False
        )
        tnba_monitor._ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        tnba_monitor._ticket_repository.build_tnba_note_for_AI_autoresolve.assert_not_called()

    @pytest.mark.asyncio
    async def process_ticket_detail_with_prod_env_and_request_repair_completed_prediction_and_autoresolve_ok_test(
            self, tnba_monitor, make_detail_object_with_predictions, make_in_progress_ticket_detail, make_rpc_response,
            make_next_result_item, make_next_results, make_payload_for_note_append_with_ticket_id,
            confident_request_completed_prediction, confident_repair_completed_prediction, serial_number_1,
            make_edge_with_links_info, edge_1_connected, link_1_stable, link_2_stable):
        ticket_id = 12345
        ticket_detail_id = 1

        ticket_detail = make_in_progress_ticket_detail(detail_id=ticket_detail_id, serial_number=serial_number_1)
        ticket_detail_predictions = [confident_request_completed_prediction]
        detail_object = make_detail_object_with_predictions(
            ticket_id=ticket_id,
            ticket_detail=ticket_detail,
            ticket_detail_predictions=ticket_detail_predictions,
        )
        ticket_detail_predictions_with_mirrored_request_repair_completed = [
            confident_request_completed_prediction,
            confident_repair_completed_prediction,
        ]

        request_completed_prediction_name = confident_request_completed_prediction['name']
        next_result_item_1 = make_next_result_item(result_name=request_completed_prediction_name)
        next_results = make_next_results(next_result_item_1)
        next_results_list = next_results['nextResults']
        next_results_response = make_rpc_response(
            body=next_results,
            status=200,
        )

        built_tnba_note = 'This is a TNBA note'
        edge_status = make_edge_with_links_info(
            edge_info=edge_1_connected,
            links_info=[link_1_stable, link_2_stable],
        )
        edge_status_by_serial = {
            serial_number_1: edge_status,
        }
        tnba_monitor._edge_status_by_serial = edge_status_by_serial
        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.return_value = next_results_response
        tnba_monitor._autoresolve_ticket_detail.return_value = True
        tnba_monitor._autoresolve_ticket_detail.return_value = tnba_monitor.AutoresolveTicketDetailStatus.SUCCESS

        tnba_monitor._ticket_repository.build_tnba_note_for_AI_autoresolve.return_value = built_tnba_note

        with patch.object(testconfig, 'CURRENT_ENVIRONMENT', "production"):
            await tnba_monitor._process_ticket_detail(detail_object)

        tnba_monitor._prediction_repository.map_request_and_repair_completed_predictions.assert_called_once_with(
            ticket_detail_predictions
        )
        tnba_monitor._bruin_repository.get_next_results_for_ticket_detail.assert_awaited_once_with(
            ticket_id, ticket_detail_id, serial_number_1
        )
        tnba_monitor._prediction_repository.filter_predictions_in_next_results.assert_called_once_with(
            ticket_detail_predictions_with_mirrored_request_repair_completed, next_results_list
        )
        tnba_monitor._prediction_repository.get_best_prediction.assert_called_once_with(
            ticket_detail_predictions
        )
        tnba_monitor._prediction_repository.is_request_or_repair_completed_prediction.assert_called_once_with(
            confident_request_completed_prediction
        )
        tnba_monitor._autoresolve_ticket_detail.assert_awaited_once_with(
            detail_object=detail_object,
            best_prediction=confident_request_completed_prediction,
        )
        tnba_monitor._ticket_repository.build_tnba_note_from_prediction.assert_not_called()
        tnba_monitor._t7_repository.post_live_automation_metrics.assert_called_once_with(
            ticket_id, serial_number_1, automated_successfully=True
        )
        tnba_monitor._ticket_repository.build_tnba_note_for_AI_autoresolve.assert_called_once_with(serial_number_1)

        expected_note_for_append = make_payload_for_note_append_with_ticket_id(
            ticket_id=ticket_id,
            detail_id=ticket_detail_id,
            serial_number=serial_number_1,
            text=built_tnba_note,
        )
        assert tnba_monitor._tnba_notes_to_append == [
            expected_note_for_append,
        ]

    @pytest.mark.asyncio
    async def autoresolve_ticket_detail_ok_test(self, tnba_monitor, make_in_progress_ticket_detail,
                                                make_detail_object_with_predictions, make_edge_with_links_info,
                                                make_rpc_response, edge_1_connected, link_1_stable, link_2_stable,
                                                serial_number_1, confident_request_completed_prediction,
                                                make_metrics):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_creator = 'Intelygenz Ai'
        ticket_topic = 'VOO'

        ticket_detail = make_in_progress_ticket_detail(serial_number=serial_number_1, detail_id=ticket_detail_id)
        detail_object = make_detail_object_with_predictions(
            ticket_id=ticket_id,
            ticket_topic=ticket_topic,
            ticket_creator=ticket_creator,
            ticket_detail=ticket_detail,
            ticket_notes=[],
            ticket_detail_predictions=[confident_request_completed_prediction]
        )

        edge_status = make_edge_with_links_info(
            edge_info=edge_1_connected,
            links_info=[link_1_stable, link_2_stable],
        )
        edge_status_by_serial = {
            serial_number_1: edge_status,
        }
        tnba_monitor._edge_status_by_serial = edge_status_by_serial

        metrics = make_metrics()

        tnba_monitor._link_metrics_and_events_by_serial = {
            serial_number_1: [{'link_metrics': metrics, 'link_events': []}],
        }
        resolve_detail_response = make_rpc_response(body='ok', status=200)
        expected_autoresolved_status = tnba_monitor.AutoresolveTicketDetailStatus.SUCCESS

        tnba_monitor._bruin_repository.resolve_ticket_detail.return_value = resolve_detail_response

        with patch.object(testconfig, 'CURRENT_ENVIRONMENT', "production"):
            autoresolved_status = await tnba_monitor._autoresolve_ticket_detail(
                detail_object=detail_object,
                best_prediction=confident_request_completed_prediction,
            )

        tnba_monitor._ticket_repository.is_detail_in_outage_ticket.assert_called_once_with(detail_object)
        tnba_monitor._ticket_repository.is_detail_in_affecting_ticket.assert_called_once_with(detail_object)
        tnba_monitor._ticket_repository.was_ticket_created_by_automation_engine.assert_called_once_with(detail_object)
        tnba_monitor._prediction_repository.is_prediction_confident_enough.assert_called_once_with(
            confident_request_completed_prediction
        )
        tnba_monitor._is_there_an_outage.assert_called_once_with(edge_status)
        tnba_monitor._trouble_repository.are_all_metrics_within_thresholds.assert_not_called()
        tnba_monitor._bruin_repository.unpause_ticket_detail.assert_awaited_once_with(
            ticket_id, service_number=serial_number_1, detail_id=ticket_detail_id
        )
        tnba_monitor._bruin_repository.resolve_ticket_detail.assert_awaited_once_with(ticket_id, ticket_detail_id)
        assert autoresolved_status == expected_autoresolved_status

    @pytest.mark.asyncio
    async def autoresolve_ticket_detail_with_ticket_not_automatically_created_test(
            self, tnba_monitor, make_in_progress_ticket_detail, make_detail_object_with_predictions, serial_number_1,
            confident_request_completed_prediction, make_metrics):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_creator = 'Otacon'
        ticket_topic = 'VOO'

        metrics = make_metrics()

        tnba_monitor._link_metrics_and_events_by_serial = {
            serial_number_1: [{'link_metrics': metrics, 'link_events': []}],
        }

        ticket_detail = make_in_progress_ticket_detail(serial_number=serial_number_1, detail_id=ticket_detail_id)
        detail_object = make_detail_object_with_predictions(
            ticket_id=ticket_id,
            ticket_topic=ticket_topic,
            ticket_creator=ticket_creator,
            ticket_detail=ticket_detail,
            ticket_notes=[],
            ticket_detail_predictions=[confident_request_completed_prediction]
        )

        expected_autoresolved_status = tnba_monitor.AutoresolveTicketDetailStatus.SKIPPED

        autoresolved_status = await tnba_monitor._autoresolve_ticket_detail(
            detail_object=detail_object,
            best_prediction=confident_request_completed_prediction,
        )

        tnba_monitor._ticket_repository.was_ticket_created_by_automation_engine.assert_called_once_with(detail_object)
        tnba_monitor._ticket_repository.is_detail_in_outage_ticket.assert_not_called()
        tnba_monitor._ticket_repository.is_detail_in_affecting_ticket.assert_not_called()
        tnba_monitor._prediction_repository.is_prediction_confident_enough.assert_not_called()
        tnba_monitor._is_there_an_outage.assert_not_called()
        tnba_monitor._trouble_repository.are_all_metrics_within_thresholds.assert_not_called()
        tnba_monitor._bruin_repository.resolve_ticket_detail.assert_not_awaited()
        assert autoresolved_status == expected_autoresolved_status

    @pytest.mark.asyncio
    async def autoresolve_ticket_detail_with_prediction_having_insufficient_confidence_level_test(
            self, tnba_monitor, make_in_progress_ticket_detail, make_detail_object_with_predictions, serial_number_1,
            unconfident_request_completed_prediction, make_metrics,
            make_edge_with_links_info, edge_1_connected, link_1_stable, link_2_stable):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_creator = 'Intelygenz Ai'
        ticket_topic = 'VOO'

        edge_status = make_edge_with_links_info(
            edge_info=edge_1_connected,
            links_info=[link_1_stable, link_2_stable],
        )
        edge_status_by_serial = {
            serial_number_1: edge_status,
        }
        tnba_monitor._edge_status_by_serial = edge_status_by_serial

        metrics = make_metrics()

        tnba_monitor._link_metrics_and_events_by_serial = {
            serial_number_1: [{'link_metrics': metrics, 'link_events': []}],
        }

        ticket_detail = make_in_progress_ticket_detail(serial_number=serial_number_1, detail_id=ticket_detail_id)
        detail_object = make_detail_object_with_predictions(
            ticket_id=ticket_id,
            ticket_topic=ticket_topic,
            ticket_creator=ticket_creator,
            ticket_detail=ticket_detail,
            ticket_notes=[],
            ticket_detail_predictions=[unconfident_request_completed_prediction]
        )

        expected_autoresolved_status = tnba_monitor.AutoresolveTicketDetailStatus.SKIPPED

        autoresolved_status = await tnba_monitor._autoresolve_ticket_detail(
            detail_object=detail_object,
            best_prediction=unconfident_request_completed_prediction,
        )

        tnba_monitor._ticket_repository.was_ticket_created_by_automation_engine.assert_called_once_with(detail_object)
        tnba_monitor._prediction_repository.is_prediction_confident_enough.assert_called_once_with(
            unconfident_request_completed_prediction
        )
        tnba_monitor._is_there_an_outage.assert_called_once_with(edge_status)
        tnba_monitor._ticket_repository.is_detail_in_outage_ticket.assert_called_once_with(detail_object)
        tnba_monitor._ticket_repository.is_detail_in_affecting_ticket.assert_called_once_with(detail_object)
        tnba_monitor._trouble_repository.are_all_metrics_within_thresholds.assert_not_called()
        tnba_monitor._bruin_repository.resolve_ticket_detail.assert_not_awaited()
        assert autoresolved_status == expected_autoresolved_status

    @pytest.mark.asyncio
    async def autoresolve_ticket_detail_with_edge_in_outage_state_test(self, tnba_monitor,
                                                                       make_in_progress_ticket_detail,
                                                                       make_detail_object_with_predictions,
                                                                       make_edge_with_links_info,
                                                                       edge_1_offline, link_1_disconnected,
                                                                       link_2_disconnected, serial_number_1,
                                                                       confident_request_completed_prediction,
                                                                       make_metrics):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_creator = 'Intelygenz Ai'
        ticket_topic = 'VOO'

        metrics = make_metrics()

        tnba_monitor._link_metrics_and_events_by_serial = {
            serial_number_1: [{'link_metrics': metrics, 'link_events': []}],
        }

        ticket_detail = make_in_progress_ticket_detail(serial_number=serial_number_1, detail_id=ticket_detail_id)
        detail_object = make_detail_object_with_predictions(
            ticket_id=ticket_id,
            ticket_topic=ticket_topic,
            ticket_creator=ticket_creator,
            ticket_detail=ticket_detail,
            ticket_notes=[],
            ticket_detail_predictions=[confident_request_completed_prediction]
        )

        edge_status = make_edge_with_links_info(
            edge_info=edge_1_offline,
            links_info=[link_1_disconnected, link_2_disconnected],
        )
        edge_status_by_serial = {
            serial_number_1: edge_status,
        }
        tnba_monitor._edge_status_by_serial = edge_status_by_serial

        expected_autoresolved_status = tnba_monitor.AutoresolveTicketDetailStatus.BAD_PREDICTION

        autoresolved_status = await tnba_monitor._autoresolve_ticket_detail(
            detail_object=detail_object,
            best_prediction=confident_request_completed_prediction,
        )

        tnba_monitor._ticket_repository.was_ticket_created_by_automation_engine.assert_called_once_with(detail_object)
        tnba_monitor._prediction_repository.is_prediction_confident_enough.assert_not_called()
        tnba_monitor._is_there_an_outage.assert_called_once_with(edge_status)
        tnba_monitor._ticket_repository.is_detail_in_outage_ticket.assert_called_once_with(detail_object)
        tnba_monitor._ticket_repository.is_detail_in_affecting_ticket.assert_not_called()
        tnba_monitor._trouble_repository.are_all_metrics_within_thresholds.assert_not_called()
        tnba_monitor._bruin_repository.resolve_ticket_detail.assert_not_awaited()
        assert autoresolved_status == expected_autoresolved_status

    @pytest.mark.asyncio
    async def autoresolve_ticket_detail_with_affecting_not_all_metrics_within_threshold_test(
            self, tnba_monitor, make_in_progress_ticket_detail, make_detail_object_with_predictions, serial_number_1,
            unconfident_request_completed_prediction, make_metrics,
            make_edge_with_links_info, edge_1_connected, link_1_stable, link_2_stable):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_creator = 'Intelygenz Ai'
        ticket_topic = 'VAS'

        edge_status = make_edge_with_links_info(
            edge_info=edge_1_connected,
            links_info=[link_1_stable, link_2_stable],
        )
        edge_status_by_serial = {
            serial_number_1: edge_status,
        }
        tnba_monitor._edge_status_by_serial = edge_status_by_serial

        metrics = make_metrics()

        tnba_monitor._link_metrics_and_events_by_serial = {
            serial_number_1: [{'link_metrics': metrics, 'link_events': []}],
        }

        ticket_detail = make_in_progress_ticket_detail(serial_number=serial_number_1, detail_id=ticket_detail_id)
        detail_object = make_detail_object_with_predictions(
            ticket_id=ticket_id,
            ticket_topic=ticket_topic,
            ticket_creator=ticket_creator,
            ticket_detail=ticket_detail,
            ticket_notes=[],
            ticket_detail_predictions=[unconfident_request_completed_prediction]
        )

        tnba_monitor._trouble_repository.are_all_metrics_within_thresholds = Mock(return_value=False)
        expected_autoresolved_status = tnba_monitor.AutoresolveTicketDetailStatus.BAD_PREDICTION

        autoresolved_status = await tnba_monitor._autoresolve_ticket_detail(
            detail_object=detail_object,
            best_prediction=unconfident_request_completed_prediction,
        )

        tnba_monitor._ticket_repository.was_ticket_created_by_automation_engine.assert_called_once_with(detail_object)
        tnba_monitor._is_there_an_outage.assert_not_called()
        tnba_monitor._ticket_repository.is_detail_in_outage_ticket.assert_called_once_with(detail_object)
        tnba_monitor._ticket_repository.is_detail_in_affecting_ticket.assert_called_once_with(detail_object)
        tnba_monitor._trouble_repository.are_all_metrics_within_thresholds.assert_called_once_with(
            tnba_monitor._link_metrics_and_events_by_serial[serial_number_1])
        tnba_monitor._bruin_repository.resolve_ticket_detail.assert_not_awaited()
        tnba_monitor._prediction_repository.is_prediction_confident_enough.assert_not_called()
        assert autoresolved_status == expected_autoresolved_status

    @pytest.mark.asyncio
    async def autoresolve_ticket_detail_with_non_production_environment_test(self, tnba_monitor,
                                                                             make_in_progress_ticket_detail,
                                                                             make_detail_object_with_predictions,
                                                                             make_edge_with_links_info,
                                                                             edge_1_connected, link_1_stable,
                                                                             link_2_stable, serial_number_1,
                                                                             confident_request_completed_prediction,
                                                                             make_metrics):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_creator = 'Intelygenz Ai'
        ticket_topic = 'VOO'

        metrics = make_metrics()

        tnba_monitor._link_metrics_and_events_by_serial = {
            serial_number_1: [{'link_metrics': metrics, 'link_events': []}],
        }

        ticket_detail = make_in_progress_ticket_detail(serial_number=serial_number_1, detail_id=ticket_detail_id)
        detail_object = make_detail_object_with_predictions(
            ticket_id=ticket_id,
            ticket_topic=ticket_topic,
            ticket_creator=ticket_creator,
            ticket_detail=ticket_detail,
            ticket_notes=[],
            ticket_detail_predictions=[confident_request_completed_prediction]
        )

        edge_status = make_edge_with_links_info(
            edge_info=edge_1_connected,
            links_info=[link_1_stable, link_2_stable],
        )
        edge_status_by_serial = {
            serial_number_1: edge_status,
        }
        tnba_monitor._edge_status_by_serial = edge_status_by_serial

        with patch.object(testconfig, 'CURRENT_ENVIRONMENT', "dev"):
            expected_autoresolved_status = tnba_monitor.AutoresolveTicketDetailStatus.SKIPPED

            autoresolved_status = await tnba_monitor._autoresolve_ticket_detail(
                detail_object=detail_object,
                best_prediction=confident_request_completed_prediction,
            )

        tnba_monitor._ticket_repository.was_ticket_created_by_automation_engine.assert_called_once_with(detail_object)
        tnba_monitor._prediction_repository.is_prediction_confident_enough.assert_called_once_with(
            confident_request_completed_prediction
        )
        tnba_monitor._ticket_repository.is_detail_in_outage_ticket.assert_called_once_with(detail_object)
        tnba_monitor._ticket_repository.is_detail_in_affecting_ticket.assert_called_once_with(detail_object)
        tnba_monitor._trouble_repository.are_all_metrics_within_thresholds.assert_not_called()
        tnba_monitor._is_there_an_outage.assert_called_once_with(edge_status)
        tnba_monitor._bruin_repository.resolve_ticket_detail.assert_not_awaited()
        assert autoresolved_status == expected_autoresolved_status

    @pytest.mark.asyncio
    async def autoresolve_ticket_detail_with_failure_in_autoresolve_request_test(
            self, tnba_monitor, make_in_progress_ticket_detail, make_detail_object_with_predictions,
            make_edge_with_links_info, make_rpc_response, edge_1_connected, link_1_stable, link_2_stable,
            serial_number_1, confident_request_completed_prediction, make_metrics):
        ticket_id = 12345
        ticket_detail_id = 1
        ticket_creator = 'Intelygenz Ai'
        ticket_topic = 'VOO'

        metrics = make_metrics()

        tnba_monitor._link_metrics_and_events_by_serial = {
            serial_number_1: [{'link_metrics': metrics, 'link_events': []}],
        }

        ticket_detail = make_in_progress_ticket_detail(serial_number=serial_number_1, detail_id=ticket_detail_id)
        detail_object = make_detail_object_with_predictions(
            ticket_id=ticket_id,
            ticket_topic=ticket_topic,
            ticket_creator=ticket_creator,
            ticket_detail=ticket_detail,
            ticket_notes=[],
            ticket_detail_predictions=[confident_request_completed_prediction]
        )

        edge_status = make_edge_with_links_info(
            edge_info=edge_1_connected,
            links_info=[link_1_stable, link_2_stable],
        )
        edge_status_by_serial = {
            serial_number_1: edge_status,
        }
        tnba_monitor._edge_status_by_serial = edge_status_by_serial

        resolve_detail_response = make_rpc_response(
            body='Got internal error from Bruin',
            status=500,
        )

        tnba_monitor._bruin_repository.resolve_ticket_detail.return_value = resolve_detail_response

        with patch.object(testconfig, 'CURRENT_ENVIRONMENT', "production"):
            expected_autoresolved_status = tnba_monitor.AutoresolveTicketDetailStatus.SKIPPED

            autoresolved_status = await tnba_monitor._autoresolve_ticket_detail(
                detail_object=detail_object,
                best_prediction=confident_request_completed_prediction,
            )

        tnba_monitor._ticket_repository.was_ticket_created_by_automation_engine.assert_called_once_with(detail_object)
        tnba_monitor._prediction_repository.is_prediction_confident_enough.assert_called_once_with(
            confident_request_completed_prediction
        )
        tnba_monitor._ticket_repository.is_detail_in_outage_ticket.assert_called_once_with(detail_object)
        tnba_monitor._ticket_repository.is_detail_in_affecting_ticket.assert_called_once_with(detail_object)
        tnba_monitor._is_there_an_outage.assert_called_once_with(edge_status)
        tnba_monitor._trouble_repository.are_all_metrics_within_thresholds.assert_not_called()
        tnba_monitor._bruin_repository.resolve_ticket_detail.assert_awaited_once_with(ticket_id, ticket_detail_id)
        assert autoresolved_status == expected_autoresolved_status

    @pytest.mark.asyncio
    async def append_tnba_notes_test(self, tnba_monitor, make_payload_for_note_append_with_ticket_id,
                                     make_payload_for_note_append, make_rpc_response, serial_number_1, serial_number_2):
        ticket_1_id = 12345
        ticket_2_id = 67890

        ticket_detail_1_id = 12345
        ticket_detail_2_id = 67890
        ticket_detail_3_id = 87654

        tnba_note_1_text = 'This is a TNBA note (1)'
        tnba_note_2_text = 'This is a TNBA note (2)'
        tnba_note_3_text = 'This is a TNBA note (3)'

        ticket_1_note_1 = make_payload_for_note_append(
            serial_number=serial_number_1,
            detail_id=ticket_detail_1_id,
            text=tnba_note_1_text,
        )
        ticket_1_note_2 = make_payload_for_note_append(
            serial_number=serial_number_2,
            detail_id=ticket_detail_2_id,
            text=tnba_note_2_text,
        )
        ticket_2_note_1 = make_payload_for_note_append(
            serial_number=serial_number_1,
            detail_id=ticket_detail_3_id,
            text=tnba_note_3_text,
        )

        ticket_1_notes = [
            ticket_1_note_1,
            ticket_1_note_2,
        ]
        ticket_2_notes = [
            ticket_2_note_1,
        ]

        append_notes_response = make_rpc_response(body='ok', status=200)

        tnba_monitor._bruin_repository.append_multiple_notes_to_ticket.return_value = append_notes_response
        tnba_monitor._notifications_repository.send_slack_message = CoroutineMock()

        ticket_1_note_1_with_ticket_id = make_payload_for_note_append_with_ticket_id(
            ticket_id=ticket_1_id,
            serial_number=serial_number_1,
            detail_id=ticket_detail_1_id,
            text=tnba_note_1_text,
        )
        ticket_1_note_2_with_ticket_id = make_payload_for_note_append_with_ticket_id(
            ticket_id=ticket_1_id,
            serial_number=serial_number_2,
            detail_id=ticket_detail_2_id,
            text=tnba_note_2_text,
        )
        ticket_2_note_1_with_ticket_id = make_payload_for_note_append_with_ticket_id(
            ticket_id=ticket_2_id,
            serial_number=serial_number_1,
            detail_id=ticket_detail_3_id,
            text=tnba_note_3_text,
        )
        tnba_monitor._tnba_notes_to_append = [
            ticket_1_note_1_with_ticket_id,
            ticket_1_note_2_with_ticket_id,
            ticket_2_note_1_with_ticket_id,
        ]

        await tnba_monitor._append_tnba_notes()

        tnba_monitor._bruin_repository.append_multiple_notes_to_ticket.assert_has_awaits([
            call(ticket_1_id, ticket_1_notes),
            call(ticket_2_id, ticket_2_notes),
        ])
        assert tnba_monitor._notifications_repository.send_slack_message.await_count == 2

    def is_there_an_outage_test(self, tnba_monitor, make_edge_with_links_info, edge_1_connected, edge_1_offline,
                                link_1_stable, link_1_disconnected, link_2_stable, link_2_disconnected):
        edge_with_links_info = make_edge_with_links_info(
            edge_info=edge_1_connected,
            links_info=[link_1_stable, link_2_stable],
        )
        result = tnba_monitor._is_there_an_outage(edge_with_links_info)
        assert result is False

        edge_with_links_info = make_edge_with_links_info(
            edge_info=edge_1_offline,
            links_info=[link_1_disconnected, link_2_disconnected],
        )
        result = tnba_monitor._is_there_an_outage(edge_with_links_info)
        assert result is True

        edge_with_links_info = make_edge_with_links_info(
            edge_info=edge_1_offline,
            links_info=[link_1_stable, link_2_disconnected],
        )
        result = tnba_monitor._is_there_an_outage(edge_with_links_info)
        assert result is True

    def is_faulty_edge_test(self, edge_1_connected, edge_1_offline):
        edge_state_1 = edge_1_connected['edgeState']
        edge_state_2 = edge_1_offline['edgeState']

        result = TNBAMonitor._is_faulty_edge(edge_state_1)
        assert result is False

        result = TNBAMonitor._is_faulty_edge(edge_state_2)
        assert result is True

    def is_faulty_link_test(self, link_1_stable, link_1_disconnected):
        link_state_1 = link_1_stable['linkState']
        link_state_2 = link_1_disconnected['linkState']

        result = TNBAMonitor._is_faulty_link(link_state_1)
        assert result is False

        result = TNBAMonitor._is_faulty_link(link_state_2)
        assert result is True
