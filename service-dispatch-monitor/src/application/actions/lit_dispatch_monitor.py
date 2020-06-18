import asyncio
from datetime import datetime
from time import perf_counter
from shortuuid import uuid


from apscheduler.util import undefined
from pytz import timezone

from application.repositories.utils_repository import UtilsRepository
from application.repositories.lit_repository import LitRepository
from application.templates.lit.lit_dispatch_confirmed import lit_get_dispatch_confirmed_note
from application.templates.lit.lit_dispatch_confirmed import lit_get_dispatch_confirmed_sms_note
from application.templates.lit.lit_dispatch_confirmed import lit_get_tech_24_hours_before_sms_note
from application.templates.lit.lit_dispatch_confirmed import lit_get_tech_2_hours_before_sms_note
from application.templates.lit.lit_tech_on_site import lit_get_tech_on_site_note
from application.templates.lit.sms.dispatch_confirmed import lit_get_dispatch_confirmed_sms
from application.templates.lit.sms.dispatch_confirmed import lit_get_tech_24_hours_before_sms
from application.templates.lit.sms.dispatch_confirmed import lit_get_tech_2_hours_before_sms
from application.templates.lit.sms.tech_on_site import lit_get_tech_on_site_sms
from application.templates.lit.lit_repair_completed import lit_get_repair_completed_note


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

        self.HOURS_24 = 24
        self.HOURS_2 = 2

        # Dispatch Notes watermarks
        self.MAIN_WATERMARK = '#*Automation Engine*#'
        self.DISPATCH_REQUESTED_WATERMARK = 'Dispatch Management - Dispatch Requested'
        self.DISPATCH_CONFIRMED_WATERMARK = 'Dispatch Management - Dispatch Confirmed'
        self.DISPATCH_FIELD_ENGINEER_ON_SITE_WATERMARK = 'Dispatch Management - Field Engineer On Site'
        self.DISPATCH_REPAIR_COMPLETED_WATERMARK = 'Dispatch Management - Repair Completed'

        # SMS Notes watermarks
        self.DISPATCH_CONFIRMED_SMS_WATERMARK = 'Dispatch confirmation SMS sent to'
        self.TECH_24_HOURS_BEFORE_SMS_WATERMARK = 'Dispatch 24h prior reminder SMS'
        self.TECH_2_HOURS_BEFORE_SMS_WATERMARK = 'Dispatch 2h prior reminder SMS'
        self.TECH_ON_SITE_SMS_WATERMARK = 'Dispatch tech on site SMS'

        # Dispatch Statuses
        self.DISPATCH_REQUESTED = 'New Dispatch'
        self.DISPATCH_CONFIRMED = 'Request Confirmed'
        self.DISPATCH_FIELD_ENGINEER_ON_SITE = 'Tech Arrived'
        self.DISPATCH_REPAIR_COMPLETED = 'Close Out'
        self._dispatch_statuses = [
            self.DISPATCH_REQUESTED,
            self.DISPATCH_CONFIRMED,
            self.DISPATCH_FIELD_ENGINEER_ON_SITE,
            self.DISPATCH_REPAIR_COMPLETED
        ]

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

    def _is_dispatch_confirmed(self, dispatch):
        # A confirmed dispatch must have status: 'Request Confirmed'
        # and this two fields filled Tech_First_Name, Tech_Mobile_Number
        return all([dispatch is not None,
                    dispatch.get('Dispatch_Status') == self.DISPATCH_CONFIRMED,
                    dispatch.get("Tech_First_Name") is not None,
                    dispatch.get("Tech_Mobile_Number") is not None])

    def _is_tech_on_site(self, dispatch):
        # Filter tech on site dispatches
        # Dispatch Confirmed --> Field Engineer On Site:
        # Tech_Arrived_On_Site is set to true and Time_of_Check_In is set.
        # Bruin Note:*#Automation Engine#*Dispatch Management - Field Engineer On Site<FE Name> has arrived
        return all([dispatch is not None,
                    dispatch.get('Dispatch_Status') == self.DISPATCH_FIELD_ENGINEER_ON_SITE,
                    dispatch.get("Tech_Arrived_On_Site") is not None,
                    dispatch.get("Tech_Arrived_On_Site") is True,
                    dispatch.get("Time_of_Check_In") is not None])

    def _is_repair_completed(self, dispatch):
        # Field Engineer On Site --> Repair Completed: Tech_Off_Site is set to true and Time_of_Check_Out is set.
        # Bruin Note:
        # *#Automation Engine#*
        # Dispatch Management - Repair Completed
        #
        # Dispatch request for Mar 16, 2020 @ 07:00 AM Eastern has been completed.
        # Reference: 4585231
        return all([dispatch is not None,
                    dispatch.get('Dispatch_Status') == self.DISPATCH_REPAIR_COMPLETED,
                    dispatch.get("Tech_Arrived_On_Site") is not None,
                    dispatch.get("Tech_Arrived_On_Site") is True,
                    dispatch.get("Time_of_Check_In") is not None,
                    dispatch.get("Time_of_Check_Out") is not None])

    def _is_valid_ticket_id(self, ticket_id):
        # Check ticket id format for example: '4663397|IW24654081'
        # Bruin ticket ID like 712637/IW76236 and 123-3123 are likely to be from other
        # kind of tickets (like new installations), thus other teams that are not his,
        # 4485610(Order)/4520284(Port)
        # Discard All with more than one ticket
        ticket_id = ticket_id.replace(' ', '')
        ticket_id_1 = ticket_id.split('|')
        ticket_id_2 = ticket_id.split('-')
        ticket_id_3 = ticket_id.split('/')
        if len(ticket_id_1) > 1:
            return False
        elif len(ticket_id_2) > 1:
            return False
        elif len(ticket_id_3) > 1:
            return False
        return True

    def _get_dispatches_splitted_by_status(self, dispatches):
        dispatches_splitted_by_status = {}
        for ds in self._dispatch_statuses:
            dispatches_splitted_by_status[ds] = []
        for dispatch in dispatches:
            if dispatch.get('Dispatch_Status') in self._dispatch_statuses:
                dispatches_splitted_by_status[dispatch.get('Dispatch_Status')].append(dispatch)
        return dispatches_splitted_by_status

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
            dispatches_splitted_by_status = self._get_dispatches_splitted_by_status(lit_dispatches)

            self._logger.info(f"Splitted by status: "
                              f"{list(dispatches_splitted_by_status.keys())}")

            monitor_tasks = [
                self._monitor_confirmed_dispatches(dispatches_splitted_by_status[self.DISPATCH_CONFIRMED]),
                self._monitor_tech_on_site_dispatches(
                    dispatches_splitted_by_status[self.DISPATCH_FIELD_ENGINEER_ON_SITE]),
                # self._monitor_repair_completed(dispatches_splitted_by_status[self.DISPATCH_REPAIR_COMPLETED])
            ]

            start_monitor_tasks = perf_counter()
            await asyncio.gather(*monitor_tasks, return_exceptions=True)
            stop_monitor_tasks = perf_counter()
            self._logger.info(f"[LIT] All monitor tasks finished: "
                              f"{(stop_monitor_tasks - start_monitor_tasks) / 60} minutes")

            stop = perf_counter()
            self._logger.info(f"[LIT] Elapsed time processing all dispatches cache: {(stop - start) / 60} minutes")
        except Exception as ex:
            self._logger.error(f"Error: {ex}")

    async def _send_confirmed_sms(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local')
        }

        sms_data = lit_get_dispatch_confirmed_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }
        self._logger.info(f"Sending SMS to {sms_to} with data: `{sms_data}`")
        sms_response = await self._notifications_repository.send_sms(sms_payload)
        sms_response_status = sms_response['status']
        sms_response_body = sms_response['body']
        if sms_response_status not in range(200, 300):
            self._logger.info(f"SMS: `{sms_data}` TO: {sms_to} "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - SMS NOT sent")
            err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                      f'An error occurred when sending Confirmed SMS with notifier client. ' \
                      f'payload: {sms_payload}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(
            f"SMS sent Response {sms_response_body}")
        return True

    async def _send_tech_24_sms(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'phone_number': sms_to
        }

        sms_data = lit_get_tech_24_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }
        self._logger.info(f"Sending SMS to {sms_to} with data: `{sms_data}`")
        sms_response = await self._notifications_repository.send_sms(sms_payload)
        sms_response_status = sms_response['status']
        sms_response_body = sms_response['body']
        if sms_response_status not in range(200, 300):
            self._logger.info(f"SMS: `{sms_data}` TO: {sms_to} "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - SMS NOT sent")
            err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                      f'An error occurred when sending a tech 24 hours SMS with notifier client. ' \
                      f'payload: {sms_payload}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(
            f"SMS sent Response {sms_response_body}")
        return True

    async def _send_tech_2_sms(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'phone_number': sms_to
        }

        sms_data = lit_get_tech_2_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }
        self._logger.info(f"Sending SMS to {sms_to} with data: `{sms_data}`")
        sms_response = await self._notifications_repository.send_sms(sms_payload)
        sms_response_status = sms_response['status']
        sms_response_body = sms_response['body']
        if sms_response_status not in range(200, 300):
            self._logger.info(f"SMS: `{sms_data}` TO: {sms_to} "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - SMS NOT sent")
            err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                      f'An error occurred when sending a tech 2 hours SMS with notifier client. ' \
                      f'payload: {sms_payload}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(
            f"SMS sent Response {sms_response_body}")
        return True

    async def _send_tech_on_site_sms(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'field_engineer_name': dispatch.get('Tech_First_Name')
        }

        sms_data = lit_get_tech_on_site_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }
        self._logger.info(f"Sending SMS to {sms_to} with data: `{sms_data}`")
        sms_response = await self._notifications_repository.send_sms(sms_payload)
        sms_response_status = sms_response['status']
        sms_response_body = sms_response['body']
        if sms_response_status not in range(200, 300):
            self._logger.info(f"SMS: `{sms_data}` TO: {sms_to} "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - SMS NOT sent")
            err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                      f'An error occurred when sending a tech on site SMS with notifier client. ' \
                      f'payload: {sms_payload}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(
            f"SMS sent Response {sms_response_body}")
        return True

    async def _append_confirmed_note(self, dispatch_number, ticket_id, dispatch) -> bool:
        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                          f"- Adding confirm note")
        note_data = {
            'vendor': 'LIT',
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'tech_name': dispatch.get('Tech_First_Name'),
            'tech_phone': dispatch.get('Tech_Mobile_Number')
        }
        note = lit_get_dispatch_confirmed_note(note_data)
        # if self._config.DISPATCH_MONITOR_CONFIG['environment'] == 'production':
        append_note_response = await self._bruin_repository.append_note_to_ticket(ticket_id, note)

        append_note_response_status = append_note_response['status']
        append_note_response_body = append_note_response['body']
        if append_note_response_status not in range(200, 300):
            self._logger.info(f"Note: `{note}` "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - Not appended")
            err_msg = f'An error occurred when appending a confirmed note with bruin client. ' \
                      f'Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - payload: {note_data}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - Confirmed note appended")
        self._logger.info(
            f"Confirmed Note appended. Response {append_note_response_body}")
        return True

    async def _append_confirmed_sms_note(self, dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
            'phone_number': sms_to
        }
        sms_note = lit_get_dispatch_confirmed_sms_note(sms_note_data)
        append_sms_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, sms_note)
        append_sms_note_response_status = append_sms_note_response['status']
        append_sms_note_response_body = append_sms_note_response['body']
        if append_sms_note_response_status not in range(200, 300):
            self._logger.info(f"Note: `{sms_note}` "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - SMS Confirmed note not appended")
            err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                      f"- SMS Confirmed note not appended"
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{sms_note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - Confirmed SMS note Appended")
        self._logger.info(
            f"SMS Confirmed note appended. Response {append_sms_note_response_body}")
        return True

    async def _append_tech_24_sms_note(self, dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
            'phone_number': sms_to
        }
        sms_note = lit_get_tech_24_hours_before_sms_note(sms_note_data)
        append_sms_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, sms_note)
        append_sms_note_response_status = append_sms_note_response['status']
        append_sms_note_response_body = append_sms_note_response['body']
        if append_sms_note_response_status not in range(200, 300):
            self._logger.info(f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} "
                              f"Note: `{sms_note}` "
                              f"- SMS tech 2 hours note not appended")
            err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                      f"- SMS tech 24 hours note not appended"
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{sms_note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - SMS 24h note Appended")
        self._logger.info(
            f"SMS 24h Note appended. Response {append_sms_note_response_body}")
        return True

    async def _append_tech_2_sms_note(self, dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
            'phone_number': sms_to
        }
        sms_note = lit_get_tech_2_hours_before_sms_note(sms_note_data)
        append_sms_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, sms_note)
        append_sms_note_response_status = append_sms_note_response['status']
        append_sms_note_response_body = append_sms_note_response['body']
        if append_sms_note_response_status not in range(200, 300):
            self._logger.info(f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` "
                              f"- SMS tech 2 hours note not appended")
            err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                      f"- SMS tech 2 hours note not appended"
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{sms_note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - SMS 2h note Appended")
        self._logger.info(
            f"SMS 2h Note appended. Response {append_sms_note_response_body}")
        return True

    async def _append_tech_on_site_sms_note(self, dispatch_number, ticket_id, sms_to, field_engineer_name) -> bool:
        sms_note_data = {
            'field_engineer_name': field_engineer_name
        }
        sms_note = lit_get_tech_on_site_note(sms_note_data)
        append_sms_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, sms_note)
        append_sms_note_response_status = append_sms_note_response['status']
        append_sms_note_response_body = append_sms_note_response['body']
        if append_sms_note_response_status not in range(200, 300):
            self._logger.info(f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` "
                              f"- SMS tech on site note not appended")
            err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                      f"- SMS tech on site note not appended"
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{sms_note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - SMS tech on site note Appended")
        self._logger.info(
            f"Tech on site note appended. Response {append_sms_note_response_body}")
        return True

    async def _monitor_confirmed_dispatches(self, confirmed_dispatches):
        try:
            start = perf_counter()
            self._logger.info(f"Dispatches to process before filter {len(confirmed_dispatches)}")
            confirmed_dispatches = list(filter(self._is_dispatch_confirmed, confirmed_dispatches))
            self._logger.info(f"Total confirmed dispatches after filter: {len(confirmed_dispatches)}")

            for dispatch in confirmed_dispatches:
                try:
                    dispatch_number = dispatch.get('Dispatch_Number', None)
                    ticket_id = dispatch.get('MetTel_Bruin_TicketID', None)

                    self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id}")
                    if ticket_id is None or not self._is_valid_ticket_id(ticket_id) or dispatch_number is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} discarded.")
                        continue

                    datetime_tz_response = self._lit_repository.get_dispatch_confirmed_date_time_localized(
                        dispatch, dispatch_number, ticket_id)

                    if datetime_tz_response is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                          f"Could not determine date time of dispatch. {dispatch}")
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

                    date_time_of_dispatch = datetime_tz_response['datetime_localized']
                    tz = datetime_tz_response['timezone']

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

                    self._logger.info(
                        f"Checking watermarks for Dispatch [{dispatch_number}] in ticket_id: {ticket_id}")

                    self._logger.info(ticket_notes)

                    requested_watermark_found = UtilsRepository.find_note(ticket_notes,
                                                                          self.DISPATCH_REQUESTED_WATERMARK)
                    confirmed_note_found = UtilsRepository.find_note(ticket_notes, self.DISPATCH_CONFIRMED_WATERMARK)
                    confirmed_sms_note_found = UtilsRepository.find_note(ticket_notes,
                                                                         self.DISPATCH_CONFIRMED_SMS_WATERMARK)
                    tech_24_hours_before_note_found = UtilsRepository.find_note(ticket_notes,
                                                                                self.TECH_24_HOURS_BEFORE_SMS_WATERMARK)
                    tech_2_hours_before_note_found = UtilsRepository.find_note(ticket_notes,
                                                                               self.TECH_2_HOURS_BEFORE_SMS_WATERMARK)

                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"requested_watermark_found: {requested_watermark_found} "
                                      f"confirmed_note_found: {confirmed_note_found} "
                                      f"confirmed_sms_note_found: {confirmed_sms_note_found} "
                                      f"tech_24_hours_before_note_found: {tech_24_hours_before_note_found} "
                                      f"tech_2_hours_before_note_found: {tech_2_hours_before_note_found} ")

                    # Check if dispatch was created by the dispatch portal
                    if requested_watermark_found is None:
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- Watermark not found, ticket does not belong to us")
                        continue

                    # Check if dispatch has a confirmed note
                    if confirmed_note_found is None:
                        result_append_confirmed_note = await self._append_confirmed_note(
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
                        sms_sended = await self._send_confirmed_sms(dispatch_number, ticket_id, dispatch, sms_to)
                        if not sms_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS could not be sent to {sms_to}.")
                            continue

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- Confirm SMS note not found")

                        result_append_confirmed_sms_note = await self._append_confirmed_sms_note(
                            dispatch_number, ticket_id, sms_to)

                        if not result_append_confirmed_sms_note:
                            self._logger.info("Confirmed SMS note not appended")
                            continue

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"Confirmed Note, SMS send and Confirmed SMS note sent OK.")
                        continue
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a sms confirmed note")

                    # Check if dispatch has a sms 2 hours note
                    if tech_24_hours_before_note_found is None:
                        hours_diff = UtilsRepository.get_diff_hours_between_datetimes(datetime.now(tz),
                                                                                      date_time_of_dispatch)
                        if hours_diff > self.HOURS_24:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS 24h note not needed to send now")
                            continue

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"Sending SMS 24h note")
                        result_sms_24_sended = await self._send_tech_24_sms(dispatch_number, ticket_id, dispatch,
                                                                            sms_to)
                        if not result_sms_24_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- SMS 24h not sended")
                            continue

                        result_append_tech_24_sms_note = await self._append_tech_24_sms_note(
                            dispatch_number, ticket_id, sms_to)
                        if not result_append_tech_24_sms_note:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- A sms tech 24 hours before note not appended")
                            continue
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- A sms tech 24 hours before note appended")
                        continue
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- Already has a sms tech 24 hours before note")

                    # Check if dispatch has a sms 2 hours note
                    if tech_2_hours_before_note_found is None:
                        hours_diff = UtilsRepository.get_diff_hours_between_datetimes(datetime.now(tz),
                                                                                      date_time_of_dispatch)
                        if hours_diff > self.HOURS_2:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS 2h note not needed to send now")
                            continue

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"Sending SMS 2h note")
                        result_sms_2_sended = await self._send_tech_2_sms(dispatch_number, ticket_id, dispatch, sms_to)
                        if not result_sms_2_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- SMS 2h not sended")
                            continue

                        result_append_tech_2_sms_note = await self._append_tech_2_sms_note(
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
            tech_on_site_dispatches = list(filter(self._is_tech_on_site, tech_on_site_dispatches))
            self._logger.info(f"Dispatches to process after filter {len(tech_on_site_dispatches)}")

            for dispatch in tech_on_site_dispatches:
                try:
                    dispatch_number = dispatch.get('Dispatch_Number', None)
                    ticket_id = dispatch.get('MetTel_Bruin_TicketID', None)

                    self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id}")
                    if ticket_id is None or not self._is_valid_ticket_id(ticket_id) or dispatch_number is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} discarded.")
                        continue

                    datetime_tz_response = self._lit_repository.get_dispatch_confirmed_date_time_localized(
                        dispatch, dispatch_number, ticket_id)

                    if datetime_tz_response is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                          f"Could not determine date time of dispatch. {dispatch}")
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

                    self._logger.info(
                        f"Checking watermarks for Dispatch [{dispatch_number}] in ticket_id: {ticket_id}")

                    self._logger.info(ticket_notes)

                    requested_watermark_found = UtilsRepository.find_note(ticket_notes,
                                                                          self.DISPATCH_REQUESTED_WATERMARK)
                    confirmed_note_found = UtilsRepository.find_note(ticket_notes, self.DISPATCH_CONFIRMED_WATERMARK)
                    confirmed_sms_note_found = UtilsRepository.find_note(ticket_notes,
                                                                         self.DISPATCH_CONFIRMED_SMS_WATERMARK)
                    tech_24_hours_before_note_found = UtilsRepository.find_note(ticket_notes,
                                                                                self.TECH_24_HOURS_BEFORE_SMS_WATERMARK)
                    tech_2_hours_before_note_found = UtilsRepository.find_note(ticket_notes,
                                                                               self.TECH_2_HOURS_BEFORE_SMS_WATERMARK)
                    tech_on_site_note_found = UtilsRepository.find_note(ticket_notes,
                                                                        self.DISPATCH_FIELD_ENGINEER_ON_SITE_WATERMARK)

                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"requested_watermark_found: {requested_watermark_found} "
                                      f"confirmed_note_found: {confirmed_note_found} "
                                      f"confirmed_sms_note_found: {confirmed_sms_note_found} "
                                      f"tech_24_hours_before_note_found: {tech_24_hours_before_note_found} "
                                      f"tech_2_hours_before_note_found: {tech_2_hours_before_note_found} "
                                      f"tech_on_site_note_found: {tech_on_site_note_found}")

                    # Check if dispatch was created by the dispatch portal
                    if requested_watermark_found is None:
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- Watermark not found, ticket does not belong to us")
                        continue
                    # TODO: check if we missed other notes?
                    if tech_on_site_note_found is None:
                        result_sms_tech_on_site_sended = await self._send_tech_on_site_sms(dispatch_number, ticket_id,
                                                                                           dispatch, sms_to)
                        if not result_sms_tech_on_site_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- SMS tech on site not sended")
                            continue

                        result_append_tech_on_site_sms_note = await self._append_tech_on_site_sms_note(
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

    # async def _monitor_repair_completed(self, dispatches_completed):
    #     try:
    #         start = perf_counter()
    #         # Filter repair completed dispatches
    #         self._logger.info(f"Dispatches to process before filter {len(dispatches_completed)}")
    #         dispatches_completed = list(filter(self._is_repair_completed, dispatches_completed))
    #         self._logger.info(f"Dispatches to process after filter {len(dispatches_completed)}")
    #         for dispatch in dispatches_completed:
    #             dispatch_number = dispatch.get('Dispatch_Number', None)
    #             ticket_id = dispatch.get('MetTel_Bruin_TicketID', None)
    #
    #             self._logger.info(f"Dispatch: [{dispatch_number}] ticket id for {ticket_id}")
    #             if not self._is_valid_ticket_id(ticket_id):
    #                 self._logger.info(f"Dispatch: [{dispatch_number}] ticket id for {ticket_id} discarded.")
    #                 continue
    #
    #             if ticket_id is not None:
    #                 self._logger.info(f"Getting details for ticket [{ticket_id}]")
    #
    #                 response = await self._get_ticket_details(ticket_id)
    #                 response_status = response['status']
    #                 response_body = response['body']
    #
    #                 ticket_notes = response_body.get('ticketNotes')
    #
    #                 if response_status not in range(200, 300):
    #                     self._logger.error(f"Dispatch [{dispatch_number}] get ticket details for ticket {ticket_id}")
    #                     # TODO: notify slack
    #                     continue
    #
    #                 if dispatch_number and ticket_notes:
    #                     self._logger.info(
    #                         f"Checking watermark for Dispatch [{dispatch_number}] in ticket_id: {ticket_id}")
    #
    #                     self._logger.info(ticket_notes)
    #
    #                     watermark_found = UtilsRepository.get_first_element_matching(
    #                         iterable=ticket_notes,
    #                         condition=lambda note: self.DISPATCH_REQUESTED_WATERMARK in note.get('noteValue'),
    #                         fallback=None
    #                     )
    #                     confirmed_note_found = UtilsRepository.get_first_element_matching(
    #                         iterable=ticket_notes,
    #                         condition=lambda note: self.DISPATCH_CONFIRMED_WATERMARK in note.get('noteValue'),
    #                         fallback=None
    #                     )
    #                     tech_on_site_note_found = UtilsRepository.get_first_element_matching(
    #                         iterable=ticket_notes,
    #                         condition=lambda note: self.DISPATCH_FIELD_ENGINEER_ON_SITE_WATERMARK in note.get(
    #                             'noteValue'),
    #                         fallback=None
    #                     )
    #                     repair_completed_note_found = UtilsRepository.get_first_element_matching(
    #                         iterable=ticket_notes,
    #                         condition=lambda note: self.DISPATCH_REPAIR_COMPLETED_WATERMARK in note.get(
    #                             'noteValue'),
    #                         fallback=None
    #                     )
    #                     self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
    #                                       f"watermark_found: {watermark_found} "
    #                                       f"confirmed_note_found: {confirmed_note_found} "
    #                                       f"tech_on_site_note_found: {tech_on_site_note_found} "
    #                                       f"repair_completed_note_found: {repair_completed_note_found}")
    #                     if watermark_found is not None:
    #                         if confirmed_note_found is not None and tech_on_site_note_found is not None \
    #                                 and repair_completed_note_found is not None:
    #                             self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
    #                                               f"- already has a repair completed note")
    #                             # TODO: notify slack
    #                         else:
    #                             self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
    #                                               f"- Adding repair completed note")
    #                             time_of_dispatch = dispatch.get('Local_Time_of_Dispatch')
    #                             am_pm_of_dispatch = ''
    #                             if time_of_dispatch is not None and time_of_dispatch != 'None':
    #                                 time_of_dispatch = time_of_dispatch[:-2]
    #                                 am_pm_of_dispatch = time_of_dispatch[-2:]
    #
    #                             note_data = {
    #                                 'vendor': 'LIT',
    #                                 'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
    #                                 'time_of_dispatch': time_of_dispatch,
    #                                 'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
    #                                 'ticket_id': ticket_id
    #                             }
    #
    #                             note = lit_get_repair_completed_note(note_data)
    #                             # if self._config.DISPATCH_MONITOR_CONFIG['environment'] == 'production':
    #                             append_note_response = await self._bruin_repository.append_note_to_ticket(
    #                                                               ticket_id, note)
    #                             append_note_response_status = append_note_response['status']
    #                             append_note_response_body = append_note_response['body']
    #                             if append_note_response_status not in range(200, 300):
    #                                 self._logger.info(f"Note: `{note}` "
    #                                                   f"Dispatch: {dispatch_number} "
    #                                                   f"Ticket_id: {ticket_id} - Not appended")
    #                                 return
    #                             self._logger.info(f"Note: `{note}` "
    #                                               f"Dispatch: {dispatch_number} "
    #                                               f"Ticket_id: {ticket_id} - Appended")
    #                             self._logger.info(
    #                                 f"Note appended. Response {append_note_response_body}")
    #                     else:
    #                         self._logger.warn(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
    #                                           f"- Watermark not found, ticket does not belong to us")
    #     except Exception as ex:
    #         self._logger.error(f"Error: {ex}")
    #
    #     stop = perf_counter()
    #     self._logger.info(f"Monitor Tech on Site Dispatches took: {(stop - start) / 60} minutes")
