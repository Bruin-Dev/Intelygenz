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

from application.templates.lit.sms.dispatch_confirmed import lit_get_dispatch_confirmed_sms
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

    def is_repair_completed_test(self, lit_dispatch_monitor, dispatch_completed, dispatch_not_completed):
        assert lit_dispatch_monitor._is_repair_completed(dispatch_completed) is True
        assert lit_dispatch_monitor._is_repair_completed(dispatch_not_completed) is False

    def get_dispatches_splitted_by_status_test(self, lit_dispatch_monitor, dispatch, dispatch_confirmed,
                                               dispatch_tech_on_site, dispatch_completed):
        dispatches = [dispatch, dispatch_confirmed, dispatch_tech_on_site, dispatch_completed]
        expected_dispatches_splitted = {
            str(lit_dispatch_monitor.DISPATCH_REQUESTED): [dispatch],
            str(lit_dispatch_monitor.DISPATCH_CONFIRMED): [dispatch_confirmed],
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

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])

        response = await lit_dispatch_monitor._send_confirmed_sms(dispatch_number, ticket_id, dispatch, sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

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

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +1987654327\n'
        sms_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +1987654327\n'

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
                           'Dispatch scheduled for 2020-03-16 @ 10:30AM-11:30PM Eastern Time\n\n' \
                           'Field Engineer\nHulk Hogan\n+12123596666\n'

        sms_to = '+1987654327'
        sms_to_2 = '+1987654327'

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
