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
from dateutil.parser import parse
from pytz import timezone
from shortuuid import uuid

from application.actions.lit_dispatch_monitor import LitDispatchMonitor
from application.actions import lit_dispatch_monitor as lit_dispatch_monitor_module

from application.repositories.lit_repository import LitRepository

from application.templates.lit.sms.dispatch_confirmed import lit_get_dispatch_confirmed_sms, \
    lit_get_tech_24_hours_before_sms, lit_get_tech_2_hours_before_sms

from application.repositories.utils_repository import UtilsRepository

from application.templates.lit.sms.tech_on_site import lit_get_tech_on_site_sms
from config import testconfig


uuid_ = uuid()
uuid_mock = patch.object(lit_dispatch_monitor_module, 'uuid', return_value=uuid_)


class TestLitDispatchMonitor:
    def instance_test(self):
        redis_client = Mock()
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        lit_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()

        lit_dispatch_monitor = LitDispatchMonitor(config, redis_client, event_bus, scheduler, logger,
                                                  lit_repository, bruin_repository, notifications_repository)

        assert lit_dispatch_monitor._redis_client is redis_client
        assert lit_dispatch_monitor._event_bus is event_bus
        assert lit_dispatch_monitor._logger is logger
        assert lit_dispatch_monitor._scheduler is scheduler
        assert lit_dispatch_monitor._config is config
        assert lit_dispatch_monitor._lit_repository is lit_repository
        assert lit_dispatch_monitor._bruin_repository is bruin_repository
        assert lit_dispatch_monitor._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def start_dispatch_monitor_job_with_exec_on_start_test(self, lit_dispatch_monitor):
        config = testconfig

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(lit_dispatch_monitor_module, 'datetime', new=datetime_mock):
            with patch.object(lit_dispatch_monitor_module, 'timezone', new=Mock()):
                await lit_dispatch_monitor.start_monitoring_job(exec_on_start=True)

        lit_dispatch_monitor._scheduler.add_job.assert_called_once_with(
            lit_dispatch_monitor._lit_dispatch_monitoring_process, 'interval',
            minutes=config.DISPATCH_MONITOR_CONFIG["jobs_intervals"]["lit_dispatch_monitor"],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_service_dispatch_monitor_lit_process',
        )

    @pytest.mark.asyncio
    async def start_dispatch_monitor_job_with_no_exec_on_start_test(self, lit_dispatch_monitor):
        config = testconfig

        await lit_dispatch_monitor.start_monitoring_job(exec_on_start=False)

        lit_dispatch_monitor._scheduler.add_job.assert_called_once_with(
            lit_dispatch_monitor._lit_dispatch_monitoring_process, 'interval',
            minutes=config.DISPATCH_MONITOR_CONFIG["jobs_intervals"]["lit_dispatch_monitor"],
            next_run_time=undefined,
            replace_existing=False,
            id='_service_dispatch_monitor_lit_process',
        )

    def is_dispatch_confirmed_test(self, lit_dispatch_monitor, dispatch_confirmed, dispatch_not_confirmed):
        assert lit_dispatch_monitor._is_dispatch_confirmed(dispatch_confirmed) is True
        assert lit_dispatch_monitor._is_dispatch_confirmed(dispatch_not_confirmed) is False

    def is_tech_on_site_test(self, lit_dispatch_monitor, dispatch_tech_on_site, dispatch_tech_not_on_site):
        assert lit_dispatch_monitor._is_tech_on_site(dispatch_tech_on_site) is True
        assert lit_dispatch_monitor._is_tech_on_site(dispatch_tech_not_on_site) is False

    def is_valid_ticket_id_test(self, lit_dispatch_monitor):
        valid_ticket_id = '4663397'
        invalid_ticket_id_1 = '4663397|IW24654081'
        invalid_ticket_id_2 = '712637/IW76236'
        invalid_ticket_id_3 = '123-3123'
        invalid_ticket_id_4 = '4485610(Order)/4520284(Port)'
        assert lit_dispatch_monitor._is_valid_ticket_id(ticket_id=valid_ticket_id) is True
        assert lit_dispatch_monitor._is_valid_ticket_id(ticket_id=invalid_ticket_id_1) is False
        assert lit_dispatch_monitor._is_valid_ticket_id(ticket_id=invalid_ticket_id_2) is False
        assert lit_dispatch_monitor._is_valid_ticket_id(ticket_id=invalid_ticket_id_3) is False
        assert lit_dispatch_monitor._is_valid_ticket_id(ticket_id=invalid_ticket_id_4) is False

    def is_repair_completed_test(self, lit_dispatch_monitor, dispatch_completed, dispatch_not_completed,
                                 dispatch_confirmed_2):
        assert lit_dispatch_monitor._is_repair_completed(dispatch_completed) is True
        assert lit_dispatch_monitor._is_repair_completed(dispatch_not_completed) is False

    def get_dispatches_splitted_by_status_test(self, lit_dispatch_monitor, dispatch, dispatch_confirmed,
                                               dispatch_confirmed_2, dispatch_tech_on_site, dispatch_completed,
                                               bad_status_dispatch):
        dispatches = [
            dispatch, dispatch_confirmed, dispatch_confirmed_2,
            dispatch_tech_on_site, dispatch_completed, bad_status_dispatch
        ]
        expected_dispatches_splitted = {
            str(lit_dispatch_monitor.DISPATCH_REQUESTED): [dispatch],
            str(lit_dispatch_monitor.DISPATCH_CONFIRMED): [dispatch_confirmed, dispatch_confirmed_2],
            str(lit_dispatch_monitor.DISPATCH_FIELD_ENGINEER_ON_SITE): [dispatch_tech_on_site],
            str(lit_dispatch_monitor.DISPATCH_REPAIR_COMPLETED): [dispatch_completed]
        }
        assert lit_dispatch_monitor._get_dispatches_splitted_by_status(dispatches) == expected_dispatches_splitted

    @pytest.mark.asyncio
    async def lit_dispatch_monitoring_process_test(self, lit_dispatch_monitor, dispatch, dispatch_confirmed):
        dispatches = [dispatch, dispatch_confirmed]
        dispatches_response = {
            'status': 200,
            'body': {
                'Status': 'Success',
                'DispatchList': dispatches
            }
        }
        splitted_dispatches = {
            str(lit_dispatch_monitor.DISPATCH_REQUESTED): [dispatch],
            str(lit_dispatch_monitor.DISPATCH_CONFIRMED): [dispatch_confirmed],
        }
        confirmed_dispatches = [dispatch_confirmed]
        lit_dispatch_monitor._lit_repository.get_all_dispatches = CoroutineMock(return_value=dispatches_response)
        lit_dispatch_monitor._get_dispatches_splitted_by_status = Mock(return_value=splitted_dispatches)
        lit_dispatch_monitor._monitor_confirmed_dispatches = CoroutineMock()
        await lit_dispatch_monitor._lit_dispatch_monitoring_process()

        lit_dispatch_monitor._monitor_confirmed_dispatches.assert_awaited_once()
        lit_dispatch_monitor._monitor_confirmed_dispatches.assert_awaited_with(confirmed_dispatches)

    @pytest.mark.asyncio
    async def lit_dispatch_monitoring_process_error_exception_test(
            self, lit_dispatch_monitor):
        lit_dispatch_monitor._lit_dispatch_monitoring_process = CoroutineMock(side_effect=Exception)
        lit_dispatch_monitor._monitor_confirmed_dispatches = CoroutineMock(side_effect=Exception)
        lit_dispatch_monitor._lit_repository.get_all_dispatches = CoroutineMock(side_effect=Exception)
        lit_dispatch_monitor._get_dispatches_splitted_by_status = CoroutineMock()
        with pytest.raises(Exception):
            await lit_dispatch_monitor._lit_dispatch_monitoring_process()
            lit_dispatch_monitor._logger.error.assert_called_once()
            lit_dispatch_monitor._get_dispatches_splitted_by_status.assert_not_awaited()
            lit_dispatch_monitor._monitor_confirmed_dispatches.assert_not_awaited()

    @pytest.mark.asyncio
    async def lit_dispatch_monitoring_process_error_getting_dispatches_test(
            self, lit_dispatch_monitor, dispatch, dispatch_confirmed):
        dispatches = [dispatch, dispatch_confirmed]
        dispatches_response = {
            'status': 400,
            'body': {
                'Status': 'Error',
                'DispatchList': dispatches
            }
        }
        lit_dispatch_monitor._lit_repository.get_all_dispatches = CoroutineMock(return_value=dispatches_response)
        lit_dispatch_monitor._monitor_confirmed_dispatches = CoroutineMock()
        await lit_dispatch_monitor._lit_dispatch_monitoring_process()

        lit_dispatch_monitor._monitor_confirmed_dispatches.assert_not_awaited()

    @pytest.mark.asyncio
    async def lit_dispatch_monitoring_process_error_getting_dispatches_invalid_body_test(
            self, lit_dispatch_monitor, dispatch, dispatch_confirmed):
        dispatches = [dispatch, dispatch_confirmed]
        dispatches_response = {
            'status': 200,
            'body': {
                'Status': 'Error',
                'DispatchList': dispatches
            }
        }
        lit_dispatch_monitor._lit_repository.get_all_dispatches = CoroutineMock(return_value=dispatches_response)
        lit_dispatch_monitor._monitor_confirmed_dispatches = CoroutineMock()
        await lit_dispatch_monitor._lit_dispatch_monitoring_process()

        lit_dispatch_monitor._monitor_confirmed_dispatches.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_confirmed_note_test(self, lit_dispatch_monitor, dispatch_confirmed, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = '#*Automation Engine*#\nDispatch Management - Dispatch Confirmed\n' \
                   'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                   'Field Engineer\nJoe Malone\n+12123595129\n'
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(side_effect=[response_append_note_1])

        response = await lit_dispatch_monitor._append_confirmed_note(dispatch_number, ticket_id, dispatch_confirmed)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_confirmed_note_error_test(self, lit_dispatch_monitor, dispatch_confirmed, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        note_data = {
            'vendor': 'LIT',
            'date_of_dispatch': dispatch_confirmed.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch_confirmed.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch_confirmed.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'tech_name': dispatch_confirmed.get('Tech_First_Name'),
            'tech_phone': dispatch_confirmed.get('Tech_Mobile_Number')
        }
        sms_note = '#*Automation Engine*#\nDispatch Management - Dispatch Confirmed\n' \
                   'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                   'Field Engineer\nJoe Malone\n+12123595129\n'

        send_error_sms_to_slack_response = f'An error occurred when appending a confirmed note with bruin client. ' \
                                           f'Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - payload: {note_data}'

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(side_effect=[response_append_note_1])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._append_confirmed_note(dispatch_number, ticket_id, dispatch_confirmed)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def send_confirmed_sms_test(self, lit_dispatch_monitor, dispatch, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        # sms_to = dispatch.get('Job_Site_Contact_Name_and_Phone_Number')
        # sms_to = LitRepository.get_sms_to(dispatch)
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'phone_number': sms_to
        }

        sms_data = lit_get_dispatch_confirmed_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to,
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

        # lit_dispatch_monitor._event_bus.rpc_request = CoroutineMock(return_value=response)
        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await lit_dispatch_monitor._send_confirmed_sms(dispatch_number, ticket_id, dispatch, sms_to)
        assert response is True

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        # lit_dispatch_monitor._notifications_repository._event_bus.rpc_request.assert_awaited_once_with(
        #     "notification.sms.request", request, timeout=30)

    @pytest.mark.asyncio
    async def send_confirmed_sms_with_not_valid_sms_to_phone_test(self, lit_dispatch_monitor, dispatch):
        updated_dispatch = dispatch.copy()
        ticket_id = '3544800'
        dispatch_number = updated_dispatch.get('Dispatch_Number')
        updated_dispatch['Job_Site_Contact_Name_and_Phone_Number'] = 'NOT VALID PHONE'
        sms_to = None

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await lit_dispatch_monitor._send_confirmed_sms(dispatch_number, ticket_id, updated_dispatch, sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_confirmed_sms_with_error_test(self, lit_dispatch_monitor, dispatch, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        # sms_to = dispatch.get('Job_Site_Contact_Name_and_Phone_Number')
        # sms_to = LitRepository.get_sms_to(dispatch)
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'phone_number': sms_to
        }

        sms_data = lit_get_dispatch_confirmed_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to,
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

        send_error_sms_to_slack_response = f'An error occurred when sending Confirmed SMS with notifier client. ' \
                                           f'payload: {sms_payload}'

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._send_confirmed_sms(dispatch_number, ticket_id, dispatch, sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_tech_24_sms_test(self, lit_dispatch_monitor, dispatch, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'phone_number': sms_to
        }

        sms_data = lit_get_tech_24_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to,
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await lit_dispatch_monitor._send_tech_24_sms(dispatch_number, ticket_id, dispatch, sms_to)
        assert response is True

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_tech_24_sms_with_not_valid_sms_to_phone_test(self, lit_dispatch_monitor, dispatch):
        updated_dispatch = dispatch.copy()
        ticket_id = '3544800'
        dispatch_number = updated_dispatch.get('Dispatch_Number')
        updated_dispatch['Job_Site_Contact_Name_and_Phone_Number'] = 'NOT VALID PHONE'
        sms_to = None

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await lit_dispatch_monitor._send_tech_24_sms(dispatch_number, ticket_id, updated_dispatch, sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_tech_24_sms_with_error_test(self, lit_dispatch_monitor, dispatch, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        # sms_to = dispatch.get('Job_Site_Contact_Name_and_Phone_Number')
        # sms_to = LitRepository.get_sms_to(dispatch)
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'phone_number': sms_to
        }

        sms_data = lit_get_tech_24_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to,
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 400
        }

        send_error_sms_to_slack_response = f'An error occurred when sending a tech 24 hours SMS with notifier client. ' \
                                           f'payload: {sms_payload}'

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._send_tech_24_sms(dispatch_number, ticket_id, dispatch, sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_tech_2_sms_test(self, lit_dispatch_monitor, dispatch, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'phone_number': sms_to
        }

        sms_data = lit_get_tech_2_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to,
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await lit_dispatch_monitor._send_tech_2_sms(dispatch_number, ticket_id, dispatch, sms_to)
        assert response is True

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_tech_2_sms_with_not_valid_sms_to_phone_test(self, lit_dispatch_monitor, dispatch):
        updated_dispatch = dispatch.copy()
        ticket_id = '3544800'
        dispatch_number = updated_dispatch.get('Dispatch_Number')
        updated_dispatch['Job_Site_Contact_Name_and_Phone_Number'] = 'NOT VALID PHONE'
        sms_to = None

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await lit_dispatch_monitor._send_tech_2_sms(dispatch_number, ticket_id, updated_dispatch, sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_tech_2_sms_with_error_test(self, lit_dispatch_monitor, dispatch, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        # sms_to = dispatch.get('Job_Site_Contact_Name_and_Phone_Number')
        # sms_to = LitRepository.get_sms_to(dispatch)
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'phone_number': sms_to
        }

        sms_data = lit_get_tech_2_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to,
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 400
        }

        send_error_sms_to_slack_response = f'An error occurred when sending a tech 2 hours SMS with notifier client. ' \
                                           f'payload: {sms_payload}'

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._send_tech_2_sms(dispatch_number, ticket_id, dispatch, sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_tech_on_site_sms_test(self, lit_dispatch_monitor, dispatch, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        sms_data_payload = {
            'field_engineer_name': dispatch.get('Tech_First_Name')
        }

        sms_data = lit_get_tech_on_site_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to,
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await lit_dispatch_monitor._send_tech_on_site_sms(dispatch_number, ticket_id, dispatch, sms_to)
        assert response is True

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_tech_on_site_sms_with_not_valid_sms_to_phone_test(self, lit_dispatch_monitor, dispatch):
        updated_dispatch = dispatch.copy()
        ticket_id = '3544800'
        dispatch_number = updated_dispatch.get('Dispatch_Number')
        updated_dispatch['Job_Site_Contact_Name_and_Phone_Number'] = 'NOT VALID PHONE'
        sms_to = None

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await lit_dispatch_monitor._send_tech_on_site_sms(dispatch_number, ticket_id, updated_dispatch, sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_tech_on_site_sms_with_error_test(self, lit_dispatch_monitor, dispatch, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        # sms_to = dispatch.get('Job_Site_Contact_Name_and_Phone_Number')
        # sms_to = LitRepository.get_sms_to(dispatch)
        sms_to = '+1987654327'
        sms_data_payload = {
            'field_engineer_name': dispatch.get('Tech_First_Name')
        }

        sms_data = lit_get_tech_on_site_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to,
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 400
        }

        send_error_sms_to_slack_response = f'An error occurred when sending a tech on site SMS with notifier client. ' \
                                           f'payload: {sms_payload}'

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._send_tech_on_site_sms(dispatch_number, ticket_id, dispatch, sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def append_confirmed_sms_note_test(self, lit_dispatch_monitor, dispatch, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = '#*Automation Engine*#\nDispatch confirmation SMS sent to +1987654327\n'
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(side_effect=[response_append_note_1])

        response = await lit_dispatch_monitor._append_confirmed_sms_note(dispatch_number, ticket_id, sms_to)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_confirmed_sms_note_error_test(self, lit_dispatch_monitor, dispatch, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = '#*Automation Engine*#\nDispatch confirmation SMS sent to +1987654327\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS Confirmed note not appended'

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._append_confirmed_sms_note(dispatch_number, ticket_id, sms_to)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_tech_24_sms_note_test(self, lit_dispatch_monitor, dispatch, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = '#*Automation Engine*#\nDispatch 24h prior reminder SMS sent to +1987654327\n'
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await lit_dispatch_monitor._append_tech_24_sms_note(dispatch_number, ticket_id, sms_to)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_tech_24_sms_note_error_test(self, lit_dispatch_monitor, dispatch, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = '#*Automation Engine*#\nDispatch 24h prior reminder SMS sent to +1987654327\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS tech 24 hours note not appended'

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._append_tech_24_sms_note(dispatch_number, ticket_id, sms_to)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_tech_2_sms_note_test(self, lit_dispatch_monitor, dispatch, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = '#*Automation Engine*#\nDispatch 2h prior reminder SMS sent to +1987654327\n'
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await lit_dispatch_monitor._append_tech_2_sms_note(dispatch_number, ticket_id, sms_to)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_tech_2_sms_note_error_test(self, lit_dispatch_monitor, dispatch, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = '#*Automation Engine*#\nDispatch 2h prior reminder SMS sent to +1987654327\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS tech 2 hours note not appended'

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._append_tech_2_sms_note(dispatch_number, ticket_id, sms_to)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_tech_on_site_sms_note_test(self, lit_dispatch_monitor, dispatch_confirmed, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = '#*Automation Engine*#\nDispatch Management - Field Engineer On Site\n\nJoe Malone has arrived\n'
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await lit_dispatch_monitor._append_tech_on_site_sms_note(dispatch_number, ticket_id, sms_to,
                                                                            dispatch_confirmed.get('Tech_First_Name'))

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_tech_on_site_sms_note_error_test(self, lit_dispatch_monitor, dispatch_confirmed, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = '#*Automation Engine*#\nDispatch Management - Field Engineer On Site\n\nJoe Malone has arrived\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS tech on site note not appended'

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._append_tech_on_site_sms_note(dispatch_number, ticket_id, sms_to,
                                                                            dispatch_confirmed.get('Tech_First_Name'))

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_test(self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2,
                                                ticket_details_1, ticket_details_2,
                                                append_note_response, append_note_response_2,
                                                sms_success_response, sms_success_response_2):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
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

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595129\n'
        sms_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595126\n'

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'
        confirmed_note_2 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 10:30AM-11:30AM Eastern Time\n\n' \
                           'Field Engineer\nHulk Hogan\n+12123595126\n'

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

        sms_data = ''
        sms_payload = {
            'sms_to': sms_to,
            'sms_data': sms_data
        }
        sms_payload_2 = {
            'sms_to': sms_to,
            'sms_data': sms_data
        }

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

        datetime_return_1 = {
            'datetime_localized': datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = {
            'datetime_localized': datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Eastern')
        }
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]
        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(side_effect=responses_append_notes_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)

        await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
            call(dispatch_confirmed_2, dispatch_number_2, ticket_id_2),
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_2, confirmed_note_2),
            call(ticket_id_2, sms_note_2)
        ])

        lit_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_exception_test(self, lit_dispatch_monitor, dispatch_confirmed):
        confirmed_dispatches = [
            dispatch_confirmed
        ]
        lit_dispatch_monitor.get_dispatch_confirmed_date_time_localized = Mock(side_effect=Exception)

        await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches)

        lit_dispatch_monitor._logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skipping_one_invalid_ticket_id_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_skipped, ticket_details_1, append_note_response):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_skipped
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595129\n'

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'

        sms_to = '+12123595129'

        responses_details_mock = [
            ticket_details_1
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_1
        ]
        responses_confirmed_sms = [
            True
        ]

        datetime_return_1 = {
            'datetime_localized': datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_returns_mock = [
            datetime_return_1
        ]
        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)

        await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1)
        ])

        lit_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skipping_one_invalid_datetime_test(self, lit_dispatch_monitor, dispatch_confirmed,
                                                             dispatch_confirmed_skipped_datetime, ticket_details_1,
                                                             append_note_response):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_skipped_datetime
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595129\n'

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'

        sms_to = '+12123595129'

        responses_details_mock = [
            ticket_details_1
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_1
        ]
        responses_confirmed_sms = [
            True
        ]

        datetime_return_1 = {
            'datetime_localized': datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = None
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]
        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)

        await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1)
        ])

        lit_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skipping_one_invalid_sms_to_test(self, lit_dispatch_monitor, dispatch_confirmed,
                                                             dispatch_confirmed_skipped_bad_phone, ticket_details_1,
                                                             append_note_response):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_skipped_bad_phone
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595129\n'

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        dispatch_number_2 = dispatch_confirmed_skipped_bad_phone.get('Dispatch_Number')
        ticket_id_2 = dispatch_confirmed_skipped_bad_phone.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'

        sms_to = '+12123595129'

        responses_details_mock = [
            ticket_details_1
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_1
        ]
        responses_confirmed_sms = [
            True
        ]

        datetime_return_1 = {
            'datetime_localized': datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = {
            'datetime_localized': datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Eastern')
        }
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]

        err_msg = f"An error occurred retrieve 'sms_to' number " \
                  f"Dispatch: {dispatch_number_2} - Ticket_id: {ticket_id_2} - " \
                  f"from: {dispatch_confirmed_skipped_bad_phone.get('Job_Site_Contact_Name_and_Phone_Number')}"

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(sideffect=[])

        await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1)
        ])

        lit_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        ])

        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_error_getting_ticket_details_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2, ticket_details_1, ticket_details_2_error,
            append_note_response):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595129\n'

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'

        sms_to = '+12123595129'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2_error
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_1
        ]
        responses_confirmed_sms = [
            True
        ]

        datetime_return_1 = {
            'datetime_localized': datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = {
            'datetime_localized': datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Eastern')
        }
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]

        response_slack_2 = {'request_id': uuid_, 'status': 200}
        responses_send_to_slack_mock = [
            response_slack_2
        ]

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(side_effect=responses_send_to_slack_mock)
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)

        await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1)
        ])

        lit_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skip_details_requested_watermark_not_found_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2, ticket_details_1,
            ticket_details_2_no_requested_watermark, append_note_response):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595129\n'

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'

        sms_to = '+12123595129'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2_no_requested_watermark
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_1
        ]
        responses_confirmed_sms = [
            True
        ]

        datetime_return_1 = {
            'datetime_localized': datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = {
            'datetime_localized': datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Eastern')
        }
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)

        await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1)
        ])

        lit_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_sms_sent_but_not_added_confirmed_sms_note_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2, ticket_details_1,
            ticket_details_2, append_note_response):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
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

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'
        confirmed_note_2 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 10:30AM-11:30AM Eastern Time\n\n' \
                           'Field Engineer\nHulk Hogan\n+12123595126\n'
        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595129\n'
        sms_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595126\n'

        sms_to = '+12123595129'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2
        ]
        responses_append_confirmed_notes_mock = [
            response_append_confirmed_note_1,
            response_append_confirmed_note_2_error
        ]
        responses_append_confirmed_note_mock = [
            True,
            False
        ]
        responses_send_confirmed_sms_mock = [
            True,
            True
        ]

        datetime_return_1 = {
            'datetime_localized': datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = {
            'datetime_localized': datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Eastern')
        }
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]

        responses_append_confirmed_sms_note_mock = [
            True,
            False
        ]

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_note_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_send_confirmed_sms_mock)
        lit_dispatch_monitor._append_confirmed_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_note_mock)

        await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
            call(dispatch_confirmed_2, dispatch_number_2, ticket_id_2)
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_confirmed_sms_not_sent_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2, ticket_details_1,
            ticket_details_2, append_note_response):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
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

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'
        confirmed_note_2 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 10:30AM-11:30AM Eastern Time\n\n' \
                           'Field Engineer\nHulk Hogan\n+12123595126\n'
        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595129\n'
        sms_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595126\n'

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2
        ]
        responses_append_confirmed_notes_mock = [
            response_append_confirmed_note_1,
            response_append_confirmed_note_2
        ]
        responses_send_confirmed_sms_mock = [
            True,
            False
        ]

        datetime_return_1 = {
            'datetime_localized': datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = {
            'datetime_localized': datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Eastern')
        }
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]

        responses_append_confirmed_sms_note_mock = [
            response_append_confirmed_sms_note_1
        ]

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_send_confirmed_sms_mock)
        lit_dispatch_monitor._append_confirmed_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_note_mock)

        await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
            call(dispatch_confirmed_2, dispatch_number_2, ticket_id_2)
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_2, confirmed_note_2)
        ])

        lit_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_confirmed_sms_sent_but_not_sms_note_appended_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2, ticket_details_1,
            ticket_details_2, append_note_response):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
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

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'
        confirmed_note_2 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 10:30AM-11:30AM Eastern Time\n\n' \
                           'Field Engineer\nHulk Hogan\n+12123595126\n'
        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595129\n'
        sms_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595126\n'

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2
        ]
        responses_append_confirmed_notes_mock = [
            response_append_confirmed_note_1,
            response_append_confirmed_note_2
        ]
        responses_send_confirmed_sms_mock = [
            True,
            True
        ]

        datetime_return_1 = {
            'datetime_localized': datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = {
            'datetime_localized': datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p'),
            'timezone': timezone(f'US/Eastern')
        }
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]

        responses_append_confirmed_sms_note_mock = [
            True,
            False
        ]

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_send_confirmed_sms_mock)
        lit_dispatch_monitor._append_confirmed_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_note_mock)

        await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
            call(dispatch_confirmed_2, dispatch_number_2, ticket_id_2)
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_2, confirmed_note_2)
        ])

        lit_dispatch_monitor._send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2)
        ])

        lit_dispatch_monitor._append_confirmed_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to),
            call(dispatch_number_2, ticket_id_2, sms_to_2),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_sms_and_24h_sms_notes_test(self, lit_dispatch_monitor,
        dispatch_confirmed, dispatch_confirmed_2,
        ticket_details_1_with_confirmation_note, ticket_details_2_with_confirmation_note):

        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
        ]

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

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

        tz_1 = timezone(f'US/Pacific')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')),
            'timezone': tz_1
        }
        tz_2 = timezone(f'US/Eastern')
        datetime_return_2 = {
            'datetime_localized': tz_2.localize(datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')),
            'timezone': tz_2
        }
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]
        # First not skipped, Second skipped
        responses_get_diff_hours = [
            lit_dispatch_monitor.HOURS_24 - 1,
            lit_dispatch_monitor.HOURS_24 + 1
        ]

        responses_send_tech_24_sms_mock = [
            True
        ]

        responses_send_tech_24_sms_note_mock = [
            True
        ]

        sms_to = '+12123595129'

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._send_tech_24_sms = CoroutineMock(side_effect=responses_send_tech_24_sms_mock)
        lit_dispatch_monitor._append_tech_24_sms_note = CoroutineMock(side_effect=responses_send_tech_24_sms_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
            call(dispatch_confirmed_2, dispatch_number_2, ticket_id_2),
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._append_confirmed_note.assert_not_awaited()
        lit_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

        lit_dispatch_monitor._send_tech_24_sms.assert_awaited_once_with(dispatch_number_1, ticket_id_1,
                                                                        dispatch_confirmed, sms_to)
        lit_dispatch_monitor._append_tech_24_sms_note.assert_awaited_once_with(dispatch_number_1, ticket_id_1, sms_to)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_and_confirmed_sms_notes_but_not_24h_sms_sended_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2,
            ticket_details_1_with_confirmation_note, ticket_details_2_with_confirmation_note):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
        ]

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

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

        tz_1 = timezone(f'US/Pacific')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')),
            'timezone': tz_1
        }
        tz_2 = timezone(f'US/Eastern')
        datetime_return_2 = {
            'datetime_localized': tz_2.localize(datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')),
            'timezone': tz_2
        }
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]
        # First not skipped, Second skipped
        responses_get_diff_hours = [
            lit_dispatch_monitor.HOURS_24 - 1,
            lit_dispatch_monitor.HOURS_24 - 1
        ]

        responses_send_tech_24_sms_mock = [
            True,
            False
        ]

        responses_send_tech_24_sms_note_mock = [
            False
        ]

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._send_tech_24_sms = CoroutineMock(side_effect=responses_send_tech_24_sms_mock)
        lit_dispatch_monitor._append_tech_24_sms_note = CoroutineMock(side_effect=responses_send_tech_24_sms_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
            call(dispatch_confirmed_2, dispatch_number_2, ticket_id_2),
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._append_confirmed_note.assert_not_awaited()
        lit_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

        lit_dispatch_monitor._send_tech_24_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2)
        ])
        lit_dispatch_monitor._append_tech_24_sms_note.assert_awaited_once_with(dispatch_number_1, ticket_id_1, sms_to)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_sms_and_24h_sms_and_2h_sms_notes_test(self, lit_dispatch_monitor,
        dispatch_confirmed, dispatch_confirmed_2,
        ticket_details_1_with_24h_sms_note, ticket_details_2_with_24h_sms_note):

        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
        ]

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

        responses_details_mock = [
            ticket_details_1_with_24h_sms_note,
            ticket_details_2_with_24h_sms_note
        ]

        responses_append_confirmed_notes_mock = [
            True,
            True,
        ]
        responses_confirmed_sms = [
            True,
            True
        ]

        tz_1 = timezone(f'US/Pacific')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')),
            'timezone': tz_1
        }
        tz_2 = timezone(f'US/Eastern')
        datetime_return_2 = {
            'datetime_localized': tz_2.localize(datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')),
            'timezone': tz_2
        }
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]
        # First not skipped, Second skipped
        responses_get_diff_hours = [
            lit_dispatch_monitor.HOURS_2 - 1,
            lit_dispatch_monitor.HOURS_2 + 1
        ]

        responses_send_tech_24_sms_mock = [
            True,
            True
        ]

        responses_send_tech_24_sms_note_mock = [
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

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._send_tech_24_sms = CoroutineMock(side_effect=responses_send_tech_24_sms_mock)
        lit_dispatch_monitor._append_tech_24_sms_note = CoroutineMock(side_effect=responses_send_tech_24_sms_note_mock)
        lit_dispatch_monitor._send_tech_2_sms = CoroutineMock(side_effect=responses_send_tech_2_sms_mock)
        lit_dispatch_monitor._append_tech_2_sms_note = CoroutineMock(side_effect=responses_send_tech_2_sms_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
            call(dispatch_confirmed_2, dispatch_number_2, ticket_id_2),
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._append_confirmed_note.assert_not_awaited()
        lit_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

        lit_dispatch_monitor._send_tech_24_sms.assert_not_awaited()
        lit_dispatch_monitor._append_tech_24_sms_note.assert_not_awaited()

        lit_dispatch_monitor._send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        ])

        lit_dispatch_monitor._append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_and_confirmed_sms_and_2h_sms_notes_but_not_24h_sms_sended_test(
        self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2,
        ticket_details_1_with_24h_sms_note, ticket_details_2_with_24h_sms_note):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
        ]

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

        responses_details_mock = [
            ticket_details_1_with_24h_sms_note,
            ticket_details_2_with_24h_sms_note
        ]

        responses_append_confirmed_notes_mock = [
            True,
            True,
        ]
        responses_confirmed_sms = [
            True,
            True
        ]

        tz_1 = timezone(f'US/Pacific')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')),
            'timezone': tz_1
        }
        tz_2 = timezone(f'US/Eastern')
        datetime_return_2 = {
            'datetime_localized': tz_2.localize(datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')),
            'timezone': tz_2
        }
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]
        # First not skipped, Second skipped
        responses_get_diff_hours = [
            lit_dispatch_monitor.HOURS_2 - 1,
            lit_dispatch_monitor.HOURS_2 - 1
        ]

        responses_send_tech_24_sms_mock = [
            True,
            True
        ]

        responses_send_tech_24_sms_note_mock = [
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

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._send_tech_24_sms = CoroutineMock(side_effect=responses_send_tech_24_sms_mock)
        lit_dispatch_monitor._append_tech_24_sms_note = CoroutineMock(side_effect=responses_send_tech_24_sms_note_mock)
        lit_dispatch_monitor._send_tech_2_sms = CoroutineMock(side_effect=responses_send_tech_2_sms_mock)
        lit_dispatch_monitor._append_tech_2_sms_note = CoroutineMock(side_effect=responses_send_tech_2_sms_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
            call(dispatch_confirmed_2, dispatch_number_2, ticket_id_2),
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._append_confirmed_note.assert_not_awaited()
        lit_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

        lit_dispatch_monitor._send_tech_24_sms.assert_not_awaited()
        lit_dispatch_monitor._append_tech_24_sms_note.assert_not_awaited()

        lit_dispatch_monitor._send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2)
        ])

        lit_dispatch_monitor._append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_and_confirmed_sms_and_2h_sms_notes_but_sms_2h_sms_not_sended_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2,
            ticket_details_1_with_24h_sms_note, ticket_details_2_with_24h_sms_note):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
        ]

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

        responses_details_mock = [
            ticket_details_1_with_24h_sms_note,
            ticket_details_2_with_24h_sms_note
        ]

        responses_append_confirmed_notes_mock = [
            True,
            True,
        ]
        responses_confirmed_sms = [
            True,
            True
        ]

        tz_1 = timezone(f'US/Pacific')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')),
            'timezone': tz_1
        }
        tz_2 = timezone(f'US/Eastern')
        datetime_return_2 = {
            'datetime_localized': tz_2.localize(datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')),
            'timezone': tz_2
        }
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]
        # First not skipped, Second skipped
        responses_get_diff_hours = [
            lit_dispatch_monitor.HOURS_2 - 1,
            lit_dispatch_monitor.HOURS_2 - 1
        ]

        responses_send_tech_24_sms_mock = [
            True,
            True
        ]

        responses_send_tech_24_sms_note_mock = [
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

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._send_tech_24_sms = CoroutineMock(side_effect=responses_send_tech_24_sms_mock)
        lit_dispatch_monitor._append_tech_24_sms_note = CoroutineMock(side_effect=responses_send_tech_24_sms_note_mock)
        lit_dispatch_monitor._send_tech_2_sms = CoroutineMock(side_effect=responses_send_tech_2_sms_mock)
        lit_dispatch_monitor._append_tech_2_sms_note = CoroutineMock(side_effect=responses_send_tech_2_sms_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
            call(dispatch_confirmed_2, dispatch_number_2, ticket_id_2),
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._append_confirmed_note.assert_not_awaited()
        lit_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

        lit_dispatch_monitor._send_tech_24_sms.assert_not_awaited()
        lit_dispatch_monitor._append_tech_24_sms_note.assert_not_awaited()

        lit_dispatch_monitor._send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2)
        ])

        lit_dispatch_monitor._append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_and_confirmed_sms_and_2h_sms_notes_sended_ok_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2,
            ticket_details_1_with_24h_sms_note, ticket_details_2_with_24h_sms_note):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
        ]

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

        responses_details_mock = [
            ticket_details_1_with_24h_sms_note,
            ticket_details_2_with_24h_sms_note
        ]

        responses_append_confirmed_notes_mock = [
            True,
            True,
        ]
        responses_confirmed_sms = [
            True,
            True
        ]

        tz_1 = timezone(f'US/Pacific')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')),
            'timezone': tz_1
        }
        tz_2 = timezone(f'US/Eastern')
        datetime_return_2 = {
            'datetime_localized': tz_2.localize(datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')),
            'timezone': tz_2
        }
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]
        # First not skipped, Second skipped
        responses_get_diff_hours = [
            lit_dispatch_monitor.HOURS_2 - 1,
            lit_dispatch_monitor.HOURS_2 - 1
        ]

        responses_send_tech_24_sms_mock = [
            True,
            True
        ]

        responses_send_tech_24_sms_note_mock = [
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

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._send_tech_24_sms = CoroutineMock(side_effect=responses_send_tech_24_sms_mock)
        lit_dispatch_monitor._append_tech_24_sms_note = CoroutineMock(side_effect=responses_send_tech_24_sms_note_mock)
        lit_dispatch_monitor._send_tech_2_sms = CoroutineMock(side_effect=responses_send_tech_2_sms_mock)
        lit_dispatch_monitor._append_tech_2_sms_note = CoroutineMock(side_effect=responses_send_tech_2_sms_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
            call(dispatch_confirmed_2, dispatch_number_2, ticket_id_2),
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._append_confirmed_note.assert_not_awaited()
        lit_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

        lit_dispatch_monitor._send_tech_24_sms.assert_not_awaited()
        lit_dispatch_monitor._append_tech_24_sms_note.assert_not_awaited()

        lit_dispatch_monitor._send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2)
        ])

        lit_dispatch_monitor._append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to),
            call(dispatch_number_2, ticket_id_2, sms_to_2)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_2h_sms_and_note_sended_test(self, lit_dispatch_monitor,
                                                            dispatch_confirmed, dispatch_confirmed_2,
                                                            ticket_details_1_with_2h_sms_note,
                                                            ticket_details_2_with_2h_sms_note):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
        ]

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

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

        tz_1 = timezone(f'US/Pacific')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')),
            'timezone': tz_1
        }
        tz_2 = timezone(f'US/Eastern')
        datetime_return_2 = {
            'datetime_localized': tz_2.localize(datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')),
            'timezone': tz_2
        }
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]
        # First not skipped, Second skipped
        responses_get_diff_hours = [
            lit_dispatch_monitor.HOURS_2 - 1,
            lit_dispatch_monitor.HOURS_2 + 1
        ]

        responses_send_tech_24_sms_mock = [
            True,
            True
        ]

        responses_send_tech_24_sms_note_mock = [
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

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._append_confirmed_note = CoroutineMock(side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._send_tech_24_sms = CoroutineMock(side_effect=responses_send_tech_24_sms_mock)
        lit_dispatch_monitor._append_tech_24_sms_note = CoroutineMock(side_effect=responses_send_tech_24_sms_note_mock)
        lit_dispatch_monitor._send_tech_2_sms = CoroutineMock()
        lit_dispatch_monitor._append_tech_2_sms_note = CoroutineMock()

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
            call(dispatch_confirmed_2, dispatch_number_2, ticket_id_2),
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._append_confirmed_note.assert_not_awaited()
        lit_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

        lit_dispatch_monitor._send_tech_24_sms.assert_not_awaited()
        lit_dispatch_monitor._append_tech_24_sms_note.assert_not_awaited()

        lit_dispatch_monitor._send_tech_2_sms.assert_not_awaited()
        lit_dispatch_monitor._append_tech_2_sms_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_test(self, lit_dispatch_monitor, dispatch_tech_on_site,
                                                   dispatch_tech_on_site_2, ticket_details_1, ticket_details_2,
                                                   append_note_response, append_note_response_2,
                                                   sms_success_response, sms_success_response_2):
        tech_on_site_dispatches = [
            dispatch_tech_on_site,
            dispatch_tech_on_site_2
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

        sms_note_1 = '#*Automation Engine*#\nDispatch Management - Field Engineer On Site\n\nJoe Malone has arrived\n'
        sms_note_2 = '#*Automation Engine*#\nDispatch Management - Field Engineer On Site\n\nHulk Hogan has arrived\n'

        dispatch_number_1 = dispatch_tech_on_site.get('Dispatch_Number')
        dispatch_number_2 = dispatch_tech_on_site_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_tech_on_site.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_tech_on_site_2.get('MetTel_Bruin_TicketID')

        tech_on_site_sms_note_1 = '#*Automation Engine*#\n' \
                                  'Dispatch Management - Field Engineer On Site\n\n' \
                                  'Joe Malone has arrived\n'
        tech_on_site_sms_note_2 = '#*Automation Engine*#\n' \
                                  'Dispatch Management - Field Engineer On Site\n\n' \
                                  'Hulk Hogan has arrived\n'

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

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

        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        # lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(side_effect=responses_append_notes_mock)
        lit_dispatch_monitor._send_tech_on_site_sms = CoroutineMock(side_effect=responses_sms_tech_on_site_mock)
        lit_dispatch_monitor._append_tech_on_site_sms_note = CoroutineMock(side_effect=responses_append_tech_on_site_sms_note_mock)

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        """
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, tech_on_site_sms_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_2, tech_on_site_sms_note_2),
            call(ticket_id_2, sms_note_2)
        ])
        """

        lit_dispatch_monitor._send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_tech_on_site, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_tech_on_site_2, sms_to_2)
        ])

        lit_dispatch_monitor._append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, dispatch_tech_on_site.get('Tech_First_Name')),
            call(dispatch_number_2, ticket_id_2, sms_to_2, dispatch_tech_on_site_2.get('Tech_First_Name'))
        ])

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_with_exception_test(self, lit_dispatch_monitor, dispatch_tech_on_site):
        tech_on_site_dispatches = [
            dispatch_tech_on_site
        ]
        lit_dispatch_monitor.get_dispatch_confirmed_date_time_localized = Mock(side_effect=Exception)

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches)

        lit_dispatch_monitor._logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_skipping_one_invalid_ticket_id_test(self, lit_dispatch_monitor,
                                                                                  dispatch_tech_on_site_skipped):
        tech_on_site_dispatches = [
            dispatch_tech_on_site_skipped
        ]

        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock()
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock()
        lit_dispatch_monitor._send_confirmed_sms = CoroutineMock()

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_not_awaited()
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        lit_dispatch_monitor._send_confirmed_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_skipping_one_invalid_sms_to_test(self, lit_dispatch_monitor,
                                                                            dispatch_tech_on_site_skipped_bad_phone):
        tech_on_site_dispatches = [
            dispatch_tech_on_site_skipped_bad_phone
        ]

        dispatch_number_1 = dispatch_tech_on_site_skipped_bad_phone.get('Dispatch_Number')
        ticket_id_1 = dispatch_tech_on_site_skipped_bad_phone.get('MetTel_Bruin_TicketID')

        err_msg = f"An error occurred retrieve 'sms_to' number " \
                  f"Dispatch: {dispatch_number_1} - Ticket_id: {ticket_id_1} - " \
                  f"from: {dispatch_tech_on_site_skipped_bad_phone.get('Job_Site_Contact_Name_and_Phone_Number')}"

        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(return_value=err_msg)

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_error_getting_ticket_details_test(self, lit_dispatch_monitor,
        dispatch_tech_on_site, dispatch_tech_on_site_2, ticket_details_1, ticket_details_2_error):
        tech_on_site_dispatches = [
            dispatch_tech_on_site,
            dispatch_tech_on_site_2
        ]

        sms_note_1 = '#*Automation Engine*#\nDispatch Management - Field Engineer On Site\n\nJoe Malone has arrived\n'

        dispatch_number_1 = dispatch_tech_on_site.get('Dispatch_Number')
        dispatch_number_2 = dispatch_tech_on_site_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_tech_on_site.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_tech_on_site_2.get('MetTel_Bruin_TicketID')

        tech_on_site_sms_note_1 = '#*Automation Engine*#\n' \
                                  'Dispatch Management - Field Engineer On Site\n\n' \
                                  'Joe Malone has arrived\n'

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

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

        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)

        lit_dispatch_monitor._send_tech_on_site_sms = CoroutineMock(side_effect=responses_sms_tech_on_site_mock)
        lit_dispatch_monitor._append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        err_msg = f"An error occurred retrieve getting ticket details from bruin " \
                  f"Dispatch: {dispatch_number_2} - Ticket_id: {ticket_id_2}"

        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(return_value=err_msg)

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_tech_on_site, sms_to)
        ])

        lit_dispatch_monitor._append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, dispatch_tech_on_site.get('Tech_First_Name'))
        ])

        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_watermark_not_found_test(self, lit_dispatch_monitor,
                                                                       dispatch_tech_on_site,
                                                                       dispatch_tech_on_site_2,
                                                                       ticket_details_1,
                                                                       ticket_details_2_no_requested_watermark):
        tech_on_site_dispatches = [
            dispatch_tech_on_site,
            dispatch_tech_on_site_2
        ]

        sms_note_1 = '#*Automation Engine*#\nDispatch Management - Field Engineer On Site\n\nJoe Malone has arrived\n'

        dispatch_number_1 = dispatch_tech_on_site.get('Dispatch_Number')
        dispatch_number_2 = dispatch_tech_on_site_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_tech_on_site.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_tech_on_site_2.get('MetTel_Bruin_TicketID')

        tech_on_site_sms_note_1 = '#*Automation Engine*#\n' \
                                  'Dispatch Management - Field Engineer On Site\n\n' \
                                  'Joe Malone has arrived\n'

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

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

        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)

        lit_dispatch_monitor._send_tech_on_site_sms = CoroutineMock(side_effect=responses_sms_tech_on_site_mock)
        lit_dispatch_monitor._append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_tech_on_site, sms_to)
        ])

        lit_dispatch_monitor._append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, dispatch_tech_on_site.get('Tech_First_Name'))
        ])

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_sms_not_sended_test(self, lit_dispatch_monitor,
                                                                        dispatch_tech_on_site,
                                                                        dispatch_tech_on_site_2,
                                                                        ticket_details_1,
                                                                        ticket_details_2):
        tech_on_site_dispatches = [
            dispatch_tech_on_site,
            dispatch_tech_on_site_2
        ]

        dispatch_number_1 = dispatch_tech_on_site.get('Dispatch_Number')
        dispatch_number_2 = dispatch_tech_on_site_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_tech_on_site.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_tech_on_site_2.get('MetTel_Bruin_TicketID')

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

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

        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)

        lit_dispatch_monitor._send_tech_on_site_sms = CoroutineMock(side_effect=responses_sms_tech_on_site_mock)
        lit_dispatch_monitor._append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_tech_on_site, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_tech_on_site_2, sms_to_2)
        ])

        lit_dispatch_monitor._append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, dispatch_tech_on_site.get('Tech_First_Name'))
        ])

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_sms_note_not_appended_test(self, lit_dispatch_monitor,
                                                                               dispatch_tech_on_site,
                                                                               dispatch_tech_on_site_2,
                                                                               ticket_details_1,
                                                                               ticket_details_2):
        tech_on_site_dispatches = [
            dispatch_tech_on_site,
            dispatch_tech_on_site_2
        ]

        dispatch_number_1 = dispatch_tech_on_site.get('Dispatch_Number')
        dispatch_number_2 = dispatch_tech_on_site_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_tech_on_site.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_tech_on_site_2.get('MetTel_Bruin_TicketID')

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

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

        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)

        lit_dispatch_monitor._send_tech_on_site_sms = CoroutineMock(side_effect=responses_sms_tech_on_site_mock)
        lit_dispatch_monitor._append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_tech_on_site, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_tech_on_site_2, sms_to_2)
        ])

        lit_dispatch_monitor._append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, dispatch_tech_on_site.get('Tech_First_Name')),
            call(dispatch_number_2, ticket_id_2, sms_to_2, dispatch_tech_on_site_2.get('Tech_First_Name'))
        ])

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_with_tech_on_site_note_already_sended_ok_test(self, lit_dispatch_monitor,
        dispatch_tech_on_site, dispatch_tech_on_site_2, ticket_details_1_with_tech_on_site_sms_note,
                                                                                            ticket_details_2_with_tech_on_site_sms_note):
        tech_on_site_dispatches = [
            dispatch_tech_on_site,
            dispatch_tech_on_site_2
        ]

        dispatch_number_1 = dispatch_tech_on_site.get('Dispatch_Number')
        dispatch_number_2 = dispatch_tech_on_site_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_tech_on_site.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_tech_on_site_2.get('MetTel_Bruin_TicketID')

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

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

        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)

        lit_dispatch_monitor._send_tech_on_site_sms = CoroutineMock()
        lit_dispatch_monitor._append_tech_on_site_sms_note = CoroutineMock()

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._send_tech_on_site_sms.assert_not_awaited()
        lit_dispatch_monitor._append_tech_on_site_sms_note.assert_not_awaited()
