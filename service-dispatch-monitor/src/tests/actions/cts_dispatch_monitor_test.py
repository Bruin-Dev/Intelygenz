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
from application.repositories.utils_repository import UtilsRepository

from application.repositories.cts_repository import CtsRepository

from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_sms_tech_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_sms_note

from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_12_hours_before_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_2_hours_before_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms_tech
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_12_hours_before_sms_tech
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_2_hours_before_sms_tech
from application.templates.cts.sms.tech_on_site import cts_get_tech_on_site_sms

from config import testconfig


uuid_ = uuid()
uuid_mock = patch.object(cts_dispatch_monitor_module, 'uuid', return_value=uuid_)


class TestCtsDispatchMonitor:

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
    async def append_confirmed_sms_tech_note_test(self, cts_dispatch_monitor, cts_dispatch_confirmed):
        ticket_id = cts_dispatch_confirmed['Ext_Ref_Num__c']
        dispatch_number = cts_dispatch_confirmed['Name']
        sms_to = '+16666666666'
        sms_note_data = {
            'phone_number': sms_to
        }
        sms_note = cts_get_dispatch_confirmed_sms_tech_note(sms_note_data)
        response_append_note_to_ticket_mock = {
            'body': '',
            'status': 200
        }
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_to_ticket_mock])
        response = await cts_dispatch_monitor._append_confirmed_sms_tech_note(dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_confirmed_sms_tech_note_error_test(self, cts_dispatch_monitor, cts_dispatch_confirmed):
        ticket_id = cts_dispatch_confirmed['Ext_Ref_Num__c']
        dispatch_number = cts_dispatch_confirmed['Name']

        sms_to = '+16666666666'
        sms_note_data = {
            'phone_number': sms_to
        }
        sms_note = cts_get_dispatch_confirmed_sms_tech_note(sms_note_data)
        response_append_note_to_ticket_mock = {
            'body': '',
            'status': 400
        }
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_to_ticket_mock])
        err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                  f"- Tech SMS Confirmed note not appended"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._append_confirmed_sms_tech_note(dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)
        assert response is False

    @pytest.mark.asyncio
    async def append_tech_12_sms_note_test(self, cts_dispatch_monitor, cts_dispatch, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch.get('Name')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = '#*Automation Engine*#\nDispatch 12h prior reminder SMS sent to +1987654327\n'
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await cts_dispatch_monitor._append_tech_12_sms_note(dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_tech_12_sms_note_error_test(self, cts_dispatch_monitor, cts_dispatch, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch.get('Name')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = '#*Automation Engine*#\nDispatch 12h prior reminder SMS sent to +1987654327\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS 12 hours note not appended'

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._append_tech_12_sms_note(dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_tech_12_sms_tech_note_test(self, cts_dispatch_monitor, cts_dispatch, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch.get('Name')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = '#*Automation Engine*#\nDispatch 12h prior reminder tech SMS sent to +1987654327\n'
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await cts_dispatch_monitor._append_tech_12_sms_tech_note(dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_tech_12_sms_tech_note_error_test(self, cts_dispatch_monitor, cts_dispatch, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch.get('Name')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = '#*Automation Engine*#\nDispatch 12h prior reminder tech SMS sent to +1987654327\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS tech 12 hours note not appended'

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._append_tech_12_sms_tech_note(dispatch_number, ticket_id, sms_to)

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
                                           f'- SMS 2 hours note not appended'

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._append_tech_2_sms_note(dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_tech_2_sms_tech_note_test(self, cts_dispatch_monitor, cts_dispatch, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch.get('Name')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = '#*Automation Engine*#\nDispatch 2h prior reminder tech SMS sent to +1987654327\n'
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await cts_dispatch_monitor._append_tech_2_sms_tech_note(dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_tech_2_sms_tech_note_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = '#*Automation Engine*#\nDispatch 2h prior reminder tech SMS sent to +1987654327\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS tech 2 hours note not appended'

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._append_tech_2_sms_tech_note(dispatch_number, ticket_id, sms_to)

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
    async def send_confirmed_sms_tech_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+12123595129'
        sms_data_payload = {
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'phone_number': sms_to
        }

        sms_data = cts_get_dispatch_confirmed_sms_tech(sms_data_payload)

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

        response = await cts_dispatch_monitor._send_confirmed_sms_tech(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_confirmed_sms_tech_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        sms_to = None

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._send_confirmed_sms_tech(
            dispatch_number, ticket_id, updated_dispatch, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_confirmed_sms_tech_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+12123595129'
        sms_data_payload = {
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'phone_number': sms_to
        }

        sms_data = cts_get_dispatch_confirmed_sms_tech(sms_data_payload)

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
                                           f'An error occurred when sending Confirmed SMS tech ' \
                                           f'with notifier client. payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._send_confirmed_sms_tech(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_tech_12_sms_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_12_hours_before_sms(sms_data_payload)

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

        response = await cts_dispatch_monitor._send_tech_12_sms(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_tech_12_sms_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        sms_to = None

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._send_tech_12_sms(dispatch_number, ticket_id, updated_dispatch, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_tech_12_sms_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_12_hours_before_sms(sms_data_payload)

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
                                           f'An error occurred when sending a tech 12 hours SMS with notifier ' \
                                           f'client. ' \
                                           f'payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._send_tech_12_sms(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_tech_12_sms_tech_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+12123595129'
        sms_data_payload = {
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_12_hours_before_sms_tech(sms_data_payload)

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

        response = await cts_dispatch_monitor._send_tech_12_sms_tech(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_tech_12_sms_tech_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        sms_to = None

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._send_tech_12_sms_tech(
            dispatch_number, ticket_id, updated_dispatch, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_tech_12_sms_tech_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+12123595129'
        sms_data_payload = {
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_12_hours_before_sms_tech(sms_data_payload)

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
                                           f'An error occurred when sending a tech 12 hours SMS tech ' \
                                           f'with notifier client. payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._send_tech_12_sms_tech(
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
    async def send_tech_2_sms_tech_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_2_hours_before_sms_tech(sms_data_payload)

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

        response = await cts_dispatch_monitor._send_tech_2_sms_tech(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_tech_2_sms_tech_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        sms_to = None

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._send_tech_2_sms_tech(
            dispatch_number, ticket_id, updated_dispatch, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_tech_2_sms_tech_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')

        sms_to = '+12123595129'
        sms_data_payload = {
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_2_hours_before_sms_tech(sms_data_payload)

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
                                           f'An error occurred when sending a tech 2 hours SMS tech ' \
                                           f'with notifier client. payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._send_tech_2_sms_tech(
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

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_test(self, cts_dispatch_monitor, cts_dispatch_confirmed,
                                                cts_dispatch_confirmed_2, ticket_details_1, ticket_details_2,
                                                append_note_response, append_note_response_2,
                                                sms_success_response, sms_success_response_2):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        response_append_note_2 = {
            'request_id': uuid_,
            'body': append_note_response_2,
            'status': 200
        }

        response_sms_note_1 = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }
        response_sms_note_2 = {
            'request_id': uuid_,
            'body': sms_success_response_2,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723610\n'
        sms_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723611\n'
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'
        sms_tech_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')

        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'
        confirmed_note_2 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_2}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'

        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        sms_data = ''

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_2,
            response_append_note_1,
            response_append_note_2,
            response_append_note_1,
            response_append_note_2,
            response_append_note_1,
            response_append_note_2
        ]
        responses_confirmed_sms = [
            True,
            True,
            True
        ]
        responses_confirmed_sms_tech = [
            True,
            True,
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_confirmed_sms_tech = CoroutineMock(side_effect=responses_confirmed_sms_tech)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1),
            call(ticket_id_2, confirmed_note_2),
            call(ticket_id_2, sms_note_2),
            call(ticket_id_2, sms_tech_note_2)
        ])

        cts_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2)
        ])
        cts_dispatch_monitor._send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_tech_sms_not_sended_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            ticket_details_1, ticket_details_2, append_note_response, append_note_response_2,
            sms_success_response, sms_success_response_2):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        response_append_note_2 = {
            'request_id': uuid_,
            'body': append_note_response_2,
            'status': 200
        }

        response_sms_note_1 = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }
        response_sms_note_2 = {
            'request_id': uuid_,
            'body': sms_success_response_2,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723610\n'
        sms_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723611\n'
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'
        sms_tech_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')

        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'
        confirmed_note_2 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_2}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'

        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        sms_data = ''

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_2,
            response_append_note_1,
            response_append_note_2,
            response_append_note_1,
            response_append_note_2,
            response_append_note_1,
            response_append_note_2
        ]
        responses_confirmed_sms = [
            True,
            True,
            True
        ]
        responses_confirmed_sms_tech = [
            True,
            False,
            False
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_confirmed_sms_tech = CoroutineMock(side_effect=responses_confirmed_sms_tech)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1),
            call(ticket_id_2, confirmed_note_2),
            call(ticket_id_2, sms_note_2),
            # call(ticket_id_2, sms_tech_note_2)
        ])

        cts_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2)
        ])
        cts_dispatch_monitor._send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech),
            # call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_tech_sms_tech_note_not_appended_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            ticket_details_1, ticket_details_2, append_note_response, append_note_response_2,
            sms_success_response, sms_success_response_2):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        response_append_note_2 = {
            'request_id': uuid_,
            'body': append_note_response_2,
            'status': 200
        }

        response_append_note_2_err = {
            'request_id': uuid_,
            'body': append_note_response_2,
            'status': 400
        }

        response_sms_note_1 = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }
        response_sms_note_2 = {
            'request_id': uuid_,
            'body': sms_success_response_2,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723610\n'
        sms_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723611\n'
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'
        sms_tech_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')

        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'
        confirmed_note_2 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_2}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'

        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        sms_data = ''

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_2,
            response_append_note_1,
            response_append_note_2,
            response_append_note_1,
            response_append_note_2_err,
            response_append_note_2,
            response_append_note_2
        ]
        responses_confirmed_sms = [
            True,
            True,
            True
        ]

        responses_confirmed_sms_tech = [
            True,
            True
        ]

        err_msg = f"Dispatch: {dispatch_number_2} Ticket_id: {ticket_id_2} Note: `{sms_tech_note_2}` " \
                  f"- Tech SMS Confirmed note not appended"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_confirmed_sms_tech = CoroutineMock(side_effect=responses_confirmed_sms_tech)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1),
            call(ticket_id_2, confirmed_note_2),
            call(ticket_id_2, sms_note_2),
            # call(ticket_id_2, sms_tech_note_2)
        ])

        cts_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2)
        ])
        cts_dispatch_monitor._send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2_tech)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_general_exception_test(self, cts_dispatch_monitor):
        confirmed_dispatches = 0  # Non valid list for filter
        err_msg = f"Error: _monitor_confirmed_dispatches - object of type 'int' has no len()"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches)

        cts_dispatch_monitor._logger.error.assert_called_once()
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_exception_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_skipped_datetime):
        dispatch_number = cts_dispatch_confirmed_skipped_datetime.get('Name')
        ticket_id = cts_dispatch_confirmed_skipped_datetime.get('Ext_Ref_Num__c')
        cts_dispatch_confirmed_skipped_datetime['Local_Site_Time__c'] = None
        confirmed_dispatches = [
            cts_dispatch_confirmed_skipped_datetime
        ]
        err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                  f"An error occurred retrieve datetime of dispatch: " \
                  f"{cts_dispatch_confirmed_skipped_datetime.get('Local_Site_Time__c')}"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches)

        cts_dispatch_monitor._logger.error.assert_called_once()
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_bad_datetime_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_bad_date):
        dispatch_number = cts_dispatch_confirmed_bad_date.get('Name')
        ticket_id = cts_dispatch_confirmed_bad_date.get('Ext_Ref_Num__c')
        cts_dispatch_confirmed_bad_date['Local_Site_Time__c'] = "BAD DATE FORMAT"
        confirmed_dispatches = [
            cts_dispatch_confirmed_bad_date
        ]
        err_msg = f"Error: Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                  f"- {cts_dispatch_confirmed_bad_date}"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches)

        cts_dispatch_monitor._logger.error.assert_called_once()
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skipping_one_invalid_ticket_id_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_skipped, ticket_details_1,
            append_note_response):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_skipped
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_1,
            response_append_note_1
        ]
        responses_confirmed_sms = [
            True
        ]
        responses_confirmed_sms_tech = [
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_confirmed_sms_tech = CoroutineMock(side_effect=responses_confirmed_sms_tech)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1)
        ])

        cts_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to)
        ])
        cts_dispatch_monitor._send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skipping_one_invalid_datetime_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_skipped_datetime,
            ticket_details_1, append_note_response):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_skipped_datetime
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_skipped_datetime.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_skipped_datetime.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_skipped_datetime.get('Local_Site_Time__c')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_1,
            response_append_note_1
        ]
        responses_confirmed_sms = [
            True
        ]
        responses_confirmed_sms_tech = [
            True
        ]

        err_msg = f"Dispatch: {dispatch_number_2} - Ticket_id: {ticket_id_2} - " \
                  f"An error occurred retrieve datetime of dispatch: " \
                  f"{cts_dispatch_confirmed_skipped_datetime.get('Local_Site_Time__c', None)}"
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_confirmed_sms_tech = CoroutineMock(side_effect=responses_confirmed_sms_tech)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1),
        ])

        cts_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to)
        ])
        cts_dispatch_monitor._send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech)
        ])

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skipping_one_invalid_sms_to_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_skipped_bad_phone,
            ticket_details_1, append_note_response):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_skipped_bad_phone
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_skipped_bad_phone.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_skipped_bad_phone.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_skipped_bad_phone.get('Local_Site_Time__c')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_1,
            response_append_note_1
        ]
        responses_confirmed_sms = [
            True
        ]
        responses_confirmed_sms_tech = [
            True
        ]

        err_msg = f"An error occurred retrieve 'sms_to' number " \
                  f"Dispatch: {dispatch_number_2} - Ticket_id: {ticket_id_2} - " \
                  f"from: {cts_dispatch_confirmed_skipped_bad_phone.get('Description__c')}"

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_confirmed_sms_tech = CoroutineMock(side_effect=responses_confirmed_sms_tech)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(sideffect=[])

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        cts_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to)
        ])
        cts_dispatch_monitor._send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech)
        ])

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skipping_one_invalid_sms_to_tech_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_skipped_bad_phone_tech,
            ticket_details_1, append_note_response):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_skipped_bad_phone_tech
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_skipped_bad_phone_tech.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_skipped_bad_phone_tech.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_skipped_bad_phone_tech.get('Local_Site_Time__c')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_1,
            response_append_note_1
        ]
        responses_confirmed_sms = [
            True
        ]
        responses_confirmed_sms_tech = [
            True
        ]

        err_msg = f"An error occurred retrieve 'sms_to_tech' number " \
                  f"Dispatch: {dispatch_number_2} - Ticket_id: {ticket_id_2} - " \
                  f"from: {cts_dispatch_confirmed_skipped_bad_phone_tech.get('Resource_Phone_Number__c')}"

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_confirmed_sms_tech = CoroutineMock(side_effect=responses_confirmed_sms_tech)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(sideffect=[])

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        cts_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to)
        ])
        cts_dispatch_monitor._send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech)
        ])

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_error_getting_ticket_details_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2, ticket_details_1,
            ticket_details_2_error, append_note_response):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2_error
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_1,
            response_append_note_1
        ]
        responses_confirmed_sms = [
            True
        ]
        responses_confirmed_sms_tech = [
            True
        ]

        response_slack_2 = {'request_id': uuid_, 'status': 200}
        responses_send_to_slack_mock = [
            response_slack_2
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_to_slack_mock)
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_confirmed_sms_tech = CoroutineMock(side_effect=responses_confirmed_sms_tech)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        cts_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to)
        ])
        cts_dispatch_monitor._send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skip_details_requested_watermark_not_found_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2, ticket_details_1,
            ticket_details_2_no_requested_watermark, append_note_response):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2_no_requested_watermark
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_1,
            response_append_note_1
        ]
        responses_confirmed_sms = [
            True
        ]
        responses_confirmed_sms_tech = [
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_confirmed_sms_tech = CoroutineMock(side_effect=responses_confirmed_sms_tech)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        cts_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to)
        ])
        cts_dispatch_monitor._send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_sms_sent_but_not_added_confirmed_sms_note_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2, ticket_details_1,
            ticket_details_2, append_note_response):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        response_append_confirmed_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        response_append_confirmed_note_2 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        response_append_confirmed_note_2_error = {
            'request_id': uuid_,
            'body': None,
            'status': 400
        }

        response_append_confirmed_sms_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        response_append_confirmed_sms_note_2_error = {
            'request_id': uuid_,
            'body': None,
            'status': 400
        }

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')

        sms_to = '+12027723610'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2
        ]

        responses_append_confirmed_note_mock = [
            True,
            False
        ]
        responses_send_confirmed_sms_mock = [
            True,
            True
        ]
        responses_send_confirmed_sms_tech_mock = [
            True,
            True
        ]

        responses_append_confirmed_sms_note_mock = [
            True,
            False
        ]
        responses_append_confirmed_sms_tech_note_mock = [
            True,
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_note_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_send_confirmed_sms_mock)
        cts_dispatch_monitor._send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_send_confirmed_sms_tech_mock)
        cts_dispatch_monitor._append_confirmed_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_note_mock)
        cts_dispatch_monitor._append_confirmed_sms_tech_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_tech_note_mock)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_confirmed_sms_not_sent_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2, ticket_details_1,
            ticket_details_2, append_note_response):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        response_append_confirmed_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        response_append_confirmed_note_2 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        response_append_confirmed_sms_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'
        sms_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723611\n'
        sms_tech_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'
        confirmed_note_2 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_2}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'
        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2
        ]
        responses_append_confirmed_notes_mock = [
            response_append_confirmed_note_1,
            response_append_confirmed_note_2,
            response_append_confirmed_note_1,
            response_append_confirmed_note_2
        ]
        responses_send_confirmed_sms_mock = [
            True,
            False
        ]
        responses_send_confirmed_sms_tech_mock = [
            True,
            True
        ]

        responses_append_confirmed_sms_note_mock = [
            response_append_confirmed_sms_note_1
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_send_confirmed_sms_mock)
        cts_dispatch_monitor._send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_send_confirmed_sms_tech_mock)
        cts_dispatch_monitor._append_confirmed_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_note_mock)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_tech_note_1),
            call(ticket_id_2, confirmed_note_2),
            call(ticket_id_2, sms_tech_note_2),
        ])

        cts_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2)
        ])
        cts_dispatch_monitor._send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_confirmed_sms_sent_but_not_sms_note_appended_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2, ticket_details_1,
            ticket_details_2, append_note_response):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        response_append_confirmed_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        response_append_confirmed_note_2 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        response_append_confirmed_sms_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        response_append_confirmed_sms_note_2_error = {
            'request_id': uuid_,
            'body': None,
            'status': 400
        }

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'
        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'
        confirmed_note_2 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_2}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'
        sms_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12027723611\n'
        sms_tech_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2
        ]
        responses_append_confirmed_notes_mock = [
            response_append_confirmed_note_1,
            response_append_confirmed_note_2,
            response_append_confirmed_note_1,
            response_append_confirmed_note_2
        ]
        responses_send_confirmed_sms_mock = [
            True,
            True
        ]
        responses_send_confirmed_sms_tech_mock = [
            True,
            True
        ]

        responses_append_confirmed_sms_note_mock = [
            True,
            False
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_send_confirmed_sms_mock)
        cts_dispatch_monitor._send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_send_confirmed_sms_tech_mock)
        cts_dispatch_monitor._append_confirmed_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_note_mock)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_tech_note_1),
            call(ticket_id_2, confirmed_note_2),
            call(ticket_id_2, sms_tech_note_2),
        ])

        cts_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2)
        ])
        cts_dispatch_monitor._send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2_tech)
        ])

        cts_dispatch_monitor._append_confirmed_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to),
            call(dispatch_number_2, ticket_id_2, sms_to_2),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_sms_and_12h_sms_notes_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            ticket_details_1_with_confirmation_note, ticket_details_2_with_confirmation_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'
        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1_with_confirmation_note,
            ticket_details_2_with_confirmation_note
        ]

        responses_append_confirmed_notes_mock = [
            True,
            True,
        ]
        responses_confirmed_sms = [
            True,
            True
        ]

        # First not skipped, Second skipped
        responses_get_diff_hours = [
            cts_dispatch_monitor.HOURS_12 - 1,
            cts_dispatch_monitor.HOURS_12 - 1,
            cts_dispatch_monitor.HOURS_12 + 1,
            cts_dispatch_monitor.HOURS_12 + 1
        ]

        responses_send_tech_12_sms_mock = [
            True
        ]

        responses_send_tech_12_sms_note_mock = [
            True
        ]

        responses_send_tech_12_sms_tech_mock = [
            True
        ]

        responses_send_tech_12_sms_tech_note_mock = [
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_tech_12_sms = CoroutineMock(side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._append_tech_12_sms_note = CoroutineMock(side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._send_tech_12_sms_tech = CoroutineMock(side_effect=responses_send_tech_12_sms_tech_mock)
        cts_dispatch_monitor._append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._send_tech_12_sms.assert_awaited_once_with(dispatch_number_1, ticket_id_1,
                                                                        cts_dispatch_confirmed, sms_to)
        cts_dispatch_monitor._append_tech_12_sms_note.assert_awaited_once_with(dispatch_number_1, ticket_id_1, sms_to)
        cts_dispatch_monitor._send_tech_12_sms_tech.assert_awaited_once_with(
            dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech)
        cts_dispatch_monitor._append_tech_12_sms_tech_note.assert_awaited_once_with(
            dispatch_number_1, ticket_id_1, sms_to_tech)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_and_confirmed_sms_notes_but_not_12h_sms_sended_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            ticket_details_1_with_confirmation_note, ticket_details_2_with_confirmation_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'
        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1_with_confirmation_note,
            ticket_details_2_with_confirmation_note
        ]

        responses_append_confirmed_notes_mock = [
            True,
            True,
        ]
        responses_confirmed_sms = [
            True,
            True
        ]

        # First not skipped, Second skipped
        responses_get_diff_hours = [
            cts_dispatch_monitor.HOURS_12 - 1,
            cts_dispatch_monitor.HOURS_12 - 1,
            cts_dispatch_monitor.HOURS_12 - 1,
            cts_dispatch_monitor.HOURS_12 - 1
        ]

        responses_send_tech_12_sms_mock = [
            True,
            False
        ]

        responses_send_tech_12_sms_note_mock = [
            False
        ]

        responses_send_tech_12_sms_tech_mock = [
            True,
            False
        ]

        responses_send_tech_12_sms_tech_note_mock = [
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_tech_12_sms = CoroutineMock(side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._append_tech_12_sms_note = CoroutineMock(side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._send_tech_12_sms_tech = CoroutineMock(side_effect=responses_send_tech_12_sms_tech_mock)
        cts_dispatch_monitor._append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._send_tech_12_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2)
        ])
        cts_dispatch_monitor._append_tech_12_sms_note.assert_awaited_once_with(dispatch_number_1, ticket_id_1, sms_to)

        cts_dispatch_monitor._send_tech_12_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2_tech)
        ])
        cts_dispatch_monitor._append_tech_12_sms_tech_note.assert_awaited_once_with(
            dispatch_number_1, ticket_id_1, sms_to_tech)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_sms_and_12h_sms_and_2h_sms_notes_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            ticket_details_1_with_12h_sms_note, ticket_details_2_with_12h_sms_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'
        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1_with_12h_sms_note,
            ticket_details_2_with_12h_sms_note
        ]

        responses_append_confirmed_notes_mock = [
            True,
            True,
        ]
        responses_confirmed_sms = [
            True,
            True
        ]

        # First not skipped, Second skipped
        responses_get_diff_hours = [
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 + 1,
            cts_dispatch_monitor.HOURS_2 + 1,
            cts_dispatch_monitor.HOURS_2 + 1,
            cts_dispatch_monitor.HOURS_2 + 1
        ]

        responses_send_tech_12_sms_mock = [
            True,
            True
        ]

        responses_send_tech_12_sms_note_mock = [
            True,
            True
        ]

        responses_send_tech_12_sms_tech_mock = [
            True,
            True
        ]

        responses_send_tech_12_sms_tech_note_mock = [
            True,
            True
        ]

        responses_send_tech_2_sms_mock = [
            True,
            True
        ]

        responses_send_tech_2_sms_note_mock = [
            True,
            True
        ]

        responses_send_tech_2_sms_tech_mock = [
            True,
            True
        ]

        responses_send_tech_2_sms_tech_note_mock = [
            True,
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_tech_12_sms = CoroutineMock(side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._append_tech_12_sms_note = CoroutineMock(side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._send_tech_12_sms_tech = CoroutineMock(side_effect=responses_send_tech_12_sms_tech_mock)
        cts_dispatch_monitor._append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_note_mock)
        cts_dispatch_monitor._send_tech_2_sms = CoroutineMock(side_effect=responses_send_tech_2_sms_mock)
        cts_dispatch_monitor._append_tech_2_sms_note = CoroutineMock(side_effect=responses_send_tech_2_sms_note_mock)
        cts_dispatch_monitor._send_tech_2_sms_tech = CoroutineMock(side_effect=responses_send_tech_2_sms_tech_mock)
        cts_dispatch_monitor._append_tech_2_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_tech_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._send_tech_12_sms.assert_not_awaited()
        cts_dispatch_monitor._append_tech_12_sms_note.assert_not_awaited()

        cts_dispatch_monitor._send_tech_12_sms_tech.assert_not_awaited()
        cts_dispatch_monitor._send_tech_12_sms_tech.assert_not_awaited()

        cts_dispatch_monitor._send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to)
        ])

        cts_dispatch_monitor._append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to)
        ])

        cts_dispatch_monitor._send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech)
        ])

        cts_dispatch_monitor._append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_sms_and_2h_sms_notes_but_not_12h_sms_sended_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            ticket_details_1_with_12h_sms_note, ticket_details_2_with_12h_sms_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'
        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1_with_12h_sms_note,
            ticket_details_2_with_12h_sms_note
        ]

        responses_append_confirmed_notes_mock = [
            True,
            True,
        ]
        responses_confirmed_sms = [
            True,
            True
        ]

        # First not skipped, Second skipped
        responses_get_diff_hours = [
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1
        ]

        responses_send_tech_12_sms_mock = [
            True,
            True
        ]

        responses_send_tech_12_sms_note_mock = [
            True,
            True
        ]

        responses_send_tech_2_sms_mock = [
            True,
            True
        ]

        responses_send_tech_2_sms_note_mock = [
            True,
            False
        ]

        responses_send_tech_2_sms_tech_mock = [
            True,
            True
        ]

        responses_send_tech_2_sms_tech_note_mock = [
            True,
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_tech_12_sms = CoroutineMock(side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._append_tech_12_sms_note = CoroutineMock(side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._send_tech_12_sms_tech = CoroutineMock()
        cts_dispatch_monitor._append_tech_12_sms_tech_note = CoroutineMock()
        cts_dispatch_monitor._send_tech_2_sms = CoroutineMock(side_effect=responses_send_tech_2_sms_mock)
        cts_dispatch_monitor._append_tech_2_sms_note = CoroutineMock(side_effect=responses_send_tech_2_sms_note_mock)
        cts_dispatch_monitor._send_tech_2_sms_tech = CoroutineMock(side_effect=responses_send_tech_2_sms_tech_mock)
        cts_dispatch_monitor._append_tech_2_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_tech_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._send_tech_12_sms.assert_not_awaited()
        cts_dispatch_monitor._append_tech_12_sms_note.assert_not_awaited()
        cts_dispatch_monitor._send_tech_12_sms_tech.assert_not_awaited()
        cts_dispatch_monitor._send_tech_12_sms_tech.assert_not_awaited()

        cts_dispatch_monitor._send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2)
        ])

        cts_dispatch_monitor._append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to)
        ])

        cts_dispatch_monitor._send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2_tech)
        ])

        cts_dispatch_monitor._append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, sms_to_2_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_sms_and_2h_sms_notes_but_sms_2h_sms_not_sended_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            ticket_details_1_with_12h_sms_note, ticket_details_2_with_12h_sms_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'
        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1_with_12h_sms_note,
            ticket_details_2_with_12h_sms_note
        ]

        responses_append_confirmed_notes_mock = [
            True,
            True,
        ]
        responses_confirmed_sms = [
            True,
            True
        ]

        # First not skipped, Second skipped
        responses_get_diff_hours = [
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1
        ]

        responses_send_tech_12_sms_mock = [
            True,
            True
        ]

        responses_send_tech_12_sms_note_mock = [
            True,
            True
        ]

        responses_send_tech_12_sms_tech_mock = [
            True,
            True
        ]

        responses_send_tech_12_sms_tech_note_mock = [
            True,
            True
        ]

        responses_send_tech_2_sms_mock = [
            True,
            False
        ]

        responses_send_tech_2_sms_note_mock = [
            False
        ]

        responses_send_tech_2_sms_tech_mock = [
            True,
            True
        ]

        responses_send_tech_2_sms_tech_note_mock = [
            True,
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_tech_12_sms = CoroutineMock(side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._append_tech_12_sms_note = CoroutineMock(side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._send_tech_12_sms_tech = CoroutineMock(side_effect=responses_send_tech_12_sms_tech_mock)
        cts_dispatch_monitor._append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_note_mock)
        cts_dispatch_monitor._send_tech_2_sms = CoroutineMock(side_effect=responses_send_tech_2_sms_mock)
        cts_dispatch_monitor._append_tech_2_sms_note = CoroutineMock(side_effect=responses_send_tech_2_sms_note_mock)
        cts_dispatch_monitor._send_tech_2_sms_tech = CoroutineMock(side_effect=responses_send_tech_2_sms_tech_mock)
        cts_dispatch_monitor._append_tech_2_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_tech_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._send_tech_12_sms.assert_not_awaited()
        cts_dispatch_monitor._append_tech_12_sms_note.assert_not_awaited()
        cts_dispatch_monitor._send_tech_12_sms_tech.assert_not_awaited()
        cts_dispatch_monitor._append_tech_12_sms_tech_note.assert_not_awaited()

        cts_dispatch_monitor._send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2)
        ])

        cts_dispatch_monitor._append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to)
        ])

        cts_dispatch_monitor._send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2_tech)
        ])

        cts_dispatch_monitor._append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, sms_to_2_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_and_confirmed_sms_and_2h_sms_notes_sended_ok_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            ticket_details_1_with_12h_sms_note, ticket_details_2_with_12h_sms_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'
        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1_with_12h_sms_note,
            ticket_details_2_with_12h_sms_note
        ]

        responses_append_confirmed_notes_mock = [
            True,
            True,
        ]
        responses_confirmed_sms = [
            True,
            True
        ]

        # First not skipped, Second skipped
        responses_get_diff_hours = [
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1
        ]

        responses_send_tech_12_sms_mock = [
            True,
            True
        ]

        responses_send_tech_12_sms_note_mock = [
            True,
            True
        ]

        responses_send_tech_12_sms_tech_mock = [
            True,
            True
        ]

        responses_send_tech_12_sms_tech_note_mock = [
            True,
            True
        ]

        responses_send_tech_2_sms_mock = [
            True,
            True
        ]

        responses_send_tech_2_sms_note_mock = [
            True,
            True
        ]

        responses_send_tech_2_sms_tech_mock = [
            True,
            True
        ]

        responses_send_tech_2_sms_tech_note_mock = [
            True,
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_tech_12_sms = CoroutineMock(side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._append_tech_12_sms_note = CoroutineMock(side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._send_tech_12_sms_tech = CoroutineMock(side_effect=responses_send_tech_12_sms_tech_mock)
        cts_dispatch_monitor._append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_note_mock)
        cts_dispatch_monitor._send_tech_2_sms = CoroutineMock(side_effect=responses_send_tech_2_sms_mock)
        cts_dispatch_monitor._append_tech_2_sms_note = CoroutineMock(side_effect=responses_send_tech_2_sms_note_mock)
        cts_dispatch_monitor._send_tech_2_sms_tech = CoroutineMock(side_effect=responses_send_tech_2_sms_tech_mock)
        cts_dispatch_monitor._append_tech_2_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_tech_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._send_tech_12_sms.assert_not_awaited()
        cts_dispatch_monitor._append_tech_12_sms_note.assert_not_awaited()
        cts_dispatch_monitor._send_tech_12_sms_tech.assert_not_awaited()
        cts_dispatch_monitor._append_tech_12_sms_tech_note.assert_not_awaited()

        cts_dispatch_monitor._send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2)
        ])

        cts_dispatch_monitor._append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to),
            call(dispatch_number_2, ticket_id_2, sms_to_2)
        ])

        cts_dispatch_monitor._send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2_tech)
        ])

        cts_dispatch_monitor._append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, sms_to_2_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_2h_sms_and_note_sended_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            ticket_details_1_with_2h_sms_note, ticket_details_2_with_2h_sms_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'
        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1_with_2h_sms_note,
            ticket_details_2_with_2h_sms_note
        ]

        responses_append_confirmed_notes_mock = [
            True,
            True,
        ]
        responses_confirmed_sms = [
            True,
            True
        ]

        # First not skipped, Second skipped
        responses_get_diff_hours = [
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 + 1,
            cts_dispatch_monitor.HOURS_2 + 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 - 1,
            cts_dispatch_monitor.HOURS_2 + 1,
            cts_dispatch_monitor.HOURS_2 + 1
        ]

        responses_send_tech_12_sms_mock = [
            True,
            True
        ]

        responses_send_tech_12_sms_note_mock = [
            True,
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._send_tech_12_sms = CoroutineMock(side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._append_tech_12_sms_note = CoroutineMock(side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._send_tech_12_sms_tech = CoroutineMock(side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._append_tech_12_sms_tech_note = CoroutineMock(side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._send_tech_2_sms = CoroutineMock()
        cts_dispatch_monitor._append_tech_2_sms_note = CoroutineMock()
        cts_dispatch_monitor._send_tech_2_sms_tech = CoroutineMock()
        cts_dispatch_monitor._append_tech_2_sms_tech_note = CoroutineMock()

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._send_tech_12_sms.assert_not_awaited()
        cts_dispatch_monitor._append_tech_12_sms_note.assert_not_awaited()

        cts_dispatch_monitor._send_tech_12_sms_tech.assert_not_awaited()
        cts_dispatch_monitor._append_tech_12_sms_tech_note.assert_not_awaited()

        cts_dispatch_monitor._send_tech_2_sms.assert_not_awaited()
        cts_dispatch_monitor._append_tech_2_sms_note.assert_not_awaited()

        cts_dispatch_monitor._send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2_tech)
        ])

        cts_dispatch_monitor._append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, sms_to_2_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_test(self, cts_dispatch_monitor, cts_dispatch_tech_on_site,
                                                   cts_dispatch_tech_on_site_2, cts_dispatch_tech_on_site_bad_datetime,
                                                   ticket_details_1, ticket_details_2,
                                                   append_note_response, append_note_response_2,
                                                   sms_success_response, sms_success_response_2):
        tech_on_site_dispatches = [
            cts_dispatch_tech_on_site,
            cts_dispatch_tech_on_site_2,
            cts_dispatch_tech_on_site_bad_datetime
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        response_append_note_2 = {
            'request_id': uuid_,
            'body': append_note_response_2,
            'status': 200
        }

        dispatch_number_1 = cts_dispatch_tech_on_site.get('Name')
        dispatch_number_2 = cts_dispatch_tech_on_site_2.get('Name')
        dispatch_number_3 = cts_dispatch_tech_on_site_bad_datetime.get('Name')
        ticket_id_1 = cts_dispatch_tech_on_site.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_tech_on_site_2.get('Ext_Ref_Num__c')
        ticket_id_3 = cts_dispatch_tech_on_site_bad_datetime.get('Ext_Ref_Num__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_2,
            response_append_note_1,
            response_append_note_2
        ]
        responses_confirmed_sms = [
            True,
            True
        ]

        responses_sms_tech_on_site_mock = [
            True,
            True
        ]

        responses_append_tech_on_site_sms_note_mock = [
            True,
            True
        ]

        err_msg = 'Dispatch: S-12345 - Ticket_id: 4694961 - ' \
                  'An error occurred retrieve datetime of dispatch: None'

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._send_tech_on_site_sms = CoroutineMock(side_effect=responses_sms_tech_on_site_mock)
        cts_dispatch_monitor._append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_tech_on_site, sms_to),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_tech_on_site_2, sms_to_2)
        ])

        cts_dispatch_monitor._append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, cts_dispatch_tech_on_site.get('API_Resource_Name__c')),
            call(dispatch_number_2, ticket_id_2, sms_to_2, cts_dispatch_tech_on_site_2.get('API_Resource_Name__c'))
        ])

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_with_general_exception_test(
            self, cts_dispatch_monitor):
        tech_on_site_dispatches = 0  # Non valid list for filter
        err_msg = f"Error: _monitor_tech_on_site_dispatches - object of type 'int' has no len()"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches)

        cts_dispatch_monitor._logger.error.assert_called_once()
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_with_exception_test(
            self, cts_dispatch_monitor, cts_dispatch_tech_on_site):
        tech_on_site_dispatches = [
            cts_dispatch_tech_on_site
        ]
        err_msg = f"Error: Dispatch [{cts_dispatch_tech_on_site.get('Name')}] " \
                  f"in ticket_id: {cts_dispatch_tech_on_site.get('Ext_Ref_Num__c')} " \
                  f"- {cts_dispatch_tech_on_site}"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches)

        cts_dispatch_monitor._logger.error.assert_called_once()
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_skipping_one_invalid_ticket_id_test(self, cts_dispatch_monitor,
                                                                                  cts_dispatch_tech_on_site_skipped):
        tech_on_site_dispatches = [
            cts_dispatch_tech_on_site_skipped
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock()
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock()
        cts_dispatch_monitor._send_confirmed_sms = CoroutineMock()

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_not_awaited()
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        cts_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_skipping_one_invalid_sms_to_test(
            self, cts_dispatch_monitor, cts_dispatch_tech_on_site_skipped_bad_phone):
        tech_on_site_dispatches = [
            cts_dispatch_tech_on_site_skipped_bad_phone
        ]

        dispatch_number_1 = cts_dispatch_tech_on_site_skipped_bad_phone.get('Name')
        ticket_id_1 = cts_dispatch_tech_on_site_skipped_bad_phone.get('Ext_Ref_Num__c')
        sms_to = '+12027723610'

        err_msg = f"An error occurred retrieve 'sms_to' number " \
                  f"Dispatch: {dispatch_number_1} - Ticket_id: {ticket_id_1} - " \
                  f"from: {cts_dispatch_tech_on_site_skipped_bad_phone.get('Description__c')}"

        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(return_value=err_msg)

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_error_getting_ticket_details_test(
            self, cts_dispatch_monitor, cts_dispatch_tech_on_site, cts_dispatch_tech_on_site_2, ticket_details_1,
            ticket_details_2_error):
        tech_on_site_dispatches = [
            cts_dispatch_tech_on_site,
            cts_dispatch_tech_on_site_2
        ]

        dispatch_number_1 = cts_dispatch_tech_on_site.get('Name')
        dispatch_number_2 = cts_dispatch_tech_on_site_2.get('Name')
        ticket_id_1 = cts_dispatch_tech_on_site.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_tech_on_site_2.get('Ext_Ref_Num__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2_error
        ]

        responses_sms_tech_on_site_mock = [
            True
        ]

        responses_append_tech_on_site_sms_note_mock = [
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)

        cts_dispatch_monitor._send_tech_on_site_sms = CoroutineMock(side_effect=responses_sms_tech_on_site_mock)
        cts_dispatch_monitor._append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        err_msg = f"An error occurred retrieve getting ticket details from bruin " \
                  f"Dispatch: {dispatch_number_2} - Ticket_id: {ticket_id_2}"

        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(return_value=err_msg)

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_tech_on_site, sms_to)
        ])

        cts_dispatch_monitor._append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, cts_dispatch_tech_on_site.get('API_Resource_Name__c'))
        ])

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_watermark_not_found_test(
            self, cts_dispatch_monitor, cts_dispatch_tech_on_site, cts_dispatch_tech_on_site_2, ticket_details_1,
            ticket_details_2_no_requested_watermark):
        tech_on_site_dispatches = [
            cts_dispatch_tech_on_site,
            cts_dispatch_tech_on_site_2
        ]

        dispatch_number_1 = cts_dispatch_tech_on_site.get('Name')
        dispatch_number_2 = cts_dispatch_tech_on_site_2.get('Name')
        ticket_id_1 = cts_dispatch_tech_on_site.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_tech_on_site_2.get('Ext_Ref_Num__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2_no_requested_watermark
        ]

        responses_sms_tech_on_site_mock = [
            True
        ]

        responses_append_tech_on_site_sms_note_mock = [
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)

        cts_dispatch_monitor._send_tech_on_site_sms = CoroutineMock(side_effect=responses_sms_tech_on_site_mock)
        cts_dispatch_monitor._append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_tech_on_site, sms_to)
        ])

        cts_dispatch_monitor._append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, cts_dispatch_tech_on_site.get('API_Resource_Name__c'))
        ])

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_sms_not_sended_test(
            self, cts_dispatch_monitor, cts_dispatch_tech_on_site, cts_dispatch_tech_on_site_2, ticket_details_1,
            ticket_details_2):
        tech_on_site_dispatches = [
            cts_dispatch_tech_on_site,
            cts_dispatch_tech_on_site_2
        ]

        dispatch_number_1 = cts_dispatch_tech_on_site.get('Name')
        dispatch_number_2 = cts_dispatch_tech_on_site_2.get('Name')
        ticket_id_1 = cts_dispatch_tech_on_site.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_tech_on_site_2.get('Ext_Ref_Num__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2
        ]

        responses_sms_tech_on_site_mock = [
            True,
            False
        ]

        responses_append_tech_on_site_sms_note_mock = [
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)

        cts_dispatch_monitor._send_tech_on_site_sms = CoroutineMock(side_effect=responses_sms_tech_on_site_mock)
        cts_dispatch_monitor._append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_tech_on_site, sms_to),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_tech_on_site_2, sms_to_2)
        ])

        cts_dispatch_monitor._append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, cts_dispatch_tech_on_site.get('API_Resource_Name__c'))
        ])

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_sms_note_not_appended_test(
            self, cts_dispatch_monitor, cts_dispatch_tech_on_site, cts_dispatch_tech_on_site_2, ticket_details_1,
            ticket_details_2):
        tech_on_site_dispatches = [
            cts_dispatch_tech_on_site,
            cts_dispatch_tech_on_site_2
        ]

        dispatch_number_1 = cts_dispatch_tech_on_site.get('Name')
        dispatch_number_2 = cts_dispatch_tech_on_site_2.get('Name')
        ticket_id_1 = cts_dispatch_tech_on_site.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_tech_on_site_2.get('Ext_Ref_Num__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2
        ]

        responses_sms_tech_on_site_mock = [
            True,
            True
        ]

        responses_append_tech_on_site_sms_note_mock = [
            True,
            False
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)

        cts_dispatch_monitor._send_tech_on_site_sms = CoroutineMock(side_effect=responses_sms_tech_on_site_mock)
        cts_dispatch_monitor._append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_tech_on_site, sms_to),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_tech_on_site_2, sms_to_2)
        ])

        cts_dispatch_monitor._append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, cts_dispatch_tech_on_site.get('API_Resource_Name__c')),
            call(dispatch_number_2, ticket_id_2, sms_to_2, cts_dispatch_tech_on_site_2.get('API_Resource_Name__c'))
        ])

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_with_tech_on_site_note_already_sended_ok_test(
            self, cts_dispatch_monitor, cts_dispatch_tech_on_site, cts_dispatch_tech_on_site_2,
            ticket_details_1_with_tech_on_site_sms_note, ticket_details_2_with_tech_on_site_sms_note):
        tech_on_site_dispatches = [
            cts_dispatch_tech_on_site,
            cts_dispatch_tech_on_site_2
        ]

        dispatch_number_1 = cts_dispatch_tech_on_site.get('Name')
        dispatch_number_2 = cts_dispatch_tech_on_site_2.get('Name')
        ticket_id_1 = cts_dispatch_tech_on_site.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_tech_on_site_2.get('Ext_Ref_Num__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'

        responses_details_mock = [
            ticket_details_1_with_tech_on_site_sms_note,
            ticket_details_2_with_tech_on_site_sms_note
        ]

        responses_sms_tech_on_site_mock = [
            True,
            True
        ]

        responses_append_tech_on_site_sms_note_mock = [
            True,
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)

        cts_dispatch_monitor._send_tech_on_site_sms = CoroutineMock()
        cts_dispatch_monitor._append_tech_on_site_sms_note = CoroutineMock()

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._send_tech_on_site_sms.assert_not_awaited()
        cts_dispatch_monitor._append_tech_on_site_sms_note.assert_not_awaited()
