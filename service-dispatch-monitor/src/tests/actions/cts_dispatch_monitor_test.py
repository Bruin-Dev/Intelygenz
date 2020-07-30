from datetime import datetime
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import iso8601
import pytest
import pytz

from apscheduler.util import undefined
from asynctest import CoroutineMock
from pytz import timezone
from shortuuid import uuid

from application.actions.cts_dispatch_monitor import CtsDispatchMonitor
from application.actions import cts_dispatch_monitor as cts_dispatch_monitor_module
from application.repositories.utils_repository import UtilsRepository
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
        for ds in cts_dispatch_monitor._cts_repository._dispatch_statuses:
            splitted_dispatches[ds] = []
        splitted_dispatches[str(cts_dispatch_monitor._cts_repository.DISPATCH_REQUESTED)] = [cts_dispatch]
        splitted_dispatches[str(cts_dispatch_monitor._cts_repository.DISPATCH_CONFIRMED)] = [cts_dispatch_confirmed]

        confirmed_dispatches = [cts_dispatch_confirmed]
        cts_dispatch_monitor._cts_repository.get_all_dispatches = CoroutineMock(return_value=dispatches_response)
        cts_dispatch_monitor._cts_repository.get_dispatches_splitted_by_status = Mock(return_value=splitted_dispatches)
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
        cts_dispatch_monitor._cts_repository.get_dispatches_splitted_by_status = CoroutineMock()
        with pytest.raises(Exception):
            await cts_dispatch_monitor._cts_dispatch_monitoring_process()
            cts_dispatch_monitor._logger.error.assert_called_once()
            cts_dispatch_monitor._cts_repository.get_dispatches_splitted_by_status.assert_not_awaited()
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
    async def filter_dispatches_by_watermark_test(self, cts_dispatch_monitor, cts_dispatch_confirmed,
                                                  cts_dispatch_confirmed_2, cts_dispatch_confirmed_no_main_watermark,
                                                  cts_ticket_details_1,
                                                  cts_ticket_details_2_error,
                                                  cts_ticket_details_2_no_requested_watermark,
                                                  cts_ticket_details_no_watermark,
                                                  cts_dispatch_confirmed_skipped):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2,
            cts_dispatch_confirmed_2,
            cts_dispatch_confirmed_no_main_watermark,
            cts_dispatch_confirmed_skipped
        ]
        responses_details_mock = [
            cts_ticket_details_1,
            cts_ticket_details_2_error,
            cts_ticket_details_2_no_requested_watermark,
            cts_ticket_details_no_watermark
        ]
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        filtered_confirmed_dispatches = await cts_dispatch_monitor._filter_dispatches_by_watermark(confirmed_dispatches)

        assert filtered_confirmed_dispatches == [cts_dispatch_confirmed]

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_test(self, cts_dispatch_monitor, cts_dispatch_confirmed,
                                                cts_dispatch_confirmed_2, cts_dispatch_confirmed_no_main_watermark,
                                                cts_ticket_details_1,
                                                append_note_response, append_note_response_2,
                                                sms_success_response, sms_success_response_2):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
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
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        sms_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_note_2 = f'#*Automation Engine*# \n' \
                     f'Dispatch confirmation SMS sent to +12027723611\n'
        sms_tech_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'
        sms_tech_note_2 = f'#*Automation Engine*# \n' \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        dispatch_number_3 = cts_dispatch_confirmed_no_main_watermark.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        ticket_id_3 = cts_dispatch_confirmed_no_main_watermark.get('Ext_Ref_Num__c')

        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')
        time_3 = cts_dispatch_confirmed_no_main_watermark.get('Local_Site_Time__c')

        confirmed_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'
        confirmed_note_2 = f'#*Automation Engine*# \n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_2}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'
        sms_to_3 = '+12027723611'

        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'
        sms_to_3_tech = '+12123595129'

        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        sms_data = ''

        responses_details_mock = [
            cts_ticket_details_1,
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

        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} Confirmed Note appended"
        slack_msg_2 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} Confirmed Note appended"
        slack_msg_note_1 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                           f"Confirmed Note, SMS send and Confirmed SMS note sent OK."
        slack_msg_tech_note_1 = f"[service-dispatch-monitor] [CTS] " \
                                f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                                f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK."
        slack_msg_note_2 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} " \
                           f"Confirmed Note, SMS send and Confirmed SMS note sent OK."
        slack_msg_tech_note_2 = f"[service-dispatch-monitor] [CTS] " \
                                f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} " \
                                f"Confirmed SMS tech note not appended"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to),
        ])
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech),
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_note_1),
            call(slack_msg_tech_note_1),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_tech_sms_not_sent_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_ticket_details_1, cts_ticket_details_2, append_note_response, append_note_response_2,
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
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        sms_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_note_2 = f'#*Automation Engine*# {igz_dispatch_number_2}\n' \
                     f'Dispatch confirmation SMS sent to +12027723611\n'
        sms_tech_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'
        sms_tech_note_2 = f'#*Automation Engine*# {igz_dispatch_number_2}\n' \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')

        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        confirmed_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'
        confirmed_note_2 = f'#*Automation Engine*# {igz_dispatch_number_2}\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_2}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'

        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        sms_data = ''

        responses_details_mock = [
            cts_ticket_details_1,
            cts_ticket_details_2
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
        err_msg = f"Dispatch: {dispatch_number_2} Ticket_id: {ticket_id_2} Note: `{sms_tech_note_2}` " \
                  f"- Tech SMS Confirmed note not appended"
        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} Confirmed Note appended"
        slack_msg_2 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} Confirmed Note appended"
        slack_msg_note_1 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                           f"Confirmed Note, SMS send and Confirmed SMS note sent OK."
        slack_msg_tech_note_1 = f"[service-dispatch-monitor] [CTS] " \
                                f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                                f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK."
        slack_msg_note_2 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} " \
                           f"Confirmed Note, SMS send and Confirmed SMS note sent OK."
        slack_msg_tech_note_2 = f"[service-dispatch-monitor] [CTS] " \
                                f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} " \
                                f"Confirmed SMS tech note not appended"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1),
            call(ticket_id_2, confirmed_note_2),
            call(ticket_id_2, sms_note_2),
            # call(ticket_id_2, sms_tech_note_2)
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to),
            call(dispatch_number_2, ticket_id_2, datetime_2_str, sms_to_2)
        ])
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech),
            # call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, sms_to_2_tech)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_note_1),
            call(slack_msg_tech_note_1),
            call(slack_msg_2),
            call(slack_msg_note_2),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_tech_sms_tech_note_not_appended_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_ticket_details_1, cts_ticket_details_2, append_note_response, append_note_response_2,
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
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        sms_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_note_2 = f'#*Automation Engine*# {igz_dispatch_number_2}\n' \
                     f'Dispatch confirmation SMS sent to +12027723611\n'
        sms_tech_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'
        sms_tech_note_2 = f'#*Automation Engine*# {igz_dispatch_number_2}\n' \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')

        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        confirmed_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'
        confirmed_note_2 = f'#*Automation Engine*# {igz_dispatch_number_2}\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_2}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'

        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        sms_data = ''

        responses_details_mock = [
            cts_ticket_details_1,
            cts_ticket_details_2
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
        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} Confirmed Note appended"
        slack_msg_2 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} Confirmed Note appended"
        slack_msg_note_1 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                           f"Confirmed Note, SMS send and Confirmed SMS note sent OK."
        slack_msg_tech_note_1 = f"[service-dispatch-monitor] [CTS] " \
                                f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                                f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK."
        slack_msg_note_2 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} " \
                           f"Confirmed Note, SMS send and Confirmed SMS note sent OK."
        slack_msg_tech_note_2 = f"[service-dispatch-monitor] [CTS] " \
                                f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} " \
                                f"Confirmed SMS tech note not appended"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1),
            call(ticket_id_2, confirmed_note_2),
            call(ticket_id_2, sms_note_2),
            # call(ticket_id_2, sms_tech_note_2)
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to),
            call(dispatch_number_2, ticket_id_2, datetime_2_str, sms_to_2)
        ])
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, datetime_2_str, sms_to_2_tech)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_note_1),
            call(slack_msg_tech_note_1),
            call(slack_msg_2),
            call(slack_msg_note_2),
            call(slack_msg_tech_note_2),
        ])

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
        # cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

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
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_skipped,
            cts_ticket_details_1, append_note_response):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_skipped
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        sms_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        confirmed_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'

        responses_details_mock = [
            cts_ticket_details_1
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
        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} Confirmed Note appended"
        slack_msg_note_1 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                           f"Confirmed Note, SMS send and Confirmed SMS note sent OK."
        slack_msg_tech_note_1 = f"[service-dispatch-monitor] [CTS] " \
                                f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                                f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK."
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to)
        ])
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_note_1),
            call(slack_msg_tech_note_1),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skipping_one_invalid_datetime_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_skipped_datetime,
            cts_ticket_details_1, append_note_response):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_skipped_datetime
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        sms_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_skipped_datetime.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_skipped_datetime.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_skipped_datetime.get('Local_Site_Time__c')

        confirmed_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'

        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        responses_details_mock = [
            cts_ticket_details_1
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
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1),
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to)
        ])
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech)
        ])

        # cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skipping_one_invalid_sms_to_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_skipped_bad_phone,
            cts_ticket_details_1, append_note_response):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_skipped_bad_phone
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'

        sms_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_skipped_bad_phone.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_skipped_bad_phone.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_skipped_bad_phone.get('Local_Site_Time__c')

        confirmed_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'

        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        responses_details_mock = [
            cts_ticket_details_1
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
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(sideffect=[])

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to)
        ])
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech)
        ])

        # cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_skipping_one_invalid_sms_to_tech_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_skipped_bad_phone_tech,
            cts_ticket_details_1, append_note_response):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_skipped_bad_phone_tech
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'

        sms_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_skipped_bad_phone_tech.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_skipped_bad_phone_tech.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_skipped_bad_phone_tech.get('Local_Site_Time__c')
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        confirmed_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'

        responses_details_mock = [
            cts_ticket_details_1
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
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(sideffect=[])

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to)
        ])
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech)
        ])

        # cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_error_getting_ticket_details_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2, cts_ticket_details_1,
            cts_ticket_details_2_error, append_note_response):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        sms_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')

        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        confirmed_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'

        responses_details_mock = [
            cts_ticket_details_1,
            cts_ticket_details_2_error
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

        responses_send_slack_message_mock = [
            {'status': 200},
            response_slack_2
        ]
        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} Confirmed Note appended"
        slack_msg_2 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} Confirmed Note appended"
        slack_msg_note_1 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                           f"Confirmed Note, SMS send and Confirmed SMS note sent OK."
        slack_msg_tech_note_1 = f"[service-dispatch-monitor] [CTS] " \
                                f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                                f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK."
        slack_msg_note_2 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} " \
                           f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK."
        err_msg = f"An error occurred retrieve getting ticket details from bruin " \
                  f"Dispatch: {dispatch_number_2} - Ticket_id: {ticket_id_2}"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        # cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
        #     side_effect=responses_send_to_slack_mock)
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to)
        ])
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech)
        ])

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_note_1),
            call(slack_msg_tech_note_1),
            call(err_msg),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_sms_sent_but_not_added_confirmed_sms_note_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2, cts_ticket_details_1,
            cts_ticket_details_2, append_note_response):
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
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        sms_to = '+12027723610'

        responses_details_mock = [
            cts_ticket_details_1,
            cts_ticket_details_2
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
        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} Confirmed Note appended"
        slack_msg_2 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} Confirmed Note not appended"
        slack_msg_note_1 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                           f"Confirmed Note, SMS send and Confirmed SMS note sent OK."
        slack_msg_tech_note_1 = f"[service-dispatch-monitor] [CTS] " \
                                f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                                f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK."
        slack_msg_note_2 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2}" \
                           f" Confirmed SMS Note not appended"
        slack_msg_tech_note_2 = f"[service-dispatch-monitor] [CTS] " \
                                f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} " \
                                f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK."
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_note_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_send_confirmed_sms_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_send_confirmed_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_note_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_sms_tech_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_tech_note_mock)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to)
        ])

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_note_1),
            call(slack_msg_tech_note_1),
            call(slack_msg_2),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_confirmed_sms_not_sent_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2, cts_ticket_details_1,
            cts_ticket_details_2, append_note_response):
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
        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        sms_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                     'Dispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'
        sms_note_2 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                     f'Dispatch confirmation SMS sent to +12027723611\n'
        sms_tech_note_2 = f'#*Automation Engine*# {igz_dispatch_number_2}\n' \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')

        confirmed_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'
        confirmed_note_2 = f'#*Automation Engine*# {igz_dispatch_number_2}\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_2}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'
        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        responses_details_mock = [
            cts_ticket_details_1,
            cts_ticket_details_2
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

        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} Confirmed Note appended"
        slack_msg_2 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} Confirmed Note appended"
        slack_msg_note_1 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                           f"Confirmed Note, SMS send and Confirmed SMS note sent OK."
        slack_msg_tech_note_1 = f"[service-dispatch-monitor] [CTS] " \
                                f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                                f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK."
        slack_msg_note_2 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} " \
                           f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK."
        err_msg = f"[service-dispatch-monitor] [CTS] " \
                  f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} " \
                  f"SMS could not be sent to {sms_to_2}."
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_send_confirmed_sms_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_send_confirmed_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_note_mock)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_tech_note_1),
            call(ticket_id_2, confirmed_note_2),
            call(ticket_id_2, sms_tech_note_2),
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to),
            call(dispatch_number_2, ticket_id_2, datetime_2_str, sms_to_2)
        ])
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, datetime_2_str, sms_to_2_tech)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_note_1),
            call(slack_msg_tech_note_1),
            call(slack_msg_2),
            call(err_msg),
            call(slack_msg_note_2),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_confirmed_sms_sent_but_not_sms_note_appended_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2, cts_ticket_details_1,
            cts_ticket_details_2, append_note_response):
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
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
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
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        confirmed_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_1}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'
        confirmed_note_2 = f'#*Automation Engine*# {igz_dispatch_number_2}\n' \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {time_2}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = f'#*Automation Engine*# {igz_dispatch_number_1}\n' \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'
        sms_note_2 = f'#*Automation Engine*# {igz_dispatch_number_2}\n' \
                     f'Dispatch confirmation SMS sent to +12027723611\n'
        sms_tech_note_2 = f'#*Automation Engine*# {igz_dispatch_number_2}\n' \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        responses_details_mock = [
            cts_ticket_details_1,
            cts_ticket_details_2
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

        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} Confirmed Note appended"
        slack_msg_2 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} Confirmed Note appended"
        slack_msg_note_1 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                           f"Confirmed Note, SMS send and Confirmed SMS note sent OK."
        slack_msg_tech_note_1 = f"[service-dispatch-monitor] [CTS] " \
                                f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                                f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK."
        slack_msg_note_2 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2}" \
                           f" Confirmed SMS Note not appended"
        slack_msg_tech_note_2 = f"[service-dispatch-monitor] [CTS] " \
                                f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} " \
                                f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK."
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_send_confirmed_sms_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_send_confirmed_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_note_mock)

        await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_tech_note_1),
            call(ticket_id_2, confirmed_note_2),
            call(ticket_id_2, sms_tech_note_2),
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to),
            call(dispatch_number_2, ticket_id_2, datetime_2_str, sms_to_2)
        ])
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, datetime_2_str, sms_to_2_tech)
        ])

        cts_dispatch_monitor._cts_repository.append_confirmed_sms_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to),
            call(dispatch_number_2, igz_dispatch_number_2, ticket_id_2, sms_to_2),
        ])

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_note_1),
            call(slack_msg_tech_note_1),
            call(slack_msg_2),
            call(slack_msg_note_2),
            call(slack_msg_tech_note_2),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_sms_and_12h_sms_notes_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_ticket_details_1_with_confirmation_note, cts_ticket_details_2_with_confirmation_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
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
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        responses_details_mock = [
            cts_ticket_details_1_with_confirmation_note,
            cts_ticket_details_2_with_confirmation_note
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
        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        msg_1 = f'[service-dispatch-monitor] [CTS] ' \
                f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                f'- A sms tech 12 hours before note appended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_12_sms.assert_awaited_once_with(
            dispatch_number_1, ticket_id_1, datetime_1_str, sms_to)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note.assert_awaited_once_with(
            dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech.assert_awaited_once_with(
            dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note.assert_awaited_once_with(
            dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to_tech)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(msg_1),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_sms_and_12h_sms_notes_not_appended_tech_sms_note_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_ticket_details_1_with_confirmation_note, cts_ticket_details_2_with_confirmation_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
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
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        responses_details_mock = [
            cts_ticket_details_1_with_confirmation_note,
            cts_ticket_details_2_with_confirmation_note
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
            False
        ]
        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        msg_1 = f'[service-dispatch-monitor] [CTS] ' \
                f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                f'- A sms tech 12 hours before note appended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_12_sms.assert_awaited_once_with(
            dispatch_number_1, ticket_id_1, datetime_1_str, sms_to)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note.assert_awaited_once_with(
            dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech.assert_awaited_once_with(
            dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note.assert_awaited_once_with(
            dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to_tech)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(msg_1),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_and_confirmed_sms_notes_but_not_12h_sms_sended_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_ticket_details_1_with_confirmation_note, cts_ticket_details_2_with_confirmation_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
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
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        responses_details_mock = [
            cts_ticket_details_1_with_confirmation_note,
            cts_ticket_details_2_with_confirmation_note
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
        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        msg_1 = f'[service-dispatch-monitor] [CTS] ' \
                f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                f'- A sms tech 12 hours before note not appended'
        msg_note_1 = f'[service-dispatch-monitor] [CTS] ' \
                     f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                     f'- A sms tech 12 hours before tech note appended'
        msg_2 = f'[service-dispatch-monitor] [CTS] ' \
                f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} ' \
                f'- SMS 12h not sended'
        msg_note_2 = f'[service-dispatch-monitor] [CTS] ' \
                     f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} ' \
                     f'- SMS tech 12h not sended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_12_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to),
            call(dispatch_number_2, ticket_id_2, datetime_2_str, sms_to_2)
        ])
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note.assert_awaited_once_with(
            dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to)

        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, datetime_2_str, sms_to_2_tech)
        ])
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note.assert_awaited_once_with(
            dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to_tech)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(msg_1),
            call(msg_note_1),
            call(msg_2),
            call(msg_note_2),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_sms_and_12h_sms_and_2h_sms_notes_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_ticket_details_1_with_12h_sms_note, cts_ticket_details_2_with_12h_sms_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
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
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        responses_details_mock = [
            cts_ticket_details_1_with_12h_sms_note,
            cts_ticket_details_2_with_12h_sms_note
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
        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                      f'- A sms tech 2 hours before note appended'
        slack_msg_2 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} ' \
                      f'- A sms tech 2 hours before note appended'
        slack_msg_sms_1 = f'[service-dispatch-monitor] [CTS] ' \
                          f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                          f'- A sms tech 2 hours before tech note appended'
        slack_msg_sms_2 = f'[service-dispatch-monitor] [CTS] ' \
                          f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} ' \
                          f'- A sms tech 2 hours before tech note appended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_2_sms = CoroutineMock(
            side_effect=responses_send_tech_2_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_2_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_tech_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_12_sms.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to)
        ])

        cts_dispatch_monitor._cts_repository.append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to)
        ])

        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech)
        ])

        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to_tech)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_sms_1),
            call(slack_msg_2),
            call(slack_msg_sms_2),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_sms_and_2h_sms_notes_but_not_12h_sms_sended_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_ticket_details_1_with_12h_sms_note, cts_ticket_details_2_with_12h_sms_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
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
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        responses_details_mock = [
            cts_ticket_details_1_with_12h_sms_note,
            cts_ticket_details_2_with_12h_sms_note
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
        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                      f'- A sms tech 2 hours before note appended'
        slack_msg_2 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} ' \
                      f'- A sms tech 2 hours before note not appended'
        slack_msg_sms_1 = f'[service-dispatch-monitor] [CTS] ' \
                          f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                          f'- A sms tech 2 hours before tech note appended'
        slack_msg_sms_2 = f'[service-dispatch-monitor] [CTS] ' \
                          f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} ' \
                          f'- A sms tech 2 hours before tech note appended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech = CoroutineMock()
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note = CoroutineMock()
        cts_dispatch_monitor._cts_repository.send_tech_2_sms = CoroutineMock(
            side_effect=responses_send_tech_2_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_2_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_tech_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_12_sms.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to),
            call(dispatch_number_2, ticket_id_2, datetime_2_str, sms_to_2)
        ])

        cts_dispatch_monitor._cts_repository.append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to)
        ])

        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, datetime_2_str, sms_to_2_tech)
        ])

        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to_tech),
            call(dispatch_number_2, igz_dispatch_number_2, ticket_id_2, sms_to_2_tech)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_sms_1),
            call(slack_msg_2),
            call(slack_msg_sms_2),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_sms_and_2h_sms_notes_but_sms_2h_sms_not_sent_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_ticket_details_1_with_12h_sms_note, cts_ticket_details_2_with_12h_sms_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
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
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        responses_details_mock = [
            cts_ticket_details_1_with_12h_sms_note,
            cts_ticket_details_2_with_12h_sms_note
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
        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                      f'- A sms tech 2 hours before note not appended'
        slack_msg_sms_1 = f'[service-dispatch-monitor] [CTS] ' \
                          f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                          f'- A sms tech 2 hours before tech note appended'
        slack_msg_2 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} ' \
                      f'- SMS 2h not sent'
        slack_msg_sms_2 = f'[service-dispatch-monitor] [CTS] ' \
                          f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} ' \
                          f'- A sms tech 2 hours before tech note appended'

        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_2_sms = CoroutineMock(
            side_effect=responses_send_tech_2_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_2_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_tech_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_12_sms.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to),
            call(dispatch_number_2, ticket_id_2, datetime_2_str, sms_to_2)
        ])

        cts_dispatch_monitor._cts_repository.append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to)
        ])

        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, datetime_2_str, sms_to_2_tech)
        ])

        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to_tech),
            call(dispatch_number_2, igz_dispatch_number_2, ticket_id_2, sms_to_2_tech)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_sms_1),
            call(slack_msg_2),
            call(slack_msg_sms_2),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_and_confirmed_sms_and_2h_sms_notes_sentok_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_ticket_details_1_with_12h_sms_note, cts_ticket_details_2_with_12h_sms_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
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
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        responses_details_mock = [
            cts_ticket_details_1_with_12h_sms_note,
            cts_ticket_details_2_with_12h_sms_note
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
        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                      f'- A sms tech 2 hours before note appended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_2_sms = CoroutineMock(
            side_effect=responses_send_tech_2_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_2_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_tech_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_12_sms.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to),
            call(dispatch_number_2, ticket_id_2, datetime_2_str, sms_to_2)
        ])

        cts_dispatch_monitor._cts_repository.append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to),
            call(dispatch_number_2, igz_dispatch_number_2, ticket_id_2, sms_to_2)
        ])

        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, datetime_2_str, sms_to_2_tech)
        ])

        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to_tech),
            call(dispatch_number_2, igz_dispatch_number_2, ticket_id_2, sms_to_2_tech)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_confirmed_and_confirmed_sms_and_2h_sms_not_needed_to_send_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_ticket_details_1_with_12h_sms_note, cts_ticket_details_2_with_12h_sms_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
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
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        responses_details_mock = [
            cts_ticket_details_1_with_12h_sms_note,
            cts_ticket_details_2_with_12h_sms_note
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
        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                      f'- A sms tech 2 hours before note appended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_tech_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_2_sms = CoroutineMock(
            side_effect=responses_send_tech_2_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_2_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_tech_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_12_sms.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_2_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to),
        ])

        cts_dispatch_monitor._cts_repository.append_tech_2_sms_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to),
        ])

        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech),
        ])

        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to_tech),
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_2h_sms_and_note_sent_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_ticket_details_1_with_2h_sms_note, cts_ticket_details_2_with_2h_sms_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
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
        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        responses_details_mock = [
            cts_ticket_details_1_with_2h_sms_note,
            cts_ticket_details_2_with_2h_sms_note
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

        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                      f'- A sms tech 2 hours before tech note appended'
        slack_msg_2 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} ' \
                      f'- A sms tech 2 hours before tech note appended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_2_sms = CoroutineMock()
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_note = CoroutineMock()
        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech = CoroutineMock()
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note = CoroutineMock()

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_12_sms.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_2_sms.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_note.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, datetime_2_str, sms_to_2_tech)
        ])

        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to_tech),
            call(dispatch_number_2, igz_dispatch_number_2, ticket_id_2, sms_to_2_tech)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_2),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_2h_sms_and_note_not_sent_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_ticket_details_1_with_2h_sms_note, cts_ticket_details_2_with_2h_sms_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
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

        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        datetime_2_localized = iso8601.parse_date(time_2, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        datetime_2_str = datetime_2_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        responses_details_mock = [
            cts_ticket_details_1_with_2h_sms_note,
            cts_ticket_details_2_with_2h_sms_note
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
            False
        ]

        responses_send_tech_12_sms_note_mock = [
            True,
            False
        ]

        responses_send_tech_2_sms_mock = [
            True,
            False
        ]

        responses_send_tech_2_sms_note_mock = [
            False,
            False
        ]

        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                      f'- A sms tech 2 hours before tech note not appended'
        slack_msg_2 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} ' \
                      f'- SMS tech 2h not sended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_2_sms = CoroutineMock()
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock
        )
        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_2_sms_mock
        )
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_note_mock
        )

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_12_sms.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_2_sms.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_note.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, datetime_2_str, sms_to_2_tech)
        ])

        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to_tech),
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_2),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_2h_tech_sms_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed,
            cts_ticket_details_1_with_2h_sms_tech_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'
        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        datetime_1_localized = iso8601.parse_date(time_1, pytz.utc)
        # Get datetime formatted string
        datetime_1_str = datetime_1_localized.strftime(UtilsRepository.DATETIME_FORMAT)

        responses_details_mock = [
            cts_ticket_details_1_with_2h_sms_tech_note,
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
            False
        ]

        responses_send_tech_12_sms_note_mock = [
            True,
            False
        ]

        responses_send_tech_2_sms_mock = [
            True,
            False
        ]

        responses_send_tech_2_sms_note_mock = [
            False,
            False
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._cts_repository.send_tech_2_sms = CoroutineMock()
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock
        )
        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_2_sms_mock
        )
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_2_sms_note_mock
        )
        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech = CoroutineMock()
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note = CoroutineMock()
        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            await cts_dispatch_monitor._monitor_confirmed_dispatches(confirmed_dispatches=confirmed_dispatches)

        cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_test(self, cts_dispatch_monitor, cts_dispatch_tech_on_site,
                                                   cts_dispatch_tech_on_site_2, cts_dispatch_not_valid_ticket_id,
                                                   cts_dispatch_tech_on_site_bad_datetime,
                                                   cts_ticket_details_1, cts_ticket_details_2,
                                                   append_note_response, append_note_response_2):
        tech_on_site_dispatches = [
            cts_dispatch_tech_on_site,
            cts_dispatch_tech_on_site_2,
            cts_dispatch_tech_on_site_bad_datetime,
            cts_dispatch_not_valid_ticket_id
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        dispatch_number_1 = cts_dispatch_tech_on_site.get('Name')
        dispatch_number_2 = cts_dispatch_tech_on_site_2.get('Name')
        dispatch_number_3 = cts_dispatch_tech_on_site_bad_datetime.get('Name')
        ticket_id_1 = cts_dispatch_tech_on_site.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_tech_on_site_2.get('Ext_Ref_Num__c')
        ticket_id_3 = cts_dispatch_tech_on_site_bad_datetime.get('Ext_Ref_Num__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'

        responses_details_mock = [
            cts_ticket_details_1,
            cts_ticket_details_2
        ]

        responses_sms_tech_on_site_mock = [
            True,
            True
        ]

        responses_append_tech_on_site_sms_note_mock = [
            True,
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository.send_tech_on_site_sms = CoroutineMock(
            side_effect=responses_sms_tech_on_site_mock)
        cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_tech_on_site, sms_to),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_tech_on_site_2, sms_to_2)
        ])

        cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to,
                 cts_dispatch_tech_on_site.get('API_Resource_Name__c')),
            call(dispatch_number_2, igz_dispatch_number_2, ticket_id_2, sms_to_2,
                 cts_dispatch_tech_on_site_2.get('API_Resource_Name__c'))
        ])

        # cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

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
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock()

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_not_awaited()
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

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

        # cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_error_getting_ticket_details_test(
            self, cts_dispatch_monitor, cts_dispatch_tech_on_site, cts_dispatch_tech_on_site_2,
            cts_ticket_details_1, cts_ticket_details_2_error):
        tech_on_site_dispatches = [
            cts_dispatch_tech_on_site,
            cts_dispatch_tech_on_site_2
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        dispatch_number_1 = cts_dispatch_tech_on_site.get('Name')
        dispatch_number_2 = cts_dispatch_tech_on_site_2.get('Name')
        ticket_id_1 = cts_dispatch_tech_on_site.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_tech_on_site_2.get('Ext_Ref_Num__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'

        responses_details_mock = [
            cts_ticket_details_1,
            cts_ticket_details_2_error
        ]

        responses_sms_tech_on_site_mock = [
            True
        ]

        responses_append_tech_on_site_sms_note_mock = [
            True
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)

        cts_dispatch_monitor._cts_repository.send_tech_on_site_sms = CoroutineMock(
            side_effect=responses_sms_tech_on_site_mock)
        cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        err_msg = f"An error occurred retrieve getting ticket details from bruin " \
                  f"Dispatch: {dispatch_number_2} - Ticket_id: {ticket_id_2}"

        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(return_value=err_msg)

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_tech_on_site, sms_to)
        ])

        cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to,
                 cts_dispatch_tech_on_site.get('API_Resource_Name__c'))
        ])

        # cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_sms_not_sent_test(
            self, cts_dispatch_monitor, cts_dispatch_tech_on_site, cts_dispatch_tech_on_site_2,
            cts_ticket_details_1, cts_ticket_details_2):
        tech_on_site_dispatches = [
            cts_dispatch_tech_on_site,
            cts_dispatch_tech_on_site_2
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        dispatch_number_1 = cts_dispatch_tech_on_site.get('Name')
        dispatch_number_2 = cts_dispatch_tech_on_site_2.get('Name')
        ticket_id_1 = cts_dispatch_tech_on_site.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_tech_on_site_2.get('Ext_Ref_Num__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'

        responses_details_mock = [
            cts_ticket_details_1,
            cts_ticket_details_2
        ]

        responses_sms_tech_on_site_mock = [
            True,
            False
        ]

        responses_append_tech_on_site_sms_note_mock = [
            True
        ]
        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                      f"- A sms tech on site note appended"
        slack_msg_2 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} ' \
                      f"- SMS tech on site not sended"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)

        cts_dispatch_monitor._cts_repository.send_tech_on_site_sms = CoroutineMock(
            side_effect=responses_sms_tech_on_site_mock)
        cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_tech_on_site, sms_to),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_tech_on_site_2, sms_to_2)
        ])

        cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to,
                 cts_dispatch_tech_on_site.get('API_Resource_Name__c'))
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_2),
        ])

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_sms_note_not_appended_test(
            self, cts_dispatch_monitor, cts_dispatch_tech_on_site, cts_dispatch_tech_on_site_2,
            cts_ticket_details_1, cts_ticket_details_2):
        tech_on_site_dispatches = [
            cts_dispatch_tech_on_site,
            cts_dispatch_tech_on_site_2
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        dispatch_number_1 = cts_dispatch_tech_on_site.get('Name')
        dispatch_number_2 = cts_dispatch_tech_on_site_2.get('Name')
        ticket_id_1 = cts_dispatch_tech_on_site.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_tech_on_site_2.get('Ext_Ref_Num__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'

        responses_details_mock = [
            cts_ticket_details_1,
            cts_ticket_details_2
        ]

        responses_sms_tech_on_site_mock = [
            True,
            True
        ]

        responses_append_tech_on_site_sms_note_mock = [
            True,
            False
        ]
        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} ' \
                      f"- A sms tech on site note appended"
        slack_msg_2 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} ' \
                      f"- A sms tech on site note not appended"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)

        cts_dispatch_monitor._cts_repository.send_tech_on_site_sms = CoroutineMock(
            side_effect=responses_sms_tech_on_site_mock)
        cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.send_tech_on_site_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, cts_dispatch_tech_on_site, sms_to),
            call(dispatch_number_2, ticket_id_2, cts_dispatch_tech_on_site_2, sms_to_2)
        ])

        cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, sms_to,
                 cts_dispatch_tech_on_site.get('API_Resource_Name__c')),
            call(dispatch_number_2, igz_dispatch_number_2, ticket_id_2, sms_to_2,
                 cts_dispatch_tech_on_site_2.get('API_Resource_Name__c'))
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_2),
        ])

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_with_tech_on_site_note_already_sent_ok_test(
            self, cts_dispatch_monitor, cts_dispatch_tech_on_site, cts_dispatch_tech_on_site_2,
            cts_ticket_details_1_with_tech_on_site_sms_note, cts_ticket_details_2_with_tech_on_site_sms_note):
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
            cts_ticket_details_1_with_tech_on_site_sms_note,
            cts_ticket_details_2_with_tech_on_site_sms_note
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

        cts_dispatch_monitor._cts_repository.send_tech_on_site_sms = CoroutineMock()
        cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note = CoroutineMock()

        await cts_dispatch_monitor._monitor_tech_on_site_dispatches(tech_on_site_dispatches=tech_on_site_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.send_tech_on_site_sms.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def monitor_cancelled_dispatches_test(self, cts_dispatch_monitor, cts_dispatch_cancelled,
                                                cts_dispatch_cancelled_not_valid_ticket_id,
                                                cts_dispatch_cts_dispatch_cancelled_bad_datetime,
                                                cts_ticket_details_1, append_note_response):
        cancelled_dispatches = [
            cts_dispatch_cancelled_not_valid_ticket_id,
            cts_dispatch_cancelled,
            cts_dispatch_cts_dispatch_cancelled_bad_datetime
        ]

        responses_details_mock = [
            cts_ticket_details_1
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        igz_dispatch_number_1 = 'IGZ_0001'
        dispatch_number_1 = cts_dispatch_cancelled.get('Name')
        ticket_id_1 = cts_dispatch_cancelled.get('Ext_Ref_Num__c')

        responses_append_dispatch_cancelled_note_mock = [
            True
        ]
        slack_msg = f"[service-dispatch-monitor] [CTS] " \
                    f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                    f"- A cancelled dispatch note appended"
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note = CoroutineMock(
            side_effect=responses_append_dispatch_cancelled_note_mock)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._monitor_cancelled_dispatches(cancelled_dispatches=cancelled_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, cts_dispatch_cancelled)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(slack_msg)

    @pytest.mark.asyncio
    async def monitor_cancelled_dispatches_with_general_exception_test(
            self, cts_dispatch_monitor):
        cancelled_dispatches = 0  # Non valid list for filter
        err_msg = f"Error: _monitor_cancelled_dispatches - object of type 'int' has no len()"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._monitor_cancelled_dispatches(cancelled_dispatches)

        cts_dispatch_monitor._logger.error.assert_called_once()
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_cancelled_dispatches_with_exception_test(
            self, cts_dispatch_monitor, cts_dispatch_cancelled):
        cancelled_dispatches = [
            cts_dispatch_cancelled,
        ]
        err_msg = f"Error: Dispatch [{cts_dispatch_cancelled.get('Name')}] " \
                  f"in ticket_id: {cts_dispatch_cancelled.get('Ext_Ref_Num__c')} " \
                  f"- {cts_dispatch_cancelled}"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._monitor_cancelled_dispatches(cancelled_dispatches)

        cts_dispatch_monitor._logger.error.assert_called_once()
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_cancelled_dispatches_error_getting_details_test(self, cts_dispatch_monitor,
                                                                      cts_dispatch_cancelled,
                                                                      cts_dispatch_cancelled_2,
                                                                      cts_ticket_details_1, cts_ticket_details_2_error,
                                                                      append_note_response):
        cancelled_dispatches = [
            cts_dispatch_cancelled,
            cts_dispatch_cancelled_2,
        ]

        responses_details_mock = [
            cts_ticket_details_1,
            cts_ticket_details_2_error
        ]

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }

        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'

        dispatch_number_1 = cts_dispatch_cancelled.get('Name')
        dispatch_number_2 = cts_dispatch_cancelled_2.get('Name')

        ticket_id_1 = cts_dispatch_cancelled.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_cancelled_2.get('Ext_Ref_Num__c')

        responses_append_dispatch_cancelled_note_mock = [
            True
        ]
        slack_msg = f"[service-dispatch-monitor] [CTS] " \
                    f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                    f"- A cancelled dispatch note appended"
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note = CoroutineMock(
            side_effect=responses_append_dispatch_cancelled_note_mock)
        err_msg = f"An error occurred retrieve getting ticket details from bruin " \
                  f"Dispatch: {dispatch_number_2} - Ticket_id: {ticket_id_2}"

        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._monitor_cancelled_dispatches(cancelled_dispatches=cancelled_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1),
            call(ticket_id_2)
        ])

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, cts_dispatch_cancelled)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([call(slack_msg),
                                                                                             call(err_msg)])

    @pytest.mark.asyncio
    async def monitor_already_cancelled_dispatches_test(self, cts_dispatch_monitor, cts_dispatch_cancelled,
                                                        cts_ticket_details_1_with_cancelled_note):
        cancelled_dispatches = [
            cts_dispatch_cancelled,
        ]

        responses_details_mock = [
            cts_ticket_details_1_with_cancelled_note
        ]

        dispatch_number_1 = cts_dispatch_cancelled.get('Name')
        ticket_id_1 = cts_dispatch_cancelled.get('Ext_Ref_Num__c')

        responses_append_dispatch_cancelled_note_mock = [
            True
        ]
        slack_msg = f"[service-dispatch-monitor] [CTS] " \
                    f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                    f"- A cancelled dispatch note appended"
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note = CoroutineMock(
            side_effect=responses_append_dispatch_cancelled_note_mock)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._monitor_cancelled_dispatches(cancelled_dispatches=cancelled_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note.assert_not_awaited()
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def monitor_cancelled_dispatches_not_appended_test(self, cts_dispatch_monitor, cts_dispatch_cancelled,
                                                             cts_ticket_details_1):
        cancelled_dispatches = [
            cts_dispatch_cancelled,
        ]

        responses_details_mock = [
            cts_ticket_details_1
        ]

        igz_dispatch_number_1 = 'IGZ_0001'
        dispatch_number_1 = cts_dispatch_cancelled.get('Name')
        ticket_id_1 = cts_dispatch_cancelled.get('Ext_Ref_Num__c')

        responses_append_dispatch_cancelled_note_mock = [
            False
        ]
        slack_msg = f"[service-dispatch-monitor] [CTS] " \
                    f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                    f"- A cancelled dispatch note not appended"
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note = CoroutineMock(
            side_effect=responses_append_dispatch_cancelled_note_mock)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._monitor_cancelled_dispatches(cancelled_dispatches=cancelled_dispatches)

        cts_dispatch_monitor._bruin_repository.get_ticket_details.assert_has_awaits([
            call(ticket_id_1)
        ])

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, cts_dispatch_cancelled)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(slack_msg)
