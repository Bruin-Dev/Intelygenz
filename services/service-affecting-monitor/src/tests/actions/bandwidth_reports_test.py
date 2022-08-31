from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from application.actions import bandwidth_reports as bandwidth_reports_module
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
            email_repository,
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
        assert bandwidth_reports._email_repository is email_repository
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
        edge = {'host': 'test', 'edge_id': 1, 'enterprise_id': 2}

        bruin_client_info = make_bruin_client_info(client_id=client_id, client_name=client_name)
        cached_edge = make_cached_edge(full_id=edge, serial_number=serial_number, bruin_client_info=bruin_client_info)
        customer_cache = make_customer_cache(cached_edge)

        link_metrics = make_metrics_for_link()
        links_metrics = [link_metrics]

        response_1 = make_rpc_response(body=customer_cache, status=200)
        response_2 = make_rpc_response(body=links_metrics, status=200)

        bandwidth_reports._customer_cache_repository.get_cache_for_affecting_monitoring.return_value = response_1
        bandwidth_reports._velocloud_repository.get_edge_link_series_for_bandwidth_reports.return_value = response_2
        bandwidth_reports._generate_bandwidth_report_for_client = CoroutineMock()

        await bandwidth_reports._bandwidth_reports_job()

        bandwidth_reports._customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        bandwidth_reports._generate_bandwidth_report_for_client.assert_awaited_once_with(
            client_id, client_name, {serial_number}, links_metrics
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
        # link_metrics = make_metrics_for_link(link_with_edge_info=link_with_edge)
        # links_metrics = [link_metrics]
        link_series = [
            {
                "series": [
                    {
                        "metric": "bytesRx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    },
                    {
                        "metric": "bytesTx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    },
                    {
                        "metric": "bpsOfBestPathRx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    },
                    {
                        "metric": "bpsOfBestPathTx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    }
                ],
                "linkId": 9388,
                "edgeId": 2800,
                "serial_number": serial_number,
                "edge_name": edge_name,
                "link": {
                    "id": 9388,
                    "created": "2019-03-28T18:34:00.000Z",
                    "edgeId": 2800,
                    "logicalId": "00:14:3e:44:41:6f:0000",
                    "internalId": "00000003-9e57-4087-a20f-1af16190cd15",
                    "interface": interface,
                    "macAddress": None,
                    "overlayType": "IPv4",
                    "ipAddress": "63.43.3.127",
                    "ipV6Address": None,
                    "netmask": None,
                    "networkSide": "WAN",
                    "networkType": "ETHERNET",
                    "displayName": "Verizon Wireless( MTL- 544825157)",
                    "userOverride": 0,
                    "isp": "Verizon Wireless",
                    "org": "Verizon Wireless",
                    "lat": 37.750999,
                    "lon": -97.821999,
                    "lastActive": "2022-08-30T12:04:42.000Z",
                    "state": "STABLE",
                    "backupState": "UNCONFIGURED",
                    "linkMode": "ACTIVE",
                    "vpnState": "STABLE",
                    "lastEvent": "2022-08-06T05:27:54.000Z",
                    "lastEventState": "STABLE",
                    "alertsEnabled": 1,
                    "operatorAlertsEnabled": 1,
                    "serviceState": "IN_SERVICE",
                    "modified": "2022-08-30T12:04:42.000Z"
                }
            }
        ]

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
                client_id, client_name, {serial_number}, link_series
            )

        report_items = [
            {
                "serial_number": serial_number,
                "edge_name": edge_name,
                "interface": interface,
                "avg_bandwidth": "0.0 bps",
                "down_bytes_total": "0.0 bps",
                "up_bytes_total": "0.0 bps",
                "measured_bandwidth_down": "0.0 bps",
                "measured_bandwidth_up": "0.0 bps",
                "peak_bytes_down": "0.0 bps",
                "peak_bytes_up": "0.0 bps",
                "peak_percent_down": 0.0,
                "peak_percent_up": 0.0,
                "threshold_exceeded": 1,
                "ticket_ids": {ticket_id},
            }
        ]

        bandwidth_reports._template_repository.compose_bandwidth_report_email.assert_called_once_with(
            client_id=client_id, client_name=client_name, report_items=report_items
        )
        bandwidth_reports._email_repository.send_email.assert_awaited_once()

    def add_bandwidth_to_links_metrics_test(self, bandwidth_reports, make_metrics):
        serial_number = "VC1234567"
        edge_name = "Test Edge"
        interface = "GE1"
        link_series = [
            {
                "series": [
                    {
                        "metric": "bytesRx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    },
                    {
                        "metric": "bytesTx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    },
                    {
                        "metric": "bpsOfBestPathRx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    },
                    {
                        "metric": "bpsOfBestPathTx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    }
                ],
                "linkId": 9388,
                "edgeId": 2800,
                "serial_number": serial_number,
                "edge_name": edge_name,
                "link": {
                    "id": 9388,
                    "created": "2019-03-28T18:34:00.000Z",
                    "edgeId": 2800,
                    "logicalId": "00:14:3e:44:41:6f:0000",
                    "internalId": "00000003-9e57-4087-a20f-1af16190cd15",
                    "interface": interface,
                    "macAddress": None,
                    "overlayType": "IPv4",
                    "ipAddress": "63.43.3.127",
                    "ipV6Address": None,
                    "netmask": None,
                    "networkSide": "WAN",
                    "networkType": "ETHERNET",
                    "displayName": "Verizon Wireless( MTL- 544825157)",
                    "userOverride": 0,
                    "isp": "Verizon Wireless",
                    "org": "Verizon Wireless",
                    "lat": 37.750999,
                    "lon": -97.821999,
                    "lastActive": "2022-08-30T12:04:42.000Z",
                    "state": "STABLE",
                    "backupState": "UNCONFIGURED",
                    "linkMode": "ACTIVE",
                    "vpnState": "STABLE",
                    "lastEvent": "2022-08-06T05:27:54.000Z",
                    "lastEventState": "STABLE",
                    "alertsEnabled": 1,
                    "operatorAlertsEnabled": 1,
                    "serviceState": "IN_SERVICE",
                    "modified": "2022-08-30T12:04:42.000Z"
                }
            }
        ]

        bandwidth_reports._utils_repository.humanize_bps.side_effect = lambda bps: bps
        result = bandwidth_reports._add_bandwidth_to_links_metrics(link_series)
        assert result[0]["average_bandwidth"] == 0.0

    def get_start_date_test(self, bandwidth_reports):
        with patch.object(bandwidth_reports_module, "datetime", new=datetime_mock):
            result = bandwidth_reports._get_start_date()
        assert result == "2021-12-19T00:00:00Z"

    def get_end_date_test(self, bandwidth_reports):
        with patch.object(bandwidth_reports_module, "datetime", new=datetime_mock):
            result = bandwidth_reports._get_end_date()
        assert result == "2021-12-20T00:00:00Z"

    def add_bandwidth_to_links_metrics_not_none_test(self, bandwidth_reports, make_metrics):
        serial_number = "VC1234567"
        edge_name = "Test Edge"
        interface = "GE1"
        link_series = [
            {
                "series": [
                    {
                        "metric": "bytesRx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    },
                    {
                        "metric": "bytesTx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    },
                    {
                        "metric": "bpsOfBestPathRx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    },
                    {
                        "metric": "bpsOfBestPathTx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    }
                ],
                "linkId": 9388,
                "edgeId": 2800,
                "serial_number": serial_number,
                "edge_name": edge_name,
                "link": {
                    "id": 9388,
                    "created": "2019-03-28T18:34:00.000Z",
                    "edgeId": 2800,
                    "logicalId": "00:14:3e:44:41:6f:0000",
                    "internalId": "00000003-9e57-4087-a20f-1af16190cd15",
                    "interface": interface,
                    "macAddress": None,
                    "overlayType": "IPv4",
                    "ipAddress": "63.43.3.127",
                    "ipV6Address": None,
                    "netmask": None,
                    "networkSide": "WAN",
                    "networkType": "ETHERNET",
                    "displayName": "Verizon Wireless( MTL- 544825157)",
                    "userOverride": 0,
                    "isp": "Verizon Wireless",
                    "org": "Verizon Wireless",
                    "lat": 37.750999,
                    "lon": -97.821999,
                    "lastActive": "2022-08-30T12:04:42.000Z",
                    "state": "STABLE",
                    "backupState": "UNCONFIGURED",
                    "linkMode": "ACTIVE",
                    "vpnState": "STABLE",
                    "lastEvent": "2022-08-06T05:27:54.000Z",
                    "lastEventState": "STABLE",
                    "alertsEnabled": 1,
                    "operatorAlertsEnabled": 1,
                    "serviceState": "IN_SERVICE",
                    "modified": "2022-08-30T12:04:42.000Z"
                }
            }
        ]
        bandwidth_reports._utils_repository.humanize_bps.side_effect = lambda bps: bps
        result = bandwidth_reports._add_bandwidth_to_links_metrics(
            link_series)
        assert result is not None

    def add_bandwidth_to_links_metrics_is_dict_test(self, bandwidth_reports, make_metrics):
        serial_number = "VC1234567"
        edge_name = "Test Edge"
        interface = "GE1"
        link_series = [
            {
                "series": [
                    {
                        "metric": "bytesRx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    },
                    {
                        "metric": "bytesTx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    },
                    {
                        "metric": "bpsOfBestPathRx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    },
                    {
                        "metric": "bpsOfBestPathTx",
                        "startTime": 1659636000000,
                        "tickInterval": 300000,
                        "data": [
                            0.0
                        ],
                        "total": 0.0,
                        "min": 0.0,
                        "max": 0.0
                    }
                ],
                "linkId": 9388,
                "edgeId": 2800,
                "serial_number": serial_number,
                "edge_name": edge_name,
                "link": {
                    "id": 9388,
                    "created": "2019-03-28T18:34:00.000Z",
                    "edgeId": 2800,
                    "logicalId": "00:14:3e:44:41:6f:0000",
                    "internalId": "00000003-9e57-4087-a20f-1af16190cd15",
                    "interface": interface,
                    "macAddress": None,
                    "overlayType": "IPv4",
                    "ipAddress": "63.43.3.127",
                    "ipV6Address": None,
                    "netmask": None,
                    "networkSide": "WAN",
                    "networkType": "ETHERNET",
                    "displayName": "Verizon Wireless( MTL- 544825157)",
                    "userOverride": 0,
                    "isp": "Verizon Wireless",
                    "org": "Verizon Wireless",
                    "lat": 37.750999,
                    "lon": -97.821999,
                    "lastActive": "2022-08-30T12:04:42.000Z",
                    "state": "STABLE",
                    "backupState": "UNCONFIGURED",
                    "linkMode": "ACTIVE",
                    "vpnState": "STABLE",
                    "lastEvent": "2022-08-06T05:27:54.000Z",
                    "lastEventState": "STABLE",
                    "alertsEnabled": 1,
                    "operatorAlertsEnabled": 1,
                    "serviceState": "IN_SERVICE",
                    "modified": "2022-08-30T12:04:42.000Z"
                }
            }
        ]
        bandwidth_reports._utils_repository.humanize_bps.side_effect = lambda bps: bps
        result = bandwidth_reports._add_bandwidth_to_links_metrics(
            link_series)
        assert isinstance(result, list)
