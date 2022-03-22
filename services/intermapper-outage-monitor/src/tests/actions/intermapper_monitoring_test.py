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

config_mock = patch.object(testconfig, 'CURRENT_ENVIRONMENT', 'production')


class TestInterMapperMonitor:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()
        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        assert intermapper_monitor._event_bus == event_bus
        assert intermapper_monitor._logger == logger
        assert intermapper_monitor._scheduler == scheduler
        assert intermapper_monitor._config == config
        assert intermapper_monitor._notifications_repository == notifications_repository
        assert intermapper_monitor._bruin_repository == bruin_repository
        assert intermapper_monitor._dri_repository == dri_repository

    @pytest.mark.asyncio
    async def start_intermapper_outage_monitoring_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock()

        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

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

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

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

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

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
        asset_id = '123'

        email_1 = {'msg_uid': 123, 'body': f"01/19 19:35:31: Message from InterMapper 6.1.5\n"
                                           f"Name: OReilly-HotSpringsAR({asset_id})-Site803"}
        email_2 = {'msg_uid': 456, 'body': f"01/19 19:35:31: Message from InterMapper 6.1.5\n"
                                           f"Name: OReilly-HotSpringsAR({asset_id})-Site803"}
        emails = [email_1, email_2]

        response = {
            'body': emails,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        bruin_repository = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.get_unread_emails = CoroutineMock(return_value=response)

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._process_email_batch = CoroutineMock()

        await intermapper_monitor._intermapper_monitoring_process()

        notifications_repository.get_unread_emails.assert_awaited_once()
        intermapper_monitor._process_email_batch.assert_has_awaits([call(emails, asset_id)], any_order=True)

    def group_emails_by_asset_id_test(self):
        asset_id_1 = '123'
        asset_id_2 = '456'

        email_1 = {'body': f"01/19 19:35:31: Message from InterMapper 6.1.5\n"
                           f"Name: OReilly-HotSpringsAR({asset_id_1})-Site803"}
        email_2 = {'body': f"01/19 19:35:31: Message from InterMapper 6.1.5\n"
                           f"Name: OReilly-HotSpringsAR({asset_id_1})-Site803"}
        email_3 = {'body': f"01/19 19:35:31: Message from InterMapper 6.1.5\n"
                           f"Name: OReilly-HotSpringsAR({asset_id_2})-Site803"}
        emails = [email_1, email_2, email_3]

        emails_by_asset_id = {
            asset_id_1: [email_1, email_2],
            asset_id_2: [email_3],
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        config = testconfig
        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        result = intermapper_monitor._group_emails_by_asset_id(emails)
        assert result == emails_by_asset_id

    @pytest.mark.asyncio
    async def process_email_batch_test(self):
        asset_id = 123
        circuit_id = 3214
        client_id = 83959

        email_1 = {'msg_uid': 123, 'body': f"01/19 19:35:31: Message from InterMapper 6.1.5\n"
                                           f"Name: OReilly-HotSpringsAR({asset_id})-Site803"}
        email_2 = {'msg_uid': 456, 'body': f"01/19 19:35:31: Message from InterMapper 6.1.5\n"
                                           f"Name: OReilly-HotSpringsAR({asset_id})-Site803"}
        emails = [email_1, email_2]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        config = testconfig

        response = {
            'body': {
                'wtn': circuit_id,
                'clientID': client_id,
            },
            'status': 200,
        }

        bruin_repository = Mock()
        bruin_repository.get_circuit_id = CoroutineMock(return_value=response)

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._process_email = CoroutineMock()

        await intermapper_monitor._process_email_batch(emails, asset_id)

        intermapper_monitor._bruin_repository.get_circuit_id.assert_awaited_with(asset_id)
        intermapper_monitor._process_email.assert_has_awaits([
            call(email_1, circuit_id, client_id),
            call(email_2, circuit_id, client_id),
        ])

    @pytest.mark.asyncio
    async def process_email_batch_no_asset_id_test(self):
        asset_id = None

        email_1 = {'msg_uid': 123, 'body': f"01/19 19:35:31: Message from InterMapper 6.1.5\n"
                                           f"Name: OReilly-HotSpringsAR({asset_id})-Site803"}
        email_2 = {'msg_uid': 456, 'body': f"01/19 19:35:31: Message from InterMapper 6.1.5\n"
                                           f"Name: OReilly-HotSpringsAR({asset_id})-Site803"}
        emails = [email_1, email_2]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.mark_email_as_read = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_circuit_id = CoroutineMock()

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        with config_mock:
            await intermapper_monitor._process_email_batch(emails, asset_id)

        intermapper_monitor._notifications_repository.mark_email_as_read.assert_has_awaits([
            call(email_1['msg_uid']),
            call(email_2['msg_uid']),
        ])
        intermapper_monitor._bruin_repository.get_circuit_id.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_email_batch_non_2xx_test(self):
        asset_id = 123

        email_1 = {'msg_uid': 123, 'body': f"01/19 19:35:31: Message from InterMapper 6.1.5\n"
                                           f"Name: OReilly-HotSpringsAR({asset_id})-Site803"}
        email_2 = {'msg_uid': 456, 'body': f"01/19 19:35:31: Message from InterMapper 6.1.5\n"
                                           f"Name: OReilly-HotSpringsAR({asset_id})-Site803"}
        emails = [email_1, email_2]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        response = {
            'body': None,
            'status': 400,
        }

        bruin_repository = Mock()
        bruin_repository.get_circuit_id = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.mark_email_as_read = CoroutineMock()

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        with config_mock:
            await intermapper_monitor._process_email_batch(emails, asset_id)

        intermapper_monitor._bruin_repository.get_circuit_id.assert_awaited_with(asset_id)
        intermapper_monitor._notifications_repository.mark_email_as_read.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_email_batch_204_test(self):
        asset_id = 123

        email_1 = {'msg_uid': 123, 'body': f"01/19 19:35:31: Message from InterMapper 6.1.5\n"
                                           f"Name: OReilly-HotSpringsAR({asset_id})-Site803"}
        email_2 = {'msg_uid': 456, 'body': f"01/19 19:35:31: Message from InterMapper 6.1.5\n"
                                           f"Name: OReilly-HotSpringsAR({asset_id})-Site803"}
        emails = [email_1, email_2]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        response = {
            'body': None,
            'status': 204,
        }

        bruin_repository = Mock()
        bruin_repository.get_circuit_id = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.mark_email_as_read = CoroutineMock()

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        with config_mock:
            await intermapper_monitor._process_email_batch(emails, asset_id)

        intermapper_monitor._bruin_repository.get_circuit_id.assert_awaited_with(asset_id)
        intermapper_monitor._notifications_repository.mark_email_as_read.assert_has_awaits([
            call(email_1['msg_uid']),
            call(email_2['msg_uid']),
        ])

    @pytest.mark.asyncio
    async def process_email_invalid_test(self):
        circuit_id = 3214
        client_id = 83959

        email = {
            'msg_uid': 123,
            'message': None,
            'subject': '',
            'body': 'Event: Down',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        bruin_repository = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.mark_email_as_read = CoroutineMock()

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        with config_mock:
            await intermapper_monitor._process_email(email, circuit_id, client_id)

        intermapper_monitor._logger.error.assert_called_once()
        notifications_repository.mark_email_as_read.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_email_down_event_non_PIAB_device_test(self):
        circuit_id = 3214
        client_id = 83959

        dri_parameters = None

        email = {
            'msg_uid': 123,
            'message': '',
            'subject': '',
            'body': "01/19 19:35:31: Message from InterMapper 6.1.5\nEvent: Down\nProbe Type: "
                    "SNMP - Adtran TA900 ( SNMPv2c)",
        }

        response = {
            'body': None,
            'status': 204
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        bruin_repository = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.mark_email_as_read = CoroutineMock(return_value=response)

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._create_outage_ticket = CoroutineMock(return_value=True)
        intermapper_monitor._get_dri_parameters = CoroutineMock(return_value=dri_parameters)

        parsed_email_dict = intermapper_monitor._parse_email_body(email['body'])

        with config_mock:
            await intermapper_monitor._process_email(email, circuit_id, client_id)

        intermapper_monitor._get_dri_parameters.assert_not_awaited()
        intermapper_monitor._create_outage_ticket.assert_awaited_once_with(circuit_id, client_id, parsed_email_dict,
                                                                           dri_parameters)
        notifications_repository.mark_email_as_read.assert_awaited_once_with(email['msg_uid'])

    @pytest.mark.asyncio
    async def process_email_down_event_PIAB_device_test(self):
        circuit_id = 3214
        client_id = 83959

        dri_parameters = {
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei": "864839040023968",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers": "ATT",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid": "89014103272191198072",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert": "SIM1 Active",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum": "15245139487",
                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress": "8C:19:30:69"
              }

        email = {
            'msg_uid': 123,
            'message': '',
            'subject': '',
            'body': "01/19 19:35:31: Message from InterMapper 6.1.5\nEvent: Down\nProbe Type: "
                    "Data Remote Probe ( SNMPv2c)",
        }

        response = {
            'body': None,
            'status': 204
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        bruin_repository = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.mark_email_as_read = CoroutineMock(return_value=response)

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._create_outage_ticket = CoroutineMock(return_value=True)
        intermapper_monitor._get_dri_parameters = CoroutineMock(return_value=dri_parameters)

        parsed_email_dict = intermapper_monitor._parse_email_body(email['body'])

        with config_mock:
            await intermapper_monitor._process_email(email, circuit_id, client_id)

        intermapper_monitor._get_dri_parameters.assert_awaited_once_with(circuit_id, client_id)
        intermapper_monitor._create_outage_ticket.assert_awaited_once_with(circuit_id, client_id, parsed_email_dict,
                                                                           dri_parameters)
        notifications_repository.mark_email_as_read.assert_awaited_once_with(email['msg_uid'])

    @pytest.mark.asyncio
    async def process_email_up_event_test(self):
        circuit_id = 3214
        client_id = 83959

        email = {
            'msg_uid': 123,
            'message': '',
            'subject': '',
            'body': '01/19 19:35:31: Message from InterMapper 6.1.5\nEvent: Up',
        }

        response = {
            'body': None,
            'status': 204
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        bruin_repository = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.mark_email_as_read = CoroutineMock(return_value=response)

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._autoresolve_ticket = CoroutineMock(return_value=True)
        parsed_email_dict = intermapper_monitor._parse_email_body(email['body'])

        with config_mock:
            await intermapper_monitor._process_email(email, circuit_id, client_id)

        intermapper_monitor._autoresolve_ticket.assert_awaited_once_with(circuit_id, client_id, parsed_email_dict)
        notifications_repository.mark_email_as_read.assert_awaited_once_with(email['msg_uid'])

    @pytest.mark.asyncio
    async def process_email_irrelevant_event_test(self):
        circuit_id = 3214
        client_id = 83959

        email = {
            'msg_uid': 123,
            'message': '',
            'subject': '',
            'body': '01/19 19:35:31: Message from InterMapper 6.1.5\nEvent: ACK',
        }

        response = {
            'body': None,
            'status': 204
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        bruin_repository = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.mark_email_as_read = CoroutineMock(return_value=response)

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._create_outage_ticket = CoroutineMock()
        intermapper_monitor._autoresolve_ticket = CoroutineMock()

        with config_mock:
            await intermapper_monitor._process_email(email, circuit_id, client_id)

        intermapper_monitor._create_outage_ticket.assert_not_awaited()
        intermapper_monitor._autoresolve_ticket.assert_not_awaited()
        notifications_repository.mark_email_as_read.assert_awaited_once_with(email['msg_uid'])

    @pytest.mark.asyncio
    async def process_email_failed_test(self):
        circuit_id = 3214
        client_id = 83959

        email = {
            'msg_uid': 123,
            'message': '',
            'subject': '',
            'body': '01/19 19:35:31: Message from InterMapper 6.1.5\nEvent: Up',
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        bruin_repository = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.mark_email_as_read = CoroutineMock()

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._autoresolve_ticket = CoroutineMock(return_value=False)

        with config_mock:
            await intermapper_monitor._process_email(email, circuit_id, client_id)

        notifications_repository.mark_email_as_read.assert_not_awaited()

    def parse_email_body_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()
        dri_repository = Mock()

        intermapper_body = os.linesep.join([
            "01/10 15:35:40: Message from InterMapper 6.1.5\n",
            "Event: Alarm",
            "Name: OReilly-HotSpringsAR(SD-WAN)-Site803",
            "Document: O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 ( SNMPv2c)",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Previous Condition: OK",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        expected_dict = {
                            'time': '01/10 15:35:40',
                            'version': '6.1.5',
                            'event': 'Alarm',
                            'name': 'OReilly-HotSpringsAR(SD-WAN)-Site803',
                            'document': 'O Reilly Auto Parts - South East |83959| Platinum Monitoring',
                            'address': '1.3.4',
                            'probe_type': 'SNMP - Adtran TA900 ( SNMPv2c)',
                            'condition': 'defined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)',
                            'previous_condition': 'OK',
                            'last_reported_down': '7 days, 23 hours, 54 minutes, 10 seconds',
                            'up_time': '209 days, 10 hours, 44 minutes, 16 seconds'

        }

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        email_body = intermapper_monitor._parse_email_body(intermapper_body)
        assert email_body == expected_dict

    def parse_email_body_no_condition_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()
        dri_repository = Mock()

        intermapper_body = os.linesep.join([
            "01/10 15:35:40: Message from InterMapper 6.1.5\n",
            "Event: Alarm",
            "Name: OReilly-HotSpringsAR(SD-WAN)-Site803",
            "Document: O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "Address: 1.3.4",
            "Probe Type: SNMP - Adtran TA900 ( SNMPv2c)",
            "Condition:",
            "Previous Condition: OK",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        expected_dict = {
                            'time': '01/10 15:35:40',
                            'version': '6.1.5',
                            'event': 'Alarm',
                            'name': 'OReilly-HotSpringsAR(SD-WAN)-Site803',
                            'document': 'O Reilly Auto Parts - South East |83959| Platinum Monitoring',
                            'address': '1.3.4',
                            'probe_type': 'SNMP - Adtran TA900 ( SNMPv2c)',
                            'condition': 'Alarm',
                            'previous_condition': 'OK',
                            'last_reported_down': '7 days, 23 hours, 54 minutes, 10 seconds',
                            'up_time': '209 days, 10 hours, 44 minutes, 16 seconds'

        }

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        email_body = intermapper_monitor._parse_email_body(intermapper_body)
        assert email_body == expected_dict

    def parse_email_body_missing_section_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()
        dri_repository = Mock()

        intermapper_body = os.linesep.join([
            "01/10 15:35:40: Message from InterMapper 6.1.5\n",
            "Event: Alarm",
            "Name: OReilly-HotSpringsAR(SD-WAN)-Site803",
            "Document: O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "Address: 1.3.4",
            "Condition: \t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "Previous Condition: OK",
            "Time since last reported down: 7 days, 23 hours, 54 minutes, 10 seconds",
            "Device's up time: 209 days, 10 hours, 44 minutes, 16 seconds"])

        expected_dict = {
                            'time': '01/10 15:35:40',
                            'version': '6.1.5',
                            'event': 'Alarm',
                            'name': 'OReilly-HotSpringsAR(SD-WAN)-Site803',
                            'document': 'O Reilly Auto Parts - South East |83959| Platinum Monitoring',
                            'address': '1.3.4',
                            'probe_type': None,
                            'condition': 'defined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)',
                            'previous_condition': 'OK',
                            'last_reported_down': '7 days, 23 hours, 54 minutes, 10 seconds',
                            'up_time': '209 days, 10 hours, 44 minutes, 16 seconds'

        }
        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        email_body = intermapper_monitor._parse_email_body(intermapper_body)
        assert email_body == expected_dict

    def extract_value_from_field_same_ending_and_starting_char_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()
        dri_repository = Mock()

        expected_client_id = 83959
        client_id_str = f'O Reilly Auto Parts - South East |{expected_client_id}| Platinum Monitoring'

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        client_id = intermapper_monitor._extract_value_from_field('|', '|', client_id_str)
        assert client_id == str(expected_client_id)

    def extract_value_from_field_different_ending_and_starting_char_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()
        dri_repository = Mock()

        expected_client_id = 83959
        client_id_str = f'O Reilly Auto Parts - South East [{expected_client_id}] Platinum Monitoring'

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        client_id = intermapper_monitor._extract_value_from_field('[', ']', client_id_str)
        assert client_id == str(expected_client_id)

    def extract_value_from_field_missing_ending_and_starting_char_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()
        dri_repository = Mock()

        expected_client_id = 83959
        client_id_str = f'O Reilly Auto Parts - South East [{expected_client_id}] Platinum Monitoring'

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        client_id = intermapper_monitor._extract_value_from_field('|', ']', client_id_str)
        assert client_id is None

    @pytest.mark.asyncio
    async def create_outage_ticket_test(self):
        client_id = 83959
        dri_parameter = None
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
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

        post_ticket_response = {
            'body': 'success',
            'status': 200
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.append_intermapper_note = CoroutineMock(return_value=post_ticket_response)
        bruin_repository.append_dri_note = CoroutineMock()

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        with config_mock:
            response = await intermapper_monitor._create_outage_ticket(circuit_id, client_id, parsed_email_dict,
                                                                       dri_parameter)

        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, circuit_id)
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)
        bruin_repository.append_dri_note.assert_not_awaited()
        bruin_repository.append_intermapper_note.assert_awaited_once_with(ticket_id, parsed_email_dict, False)
        assert response is True

    @pytest.mark.asyncio
    async def create_outage_ticket_dri_parameters_given_test(self):
        dri_parameter = {
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei": "864839040023968",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers": "ATT",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid": "89014103272191198072",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert": "SIM1 Active",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum": "15245139487",
                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress": "8C:19:30:69"
              }
        client_id = 83959
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "Data Remote Probe (port 161 SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
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

        post_ticket_response = {
            'body': 'success',
            'status': 200
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
        bruin_repository.append_dri_note = CoroutineMock(return_value=post_ticket_response)

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._process_dri_email = CoroutineMock(return_value=True)

        with config_mock:
            response = await intermapper_monitor._create_outage_ticket(circuit_id, client_id, parsed_email_dict,
                                                                       dri_parameter)

        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, circuit_id)
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)
        bruin_repository.append_dri_note.assert_awaited_once_with(ticket_id, dri_parameter, parsed_email_dict)
        bruin_repository.append_intermapper_note.assert_not_awaited()
        assert response is True

    @pytest.mark.asyncio
    async def create_outage_ticket_failed_ticket_creation_rpc_test(self):
        dri_parameter = None
        client_id = 83959
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
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
        bruin_repository.append_dri_note = CoroutineMock()

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        with config_mock:
            response = await intermapper_monitor._create_outage_ticket(circuit_id, client_id, parsed_email_dict,
                                                                       dri_parameter)

        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, circuit_id)
        notifications_repository.send_slack_message.assert_not_awaited()
        bruin_repository.append_intermapper_note.assert_not_awaited()
        bruin_repository.append_dri_note.assert_not_awaited()
        assert response is False

    @pytest.mark.asyncio
    async def create_outage_ticket_failed_post_intermapper_note_rpc_test(self):
        client_id = 83959
        dri_parameter = None
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
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

        post_ticket_response = {
            'body': 'failed',
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
        bruin_repository.append_intermapper_note = CoroutineMock(return_value=post_ticket_response)
        bruin_repository.append_dri_note = CoroutineMock()

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        with config_mock:
            response = await intermapper_monitor._create_outage_ticket(circuit_id, client_id, parsed_email_dict,
                                                                       dri_parameter)

        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, circuit_id)
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)
        bruin_repository.append_dri_note.assert_not_awaited()
        bruin_repository.append_intermapper_note.assert_awaited_once_with(ticket_id, parsed_email_dict, False)
        assert response is False

    @pytest.mark.asyncio
    async def create_outage_ticket_dri_parameters_given_failed_post_dri_note_rpc_test(self):
        dri_parameter = {
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei": "864839040023968",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers": "ATT",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid": "89014103272191198072",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert": "SIM1 Active",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum": "15245139487",
            "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress": "8C:19:30:69"
        }
        client_id = 83959
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "Data Remote Probe (port 161 SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
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

        post_ticket_response = {
            'body': 'failed',
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
        bruin_repository.append_dri_note = CoroutineMock(return_value=post_ticket_response)

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._process_dri_email = CoroutineMock(return_value=True)

        with config_mock:
            response = await intermapper_monitor._create_outage_ticket(circuit_id, client_id, parsed_email_dict,
                                                                       dri_parameter)

        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, circuit_id)
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)
        bruin_repository.append_dri_note.assert_awaited_once_with(ticket_id, dri_parameter, parsed_email_dict)
        bruin_repository.append_intermapper_note.assert_not_awaited()
        assert response is False

    @pytest.mark.asyncio
    async def autoresolve_ticket_test(self):
        client_id = 83959
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
        circuit_id = 3214

        serial_number_2 = 'VC9999999'

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": "POTS in a Box,Switches",
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

        unpause_ticket_detail_response = {
            'body': 'ok',
            'status': '200',
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
        append_intermapper_up_response = {
            'body': 'OK',
            'status': 200
        }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_basic_info = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.unpause_ticket_detail = CoroutineMock(return_value=unpause_ticket_detail_response)
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_outage_ticket_response)
        bruin_repository.append_intermapper_up_note = CoroutineMock(return_value=append_intermapper_up_response)
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        intermapper_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock(return_value=True)

        with config_mock:
            response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, parsed_email_dict)

        bruin_repository.get_ticket_basic_info.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.append_intermapper_up_note.assert_awaited_once_with(outage_ticket_1_id, circuit_id,
                                                                             parsed_email_dict, False)
        bruin_repository.get_tickets.assert_awaited_once_with(client_id, outage_ticket_1_id)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        intermapper_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date, parsed_email_dict
        )
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable.assert_called_once_with(
            relevant_notes_for_edge, circuit_id, max_autoresolves=3
        )

        bruin_repository.resolve_ticket.assert_awaited_once_with(outage_ticket_1_id, outage_ticket_detail_1_id)
        bruin_repository.append_autoresolve_note.assert_awaited_once_with(outage_ticket_1_id, circuit_id)
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)

        assert response is True

    @pytest.mark.asyncio
    async def autoresolve_no_tickets_test(self):
        asset_id = 123
        client_id = 83959
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
        circuit_id = 3214

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
        bruin_repository.get_ticket_basic_info = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_tickets = CoroutineMock()
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock()
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock()

        with config_mock:
            response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, parsed_email_dict)

        bruin_repository.get_ticket_basic_info.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.get_tickets.assert_not_awaited()
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
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
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
        bruin_repository.get_ticket_basic_info = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_tickets = CoroutineMock()
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock(return_value=True)

        with config_mock:
            response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, parsed_email_dict)

        bruin_repository.get_ticket_basic_info.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.get_tickets.assert_not_awaited()
        bruin_repository.get_ticket_details.assert_not_awaited()
        intermapper_monitor._was_last_outage_detected_recently.assert_not_called()
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable.assert_not_called()

        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()
        assert response is False

    @pytest.mark.asyncio
    async def autoresolve_ticket_failed_append_up_note_rpc_request_test(self):
        asset_id = 123
        client_id = 83959
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
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

        append_intermapper_up_response = {
            'body': 'KO',
            'status': 400
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_basic_info = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_tickets = CoroutineMock()
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_intermapper_up_note = CoroutineMock(return_value=append_intermapper_up_response)
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock(return_value=True)

        with config_mock:
            response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, parsed_email_dict)

        bruin_repository.get_ticket_basic_info.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.append_intermapper_up_note.assert_awaited_once_with(outage_ticket_1_id, circuit_id,
                                                                             parsed_email_dict, False)
        bruin_repository.get_tickets.assert_not_awaited()
        bruin_repository.get_ticket_details.assert_not_awaited()
        intermapper_monitor._was_last_outage_detected_recently.assert_not_called()
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable.assert_not_called()

        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()
        assert response is False

    @pytest.mark.asyncio
    async def autoresolve_ticket_failed_product_category_rpc_request_test(self):
        asset_id = 123
        client_id = 83959
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
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

        product_category_response = {
            'body': 'Failed RPC',
            'status': 400,
        }

        append_intermapper_up_response = {
            'body': 'OK',
            'status': 200
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_basic_info = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_tickets = CoroutineMock(return_value=product_category_response)
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_intermapper_up_note = CoroutineMock(return_value=append_intermapper_up_response)
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock()
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock()

        with config_mock:
            response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, parsed_email_dict)

        bruin_repository.get_ticket_basic_info.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.append_intermapper_up_note.assert_awaited_once_with(outage_ticket_1_id, circuit_id,
                                                                             parsed_email_dict, False)
        bruin_repository.get_tickets.assert_awaited_once_with(client_id, outage_ticket_1_id)
        bruin_repository.get_ticket_details.assert_not_awaited()
        intermapper_monitor._was_last_outage_detected_recently.assert_not_called()

        intermapper_monitor._is_outage_ticket_detail_auto_resolvable.assert_not_called()

        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()
        assert response is False

    @pytest.mark.asyncio
    async def autoresolve_ticket_no_product_category_test(self):
        asset_id = 123
        client_id = 83959
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
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

        product_category_response = {
            'body': [],
            'status': 200,
        }

        append_intermapper_up_response = {
            'body': 'OK',
            'status': 200
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_basic_info = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_tickets = CoroutineMock(return_value=product_category_response)
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_intermapper_up_note = CoroutineMock(return_value=append_intermapper_up_response)
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock()
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock()

        with config_mock:
            response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, parsed_email_dict)

        bruin_repository.get_ticket_basic_info.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.append_intermapper_up_note.assert_awaited_once_with(outage_ticket_1_id, circuit_id,
                                                                             parsed_email_dict, False)
        bruin_repository.get_tickets.assert_awaited_once_with(client_id, outage_ticket_1_id)
        bruin_repository.get_ticket_details.assert_not_awaited()
        intermapper_monitor._was_last_outage_detected_recently.assert_not_called()

        intermapper_monitor._is_outage_ticket_detail_auto_resolvable.assert_not_called()

        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()
        assert response is True

    @pytest.mark.asyncio
    async def autoresolve_ticket_product_category_not_in_list_test(self):
        asset_id = 123
        client_id = 83959
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
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

        append_intermapper_up_response = {
            'body': 'OK',
            'status': 200
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_basic_info = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_intermapper_up_note = CoroutineMock(return_value=append_intermapper_up_response)
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock()
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock()

        with config_mock:
            response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, parsed_email_dict)

        bruin_repository.get_ticket_basic_info.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.append_intermapper_up_note.assert_awaited_once_with(outage_ticket_1_id, circuit_id,
                                                                             parsed_email_dict, False)
        bruin_repository.get_tickets.assert_awaited_once_with(client_id, outage_ticket_1_id)
        bruin_repository.get_ticket_details.assert_not_awaited()
        intermapper_monitor._was_last_outage_detected_recently.assert_not_called()

        intermapper_monitor._is_outage_ticket_detail_auto_resolvable.assert_not_called()

        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()
        assert response is True

    @pytest.mark.asyncio
    async def autoresolve_ticket_failed_tickets_details_rpc_request_test(self):
        asset_id = 123
        client_id = 83959
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
        circuit_id = 3214

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": "POTS in a Box",
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

        append_intermapper_up_response = {
            'body': 'OK',
            'status': 200
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_basic_info = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_intermapper_up_note = CoroutineMock(return_value=append_intermapper_up_response)
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock()
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock()

        with config_mock:
            response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, parsed_email_dict)

        bruin_repository.get_ticket_basic_info.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.append_intermapper_up_note.assert_awaited_once_with(outage_ticket_1_id, circuit_id,
                                                                             parsed_email_dict, False)
        bruin_repository.get_tickets.assert_awaited_once_with(client_id, outage_ticket_1_id)
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
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
        circuit_id = 3214

        serial_number_2 = 'VC9999999'

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": "POTS in a Box",
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

        append_intermapper_up_response = {
            'body': 'OK',
            'status': 200
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_basic_info = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_outage_ticket_response)
        bruin_repository.append_intermapper_up_note = CoroutineMock(return_value=append_intermapper_up_response)
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock(return_value=False)
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock(return_value=True)

        with config_mock:
            response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, parsed_email_dict)

        bruin_repository.get_ticket_basic_info.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.append_intermapper_up_note.assert_awaited_once_with(outage_ticket_1_id, circuit_id,
                                                                             parsed_email_dict, False)
        bruin_repository.get_tickets.assert_awaited_once_with(client_id, outage_ticket_1_id)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        intermapper_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date, parsed_email_dict
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
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
        circuit_id = 3214

        serial_number_2 = 'VC9999999'

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": "POTS in a Box",
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

        append_intermapper_up_response = {
            'body': 'OK',
            'status': 200
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_basic_info = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_outage_ticket_response)
        bruin_repository.append_intermapper_up_note = CoroutineMock(return_value=append_intermapper_up_response)
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock(return_value=False)

        with config_mock:
            response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, parsed_email_dict)

        bruin_repository.get_ticket_basic_info.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.append_intermapper_up_note.assert_awaited_once_with(outage_ticket_1_id, circuit_id,
                                                                             parsed_email_dict, False)
        bruin_repository.get_tickets.assert_awaited_once_with(client_id, outage_ticket_1_id)

        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        intermapper_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date, parsed_email_dict
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
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            'version': '6.1.5',
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": "\t\tdefined(\"lcpu.avgBusy1\") && (lcpu.avgBusy1 > 90)",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds"
        }
        circuit_id = 3214

        serial_number_2 = 'VC9999999'

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": "POTS in a Box",
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

        unpause_ticket_detail_response = {
            'body': 'ok',
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

        append_intermapper_up_response = {
            'body': 'OK',
            'status': 200
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_basic_info = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.unpause_ticket_detail = CoroutineMock(return_value=unpause_ticket_detail_response)
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_outage_ticket_response)
        bruin_repository.append_intermapper_up_note = CoroutineMock(return_value=append_intermapper_up_response)
        bruin_repository.append_autoresolve_note = CoroutineMock()

        config = testconfig

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable = Mock(return_value=True)

        with config_mock:
            response = await intermapper_monitor._autoresolve_ticket(circuit_id, client_id, parsed_email_dict)

        bruin_repository.get_ticket_basic_info.assert_awaited_once_with(client_id, circuit_id)
        bruin_repository.append_intermapper_up_note.assert_awaited_once_with(outage_ticket_1_id, circuit_id,
                                                                             parsed_email_dict, False)
        bruin_repository.get_tickets.assert_awaited_once_with(client_id, outage_ticket_1_id)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        intermapper_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date, parsed_email_dict
        )
        intermapper_monitor._is_outage_ticket_detail_auto_resolvable.assert_called_once_with(
            relevant_notes_for_edge, circuit_id, max_autoresolves=3
        )

        bruin_repository.resolve_ticket.assert_awaited_once_with(outage_ticket_1_id, outage_ticket_detail_1_id)
        bruin_repository.append_autoresolve_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()
        assert response is False

    @pytest.mark.asyncio
    async def get_dri_parameters_test(self):
        circuit_id = 3214
        client_id = 83959

        dri_parameters_response_body = {
                    "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei": "864839040023968",
                    "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers": "ATT",
                    "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid": "89014103272191198072",
                    "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert": "SIM1 Active",
                    "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum": "15245139487",
                    "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress": "8C:3:30:69"
                }
        dri_parameters_response = {
                'body': dri_parameters_response_body,
                'status': 200
         }

        attribute_serial = "705286"
        attribute_serial_response = {
            "body": attribute_serial,
            "status": 200
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_attributes_serial = CoroutineMock(return_value=attribute_serial_response)

        dri_repository = Mock()
        dri_repository.get_dri_parameters = CoroutineMock(return_value=dri_parameters_response)

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        dri_parameters = await intermapper_monitor._get_dri_parameters(circuit_id, client_id)
        bruin_repository.get_attributes_serial.assert_awaited_once_with(circuit_id, client_id)
        dri_repository.get_dri_parameters.assert_awaited_once_with(attribute_serial)
        assert dri_parameters == dri_parameters_response_body

    @pytest.mark.asyncio
    async def get_dri_parameters_failed_attributes_serial_rpc_request_test(self):
        circuit_id = 3214
        client_id = 83959

        attribute_serial = "Failed"
        attribute_serial_response = {
            "body": attribute_serial,
            "status": 400
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_attributes_serial = CoroutineMock(return_value=attribute_serial_response)

        dri_repository = Mock()
        dri_repository.get_dri_parameters = CoroutineMock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        dri_parameters = await intermapper_monitor._get_dri_parameters(circuit_id, client_id)
        bruin_repository.get_attributes_serial.assert_awaited_once_with(circuit_id, client_id)
        dri_repository.get_dri_parameters.assert_not_awaited()
        assert dri_parameters is None

    @pytest.mark.asyncio
    async def get_dri_parameters_none_attribute_test(self):
        circuit_id = 3214
        client_id = 83959

        dri_parameters_response_body = {
                    "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei": "864839040023968",
                    "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers": "ATT",
                    "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid": "89014103272191198072",
                    "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert": "SIM1 Active",
                    "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum": "15245139487",
                    "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress": "8C:3:30:69"
                }
        dri_parameters_response = {
                'body': dri_parameters_response_body,
                'status': 200
         }

        attribute_serial = None
        attribute_serial_response = {
            "body": attribute_serial,
            "status": 200
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_attributes_serial = CoroutineMock(return_value=attribute_serial_response)

        dri_repository = Mock()
        dri_repository.get_dri_parameters = CoroutineMock(return_value=dri_parameters_response)

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        dri_parameters = await intermapper_monitor._get_dri_parameters(circuit_id, client_id)
        bruin_repository.get_attributes_serial.assert_awaited_once_with(circuit_id, client_id)
        dri_repository.get_dri_parameters.assert_not_awaited()
        assert dri_parameters is None

    @pytest.mark.asyncio
    async def get_dri_parameters_failed_dri_parameters_rpc_request_test(self):
        circuit_id = 3214
        client_id = 83959

        attribute_serial = "705286"
        attribute_serial_response = {
            "body": attribute_serial,
            "status": 200
        }

        dri_parameters_response_body = f"DRI task was rejected for serial {attribute_serial}"
        dri_parameters_response = {
            'body': dri_parameters_response_body,
            'status': 403
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_attributes_serial = CoroutineMock(return_value=attribute_serial_response)

        dri_repository = Mock()
        dri_repository.get_dri_parameters = CoroutineMock(return_value=dri_parameters_response)

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        dri_parameters = await intermapper_monitor._get_dri_parameters(circuit_id, client_id)
        bruin_repository.get_attributes_serial.assert_awaited_once_with(circuit_id, client_id)
        dri_repository.get_dri_parameters.assert_awaited_once_with(attribute_serial)
        assert dri_parameters is None

    def last_outage_detected_recently_with_no_reopen_note_or_no_triage_test(self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        ticket_notes = []
        parsed_email_dict = {'name': ''}

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()
        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._get_max_seconds_since_last_outage = Mock(return_value=3600)
        datetime_mock = Mock()

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date,
                                                                            parsed_email_dict)
            assert result is True

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date,
                                                                            parsed_email_dict)
            assert result is True

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date,
                                                                            parsed_email_dict)
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

        parsed_email_dict = {'name': ''}

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()
        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._get_max_seconds_since_last_outage = Mock(return_value=3600)
        datetime_mock = Mock()

        new_now = parse(reopen_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date,
                                                                            parsed_email_dict)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date,
                                                                            parsed_email_dict)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date,
                                                                            parsed_email_dict)
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

        parsed_email_dict = {'name': ''}

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()
        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._get_max_seconds_since_last_outage = Mock(return_value=3600)
        datetime_mock = Mock()

        new_now = parse(triage_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date,
                                                                            parsed_email_dict)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date,
                                                                            parsed_email_dict)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            result = intermapper_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date,
                                                                            parsed_email_dict)
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
        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
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

    @pytest.mark.asyncio
    async def mark_email_as_read_test(self):
        msg_uid = 123

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        bruin_repository = Mock()
        config = testconfig

        response = {
            'body': None,
            'status': 204
        }

        notifications_repository = Mock()
        notifications_repository.mark_email_as_read = CoroutineMock(return_value=response)

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        await intermapper_monitor._mark_email_as_read(msg_uid)

        intermapper_monitor._notifications_repository.mark_email_as_read.assert_awaited_once_with(msg_uid)
        intermapper_monitor._logger.error.assert_not_called()

    @pytest.mark.asyncio
    async def mark_email_as_read_non_2xx_test(self):
        msg_uid = 123

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        bruin_repository = Mock()
        config = testconfig

        response = {
            'body': None,
            'status': 400
        }

        notifications_repository = Mock()
        notifications_repository.mark_email_as_read = CoroutineMock(return_value=response)

        dri_repository = Mock()

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        await intermapper_monitor._mark_email_as_read(msg_uid)

        intermapper_monitor._notifications_repository.mark_email_as_read.assert_awaited_once_with(msg_uid)
        intermapper_monitor._logger.error.assert_called_once()

    def get_tz_offset_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        dri_repository = Mock()
        config = testconfig

        datetime_mock = Mock()
        datetime_mock.now.side_effect = lambda tz: tz.localize(datetime.now().replace(month=1))

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)
        intermapper_monitor._zip_db.get = Mock()

        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            intermapper_monitor._get_tz_offset('1 Infinite Loop, Cupertino, CA')
            intermapper_monitor._zip_db.get.assert_not_called()

            intermapper_monitor._get_tz_offset('1 Infinite Loop, Cupertino, CA 95014')
            intermapper_monitor._zip_db.get.assert_called_once_with('95014')

    def get_max_seconds_since_last_outage_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        dri_repository = Mock()
        config = testconfig

        intermapper_monitor = InterMapperMonitor(event_bus, logger, scheduler, config, notifications_repository,
                                                 bruin_repository, dri_repository)

        tz_offset = 0

        day_schedule = testconfig.INTERMAPPER_CONFIG['autoresolve']['day_schedule']
        last_outage_seconds = testconfig.INTERMAPPER_CONFIG['autoresolve']['last_outage_seconds']

        current_datetime = datetime.now().replace(hour=10)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        with patch.object(intermapper_monitor_module, 'datetime', new=datetime_mock):
            with patch.dict(day_schedule, start_hour=6, end_hour=22):
                result = intermapper_monitor._get_max_seconds_since_last_outage(tz_offset)
                assert result == last_outage_seconds['day']

            with patch.dict(day_schedule, start_hour=8, end_hour=0):
                result = intermapper_monitor._get_max_seconds_since_last_outage(tz_offset)
                assert result == last_outage_seconds['day']

            with patch.dict(day_schedule, start_hour=10, end_hour=2):
                result = intermapper_monitor._get_max_seconds_since_last_outage(tz_offset)
                assert result == last_outage_seconds['day']

            with patch.dict(day_schedule, start_hour=12, end_hour=4):
                result = intermapper_monitor._get_max_seconds_since_last_outage(tz_offset)
                assert result == last_outage_seconds['night']

            with patch.dict(day_schedule, start_hour=2, end_hour=8):
                result = intermapper_monitor._get_max_seconds_since_last_outage(tz_offset)
                assert result == last_outage_seconds['night']
