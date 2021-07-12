import os
from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest
from application.actions import intermapper_monitoring as intermapper_monitor_module
from application.actions.intermapper_monitoring import InterMapperMonitor
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from asynctest import CoroutineMock
from dateutil.parser import parse
from pytz import utc

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

        intermapper_up_body = os.linesep.join([
            "Event: Up",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        msg_uid = 123
        email_msg = '\nSubject: Up: Signet_Piercing_Pagoda_Jewelers_PP00305VC(CCQ22250L1Y)\n'

        intermapper_response = {
            'body': [{'message': email_msg, 'subject': email_msg, 'body': intermapper_body, 'msg_uid': msg_uid},
                     {'message': email_msg, 'subject': email_msg, 'body': intermapper_up_body, 'msg_uid': msg_uid}],
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

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.get_unread_emails = CoroutineMock(return_value=intermapper_response)
        notifications_repository.mark_email_as_read = CoroutineMock(return_value=mark_email_as_read_response)

        bruin_repository = Mock()
        bruin_repository.get_circuit_id = CoroutineMock(return_value=circuit_id_response)

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        intermapper_monitor._create_outage_ticket = CoroutineMock(return_value=True)
        intermapper_monitor._autoresolve_ticket = CoroutineMock(return_value=True)

        await intermapper_monitor._intermapper_monitoring_process()

        notifications_repository.get_unread_emails.assert_awaited()
        notifications_repository.mark_email_as_read.assert_has_awaits([
            call(msg_uid),
            call(msg_uid)
        ])

        bruin_repository.get_circuit_id.assert_has_awaits([
            call(str(asset_id)),
            call(str(asset_id))
        ])
        intermapper_monitor._create_outage_ticket.assert_awaited_once_with(circuit_id, client_id,
                                                                           intermapper_body)
        intermapper_monitor._autoresolve_ticket.assert_awaited_once_with(circuit_id, client_id,
                                                                         intermapper_up_body)

    @pytest.mark.asyncio
    async def intermapper_monitoring_process_irrelevant_event_test(self):
        asset_id = 123
        client_id = 83959
        intermapper_body = os.linesep.join([
            "Event: ACK",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        msg_uid = 123
        email_msg = '\nSubject: Up: Signet_Piercing_Pagoda_Jewelers_PP00305VC(CCQ22250L1Y)\n'

        intermapper_response = {
            'body': [{'message': email_msg, 'subject': email_msg, 'body': intermapper_body, 'msg_uid': msg_uid}],
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

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.get_unread_emails = CoroutineMock(return_value=intermapper_response)
        notifications_repository.mark_email_as_read = CoroutineMock(return_value=mark_email_as_read_response)

        bruin_repository = Mock()
        bruin_repository.get_circuit_id = CoroutineMock(return_value=circuit_id_response)

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        intermapper_monitor._create_outage_ticket = CoroutineMock(return_value=True)
        intermapper_monitor._autoresolve_ticket = CoroutineMock(return_value=True)

        await intermapper_monitor._intermapper_monitoring_process()

        notifications_repository.get_unread_emails.assert_awaited()
        notifications_repository.mark_email_as_read.assert_awaited_once_with(msg_uid)

        bruin_repository.get_circuit_id.assert_awaited_once_with(str(asset_id))

        intermapper_monitor._create_outage_ticket.assert_not_awaited()
        intermapper_monitor._autoresolve_ticket.assert_not_awaited()

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

        bruin_repository = Mock()
        bruin_repository.get_circuit_id = CoroutineMock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        intermapper_monitor._create_outage_ticket = CoroutineMock()

        await intermapper_monitor._intermapper_monitoring_process()

        notifications_repository.get_unread_emails.assert_awaited_once()
        notifications_repository.mark_email_as_read.assert_not_awaited()

        bruin_repository.get_circuit_id.assert_not_awaited()
        intermapper_monitor._create_outage_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def intermapper_monitoring_process_failed_test(self):
        asset_id = 123
        client_id = 83959
        intermapper_sd_wan_body = os.linesep.join([
            "Event: Alarm",
            f"Name: OReilly-HotSpringsAR(SD-WAN)-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        intermapper_failed_circuit_id_body = os.linesep.join([
            "Event: Alarm",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        intermapper_failed_to_mark_as_read = os.linesep.join([
            "Event: Down",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        intermapper_failed_outage_process = os.linesep.join([
            "Event: Down",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        intermapper_204_circuit_id_body = os.linesep.join([
            "Event: Alarm",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
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
        msg_uid_6 = 6

        email_msg = '\nSubject: Up: Signet_Piercing_Pagoda_Jewelers_PP00305VC(CCQ22250L1Y)\n'

        intermapper_response = {
            'body': [{'message': email_msg, 'subject': email_msg, 'body': 'skipped', 'msg_uid': -1},
                     {'message': email_msg, 'subject': email_msg, 'body': intermapper_sd_wan_body,
                      'msg_uid': msg_uid_0},
                     {'message': email_msg, 'subject': email_msg, 'body': intermapper_sd_wan_body,
                      'msg_uid': msg_uid_1},
                     {'message': email_msg, 'subject': email_msg, 'body': intermapper_failed_circuit_id_body,
                      'msg_uid': msg_uid_2},
                     {'message': email_msg, 'subject': email_msg, 'body': intermapper_failed_to_mark_as_read,
                      'msg_uid': msg_uid_3},
                     {'message': email_msg, 'subject': email_msg, 'body': intermapper_failed_outage_process,
                      'msg_uid': msg_uid_4},
                     {'message': email_msg, 'subject': email_msg, 'body': intermapper_204_circuit_id_body,
                      'msg_uid': msg_uid_5},
                     {'message': email_msg, 'subject': email_msg, 'body': intermapper_204_circuit_id_body,
                      'msg_uid': msg_uid_6},
                     ],

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
        circuit_id_response = {
            "body": {
                "clientID": client_id,
                "subAccount": "string",
                "wtn": asset_id,
                "inventoryID": 0,
                "addressID": 0
            },
            "status": 200
        }
        circuit_id_failed_response = {
            "body": 'Failed',
            "status": 400
        }
        circuit_id_204_response = {
            "body": 'Failed',
            "status": 204
        }
        event_bus = Mock()
        logger = Mock()
        logger.error = Mock()
        scheduler = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.get_unread_emails = CoroutineMock(return_value=intermapper_response)
        notifications_repository.mark_email_as_read = CoroutineMock(side_effect=[mark_email_as_read_success_response,
                                                                                 mark_email_as_read_failed_response,
                                                                                 mark_email_as_read_failed_response,
                                                                                 mark_email_as_read_success_response,
                                                                                 mark_email_as_read_failed_response])

        bruin_repository = Mock()
        bruin_repository.get_circuit_id = CoroutineMock(side_effect=[circuit_id_failed_response,
                                                                     circuit_id_response,
                                                                     circuit_id_response,
                                                                     circuit_id_204_response,
                                                                     circuit_id_204_response])

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        intermapper_monitor._create_outage_ticket = CoroutineMock(side_effect=[True, False])

        await intermapper_monitor._intermapper_monitoring_process()

        notifications_repository.get_unread_emails.assert_awaited_once()
        notifications_repository.mark_email_as_read.assert_has_awaits([
            call(msg_uid_0),
            call(msg_uid_1),
            call(msg_uid_3),
            call(msg_uid_5),
            call(msg_uid_6),
        ])

        bruin_repository.get_circuit_id.assert_has_awaits([
            call(str(asset_id)),
            call(str(asset_id)),
            call(str(asset_id)),
            call(str(asset_id)),
            call(str(asset_id))
        ])
        intermapper_monitor._create_outage_ticket.assert_has_awaits([call(asset_id, client_id,
                                                                          intermapper_failed_to_mark_as_read),
                                                                     call(asset_id, client_id,
                                                                          intermapper_failed_outage_process)
                                                                     ])

        logger.error.assert_called()

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

    @pytest.mark.asyncio
    async def create_outage_ticket_test(self):
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

        circuit_id = 3214
        ticket_id = 321
        outage_ticket_response = {
            'body': ticket_id,
            'status': 200
        }

        slack_message = (
            f'Outage ticket created through InterMapper emails for circuit_id {circuit_id}. Ticket '
            f'details at https://app.bruin.com/t/{ticket_id}.'
        )

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.append_intermapper_note = CoroutineMock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)

        response = await intermapper_monitor._create_outage_ticket(circuit_id, client_id, intermapper_body)

        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, circuit_id)
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)
        bruin_repository.append_intermapper_note.assert_awaited_once_with(ticket_id, intermapper_body)
        assert response is True

    @pytest.mark.asyncio
    async def create_outage_ticket_failed_rpc_test(self):
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

        circuit_id = 3214
        ticket_id = 321
        outage_ticket_response = {
            'body': ticket_id,
            'status': 400
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.append_intermapper_note = CoroutineMock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)

        response = await intermapper_monitor._create_outage_ticket(circuit_id, client_id, intermapper_body)

        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, circuit_id)
        notifications_repository.send_slack_message.assert_not_awaited()
        bruin_repository.append_intermapper_note.assert_not_awaited()
        assert response is False

    @pytest.mark.asyncio
    async def autoresolve_ticket_test(self):
        asset_id = 123
        client_id = 83959
        intermapper_body = os.linesep.join([
            "Event: UP",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        circuit_id = 3214

        serial_number_2 = 'VC9999999'

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": "SD-WAN",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": outage_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            'body': [
                outage_ticket_1
            ],
            'status': 200,
        }

        outage_ticket_detail_1_id = 2746937
        outage_ticket_detail_1 = {
            "detailID": outage_ticket_detail_1_id,
            "detailValue": circuit_id,
            "detailStatus": "I",
        }
        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": f"#*MetTel's IPA*#\nAuto-resolving task for {circuit_id}\n"
                         f"TimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                circuit_id,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": f"#*MetTel's IPA*#\nAuto-resolving task for {circuit_id}\n"
                         f"TimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                circuit_id,
            ],
        }

        ticket_note_3 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                circuit_id,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        relevant_notes_for_edge = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_4,
        ]

        resolve_outage_ticket_response = {
            'body': 'ok',
            'status': 200,
        }

        slack_message = (
            f'Outage ticket {outage_ticket_1_id} for circuit_id {circuit_id} '
            f'was autoresolved through InterMapper emails. '
            f'Ticket details at https://app.bruin.com/t/{outage_ticket_1_id}.'
        )
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_outage_ticket_response)
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock(return_value=True)

        response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, intermapper_body)

        bruin_repository.get_tickets.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        intermapper_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date
        )
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable.assert_called_once_with(
            relevant_notes_for_edge, circuit_id, max_autoresolves=3
        )

        bruin_repository.resolve_ticket.assert_awaited_once_with(outage_ticket_1_id, outage_ticket_detail_1_id)
        bruin_repository.append_autoresolve_note.assert_awaited_once_with(outage_ticket_1_id, circuit_id,
                                                                          intermapper_body)
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)

        assert response is True

    @pytest.mark.asyncio
    async def autoresolve_no_tickets_test(self):
        asset_id = 123
        client_id = 83959
        intermapper_body = os.linesep.join([
            "Event: UP",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        circuit_id = 3214

        serial_number_2 = 'VC9999999'

        outage_ticket_response = {
            'body': [],
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock()
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock()

        response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, intermapper_body)

        bruin_repository.get_tickets.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.get_ticket_details.assert_not_awaited()
        intermapper_monitor._was_last_outage_detected_recently.assert_not_called()
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable.assert_not_called()

        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

        assert response is True

    @pytest.mark.asyncio
    async def autoresolve_ticket_failed_tickets_rpc_request_test(self):
        asset_id = 123
        client_id = 83959
        intermapper_body = os.linesep.join([
            "Event: UP",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        circuit_id = 3214

        outage_ticket_response = {
            'body': 'Failed RPC',
            'status': 400,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock(return_value=True)

        response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, intermapper_body)

        bruin_repository.get_tickets.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.get_ticket_details.assert_not_awaited()
        intermapper_monitor._was_last_outage_detected_recently.assert_not_called()
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable.assert_not_called()

        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()
        assert response is False

    @pytest.mark.asyncio
    async def autoresolve_ticket_failed_tickets_details_rpc_request_test(self):
        asset_id = 123
        client_id = 83959
        intermapper_body = os.linesep.join([
            "Event: UP",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        circuit_id = 3214

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": "SD-WAN",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": outage_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            'body': [
                outage_ticket_1
            ],
            'status': 200,
        }

        ticket_details_response = {
            'body': 'Failed RPC',
            'status': 400,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock()
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock()

        response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, intermapper_body)

        bruin_repository.get_tickets.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        intermapper_monitor._was_last_outage_detected_recently.assert_not_called()

        intermapper_monitor._is_outage_ticket_detail_auto_resolvable.assert_not_called()

        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()
        assert response is False

    @pytest.mark.asyncio
    async def autoresolve_ticket_outage_not_detected_recently_test(self):
        asset_id = 123
        client_id = 83959
        intermapper_body = os.linesep.join([
            "Event: UP",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        circuit_id = 3214

        serial_number_2 = 'VC9999999'

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": "SD-WAN",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": outage_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            'body': [
                outage_ticket_1
            ],
            'status': 200,
        }

        outage_ticket_detail_1_id = 2746937
        outage_ticket_detail_1 = {
            "detailID": outage_ticket_detail_1_id,
            "detailValue": circuit_id,
            "detailStatus": "I",
        }
        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail for circuit ID\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                circuit_id,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail for circuit ID\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                circuit_id,
            ],
        }

        ticket_note_3 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                circuit_id,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        relevant_notes_for_edge = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_4,
        ]

        resolve_outage_ticket_response = {
            'body': 'ok',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_outage_ticket_response)
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock(return_value=False)
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock(return_value=True)

        response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, intermapper_body)

        bruin_repository.get_tickets.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        intermapper_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date
        )
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable.assert_not_called()

        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()
        assert response is True

    @pytest.mark.asyncio
    async def autoresolve_ticket_cannot_autoresolve_one_more_time_test(self):
        asset_id = 123
        client_id = 83959
        intermapper_body = os.linesep.join([
            "Event: UP",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        circuit_id = 3214

        serial_number_2 = 'VC9999999'

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": "SD-WAN",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": outage_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            'body': [
                outage_ticket_1
            ],
            'status': 200,
        }

        outage_ticket_detail_1_id = 2746937
        outage_ticket_detail_1 = {
            "detailID": outage_ticket_detail_1_id,
            "detailValue": circuit_id,
            "detailStatus": "I",
        }
        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail for circuit ID\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                circuit_id,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail for circuit ID\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                circuit_id,
            ],
        }

        ticket_note_3 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                circuit_id,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        relevant_notes_for_edge = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_4,
        ]

        resolve_outage_ticket_response = {
            'body': 'ok',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_outage_ticket_response)
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock(return_value=False)

        response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, intermapper_body)

        bruin_repository.get_tickets.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        intermapper_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date
        )
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable.assert_called_once_with(
            relevant_notes_for_edge, circuit_id, max_autoresolves=3
        )

        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()
        assert response is True

    @pytest.mark.asyncio
    async def autoresolve_ticket_failed_resolve_rpc_request_test(self):
        asset_id = 123
        client_id = 83959
        intermapper_body = os.linesep.join([
            "Event: UP",
            f"Name: OReilly-HotSpringsAR({asset_id})-Site803",
            f"Document: O Reilly Auto Parts - South East |{client_id}| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 (SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        circuit_id = 3214

        serial_number_2 = 'VC9999999'

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": "SD-WAN",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": outage_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            'body': [
                outage_ticket_1
            ],
            'status': 200,
        }

        outage_ticket_detail_1_id = 2746937
        outage_ticket_detail_1 = {
            "detailID": outage_ticket_detail_1_id,
            "detailValue": circuit_id,
            "detailStatus": "I",
        }
        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail for circuit ID\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                circuit_id,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail for circuit ID\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                circuit_id,
            ],
        }

        ticket_note_3 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                circuit_id,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        relevant_notes_for_edge = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_4,
        ]

        resolve_outage_ticket_response = {
            'body': 'Failed',
            'status': 400,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_outage_ticket_response)
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock(return_value=True)

        response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, intermapper_body)

        bruin_repository.get_tickets.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        intermapper_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date
        )
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable.assert_called_once_with(
            relevant_notes_for_edge, circuit_id, max_autoresolves=3
        )

        bruin_repository.resolve_ticket.assert_awaited_once_with(outage_ticket_1_id, outage_ticket_detail_1_id)
        bruin_repository.append_autoresolve_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()
        assert response is False

    def last_outage_detected_recently_with_no_reopen_note_or_no_triage_test(self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        ticket_notes = []

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        datetime_mock = Mock()

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    def last_outage_detected_recently_with_reopen_note_test(self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        triage_timestamp = '2021-01-02T10:18:16.71-05:00'
        reopen_timestamp = '2021-01-02T11:00:16.71-05:00'

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nInterMapper Triage\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                'VC1234567',
            ],
            "createdDate": triage_timestamp,
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nRe-opening\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                'VC1234567',
            ],
            "createdDate": reopen_timestamp,
        }

        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        datetime_mock = Mock()

        new_now = parse(reopen_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    def last_outage_detected_recently_with_triage_note_and_no_reopen_note_test(self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        triage_timestamp = '2021-01-02T10:18:16.71-05:00'

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nInterMapper Triage\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                'VC1234567',
            ],
            "createdDate": triage_timestamp,
        }

        ticket_notes = [
            ticket_note_1,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        datetime_mock = Mock()

        new_now = parse(triage_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    def is_outage_ticket_detail_auto_resolvable_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC7654321'
        serial_number_3 = '123'

        text_identifier = ("#*MetTel's IPA*#\n"
                           f"Auto-resolving task")

        note_value1 = f"{text_identifier} for {serial_number_1}\nTimeStamp: 2021-01-02 10:18:16-05:00"
        note_value2 = f"{text_identifier} for {serial_number_2}\nTimeStamp: 2020-01-02 10:18:16-05:00"
        note_value3 = f"{text_identifier} for {serial_number_3}\nTimeStamp: 2022-01-02 10:18:16-05:00"

        note_value4 = ("#*MetTel's IPA*#\n"
                       "Just another kind of note\n")

        ticket_notes1 = [
            {
                "noteId": 41894040,
                "noteValue": note_value1,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894043,
                "noteValue": note_value4,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
        ]

        ticket_notes2 = [
            {
                "noteId": 41894040,
                "noteValue": note_value1,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894041,
                "noteValue": note_value2,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894042,
                "noteValue": note_value4,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
        ]

        ticket_notes3 = [
            {
                "noteId": 41894040,
                "noteValue": note_value1,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894041,
                "noteValue": note_value4,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894042,
                "noteValue": note_value2,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894043,
                "noteValue": note_value3,
                "serviceNumber": [
                    serial_number_1,
                ],
            }
        ]

        ticket_notes4 = [
            {
                "noteId": 41894040,
                "noteValue": note_value1,
                "serviceNumber": [
                    serial_number_2,
                ],
            },
            {
                "noteId": 41894042,
                "noteValue": note_value2,
                "serviceNumber": [
                    serial_number_2,
                ],
            },
            {
                "noteId": 41894043,
                "noteValue": note_value3,
                "serviceNumber": [
                    serial_number_2,
                ],
            }
        ]

        ticket_notes5 = [
            {
                "noteId": 41894040,
                "noteValue": note_value1,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894040,
                "noteValue": note_value1,
                "serviceNumber": [
                    serial_number_2,
                ],
            },
            {
                "noteId": 41894042,
                "noteValue": note_value2,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894042,
                "noteValue": note_value2,
                "serviceNumber": [
                    serial_number_2,
                ],
            },
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository)
        autoresolve_limit = 3

        ticket_bool1 = intermapper_monitor._is_outage_ticket_detail_auto_resolvable(
            ticket_notes1, serial_number_1, autoresolve_limit
        )
        assert ticket_bool1 is True

        ticket_bool2 = intermapper_monitor._is_outage_ticket_detail_auto_resolvable(
            ticket_notes2, serial_number_1, autoresolve_limit
        )
        assert ticket_bool2 is True

        ticket_bool3 = intermapper_monitor._is_outage_ticket_detail_auto_resolvable(
            ticket_notes3, serial_number_1, autoresolve_limit
        )
        assert ticket_bool3 is False

        ticket_bool4 = intermapper_monitor._is_outage_ticket_detail_auto_resolvable(
            ticket_notes4, serial_number_2, autoresolve_limit
        )
        assert ticket_bool4 is False

        ticket_bool5 = intermapper_monitor._is_outage_ticket_detail_auto_resolvable(
            ticket_notes5, serial_number_1, autoresolve_limit
        )
        assert ticket_bool5 is True

        ticket_bool6 = intermapper_monitor._is_outage_ticket_detail_auto_resolvable(
            ticket_notes5, serial_number_2, autoresolve_limit
        )
        assert ticket_bool6 is True
