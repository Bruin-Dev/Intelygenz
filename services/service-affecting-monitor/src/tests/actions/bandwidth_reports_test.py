from datetime import datetime, timedelta
from datetime import timezone as tz
from unittest.mock import Mock, patch

import pytest
from application.actions import bandwidth_reports as bandwidth_reports_module
from application.actions.bandwidth_reports import BandwidthReports
from apscheduler.triggers.cron import CronTrigger
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(bandwidth_reports_module, "uuid", return_value=uuid_)

frozen_datetime = datetime.strptime("20/12/2021", "%d/%m/%Y")
datetime_mock = Mock()
datetime_mock.utcnow = Mock(return_value=frozen_datetime)


class TestBandwidthReports:
    def instance_test(
        self,
        bandwidth_reports,
        logger,
        scheduler,
        velocloud_repository,
        bruin_repository,
        trouble_repository,
        customer_cache_repository,
        notifications_repository,
        utils_repository,
        template_repository,
    ):
        assert bandwidth_reports._logger is logger
        assert bandwidth_reports._scheduler is scheduler
        assert bandwidth_reports._config is testconfig
        assert bandwidth_reports._velocloud_repository is velocloud_repository
        assert bandwidth_reports._bruin_repository is bruin_repository
        assert bandwidth_reports._trouble_repository is trouble_repository
        assert bandwidth_reports._customer_cache_repository is customer_cache_repository
        assert bandwidth_reports._notifications_repository is notifications_repository
        assert bandwidth_reports._utils_repository is utils_repository
        assert bandwidth_reports._template_repository is template_repository

    @pytest.mark.asyncio
    async def start_bandwidth_reports_job__exec_on_start_test(self, bandwidth_reports):
        bandwidth_reports._bandwidth_reports_job = CoroutineMock()
        await bandwidth_reports.start_bandwidth_reports_job(exec_on_start=True)
        bandwidth_reports._bandwidth_reports_job.assert_awaited_once()
        bandwidth_reports._scheduler.add_job.assert_called_once()

    @pytest.mark.asyncio
    async def start_bandwidth_reports_job__schedule_test(self, bandwidth_reports):
        bandwidth_reports._bandwidth_reports_job = CoroutineMock()
        await bandwidth_reports.start_bandwidth_reports_job()
        bandwidth_reports._bandwidth_reports_job.assert_not_awaited()
        bandwidth_reports._scheduler.add_job.assert_called_once()

    @pytest.mark.asyncio
    async def bandwidth_reports_job_test(
        self,
        bandwidth_reports,
        make_bruin_client_info,
        make_cached_edge,
        make_customer_cache,
        make_metrics_for_link,
        make_rpc_response,
    ):
        client_id = 9994
        client_name = "MetTel"
        serial_number = "VC1234567"

        bruin_client_info = make_bruin_client_info(client_id=client_id, client_name=client_name)
        cached_edge = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)
        customer_cache = make_customer_cache(cached_edge)

        link_metrics = make_metrics_for_link()
        links_metrics = [link_metrics]

        response_1 = make_rpc_response(body=customer_cache, status=200)
        response_2 = make_rpc_response(body=links_metrics, status=200)

        bandwidth_reports._customer_cache_repository.get_cache_for_affecting_monitoring.return_value = response_1
        bandwidth_reports._velocloud_repository.get_links_metrics_for_bandwidth_reports.return_value = response_2
        bandwidth_reports._generate_bandwidth_report_for_client = CoroutineMock()

        await bandwidth_reports._bandwidth_reports_job()

        bandwidth_reports._customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        bandwidth_reports._velocloud_repository.get_links_metrics_for_bandwidth_reports.assert_awaited_once()
        bandwidth_reports._generate_bandwidth_report_for_client.assert_awaited_once_with(
            client_id, client_name, {serial_number}, links_metrics, customer_cache
        )

    @pytest.mark.asyncio
    async def generate_bandwidth_report_for_client_test(
        self,
        bandwidth_reports,
        make_edge_full_id,
        make_bruin_client_info,
        make_cached_edge,
        make_customer_cache,
        make_link,
        make_edge,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_ticket,
        make_detail_item,
        make_ticket_note,
        make_ticket_details,
    ):
        host = "mettel.velocloud.net"
        enterprise_id = 1
        edge_id = 123
        client_id = 9994
        client_name = "MetTel"
        serial_number = "VC1234567"
        ticket_id = 12345
        edge_name = "Test Edge"
        interface = "GE1"

        edge_full_id = make_edge_full_id(host=host, enterprise_id=enterprise_id, edge_id=edge_id)
        bruin_client_info = make_bruin_client_info(client_id=client_id, client_name=client_name)
        cached_edge = make_cached_edge(
            serial_number=serial_number, full_id=edge_full_id, bruin_client_info=bruin_client_info
        )
        customer_cache = make_customer_cache(cached_edge)

        link = make_link(interface=interface)
        edge = make_edge(
            host=host, enterprise_id=enterprise_id, id_=edge_id, serial_number=serial_number, name=edge_name
        )
        link_with_edge = make_link_with_edge_info(link_info=link, edge_info=edge)
        link_metrics = make_metrics_for_link(link_with_edge_info=link_with_edge)
        links_metrics = [link_metrics]

        ticket = make_ticket(ticket_id=ticket_id)
        detail_item = make_detail_item(value=serial_number)
        note = make_ticket_note(
            text="#*MetTel's IPA*#\nTrouble: Bandwidth Over Utilization\nInterface: GE1",
            service_numbers=[serial_number],
        )
        ticket_details = make_ticket_details(detail_items=[detail_item], notes=[note])
        tickets = {
            ticket_id: {
                "ticket": ticket,
                "ticket_details": ticket_details,
            }
        }

        bandwidth_reports._bruin_repository.get_affecting_ticket_for_report.return_value = tickets

        with patch.object(bandwidth_reports._config, "CURRENT_ENVIRONMENT", "production"):
            await bandwidth_reports._generate_bandwidth_report_for_client(
                client_id, client_name, {serial_number}, links_metrics, customer_cache
            )

        report_items = [
            {
                "serial_number": serial_number,
                "edge_name": edge_name,
                "interface": interface,
                "bandwidth": "0.0 bps",
                "threshold_exceeded": 1,
                "ticket_ids": {ticket_id},
            }
        ]

        bandwidth_reports._template_repository.compose_bandwidth_report_email.assert_called_once_with(
            client_id=client_id, client_name=client_name, report_items=report_items
        )
        bandwidth_reports._notifications_repository.send_email.assert_awaited_once()

    def add_bandwidth_to_links_metrics_test(self, bandwidth_reports, make_metrics):
        bytes_rx = 9_600_000
        bytes_tx = 12_000_000
        link_metrics = make_metrics(bytes_rx=bytes_rx, bytes_tx=bytes_tx)
        links_metrics = [link_metrics]

        bandwidth_reports._utils_repository.humanize_bps.side_effect = lambda bps: bps
        result = bandwidth_reports._add_bandwidth_to_links_metrics(links_metrics)
        assert result[0]["avgBandwidth"] == 1_000

    def get_start_date_test(self, bandwidth_reports):
        with patch.object(bandwidth_reports_module, "datetime", new=datetime_mock):
            result = bandwidth_reports._get_start_date()
        assert result == "2021-12-19T00:00:00Z"

    def get_end_date_test(self, bandwidth_reports):
        with patch.object(bandwidth_reports_module, "datetime", new=datetime_mock):
            result = bandwidth_reports._get_end_date()
        assert result == "2021-12-20T00:00:00Z"
