import json

from datetime import datetime
from time import perf_counter
import iso8601
import pytz


from apscheduler.util import undefined
from pytz import timezone

from application.repositories.bruin_repository import BruinRepository
from application.repositories.utils_repository import UtilsRepository
from application.repositories.cts_repository import CtsRepository


class CtsDispatchMonitor:
    def __init__(self, config, redis_client, event_bus, scheduler, logger, cts_repository, bruin_repository,
                 notifications_repository):
        self._config = config
        self._redis_client = redis_client
        self._scheduler = scheduler
        self._event_bus = event_bus
        self._logger = logger
        self._cts_repository = cts_repository
        self._bruin_repository = bruin_repository
        self._notifications_repository = notifications_repository

        self.HOURS_12 = 12.0
        self.HOURS_6 = 6.0
        self.HOURS_2 = 2.0

        # Dispatch Notes watermarks
        self.MAIN_WATERMARK = '#*Automation Engine*#'
        self.IGZ_DN_WATERMARK = 'IGZ'
        self.DISPATCH_REQUESTED_WATERMARK = 'Dispatch Management - Dispatch Requested'
        self.DISPATCH_CONFIRMED_WATERMARK = 'Dispatch Management - Dispatch Confirmed'
        self.DISPATCH_FIELD_ENGINEER_ON_SITE_WATERMARK = 'Dispatch Management - Field Engineer On Site'
        self.DISPATCH_REPAIR_COMPLETED_WATERMARK = 'Dispatch Management - Repair Completed'
        self.DISPATCH_CANCELLED_WATERMARK = 'Dispatch Management - Dispatch Cancelled'
        self.DISPATCH_UPDATED_TECH_WATERMARK = 'The Field Engineer assigned to this dispatch has changed'

        # SMS Notes watermarks
        self.DISPATCH_CONFIRMED_SMS_WATERMARK = 'Dispatch confirmation SMS sent to'
        self.DISPATCH_CONFIRMED_SMS_TECH_WATERMARK = 'Dispatch confirmation SMS tech sent to'
        self.TECH_12_HOURS_BEFORE_SMS_WATERMARK = 'Dispatch 12h prior reminder SMS'
        self.TECH_12_HOURS_BEFORE_SMS_TECH_WATERMARK = 'Dispatch 12h prior reminder tech SMS'
        self.TECH_2_HOURS_BEFORE_SMS_WATERMARK = 'Dispatch 2h prior reminder SMS'
        self.TECH_2_HOURS_BEFORE_SMS_TECH_WATERMARK = 'Dispatch 2h prior reminder tech SMS'
        self.TECH_ON_SITE_SMS_WATERMARK = 'Dispatch tech on site SMS'

    async def start_monitoring_job(self, exec_on_start):
        self._logger.info('Scheduling Service Dispatch Monitor job for CTS...')
        next_run_time = undefined
        if exec_on_start:
            tz = timezone(self._config.DISPATCH_MONITOR_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('Service Outage Monitor job is going to be executed immediately')

        self._scheduler.add_job(self._cts_dispatch_monitoring_process, 'interval',
                                minutes=self._config.DISPATCH_MONITOR_CONFIG['jobs_intervals']['cts_dispatch_monitor'],
                                next_run_time=next_run_time, replace_existing=False,
                                id='_service_dispatch_monitor_cts_process')

    async def _cts_dispatch_monitoring_process(self):
        try:
            start = perf_counter()
            self._logger.info(f"Starting Dispatch Monitor Process...")
            response_cts_dispatches = await self._cts_repository.get_all_dispatches()
            response_cts_dispatches_status = response_cts_dispatches.get('status')
            response_cts_dispatches_body = response_cts_dispatches.get('body')

            if response_cts_dispatches_status not in range(200, 300):
                self._logger.error("Error getting all dispatches from CTS")
                err_msg = f'An error occurred retrieving all dispatches in the request status from CTS.'
                await self._notifications_repository.send_slack_message(err_msg)
                return

            if response_cts_dispatches_body is None \
                    or response_cts_dispatches_body['done'] is not True \
                    or 'records' not in response_cts_dispatches_body \
                    or response_cts_dispatches_body['records'] is None:
                self._logger.error(f"[get_all_dispatches] Could not retrieve all dispatches, "
                                   f"reason: {response_cts_dispatches_body}")
                err_msg = f'An error occurred retrieving all dispatches from CTS.'
                await self._notifications_repository.send_slack_message(err_msg)
                return

            cts_dispatches = response_cts_dispatches_body.get('records', [])
            self._logger.info(f"Length of dispatches: {len(cts_dispatches)}")

            await self._distribute_and_process_dispatches(cts_dispatches)

            stop = perf_counter()
            self._logger.info(f"[CTS] Elapsed time processing all dispatches: {(stop - start) / 60} minutes")
        except Exception as ex:
            err_msg = f"[CTS] Error: {ex}"
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

    def _get_process_dispatch(self, dispatch):
        switcher = {
            self._cts_repository.DISPATCH_CONFIRMED: self._process_confirmed_dispatch,
            self._cts_repository.DISPATCH_FIELD_ENGINEER_ON_SITE: self._process_tech_on_site_dispatch,
            self._cts_repository.DISPATCH_CANCELLED: self._process_canceled_dispatch
        }
        return switcher.get(dispatch.get('Status__c'), None)

    async def _process_generic_dispatch(self, dispatch):
        try:
            dispatch_number = dispatch.get('Name', None)
            ticket_id = dispatch.get('Ext_Ref_Num__c', None)

            self._logger.info(f"Processing generic Dispatch: "
                              f"[{dispatch_number}] for ticket_id: {ticket_id}")

            if ticket_id is None or not BruinRepository.is_valid_ticket_id(ticket_id) or dispatch_number is None:
                self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} discarded.")
                return False

            response = await self._bruin_repository.get_ticket_details(ticket_id)
            response_status = response['status']
            response_body = response['body']
            if response_status not in range(200, 300):
                self._logger.error(f"Error: Dispatch [{dispatch_number}] "
                                   f"Get ticket details for ticket {ticket_id}: "
                                   f"{response_body}")
                err_msg = f"An error occurred retrieve getting ticket details from bruin " \
                          f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id}"
                await self._notifications_repository.send_slack_message(err_msg)
                return False
            ticket_notes = response_body.get('ticketNotes', [])
            ticket_notes = BruinRepository.sort_ticket_notes_by_created_date(ticket_notes)
            all_igz_notes = self._cts_repository.filter_ticket_notes_by_dispatch_number(
                ticket_notes, self.IGZ_DN_WATERMARK)
            filtered_ticket_notes_by_igz_id = self._cts_repository.split_ticket_notes_by_igz_dispatch_num(
                all_igz_notes)

            final_igz_id = self._cts_repository.get_igz_dispatch_number(dispatch)

            if final_igz_id is None:
                self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                  f"discarded matching igz dispatch number")
                return False

            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                              f"matches with IGZ id: {final_igz_id}")

            process_dispatch = self._get_process_dispatch(dispatch)

            if process_dispatch:
                func_args = [dispatch, final_igz_id, filtered_ticket_notes_by_igz_id[final_igz_id]]
                self._scheduler.add_job(process_dispatch, 'date', next_run_time=undefined, replace_existing=False,
                                        id=f"_process_dispatch_{dispatch_number}", args=func_args)
                if self._redis_client.get(dispatch_number) is None:
                    redis_data = {
                        'ticket_id': ticket_id,
                        'igz_dispatch_number': final_igz_id,
                    }
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"Adding to redis cts dispatch. data: {redis_data}")
                    self._redis_client.set(dispatch_number, json.dumps(redis_data),
                                           ex=self._config.DISPATCH_MONITOR_CONFIG['redis_ttl'])
                return True
            else:
                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                  f"with IGZ id: {final_igz_id}"
                                  f"couldn't be processes, current status: {dispatch.get('Status__c')}")
                return False
        except Exception as ex:
            self._logger.error(f"Error: Dispatch [{dispatch_number}] in ticket_id: {ticket_id}. ex: {ex}")
            return False

    async def _distribute_and_process_dispatches(self, all_dispatches):
        for dispatch in all_dispatches:
            await self._process_generic_dispatch(dispatch)

    async def _process_confirmed_dispatch(self, dispatch, igz_dispatch_number, ticket_notes):
        try:
            if not dispatch:
                err_msg = f"Error: Dispatch [{dispatch}] - {igz_dispatch_number} - Not valid dispatch"
                self._logger.error(f"{err_msg}")
                await self._notifications_repository.send_slack_message(err_msg)
                return

            dispatch_number = dispatch.get('Name', None)
            ticket_id = dispatch.get('Ext_Ref_Num__c', None)
            tech_name = dispatch.get('API_Resource_Name__c')
            dispatch_status = dispatch.get('Status__c')

            self._logger.info(f"Processing confirmed dispatch: {dispatch.get('Name')} in ticket_id: {ticket_id} "
                              f"with IGZ id: {igz_dispatch_number} and {len(ticket_notes)} notes")

            if ticket_id is None or not BruinRepository.is_valid_ticket_id(ticket_id) \
                    or dispatch_number is None:
                self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} discarded.")
                return

            if not self._cts_repository.is_dispatch_confirmed(dispatch=dispatch):
                self._logger.info(f"Dispatch not confirmed: {dispatch.get('Name')} in ticket_id: {ticket_id} "
                                  f"with IGZ id: {igz_dispatch_number} and status: {dispatch_status}")
                return

            date_time_of_dispatch = dispatch.get('Local_Site_Time__c')
            if date_time_of_dispatch is None:
                self._logger.error(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                   f"Could not determine date time of dispatch: {dispatch}")
                return

            datetime_tz_response = self._cts_repository.get_dispatch_confirmed_date_time_localized(
                dispatch, dispatch_number, ticket_id)
            date_time_of_dispatch_localized = datetime_tz_response['date_time_of_dispatch_localized']
            datetime_formatted_str = datetime_tz_response['datetime_formatted_str']

            sms_to = CtsRepository.get_sms_to(dispatch)
            if sms_to is None:
                self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                  f"- Error: we could not retrieve 'sms_to' number from: "
                                  f"{dispatch.get('Description__c')}")
                return

            # Tech phonenumber
            sms_to_tech = CtsRepository.get_sms_to_tech(dispatch)
            if sms_to_tech is None:
                self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                  f"- Error: we could not retrieve 'sms_to_tech' number from: "
                                  f"{dispatch.get('Tech_Mobile_Number')}")
                return

            filtered_ticket_notes = BruinRepository.sort_ticket_notes_by_created_date(ticket_notes)
            self._logger.info(f"Checking watermarks for Dispatch [{dispatch_number}] in ticket_id: {ticket_id}")

            requested_watermark_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.DISPATCH_REQUESTED_WATERMARK)
            confirmed_note_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.DISPATCH_CONFIRMED_WATERMARK)
            confirmed_sms_note_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.DISPATCH_CONFIRMED_SMS_WATERMARK)
            confirmed_sms_tech_note_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.DISPATCH_CONFIRMED_SMS_TECH_WATERMARK)
            tech_12_hours_before_note_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.TECH_12_HOURS_BEFORE_SMS_WATERMARK)
            tech_12_hours_before_tech_note_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.TECH_12_HOURS_BEFORE_SMS_TECH_WATERMARK)
            tech_2_hours_before_note_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.TECH_2_HOURS_BEFORE_SMS_WATERMARK)
            tech_2_hours_before_tech_note_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.TECH_2_HOURS_BEFORE_SMS_TECH_WATERMARK)

            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                              f"requested_watermark_found: {requested_watermark_found} "
                              f"confirmed_note_found: {confirmed_note_found} "
                              f"confirmed_sms_tech_note_found: {confirmed_sms_tech_note_found} "
                              f"confirmed_sms_note_found: {confirmed_sms_note_found} "
                              f"tech_12_hours_before_note_found: {tech_12_hours_before_note_found} "
                              f"tech_12_hours_before_tech_note_found: {tech_12_hours_before_tech_note_found} "
                              f"tech_2_hours_before_note_found: {tech_2_hours_before_note_found} "
                              f"tech_2_hours_before_tech_note_found: {tech_2_hours_before_tech_note_found} ")

            # Check if dispatch has a confirmed note
            if confirmed_note_found is None:
                result_append_confirmed_note = await self._cts_repository.append_confirmed_note(
                    dispatch_number, igz_dispatch_number, ticket_id, dispatch)
                if not result_append_confirmed_note:
                    msg = f"[service-dispatch-monitor] [CTS] " \
                          f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id}" \
                          f" Confirmed Note not appended"
                    self._logger.info(msg)
                    await self._notifications_repository.send_slack_message(msg)
                    return
                msg = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                      f"Confirmed Note appended"
                await self._notifications_repository.send_slack_message(msg)

                self._logger.info(f"Dispatch: {dispatch_number} "
                                  f"Ticket_id: {ticket_id} - Sending confirmed SMS")
            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                              f"- already has a confirmed note")

            # Check if dispatch has a sms confirmed note
            if confirmed_sms_note_found is None:
                self._logger.info(f"Dispatch: {dispatch_number} "
                                  f"Ticket_id: {ticket_id} - Sending confirmed SMS")
                sms_sended = await self._cts_repository.send_confirmed_sms(
                    dispatch_number, ticket_id, datetime_formatted_str, sms_to, tech_name)
                if not sms_sended:
                    msg = f"[service-dispatch-monitor] [CTS] " \
                          f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                          f"SMS could not be sent to {sms_to}."
                else:
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- Confirm SMS note not found")

                    result_append_confirmed_sms_note = await self._cts_repository.append_confirmed_sms_note(
                        dispatch_number, igz_dispatch_number, ticket_id, sms_to)

                    if not result_append_confirmed_sms_note:
                        msg = f"[service-dispatch-monitor] [CTS] " \
                              f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id}" \
                              f" Confirmed SMS Note not appended"
                    else:
                        msg = f"[service-dispatch-monitor] [CTS] " \
                              f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                              f"Confirmed Note, SMS send and Confirmed SMS note sent OK."
                self._logger.info(msg)
                await self._notifications_repository.send_slack_message(msg)

            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                              f"- already has a sms confirmed note")

            if confirmed_sms_tech_note_found is None:
                self._logger.info(f"Dispatch: {dispatch_number} "
                                  f"Ticket_id: {ticket_id} - Sending confirmed SMS Tech")
                sms_sended = await self._cts_repository.send_confirmed_sms_tech(
                    dispatch_number, ticket_id, dispatch, datetime_formatted_str, sms_to_tech)
                if not sms_sended:
                    msg = f"[service-dispatch-monitor] [CTS] " \
                          f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                          f"SMS Tech could not be sent to {sms_to_tech}."
                    self._logger.info(msg)
                    await self._notifications_repository.send_slack_message(msg)
                    return

                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                  f"- Confirm SMS tech note not found")

                result_append_confirmed_sms_note = await self._cts_repository.append_confirmed_sms_tech_note(
                    dispatch_number, igz_dispatch_number, ticket_id, sms_to_tech)

                if not result_append_confirmed_sms_note:
                    msg = f"[service-dispatch-monitor] [CTS] " \
                          f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                          f"Confirmed SMS tech note not appended"
                    self._logger.info(msg)
                    await self._notifications_repository.send_slack_message(msg)
                    return
                msg = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                      f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK."
                self._logger.info(msg)
                await self._notifications_repository.send_slack_message(msg)
                return
            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                              f"- already has a sms tech confirmed note")

            # Check for Tech updates
            # First retrieve original tech name from confirmed note
            updated_tech_notes = [confirmed_note_found]
            latest_tech_name_assigned = self._cts_repository.get_latest_tech_name_assigned_from_notes(
                updated_tech_notes, filtered_ticket_notes, self.DISPATCH_UPDATED_TECH_WATERMARK)
            self._logger.info(f"[service-dispatch-monitor] [CTS] "
                              f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} - "
                              f"Tech Name Actual: {tech_name} latest: {latest_tech_name_assigned}")
            if latest_tech_name_assigned is not None and latest_tech_name_assigned != tech_name:
                # Latest tech in notes is different than the actual tech
                self._logger.info(f"[service-dispatch-monitor] [CTS] "
                                  f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} - "
                                  f"The tech has changed. "
                                  f"Actual: {tech_name} latest: {latest_tech_name_assigned}")
                # Append update tech note
                result_append_updated_tech_note = await self._cts_repository.append_updated_tech_note(
                    igz_dispatch_number, ticket_id, dispatch)
                msg = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                      f"- A updated tech note appended"
                if not result_append_updated_tech_note:
                    msg = f"[service-dispatch-monitor] [CTS] " \
                          f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                          f"- An updated tech note not appended"
                self._logger.info(msg)
                await self._notifications_repository.send_slack_message(msg)

                # Send sms client
                result_sms_update_tech_sended = await self._cts_repository.send_updated_tech_sms(
                    dispatch_number, ticket_id, dispatch, datetime_formatted_str, sms_to, tech_name
                )
                msg = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                      f"- A updated tech sms sent"
                if not result_sms_update_tech_sended:
                    msg = f"[service-dispatch-monitor] [CTS] " \
                          f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                          f"- An updated tech sms not sent"
                self._logger.info(msg)
                await self._notifications_repository.send_slack_message(msg)

                # Send sms tech
                result_sms_tech_update_tech_sended = await self._cts_repository.send_updated_tech_sms_tech(
                    dispatch_number, ticket_id, dispatch, datetime_formatted_str, sms_to_tech
                )
                msg = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                      f"- A updated tech sms tech sent"
                if not result_sms_tech_update_tech_sended:
                    msg = f"[service-dispatch-monitor] [CTS] " \
                          f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                          f"- An updated tech sms tech not sent"
                self._logger.info(msg)
                await self._notifications_repository.send_slack_message(msg)

            # Check if dispatch has a sms 12 hours note
            should_send_12_hours_info = None
            if tech_12_hours_before_note_found is None:
                just_now = datetime.now(pytz.utc)
                hours_diff = UtilsRepository.get_diff_hours_between_datetimes(just_now,
                                                                              date_time_of_dispatch_localized)
                should_send_12_hours_info = UtilsRepository.in_range(hours_diff, self.HOURS_12 - 1, self.HOURS_12)
                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} UTC - "
                                  f"dt: {date_time_of_dispatch_localized} - now: {just_now} - "
                                  f"diff: {hours_diff}")
                if not should_send_12_hours_info:
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"SMS 12h note not needed to send now")
                else:
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"Sending SMS 12h note")
                    result_sms_12_sended = await self._cts_repository.send_tech_12_sms(
                        dispatch_number, ticket_id, datetime_formatted_str, sms_to)
                    if not result_sms_12_sended:
                        msg = f"[service-dispatch-monitor] [CTS] " \
                              f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                              f"- SMS 12h not sended"
                    else:
                        result_append_tech_12_sms_note = await self._cts_repository.append_tech_12_sms_note(
                            dispatch_number, igz_dispatch_number, ticket_id, sms_to)
                        if not result_append_tech_12_sms_note:
                            msg = f"[service-dispatch-monitor] [CTS] " \
                                  f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                                  f"- A sms tech 12 hours before note not appended"
                        else:
                            msg = f"[service-dispatch-monitor] [CTS] " \
                                  f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                                  f"- A sms tech 12 hours before note appended"
                    self._logger.info(msg)
                    await self._notifications_repository.send_slack_message(msg)
            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                              f"- should_send_12_hours_info: {should_send_12_hours_info}"
                              f"- Already has a sms tech 12 hours before note")

            should_send_12_hours_info = None
            if tech_12_hours_before_tech_note_found is None:
                just_now = datetime.now(pytz.utc)
                hours_diff = UtilsRepository.get_diff_hours_between_datetimes(just_now,
                                                                              date_time_of_dispatch_localized)
                should_send_12_hours_info = UtilsRepository.in_range(hours_diff, self.HOURS_12 - 1, self.HOURS_12)
                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} UTC - "
                                  f"dt: {date_time_of_dispatch_localized} - now: {just_now} - "
                                  f"diff: {hours_diff}")
                if not should_send_12_hours_info:
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"Not needed to send SMS tech 12h note due to time")
                else:
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"Sending SMS tech 12h note")
                    result_sms_12_sended = await self._cts_repository.send_tech_12_sms_tech(
                        dispatch_number, ticket_id, dispatch, datetime_formatted_str, sms_to_tech)
                    if not result_sms_12_sended:
                        msg = f"[service-dispatch-monitor] [CTS] " \
                              f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                              f"- SMS tech 12h not sended"
                        self._logger.info(msg)
                        await self._notifications_repository.send_slack_message(msg)
                        return

                    result_append_tech_12_sms_note = await self._cts_repository.append_tech_12_sms_tech_note(
                        dispatch_number, igz_dispatch_number, ticket_id, sms_to_tech)
                    if not result_append_tech_12_sms_note:
                        msg = f"[service-dispatch-monitor] [CTS] " \
                              f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                              f"- A sms tech 12 hours before tech note not appended"
                        self._logger.info(msg)
                        await self._notifications_repository.send_slack_message(msg)
                        return
                    msg = f"[service-dispatch-monitor] [CTS] " \
                          f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                          f"- A sms tech 12 hours before tech note appended"
                    self._logger.info(msg)
                    await self._notifications_repository.send_slack_message(msg)
                    return
            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                              f"- should_send_12_hours_info: {should_send_12_hours_info}"
                              f"- Already has a sms tech 12 hours before tech note")

            # Check if dispatch has a sms 2 hours note
            should_send_2_hours_info = None
            if tech_2_hours_before_note_found is None:
                just_now = datetime.now(pytz.utc)
                hours_diff = UtilsRepository.get_diff_hours_between_datetimes(just_now,
                                                                              date_time_of_dispatch_localized)
                should_send_2_hours_info = UtilsRepository.in_range(hours_diff, self.HOURS_2 - 1, self.HOURS_2)
                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} UTC - "
                                  f"dt: {date_time_of_dispatch_localized} - now: {just_now} - "
                                  f"diff: {hours_diff}")
                if not should_send_2_hours_info:
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"SMS 2h note not needed to send now")
                else:
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"Sending SMS 2h note")
                    result_sms_2_sended = await self._cts_repository.send_tech_2_sms(
                        dispatch_number, ticket_id, datetime_formatted_str, sms_to)
                    if not result_sms_2_sended:
                        msg = f"[service-dispatch-monitor] [CTS] " \
                              f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                              f"- SMS 2h not sent"
                    else:
                        result_append_tech_2_sms_note = await self._cts_repository.append_tech_2_sms_note(
                            dispatch_number, igz_dispatch_number, ticket_id, sms_to)
                        if not result_append_tech_2_sms_note:
                            msg = f"[service-dispatch-monitor] [CTS] " \
                                  f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                                  f"- A sms tech 2 hours before note not appended"
                        else:
                            msg = f"[service-dispatch-monitor] [CTS] " \
                                  f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                                  f"- A sms tech 2 hours before note appended"
                    self._logger.info(msg)
                    await self._notifications_repository.send_slack_message(msg)
            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                              f"- should_send_2_hours_info: {should_send_2_hours_info}"
                              f"- already has a sms tech 2 hours before note")

            should_send_2_hours_info = None
            if tech_2_hours_before_tech_note_found is None:
                just_now = datetime.now(pytz.utc)
                hours_diff = UtilsRepository.get_diff_hours_between_datetimes(just_now,
                                                                              date_time_of_dispatch_localized)
                should_send_2_hours_info = UtilsRepository.in_range(hours_diff, self.HOURS_2 - 1, self.HOURS_2)
                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} UTC - "
                                  f"dt: {date_time_of_dispatch_localized} - now: {just_now} - "
                                  f"diff: {hours_diff}")
                if not should_send_2_hours_info:
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"SMS tech 2h note not needed to send now")
                else:
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"Sending SMS tech 2h note")
                    result_sms_2_sended = await self._cts_repository.send_tech_2_sms_tech(
                        dispatch_number, ticket_id, dispatch, datetime_formatted_str, sms_to_tech)
                    if not result_sms_2_sended:
                        msg = f"[service-dispatch-monitor] [CTS] " \
                              f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                              f"- SMS tech 2h not sended"
                        self._logger.info(msg)
                        await self._notifications_repository.send_slack_message(msg)
                        return

                    result_append_tech_2_sms_note = await self._cts_repository.append_tech_2_sms_tech_note(
                        dispatch_number, igz_dispatch_number, ticket_id, sms_to_tech)
                    if not result_append_tech_2_sms_note:
                        msg = f"[service-dispatch-monitor] [CTS] " \
                              f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                              f"- A sms tech 2 hours before tech note not appended"
                        self._logger.info(msg)
                        await self._notifications_repository.send_slack_message(msg)
                        return
                    msg = f"[service-dispatch-monitor] [CTS] " \
                          f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                          f"- A sms tech 2 hours before tech note appended"
                    self._logger.info(msg)
                    await self._notifications_repository.send_slack_message(msg)

            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                              f"- should_send_2_hours_info: {should_send_2_hours_info}"
                              f"- already has a sms tech 2 hours before tech note")

            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                              f"- This ticket should never be again in Dispatch Confirmed, "
                              f"at some point it has to change to tech on site")

        except Exception as ex:
            err_msg = f"Error: Dispatch [{dispatch_number}] in ticket_id: {ticket_id} - {dispatch}"
            self._logger.error(f"{err_msg} - {ex}")
            await self._notifications_repository.send_slack_message(err_msg)
        finally:
            self._logger.info(f"Processed confirmed dispatch: {dispatch} "
                              f"with IGZ id: {igz_dispatch_number}")

    async def _process_tech_on_site_dispatch(self, dispatch, igz_dispatch_number, ticket_notes):
        try:
            if not dispatch:
                err_msg = f"Error: Dispatch [{dispatch}] - {igz_dispatch_number} - Not valid dispatch"
                self._logger.error(f"{err_msg}")
                await self._notifications_repository.send_slack_message(err_msg)
                return

            dispatch_number = dispatch.get('Name', None)
            ticket_id = dispatch.get('Ext_Ref_Num__c', None)
            dispatch_status = dispatch.get('Status__c')

            self._logger.info(f"Processing tech on site dispatch: {dispatch.get('Name')} in ticket_id: {ticket_id} "
                              f"with IGZ id: {igz_dispatch_number} and {len(ticket_notes)} notes")
            if ticket_id is None or not BruinRepository.is_valid_ticket_id(ticket_id) \
                    or dispatch_number is None:
                self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} discarded.")
                return
            if not self._cts_repository.is_tech_on_site(dispatch=dispatch):
                self._logger.info(f"Dispatch not tech on site: {dispatch.get('Name')} in ticket_id: {ticket_id} "
                                  f"with IGZ id: {igz_dispatch_number} and status: {dispatch_status}")
                return

            date_time_of_dispatch = dispatch.get('Local_Site_Time__c')
            if date_time_of_dispatch is None:
                self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                  f"Could not determine date time of dispatch: {dispatch}")
                return

            sms_to = CtsRepository.get_sms_to(dispatch)
            if sms_to is None:
                self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                  f"- Error: we could not retrieve 'sms_to' number from: "
                                  f"{dispatch.get('Description__c')}")
                return

            self._logger.info(f"Getting details for ticket [{ticket_id}]")
            filtered_ticket_notes = BruinRepository.sort_ticket_notes_by_created_date(ticket_notes)
            self._logger.info(ticket_notes)
            self._logger.info(f"Checking watermarks for Dispatch [{dispatch_number}] in ticket_id: {ticket_id}")

            requested_watermark_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.DISPATCH_REQUESTED_WATERMARK)
            confirmed_note_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.DISPATCH_CONFIRMED_WATERMARK)
            confirmed_sms_note_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.DISPATCH_CONFIRMED_SMS_WATERMARK)
            tech_12_hours_before_note_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.TECH_12_HOURS_BEFORE_SMS_WATERMARK)
            tech_2_hours_before_note_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.TECH_2_HOURS_BEFORE_SMS_WATERMARK)
            tech_on_site_note_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.DISPATCH_FIELD_ENGINEER_ON_SITE_WATERMARK)
            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                              f"requested_watermark_found: {requested_watermark_found} "
                              f"confirmed_note_found: {confirmed_note_found} "
                              f"confirmed_sms_note_found: {confirmed_sms_note_found} "
                              f"tech_12_hours_before_note_found: {tech_12_hours_before_note_found} "
                              f"tech_2_hours_before_note_found: {tech_2_hours_before_note_found} "
                              f"tech_on_site_note_found: {tech_on_site_note_found}")

            if tech_on_site_note_found is None:
                result_sms_tech_on_site_sended = await self._cts_repository.send_tech_on_site_sms(
                    dispatch_number, ticket_id, dispatch, sms_to)
                if not result_sms_tech_on_site_sended:
                    msg = f"[service-dispatch-monitor] [CTS] " \
                          f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                          f"- SMS tech on site not sended"
                    self._logger.info(msg)
                    await self._notifications_repository.send_slack_message(msg)
                    return

                result_append_tech_on_site_sms_note = await self._cts_repository.append_tech_on_site_sms_note(
                    dispatch_number, igz_dispatch_number, ticket_id, sms_to,
                    dispatch.get('API_Resource_Name__c'))
                if not result_append_tech_on_site_sms_note:
                    msg = f"[service-dispatch-monitor] [CTS] " \
                          f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                          f"- A sms tech on site note not appended"
                    self._logger.info(msg)
                    await self._notifications_repository.send_slack_message(msg)
                    return
                msg = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                      f"- A sms tech on site note appended"
                self._logger.info(msg)
                await self._notifications_repository.send_slack_message(msg)
            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                              f"- already has a sms tech tech on site note")
        except Exception as ex:
            err_msg = f"Error: Dispatch [{dispatch}] in igz_id: {igz_dispatch_number}"
            self._logger.error(f"{err_msg} - {ex}")
            await self._notifications_repository.send_slack_message(err_msg)
        finally:
            self._logger.info(f"Processed tech on site  dispatch: {dispatch} "
                              f"with IGZ id: {igz_dispatch_number}")

    async def _process_canceled_dispatch(self, dispatch, igz_dispatch_number, ticket_notes):
        try:
            if not dispatch or len(ticket_notes) == 0:
                err_msg = f"Error: Dispatch [{dispatch}] - {igz_dispatch_number} - Not valid dispatch"
                self._logger.error(f"{err_msg}")
                await self._notifications_repository.send_slack_message(err_msg)
                return
            dispatch_number = dispatch.get('Name', None)
            ticket_id = dispatch.get('Ext_Ref_Num__c', None)
            dispatch_status = dispatch.get('Status__c')

            self._logger.info(f"Processing canceled dispatch: {dispatch_number} in ticket_id: {ticket_id} "
                              f"with IGZ id: {igz_dispatch_number}")

            if ticket_id is None or not BruinRepository.is_valid_ticket_id(ticket_id) \
                    or dispatch_number is None:
                self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} discarded.")
                return

            if not self._cts_repository.is_dispatch_cancelled(dispatch=dispatch):
                self._logger.info(f"Dispatch is not canceled: {dispatch.get('Name')} in ticket_id: {ticket_id} "
                                  f"with IGZ id: {igz_dispatch_number} and status: {dispatch_status}")
                return

            date_time_of_dispatch = dispatch.get('Local_Site_Time__c')
            if date_time_of_dispatch is None:
                self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                  f"Could not determine date time of dispatch: {dispatch}")
                return

            datetime_tz_response = self._cts_repository.get_dispatch_confirmed_date_time_localized(
                dispatch, dispatch_number, ticket_id)
            datetime_formatted_str = datetime_tz_response['datetime_formatted_str']

            self._logger.info(f"Getting details for ticket [{ticket_id}]")
            filtered_ticket_notes = BruinRepository.sort_ticket_notes_by_created_date(ticket_notes)
            self._logger.info(ticket_notes)
            self._logger.info(
                f"Checking watermarks for Dispatch [{dispatch_number}] in ticket_id: {ticket_id}")

            requested_watermark_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.DISPATCH_REQUESTED_WATERMARK)
            cancelled_watermark_note_found = UtilsRepository.find_note(
                filtered_ticket_notes, self.DISPATCH_CANCELLED_WATERMARK)
            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                              f"requested_watermark_found: {requested_watermark_found} "
                              f"cancelled_watermark_note_found: {cancelled_watermark_note_found}")

            if cancelled_watermark_note_found is None:
                result_append_cancelled_note = await self._cts_repository.append_dispatch_cancelled_note(
                    dispatch_number, igz_dispatch_number, ticket_id, datetime_formatted_str)
                if not result_append_cancelled_note:
                    msg = f"[service-dispatch-monitor] [CTS] " \
                          f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                          f"- A cancelled dispatch note not appended"
                    self._logger.info(msg)
                    await self._notifications_repository.send_slack_message(msg)
                    return
                msg = f"[service-dispatch-monitor] [CTS] " \
                      f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                      f"- A cancelled dispatch note appended"
                self._logger.info(msg)
                await self._notifications_repository.send_slack_message(msg)

            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                              f"- already has a cancelled dispatch note")
        except Exception as ex:
            err_msg = f"Error: Dispatch [{dispatch}] in igz_id: {igz_dispatch_number}"
            self._logger.error(f"{err_msg} - {ex}")
            await self._notifications_repository.send_slack_message(err_msg)
        finally:
            self._logger.info(f"Processed canceled dispatch: {dispatch} "
                              f"with IGZ id: {igz_dispatch_number}")
