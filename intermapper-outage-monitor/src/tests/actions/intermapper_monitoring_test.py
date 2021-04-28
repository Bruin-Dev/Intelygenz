import os
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch
from unittest.mock import call

import pytest
from application.actions.intermapper_monitoring import InterMapperMonitor
from asynctest import CoroutineMock
from shortuuid import uuid
from apscheduler.util import undefined
from apscheduler.jobstores.base import ConflictingIdError

from application.actions import intermapper_monitoring as intermapper_monitor_module

from config import testconfig


class TestInterMapperMonitor:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)

        assert intermapper_monitor._event_bus == event_bus
        assert intermapper_monitor._logger == logger
        assert intermapper_monitor._scheduler == scheduler
        assert intermapper_monitor._config == config
        assert intermapper_monitor._notifications_repository == notifications_repository
        assert intermapper_monitor._bruin_repository == bruin_repository

    @pytest.mark.asyncio
    async def start_intermapper_outage_monitoring_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock()

        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)

        await intermapper_monitor.start_intermapper_outage_monitoring()

        scheduler.add_job.assert_called_once_with(
            intermapper_monitor._intermapper_monitoring_process, 'interval',
            seconds=config.INTERMAPPER_CONFIG['monitoring_interval'],
            next_run_time=undefined,
            replace_existing=False,
            id='_intermapper_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_intermapper_outage_monitoring_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock()

        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            with patch.object(intermapper_monitor_module, 'timezone', new=Mock()):
                await intermapper_monitor.start_intermapper_outage_monitoring(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            intermapper_monitor._intermapper_monitoring_process, 'interval',
            seconds=config.INTERMAPPER_CONFIG['monitoring_interval'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_intermapper_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_intermapper_outage_monitoring_with_job_id_already_executing_test(self):
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)

        try:
            await intermapper_monitor.start_intermapper_outage_monitoring()
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                intermapper_monitor._intermapper_monitoring_process, 'interval',
                seconds=config.INTERMAPPER_CONFIG['monitoring_interval'],
                next_run_time=undefined,
                replace_existing=False,
                id='_intermapper_monitor_process',
            )

    @pytest.mark.asyncio
    async def intermapper_monitoring_process_test(self):
        asset_id = 123
        client_id = 83959
        intermapper_body = os.linesep.join([
            "Event: Alarm",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        msg_uid = 123
        intermapper_response = {
            'body': [{'message': 'msg', 'body': intermapper_body, 'msg_uid': msg_uid}],
            'status': 200
        }
        mark_email_as_read_response = {
            'body': 'Marked as read',
            'status': 200
        }
        circuit_id = 3214
        circuit_id_response = {
            "body": {
                      "clientID": 83959,
                      "subAccount": "string",
                      "wtn": circuit_id,
                      "inventoryID": 0,
                      "addressID": 0
            },
            "status": 200
        }
        ticket_id = 321
        outage_ticket_response = {
            'body': ticket_id,
            'status': 200
        }

        slack_message = (
            f'Outage ticket created through Intermapper emails for circuit_id {circuit_id}. Ticket '
            f'details at https://app.bruin.com/t/{ticket_id}.'
        )
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.get_unread_emails = CoroutineMock(return_value=intermapper_response)
        notifications_repository.mark_email_as_read = CoroutineMock(return_value=mark_email_as_read_response)
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_circuit_id = CoroutineMock(return_value=circuit_id_response)
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.append_intermapper_note = CoroutineMock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)

        await intermapper_monitor._intermapper_monitoring_process()

        notifications_repository.get_unread_emails.assert_awaited_once()
        notifications_repository.mark_email_as_read.assert_awaited_once_with(msg_uid)

        bruin_repository.get_circuit_id.assert_awaited_once_with(str(asset_id), str(client_id))
        bruin_repository.create_outage_ticket.assert_awaited_once_with(str(client_id), circuit_id)

        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)
        bruin_repository.append_intermapper_note.assert_awaited_once_with(ticket_id, intermapper_body)

    @pytest.mark.asyncio
    async def intermapper_monitoring_process_failed_unread_rpc_test(self):

        intermapper_response = {
            'body': 'Failed',
            'status': 400
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.get_unread_emails = CoroutineMock(return_value=intermapper_response)
        notifications_repository.mark_email_as_read = CoroutineMock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_circuit_id = CoroutineMock()
        bruin_repository.create_outage_ticket = CoroutineMock()
        bruin_repository.append_intermapper_note = CoroutineMock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)

        await intermapper_monitor._intermapper_monitoring_process()

        notifications_repository.get_unread_emails.assert_awaited_once()
        notifications_repository.mark_email_as_read.assert_not_awaited()

        bruin_repository.get_circuit_id.assert_not_awaited()
        bruin_repository.create_outage_ticket.assert_not_awaited()

        notifications_repository.send_slack_message.assert_not_awaited()
        bruin_repository.append_intermapper_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def intermapper_monitoring_process_failed_test(self):
        asset_id = 123
        client_id = 83959
        intermapper_failed_circuit_id_body = os.linesep.join([
            "Event: Alarm",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])
        asset_id_1 = 1234
        client_id_1 = 839590
        intermapper_failed_outage_body = os.linesep.join([
            "Event: Alarm",
            f"Name: OReilly-HotSpringsAR({asset_id_1})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id_1}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        intermapper_up_body = os.linesep.join([
            "Event: Up",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])
        intermapper_sd_wan_body = os.linesep.join([
            "Event: Alarm",
            f"Name: OReilly-HotSpringsAR(SD-WAN)-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])
        intermapper_no_client_id_body = os.linesep.join([
            "Event: Alarm",
            f"Name: OReilly-HotSpringsAR(541)-Site803",
            f"Document: O Reilly Auto Parts - South East Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        msg_uid_0 = 0
        msg_uid_1 = 1
        msg_uid_2 = 2
        msg_uid_3 = 3
        msg_uid_4 = 4
        msg_uid_5 = 5

        intermapper_response = {
            'body': [{'message': 'msg', 'body': 'skipped', 'msg_uid': -1},
                     {'message': 'msg', 'body': 'failed to mark as read', 'msg_uid': msg_uid_0},
                     {'message': 'msg', 'body': intermapper_up_body, 'msg_uid': msg_uid_1},
                     {'message': 'msg', 'body': intermapper_sd_wan_body, 'msg_uid': msg_uid_2},
                     {'message': 'msg', 'body': intermapper_no_client_id_body, 'msg_uid': msg_uid_3},
                     {'message': 'msg', 'body': intermapper_failed_circuit_id_body, 'msg_uid': msg_uid_4},
                     {'message': 'msg', 'body': intermapper_failed_outage_body, 'msg_uid': msg_uid_5}],
            'status': 200
        }
        mark_email_as_read_failed_response = {
            'body': 'Failed to mark as read',
            'status': 400
        }
        mark_email_as_read_success_response = {
            'body': 'Marked as read',
            'status': 200
        }
        circuit_id = 3214
        circuit_id_response = {
            "body": {
                      "clientID": 83959,
                      "subAccount": "string",
                      "wtn": circuit_id,
                      "inventoryID": 0,
                      "addressID": 0
            },
            "status": 200
        }
        circuit_id_failed_response = {
            "body": 'Failed',
            "status": 204
        }

        ticket_id = 321
        outage_ticket_response = {
            'body': 'Failed',
            'status': 400
        }

        slack_message = (
            f'Outage ticket created through Intermapper emails for circuit_id {circuit_id}. Ticket '
            f'details at https://app.bruin.com/t/{ticket_id}.'
        )
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.get_unread_emails = CoroutineMock(return_value=intermapper_response)
        notifications_repository.mark_email_as_read = CoroutineMock(side_effect=[mark_email_as_read_failed_response,
                                                                                 mark_email_as_read_success_response,
                                                                                 mark_email_as_read_success_response,
                                                                                 mark_email_as_read_success_response,
                                                                                 mark_email_as_read_success_response,
                                                                                 mark_email_as_read_success_response])
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_circuit_id = CoroutineMock(side_effect=[circuit_id_failed_response,
                                                                     circuit_id_response])
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.append_intermapper_note = CoroutineMock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)

        await intermapper_monitor._intermapper_monitoring_process()

        notifications_repository.get_unread_emails.assert_awaited_once()
        notifications_repository.mark_email_as_read.assert_has_awaits([
            call(msg_uid_1),
            call(msg_uid_2),
            call(msg_uid_3),
            call(msg_uid_4),
            call(msg_uid_5),

        ])

        bruin_repository.get_circuit_id.assert_has_awaits([
            call(str(asset_id), str(client_id)),
            call(str(asset_id_1), str(client_id_1)),

        ])
        bruin_repository.create_outage_ticket.assert_awaited_once_with(str(client_id_1), circuit_id)

        notifications_repository.send_slack_message.assert_not_awaited()
        bruin_repository.append_intermapper_note.assert_not_awaited()

    def parse_email_body_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        intermapper_body = os.linesep.join([
            "Event: Alarm",
            "Name: OReilly-HotSpringsAR(SD-WAN)-Site803",
            "Document: O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 ( SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        expected_dict = {
                            'event': 'Alarm',
                            'name': 'OReilly-HotSpringsAR(SD-WAN)-Site803',
                            'document': 'O Reilly Auto Parts - South East |83959| Platinum Monitoring',
                            'address': '1.3.4',
                            'probe_type': 'SNMP - Adtran TA900 ( SNMPv2c)',
                            'condition': '\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)',
                            'last_reported_down': '7 days, 23 hours, 54 minutes, 10 seconds',
                            'up_time': '209 days, 10 hours, 44 minutes, 16 seconds'

        }
        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)

        email_body = intermapper_monitor._parse_email_body(intermapper_body)
        assert email_body == expected_dict

    def parse_email_body_missing_section_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        intermapper_body = os.linesep.join([
            "Event: Alarm",
            "Name: OReilly-HotSpringsAR(SD-WAN)-Site803",
            "Document: O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "Address: 1.3.4",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        expected_dict = {
                            'event': 'Alarm',
                            'name': 'OReilly-HotSpringsAR(SD-WAN)-Site803',
                            'document': 'O Reilly Auto Parts - South East |83959| Platinum Monitoring',
                            'address': '1.3.4',
                            'probe_type': None,
                            'condition': '\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)',
                            'last_reported_down': '7 days, 23 hours, 54 minutes, 10 seconds',
                            'up_time': '209 days, 10 hours, 44 minutes, 16 seconds'

        }
        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)

        email_body = intermapper_monitor._parse_email_body(intermapper_body)
        assert email_body == expected_dict

    def extract_value_from_field_same_ending_and_starting_char_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        expected_client_id = 83959
        client_id_str = f'O Reilly Auto Parts - South East |{expected_client_id}| Platinum Monitoring'

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        client_id = intermapper_monitor._extract_value_from_field('|', '|', client_id_str)
        assert client_id == str(expected_client_id)

    def extract_value_from_field_different_ending_and_starting_char_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        expected_client_id = 83959
        client_id_str = f'O Reilly Auto Parts - South East [{expected_client_id}] Platinum Monitoring'

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        client_id = intermapper_monitor._extract_value_from_field('[', ']', client_id_str)
        assert client_id == str(expected_client_id)

    def extract_value_from_field_missing_ending_and_starting_char_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        expected_client_id = 83959
        client_id_str = f'O Reilly Auto Parts - South East [{expected_client_id}] Platinum Monitoring'

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        client_id = intermapper_monitor._extract_value_from_field('|', ']', client_id_str)
        assert client_id is None
