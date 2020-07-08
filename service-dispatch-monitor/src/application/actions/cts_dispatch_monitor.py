import asyncio
from datetime import datetime
from time import perf_counter
import iso8601
import pytz
from shortuuid import uuid


from apscheduler.util import undefined
from pytz import timezone

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

        self.HOURS_12 = 12
        self.HOURS_2 = 2

        # Dispatch Notes watermarks
        self.MAIN_WATERMARK = '#*Automation Engine*#'
        self.DISPATCH_REQUESTED_WATERMARK = 'Dispatch Management - Dispatch Requested'
        self.DISPATCH_CONFIRMED_WATERMARK = 'Dispatch Management - Dispatch Confirmed'
        self.DISPATCH_FIELD_ENGINEER_ON_SITE_WATERMARK = 'Dispatch Management - Field Engineer On Site'
        self.DISPATCH_REPAIR_COMPLETED_WATERMARK = 'Dispatch Management - Repair Completed'

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
                raise

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
            dispatches_splitted_by_status = self._cts_repository.get_dispatches_splitted_by_status(cts_dispatches)

            self._logger.info(f"Splitted by status: {list(dispatches_splitted_by_status.keys())}")

            monitor_tasks = [
                self._monitor_confirmed_dispatches(
                    dispatches_splitted_by_status[self._cts_repository.DISPATCH_CONFIRMED]),
                self._monitor_tech_on_site_dispatches(
                    dispatches_splitted_by_status[self._cts_repository.DISPATCH_FIELD_ENGINEER_ON_SITE])
            ]

            start_monitor_tasks = perf_counter()
            await asyncio.gather(*monitor_tasks, return_exceptions=True)
            stop_monitor_tasks = perf_counter()
            self._logger.info(f"[CTS] All monitor tasks finished: "
                              f"{(stop_monitor_tasks - start_monitor_tasks) / 60} minutes")

            stop = perf_counter()
            self._logger.info(f"[CTS] Elapsed time processing all dispatches: {(stop - start) / 60} minutes")
        except Exception as ex:
            self._logger.error(f"[CTS] Error: {ex}")

    async def _monitor_confirmed_dispatches(self, confirmed_dispatches):
        try:
            start = perf_counter()
            self._logger.info(f"Dispatches to process before filter {len(confirmed_dispatches)}")
            confirmed_dispatches = list(filter(self._cts_repository.is_dispatch_confirmed, confirmed_dispatches))
            self._logger.info(f"Total confirmed dispatches after filter: {len(confirmed_dispatches)}")

            for dispatch in confirmed_dispatches:
                try:
                    dispatch_number = dispatch.get('Name', None)
                    ticket_id = dispatch.get('Ext_Ref_Num__c', None)

                    self._logger.info(f"Processing Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - {dispatch}")

                    if ticket_id is None or not CtsRepository.is_valid_ticket_id(ticket_id) or dispatch_number is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} discarded.")
                        continue

                    date_time_of_dispatch = dispatch.get('Local_Site_Time__c')
                    if date_time_of_dispatch is None:
                        self._logger.error(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                           f"Could not determine date time of dispatch: {dispatch}")
                        err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                  f"An error occurred retrieve datetime of dispatch: " \
                                  f"{dispatch.get('Local_Site_Time__c')}"
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue

                    date_time_of_dispatch_localized = iso8601.parse_date(date_time_of_dispatch, pytz.utc)

                    sms_to = CtsRepository.get_sms_to(dispatch)
                    if sms_to is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                          f"- Error: we could not retrieve 'sms_to' number from: "
                                          f"{dispatch.get('Description__c')}")
                        err_msg = f"An error occurred retrieve 'sms_to' number " \
                                  f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                  f"from: {dispatch.get('Description__c')}"
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue

                    # Tech phonenumber
                    sms_to_tech = CtsRepository.get_sms_to_tech(dispatch)
                    if sms_to_tech is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                          f"- Error: we could not retrieve 'sms_to_tech' number from: "
                                          f"{dispatch.get('Tech_Mobile_Number')}")
                        err_msg = f"An error occurred retrieve 'sms_to_tech' number " \
                                  f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                  f"from: {dispatch.get('Resource_Phone_Number__c')}"
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue

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
                        continue
                    ticket_notes = response_body.get('ticketNotes', [])
                    ticket_notes = [tn for tn in ticket_notes if tn.get('noteValue')]

                    igz_dispatch_number_note = UtilsRepository.find_note(ticket_notes, self.MAIN_WATERMARK)
                    igz_dispatch_number = ''
                    if igz_dispatch_number_note and igz_dispatch_number_note.get('noteValue'):
                        lines = igz_dispatch_number_note.get('noteValue').splitlines()
                        for line in lines:
                            if self.MAIN_WATERMARK in line:
                                igz_dispatch_number = line.replace(
                                    f"{self.MAIN_WATERMARK} ", "").strip().replace(" ", "")
                                if len(igz_dispatch_number) >= 3:
                                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                      f"IGZ dispatch number found: {igz_dispatch_number}")
                                    break
                    if len(igz_dispatch_number) == 0:
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"IGZ dispatch number not found: {igz_dispatch_number}")
                        continue

                    watermark_found = UtilsRepository.find_note(ticket_notes, self.MAIN_WATERMARK)
                    requested_watermark_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_REQUESTED_WATERMARK)
                    confirmed_note_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_CONFIRMED_WATERMARK)
                    confirmed_sms_note_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_CONFIRMED_SMS_WATERMARK)
                    confirmed_sms_tech_note_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_CONFIRMED_SMS_TECH_WATERMARK)
                    tech_12_hours_before_note_found = UtilsRepository.find_note(
                        ticket_notes, self.TECH_12_HOURS_BEFORE_SMS_WATERMARK)
                    tech_12_hours_before_tech_note_found = UtilsRepository.find_note(
                        ticket_notes, self.TECH_12_HOURS_BEFORE_SMS_TECH_WATERMARK)
                    tech_2_hours_before_note_found = UtilsRepository.find_note(
                        ticket_notes, self.TECH_2_HOURS_BEFORE_SMS_WATERMARK)
                    tech_2_hours_before_tech_note_found = UtilsRepository.find_note(
                        ticket_notes, self.TECH_2_HOURS_BEFORE_SMS_TECH_WATERMARK)

                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"requested_watermark_found: {requested_watermark_found} "
                                      f"confirmed_note_found: {confirmed_note_found} "
                                      f"confirmed_sms_tech_note_found: {confirmed_sms_tech_note_found} "
                                      f"confirmed_sms_note_found: {confirmed_sms_note_found} "
                                      f"tech_12_hours_before_note_found: {tech_12_hours_before_note_found} "
                                      f"tech_12_hours_before_tech_note_found: {tech_12_hours_before_tech_note_found} "
                                      f"tech_2_hours_before_note_found: {tech_2_hours_before_note_found} "
                                      f"tech_2_hours_before_tech_note_found: {tech_2_hours_before_tech_note_found} ")

                    if watermark_found is None:
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- Watermark not found, ticket does not created through dispatch portal")
                        continue
                    if requested_watermark_found is None:
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- Watermark not found, ticket does not belong to us")
                        continue

                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"main_watermark_found: {watermark_found} "
                                      f"requested_watermark_found: {requested_watermark_found} ")
                    # Check if dispatch has a confirmed note
                    if confirmed_note_found is None:
                        result_append_confirmed_note = await self._cts_repository.append_confirmed_note(
                            dispatch_number, igz_dispatch_number, ticket_id, dispatch)
                        if not result_append_confirmed_note:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"Confirmed Note not appended")
                            continue

                        self._logger.info(f"Dispatch: {dispatch_number} "
                                          f"Ticket_id: {ticket_id} - Sending confirmed SMS")
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a confirmed note")

                    # Check if dispatch has a sms confirmed note
                    if confirmed_sms_note_found is None:
                        self._logger.info(f"Dispatch: {dispatch_number} "
                                          f"Ticket_id: {ticket_id} - Sending confirmed SMS")
                        sms_sended = await self._cts_repository.send_confirmed_sms(
                            dispatch_number, ticket_id, dispatch, sms_to)
                        if not sms_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS could not be sent to {sms_to}.")
                            # continue
                        else:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- Confirm SMS note not found")

                            result_append_confirmed_sms_note = await self._cts_repository.append_confirmed_sms_note(
                                dispatch_number, igz_dispatch_number, ticket_id, sms_to)

                            if not result_append_confirmed_sms_note:
                                self._logger.info("Confirmed SMS note not appended")
                                # continue
                            else:
                                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                  f"Confirmed Note, SMS send and Confirmed SMS note sent OK.")
                            # continue
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a sms confirmed note")

                    if confirmed_sms_tech_note_found is None:
                        self._logger.info(f"Dispatch: {dispatch_number} "
                                          f"Ticket_id: {ticket_id} - Sending confirmed SMS Tech")
                        sms_sended = await self._cts_repository.send_confirmed_sms_tech(
                            dispatch_number, ticket_id, dispatch, sms_to_tech)
                        if not sms_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS Tech could not be sent to {sms_to_tech}.")
                            continue

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- Confirm SMS tech note not found")

                        result_append_confirmed_sms_note = await self._cts_repository.append_confirmed_sms_tech_note(
                            dispatch_number, igz_dispatch_number, ticket_id, sms_to_tech)

                        if not result_append_confirmed_sms_note:
                            self._logger.info("Confirmed SMS tech note not appended")
                            continue

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK.")
                        continue
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a sms tech confirmed note")

                    # Check if dispatch has a sms 12 hours note
                    if tech_12_hours_before_note_found is None:
                        just_now = datetime.now(pytz.utc)
                        hours_diff = UtilsRepository.get_diff_hours_between_datetimes(date_time_of_dispatch_localized,
                                                                                      just_now)
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} UTC - "
                                          f"dt: {date_time_of_dispatch_localized} - now: {just_now} - "
                                          f"diff: {hours_diff}")
                        if hours_diff > self.HOURS_12:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS 12h note not needed to send now")
                            # continue
                        else:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"Sending SMS 12h note")
                            result_sms_12_sended = await self._cts_repository.send_tech_12_sms(
                                dispatch_number, ticket_id, dispatch, sms_to)
                            if not result_sms_12_sended:
                                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                  f"- SMS 12h not sended")
                                # continue
                            else:
                                result_append_tech_12_sms_note = await self._cts_repository.append_tech_12_sms_note(
                                    dispatch_number, igz_dispatch_number, ticket_id, sms_to)
                                if not result_append_tech_12_sms_note:
                                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                      f"- A sms tech 12 hours before note not appended")
                                    # continue
                                else:
                                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                      f"- A sms tech 12 hours before note appended")
                            # continue
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- Already has a sms tech 12 hours before note")

                    if tech_12_hours_before_tech_note_found is None:
                        just_now = datetime.now(pytz.utc)
                        hours_diff = UtilsRepository.get_diff_hours_between_datetimes(date_time_of_dispatch_localized,
                                                                                      just_now)
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} UTC - "
                                          f"dt: {date_time_of_dispatch_localized} - now: {just_now} - "
                                          f"diff: {hours_diff}")
                        if hours_diff > self.HOURS_12:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS tech 12h note not needed to send now")
                            continue

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"Sending SMS tech 12h note")
                        result_sms_12_sended = await self._cts_repository.send_tech_12_sms_tech(
                            dispatch_number, ticket_id, dispatch, sms_to_tech)
                        if not result_sms_12_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- SMS tech 12h not sended")
                            continue

                        result_append_tech_12_sms_note = await self._cts_repository.append_tech_12_sms_tech_note(
                            dispatch_number, igz_dispatch_number, ticket_id, sms_to_tech)
                        if not result_append_tech_12_sms_note:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- A sms tech 12 hours before tech note not appended")
                            continue
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- A sms tech 12 hours before tech note appended")
                        continue
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- Already has a sms tech 12 hours before tech note")

                    # Check if dispatch has a sms 2 hours note
                    if tech_2_hours_before_note_found is None:
                        just_now = datetime.now(pytz.utc)
                        hours_diff = UtilsRepository.get_diff_hours_between_datetimes(date_time_of_dispatch_localized,
                                                                                      just_now)
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} UTC - "
                                          f"dt: {date_time_of_dispatch_localized} - now: {just_now} - "
                                          f"diff: {hours_diff}")
                        if hours_diff > self.HOURS_2:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS 2h note not needed to send now")
                            # continue
                        else:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"Sending SMS 2h note")
                            result_sms_2_sended = await self._cts_repository.send_tech_2_sms(
                                dispatch_number, ticket_id, dispatch, sms_to)
                            if not result_sms_2_sended:
                                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                  f"- SMS 2h not sended")
                                # continue
                            else:
                                result_append_tech_2_sms_note = await self._cts_repository.append_tech_2_sms_note(
                                    dispatch_number, igz_dispatch_number, ticket_id, sms_to)
                                if not result_append_tech_2_sms_note:
                                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                      f"- A sms tech 2 hours before note not appended")
                                    # continue
                                else:
                                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                      f"- A sms tech 2 hours before note appended")
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a sms tech 2 hours before note")

                    if tech_2_hours_before_tech_note_found is None:
                        just_now = datetime.now(pytz.utc)
                        hours_diff = UtilsRepository.get_diff_hours_between_datetimes(date_time_of_dispatch_localized,
                                                                                      just_now)
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} UTC - "
                                          f"dt: {date_time_of_dispatch_localized} - now: {just_now} - "
                                          f"diff: {hours_diff}")
                        if hours_diff > self.HOURS_2:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS tech 2h note not needed to send now")
                            continue

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"Sending SMS tech 2h note")
                        result_sms_2_sended = await self._cts_repository.send_tech_2_sms_tech(
                            dispatch_number, ticket_id, dispatch, sms_to_tech)
                        if not result_sms_2_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- SMS tech 2h not sended")
                            continue

                        result_append_tech_2_sms_note = await self._cts_repository.append_tech_2_sms_tech_note(
                            dispatch_number, igz_dispatch_number, ticket_id, sms_to_tech)
                        if not result_append_tech_2_sms_note:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- A sms tech 2 hours before tech note not appended")
                            continue
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- A sms tech 2 hours before tech note appended")
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a sms tech 2 hours before tech note")

                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- This ticket should never be again in Dispatch Confirmed, "
                                      f"at some point it has to change to tech on site")

                except Exception as ex:
                    err_msg = f"Error: Dispatch [{dispatch_number}] in ticket_id: {ticket_id} - {dispatch}"
                    self._logger.error(f"Error: {ex}")
                    await self._notifications_repository.send_slack_message(err_msg)
                    continue
        except Exception as ex:
            err_msg = f"Error: _monitor_confirmed_dispatches - {ex}"
            self._logger.error(f"Error: {ex}")
            await self._notifications_repository.send_slack_message(err_msg)
        stop = perf_counter()
        self._logger.info(f"Monitor Confirmed Dispatches took: {(stop - start) / 60} minutes")

    async def _monitor_tech_on_site_dispatches(self, tech_on_site_dispatches):
        try:
            start = perf_counter()
            self._logger.info(f"Dispatches to process before filter {len(tech_on_site_dispatches)}")
            tech_on_site_dispatches = list(filter(self._cts_repository.is_tech_on_site, tech_on_site_dispatches))
            self._logger.info(f"Dispatches to process after filter {len(tech_on_site_dispatches)}")

            for dispatch in tech_on_site_dispatches:
                try:
                    dispatch_number = dispatch.get('Name', None)
                    ticket_id = dispatch.get('Ext_Ref_Num__c', None)

                    self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id}")
                    if ticket_id is None or not CtsRepository.is_valid_ticket_id(ticket_id) \
                            or dispatch_number is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} discarded.")
                        continue

                    date_time_of_dispatch = dispatch.get('Local_Site_Time__c')

                    if date_time_of_dispatch is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                          f"Could not determine date time of dispatch: {dispatch}")
                        err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                  f"An error occurred retrieve datetime of dispatch: " \
                                  f"{dispatch.get('Local_Site_Time__c', None)}"
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue

                    sms_to = CtsRepository.get_sms_to(dispatch)

                    if sms_to is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                          f"- Error: we could not retrieve 'sms_to' number from: "
                                          f"{dispatch.get('Description__c')}")
                        err_msg = f"An error occurred retrieve 'sms_to' number " \
                                  f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                  f"from: {dispatch.get('Description__c')}"
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue

                    self._logger.info(f"Getting details for ticket [{ticket_id}]")

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
                        continue
                    ticket_notes = response_body.get('ticketNotes', [])
                    ticket_notes = [tn for tn in ticket_notes if tn.get('noteValue')]
                    igz_dispatch_number_note = UtilsRepository.find_note(ticket_notes, self.MAIN_WATERMARK)
                    igz_dispatch_number = ''
                    if igz_dispatch_number_note and igz_dispatch_number_note.get('noteValue'):
                        lines = igz_dispatch_number_note.get('noteValue').splitlines()
                        for line in lines:
                            if self.MAIN_WATERMARK in line:
                                igz_dispatch_number = line.replace(
                                    f"{self.MAIN_WATERMARK} ", "").strip().replace(" ", "")
                                if len(igz_dispatch_number) >= 3:
                                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                      f"IGZ dispatch number found: {igz_dispatch_number}")
                                    break
                                igz_dispatch_number = ''
                    if len(igz_dispatch_number) == 0:
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"IGZ dispatch number not found: {igz_dispatch_number}")
                        continue
                    self._logger.info(
                        f"Checking watermarks for Dispatch [{dispatch_number}] in ticket_id: {ticket_id}")

                    self._logger.info(ticket_notes)

                    # watermark_found = UtilsRepository.find_note(ticket_notes, self.MAIN_WATERMARK)
                    requested_watermark_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_REQUESTED_WATERMARK)
                    confirmed_note_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_CONFIRMED_WATERMARK)
                    confirmed_sms_note_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_CONFIRMED_SMS_WATERMARK)
                    tech_12_hours_before_note_found = UtilsRepository.find_note(
                        ticket_notes, self.TECH_12_HOURS_BEFORE_SMS_WATERMARK)
                    tech_2_hours_before_note_found = UtilsRepository.find_note(
                        ticket_notes, self.TECH_2_HOURS_BEFORE_SMS_WATERMARK)
                    tech_on_site_note_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_FIELD_ENGINEER_ON_SITE_WATERMARK)
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"requested_watermark_found: {requested_watermark_found} "
                                      f"confirmed_note_found: {confirmed_note_found} "
                                      f"confirmed_sms_note_found: {confirmed_sms_note_found} "
                                      f"tech_12_hours_before_note_found: {tech_12_hours_before_note_found} "
                                      f"tech_2_hours_before_note_found: {tech_2_hours_before_note_found} "
                                      f"tech_on_site_note_found: {tech_on_site_note_found}")

                    # Check if dispatch was created by the dispatch portal
                    if requested_watermark_found is None:
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- Watermark not found, ticket does not belong to us")
                        continue

                    if tech_on_site_note_found is None:
                        result_sms_tech_on_site_sended = await self._cts_repository.send_tech_on_site_sms(
                            dispatch_number, ticket_id, dispatch, sms_to)
                        if not result_sms_tech_on_site_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- SMS tech on site not sended")
                            continue

                        result_append_tech_on_site_sms_note = await self._cts_repository.append_tech_on_site_sms_note(
                            dispatch_number, igz_dispatch_number, ticket_id, sms_to,
                            dispatch.get('API_Resource_Name__c'))
                        if not result_append_tech_on_site_sms_note:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- A sms tech on site note not appended")
                            continue
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- A sms tech on site note appended")
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a sms tech tech on site note")
                except Exception as ex:
                    err_msg = f"Error: Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "\
                              f"- {dispatch}"
                    self._logger.error(err_msg)
                    await self._notifications_repository.send_slack_message(err_msg)
                    continue
        except Exception as ex:
            err_msg = f"Error: _monitor_tech_on_site_dispatches - {ex}"
            self._logger.error(f"Error: {ex}")
            await self._notifications_repository.send_slack_message(err_msg)

        stop = perf_counter()
        self._logger.info(f"Monitor Tech on Site Dispatches took: {(stop - start) / 60} minutes")
