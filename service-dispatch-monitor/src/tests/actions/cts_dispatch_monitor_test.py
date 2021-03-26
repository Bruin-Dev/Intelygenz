import json
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

        cts_dispatch_monitor._scheduler.add_job.assert_has_calls([
            call(cts_dispatch_monitor._cts_dispatch_monitoring_process, 'interval',
                 minutes=config.DISPATCH_MONITOR_CONFIG["jobs_intervals"]["cts_dispatch_monitor"],
                 next_run_time=next_run_time,
                 replace_existing=False,
                 id='_service_dispatch_monitor_cts_process')
        ], any_order=False)

    @pytest.mark.asyncio
    async def start_dispatch_monitor_job_with_no_exec_on_start_test(self, cts_dispatch_monitor):
        config = testconfig

        await cts_dispatch_monitor.start_monitoring_job(exec_on_start=False)

        cts_dispatch_monitor._scheduler.add_job.assert_has_calls([
            call(cts_dispatch_monitor._cts_dispatch_monitoring_process, 'interval',
                 minutes=config.DISPATCH_MONITOR_CONFIG["jobs_intervals"]["cts_dispatch_monitor"],
                 next_run_time=undefined,
                 replace_existing=False,
                 id='_service_dispatch_monitor_cts_process')
        ], any_order=False)

    def get_process_dispatch_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_tech_on_site,
                                  cts_dispatch_cancelled):
        expected_processes = [
            (cts_dispatch_monitor._process_confirmed_dispatch, cts_dispatch_confirmed,),
            (cts_dispatch_monitor._process_tech_on_site_dispatch, cts_dispatch_tech_on_site,),
            (cts_dispatch_monitor._process_canceled_dispatch, cts_dispatch_cancelled,)
        ]
        for expected_process, dispatch in expected_processes:
            result = cts_dispatch_monitor._get_process_dispatch(dispatch)
            assert result == expected_process

    @pytest.mark.asyncio
    async def cts_dispatch_monitoring_process_test(self, cts_dispatch_monitor, cts_dispatch, cts_dispatch_confirmed):
        dispatches = [cts_dispatch, cts_dispatch_confirmed]
        dispatches_response = {
            'status': 200,
            'body': {
                'done': True,
                'records': dispatches
            }
        }

        cts_dispatch_monitor._cts_repository.get_all_dispatches = CoroutineMock(return_value=dispatches_response)
        cts_dispatch_monitor._distribute_and_process_dispatches = CoroutineMock()

        await cts_dispatch_monitor._cts_dispatch_monitoring_process()

        cts_dispatch_monitor._distribute_and_process_dispatches.assert_awaited_with(dispatches)

    def split_ticket_notes_by_igz_dispatch_num_test(self, cts_dispatch_monitor, cts_ticket_notes_with_2_dispatches,
                                                    cts_filtered_tickets_1, cts_filtered_tickets_2):
        igz_id_1 = 'IGZTqSAzuvj2wehMXzqYxixxd'
        igz_id_2 = 'IGZWtpGZCJopULhsiUhbWjUYf'
        expected = {
            igz_id_1: cts_filtered_tickets_1,
            igz_id_2: cts_filtered_tickets_2
        }
        ticket_notes = cts_ticket_notes_with_2_dispatches.get('ticketNotes')
        result = cts_dispatch_monitor._cts_repository.split_ticket_notes_by_igz_dispatch_num(ticket_notes)

        assert result == expected

    @pytest.mark.asyncio
    async def process_generic_dispatch_test(self, cts_dispatch_monitor,
                                            cts_dispatch_confirmed, cts_dispatch_confirmed_2,
                                            cts_dispatch_confirmed_no_main_watermark,
                                            cts_dispatch_confirmed_skipped,
                                            cts_dispatch_tech_on_site, cts_dispatch_cancelled,
                                            cts_ticket_details_1, cts_ticket_details_2,
                                            cts_ticket_details_2_error,
                                            cts_ticket_details_2_no_requested_watermark,
                                            cts_ticket_details_no_watermark):
        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        igz_dispatch_number_1 = 'IGZ_0001'
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        redis_data_1 = {
            "ticket_id": ticket_id_1,
            "igz_dispatch_number": igz_dispatch_number_1
        }
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        igz_dispatch_number_2 = 'IGZ_0002'
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        redis_data_2 = {
            "ticket_id": ticket_id_2,
            "igz_dispatch_number": igz_dispatch_number_2
        }
        dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2,
            cts_dispatch_confirmed_no_main_watermark,
            cts_dispatch_confirmed_skipped,
            # cts_dispatch_tech_on_site,
            # cts_dispatch_cancelled
        ]
        responses_details_mock = [
            cts_ticket_details_1,
            cts_ticket_details_2,
            cts_ticket_details_2_error,
            cts_ticket_details_2_no_requested_watermark,
            cts_ticket_details_no_watermark
        ]

        get_process_dispatch_mock = [
            cts_dispatch_monitor._process_confirmed_dispatch,
            cts_dispatch_monitor._process_confirmed_dispatch,
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()
        cts_dispatch_monitor._get_process_dispatch = Mock(side_effect=get_process_dispatch_mock)
        cts_dispatch_monitor._scheduler.add_job = Mock()
        cts_dispatch_monitor._redis_client.get = Mock(side_effect=[None, redis_data_2])
        cts_dispatch_monitor._redis_client.set = Mock()
        cts_dispatch_monitor._cts_repository.get_igz_dispatch_number = \
            Mock(side_effect=[igz_dispatch_number_1, igz_dispatch_number_2, None, None])

        ticket_notes_1 = [{'noteId': 70805300,
                           'noteValue': "#*MetTel's IPA*# IGZ_0001\nDispatch Management - Dispatch Requested\n\nPlease see the summary below.\n--\nDispatch Number:  [IGZ_0001|https://master.mettel-automation.net/dispatch_portal/dispatch/IGZ_0001] \nDate of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\nTime Zone (Local): Pacific Time\n\nLocation Owner/Name: Red Rose Inn\nAddress: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\nPhone: +1 666 6666 666\n\nIssues Experienced:\nDevice is bouncing constantly TEST LUNES\nArrival Instructions: When arriving to the site call HOLMDEL NOC for telematic assistance\nMaterials Needed:\nLaptop, cable, tuner, ladder,internet hotspot\n\nRequester\nName: Karen Doe\nPhone: +1 666 6666 666\nEmail: karen.doe@mettel.net\nDepartment: Customer Care",  # noqa
                           'serviceNumber': ['4664325'], 'createdDate': '2020-05-28T06:06:40.27-04:00',
                           'creator': None}]
        ticket_notes_2 = [{'noteId': 70805300,
                           'noteValue': "#*MetTel's IPA*# IGZ_0002\nDispatch Management - Dispatch Requested\n\nPlease see the summary below.\n--\nDispatch Number:  [IGZ_0002|https://master.mettel-automation.net/dispatch_portal/dispatch/IGZ_0002] \nDate of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\nTime Zone (Local): Pacific Time\n\nLocation Owner/Name: Red Rose Inn\nAddress: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\nPhone: +1 666 6666 666\n\nIssues Experienced:\nDevice is bouncing constantly TEST LUNES\nArrival Instructions: When arriving to the site call HOLMDEL NOC for telematic assistance\nMaterials Needed:\nLaptop, cable, tuner, ladder,internet hotspot\n\nRequester\nName: Karen Doe\nPhone: +1 666 6666 666\nEmail: karen.doe@mettel.net\nDepartment: Customer Care",  # noqa
                           'serviceNumber': ['4664325'], 'createdDate': '2020-05-28T06:06:40.27-04:00',
                           'creator': None}]  # noqa

        func_args_1 = [cts_dispatch_confirmed, igz_dispatch_number_1, ticket_notes_1]
        func_args_2 = [cts_dispatch_confirmed_2, igz_dispatch_number_2, ticket_notes_2]

        for _dispatch in dispatches:
            await cts_dispatch_monitor._process_generic_dispatch(_dispatch)

        cts_dispatch_monitor._get_process_dispatch.assert_has_calls([
            call(cts_dispatch_confirmed),
            call(cts_dispatch_confirmed_2),
        ])
        cts_dispatch_monitor._scheduler.add_job.assert_has_calls([
            call(get_process_dispatch_mock[0], 'date', next_run_time=undefined, replace_existing=False,
                 id=f"_process_dispatch_{dispatch_number_1}", args=func_args_1),
            call(get_process_dispatch_mock[0], 'date', next_run_time=undefined, replace_existing=False,
                 id=f"_process_dispatch_{dispatch_number_2}", args=func_args_2),
        ])

    @pytest.mark.asyncio
    async def process_generic_dispatch_with_general_exception_test(self, cts_dispatch_monitor, cts_dispatch_confirmed):
        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        igz_dispatch_number_1 = 'IGZ_0001'
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        redis_data_1 = {
            "ticket_id": ticket_id_1,
            "igz_dispatch_number": igz_dispatch_number_1
        }
        cts_dispatch_monitor._bruin_repository_get_ticket_details = CoroutineMock(side_effect=Exception)
        with pytest.raises(Exception):
            await cts_dispatch_monitor._process_generic_dispatch(cts_dispatch_confirmed)
            cts_dispatch_monitor._bruin_repository_get_ticket_details.assert_called_once_with(ticket_id_1)
            cts_dispatch_monitor._logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def process_generic_dispatch_with_not_valid_dispatches_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_dispatch_confirmed_no_main_watermark, cts_dispatch_confirmed_skipped,
            cts_dispatch_tech_on_site, cts_dispatch_cancelled, cts_ticket_details_1, cts_ticket_details_2,
            cts_ticket_details_2_error,
            cts_ticket_details_2_no_requested_watermark, cts_ticket_details_no_watermark_1):
        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        igz_dispatch_number_1 = 'IGZ_0001'
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        redis_data_1 = {
            "ticket_id": ticket_id_1,
            "igz_dispatch_number": igz_dispatch_number_1
        }
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        igz_dispatch_number_2 = 'IGZ_0002'
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        redis_data_2 = {
            "ticket_id": ticket_id_2,
            "igz_dispatch_number": igz_dispatch_number_2
        }
        dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_no_main_watermark,
            cts_dispatch_confirmed_skipped,
            cts_dispatch_confirmed_2,
            # cts_dispatch_tech_on_site,
            # cts_dispatch_cancelled
        ]
        responses_details_mock = [
            cts_ticket_details_1,
            cts_ticket_details_no_watermark_1,
            cts_ticket_details_2,
            cts_ticket_details_2_error,
        ]

        get_process_dispatch_mock = [
            cts_dispatch_monitor._process_confirmed_dispatch,
            None,
            None,
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()
        cts_dispatch_monitor._get_process_dispatch = Mock(side_effect=get_process_dispatch_mock)
        cts_dispatch_monitor._scheduler.add_job = Mock()
        cts_dispatch_monitor._redis_client.get = Mock(side_effect=[None, None, None])
        cts_dispatch_monitor._redis_client.set = Mock()
        cts_dispatch_monitor._cts_repository.get_igz_dispatch_number = \
            Mock(side_effect=[igz_dispatch_number_1, None, igz_dispatch_number_2])

        ticket_notes_1 = [{'noteId': 70805300,
                           'noteValue': "#*MetTel's IPA*# IGZ_0001\nDispatch Management - Dispatch Requested\n\n"
                                        'Please see the summary below.\n--\n'
                                        'Dispatch Number:  [IGZ_0001|'
                                        'https://master.mettel-automation.net/dispatch_portal/dispatch/IGZ_0001] \n'
                                        'Date of Dispatch: 2019-11-14\n'
                                        'Time of Dispatch (Local): 6PM-8PM\n'
                                        'Time Zone (Local): Pacific Time\n\nLocation Owner/Name: Red Rose Inn\n'
                                        'Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n'
                                        'Phone: +1 666 6666 666\n\n'
                                        'Issues Experienced:\nDevice is bouncing constantly TEST LUNES\n'
                                        'Arrival Instructions: When arriving to the site call'
                                        ' HOLMDEL NOC for telematic assistance\n'
                                        'Materials Needed:\nLaptop, cable, tuner, ladder,internet hotspot\n\n'
                                        'Requester\nName: Karen Doe\nPhone: +1 666 6666 666\n'
                                        'Email: karen.doe@mettel.net\nDepartment: Customer Care',
                           # noqa
                           'serviceNumber': ['4664325'], 'createdDate': '2020-05-28T06:06:40.27-04:00',
                           'creator': None}]
        ticket_notes_2 = [{'noteId': 70805300,
                           'noteValue':
                               "#*MetTel's IPA*# IGZ_0002\nDispatch Management - Dispatch Requested\n\n"
                               'Please see the summary below.\n--\nDispatch Number:  '
                               '[IGZ_0002|https://master.mettel-automation.net/dispatch_portal/dispatch/IGZ_0002] \n'
                               'Date of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n'
                               'Time Zone (Local): Pacific Time\n\nLocation Owner/Name: Red Rose Inn\n'
                               'Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n'
                               'Phone: +1 666 6666 666\n\n'
                               'Issues Experienced:\nDevice is bouncing constantly TEST LUNES\n'
                               'Arrival Instructions: When arriving to the '
                               'site call HOLMDEL NOC for telematic assistance\n'
                               'Materials Needed:\nLaptop, cable, tuner, ladder,internet hotspot\n\n'
                               'Requester\nName: Karen Doe\nPhone: +1 666 6666 666\nEmail: karen.doe@mettel.net\n'
                               'Department: Customer Care',
                           # noqa
                           'serviceNumber': ['4664325'], 'createdDate': '2020-05-28T06:06:40.27-04:00',
                           'creator': None}]

        func_args_1 = [cts_dispatch_confirmed, igz_dispatch_number_1, ticket_notes_1]
        func_args_2 = [cts_dispatch_confirmed_2, igz_dispatch_number_2, ticket_notes_2]

        for _dispatch in dispatches:
            await cts_dispatch_monitor._process_generic_dispatch(dispatch=_dispatch)

        cts_dispatch_monitor._get_process_dispatch.assert_has_calls([
            call(cts_dispatch_confirmed),
        ])
        cts_dispatch_monitor._scheduler.add_job.assert_has_calls([
            call(get_process_dispatch_mock[0], 'date', next_run_time=undefined, replace_existing=False,
                 id=f"_process_dispatch_{dispatch_number_1}", args=func_args_1)
        ])

    @pytest.mark.asyncio
    async def cts_dispatch_monitoring_process_general_error_getting_dispatches_test(
            self, cts_dispatch_monitor, cts_dispatch, cts_dispatch_confirmed):
        dispatches = [cts_dispatch, cts_dispatch_confirmed]
        dispatches_response = {
            'status': 200,
            'body': {
                'done': False,
                'records': []
            }
        }
        err_msg = f'[CTS] Error: '
        cts_dispatch_monitor._cts_repository.get_all_dispatches = CoroutineMock(side_effect=Exception)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._cts_dispatch_monitoring_process()

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

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
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._cts_dispatch_monitoring_process()

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

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
    async def cts_distribute_and_process_dispatches_test(self, cts_dispatch_monitor,
                                                         cts_dispatch_not_confirmed,
                                                         cts_dispatch_confirmed,
                                                         cts_dispatch_confirmed_2,
                                                         cts_dispatch_confirmed_no_main_watermark,
                                                         cts_ticket_details_1, cts_ticket_details_2_error,
                                                         cts_ticket_details_2_no_requested_watermark,
                                                         cts_dispatch_confirmed_skipped,
                                                         cts_ticket_details_no_watermark):
        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        redis_data_1 = {
            "ticket_id": ticket_id_1,
            "igz_dispatch_number": "IGZ_0001"
        }
        redis_expire_ttl = cts_dispatch_monitor._config.DISPATCH_MONITOR_CONFIG['redis_ttl']
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2,
            cts_dispatch_confirmed_2,
            cts_dispatch_confirmed_no_main_watermark,
            cts_dispatch_confirmed_skipped,
            cts_dispatch_not_confirmed
        ]
        responses_details_mock = [
            cts_ticket_details_1,
            cts_ticket_details_1,
            cts_ticket_details_2_error,
            cts_ticket_details_2_no_requested_watermark,
            cts_ticket_details_no_watermark,
            cts_ticket_details_1
        ]
        cts_dispatch_monitor._redis_client.get = Mock(side_effect=[None, redis_data_1])
        cts_dispatch_monitor._redis_client.set = Mock()
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(side_effect=responses_details_mock)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()
        cts_dispatch_monitor._process_generic_dispatch = CoroutineMock()

        await cts_dispatch_monitor._distribute_and_process_dispatches(confirmed_dispatches)

        # cts_dispatch_monitor._redis_client.get.assert_has_calls([call(dispatch_number_1), call(dispatch_number_1)],
        #                                                         any_order=False)
        cts_dispatch_monitor._process_generic_dispatch.assert_has_awaits([
            call(cts_dispatch_confirmed),
            call(cts_dispatch_confirmed)
        ])
        # cts_dispatch_monitor._redis_client.set.assert_called_once_with(
        #     dispatch_number_1, json.dumps(redis_data_1), ex=redis_expire_ttl)

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_test(self, cts_dispatch_monitor, cts_dispatch_confirmed,
                                                cts_dispatch_not_confirmed,
                                                cts_dispatch_confirmed_2,
                                                cts_ticket_details_1,
                                                append_note_response, append_note_response_2,
                                                sms_success_response, sms_success_response_2):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_not_confirmed
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

        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        sms_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'
        datetime_1_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'

        confirmed_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {datetime_1_str}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

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
        slack_msg_note_1 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                           f"Confirmed Note, SMS send and Confirmed SMS note sent OK."
        slack_msg_tech_note_1 = f"[service-dispatch-monitor] [CTS] " \
                                f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                                f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK."
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [
            cts_ticket_details_1['body'].get('ticketNotes', []),
            []
        ]
        for confirmed_dispatch in confirmed_dispatches:
            await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                   igz_dispatch_numbers[i],
                                                                   ticket_notes[i])
            i = i + 1

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to, tech_name),
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

        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        sms_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_note_2 = f"#*MetTel's IPA*# {igz_dispatch_number_2}\n" \
                     f'Dispatch confirmation SMS sent to +12027723611\n'
        sms_tech_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'
        sms_tech_note_2 = f"#*MetTel's IPA*# {igz_dispatch_number_2}\n" \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_name_2 = cts_dispatch_confirmed_2.get('API_Resource_Name__c')

        # Get datetime formatted string
        datetime_1_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'
        datetime_2_str = 'Jun 23, 2020 @ 03:00 AM US/Pacific'

        confirmed_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {datetime_1_str}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'
        confirmed_note_2 = f"#*MetTel's IPA*# {igz_dispatch_number_2}\n" \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {datetime_2_str}\n\n' \
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
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [
            cts_ticket_details_1['body'].get('ticketNotes', []),
            cts_ticket_details_2['body'].get('ticketNotes', []),
        ]
        for confirmed_dispatch in confirmed_dispatches:
            await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                   igz_dispatch_numbers[i],
                                                                   ticket_notes[i])
            i = i + 1

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1),
            call(ticket_id_2, confirmed_note_2),
            call(ticket_id_2, sms_note_2),
            # call(ticket_id_2, sms_tech_note_2)
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to, tech_name),
            call(dispatch_number_2, ticket_id_2, datetime_2_str, sms_to_2, tech_name)
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
        sms_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_note_2 = f"#*MetTel's IPA*# {igz_dispatch_number_2}\n" \
                     f'Dispatch confirmation SMS sent to +12027723611\n'
        sms_tech_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'
        sms_tech_note_2 = f"#*MetTel's IPA*# {igz_dispatch_number_2}\n" \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_name_2 = cts_dispatch_confirmed_2.get('API_Resource_Name__c')

        # Get datetime formatted string
        datetime_1_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'
        datetime_2_str = 'Jun 23, 2020 @ 03:00 AM US/Pacific'
        confirmed_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {datetime_1_str}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'
        confirmed_note_2 = f"#*MetTel's IPA*# {igz_dispatch_number_2}\n" \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {datetime_2_str}\n\n' \
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
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [
            cts_ticket_details_1['body'].get('ticketNotes', []),
            []
        ]
        for confirmed_dispatch in confirmed_dispatches:
            await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                   igz_dispatch_numbers[i],
                                                                   ticket_notes[i])
            i = i + 1

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1),
            call(ticket_id_2, confirmed_note_2),
            call(ticket_id_2, sms_note_2),
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to, tech_name),
            call(dispatch_number_2, ticket_id_2, datetime_2_str, sms_to_2, tech_name_2)
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
            call(err_msg),
            call(slack_msg_tech_note_2),
        ])

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_with_general_exception_test(self, cts_dispatch_monitor):
        confirmed_dispatch = 0  # Non valid list for filter
        err_msg = f"Error: Dispatch [0] - IGZ_0001 - Not valid dispatch"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch, 'IGZ_0001', [])

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

        for confirmed_dispatch in confirmed_dispatches:
            await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch, 'IGZ_0001', [])

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

        igz_dispatch_numbers = ['IGZ_0001', 'IGZ_0002']
        ticket_notes = [
            []
        ]
        await cts_dispatch_monitor._process_confirmed_dispatch(cts_dispatch_confirmed_bad_date,
                                                               igz_dispatch_numbers[0],
                                                               ticket_notes[0])

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
        sms_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')

        # Get datetime formatted string
        datetime_1_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'

        confirmed_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {datetime_1_str}\n\n' \
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
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [
            cts_ticket_details_1['body'].get('ticketNotes', []),
            []
        ]
        for confirmed_dispatch in confirmed_dispatches:
            await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                   igz_dispatch_numbers[i],
                                                                   ticket_notes[i])
            i = i + 1

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to, tech_name)
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
        sms_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        dispatch_number_2 = cts_dispatch_confirmed_skipped_datetime.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_skipped_datetime.get('Ext_Ref_Num__c')
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_name_2 = cts_dispatch_confirmed_skipped_datetime.get('API_Resource_Name__c')

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'

        # Get datetime formatted string
        datetime_1_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'

        confirmed_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {datetime_1_str}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

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
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [
            cts_ticket_details_1['body'].get('ticketNotes', []),
            []
        ]
        for confirmed_dispatch in confirmed_dispatches:
            await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                   igz_dispatch_numbers[i],
                                                                   ticket_notes[i])
            i = i + 1

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1),
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to, tech_name)
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

        sms_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        dispatch_number_2 = cts_dispatch_confirmed_skipped_bad_phone.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_skipped_bad_phone.get('Ext_Ref_Num__c')
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_name_2 = cts_dispatch_confirmed_skipped_bad_phone.get('API_Resource_Name__c')

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'

        # Get datetime formatted string
        datetime_1_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'
        datetime_2_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'

        confirmed_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {datetime_1_str}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

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

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(sideffect=[])

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [
            cts_ticket_details_1['body'].get('ticketNotes', []),
            []
        ]
        for confirmed_dispatch in confirmed_dispatches:
            await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                   igz_dispatch_numbers[i],
                                                                   ticket_notes[i])
            i = i + 1

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to, tech_name)
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

        sms_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        dispatch_number_2 = cts_dispatch_confirmed_skipped_bad_phone_tech.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_skipped_bad_phone_tech.get('Ext_Ref_Num__c')
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_name_2 = cts_dispatch_confirmed_skipped_bad_phone_tech.get('API_Resource_Name__c')

        # Get datetime formatted string
        datetime_1_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'
        datetime_2_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'
        confirmed_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {datetime_1_str}\n\n' \
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

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(sideffect=[])

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [
            cts_ticket_details_1['body'].get('ticketNotes', []),
            []
        ]
        for confirmed_dispatch in confirmed_dispatches:
            await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                   igz_dispatch_numbers[i],
                                                                   ticket_notes[i])
            i = i + 1

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to, tech_name)
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
        sms_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_name_2 = cts_dispatch_confirmed_2.get('API_Resource_Name__c')

        # Get datetime formatted string
        datetime_1_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'

        confirmed_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {datetime_1_str}\n\n' \
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
        err_msg = f"Error: Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} - {cts_dispatch_confirmed_2}"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms_tech)

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [
            cts_ticket_details_1['body'].get('ticketNotes', []),
            []
        ]
        for confirmed_dispatch in confirmed_dispatches:
            await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                   igz_dispatch_numbers[i],
                                                                   ticket_notes[i])
            i = i + 1

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_note_1),
            call(ticket_id_1, sms_tech_note_1)
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to, tech_name)
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
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_name_2 = cts_dispatch_confirmed_2.get('API_Resource_Name__c')

        # Get datetime formatted string
        datetime_1_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'
        datetime_2_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'

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

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [
            cts_ticket_details_1['body'].get('ticketNotes', []),
            cts_ticket_details_2['body'].get('ticketNotes', [])
        ]
        for confirmed_dispatch in confirmed_dispatches:
            await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                   igz_dispatch_numbers[i],
                                                                   ticket_notes[i])
            i = i + 1

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to, tech_name)
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
        sms_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                     'Dispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'
        sms_note_2 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                     f'Dispatch confirmation SMS sent to +12027723611\n'
        sms_tech_note_2 = f"#*MetTel's IPA*# {igz_dispatch_number_2}\n" \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'

        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_name_2 = cts_dispatch_confirmed_2.get('API_Resource_Name__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'
        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        # Get datetime formatted string
        datetime_1_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'
        datetime_2_str = 'Jun 23, 2020 @ 03:00 AM US/Pacific'

        confirmed_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {datetime_1_str}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'
        confirmed_note_2 = f"#*MetTel's IPA*# {igz_dispatch_number_2}\n" \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {datetime_2_str}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

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
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_send_confirmed_sms_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_send_confirmed_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_note_mock)

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [
            cts_ticket_details_1['body'].get('ticketNotes', []),
            cts_ticket_details_2['body'].get('ticketNotes', [])
        ]
        for confirmed_dispatch in confirmed_dispatches:
            await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                   igz_dispatch_numbers[i],
                                                                   ticket_notes[i])
            i = i + 1

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_tech_note_1),
            call(ticket_id_2, confirmed_note_2),
            call(ticket_id_2, sms_tech_note_2),
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to, tech_name),
            call(dispatch_number_2, ticket_id_2, datetime_2_str, sms_to_2, tech_name_2)
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
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_name_2 = cts_dispatch_confirmed_2.get('API_Resource_Name__c')

        sms_to = '+12027723610'
        sms_to_2 = '+12027723611'
        sms_to_tech = '+12123595129'
        sms_to_2_tech = '+12123595129'

        # Get datetime formatted string
        datetime_1_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'
        datetime_2_str = 'Jun 23, 2020 @ 03:00 AM US/Pacific'

        confirmed_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {datetime_1_str}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'
        confirmed_note_2 = f"#*MetTel's IPA*# {igz_dispatch_number_2}\n" \
                           'Dispatch Management - Dispatch Confirmed\n' \
                           f'Dispatch scheduled for {datetime_2_str}\n\n' \
                           'Field Engineer\nMichael J. Fox\n+1 (212) 359-5129\n'

        sms_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                     f'Dispatch confirmation SMS sent to +12027723610\n'
        sms_tech_note_1 = f"#*MetTel's IPA*# {igz_dispatch_number_1}\n" \
                          f'Dispatch confirmation SMS tech sent to +12123595129\n'
        sms_note_2 = f"#*MetTel's IPA*# {igz_dispatch_number_2}\n" \
                     f'Dispatch confirmation SMS sent to +12027723611\n'
        sms_tech_note_2 = f"#*MetTel's IPA*# {igz_dispatch_number_2}\n" \
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
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_send_confirmed_sms_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_send_confirmed_sms_tech_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_sms_note = CoroutineMock(
            side_effect=responses_append_confirmed_sms_note_mock)

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [
            cts_ticket_details_1['body'].get('ticketNotes', []),
            cts_ticket_details_2['body'].get('ticketNotes', [])
        ]
        for confirmed_dispatch in confirmed_dispatches:
            await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                   igz_dispatch_numbers[i],
                                                                   ticket_notes[i])
            i = i + 1

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_has_awaits([
            call(ticket_id_1, confirmed_note_1),
            call(ticket_id_1, sms_tech_note_1),
            call(ticket_id_2, confirmed_note_2),
            call(ticket_id_2, sms_tech_note_2),
        ])

        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, datetime_1_str, sms_to, tech_name),
            call(dispatch_number_2, ticket_id_2, datetime_2_str, sms_to_2, tech_name_2)
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
    async def monitor_confirmed_dispatches_update_tech_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed,
            cts_ticket_details_1_with_confirmation_and_outdated_tech_note,
            cts_ticket_details_1_with_confirmation_and_multiple_outdated_tech_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        cts_dispatch_confirmed['Name'] = 'IGZ_0001'
        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_phone = cts_dispatch_confirmed.get('Resource_Phone_Number__c')
        datetime_1_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'

        responses_details_mock = [
            cts_ticket_details_1_with_confirmation_and_outdated_tech_note,
            cts_ticket_details_1_with_confirmation_and_multiple_outdated_tech_note
        ]

        # First not skipped, Second skipped
        responses_get_diff_hours = [
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1
        ]

        responses_append_confirmed_notes_mock = [
            True,
            True,
        ]
        responses_confirmed_sms = [
            True,
            True
        ]
        response_append_updated_sms_mock = [
            True,
            True
        ]
        response_send_updated_sms_mock = [
            True,
            True
        ]
        response_send_tech_updated_sms_mock = [
            True,
            True
        ]

        responses_send_tech_12_sms_mock = [
            True,
            True
        ]

        responses_send_tech_12_sms_note_mock = [
            True,
            True
        ]

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'

        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                      f"- A sms tech 12 hours before note appended"
        slack_msg_note_1 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                           f"- A sms tech 12 hours before note tech appended"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=responses_details_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.append_updated_tech_note = CoroutineMock(
            side_effect=response_append_updated_sms_mock)
        cts_dispatch_monitor._cts_repository.send_updated_tech_sms = CoroutineMock(
            side_effect=response_send_updated_sms_mock)
        cts_dispatch_monitor._cts_repository.send_updated_tech_sms_tech = CoroutineMock(
            side_effect=response_send_tech_updated_sms_mock)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech = CoroutineMock(
            side_effect=responses_send_tech_12_sms_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)
        cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note = CoroutineMock(
            side_effect=responses_send_tech_12_sms_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            i = 0
            igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_1]
            ticket_notes = [
                cts_ticket_details_1_with_confirmation_and_outdated_tech_note['body'].get('ticketNotes', []),
                cts_ticket_details_1_with_confirmation_and_multiple_outdated_tech_note['body'].get('ticketNotes', [])
            ]
            for confirmed_dispatch in confirmed_dispatches:
                await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                       igz_dispatch_numbers[i],
                                                                       ticket_notes[i])
                i = i + 1

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.append_updated_tech_note.assert_has_awaits(
            [
                call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed),
                # call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed)
            ],
            any_order=False
        )
        cts_dispatch_monitor._cts_repository.send_updated_tech_sms.assert_has_awaits(
            [
                call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to, tech_name),
                # call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to, tech_name)
            ],
            any_order=False
        )
        cts_dispatch_monitor._cts_repository.send_updated_tech_sms_tech.assert_has_awaits(
            [
                call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech),
                # call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech)
            ],
            any_order=False
        )

    @pytest.mark.asyncio
    async def monitor_confirmed_dispatches_update_tech_with_errors_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_ticket_details_1_with_confirmation_and_outdated_tech_note,
            cts_ticket_details_2_with_confirmation_and_outdated_tech_note):
        confirmed_dispatches = [
            cts_dispatch_confirmed,
            cts_dispatch_confirmed_2
        ]
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'
        cts_dispatch_confirmed['Name'] = 'IGZ_0001'
        dispatch_number_1 = cts_dispatch_confirmed.get('Name')
        ticket_id_1 = cts_dispatch_confirmed.get('Ext_Ref_Num__c')
        time_1 = cts_dispatch_confirmed.get('Local_Site_Time__c')
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_phone = cts_dispatch_confirmed.get('Resource_Phone_Number__c')
        datetime_1_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'
        cts_dispatch_confirmed_2['Name'] = 'IGZ_0002'
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')
        time_2 = cts_dispatch_confirmed_2.get('Local_Site_Time__c')
        tech_name_2 = cts_dispatch_confirmed_2.get('API_Resource_Name__c')
        tech_phone_2 = cts_dispatch_confirmed_2.get('Resource_Phone_Number__c')
        datetime_2_str = 'Jun 23, 2020 @ 03:00 AM US/Pacific'

        responses_details_mock = [
            cts_ticket_details_1_with_confirmation_and_outdated_tech_note,
            cts_ticket_details_2_with_confirmation_and_outdated_tech_note
        ]

        # First not skipped, Second skipped
        responses_get_diff_hours = [
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1
        ]

        responses_append_confirmed_notes_mock = [
            True,
            False,
        ]
        responses_confirmed_sms = [
            True,
            False
        ]
        response_append_updated_sms_mock = [
            True,
            False
        ]
        response_send_updated_sms_mock = [
            True,
            False
        ]
        response_send_tech_updated_sms_mock = [
            True,
            False
        ]

        responses_send_tech_12_sms_mock = [
            True,
            True
        ]

        responses_send_tech_12_sms_note_mock = [
            True,
            True
        ]

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'
        sms_to_2 = '+12027723611'
        sms_to_tech_2 = '+12123595129'

        responses_send_slack_message_mock = [
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
            {'status': 200},
        ]
        slack_msg_1 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                      f"- A sms tech 12 hours before note appended"
        slack_msg_note_1 = f"[service-dispatch-monitor] [CTS] " \
                           f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                           f"- A sms tech 12 hours before note tech appended"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.append_updated_tech_note = CoroutineMock(
            side_effect=response_append_updated_sms_mock)
        cts_dispatch_monitor._cts_repository.send_updated_tech_sms = CoroutineMock(
            side_effect=response_send_updated_sms_mock)
        cts_dispatch_monitor._cts_repository.send_updated_tech_sms_tech = CoroutineMock(
            side_effect=response_send_tech_updated_sms_mock)
        cts_dispatch_monitor._cts_repository.send_sms = CoroutineMock(side_effect=[True, True])
        cts_dispatch_monitor._cts_repository.append_note = CoroutineMock(side_effect=[True, True])

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            i = 0
            igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
            ticket_notes = [
                cts_ticket_details_1_with_confirmation_and_outdated_tech_note['body'].get('ticketNotes', []),
                cts_ticket_details_2_with_confirmation_and_outdated_tech_note['body'].get('ticketNotes', []),
            ]
            for confirmed_dispatch in confirmed_dispatches:
                await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                       igz_dispatch_numbers[i],
                                                                       ticket_notes[i])
                i = i + 1

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.append_updated_tech_note.assert_has_awaits(
            [
                call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed),
                call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2)
            ],
            any_order=False
        )
        cts_dispatch_monitor._cts_repository.send_updated_tech_sms.assert_has_awaits(
            [
                call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to, tech_name),
                call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, datetime_2_str, sms_to_2, tech_name_2)
            ],
            any_order=False
        )
        cts_dispatch_monitor._cts_repository.send_updated_tech_sms_tech.assert_has_awaits(
            [
                call(dispatch_number_1, ticket_id_1, cts_dispatch_confirmed, datetime_1_str, sms_to_tech),
                call(dispatch_number_2, ticket_id_2, cts_dispatch_confirmed_2, datetime_2_str, sms_to_tech_2)
            ],
            any_order=False
        )

        updated_tech_note_1 = f"[service-dispatch-monitor] [CTS] " \
                              f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                              f"- A updated tech note appended"
        updated_tech_sms_1 = f"[service-dispatch-monitor] [CTS] " \
                             f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                             f"- A updated tech sms sent"
        updated_tech_sms_tech_1 = f"[service-dispatch-monitor] [CTS] " \
                                  f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                                  f"- A updated tech sms tech sent"
        sms_tech_12_note_1 = f"[service-dispatch-monitor] [CTS] " \
                             f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 " \
                             f"- Reminder 12 hours for client - A sms before note appended"
        sms_tech_12_tech_note_1 = f"[service-dispatch-monitor] [CTS] " \
                                  f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 " \
                                  f"- Reminder 12 hours for tech - A sms before note appended"
        updated_tech_note_2 = f"[service-dispatch-monitor] [CTS] " \
                              f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} " \
                              f"- An updated tech note not appended"
        updated_tech_sms_2 = f"[service-dispatch-monitor] [CTS] " \
                             f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} " \
                             f"- An updated tech sms not sent"
        updated_tech_sms_tech_2 = f"[service-dispatch-monitor] [CTS] " \
                                  f"Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} " \
                                  f"- An updated tech sms tech not sent"

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(updated_tech_note_1),
            call(updated_tech_sms_1),
            call(updated_tech_sms_tech_1),
            call(sms_tech_12_note_1),
            call(sms_tech_12_tech_note_1),
            call(updated_tech_note_2),
            call(updated_tech_sms_2),
            call(updated_tech_sms_tech_2),
        ])

        cts_dispatch_monitor._cts_repository.send_sms.assert_awaited()
        cts_dispatch_monitor._cts_repository.append_note.assert_awaited()

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

        sms_to = '+12027723610'
        sms_to_tech = '+12123595129'
        # Get datetime formatted string
        datetime_1_str = 'Jun 23, 2020 @ 03:00 PM US/Pacific'

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
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1
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
                f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: {igz_dispatch_number_1} - ' \
                f'Reminder 12 hours for client - A sms before note appended'
        msg_1_tech = f'[service-dispatch-monitor] [CTS] ' \
                     f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: {igz_dispatch_number_1} - ' \
                     f'Reminder 12 hours for tech - A sms before note appended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)

        send_sms_mock = [
            True,
            True,
        ]
        append_note_mock = [
            True,
            True,
        ]

        sms_payload_client = {
            'date_of_dispatch': datetime_1_str,
            'phone_number': sms_to,
            'hours': 12
        }
        sms_data_payload_client = {
            'sms_to': '12027723610',
            'sms_data': 'This is an automated message from MetTel.\n\n'
                        'A field engineer will arrive in 12 hours, Jun 23, 2020 @ 03:00 PM US/Pacific, '
                        'at your location.\n\nYou will receive a text message at this number when they have arrived.\n'
        }
        sms_payload_tech = {
            'date_of_dispatch': datetime_1_str,
            'phone_number': sms_to_tech,
            'site': 'Premier Financial Bancorp',
            'street': '1501 K St NW',
            'hours': 12
        }
        sms_data_payload_tech = {
            'sms_to': '12027723610',
            'sms_data': 'This is an automated message from MetTel.\n\n'
                        'You have a dispatch coming up in 12 hours, Jun 23, 2020 @ 03:00 PM US/Pacific.\n'
                        'For Premier Financial Bancorp at 1501 K St NW\n'
        }
        sms_note = f"#*MetTel's IPA*# IGZ_0001\nDispatch 12h prior reminder SMS sent to +12027723610\n"
        sms_note_tech = f"#*MetTel's IPA*# IGZ_0001\nDispatch 12h prior reminder tech SMS sent to +12123595129\n"

        cts_dispatch_monitor._cts_repository.send_sms = CoroutineMock(side_effect=send_sms_mock)
        cts_dispatch_monitor._cts_repository.append_note = CoroutineMock(side_effect=append_note_mock)

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            i = 0
            igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
            ticket_notes = [
                cts_ticket_details_1_with_confirmation_note['body'].get('ticketNotes', []),
                cts_ticket_details_2_with_confirmation_note['body'].get('ticketNotes', []),
            ]
            for confirmed_dispatch in confirmed_dispatches:
                await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                       igz_dispatch_numbers[i],
                                                                       ticket_notes[i])
                i = i + 1

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._cts_repository.send_sms.assert_has_awaits([
            call(dispatch_number_1, ticket_id_1, sms_to, 12.0, sms_payload_client, sms_data_payload_client),
            call(dispatch_number_1, ticket_id_1, sms_to_tech, 12.0, sms_payload_tech, sms_data_payload_tech),
        ])
        cts_dispatch_monitor._cts_repository.append_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, 12.0, sms_note),
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, 12.0, sms_note_tech),
        ])

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(msg_1),
            call(msg_1_tech),
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
        datetime_1_str = 'Jun 23, 2020 @ 01:00 PM UTC'
        datetime_2_str = 'Jun 23, 2020 @ 01:00 PM UTC'

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
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 + 1
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
                f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                f'- Reminder 12 hours for client - A sms before note appended'
        msg_1_tech = f'[service-dispatch-monitor] [CTS] ' \
                     f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                     f'- Reminder 12 hours for tech - A sms before note appended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_sms = CoroutineMock(side_effect=[True, True])
        cts_dispatch_monitor._cts_repository.append_note = CoroutineMock(side_effect=[True, True])

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            i = 0
            igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
            ticket_notes = [
                cts_ticket_details_1_with_confirmation_note['body'].get('ticketNotes', []),
                cts_ticket_details_2_with_confirmation_note['body'].get('ticketNotes', []),
            ]
            for confirmed_dispatch in confirmed_dispatches:
                await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                       igz_dispatch_numbers[i],
                                                                       ticket_notes[i])
                i = i + 1

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()
        # TODO: proper calls
        cts_dispatch_monitor._cts_repository.send_sms.assert_awaited()
        cts_dispatch_monitor._cts_repository.append_note.assert_awaited()

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(msg_1),
            call(msg_1_tech)
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
        datetime_1_str = 'Jun 23, 2020 @ 01:00 PM UTC'
        datetime_2_str = 'Jun 23, 2020 @ 01:00 PM UTC'

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
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_12 * 1.0 - 1
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
                f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                f'- Reminder 12 hours for client - A sms before note not appended'
        msg_note_1 = f'[service-dispatch-monitor] [CTS] ' \
                     f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                     f'- Reminder 12 hours for tech - A sms before note appended'
        msg_2 = f'[service-dispatch-monitor] [CTS] ' \
                f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} - IGZ: IGZ_0002 ' \
                f'- Reminder 12 hours for client - A sms before note not appended'
        msg_note_2 = f'[service-dispatch-monitor] [CTS] ' \
                     f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} - IGZ: IGZ_0002 ' \
                     f'- Reminder 12 hours for tech - A sms before note not appended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_sms = CoroutineMock(side_effect=[True, True, True, True])
        cts_dispatch_monitor._cts_repository.append_note = CoroutineMock(side_effect=[False, True, False, False])

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            i = 0
            igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
            ticket_notes = [
                cts_ticket_details_1_with_confirmation_note['body'].get('ticketNotes', []),
                cts_ticket_details_2_with_confirmation_note['body'].get('ticketNotes', []),
            ]
            for confirmed_dispatch in confirmed_dispatches:
                await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                       igz_dispatch_numbers[i],
                                                                       ticket_notes[i])
                i = i + 1

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        # TODO: proper calls
        cts_dispatch_monitor._cts_repository.send_sms.assert_awaited()
        cts_dispatch_monitor._cts_repository.append_note.assert_awaited()

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

        responses_append_confirmed_notes_mock = [
            True,
            True,
        ]
        responses_confirmed_sms = [
            True,
            True
        ]

        responses_get_diff_hours = [
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1
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
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                      f'- Reminder 2 hours for client - A sms before note appended'
        slack_msg_2 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                      f'- Reminder 2 hours for tech - A sms before note appended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)

        cts_dispatch_monitor._cts_repository.send_sms = CoroutineMock(side_effect=[
            True, True, True, True, True, True])
        cts_dispatch_monitor._cts_repository.append_note = CoroutineMock(side_effect=[
            True, True, True, True, True, True])

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            i = 0
            igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
            ticket_notes = [
                cts_ticket_details_1_with_12h_sms_note['body'].get('ticketNotes', []),
                cts_ticket_details_2_with_12h_sms_note['body'].get('ticketNotes', []),
            ]
            for confirmed_dispatch in confirmed_dispatches:
                await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                       igz_dispatch_numbers[i],
                                                                       ticket_notes[i])
                i = i + 1

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        # TODO: proper calls
        cts_dispatch_monitor._cts_repository.send_sms.assert_awaited()
        cts_dispatch_monitor._cts_repository.append_note.assert_awaited()

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_2)
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
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1
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
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                      f'- Reminder 2 hours for client - A sms before note appended'
        slack_msg_sms_1 = f'[service-dispatch-monitor] [CTS] ' \
                          f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                          f'- Reminder 2 hours for tech - A sms before note appended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)

        cts_dispatch_monitor._cts_repository.send_sms = CoroutineMock(side_effect=[
            True, True, False, True, True, True])
        cts_dispatch_monitor._cts_repository.append_note = CoroutineMock(side_effect=[
            True, True, True, True, True, True])

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            i = 0
            igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
            ticket_notes = [
                cts_ticket_details_1_with_12h_sms_note['body'].get('ticketNotes', []),
                cts_ticket_details_2_with_12h_sms_note['body'].get('ticketNotes', []),
            ]
            for confirmed_dispatch in confirmed_dispatches:
                await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                       igz_dispatch_numbers[i],
                                                                       ticket_notes[i])
                i = i + 1

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        # TODO: proper calls
        cts_dispatch_monitor._cts_repository.send_sms.assert_awaited()
        cts_dispatch_monitor._cts_repository.append_note.assert_awaited()

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_sms_1),
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
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1
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
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                      f'- Reminder 2 hours for client - SMS 2.0h not sended'
        slack_msg_sms_1 = f'[service-dispatch-monitor] [CTS] ' \
                          f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                          f'- Reminder 2 hours for tech - A sms before note not appended'

        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_sms = CoroutineMock(side_effect=[
            False, True, True, True, True, True])
        cts_dispatch_monitor._cts_repository.append_note = CoroutineMock(side_effect=[
            False, True, True, True, True, True])

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            i = 0
            igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
            ticket_notes = [
                cts_ticket_details_1_with_12h_sms_note['body'].get('ticketNotes', []),
                cts_ticket_details_2_with_12h_sms_note['body'].get('ticketNotes', []),
            ]
            for confirmed_dispatch in confirmed_dispatches:
                await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                       igz_dispatch_numbers[i],
                                                                       ticket_notes[i])
                i = i + 1

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        # TODO: proper calls
        cts_dispatch_monitor._cts_repository.send_sms.assert_awaited()
        cts_dispatch_monitor._cts_repository.append_note.assert_awaited()

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_sms_1),
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
        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')

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
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1
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
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                      f'- Reminder 2 hours for client - A sms before note appended'
        slack_msg_sms_1 = f'[service-dispatch-monitor] [CTS] ' \
                          f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                          f'- Reminder 2 hours for tech - A sms before note appended'
        slack_msg_2 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} - IGZ: IGZ_0002 ' \
                      f'- Reminder 2 hours for client - A sms before note appended'
        slack_msg_sms_2 = f'[service-dispatch-monitor] [CTS] ' \
                          f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} - IGZ: IGZ_0002 ' \
                          f'- Reminder 2 hours for tech - A sms before note appended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)

        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_sms = CoroutineMock(side_effect=[
            True, True, True, True, True, True])
        cts_dispatch_monitor._cts_repository.append_note = CoroutineMock(side_effect=[
            True, True, True, True, True, True])

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            i = 0
            igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
            ticket_notes = [
                cts_ticket_details_1_with_12h_sms_note['body'].get('ticketNotes', []),
                cts_ticket_details_2_with_12h_sms_note['body'].get('ticketNotes', []),
            ]
            for confirmed_dispatch in confirmed_dispatches:
                await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                       igz_dispatch_numbers[i],
                                                                       ticket_notes[i])
                i = i + 1

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        # TODO: proper calls
        cts_dispatch_monitor._cts_repository.send_sms.assert_awaited()
        cts_dispatch_monitor._cts_repository.append_note.assert_awaited()

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_sms_1),
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
        datetime_1_str = 'Jun 23, 2020 @ 01:00 PM UTC'
        datetime_2_str = 'Jun 23, 2020 @ 01:00 PM UTC'

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
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
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
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                      f'- Reminder 2 hours for client - A sms before note appended'
        slack_msg_sms_1 = f'[service-dispatch-monitor] [CTS] ' \
                          f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                          f'- Reminder 2 hours for tech - A sms before note appended'

        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)

        cts_dispatch_monitor._cts_repository.send_sms = CoroutineMock(side_effect=[
            True, True, True, True, True, True])
        cts_dispatch_monitor._cts_repository.append_note = CoroutineMock(side_effect=[
            True, True, True, True, True, True])

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            i = 0
            igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
            ticket_notes = [
                cts_ticket_details_1_with_12h_sms_note['body'].get('ticketNotes', []),
                cts_ticket_details_2_with_12h_sms_note['body'].get('ticketNotes', []),
            ]
            for confirmed_dispatch in confirmed_dispatches:
                await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                       igz_dispatch_numbers[i],
                                                                       ticket_notes[i])
                i = i + 1

        # TODO: proper calls
        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
            call(slack_msg_sms_1),
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
        datetime_1_str = 'Jun 23, 2020 @ 01:00 PM UTC'
        datetime_2_str = 'Jun 23, 2020 @ 01:00 PM UTC'

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
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
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
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                      f'- Reminder 2 hours for tech - A sms before note appended'
        slack_msg_2 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} - IGZ: IGZ_0002 ' \
                      f'- Reminder 2 hours for tech - A sms before note appended'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)
        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)

        cts_dispatch_monitor._cts_repository.send_sms = CoroutineMock(side_effect=[
            True, True, True, True, True, True])
        cts_dispatch_monitor._cts_repository.append_note = CoroutineMock(side_effect=[
            True, True, True, True, True, True])

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            i = 0
            igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
            ticket_notes = [
                cts_ticket_details_1_with_2h_sms_note['body'].get('ticketNotes', []),
                cts_ticket_details_2_with_2h_sms_note['body'].get('ticketNotes', []),
            ]
            for confirmed_dispatch in confirmed_dispatches:
                await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                       igz_dispatch_numbers[i],
                                                                       ticket_notes[i])
                i = i + 1

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        # TODO: proper calls
        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

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

        dispatch_number_2 = cts_dispatch_confirmed_2.get('Name')
        ticket_id_2 = cts_dispatch_confirmed_2.get('Ext_Ref_Num__c')

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
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1
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
                      f'Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} - IGZ: IGZ_0001 ' \
                      f'- Reminder 2 hours for tech - SMS 2.0h not sended'
        slack_msg_2 = f'[service-dispatch-monitor] [CTS] ' \
                      f'Dispatch [{dispatch_number_2}] in ticket_id: {ticket_id_2} - IGZ: IGZ_0002 ' \
                      f'- Reminder 2 hours for tech - SMS 2.0h not sended'

        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(
            side_effect=responses_send_slack_message_mock)

        cts_dispatch_monitor._cts_repository.append_confirmed_note = CoroutineMock(
            side_effect=responses_append_confirmed_notes_mock)
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock(
            side_effect=responses_confirmed_sms)
        cts_dispatch_monitor._cts_repository.send_sms = CoroutineMock(side_effect=[
            False, False, False, False, True, False])
        cts_dispatch_monitor._cts_repository.append_note = CoroutineMock(side_effect=[
            True, False, True, False, True, False])

        with patch.object(UtilsRepository, 'get_diff_hours_between_datetimes', side_effect=responses_get_diff_hours):
            i = 0
            igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
            ticket_notes = [
                cts_ticket_details_1_with_2h_sms_note['body'].get('ticketNotes', []),
                cts_ticket_details_2_with_2h_sms_note['body'].get('ticketNotes', []),
            ]
            for confirmed_dispatch in confirmed_dispatches:
                await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                       igz_dispatch_numbers[i],
                                                                       ticket_notes[i])
                i = i + 1

        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        # TODO: proper calls
        cts_dispatch_monitor._cts_repository.append_confirmed_note.assert_not_awaited()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms.assert_not_awaited()

        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([
            call(slack_msg_1),
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
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 - 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1,
            cts_dispatch_monitor._cts_repository.HOURS_2 * 1.0 + 1
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
            i = 0
            igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
            ticket_notes = [
                cts_ticket_details_1_with_2h_sms_tech_note['body'].get('ticketNotes', [])
            ]
            for confirmed_dispatch in confirmed_dispatches:
                await cts_dispatch_monitor._process_confirmed_dispatch(confirmed_dispatch,
                                                                       igz_dispatch_numbers[i],
                                                                       ticket_notes[i])
                i = i + 1

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

        cts_dispatch_monitor._cts_repository.send_tech_on_site_sms = CoroutineMock(
            side_effect=responses_sms_tech_on_site_mock)
        cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2, '', '']
        ticket_notes = [
            cts_ticket_details_1['body'].get('ticketNotes', []),
            cts_ticket_details_2['body'].get('ticketNotes', []),
            [],
            [],
        ]
        for tech_on_site_dispatch in tech_on_site_dispatches:
            await cts_dispatch_monitor._process_tech_on_site_dispatch(tech_on_site_dispatch,
                                                                      igz_dispatch_numbers[i],
                                                                      ticket_notes[i])
            i = i + 1

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
        tech_on_site_dispatch = 0  # Non valid list for filter
        err_msg = f"Error: Dispatch [0] - IGZ_0001 - Not valid dispatch"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._process_tech_on_site_dispatch(tech_on_site_dispatch, 'IGZ_0001', [])

        cts_dispatch_monitor._logger.error.assert_called_once()
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_with_exception_test(
            self, cts_dispatch_monitor, cts_dispatch_tech_on_site):
        igz_id_1 = 'IGZ_0001'
        err_msg = f"Error: Dispatch [{cts_dispatch_tech_on_site}] in igz_id: {igz_id_1}"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._process_tech_on_site_dispatch(cts_dispatch_tech_on_site, 'IGZ_0001', [])

        cts_dispatch_monitor._logger.error.assert_called_once()
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_tech_on_site_dispatches_skipping_one_invalid_ticket_id_test(self, cts_dispatch_monitor,
                                                                                  cts_dispatch_tech_on_site_skipped,
                                                                                  cts_dispatch_confirmed):
        tech_on_site_dispatches = [
            cts_dispatch_tech_on_site_skipped,
            cts_dispatch_confirmed
        ]

        cts_dispatch_monitor._bruin_repository.get_ticket_details = CoroutineMock()
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock()
        cts_dispatch_monitor._cts_repository.send_confirmed_sms = CoroutineMock()

        for tech_on_site_dispatch in tech_on_site_dispatches:
            await cts_dispatch_monitor._process_tech_on_site_dispatch(tech_on_site_dispatch, 'IGZ_0001', [])

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

        # cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(return_value=err_msg)

        for tech_on_site_dispatch in tech_on_site_dispatches:
            await cts_dispatch_monitor._process_tech_on_site_dispatch(tech_on_site_dispatch, 'IGZ_0001', [])

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

        cts_dispatch_monitor._cts_repository.send_tech_on_site_sms = CoroutineMock(
            side_effect=responses_sms_tech_on_site_mock)
        cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        err_msg = f"An error occurred retrieve getting ticket details from bruin " \
                  f"Dispatch: {dispatch_number_2} - Ticket_id: {ticket_id_2}"

        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock(return_value=err_msg)

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [
            cts_ticket_details_1['body'].get('ticketNotes', []),
            [],
        ]
        for tech_on_site_dispatch in tech_on_site_dispatches:
            await cts_dispatch_monitor._process_tech_on_site_dispatch(tech_on_site_dispatch,
                                                                      igz_dispatch_numbers[i],
                                                                      ticket_notes[i])
            i = i + 1

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

        cts_dispatch_monitor._cts_repository.send_tech_on_site_sms = CoroutineMock(
            side_effect=responses_sms_tech_on_site_mock)
        cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [
            cts_ticket_details_1['body'].get('ticketNotes', []),
            cts_ticket_details_2['body'].get('ticketNotes', []),
        ]
        for tech_on_site_dispatch in tech_on_site_dispatches:
            await cts_dispatch_monitor._process_tech_on_site_dispatch(tech_on_site_dispatch,
                                                                      igz_dispatch_numbers[i],
                                                                      ticket_notes[i])
            i = i + 1

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

        cts_dispatch_monitor._cts_repository.send_tech_on_site_sms = CoroutineMock(
            side_effect=responses_sms_tech_on_site_mock)
        cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note = CoroutineMock(
            side_effect=responses_append_tech_on_site_sms_note_mock)

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [
            cts_ticket_details_1['body'].get('ticketNotes', []),
            cts_ticket_details_2['body'].get('ticketNotes', []),
        ]
        for tech_on_site_dispatch in tech_on_site_dispatches:
            await cts_dispatch_monitor._process_tech_on_site_dispatch(tech_on_site_dispatch,
                                                                      igz_dispatch_numbers[i],
                                                                      ticket_notes[i])
            i = i + 1

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
        igz_dispatch_number_1 = 'IGZ_0001'
        igz_dispatch_number_2 = 'IGZ_0002'

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

        cts_dispatch_monitor._cts_repository.send_tech_on_site_sms = CoroutineMock()
        cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note = CoroutineMock()

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [
            cts_ticket_details_1_with_tech_on_site_sms_note['body'].get('ticketNotes', []),
            cts_ticket_details_2_with_tech_on_site_sms_note['body'].get('ticketNotes', []),
        ]
        for tech_on_site_dispatch in tech_on_site_dispatches:
            await cts_dispatch_monitor._process_tech_on_site_dispatch(tech_on_site_dispatch,
                                                                      igz_dispatch_numbers[i],
                                                                      ticket_notes[i])
            i = i + 1

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
        datetime_of_dispatch_1 = 'Jun 23, 2020 @ 03:00 PM US/Pacific'

        responses_append_dispatch_cancelled_note_mock = [
            True
        ]
        slack_msg = f"[service-dispatch-monitor] [CTS] " \
                    f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                    f"- A cancelled dispatch note appended"
        ticket_notes_1 = cts_ticket_details_1['body'].get('ticketNotes', [])

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note = CoroutineMock(
            side_effect=responses_append_dispatch_cancelled_note_mock)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        for canceled_dispatch in cancelled_dispatches:
            await cts_dispatch_monitor._process_canceled_dispatch(canceled_dispatch, 'IGZ_0001', ticket_notes_1)

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, datetime_of_dispatch_1)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(slack_msg)

    @pytest.mark.asyncio
    async def monitor_cancelled_dispatches_with_general_exception_test(
            self, cts_dispatch_monitor):
        canceled_dispatch = 0  # Non valid list for filter
        err_msg = f"Error: Dispatch [0] - IGZ_XXXX - Not valid dispatch"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        await cts_dispatch_monitor._process_canceled_dispatch(canceled_dispatch, 'IGZ_XXXX', [])

        cts_dispatch_monitor._logger.error.assert_called_once()
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)

    @pytest.mark.asyncio
    async def monitor_cancelled_dispatches_with_exception_test(
            self, cts_dispatch_monitor, cts_dispatch_cancelled, cts_ticket_details_1):
        cancelled_dispatches = [
            cts_dispatch_cancelled,
        ]
        igz_ticket_id_1 = 'IGZ_0001'
        err_msg = f"Error: Dispatch [{cts_dispatch_cancelled}] " \
                  f"in igz_id: {igz_ticket_id_1}"
        ticket_notes_1 = cts_ticket_details_1['body'].get('ticketNotes', [])

        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        for canceled_dispatch in cancelled_dispatches:
            await cts_dispatch_monitor._process_canceled_dispatch(
                canceled_dispatch, igz_ticket_id_1, ticket_notes_1)

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

        ticket_notes_1 = cts_ticket_details_1['body'].get('ticketNotes', [])
        ticket_notes_2 = []

        datetime_of_dispatch_1 = 'Jun 23, 2020 @ 03:00 PM US/Pacific'

        responses_append_dispatch_cancelled_note_mock = [
            True
        ]
        slack_msg_1 = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                      f"- A cancelled dispatch note appended"

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note = CoroutineMock(
            side_effect=responses_append_dispatch_cancelled_note_mock)
        err_msg = f"Error: Dispatch [{cts_dispatch_cancelled_2}] - {igz_dispatch_number_2} - Not valid dispatch"

        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        i = 0
        igz_dispatch_numbers = [igz_dispatch_number_1, igz_dispatch_number_2]
        ticket_notes = [ticket_notes_1, ticket_notes_2]
        for canceled_dispatch in cancelled_dispatches:
            await cts_dispatch_monitor._process_canceled_dispatch(
                canceled_dispatch, igz_dispatch_numbers[i], ticket_notes[i])
            i = i + 1

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, datetime_of_dispatch_1)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_has_awaits([call(slack_msg_1),
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

        igz_dispatch_number_1 = 'IGZ_0001'
        ticket_notes_1 = cts_ticket_details_1_with_cancelled_note['body'].get('ticketNotes', [])

        dispatch_number_1 = cts_dispatch_cancelled.get('Name')
        ticket_id_1 = cts_dispatch_cancelled.get('Ext_Ref_Num__c')

        responses_append_dispatch_cancelled_note_mock = [
            True
        ]
        slack_msg = f"[service-dispatch-monitor] [CTS] " \
                    f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                    f"- A cancelled dispatch note appended"

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note = CoroutineMock(
            side_effect=responses_append_dispatch_cancelled_note_mock)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        for canceled_dispatch in cancelled_dispatches:
            await cts_dispatch_monitor._process_canceled_dispatch(
                canceled_dispatch, igz_dispatch_number_1, ticket_notes_1)

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note.assert_not_awaited()
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def monitor_cancelled_dispatches_not_appended_test(self, cts_dispatch_monitor, cts_dispatch_cancelled,
                                                             cts_ticket_details_1, cts_dispatch_confirmed_2):
        cancelled_dispatches = [
            cts_dispatch_cancelled,
            cts_dispatch_confirmed_2
        ]

        responses_details_mock = [
            cts_ticket_details_1
        ]

        igz_dispatch_number_1 = 'IGZ_0001'
        dispatch_number_1 = cts_dispatch_cancelled.get('Name')
        ticket_id_1 = cts_dispatch_cancelled.get('Ext_Ref_Num__c')
        datetime_of_dispatch_1 = 'Jun 23, 2020 @ 03:00 PM US/Pacific'
        ticket_notes_1 = cts_ticket_details_1['body'].get('ticketNotes', [])

        responses_append_dispatch_cancelled_note_mock = [
            False
        ]
        slack_msg = f"[service-dispatch-monitor] [CTS] " \
                    f"Dispatch [{dispatch_number_1}] in ticket_id: {ticket_id_1} " \
                    f"- A cancelled dispatch note not appended"

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note = CoroutineMock(
            side_effect=responses_append_dispatch_cancelled_note_mock)
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        for canceled_dispatch in cancelled_dispatches:
            await cts_dispatch_monitor._process_canceled_dispatch(
                canceled_dispatch, igz_dispatch_number_1, ticket_notes_1)

        cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note.assert_has_awaits([
            call(dispatch_number_1, igz_dispatch_number_1, ticket_id_1, datetime_of_dispatch_1)
        ])
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(slack_msg)
