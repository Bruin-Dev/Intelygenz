import asyncio
from datetime import datetime
from time import perf_counter
from shortuuid import uuid


from apscheduler.util import undefined
from pytz import timezone

from application.repositories.utils_repository import UtilsRepository
from application.repositories.lit_repository import LitRepository


class LitDispatchMonitor:
    def __init__(self, config, redis_client, event_bus, scheduler, logger, lit_repository, bruin_repository,
                 notifications_repository):
        self._config = config
        self._redis_client = redis_client
        self._scheduler = scheduler
        self._event_bus = event_bus
        self._logger = logger
        self._lit_repository = lit_repository
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
        self._logger.info('Scheduling Service Dispatch Monitor job...')
        next_run_time = undefined
        if exec_on_start:
            tz = timezone(self._config.DISPATCH_MONITOR_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('Service Outage Monitor job is going to be executed immediately')

        self._scheduler.add_job(self._lit_dispatch_monitoring_process, 'interval',
                                minutes=self._config.DISPATCH_MONITOR_CONFIG['jobs_intervals']['lit_dispatch_monitor'],
                                next_run_time=next_run_time, replace_existing=False,
                                id='_service_dispatch_monitor_lit_process')

    async def _lit_dispatch_monitoring_process(self):
        try:
            start = perf_counter()
            self._logger.info(f"Starting Dispatch Monitor Process for LIT...")
            response_lit_dispatches = await self._lit_repository.get_all_dispatches()
            response_lit_dispatches_status = response_lit_dispatches.get('status')
            response_lit_dispatches_body = response_lit_dispatches.get('body')

            if response_lit_dispatches_status not in range(200, 300):
                self._logger.error("Error getting all dispatches from LIT")
                err_msg = f'An error occurred retrieving all dispatches in the request status from LIT.'
                await self._notifications_repository.send_slack_message(err_msg)
                raise

            if response_lit_dispatches_body is None \
                    or 'Status' not in response_lit_dispatches_body \
                    or response_lit_dispatches_body['Status'] != "Success" \
                    or 'DispatchList' not in response_lit_dispatches_body \
                    or response_lit_dispatches_body['DispatchList'] is None:
                self._logger.error(f"[get_all_dispatches] Could not retrieve all dispatches, "
                                   f"reason: {response_lit_dispatches_body}")
                err_msg = f'An error occurred retrieving all dispatches from LIT.'
                await self._notifications_repository.send_slack_message(err_msg)
                return

            lit_dispatches = response_lit_dispatches_body.get('DispatchList', [])
            igz_dispatches = await self._filter_dispatches_by_watermark(lit_dispatches)
            dispatches_splitted_by_status = self._lit_repository.get_dispatches_splitted_by_status(igz_dispatches)

            self._logger.info(f"Splitted by status: "
                              f"{list(dispatches_splitted_by_status.keys())}")

            monitor_tasks = [
                self._monitor_confirmed_dispatches(
                    dispatches_splitted_by_status[self._lit_repository.DISPATCH_CONFIRMED]),
                self._monitor_tech_on_site_dispatches(
                    dispatches_splitted_by_status[self._lit_repository.DISPATCH_FIELD_ENGINEER_ON_SITE])
            ]

            start_monitor_tasks = perf_counter()
            await asyncio.gather(*monitor_tasks, return_exceptions=True)
            stop_monitor_tasks = perf_counter()
            self._logger.info(f"[LIT] All monitor tasks finished: "
                              f"{(stop_monitor_tasks - start_monitor_tasks) / 60} minutes")

            stop = perf_counter()
            self._logger.info(f"[LIT] Elapsed time processing all dispatches: {(stop - start) / 60} minutes")
        except Exception as ex:
            self._logger.error(f"Error: {ex}")

    async def _filter_dispatches_by_watermark(self, confirmed_dispatches):
        filtered_dispatches = []
        for dispatch in confirmed_dispatches:
            dispatch_number = dispatch.get("Dispatch_Number", None)
            ticket_id = dispatch.get("MetTel_Bruin_TicketID", None)
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
            watermark_found = UtilsRepository.find_note(ticket_notes, self.MAIN_WATERMARK)

            if watermark_found is None:
                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                  f"- Watermark not found, ticket is not created through dispatch portal")
                continue

            note_dispatch_number = UtilsRepository.find_dispatch_number_watermark(watermark_found,
                                                                                  dispatch_number,
                                                                                  self.MAIN_WATERMARK)
            if len(note_dispatch_number) == 0:
                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                  f"dispatch number not found found in ticket note: {note_dispatch_number}")
                continue

            requested_watermark_found = UtilsRepository.find_note(
                ticket_notes, self.DISPATCH_REQUESTED_WATERMARK)
            if requested_watermark_found is None:
                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                  f"- Watermark not found, ticket does not belong to us")
                continue
            filtered_dispatches.append(dispatch)
        return filtered_dispatches

    async def _monitor_confirmed_dispatches(self, confirmed_dispatches):
        try:
            start = perf_counter()
            self._logger.info(f"Dispatches to process before filter {len(confirmed_dispatches)}")
            confirmed_dispatches = list(filter(self._lit_repository.is_dispatch_confirmed, confirmed_dispatches))
            self._logger.info(f"Total confirmed dispatches after filter: {len(confirmed_dispatches)}")

            for dispatch in confirmed_dispatches:
                try:
                    dispatch_number = dispatch.get('Dispatch_Number', None)
                    ticket_id = dispatch.get('MetTel_Bruin_TicketID', None)

                    self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id}")
                    if ticket_id is None or not LitRepository.is_valid_ticket_id(ticket_id) or dispatch_number is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} discarded.")
                        continue

                    datetime_tz_response = self._lit_repository.get_dispatch_confirmed_date_time_localized(
                        dispatch, dispatch_number, ticket_id)

                    if datetime_tz_response is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                          f"Could not determine date time of dispatch: {dispatch}")
                        err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                  f"An error occurred retrieve datetime of dispatch: " \
                                  f"{dispatch.get('Hard_Time_of_Dispatch_Local', None)} - " \
                                  f"{dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local', None)} "
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue

                    date_time_of_dispatch = datetime_tz_response['datetime_localized']
                    tz = datetime_tz_response['timezone']
                    datetime_formatted_str = datetime_tz_response['datetime_formatted_str']

                    # Client phonenumber
                    sms_to = LitRepository.get_sms_to(dispatch)
                    if sms_to is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                          f"- Error: we could not retrieve 'sms_to' number from: "
                                          f"{dispatch.get('Job_Site_Contact_Name_and_Phone_Number')}")
                        err_msg = f"An error occurred retrieve 'sms_to' number " \
                                  f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                  f"from: {dispatch.get('Job_Site_Contact_Name_and_Phone_Number')}"
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue

                    # Tech phonenumber
                    sms_to_tech = LitRepository.get_sms_to_tech(dispatch)

                    if sms_to_tech is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                          f"- Error: we could not retrieve 'sms_to_tech' number from: "
                                          f"{dispatch.get('Tech_Mobile_Number')}")
                        err_msg = f"An error occurred retrieve 'sms_to_tech' number " \
                                  f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                  f"from: {dispatch.get('Tech_Mobile_Number')}"
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue

                    self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                      f"Getting ticket details")

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

                    self._logger.info(
                        f"Checking watermarks for Dispatch [{dispatch_number}] in ticket_id: {ticket_id}")

                    self._logger.info(ticket_notes)
                    self._logger.info(f"Filtering ticket notes to contain only notes for the "
                                      f"Lit Dispatch[{dispatch_number}]")
                    filtered_ticket_notes = self._filter_ticket_note_by_dispatch_number(ticket_notes,
                                                                                        dispatch_number,
                                                                                        ticket_id)
                    self._logger.info(filtered_ticket_notes)

                    requested_watermark_found = UtilsRepository.find_note(filtered_ticket_notes,
                                                                          self.DISPATCH_REQUESTED_WATERMARK)
                    confirmed_note_found = UtilsRepository.find_note(filtered_ticket_notes,
                                                                     self.DISPATCH_CONFIRMED_WATERMARK)
                    confirmed_sms_note_found = UtilsRepository.find_note(filtered_ticket_notes,
                                                                         self.DISPATCH_CONFIRMED_SMS_WATERMARK)
                    confirmed_sms_tech_note_found = UtilsRepository.find_note(
                        filtered_ticket_notes, self.DISPATCH_CONFIRMED_SMS_TECH_WATERMARK)
                    tech_12_hours_before_note_found = UtilsRepository.find_note(filtered_ticket_notes,
                                                                                self.TECH_12_HOURS_BEFORE_SMS_WATERMARK)
                    tech_12_hours_before_tech_note_found = UtilsRepository.find_note(
                        filtered_ticket_notes, self.TECH_12_HOURS_BEFORE_SMS_TECH_WATERMARK)
                    tech_2_hours_before_note_found = UtilsRepository.find_note(filtered_ticket_notes,
                                                                               self.TECH_2_HOURS_BEFORE_SMS_WATERMARK)
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

                    # import pdb;pdb.set_trace()
                    # Check if dispatch has a confirmed note
                    if confirmed_note_found is None:
                        result_append_confirmed_note = await self._lit_repository.append_confirmed_note(
                            dispatch_number, ticket_id, dispatch)
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
                        sms_sended = await self._lit_repository.send_confirmed_sms(
                            dispatch_number, ticket_id, dispatch, sms_to)
                        if not sms_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS could not be sent to {sms_to}.")
                            # continue
                        else:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- Confirm SMS note not found")

                            result_append_confirmed_sms_note = await self._lit_repository.append_confirmed_sms_note(
                                dispatch_number, ticket_id, sms_to)

                            if not result_append_confirmed_sms_note:
                                self._logger.info("Confirmed SMS note not appended")
                                # continue
                            else:
                                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                  f"Confirmed Note, SMS sent and Confirmed SMS note sent OK.")
                            # continue
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a sms confirmed note")

                    if confirmed_sms_tech_note_found is None:
                        self._logger.info(f"Dispatch: {dispatch_number} "
                                          f"Ticket_id: {ticket_id} - Sending confirmed SMS Tech")
                        sms_sended = await self._lit_repository.send_confirmed_sms_tech(
                            dispatch_number, ticket_id, dispatch, sms_to_tech)
                        if not sms_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS Tech could not be sent to {sms_to_tech}.")
                            continue
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- Confirm SMS tech note not found")

                        result_append_confirmed_sms_note = await self._lit_repository.append_confirmed_sms_tech_note(
                            dispatch_number, ticket_id, sms_to_tech)

                        if not result_append_confirmed_sms_note:
                            self._logger.info("Confirmed SMS tech note not appended")
                            continue
                        else:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"Confirmed Note, "
                                              f"SMS tech sent and Confirmed SMS tech note sent OK.")
                        continue
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a sms tech confirmed note")

                    # Check if dispatch has a sms 12 hours note
                    if tech_12_hours_before_note_found is None:
                        hours_diff = UtilsRepository.get_diff_hours_between_datetimes(datetime.now(tz),
                                                                                      date_time_of_dispatch)
                        if hours_diff > self.HOURS_12:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS 12h note not needed to send now")
                            # continue
                        else:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"Sending SMS 12h note")
                            result_sms_12_sended = await self._lit_repository.send_tech_12_sms(
                                dispatch_number, ticket_id, dispatch, sms_to)
                            if not result_sms_12_sended:
                                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                  f"- SMS 12h not sended")
                                # continue
                            else:

                                result_append_tech_12_sms_note = await self._lit_repository.append_tech_12_sms_note(
                                    dispatch_number, ticket_id, sms_to)
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

                    # Check if dispatch has a sms 12 hours tech note
                    if tech_12_hours_before_tech_note_found is None:
                        hours_diff = UtilsRepository.get_diff_hours_between_datetimes(datetime.now(tz),
                                                                                      date_time_of_dispatch)
                        if hours_diff > self.HOURS_12:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS tech 12h note not needed to send now")
                            continue

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"Sending SMS tech 12h note")
                        result_sms_12_sended = await self._lit_repository.send_tech_12_sms_tech(
                            dispatch_number, ticket_id, dispatch, sms_to_tech)
                        if not result_sms_12_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- SMS tech 12h not sended")
                            continue

                        result_append_tech_12_sms_note = await self._lit_repository.append_tech_12_sms_tech_note(
                            dispatch_number, ticket_id, sms_to_tech)
                        if not result_append_tech_12_sms_note:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- A sms tech 12 hours before note not appended")
                            continue
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- A sms tech 12 hours before note appended")
                        continue
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- Already has a sms tech 12 hours before note")

                    # Check if dispatch has a sms 2 hours note
                    if tech_2_hours_before_note_found is None:
                        hours_diff = UtilsRepository.get_diff_hours_between_datetimes(datetime.now(tz),
                                                                                      date_time_of_dispatch)
                        if hours_diff > self.HOURS_2:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS 2h note not needed to send now")
                            # continue
                        else:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"Sending SMS 2h note")
                            result_sms_2_sended = await self._lit_repository.send_tech_2_sms(
                                dispatch_number, ticket_id, dispatch, sms_to)
                            if not result_sms_2_sended:
                                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                  f"- SMS 2h not sended")
                                # continue
                            else:
                                result_append_tech_2_sms_note = await self._lit_repository.append_tech_2_sms_note(
                                    dispatch_number, ticket_id, sms_to)
                                if not result_append_tech_2_sms_note:
                                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                      f"- A sms tech 2 hours before note not appended")
                                    # continue
                                else:
                                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                      f"- A sms tech 2 hours before note appended")
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a sms tech 2 hours before note")

                    # Check if dispatch has a sms 2 hours note
                    if tech_2_hours_before_tech_note_found is None:
                        hours_diff = UtilsRepository.get_diff_hours_between_datetimes(datetime.now(tz),
                                                                                      date_time_of_dispatch)
                        if hours_diff > self.HOURS_2:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS tech 2h note not needed to send now")
                            continue

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"Sending SMS tech 2h note")
                        result_sms_2_sended = await self._lit_repository.send_tech_2_sms_tech(
                            dispatch_number, ticket_id, dispatch, sms_to_tech)
                        if not result_sms_2_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- SMS tech 2h not sended")
                            continue

                        result_append_tech_2_sms_note = await self._lit_repository.append_tech_2_sms_tech_note(
                            dispatch_number, ticket_id, sms_to)
                        if not result_append_tech_2_sms_note:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- A sms tech 2 hours before note not appended")
                            continue
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- A sms tech 2 hours before note appended")
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a sms tech 2 hours before note")

                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- This ticket should never be again in Dispatch Confirmed, "
                                      f"at some point it has to change to tech on site")
                except Exception as ex:
                    err_msg = f"Error: Dispatch [{dispatch_number}] in ticket_id: {ticket_id} " \
                              f"- {dispatch}"
                    self._logger.error(err_msg)
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
            tech_on_site_dispatches = list(filter(self._lit_repository.is_tech_on_site, tech_on_site_dispatches))
            self._logger.info(f"Dispatches to process after filter {len(tech_on_site_dispatches)}")

            for dispatch in tech_on_site_dispatches:
                try:
                    dispatch_number = dispatch.get('Dispatch_Number', None)
                    ticket_id = dispatch.get('MetTel_Bruin_TicketID', None)

                    self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id}")
                    if ticket_id is None or not LitRepository.is_valid_ticket_id(ticket_id) or dispatch_number is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} discarded.")
                        continue

                    datetime_tz_response = self._lit_repository.get_dispatch_confirmed_date_time_localized(
                        dispatch, dispatch_number, ticket_id)

                    if datetime_tz_response is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                          f"Could not determine date time of dispatch: {dispatch}")
                        err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                  f"An error occurred retrieve datetime of dispatch: " \
                                  f"{dispatch.get('Hard_Time_of_Dispatch_Local', None)} - " \
                                  f"{dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local', None)} "
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue

                    sms_to = LitRepository.get_sms_to(dispatch)

                    if sms_to is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                          f"- Error: we could not retrieve 'sms_to' number from: "
                                          f"{dispatch.get('Job_Site_Contact_Name_and_Phone_Number')}")
                        err_msg = f"An error occurred retrieve 'sms_to' number " \
                                  f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                  f"from: {dispatch.get('Job_Site_Contact_Name_and_Phone_Number')}"
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

                    self._logger.info(f"Checking watermarks for Dispatch [{dispatch_number}] in ticket_id: {ticket_id}")

                    self._logger.info(ticket_notes)
                    self._logger.info(f"Filtering ticket notes to contain only notes for the "
                                      f"Lit Dispatch[{dispatch_number}]")
                    filtered_ticket_notes = self._filter_ticket_note_by_dispatch_number(ticket_notes,
                                                                                        dispatch_number,
                                                                                        ticket_id)
                    self._logger.info(filtered_ticket_notes)

                    requested_watermark_found = UtilsRepository.find_note(filtered_ticket_notes,
                                                                          self.DISPATCH_REQUESTED_WATERMARK)
                    confirmed_note_found = UtilsRepository.find_note(filtered_ticket_notes,
                                                                     self.DISPATCH_CONFIRMED_WATERMARK)
                    confirmed_sms_note_found = UtilsRepository.find_note(filtered_ticket_notes,
                                                                         self.DISPATCH_CONFIRMED_SMS_WATERMARK)
                    tech_12_hours_before_note_found = UtilsRepository.find_note(filtered_ticket_notes,
                                                                                self.TECH_12_HOURS_BEFORE_SMS_WATERMARK)
                    tech_2_hours_before_note_found = UtilsRepository.find_note(filtered_ticket_notes,
                                                                               self.TECH_2_HOURS_BEFORE_SMS_WATERMARK)
                    tech_on_site_note_found = UtilsRepository.find_note(filtered_ticket_notes,
                                                                        self.DISPATCH_FIELD_ENGINEER_ON_SITE_WATERMARK)

                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"requested_watermark_found: {requested_watermark_found} "
                                      f"confirmed_note_found: {confirmed_note_found} "
                                      f"confirmed_sms_note_found: {confirmed_sms_note_found} "
                                      f"tech_12_hours_before_note_found: {tech_12_hours_before_note_found} "
                                      f"tech_2_hours_before_note_found: {tech_2_hours_before_note_found} "
                                      f"tech_on_site_note_found: {tech_on_site_note_found}")

                    if tech_on_site_note_found is None:
                        result_sms_tech_on_site_sended = await self._lit_repository.send_tech_on_site_sms(
                            dispatch_number, ticket_id, dispatch, sms_to)
                        if not result_sms_tech_on_site_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- SMS tech on site not sended")
                            continue

                        result_append_tech_on_site_sms_note = await self._lit_repository.append_tech_on_site_sms_note(
                            dispatch_number, ticket_id, sms_to, dispatch.get('Tech_First_Name'))
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

    def _filter_ticket_note_by_dispatch_number(self, ticket_notes, dispatch_number, ticket_id):
        filtered_ticket_notes = []
        for note in ticket_notes:
            note_dispatch_number = UtilsRepository.find_dispatch_number_watermark(note,
                                                                                  dispatch_number,
                                                                                  self.MAIN_WATERMARK)
            if len(note_dispatch_number) == 0:
                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                  f"dispatch number not found found in ticket note: {note}")
                continue
            filtered_ticket_notes.append(note)

        return filtered_ticket_notes
