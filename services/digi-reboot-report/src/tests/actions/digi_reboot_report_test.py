from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, call, patch

import pytest
from application.actions import digi_reboot_report as digi_reboot_report_module
from application.actions.digi_reboot_report import DiGiRebootReport
from apscheduler.util import undefined
from asynctest import CoroutineMock
from config import testconfig


class TestDiGiRebootReport:
    def instance_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        digi_repository = Mock()
        email_repository = Mock()

        digi_reboot_report = DiGiRebootReport(
            event_bus, scheduler, logger, config, bruin_repository, digi_repository, email_repository
        )

        assert digi_reboot_report._event_bus == event_bus
        assert digi_reboot_report._scheduler == scheduler
        assert digi_reboot_report._logger == logger
        assert digi_reboot_report._config == config
        assert digi_reboot_report._bruin_repository == bruin_repository
        assert digi_reboot_report._digi_repository == digi_repository
        assert digi_reboot_report._email_repository == email_repository

    @pytest.mark.asyncio
    async def start_digi_reboot_report_job_with_exec_on_start_test(self):
        event_bus = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()

        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        digi_repository = Mock()
        email_repository = Mock()

        digi_reboot_report = DiGiRebootReport(
            event_bus, scheduler, logger, config, bruin_repository, digi_repository, email_repository
        )
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(digi_reboot_report_module, "datetime", new=datetime_mock):
            with patch.object(digi_reboot_report_module, "timezone", new=Mock()):
                await digi_reboot_report.start_digi_reboot_report_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            digi_reboot_report._digi_reboot_report_process,
            "interval",
            minutes=config.DIGI_CONFIG["digi_reboot_report_time"],
            next_run_time=next_run_time,
            replace_existing=False,
            id="_digi_reboot_report",
        )

    @pytest.mark.asyncio
    async def start_digi_reboot_report_job_with_exec_on_start_false_test(self):
        event_bus = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()

        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        digi_repository = Mock()
        email_repository = Mock()

        digi_reboot_report = DiGiRebootReport(
            event_bus, scheduler, logger, config, bruin_repository, digi_repository, email_repository
        )

        await digi_reboot_report.start_digi_reboot_report_job()

        scheduler.add_job.assert_called_once_with(
            digi_reboot_report._digi_reboot_report_process,
            "interval",
            minutes=config.DIGI_CONFIG["digi_reboot_report_time"],
            next_run_time=undefined,
            replace_existing=False,
            id="_digi_reboot_report",
        )

    @pytest.mark.asyncio
    async def digi_reboot_report_process_test(self):
        digi_recovery_logs_response = {"body": {"Logs": [{"TicketID": "123"}, {"TicketID": "321"}]}, "status": 200}

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        email_repository = Mock()

        digi_repository = Mock()
        digi_repository.get_digi_recovery_logs = CoroutineMock(return_value=digi_recovery_logs_response)

        digi_reboot_report = DiGiRebootReport(
            event_bus, scheduler, logger, config, bruin_repository, digi_repository, email_repository
        )

        ticket_id_list = ["123", "321"]
        ticket_task_history_map = {
            "123": {"ClientName": "Le Duff Management ", "Ticket Entered Date": "202008242225"},
            "321": {"ClientName": "Test", "Ticket Entered Date": "202008242225"},
        }
        digi_reboot_report._get_all_ticket_ids_from_digi_recovery_logs = Mock(return_value=ticket_id_list)
        digi_reboot_report._get_ticket_task_histories = CoroutineMock(return_value=ticket_task_history_map)
        digi_reboot_report._merge_recovery_logs = CoroutineMock()
        digi_reboot_report._generate_and_email_csv_file = CoroutineMock()

        await digi_reboot_report._digi_reboot_report_process()

        assert digi_reboot_report._digi_recovery_logs == digi_recovery_logs_response["body"]["Logs"]
        digi_reboot_report._get_all_ticket_ids_from_digi_recovery_logs.assert_called_once()
        digi_reboot_report._get_ticket_task_histories.assert_called_once_with(ticket_id_list)
        digi_reboot_report._merge_recovery_logs.assert_called_once_with(ticket_task_history_map)
        digi_reboot_report._generate_and_email_csv_file.assert_awaited_once_with(ticket_task_history_map)

    @pytest.mark.asyncio
    async def digi_reboot_report_process_failed_to_get_digi_recovery_logs_test(self):
        digi_recovery_logs_response = {"body": "Failed", "status": 400}

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        email_repository = Mock()

        digi_repository = Mock()
        digi_repository.get_digi_recovery_logs = CoroutineMock(return_value=digi_recovery_logs_response)

        digi_reboot_report = DiGiRebootReport(
            event_bus, scheduler, logger, config, bruin_repository, digi_repository, email_repository
        )

        ticket_id_list = ["123", "321"]
        ticket_task_history_map = {
            "123": {"ClientName": "Le Duff Management ", "Ticket Entered Date": "202008242225"},
            "321": {"ClientName": "Test", "Ticket Entered Date": "202008242225"},
        }
        digi_reboot_report._get_all_ticket_ids_from_digi_recovery_logs = Mock(return_value=ticket_id_list)
        digi_reboot_report._get_ticket_task_histories = CoroutineMock(return_value=ticket_task_history_map)
        digi_reboot_report._merge_recovery_logs = CoroutineMock()
        digi_reboot_report._generate_and_email_csv_file = CoroutineMock()

        await digi_reboot_report._digi_reboot_report_process()

        digi_reboot_report._get_all_ticket_ids_from_digi_recovery_logs.assert_not_called()
        digi_reboot_report._get_ticket_task_histories.assert_not_called()
        digi_reboot_report._merge_recovery_logs.assert_not_called()
        digi_reboot_report._generate_and_email_csv_file.assert_not_awaited()

    def get_all_ticket_ids_from_digi_recovery_logs_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        digi_repository = Mock()
        email_repository = Mock()

        expected_digi_ticket_id_list = [123, 321]
        digi_reboot_report = DiGiRebootReport(
            event_bus, scheduler, logger, config, bruin_repository, digi_repository, email_repository
        )
        digi_reboot_report._digi_recovery_logs = [{"TicketID": "123"}, {"TicketID": "123"}, {"TicketID": "321"}]

        digi_ticket_id_list = digi_reboot_report._get_all_ticket_ids_from_digi_recovery_logs()

        assert digi_ticket_id_list == expected_digi_ticket_id_list

    @pytest.mark.asyncio
    async def _get_ticket_task_histories_test(self):
        ticket_id_list = [123, 321, 589, 684]
        task_history_response_1 = {
            "body": [
                {
                    "ClientName": "Le Duff Management ",
                    "Ticket Entered Date": "202008242225",
                    "EnteredDate": "2020-08-24T22:25:09.953-04:00",
                    "CallTicketID": 123,
                    "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                    "DetailID": None,
                    "Product": None,
                    "Asset": None,
                    "Address1": "1320 W Campbell Rd",
                    "Address2": None,
                    "City": "Richardson",
                    "State": "TX",
                    "Zip": "75080-2814",
                    "Site Name": "01106 Coit Campbell",
                    "NoteType": "ADN",
                    "Notes": None,
                    "Note Entered Date": "202008242236",
                    "EnteredDate_N": "2020-08-24T22:36:21.343-04:00",
                    "Note Entered By": "Intelygenz Ai",
                    "Task Assigned To": None,
                    "Task": None,
                    "Task Result": None,
                    "SLA": None,
                    "Ticket Status": "Resolved",
                },
            ],
            "status": 200,
        }
        task_history_response_2 = {"body": "Failed", "status": 400}
        task_history_response_3 = {
            "body": [
                {
                    "ClientName": "Le Duff Management ",
                    "Ticket Entered Date": "202008242225",
                    "EnteredDate": "2020-08-24T22:25:09.953-04:00",
                    "CallTicketID": 589,
                    "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                    "DetailID": None,
                    "Product": None,
                    "Asset": None,
                    "Address1": "1320 W Campbell Rd",
                    "Address2": None,
                    "City": "Richardson",
                    "State": "TX",
                    "Zip": "75080-2814",
                    "Site Name": "01106 Coit Campbell",
                    "NoteType": "ADN",
                    "Notes": None,
                    "Note Entered Date": "202008242236",
                    "EnteredDate_N": "2020-08-24T22:36:21.343-04:00",
                    "Note Entered By": "Intelygenz Ai",
                    "Task Assigned To": None,
                    "Task": None,
                    "Task Result": None,
                    "SLA": None,
                    "Ticket Status": "Resolved",
                },
            ],
            "status": 200,
        }
        task_history_response_4 = {
            "body": [
                {
                    "ClientName": "Le Duff Management ",
                    "Ticket Entered Date": "202008242225",
                    "EnteredDate": "2020-08-24T22:25:09.953-04:00",
                    "CallTicketID": 684,
                    "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                    "DetailID": None,
                    "Product": None,
                    "Asset": None,
                    "Address1": "1320 W Campbell Rd",
                    "Address2": None,
                    "City": "Richardson",
                    "State": "TX",
                    "Zip": "75080-2814",
                    "Site Name": "01106 Coit Campbell",
                    "NoteType": "ADN",
                    "Notes": None,
                    "Note Entered Date": "202008242236",
                    "EnteredDate_N": "2020-08-24T22:36:21.343-04:00",
                    "Note Entered By": "Intelygenz Ai",
                    "Task Assigned To": None,
                    "Task": None,
                    "Task Result": None,
                    "SLA": None,
                    "Ticket Status": "Resolved",
                },
            ],
            "status": 200,
        }
        datetime_now = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=datetime_now)
        parsed_ticket_history = [
            {"reboot_attempted": True, "reboot_time": datetime_now - timedelta(days=2)},
            {"reboot_attempted": True, "reboot_time": datetime_now - timedelta(days=1)},
            {"reboot_attempted": False, "reboot_time": datetime_now - timedelta(days=1)},
        ]
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig

        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = CoroutineMock(
            side_effect=[
                task_history_response_1,
                task_history_response_2,
                task_history_response_3,
                task_history_response_4,
            ]
        )
        digi_repository = Mock()
        email_repository = Mock()

        digi_reboot_report = DiGiRebootReport(
            event_bus, scheduler, logger, config, bruin_repository, digi_repository, email_repository
        )
        digi_reboot_report._parse_ticket_history = Mock(side_effect=parsed_ticket_history)

        with patch.object(digi_reboot_report_module, "datetime", new=datetime_mock):
            ticket_map = await digi_reboot_report._get_ticket_task_histories(ticket_id_list)

        assert ticket_map == {ticket_id_list[2]: parsed_ticket_history[1]}
        bruin_repository.get_ticket_task_history.assert_has_awaits(
            [call(ticket_id_list[0]), call(ticket_id_list[1]), call(ticket_id_list[2]), call(ticket_id_list[3])]
        )
        digi_reboot_report._parse_ticket_history.assert_has_calls(
            [
                call(task_history_response_1["body"]),
                call(task_history_response_3["body"]),
                call(task_history_response_4["body"]),
            ]
        )

    def parse_ticket_history_failed_digi_link_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        digi_repository = Mock()
        email_repository = Mock()

        ticket_task_history = [
            {
                "ClientName": "Sterling Jewelers, Inc.",
                "Ticket Entered Date": "202104070138",
                "EnteredDate": "2021-04-07T01:38:24.553-04:00",
                "CallTicketID": 5329135,
                "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                "DetailID": None,
                "Product": None,
                "Asset": None,
                "Address1": "200 Baychester Ave Ste 124B",
                "Address2": None,
                "City": "Bronx",
                "State": "NY",
                "Zip": "10475-4581",
                "Site Name": "ZALES JEWELERS-ZL01789",
                "NoteType": "MTK",
                "Notes": "MetTel's IPA -- Service Outage Trouble",
                "Note Entered Date": "202104070138",
                "EnteredDate_N": "2021-04-07T01:38:24.587-04:00",
                "Note Entered By": "Intelygenz Ai",
                "Task Assigned To": None,
                "Task": None,
                "Task Result": None,
                "SLA": None,
                "Ticket Status": "Closed",
            },
            {
                "ClientName": "Sterling Jewelers, Inc.",
                "Ticket Entered Date": "202104070138",
                "EnteredDate": "2021-04-07T01:38:24.553-04:00",
                "CallTicketID": 5329135,
                "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                "DetailID": None,
                "Product": None,
                "Asset": None,
                "Address1": "200 Baychester Ave Ste 124B",
                "Address2": None,
                "City": "Bronx",
                "State": "NY",
                "Zip": "10475-4581",
                "Site Name": "ZALES JEWELERS-ZL01789",
                "Notes": "MetTel's IPA -- Service Outage Trouble",
                "Note Entered Date": "202104070138",
                "EnteredDate_N": "2021-04-07T01:38:24.587-04:00",
                "Note Entered By": "Intelygenz Ai",
                "Task Assigned To": None,
                "Task": None,
                "Task Result": None,
                "SLA": None,
                "Ticket Status": "Closed",
            },
            {
                "ClientName": "Sterling Jewelers, Inc.",
                "Ticket Entered Date": "202104070138",
                "EnteredDate": "2021-04-07T01:38:24.553-04:00",
                "CallTicketID": 5329135,
                "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                "DetailID": None,
                "Product": None,
                "Asset": None,
                "Address1": "200 Baychester Ave Ste 124B",
                "Address2": None,
                "City": "Bronx",
                "State": "NY",
                "Zip": "10475-4581",
                "Site Name": "ZALES JEWELERS-ZL01789",
                "NoteType": "MTK",
                "Notes": None,
                "Note Entered Date": "202104070138",
                "EnteredDate_N": "2021-04-07T01:38:24.587-04:00",
                "Note Entered By": "Intelygenz Ai",
                "Task Assigned To": None,
                "Task": None,
                "Task Result": None,
                "SLA": None,
                "Ticket Status": "Closed",
            },
            {
                "ClientName": "Sterling Jewelers, Inc.",
                "Ticket Entered Date": "202104070138",
                "EnteredDate": "2021-04-07T01:38:24.553-04:00",
                "CallTicketID": 5329135,
                "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                "DetailID": 5878950,
                "Product": "SD-WAN",
                "Asset": "VC05200041384",
                "Address1": "200 Baychester Ave Ste 124B",
                "Address2": None,
                "City": "Bronx",
                "State": "NY",
                "Zip": "10475-4581",
                "Site Name": "ZALES JEWELERS-ZL01789",
                "NoteType": "ADN",
                "Notes": "#*MetTel's IPA*#\n"
                "Offline DiGi interface identified for serial: VC05200041384\n"
                "Interface: GE2\n"
                "Automatic reboot attempt started.\n"
                "TimeStamp: 2021-04-07 01:38:34.792713-04:00",
                "Note Entered Date": "202104070138",
                "EnteredDate_N": "2021-04-07T01:38:34.913-04:00",
                "Note Entered By": "Intelygenz Ai",
                "Task Assigned To": None,
                "Task": None,
                "Task Result": None,
                "SLA": 1,
                "Ticket Status": "Closed",
            },
            {
                "ClientName": "Sterling Jewelers, Inc.",
                "Ticket Entered Date": "202104070138",
                "EnteredDate": "2021-04-07T01:38:24.553-04:00",
                "CallTicketID": 5329135,
                "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                "DetailID": 5878950,
                "Product": "SD-WAN",
                "Asset": "VC05200041384",
                "Address1": "200 Baychester Ave Ste 124B",
                "Address2": None,
                "City": "Bronx",
                "State": "NY",
                "Zip": "10475-4581",
                "Site Name": "ZALES JEWELERS-ZL01789",
                "NoteType": "ADN",
                "Notes": "#*MetTel's IPA*#\n"
                "Triage (VeloCloud)\n"
                "Orchestrator Instance: metvco02.mettel.net\n"
                "Edge Name: ZL01789VC\n"
                "Links:  [Edge|https://metvco02.mettel.net/#!/operator/customer/2/monitor/edge/1191/]  "
                "-  [QoE|https://metvco02.mettel.net/#!/operator/customer/2/monitor/edge/1191/qoe/]  "
                "-  [Transport|https://metvco02.mettel.net/#!/operator/customer/2/monitor/edge/1191/links/]  "
                "-  [Events|https://metvco02.mettel.net/#!/operator/customer/2/monitor/events/] \n"
                "Edge Status: CONNECTED\nSerial: VC05200041384\nInterface GE1\n"
                "Interface GE1 Label: 74.89.102.25\nInterface GE1 Status: STABLE\nInterface GE2\n"
                "Interface GE2 Label: 10.1.4.148\nInterface GE2 Status: DISCONNECTED\nLast Edge Online: None\n"
                "Last Edge Offline: None\nLast GE1 Interface Online: None\nLast GE1 Interface Offline: None\n"
                "Last GE2 Interface Online: 2021-04-05 02:47:37-04:00\n"
                "Last GE2 Interface Offline: 2021-04-07 01:33:57-04:00",
                "Note Entered Date": "202104070138",
                "EnteredDate_N": "2021-04-07T01:38:31.837-04:00",
                "Note Entered By": "Intelygenz Ai",
                "Task Assigned To": None,
                "Task": None,
                "Task Result": None,
                "SLA": 1,
                "Ticket Status": "Closed",
            },
            {
                "ClientName": "Sterling Jewelers, Inc.",
                "Ticket Entered Date": "202104070138",
                "EnteredDate": "2021-04-07T01:38:24.553-04:00",
                "CallTicketID": 5329135,
                "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                "DetailID": None,
                "Product": None,
                "Asset": None,
                "Address1": "200 Baychester Ave Ste 124B",
                "Address2": None,
                "City": "Bronx",
                "State": "NY",
                "Zip": "10475-4581",
                "Site Name": "ZALES JEWELERS-ZL01789",
                "NoteType": "ADN",
                "Notes": "#*MetTel's IPA*#\nDiGi reboot failed\nMoving task to: Wireless Repair Intervention Needed\n"
                "TimeStamp: 2021-04-07 03:38:27.430480-04:00",
                "Note Entered Date": "202104070338",
                "EnteredDate_N": "2021-04-07T03:38:27.43-04:00",
                "Note Entered By": "Intelygenz Ai",
                "Task Assigned To": None,
                "Task": None,
                "Task Result": None,
                "SLA": None,
                "Ticket Status": "Closed",
            },
        ]
        digi_reboot_report = DiGiRebootReport(
            event_bus, scheduler, logger, config, bruin_repository, digi_repository, email_repository
        )
        ticket_info = digi_reboot_report._parse_ticket_history(ticket_task_history)

        assert ticket_info == {
            "outage_type": "Link",
            "reboot_attempted": True,
            "reboot_time": datetime(2021, 4, 7, 1, 38, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
            "process_attempted": False,
            "process_successful": False,
            "process_start": None,
            "process_end": None,
            "process_length": None,
            "reboot_method": None,
            "autoresolved": False,
            "autoresolve_time": None,
            "autoresolve_correlation": False,
            "autoresolve_diff": None,
            "forwarded": True,
        }

    def parse_ticket_history_failed_edge_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        digi_repository = Mock()
        email_repository = Mock()

        ticket_task_history = [
            {
                "ClientName": "Sterling Jewelers, Inc.",
                "Ticket Entered Date": "202104070138",
                "EnteredDate": "2021-04-07T01:38:24.553-04:00",
                "CallTicketID": 5329135,
                "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                "DetailID": 5878950,
                "Product": "SD-WAN",
                "Asset": "VC05200041384",
                "Address1": "200 Baychester Ave Ste 124B",
                "Address2": None,
                "City": "Bronx",
                "State": "NY",
                "Zip": "10475-4581",
                "Site Name": "ZALES JEWELERS-ZL01789",
                "NoteType": "ADN",
                "Notes": "#*MetTel's IPA*#\n"
                "Triage (VeloCloud)\n"
                "Orchestrator Instance: metvco02.mettel.net\n"
                "Edge Name: ZL01789VC\n"
                "Links:  [Edge|https://metvco02.mettel.net/#!/operator/customer/2/monitor/edge/1191/]  "
                "-  [QoE|https://metvco02.mettel.net/#!/operator/customer/2/monitor/edge/1191/qoe/]  "
                "-  [Transport|https://metvco02.mettel.net/#!/operator/customer/2/monitor/edge/1191/links/]  "
                "-  [Events|https://metvco02.mettel.net/#!/operator/customer/2/monitor/events/] \n"
                "Edge Status: DISCONNECTED\nSerial: VC05200041384\nInterface GE1\n"
                "Interface GE1 Label: 74.89.102.25\nInterface GE1 Status: STABLE\nInterface GE2\n"
                "Interface GE2 Label: 10.1.4.148\nInterface GE2 Status: DISCONNECTED\nLast Edge Online: None\n"
                "Last Edge Offline: None\nLast GE1 Interface Online: None\nLast GE1 Interface Offline: None\n"
                "Last GE2 Interface Online: 2021-04-05 02:47:37-04:00\n"
                "Last GE2 Interface Offline: 2021-04-07 01:33:57-04:00",
                "Note Entered Date": "202104070138",
                "EnteredDate_N": "2021-04-07T01:38:31.837-0400",
                "Note Entered By": "Intelygenz Ai",
                "Task Assigned To": None,
                "Task": None,
                "Task Result": None,
                "SLA": 1,
                "Ticket Status": "Closed",
            }
        ]
        digi_reboot_report = DiGiRebootReport(
            event_bus, scheduler, logger, config, bruin_repository, digi_repository, email_repository
        )
        ticket_info = digi_reboot_report._parse_ticket_history(ticket_task_history)

        assert ticket_info == {
            "outage_type": "Edge",
            "reboot_attempted": False,
            "reboot_time": None,
            "process_attempted": False,
            "process_successful": False,
            "process_start": None,
            "process_end": None,
            "process_length": None,
            "reboot_method": None,
            "autoresolved": False,
            "autoresolve_time": None,
            "autoresolve_correlation": False,
            "autoresolve_diff": None,
            "forwarded": False,
        }

    def parse_ticket_history_no_edge_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        digi_repository = Mock()
        email_repository = Mock()

        ticket_task_history = [
            {
                "ClientName": "Sterling Jewelers, Inc.",
                "Ticket Entered Date": "202104070138",
                "EnteredDate": "2021-04-07T01:38:24.553-04:00",
                "CallTicketID": 5329135,
                "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                "DetailID": 5878950,
                "Product": "SD-WAN",
                "Asset": "VC05200041384",
                "Address1": "200 Baychester Ave Ste 124B",
                "Address2": None,
                "City": "Bronx",
                "State": "NY",
                "Zip": "10475-4581",
                "Site Name": "ZALES JEWELERS-ZL01789",
                "NoteType": "ADN",
                "Notes": "#*MetTel's IPA*#\n"
                "Triage (VeloCloud)\n"
                "Orchestrator Instance: metvco02.mettel.net\n"
                "Edge Name: ZL01789VC\n"
                "Links:  [Edge|https://metvco02.mettel.net/#!/operator/customer/2/monitor/edge/1191/]  "
                "-  [QoE|https://metvco02.mettel.net/#!/operator/customer/2/monitor/edge/1191/qoe/]  "
                "-  [Transport|https://metvco02.mettel.net/#!/operator/customer/2/monitor/edge/1191/links/]  "
                "-  [Events|https://metvco02.mettel.net/#!/operator/customer/2/monitor/events/] \n"
                "Serial: VC05200041384\nInterface GE1\n"
                "Interface GE1 Label: 74.89.102.25\nInterface GE1 Status: STABLE\nInterface GE2\n"
                "Interface GE2 Label: 10.1.4.148\nInterface GE2 Status: DISCONNECTED\nLast Edge Online: None\n"
                "Last Edge Offline: None\nLast GE1 Interface Online: None\nLast GE1 Interface Offline: None\n"
                "Last GE2 Interface Online: 2021-04-05 02:47:37-04:00\n"
                "Last GE2 Interface Offline: 2021-04-07 01:33:57-04:00",
                "Note Entered Date": "202104070138",
                "EnteredDate_N": "2021-04-07T01:38:31-04:00",
                "Note Entered By": "Intelygenz Ai",
                "Task Assigned To": None,
                "Task": None,
                "Task Result": None,
                "SLA": 1,
                "Ticket Status": "Closed",
            }
        ]
        digi_reboot_report = DiGiRebootReport(
            event_bus, scheduler, logger, config, bruin_repository, digi_repository, email_repository
        )
        ticket_info = digi_reboot_report._parse_ticket_history(ticket_task_history)

        assert ticket_info == {
            "outage_type": "Unclassified",
            "reboot_attempted": False,
            "reboot_time": None,
            "process_attempted": False,
            "process_successful": False,
            "process_start": None,
            "process_end": None,
            "process_length": None,
            "reboot_method": None,
            "autoresolved": False,
            "autoresolve_time": None,
            "autoresolve_correlation": False,
            "autoresolve_diff": None,
            "forwarded": False,
        }

    def parse_ticket_history_auto_resolved_edge_test(self):
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        digi_repository = Mock()
        email_repository = Mock()

        ticket_task_history = [
            {
                "ClientName": "Sterling Jewelers, Inc.",
                "Ticket Entered Date": "202104131442",
                "EnteredDate": "2021-04-13T14:42:40.19-04:00",
                "CallTicketID": 5348913,
                "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                "DetailID": 5899701,
                "Product": "SD-WAN",
                "Asset": "VC05200035390",
                "Address1": "3450 28th St SE",
                "Address2": None,
                "City": "Grand Rapids",
                "State": "MI",
                "Zip": "49512-1602",
                "Site Name": "JARED THE GALLERIA OF JEWELRY-JA02489",
                "NoteType": "ADN",
                "Notes": "#*MetTel's IPA*#\nOffline DiGi interface identified for serial: VC05200035390\n"
                "Interface: GE2\nAutomatic reboot attempt started.\nTimeStamp: 2021-04-13 14:42:46.545269-04:00",
                "Note Entered Date": "202104131442",
                "EnteredDate_N": "2021-04-13T14:42:46.36-04:00",
                "Note Entered By": "Intelygenz Ai",
                "Task Assigned To": None,
                "Task": None,
                "Task Result": None,
                "SLA": 1,
                "Ticket Status": "Resolved",
            },
            {
                "ClientName": "Sterling Jewelers, Inc.",
                "Ticket Entered Date": "202104131442",
                "EnteredDate": "2021-04-13T14:42:40.19-04:00",
                "CallTicketID": 5348913,
                "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                "DetailID": 5899701,
                "Product": "SD-WAN",
                "Asset": "VC05200035390",
                "Address1": "3450 28th St SE",
                "Address2": None,
                "City": "Grand Rapids",
                "State": "MI",
                "Zip": "49512-1602",
                "Site Name": "JARED THE GALLERIA OF JEWELRY-JA02489",
                "NoteType": "ADN",
                "Notes": "#*MetTel's IPA*#\n"
                "Triage (VeloCloud)\nOrchestrator Instance: metvco02.mettel.net\nEdge Name: JA02489VC\n"
                "Links:  [Edge|https://metvco02.mettel.net/#!/operator/customer/2/monitor/edge/174/]  - "
                " [QoE|https://metvco02.mettel.net/#!/operator/customer/2/monitor/edge/174/qoe/]  -  "
                "[Transport|https://metvco02.mettel.net/#!/operator/customer/2/monitor/edge/174/links/]  - "
                " [Events|https://metvco02.mettel.net/#!/operator/customer/2/monitor/events/] \n"
                "Edge Status: CONNECTED\nSerial: VC05200035390\nInterface GE1\nInterface GE1 Label:"
                " Comcast Cable\nInterface GE1 Status: STABLE\nInterface GE2\nInterface GE2 Label: 10.1.1.158\n"
                "Interface GE2 Status: DISCONNECTED\nLast Edge Online: None\nLast Edge Offline: None\n"
                "Last GE1 Interface Online: 2021-04-07 10:59:16-04:00\n"
                "Last GE1 Interface Offline: 2021-04-07 10:53:11-04:00\n"
                "Last GE2 Interface Online: 2021-04-13 14:39:00-04:00\n"
                "Last GE2 Interface Offline: 2021-04-13 14:33:45-04:00",
                "Note Entered Date": "202104131442",
                "EnteredDate_N": "2021-04-13T14:42:43.61-04:00",
                "Note Entered By": "Intelygenz Ai",
                "Task Assigned To": None,
                "Task": None,
                "Task Result": None,
                "SLA": 1,
                "Ticket Status": "Resolved",
            },
            {
                "ClientName": "Sterling Jewelers, Inc.",
                "Ticket Entered Date": "202104131442",
                "EnteredDate": "2021-04-13T14:42:40.19-04:00",
                "CallTicketID": 5348913,
                "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                "DetailID": 5899701,
                "Product": "SD-WAN",
                "Asset": "VC05200035390",
                "Address1": "3450 28th St SE",
                "Address2": None,
                "City": "Grand Rapids",
                "State": "MI",
                "Zip": "49512-1602",
                "Site Name": "JARED THE GALLERIA OF JEWELRY-JA02489",
                "NoteType": "ADN",
                "Notes": "#*MetTel's IPA*#\nAuto-resolving detail for serial: VC05200035390\n"
                "TimeStamp: 2021-04-13 14:55:43.077211-04:00",
                "Note Entered Date": "202104131455",
                "EnteredDate_N": "2021-04-13T14:55:42.9-04:00",
                "Note Entered By": "Intelygenz Ai",
                "Task Assigned To": None,
                "Task": None,
                "Task Result": None,
                "SLA": 1,
                "Ticket Status": "Resolved",
            },
        ]
        digi_reboot_report = DiGiRebootReport(
            event_bus, scheduler, logger, config, bruin_repository, digi_repository, email_repository
        )
        ticket_info = digi_reboot_report._parse_ticket_history(ticket_task_history)

        assert ticket_info == {
            "outage_type": "Link",
            "reboot_attempted": True,
            "reboot_time": datetime(2021, 4, 13, 14, 42, 46, 360000, tzinfo=timezone(timedelta(-1, 72000))),
            "process_attempted": False,
            "process_successful": False,
            "process_start": None,
            "process_end": None,
            "process_length": None,
            "reboot_method": None,
            "autoresolved": False,
            "autoresolve_time": datetime(2021, 4, 13, 14, 55, 42, 900000, tzinfo=timezone(timedelta(-1, 72000))),
            "autoresolve_correlation": False,
            "autoresolve_diff": None,
            "forwarded": False,
        }

    def merge_recovery_logs_test(self):
        digi_recovery_logs = [
            {
                "Id": 142,
                "igzID": "42",
                "RequestID": "959b1e34-2b10-4e04-967e-7ac268d2cb1b",
                "Method": "API Start",
                "System": "NYD",
                "VeloSerial": "VC00000613",
                "TicketID": "3569284",
                "DeviceSN": "NYD",
                "Notes": "API Called 04/15/2021 11:08:26",
                "TimestampSTART": "2021-04-14T16:08:26Z",
            },
            {
                "Id": 142,
                "igzID": "42",
                "RequestID": "959b1e34-2b10-4e04-967e-7ac268d2cb1b",
                "Method": "API Start",
                "System": "NYD",
                "VeloSerial": "VC00000613",
                "TicketID": "123",
                "DeviceSN": "NYD",
                "Success": True,
                "Notes": "API Called 04/15/2021 11:08:26",
                "TimestampSTART": "2021-04-15T16:08:26Z",
                "TimestampEND": "2021-04-15T20:08:26Z",
            },
            {
                "Id": 142,
                "igzID": "42",
                "RequestID": "959b1e34-2b10-4e04-967e-7ac268d2cb1b",
                "Method": "API Start",
                "System": "NYD",
                "VeloSerial": "VC00000613",
                "TicketID": "721",
                "DeviceSN": "NYD",
                "Success": False,
                "Notes": "API Called 04/15/2021 11:08:26",
                "TimestampSTART": "2021-04-15T16:08:26Z",
                "TimestampEND": "2021-04-15T20:08:26Z",
            },
            {
                "Id": 142,
                "igzID": "42",
                "RequestID": "959b1e34-2b10-4e04-967e-7ac268d2cb1b",
                "Method": "API Start",
                "System": "NYD",
                "VeloSerial": "VC00000613",
                "TicketID": "8",
                "DeviceSN": "NYD",
                "Success": True,
                "Notes": "API Called 04/15/2021 11:08:26",
                "TimestampSTART": "2021-04-15T16:08:26Z",
                "TimestampEND": "2021-04-15T21:08:26Z",
            },
            {
                "Id": 142,
                "igzID": "42",
                "RequestID": "959b1e34-2b10-4e04-967e-7ac268d2cb1b",
                "Method": "API Start",
                "System": "NYD",
                "VeloSerial": "VC00000613",
                "TicketID": "86",
                "DeviceSN": "NYD",
                "Success": True,
                "Notes": "API Called 04/15/2021 11:08:26",
                "TimestampSTART": "2021-04-15T16:08:26Z",
            },
        ]
        intial_ticket_map = {
            123: {
                "outage_type": "Link",
                "reboot_attempted": True,
                "reboot_time": datetime(2021, 4, 15, 1, 38, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "process_attempted": False,
                "process_successful": False,
                "process_start": None,
                "process_end": None,
                "process_length": None,
                "reboot_method": None,
                "autoresolved": False,
                "autoresolve_time": datetime(2021, 4, 15, 16, 10, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "autoresolve_correlation": False,
                "autoresolve_diff": None,
                "forwarded": True,
            },
            721: {
                "outage_type": "Link",
                "reboot_attempted": True,
                "reboot_time": datetime(2021, 4, 7, 1, 38, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "process_attempted": False,
                "process_successful": False,
                "process_start": None,
                "process_end": None,
                "process_length": None,
                "reboot_method": None,
                "autoresolved": False,
                "autoresolve_time": None,
                "autoresolve_correlation": False,
                "autoresolve_diff": None,
                "forwarded": True,
            },
            8: {
                "outage_type": "Link",
                "reboot_attempted": True,
                "reboot_time": datetime(2021, 4, 15, 1, 38, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "process_attempted": False,
                "process_successful": False,
                "process_start": None,
                "process_end": None,
                "process_length": None,
                "reboot_method": None,
                "autoresolved": False,
                "autoresolve_time": datetime(2021, 4, 15, 16, 48, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "autoresolve_correlation": False,
                "autoresolve_diff": None,
                "forwarded": True,
            },
            86: {
                "outage_type": "Link",
                "reboot_attempted": True,
                "reboot_time": datetime(2021, 4, 15, 1, 38, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "process_attempted": False,
                "process_successful": False,
                "process_start": None,
                "process_end": None,
                "process_length": None,
                "reboot_method": None,
                "autoresolved": False,
                "autoresolve_time": datetime(2021, 4, 15, 16, 48, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "autoresolve_correlation": False,
                "autoresolve_diff": None,
                "forwarded": True,
            },
        }
        expected_ticket_map = {
            123: {
                "outage_type": "Link",
                "reboot_attempted": True,
                "reboot_time": datetime(2021, 4, 15, 1, 38, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "process_attempted": True,
                "process_successful": True,
                "process_start": datetime(2021, 4, 15, 16, 8, 26),
                "process_end": datetime(2021, 4, 15, 20, 8, 26),
                "process_length": 240.0,
                "reboot_method": "API Start",
                "autoresolved": True,
                "autoresolve_time": datetime(2021, 4, 15, 16, 10, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "autoresolve_correlation": True,
                "autoresolve_diff": 2.14855,
                "forwarded": True,
            },
            721: {
                "outage_type": "Link",
                "reboot_attempted": True,
                "reboot_time": datetime(2021, 4, 7, 1, 38, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "process_attempted": True,
                "process_successful": False,
                "process_start": datetime(2021, 4, 15, 16, 8, 26),
                "process_end": datetime(2021, 4, 15, 20, 8, 26),
                "process_length": 240.0,
                "reboot_method": "API Start",
                "autoresolved": False,
                "autoresolve_time": None,
                "autoresolve_correlation": False,
                "autoresolve_diff": None,
                "forwarded": True,
            },
            8: {
                "outage_type": "Link",
                "reboot_attempted": True,
                "reboot_time": datetime(2021, 4, 15, 1, 38, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "process_attempted": True,
                "process_successful": True,
                "process_start": datetime(2021, 4, 15, 16, 8, 26),
                "process_end": datetime(2021, 4, 15, 21, 8, 26),
                "process_length": 300.0,
                "reboot_method": "API Start",
                "autoresolved": False,
                "autoresolve_time": datetime(2021, 4, 15, 16, 48, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "autoresolve_correlation": False,
                "autoresolve_diff": -19.85145,
                "forwarded": True,
            },
            86: {
                "outage_type": "Link",
                "reboot_attempted": True,
                "reboot_time": datetime(2021, 4, 15, 1, 38, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "process_attempted": True,
                "process_successful": True,
                "process_start": datetime(2021, 4, 15, 16, 8, 26),
                "process_end": None,
                "process_length": None,
                "reboot_method": "API Start",
                "autoresolved": False,
                "autoresolve_time": datetime(2021, 4, 15, 16, 48, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "autoresolve_correlation": False,
                "autoresolve_diff": None,
                "forwarded": True,
            },
        }
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        digi_repository = Mock()
        email_repository = Mock()

        digi_reboot_report = DiGiRebootReport(
            event_bus, scheduler, logger, config, bruin_repository, digi_repository, email_repository
        )
        digi_reboot_report._digi_recovery_logs = digi_recovery_logs
        digi_reboot_report._merge_recovery_logs(intial_ticket_map)
        assert intial_ticket_map == expected_ticket_map

    @pytest.mark.asyncio
    async def generate_and_email_csv_file_test(self):
        ticket_map = {
            123: {
                "outage_type": "Edge",
                "reboot_attempted": True,
                "reboot_time": datetime(2021, 4, 15, 1, 38, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "process_attempted": True,
                "process_successful": True,
                "process_start": datetime(2021, 4, 15, 16, 8, 26),
                "process_end": datetime(2021, 4, 15, 20, 8, 26),
                "process_length": 240.0,
                "reboot_method": "OEMPortal",
                "autoresolved": True,
                "autoresolve_time": datetime(2021, 4, 15, 16, 10, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "autoresolve_correlation": True,
                "autoresolve_diff": -2.14855,
                "forwarded": True,
            },
            721: {
                "outage_type": "Edge",
                "reboot_attempted": True,
                "reboot_time": datetime(2021, 4, 15, 1, 38, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "process_attempted": True,
                "process_successful": False,
                "process_start": datetime(2021, 4, 15, 16, 8, 26),
                "process_end": datetime(2021, 4, 15, 20, 8, 26),
                "process_length": 240.0,
                "reboot_method": "SSH",
                "autoresolved": False,
                "autoresolve_time": None,
                "autoresolve_correlation": True,
                "autoresolve_diff": 2.14855,
                "forwarded": True,
            },
            8: {
                "outage_type": "Link",
                "reboot_attempted": True,
                "reboot_time": datetime(2021, 4, 15, 1, 38, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "process_attempted": True,
                "process_successful": True,
                "process_start": datetime(2021, 4, 15, 16, 8, 26),
                "process_end": datetime(2021, 4, 15, 21, 8, 26),
                "process_length": 300.0,
                "reboot_method": "SMS",
                "autoresolved": False,
                "autoresolve_time": datetime(2021, 4, 15, 16, 48, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "autoresolve_correlation": True,
                "autoresolve_diff": 19.85145,
                "forwarded": True,
            },
            86: {
                "outage_type": "Link",
                "reboot_attempted": True,
                "reboot_time": datetime(2021, 4, 15, 1, 38, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "process_attempted": True,
                "process_successful": True,
                "process_start": datetime(2021, 4, 15, 16, 8, 26),
                "process_end": None,
                "process_length": None,
                "reboot_method": "SMS",
                "autoresolved": False,
                "autoresolve_time": datetime(2021, 4, 15, 16, 48, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "autoresolve_correlation": True,
                "autoresolve_diff": 24.0,
                "forwarded": True,
            },
            834: {
                "outage_type": "Unclassified",
                "reboot_attempted": True,
                "reboot_time": datetime(2021, 4, 15, 1, 38, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "process_attempted": False,
                "process_successful": True,
                "process_start": datetime(2021, 4, 15, 16, 8, 26),
                "process_end": datetime(2021, 4, 15, 21, 8, 26),
                "process_length": None,
                "reboot_method": None,
                "autoresolved": False,
                "autoresolve_time": datetime(2021, 4, 15, 16, 48, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "autoresolve_correlation": False,
                "autoresolve_diff": -19.85145,
                "forwarded": True,
            },
            821: {
                "outage_type": "Unclassified",
                "reboot_attempted": True,
                "reboot_time": datetime(2021, 4, 15, 1, 38, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "process_attempted": True,
                "process_successful": True,
                "process_start": datetime(2021, 4, 15, 16, 8, 26),
                "process_end": None,
                "process_length": None,
                "reboot_method": "SSH",
                "autoresolved": False,
                "autoresolve_time": datetime(2021, 4, 15, 16, 48, 34, 913000, tzinfo=timezone(timedelta(-1, 72000))),
                "autoresolve_correlation": True,
                "autoresolve_diff": 45.0,
                "forwarded": False,
            },
        }
        day = ticket_map[123]["reboot_time"].strftime("%m/%d")
        expected_breakdown = [
            day,
            6,
            2,
            2,
            2,
            6,
            5,
            5,
            270.0,
            0,
            0,
            1,
            1,
            2,
            1,
            2,
            2,
            0,
            0,
            5,
            1,
            1,
            1,
            1,
            2,
            2,
            1,
            5,
            2,
            2,
            1,
        ]
        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        digi_repository = Mock()
        email_repository = Mock()
        email_repository.send_email = CoroutineMock()

        digi_reboot_report = DiGiRebootReport(
            event_bus, scheduler, logger, config, bruin_repository, digi_repository, email_repository
        )
        csv = Mock()
        csv.writer = Mock(writerow=Mock())
        io = Mock()
        io.StringIO = Mock()
        with patch.object(digi_reboot_report_module, "csv", new=csv):
            with patch.object(digi_reboot_report_module, "io", new=io):
                with patch.object(digi_reboot_report_module, "open", create=False):
                    await digi_reboot_report._generate_and_email_csv_file(ticket_map)
            assert csv.writer.mock_calls[2][1][0] == expected_breakdown
            email_repository.send_email.assert_awaited()
