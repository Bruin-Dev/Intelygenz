import os

from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from typing import Generator
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest

from apscheduler.util import undefined
from asynctest import CoroutineMock
from pytz import timezone
from shortuuid import uuid

from application.actions.cts_dispatch_monitor import CtsDispatchMonitor
from application.actions import cts_dispatch_monitor as cts_dispatch_monitor_module

from application.repositories.cts_repository import CtsRepository

from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms, \
    cts_get_tech_24_hours_before_sms, cts_get_tech_2_hours_before_sms

from application.repositories.utils_repository import UtilsRepository

from application.templates.cts.sms.tech_on_site import cts_get_tech_on_site_sms

from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_note, \
    cts_get_dispatch_confirmed_sms_note
from config import testconfig


uuid_ = uuid()
uuid_mock = patch.object(cts_dispatch_monitor_module, 'uuid', return_value=uuid_)


class TestLitDispatchMonitor:

    def instance_test(self):
        redis_client = Mock()
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        cts_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()

        cts_dispatch_monitor = CtsDispatchMonitor(config, redis_client, event_bus, scheduler, logger,
                                                  cts_repository, bruin_repository, notifications_repository)

        assert cts_dispatch_monitor._redis_client is redis_client
        assert cts_dispatch_monitor._event_bus is event_bus
        assert cts_dispatch_monitor._logger is logger
        assert cts_dispatch_monitor._scheduler is scheduler
        assert cts_dispatch_monitor._config is config
        assert cts_dispatch_monitor._cts_repository is cts_repository
        assert cts_dispatch_monitor._bruin_repository is bruin_repository
        assert cts_dispatch_monitor._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def start_dispatch_monitor_job_with_exec_on_start_test(self, cts_dispatch_monitor):
        config = testconfig

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(cts_dispatch_monitor_module, 'datetime', new=datetime_mock):
            with patch.object(cts_dispatch_monitor_module, 'timezone', new=Mock()):
                await cts_dispatch_monitor.start_monitoring_job(exec_on_start=True)

        cts_dispatch_monitor._scheduler.add_job.assert_called_once_with(
            cts_dispatch_monitor._cts_dispatch_monitoring_process, 'interval',
            minutes=config.DISPATCH_MONITOR_CONFIG["jobs_intervals"]["cts_dispatch_monitor"],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_service_dispatch_monitor_cts_process',
        )

    @pytest.mark.asyncio
    async def start_dispatch_monitor_job_with_no_exec_on_start_test(self, cts_dispatch_monitor):
        config = testconfig

        await cts_dispatch_monitor.start_monitoring_job(exec_on_start=False)

        cts_dispatch_monitor._scheduler.add_job.assert_called_once_with(
            cts_dispatch_monitor._cts_dispatch_monitoring_process, 'interval',
            minutes=config.DISPATCH_MONITOR_CONFIG["jobs_intervals"]["cts_dispatch_monitor"],
            next_run_time=undefined,
            replace_existing=False,
            id='_service_dispatch_monitor_cts_process',
        )

    def is_dispatch_confirmed_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_not_confirmed):
        assert cts_dispatch_monitor._is_dispatch_confirmed(cts_dispatch_confirmed) is True
        assert cts_dispatch_monitor._is_dispatch_confirmed(cts_dispatch_not_confirmed) is False

    def is_tech_on_site_test(self, cts_dispatch_monitor, cts_dispatch_tech_on_site, cts_dispatch_tech_not_on_site):
        assert cts_dispatch_monitor._is_tech_on_site(cts_dispatch_tech_on_site) is True
        assert cts_dispatch_monitor._is_tech_on_site(cts_dispatch_tech_not_on_site) is False

    def get_dispatches_splitted_by_status_test(self, cts_dispatch_monitor, cts_dispatch, cts_dispatch_confirmed,
                                               cts_dispatch_confirmed_2, cts_dispatch_tech_on_site,
                                               cts_bad_status_dispatch):
        dispatches = [
            cts_dispatch, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_dispatch_tech_on_site, cts_bad_status_dispatch
        ]
        expected_dispatches_splitted = {
            str(cts_dispatch_monitor.DISPATCH_REQUESTED): [cts_dispatch],
            str(cts_dispatch_monitor.DISPATCH_CONFIRMED): [cts_dispatch_confirmed, cts_dispatch_confirmed_2],
            str(cts_dispatch_monitor.DISPATCH_FIELD_ENGINEER_ON_SITE): [cts_dispatch_tech_on_site],
            str(cts_dispatch_monitor.DISPATCH_REPAIR_COMPLETED): [],
            str(cts_dispatch_monitor.DISPATCH_REPAIR_COMPLETED_PENDING_COLLATERAL): []
        }
        assert cts_dispatch_monitor._get_dispatches_splitted_by_status(dispatches) == expected_dispatches_splitted

    @pytest.mark.asyncio
    async def cts_dispatch_monitoring_process_test(self, cts_dispatch_monitor, cts_dispatch, cts_dispatch_confirmed):
        dispatches = [cts_dispatch, cts_dispatch_confirmed]
        dispatches_response = {
            'status': 200,
            'body': {
                'done': True,
                'records': []
            }
        }
        splitted_dispatches = {}
        for ds in cts_dispatch_monitor._dispatch_statuses:
            splitted_dispatches[ds] = []
        splitted_dispatches[str(cts_dispatch_monitor.DISPATCH_REQUESTED)] = [cts_dispatch]
        splitted_dispatches[str(cts_dispatch_monitor.DISPATCH_CONFIRMED)] = [cts_dispatch_confirmed]

        confirmed_dispatches = [cts_dispatch_confirmed]
        cts_dispatch_monitor._cts_repository.get_all_dispatches = CoroutineMock(return_value=dispatches_response)
        cts_dispatch_monitor._get_dispatches_splitted_by_status = Mock(return_value=splitted_dispatches)
        cts_dispatch_monitor._monitor_confirmed_dispatches = CoroutineMock()

        await cts_dispatch_monitor._cts_dispatch_monitoring_process()

        cts_dispatch_monitor._monitor_confirmed_dispatches.assert_awaited_once()
        cts_dispatch_monitor._monitor_confirmed_dispatches.assert_awaited_with(confirmed_dispatches)

    @pytest.mark.asyncio
    async def cts_dispatch_monitoring_process_error_exception_test(
            self, cts_dispatch_monitor):
        cts_dispatch_monitor._cts_dispatch_monitoring_process = CoroutineMock(side_effect=Exception)
        cts_dispatch_monitor._monitor_confirmed_dispatches = CoroutineMock(side_effect=Exception)
        cts_dispatch_monitor._cts_repository.get_all_dispatches = CoroutineMock(side_effect=Exception)
        cts_dispatch_monitor._get_dispatches_splitted_by_status = CoroutineMock()
        with pytest.raises(Exception):
            await cts_dispatch_monitor._cts_dispatch_monitoring_process()
            cts_dispatch_monitor._logger.error.assert_called_once()
            cts_dispatch_monitor._get_dispatches_splitted_by_status.assert_not_awaited()
            cts_dispatch_monitor._monitor_confirmed_dispatches.assert_not_awaited()

    @pytest.mark.asyncio
    async def cts_dispatch_monitoring_process_error_getting_dispatches_test(
            self, cts_dispatch_monitor, cts_dispatch, cts_dispatch_confirmed):
        dispatches = [cts_dispatch, cts_dispatch_confirmed]
        dispatches_response = {
            'status': 400,
            'body': {
                'done': False,
                'records': []
            }
        }
        err_msg = f'An error occurred retrieving all dispatches in the request status from CTS.'
        cts_dispatch_monitor._cts_repository.get_all_dispatches = CoroutineMock(return_value=dispatches_response)
        cts_dispatch_monitor._monitor_confirmed_dispatches = CoroutineMock()
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._cts_dispatch_monitoring_process()

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)
        cts_dispatch_monitor._monitor_confirmed_dispatches.assert_not_awaited()

    @pytest.mark.asyncio
    async def cts_dispatch_monitoring_process_error_getting_dispatches_invalid_body_test(
            self, cts_dispatch_monitor, cts_dispatch, cts_dispatch_confirmed):
        dispatches = [cts_dispatch, cts_dispatch_confirmed]
        dispatches_response = {
            'status': 200,
            'body': {
                'done': False,
                'INVALID_BODY': []
            }
        }
        err_msg = f'An error occurred retrieving all dispatches from CTS.'

        cts_dispatch_monitor._cts_repository.get_all_dispatches = CoroutineMock(return_value=dispatches_response)
        cts_dispatch_monitor._monitor_confirmed_dispatches = CoroutineMock()
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._cts_dispatch_monitoring_process()

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)
        cts_dispatch_monitor._monitor_confirmed_dispatches.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_confirmed_note_test(self, cts_dispatch_monitor, cts_dispatch_confirmed):
        ticket_id = cts_dispatch_confirmed['Ext_Ref_Num__c']
        dispatch_number = cts_dispatch_confirmed['Name']

        note_data = {
            'vendor': 'CTS',
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'tech_name': cts_dispatch_confirmed.get('API_Resource_Name__c'),
            'tech_phone': cts_dispatch_confirmed.get('Resource_Phone_Number__c')
        }
        note = cts_get_dispatch_confirmed_note(note_data)
        response_append_note_to_ticket_mock = {
            'body': '',
            'status': 200
        }
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_to_ticket_mock])
        response = await cts_dispatch_monitor._append_confirmed_note(dispatch_number, ticket_id, cts_dispatch_confirmed)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, note)
        assert response is True

    @pytest.mark.asyncio
    async def append_confirmed_note_error_test(self, cts_dispatch_monitor, cts_dispatch_confirmed):
        ticket_id = cts_dispatch_confirmed['Ext_Ref_Num__c']
        dispatch_number = cts_dispatch_confirmed['Name']

        note_data = {
            'vendor': 'CTS',
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'tech_name': cts_dispatch_confirmed.get('API_Resource_Name__c'),
            'tech_phone': cts_dispatch_confirmed.get('Resource_Phone_Number__c')
        }
        note = cts_get_dispatch_confirmed_note(note_data)
        response_append_note_to_ticket_mock = {
            'body': '',
            'status': 400
        }
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_to_ticket_mock])
        err_msg = f'An error occurred when appending a confirmed note with bruin client. ' \
                  f'Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - payload: {note_data}'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._append_confirmed_note(dispatch_number, ticket_id, cts_dispatch_confirmed)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)
        assert response is False

    @pytest.mark.asyncio
    async def append_confirmed_sms_note_test(self, cts_dispatch_monitor, cts_dispatch_confirmed):
        ticket_id = cts_dispatch_confirmed['Ext_Ref_Num__c']
        dispatch_number = cts_dispatch_confirmed['Name']
        sms_to = '+16666666666'
        sms_note_data = {
            'phone_number': sms_to
        }
        sms_note = cts_get_dispatch_confirmed_sms_note(sms_note_data)
        response_append_note_to_ticket_mock = {
            'body': '',
            'status': 200
        }
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_to_ticket_mock])
        response = await cts_dispatch_monitor._append_confirmed_sms_note(dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_confirmed_sms_note_error_test(self, cts_dispatch_monitor, cts_dispatch_confirmed):
        ticket_id = cts_dispatch_confirmed['Ext_Ref_Num__c']
        dispatch_number = cts_dispatch_confirmed['Name']

        sms_to = '+16666666666'
        sms_note_data = {
            'phone_number': sms_to
        }
        sms_note = cts_get_dispatch_confirmed_sms_note(sms_note_data)
        response_append_note_to_ticket_mock = {
            'body': '',
            'status': 400
        }
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_to_ticket_mock])
        err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                  f"- SMS Confirmed note not appended"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._append_confirmed_sms_note(dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)
        assert response is False

    @pytest.mark.asyncio
    async def append_tech_24_sms_note_test(self, cts_dispatch_monitor, cts_dispatch, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch.get('Name')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = '#*Automation Engine*#\nDispatch 24h prior reminder SMS sent to +1987654327\n'
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await cts_dispatch_monitor._append_tech_24_sms_note(dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_tech_24_sms_note_error_test(self, cts_dispatch_monitor, cts_dispatch, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch.get('Name')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = '#*Automation Engine*#\nDispatch 24h prior reminder SMS sent to +1987654327\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS tech 24 hours note not appended'

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._append_tech_24_sms_note(dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_tech_2_sms_note_test(self, cts_dispatch_monitor, cts_dispatch, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch.get('Name')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = '#*Automation Engine*#\nDispatch 2h prior reminder SMS sent to +1987654327\n'
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await cts_dispatch_monitor._append_tech_2_sms_note(dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_tech_2_sms_note_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = '#*Automation Engine*#\nDispatch 2h prior reminder SMS sent to +1987654327\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS tech 2 hours note not appended'

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._append_tech_2_sms_note(dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_tech_on_site_sms_note_test(self, cts_dispatch_monitor, cts_dispatch_confirmed,
                                                append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = '#*Automation Engine*#\nDispatch Management - Field Engineer On Site\n\n' \
                   'Michael J. Fox has arrived\n'
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await cts_dispatch_monitor._append_tech_on_site_sms_note(
            dispatch_number, ticket_id, sms_to, cts_dispatch_confirmed.get('API_Resource_Name__c'))

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_tech_on_site_sms_note_error_test(self, cts_dispatch_monitor, cts_dispatch_confirmed,
                                                      append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = '#*Automation Engine*#\nDispatch Management - Field Engineer On Site\n\n' \
                   'Michael J. Fox has arrived\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS tech on site note not appended'

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._append_tech_on_site_sms_note(
            dispatch_number, ticket_id, sms_to, cts_dispatch_confirmed.get('API_Resource_Name__c'))

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def send_confirmed_sms_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'phone_number': sms_to
        }

        sms_data = cts_get_dispatch_confirmed_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        request = {
            'request_id': uuid_,
            'body': sms_payload,
        }
        response = {
            'request_id': uuid_,
            'body': 'Got internal error from LIT',
            'status': 500,
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await cts_dispatch_monitor._send_confirmed_sms(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_confirmed_sms_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        sms_to = None

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._send_confirmed_sms(dispatch_number, ticket_id, updated_dispatch, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_confirmed_sms_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        # sms_to = dispatch.get('Job_Site_Contact_Name_and_Phone_Number')
        # sms_to = LitRepository.get_sms_to(dispatch)
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'phone_number': sms_to
        }

        sms_data = cts_get_dispatch_confirmed_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        request = {
            'request_id': uuid_,
            'body': sms_payload,
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 400
        }

        send_error_sms_to_slack_response = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                           f'An error occurred when sending Confirmed SMS with notifier client. ' \
                                           f'payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._send_confirmed_sms(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_tech_24_sms_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_24_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await cts_dispatch_monitor._send_tech_24_sms(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_tech_24_sms_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        sms_to = None

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._send_tech_24_sms(dispatch_number, ticket_id, updated_dispatch, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_tech_24_sms_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_24_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 400
        }

        send_error_sms_to_slack_response = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                           f'An error occurred when sending a tech 24 hours SMS with notifier ' \
                                           f'client. ' \
                                           f'payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._send_tech_24_sms(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_tech_2_sms_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_2_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await cts_dispatch_monitor._send_tech_2_sms(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_tech_2_sms_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        sms_to = None

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._send_tech_2_sms(dispatch_number, ticket_id, updated_dispatch, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_tech_2_sms_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        # sms_to = dispatch.get('Job_Site_Contact_Name_and_Phone_Number')
        # sms_to = LitRepository.get_sms_to(dispatch)
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_2_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 400
        }

        send_error_sms_to_slack_response = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                           f'An error occurred when sending a tech 2 hours SMS with notifier client. ' \
                                           f'payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._send_tech_2_sms(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_tech_on_site_sms_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        sms_data_payload = {
            'field_engineer_name': cts_dispatch_confirmed.get('API_Resource_Name__c')
        }

        sms_data = cts_get_tech_on_site_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await cts_dispatch_monitor._send_tech_on_site_sms(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_tech_on_site_sms_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        sms_to = None

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._send_tech_on_site_sms(dispatch_number, ticket_id, updated_dispatch,
                                                                     sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_tech_on_site_sms_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        # sms_to = dispatch.get('Job_Site_Contact_Name_and_Phone_Number')
        # sms_to = LitRepository.get_sms_to(dispatch)
        sms_to = '+1987654327'
        sms_data_payload = {
            'field_engineer_name': cts_dispatch_confirmed.get('API_Resource_Name__c')
        }

        sms_data = cts_get_tech_on_site_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 400
        }

        send_error_sms_to_slack_response = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                           f'An error occurred when sending a tech on site SMS with notifier client. ' \
                                           f'payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._send_tech_on_site_sms(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
