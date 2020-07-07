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

from application.actions.lit_dispatch_monitor import LitDispatchMonitor
from application.actions import lit_dispatch_monitor as lit_dispatch_monitor_module

from application.repositories.utils_repository import UtilsRepository
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
        splitted_dispatches = {}
        for ds in lit_dispatch_monitor._lit_repository._dispatch_statuses:
            splitted_dispatches[ds] = []
        splitted_dispatches[str(lit_dispatch_monitor._lit_repository.DISPATCH_REQUESTED)] = [dispatch]
        splitted_dispatches[str(lit_dispatch_monitor._lit_repository.DISPATCH_CONFIRMED)] = [dispatch_confirmed]

        confirmed_dispatches = [dispatch_confirmed]
        lit_dispatch_monitor._lit_repository.get_all_dispatches = CoroutineMock(return_value=dispatches_response)
        lit_dispatch_monitor._lit_repository._get_dispatches_splitted_by_status = \
            Mock(return_value=splitted_dispatches)
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
        err_msg = f'An error occurred retrieving all dispatches in the request status from LIT.'
        lit_dispatch_monitor._lit_repository.get_all_dispatches = CoroutineMock(return_value=dispatches_response)
        lit_dispatch_monitor._monitor_confirmed_dispatches = CoroutineMock()
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await lit_dispatch_monitor._lit_dispatch_monitoring_process()

        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)
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
        err_msg = f'An error occurred retrieving all dispatches from LIT.'

        lit_dispatch_monitor._lit_repository.get_all_dispatches = CoroutineMock(return_value=dispatches_response)
        lit_dispatch_monitor._monitor_confirmed_dispatches = CoroutineMock()
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await lit_dispatch_monitor._lit_dispatch_monitoring_process()

        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)
        lit_dispatch_monitor._monitor_confirmed_dispatches.assert_not_awaited()

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_test(self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2,
                                                dispatch_confirmed_tech_phone_none,
                                                ticket_details_1, ticket_details_2, ticket_details_3,
                                                append_note_response, append_note_response_2,
                                                sms_success_response, sms_success_response_2):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2,
            dispatch_confirmed_tech_phone_none
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
        sms_note_3 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595126\n'
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'
        sms_tech_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595126\n'

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        dispatch_number_3 = dispatch_confirmed_tech_phone_none.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')
        ticket_id_3 = dispatch_confirmed_tech_phone_none.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'
        confirmed_note_2 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 10:30AM-11:30AM Eastern Time\n\n' \
                           'Field Engineer\nHulk Hogan\n+12123595126\n'
        confirmed_note_3 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 09:30AM-11:30AM Central Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595126\n'

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'
        sms_to_3 = '+12123595126'

        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595126'
        sms_to_3_tech = None

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
            ticket_details_2,
            ticket_details_3
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_2,
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
            False
        ]

        tz_1 = timezone(f'US/Pacific')
        tz_2 = timezone(f'US/Eastern')
        tz_3 = timezone(f'US/Central')
        datetime_1 = datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')
        datetime_2 = datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')
        datetime_3 = datetime.strptime('2020-03-16 09:30AM', '%Y-%m-%d %I:%M%p')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime_1),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = {
            'datetime_localized': tz_2.localize(datetime_2),
            'timezone': timezone(f'US/Eastern')
        }
        datetime_return_3 = {
            'datetime_localized': tz_3.localize(datetime_3),
            'timezone': timezone(f'US/Central')
        }
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2,
            datetime_return_3
        ]
        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)

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
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1),
            call(ticket_id_2, confirmed_note_2),
            call(ticket_id_2, sms_note_2),
            call(ticket_id_2, sms_tech_note_2)
        ])

        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2)
        ])

        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_general_exception_test(self, lit_dispatch_monitor):
        confirmed_dispatches = 0  # Non valid list for filter
        err_msg = f"Error: _monitor_confirmed_dispatches - object of type 'int' has no len()"
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches)

        lit_dispatch_monitor._logger.error.assert_called_once()
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_exception_test(self, lit_dispatch_monitor, dispatch_confirmed):
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        ticket_id = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        confirmed_dispatches = [
            dispatch_confirmed
        ]
        err_msg = f"Error: Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                  f"- {dispatch_confirmed}"
        lit_dispatch_monitor.get_dispatch_confirmed_date_time_localized = Mock(side_effect=Exception)
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches)

        lit_dispatch_monitor._logger.error.assert_called_once()
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skipping_one_invalid_ticket_id_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_skipped, ticket_details_1,
            append_note_response):
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
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'

        sms_to = '+12123595129'
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

        tz_1 = timezone(f'US/Pacific')
        datetime_1 = datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime_1),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_returns_mock = [
            datetime_return_1
        ]
        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms)

        await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        ])

        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_awaited_once_with(
            dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skipping_one_invalid_datetime_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_skipped_datetime, ticket_details_1,
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
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        dispatch_number_2 = dispatch_confirmed_skipped_datetime.get('Dispatch_Number')
        ticket_id_2 = dispatch_confirmed_skipped_datetime.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'

        sms_to = '+12123595129'
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

        tz_1 = timezone(f'US/Pacific')
        datetime_1 = datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime_1),
            'timezone': timezone(f'US/Pacific')
        }

        datetime_return_2 = None
        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]
        err_msg = f"Dispatch: {dispatch_number_2} - Ticket_id: {ticket_id_2} - " \
                  f"An error occurred retrieve datetime of dispatch: " \
                  f"{dispatch_confirmed_skipped_datetime.get('Hard_Time_of_Dispatch_Local', None)} - " \
                  f"{dispatch_confirmed_skipped_datetime.get('Hard_Time_of_Dispatch_Time_Zone_Local', None)} "
        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await lit_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_confirmed, dispatch_number_1, ticket_id_1),
        ])

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        ])

        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech)
        ])

        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skipping_one_invalid_sms_to_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_skipped_bad_phone, ticket_details_1,
            ticket_details_2, append_note_response):
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
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        dispatch_number_2 = dispatch_confirmed_skipped_bad_phone.get('Dispatch_Number')
        ticket_id_2 = dispatch_confirmed_skipped_bad_phone.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'

        sms_to = '+12123595129'
        sms_to_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2,
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_1,
            response_append_note_1,
            response_append_note_1,
            response_append_note_1,
            response_append_note_1
        ]
        responses_confirmed_sms = [
            True,
            True
        ]
        tz_1 = timezone(f'US/Pacific')
        tz_2 = timezone(f'US/Eastern')
        datetime_1 = datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')
        datetime_2 = datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime_1),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = {
            'datetime_localized': tz_2.localize(datetime_2),
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
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms)
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
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        ])
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech)
        ])

        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skipping_one_invalid_sms_to_tech_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_skipped_bad_phone_tech,
            ticket_details_1, ticket_details_2, append_note_response):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_skipped_bad_phone_tech
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595129\n'
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        dispatch_number_2 = dispatch_confirmed_skipped_bad_phone_tech.get('Dispatch_Number')
        ticket_id_2 = dispatch_confirmed_skipped_bad_phone_tech.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'

        sms_to = '+12123595129'
        sms_to_tech = '+12123595129'

        responses_details_mock = [
            ticket_details_1,
            ticket_details_2,
        ]
        responses_append_notes_mock = [
            response_append_note_1,
            response_append_note_1,
            response_append_note_1,
            response_append_note_1,
            response_append_note_1,
            response_append_note_1
        ]
        responses_confirmed_sms = [
            True,
            True
        ]
        tz_1 = timezone(f'US/Pacific')
        tz_2 = timezone(f'US/Eastern')
        datetime_1 = datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')
        datetime_2 = datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime_1),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = {
            'datetime_localized': tz_2.localize(datetime_2),
            'timezone': timezone(f'US/Eastern')
        }

        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2
        ]

        err_msg = f"An error occurred retrieve 'sms_to_tech' number " \
                  f"Dispatch: {dispatch_number_2} - Ticket_id: {ticket_id_2} - " \
                  f"from: {dispatch_confirmed_skipped_bad_phone_tech.get('Tech_Mobile_Number')}"

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms)
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
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        ])
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech)
        ])

        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_error_getting_ticket_details_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2, ticket_details_1,
            ticket_details_2_error, append_note_response):
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
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'

        sms_to = '+12123595129'
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

        tz_1 = timezone(f'US/Pacific')
        tz_2 = timezone(f'US/Eastern')
        datetime_1 = datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')
        datetime_2 = datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime_1),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = {
            'datetime_localized': tz_2.localize(datetime_2),
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
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_to_slack_mock)
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms)

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
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        ])
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech)
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
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

        confirmed_note_1 = '#*Automation Engine*#\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n\n' \
                           'Field Engineer\nJoe Malone\n+12123595129\n'

        sms_to = '+12123595129'
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

        tz_1 = timezone(f'US/Pacific')
        tz_2 = timezone(f'US/Eastern')
        datetime_1 = datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')
        datetime_2 = datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime_1),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = {
            'datetime_localized': tz_2.localize(datetime_2),
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
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms)

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
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1),
        ])

        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        ])
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech)
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
        sms_tech_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'
        sms_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595126\n'

        sms_to = '+12123595129'
        sms_to_tech = '+12123595129'

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

        tz_1 = timezone(f'US/Pacific')
        tz_2 = timezone(f'US/Eastern')
        datetime_1 = datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')
        datetime_2 = datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime_1),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = {
            'datetime_localized': tz_2.localize(datetime_2),
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
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)
        lit_dispatch_monitor._lit_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_note_mock)
        lit_dispatch_monitor._lit_repository.append_confirmed_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_send_confirmed_sms_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_send_confirmed_sms_mock)
        lit_dispatch_monitor._lit_repository.append_confirmed_sms_tech_note = CoroutineMock(
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

        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        ])
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech)
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
        sms_note_1 = '#*Automation Engine*#\nDispatch confirmation SMS tech sent to +12123595129\n'
        sms_note_2 = '#*Automation Engine*#\nDispatch confirmation SMS sent to +12123595126\n'

        sms_to = '+12123595129'
        sms_to_tech = '+12123595129'
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

        tz_1 = timezone(f'US/Pacific')
        tz_2 = timezone(f'US/Eastern')
        datetime_1 = datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')
        datetime_2 = datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime_1),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = {
            'datetime_localized': tz_2.localize(datetime_2),
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
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_send_confirmed_sms_mock)
        lit_dispatch_monitor._lit_repository.append_confirmed_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_send_confirmed_sms_mock)
        lit_dispatch_monitor._lit_repository.append_confirmed_sms_tech_note = CoroutineMock(
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

        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2)
        ])
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech)
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
        sms_to_tech = '+12123595129'
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

        tz_1 = timezone(f'US/Pacific')
        tz_2 = timezone(f'US/Eastern')
        datetime_1 = datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')
        datetime_2 = datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')
        datetime_return_1 = {
            'datetime_localized': tz_1.localize(datetime_1),
            'timezone': timezone(f'US/Pacific')
        }
        datetime_return_2 = {
            'datetime_localized': tz_2.localize(datetime_2),
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
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_send_confirmed_sms_mock)
        lit_dispatch_monitor._lit_repository.append_confirmed_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_send_confirmed_sms_mock)
        lit_dispatch_monitor._lit_repository.append_confirmed_sms_tech_note = CoroutineMock(
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

        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2)
        ])

        lit_dispatch_monitor._lit_repository.append_confirmed_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to),
            call(dispatch_number_2, ticket_id_2, sms_to_2),
        ])
        lit_dispatch_monitor._lit_repository.append_confirmed_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_sms_and_12h_sms_notes_test(
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
            lit_dispatch_monitor.HOURS_12 - 1,
            lit_dispatch_monitor.HOURS_12 - 1,
            lit_dispatch_monitor.HOURS_12 + 1,
            lit_dispatch_monitor.HOURS_12 + 1
        ]

        responses_send_tech_12_sms_mock = [
            True
        ]

        responses_send_tech_12_sms_note_mock = [
            True
        ]

        sms_to = '+12123595129'
        sms_to_tech = '+12123595129'

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)
        lit_dispatch_monitor._lit_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        lit_dispatch_monitor._lit_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)

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

        lit_dispatch_monitor._lit_repository.append_confirmed_note.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_not_awaited()

        lit_dispatch_monitor._lit_repository.send_tech_12_sms.assert_awaited_once_with(
            dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_note.assert_awaited_once_with(
            dispatch_number_1, ticket_id_1, sms_to)
        lit_dispatch_monitor._lit_repository.send_tech_12_sms_tech.assert_awaited_once_with(
            dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech)
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_tech_note.assert_awaited_once_with(
            dispatch_number_1, ticket_id_1, sms_to_tech)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_and_confirmed_sms_notes_but_not_12h_sms_sended_test(
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
            lit_dispatch_monitor.HOURS_12 - 1,
            lit_dispatch_monitor.HOURS_12 - 1,
            lit_dispatch_monitor.HOURS_12 - 1,
            lit_dispatch_monitor.HOURS_12 - 1
        ]

        responses_send_tech_12_sms_mock = [
            True,
            False
        ]

        responses_send_tech_12_sms_note_mock = [
            False
        ]

        sms_to = '+12123595129'
        sms_to_tech = '+12123595129'
        sms_to_2 = '+12123595126'
        sms_to_2_tech = '+12123595126'

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)
        lit_dispatch_monitor._lit_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)

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

        lit_dispatch_monitor._lit_repository.append_confirmed_note.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_not_awaited()

        lit_dispatch_monitor._lit_repository.send_tech_12_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2)
        ])
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_note.assert_awaited_once_with(
            dispatch_number_1, ticket_id_1, sms_to)
        lit_dispatch_monitor._lit_repository.send_tech_12_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2_tech)
        ])
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_tech_note.assert_awaited_once_with(
            dispatch_number_1, ticket_id_1, sms_to_tech)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_sms_and_12h_sms_and_2h_sms_notes_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2,
            ticket_details_1_with_12h_sms_note, ticket_details_2_with_12h_sms_note):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
        ]

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

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
            lit_dispatch_monitor.HOURS_2 - 1,
            lit_dispatch_monitor.HOURS_2 + 1,
            lit_dispatch_monitor.HOURS_2 + 1
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
            True
        ]

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'
        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595126'

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)
        lit_dispatch_monitor._lit_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_tech_2_sms = CoroutineMock(
            side_effect=responses_send_tech_2_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_2_sms_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_tech_2_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_2_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_2_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_note_mock)

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

        lit_dispatch_monitor._lit_repository.append_confirmed_note.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_not_awaited()

        lit_dispatch_monitor._lit_repository.send_tech_12_sms.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_note.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_tech_12_sms_tech.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_tech_note.assert_not_awaited()

        lit_dispatch_monitor._lit_repository.send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to)
        ])

        lit_dispatch_monitor._lit_repository.append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to)
        ])
        lit_dispatch_monitor._lit_repository.send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech)
        ])

        lit_dispatch_monitor._lit_repository.append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_sms_and_2h_sms_notes_but_not_12h_sms_sended_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2, ticket_details_1_with_12h_sms_note,
            ticket_details_2_with_12h_sms_note):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
        ]

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

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
            lit_dispatch_monitor.HOURS_2 - 1,
            lit_dispatch_monitor.HOURS_2 - 1,
            lit_dispatch_monitor.HOURS_2 - 1
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

        sms_to = '+12123595129'
        sms_to_tech = '+12123595129'
        sms_to_2 = '+12123595126'

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)
        lit_dispatch_monitor._lit_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_tech_2_sms = CoroutineMock(
            side_effect=responses_send_tech_2_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_2_sms_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_tech_2_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_2_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_2_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_note_mock)

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

        lit_dispatch_monitor._lit_repository.append_confirmed_note.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_not_awaited()

        lit_dispatch_monitor._lit_repository.send_tech_12_sms.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_note.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_tech_12_sms_tech.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_tech_note.assert_not_awaited()

        lit_dispatch_monitor._lit_repository.send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2)
        ])

        lit_dispatch_monitor._lit_repository.append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to)
        ])

        lit_dispatch_monitor._lit_repository.send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech)
        ])

        lit_dispatch_monitor._lit_repository.append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_sms_and_2h_sms_notes_but_sms_2h_sms_not_sended_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2,
            ticket_details_1_with_12h_sms_note, ticket_details_2_with_12h_sms_note):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
        ]

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

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
            lit_dispatch_monitor.HOURS_2 - 1,
            lit_dispatch_monitor.HOURS_2 - 1,
            lit_dispatch_monitor.HOURS_2 - 1
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
            False
        ]

        responses_send_tech_2_sms_note_mock = [
            False
        ]

        sms_to = '+12123595129'
        sms_to_tech = '+12123595129'
        sms_to_2 = '+12123595126'
        sms_to_2_tech = '+12123595126'

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)
        lit_dispatch_monitor._lit_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_tech_2_sms = CoroutineMock(side_effect=responses_send_tech_2_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_2_sms_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_tech_2_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_2_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_2_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_note_mock)

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

        lit_dispatch_monitor._lit_repository.append_confirmed_note.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_not_awaited()

        lit_dispatch_monitor._lit_repository.send_tech_12_sms.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_note.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_tech_12_sms_tech.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_tech_note.assert_not_awaited()

        lit_dispatch_monitor._lit_repository.send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2)
        ])

        lit_dispatch_monitor._lit_repository.append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to)
        ])
        lit_dispatch_monitor._lit_repository.send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2_tech)
        ])

        lit_dispatch_monitor._lit_repository.append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_and_confirmed_sms_and_2h_sms_notes_sended_ok_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2,
            ticket_details_1_with_12h_sms_note, ticket_details_2_with_12h_sms_note):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
        ]

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

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
            lit_dispatch_monitor.HOURS_2 - 1,
            lit_dispatch_monitor.HOURS_2 - 1,
            lit_dispatch_monitor.HOURS_2 - 1
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
            True
        ]

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'
        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595126'

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._lit_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_tech_2_sms = CoroutineMock(side_effect=responses_send_tech_2_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_2_sms_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_tech_2_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_2_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_2_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_note_mock)

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

        lit_dispatch_monitor._lit_repository.append_confirmed_note.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_not_awaited()

        lit_dispatch_monitor._lit_repository.send_tech_12_sms.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_note.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_tech_12_sms_tech.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_tech_note.assert_not_awaited()

        lit_dispatch_monitor._lit_repository.send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2)
        ])

        lit_dispatch_monitor._lit_repository.append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to),
            call(dispatch_number_2, ticket_id_2, sms_to_2)
        ])
        lit_dispatch_monitor._lit_repository.send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2_tech)
        ])

        lit_dispatch_monitor._lit_repository.append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, sms_to_2_tech)
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_2h_sms_and_note_sended_also_tech_sms_and_note_test(
            self, lit_dispatch_monitor, dispatch_confirmed, dispatch_confirmed_2,
            ticket_details_1_with_confirmation_note_but_not_tech,
            ticket_details_2_with_confirmation_note_but_not_tech):
        confirmed_dispatches = [
            dispatch_confirmed,
            dispatch_confirmed_2
        ]

        dispatch_number_1 = dispatch_confirmed.get('Dispatch_Number')
        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_1 = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')

        responses_details_mock = [
            ticket_details_1_with_confirmation_note_but_not_tech,
            ticket_details_2_with_confirmation_note_but_not_tech
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
            True
        ]

        sms_to = '+12123595129'
        sms_to_2 = '+12123595126'

        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595126'

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._lit_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock(side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms)
        lit_dispatch_monitor._lit_repository.append_confirmed_sms_tech_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        lit_dispatch_monitor._lit_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        lit_dispatch_monitor._lit_repository.send_tech_2_sms = CoroutineMock()
        lit_dispatch_monitor._lit_repository.append_tech_2_sms_note = CoroutineMock()

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

        lit_dispatch_monitor._lit_repository.append_confirmed_note.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_not_awaited()

        lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_confirmed, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, dispatch_confirmed_2, sms_to_2_tech)
        ])

        lit_dispatch_monitor._lit_repository.send_tech_12_sms.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.append_tech_12_sms_note.assert_not_awaited()

        lit_dispatch_monitor._lit_repository.send_tech_2_sms.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.append_tech_2_sms_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_test(self, lit_dispatch_monitor, dispatch_tech_on_site,
                                                   dispatch_tech_on_site_2, dispatch_tech_on_site_bad_datetime,
                                                   ticket_details_1, ticket_details_2,
                                                   append_note_response, append_note_response_2,
                                                   sms_success_response, sms_success_response_2):
        tech_on_site_dispatches = [
            dispatch_tech_on_site,
            dispatch_tech_on_site_2,
            dispatch_tech_on_site_bad_datetime
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
        tz_3 = timezone(f'US/Pacific')
        datetime_return_3 = None

        datetime_returns_mock = [
            datetime_return_1,
            datetime_return_2,
            datetime_return_3
        ]

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
        dispatch_number_3 = dispatch_tech_on_site_bad_datetime.get('Dispatch_Number')
        ticket_id_1 = dispatch_tech_on_site.get('MetTel_Bruin_TicketID')
        ticket_id_2 = dispatch_tech_on_site_2.get('MetTel_Bruin_TicketID')
        ticket_id_3 = dispatch_tech_on_site_bad_datetime.get('MetTel_Bruin_TicketID')

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

        err_msg = 'Dispatch: DIS37406 - Ticket_id: 3544801 - ' \
                  'An error occurred retrieve datetime of dispatch: None - Eastern Time '

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized = Mock(
            side_effect=datetime_returns_mock)
        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        lit_dispatch_monitor._lit_repository.send_tech_on_site_sms = CoroutineMock(
            side_effect=responses_sms_tech_on_site_mock)
        lit_dispatch_monitor._lit_repository.append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized.assert_has_calls([
            call(dispatch_tech_on_site, dispatch_number_1, ticket_id_1),
            call(dispatch_tech_on_site_2, dispatch_number_2, ticket_id_2),
            call(dispatch_tech_on_site_bad_datetime, dispatch_number_3, ticket_id_3),
        ])

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

        lit_dispatch_monitor._lit_repository.send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_tech_on_site, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_tech_on_site_2, sms_to_2)
        ])

        lit_dispatch_monitor._lit_repository.append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, dispatch_tech_on_site.get('Tech_First_Name')),
            call(dispatch_number_2, ticket_id_2, sms_to_2, dispatch_tech_on_site_2.get('Tech_First_Name'))
        ])

        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_with_general_exception_test(
            self, lit_dispatch_monitor):
        tech_on_site_dispatches = 0  # Non valid list for filter
        err_msg = f"Error: _monitor_tech_on_site_dispatches - object of type 'int' has no len()"
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches)

        lit_dispatch_monitor._logger.error.assert_called_once()
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_with_exception_test(self, lit_dispatch_monitor, dispatch_tech_on_site):
        tech_on_site_dispatches = [
            dispatch_tech_on_site
        ]
        err_msg = f"Error: Dispatch [{dispatch_tech_on_site.get('Dispatch_Number')}] " \
                  f"in ticket_id: {dispatch_tech_on_site.get('MetTel_Bruin_TicketID')} " \
                  f"- {dispatch_tech_on_site}"
        lit_dispatch_monitor.get_dispatch_confirmed_date_time_localized = CoroutineMock(
            side_effect=Exception('mocked exception'))
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches)

        lit_dispatch_monitor._logger.error.assert_called_once()
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_skipping_one_invalid_ticket_id_test(self, lit_dispatch_monitor,
                                                                                  dispatch_tech_on_site_skipped):
        tech_on_site_dispatches = [
            dispatch_tech_on_site_skipped
        ]

        lit_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock()
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock()
        lit_dispatch_monitor._lit_repository.send_confirmed_sms = CoroutineMock()

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_not_awaited()
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.send_confirmed_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_skipping_one_invalid_sms_to_test(
            self, lit_dispatch_monitor, dispatch_tech_on_site_skipped_bad_phone):
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
    async def monitor_tech_on_site_dispatches_error_getting_ticket_details_test(
            self, lit_dispatch_monitor, dispatch_tech_on_site, dispatch_tech_on_site_2, ticket_details_1,
            ticket_details_2_error):
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

        lit_dispatch_monitor._lit_repository.send_tech_on_site_sms = CoroutineMock(
            side_effect=responses_sms_tech_on_site_mock)
        lit_dispatch_monitor._lit_repository.append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        err_msg = f"An error occurred retrieve getting ticket details from bruin " \
                  f"Dispatch: {dispatch_number_2} - Ticket_id: {ticket_id_2}"

        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(return_value=err_msg)

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._lit_repository.send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_tech_on_site, sms_to)
        ])

        lit_dispatch_monitor._lit_repository.append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, dispatch_tech_on_site.get('Tech_First_Name'))
        ])

        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_watermark_not_found_test(
            self, lit_dispatch_monitor, dispatch_tech_on_site, dispatch_tech_on_site_2, ticket_details_1,
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

        lit_dispatch_monitor._lit_repository.send_tech_on_site_sms = CoroutineMock(
            side_effect=responses_sms_tech_on_site_mock)
        lit_dispatch_monitor._lit_repository.append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._lit_repository.send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_tech_on_site, sms_to)
        ])

        lit_dispatch_monitor._lit_repository.append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, dispatch_tech_on_site.get('Tech_First_Name'))
        ])

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_sms_not_sended_test(
            self, lit_dispatch_monitor, dispatch_tech_on_site, dispatch_tech_on_site_2, ticket_details_1,
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

        lit_dispatch_monitor._lit_repository.send_tech_on_site_sms = CoroutineMock(
            side_effect=responses_sms_tech_on_site_mock)
        lit_dispatch_monitor._lit_repository.append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._lit_repository.send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_tech_on_site, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_tech_on_site_2, sms_to_2)
        ])

        lit_dispatch_monitor._lit_repository.append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, dispatch_tech_on_site.get('Tech_First_Name'))
        ])

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_sms_note_not_appended_test(
            self, lit_dispatch_monitor, dispatch_tech_on_site, dispatch_tech_on_site_2, ticket_details_1,
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

        lit_dispatch_monitor._lit_repository.send_tech_on_site_sms = CoroutineMock(
            side_effect=responses_sms_tech_on_site_mock)
        lit_dispatch_monitor._lit_repository.append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._lit_repository.send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, dispatch_tech_on_site, sms_to),
            call(dispatch_number_2, ticket_id_2, dispatch_tech_on_site_2, sms_to_2)
        ])

        lit_dispatch_monitor._lit_repository.append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, dispatch_tech_on_site.get('Tech_First_Name')),
            call(dispatch_number_2, ticket_id_2, sms_to_2, dispatch_tech_on_site_2.get('Tech_First_Name'))
        ])

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_with_tech_on_site_note_already_sended_ok_test(
            self, lit_dispatch_monitor, dispatch_tech_on_site, dispatch_tech_on_site_2,
            ticket_details_1_with_tech_on_site_sms_note, ticket_details_2_with_tech_on_site_sms_note):
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

        lit_dispatch_monitor._lit_repository.send_tech_on_site_sms = CoroutineMock()
        lit_dispatch_monitor._lit_repository.append_tech_on_site_sms_note = CoroutineMock()

        await lit_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        lit_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        lit_dispatch_monitor._lit_repository.send_tech_on_site_sms.assert_not_awaited()
        lit_dispatch_monitor._lit_repository.append_tech_on_site_sms_note.assert_not_awaited()
