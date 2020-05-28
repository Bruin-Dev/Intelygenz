import asyncio
from datetime import datetime
from time import perf_counter
from collections import defaultdict

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone

from application.repositories.utils_repository import UtilsRepository
from application.templates.lit_dispatch_confirmed import lit_get_dispatch_confirmed_note
from application.templates.lit_tech_on_site import lit_get_tech_on_site_note
from application.templates.lit_repair_complete import lit_get_repair_completed_note


class LitDispatchMonitor:
    def __init__(self, config, redis_client, event_bus, scheduler, logger, lit_repository, bruin_repository):
        self._config = config
        self._redis_client = redis_client
        self._scheduler = scheduler
        self._event_bus = event_bus
        self._logger = logger
        self._lit_repository = lit_repository
        self._bruin_repository = bruin_repository

        self.MAIN_WATERMARK = '#*Automation Engine*#'
        self.DISPATCH_REQUESTED_WATERMARK = 'Dispatch Management - Dispatch Requested'
        self.DISPATCH_CONFIRMED_WATERMARK = 'Dispatch Management - Dispatch Confirmed'
        self.DISPATCH_FIELD_ENGINEER_ON_SITE_WATERMARK = 'Dispatch Management - Field Engineer On Site'
        self.DISPATCH_REPAIR_COMPLETED_WATERMARK = 'Dispatch Management - Repair Completed'

        # Dispatch Status
        self.DISPATCH_NEW = 'New Dispatch'
        self.DISPATCH_REQUESTED = 'Dispatch Requested'  # TODO: Check if this one exists
        self.DISPATCH_CONFIRMED = 'Request Confirmed'
        self.DISPATCH_FIELD_ENGINEER_ON_SITE = 'Tech Arrived'
        self.DISPATCH_REPAIR_COMPLETED = 'Repair Completed'
        self._dispatch_statuses = [
            self.DISPATCH_NEW,
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

        try:
            self._scheduler.add_job(self._lit_dispatch_monitoring_process, 'interval',
                                    seconds=self._config.DISPATCH_MONITOR_CONFIG['jobs_intervals']['dispatch_monitor'],
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_service_outage_monitor_process')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of Service Dispatch Monitoring. Reason: {conflict}')

    def _is_dispatch_confirmed(self, dispatch):
        # A confirmed dispatch must have status: 'Request Confirmed'
        # and this two fields filled Tech_First_Name, Tech_Mobile_Number
        return dispatch is not None and dispatch.get('Dispatch_Status') == self.DISPATCH_CONFIRMED \
               and dispatch.get("Tech_First_Name") is not None \
               and len(dispatch.get("Tech_First_Name")) > 0 \
               and dispatch.get("Tech_Mobile_Number") is not None \
               and len(dispatch.get("Tech_Mobile_Number")) > 0

    def _is_tech_on_site(self, dispatch):
        # Filter tech on site dispatches
        # Dispatch Confirmed --> Field Engineer On Site:
        # Tech_Arrived_On_Site is set to true and Time_of_Check_In is set.
        # Bruin Note:*#Automation Engine#*Dispatch Management - Field Engineer On Site<FE Name> has arrived
        return dispatch is not None and dispatch.get('Dispatch_Status') == self.DISPATCH_FIELD_ENGINEER_ON_SITE \
               and dispatch.get("Tech_Arrived_On_Site") is not None \
               and dispatch.get("Tech_Arrived_On_Site") is True \
               and dispatch.get("Time_of_Check_In") is not None \
               and len(dispatch.get("Time_of_Check_In")) > 0  # TODO: recheck

    def _is_repair_completed(self, dispatch):
        # Field Engineer On Site --> Repair Completed: Tech_Off_Site is set to true and Time_of_Check_Out is set.
        # Bruin Note:
        # *#Automation Engine#*
        # Dispatch Management - Repair Completed
        #
        # Dispatch request for Mar 16, 2020 @ 07:00 AM Eastern has been completed.
        # Reference: 4585231
        return dispatch is not None and dispatch.get('Dispatch_Status') == self.DISPATCH_REPAIR_COMPLETED \
               and dispatch.get("Tech_Arrived_On_Site") is not None \
               and dispatch.get("Tech_Arrived_On_Site") is True \
               and dispatch.get("Time_of_Check_In") is not None \
               and len(dispatch.get("Time_of_Check_In")) > 0 \
               and dispatch.get("Time_of_Check_Out") is not None \
               and len(dispatch.get("Time_of_Check_Out")) > 0  # TODO: recheck

    def _is_valid_ticket_id(self, ticket_id):
        # Check ticket id format for example: '4663397|IW24654081'
        # Bruin ticket ID like 712637/IW76236 and 123-3123 are likely to be from other
        # kind of tickets (like new installations), thus other teams that are not his,
        # 4485610(Order)/4520284(Port)
        # Discard All with more than one ticket
        try:
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
        except Exception as ex:
            self._logger.error(f"Error while validating ticket id: {ticket_id}: {ex}")
            return False

    def _get_dispatches_splitted_by_status(self, dispatches):
        dispatches_splitted_by_status = defaultdict(list)
        for dispatch in dispatches:
            if dispatch.get('Dispatch_Status') in self._dispatch_statuses:
                dispatches_splitted_by_status[dispatch.get('Dispatch_Status')].append(dispatch)
        return dispatches_splitted_by_status

    async def _lit_dispatch_monitoring_process(self):
        try:
            start = perf_counter()
            self._logger.info(f"Starting Dispatch Monitor Process...")

            response_lit_dispatches = await self._lit_repository.get_all_dispatches()
            response_lit_dispatches_status = response_lit_dispatches.get('status')
            response_lit_dispatches_body = response_lit_dispatches.get('body')

            if response_lit_dispatches_status not in range(200, 300):
                self._logger.error("Error getting all dispatches from LIT")
                return

            if response_lit_dispatches_body is None \
                    or 'Status' not in response_lit_dispatches_body \
                    or response_lit_dispatches_body['Status'] != "Success" \
                    or 'DispatchList' not in response_lit_dispatches_body \
                    or response_lit_dispatches_body['DispatchList'] is None:
                self._logger.error(f"[get_all_dispatches] Could not retrieve all dispatches, "
                                   f"reason: {response_lit_dispatches_body}")
                return

            lit_dispatches = response_lit_dispatches_body.get('DispatchList', [])
            dispatches_splitted_by_status = self._get_dispatches_splitted_by_status(lit_dispatches)

            self._logger.info(f"Splitted by status: "
                              f"{list(dispatches_splitted_by_status.keys())}")

            monitor_tasks = [
                self._monitor_confirmed_dispatches(dispatches_splitted_by_status[self.DISPATCH_CONFIRMED]),
                self._monitor_tech_on_site_dispatches(dispatches_splitted_by_status[self.DISPATCH_FIELD_ENGINEER_ON_SITE]),
                self._monitor_repair_completed(dispatches_splitted_by_status[self.DISPATCH_REPAIR_COMPLETED])
            ]

            start_monitor_tasks = perf_counter()
            await asyncio.gather(*monitor_tasks, return_exceptions=True)
            stop_monitor_tasks = perf_counter()
            self._logger.info(f"All monitor tasks finished: "
                              f"{(stop_monitor_tasks - start_monitor_tasks) / 60} minutes")

            stop = perf_counter()
            self._logger.info(f"Elapsed time processing all dispatches cache: {(stop - start) / 60} minutes")
        except Exception as ex:
            self._logger.error(f"Error: {ex}")

    async def _monitor_confirmed_dispatches(self, confirmed_dispatches):
        try:
            start = perf_counter()

            self._logger.info(f"Dispatches to process before filter {len(confirmed_dispatches)}")
            confirmed_dispatches = list(filter(self._is_dispatch_confirmed, confirmed_dispatches))
            self._logger.info(f"Total confirmed dispatches after filter: {len(confirmed_dispatches)}")

            for dispatch in confirmed_dispatches:
                dispatch_number = dispatch.get('Dispatch_Number', None)
                ticket_id = dispatch.get('MetTel_Bruin_TicketID', None)

                self._logger.info(f"Dispatch: [{dispatch_number}] ticket id for {ticket_id}")
                if not self._is_valid_ticket_id(ticket_id):
                    self._logger.info(f"Dispatch: [{dispatch_number}] ticket id for {ticket_id} discarded.")
                    continue
                self._logger.info(f"Dispatch: [{dispatch_number}] Determined final ticket id for {ticket_id}")

                if ticket_id is not None:
                    self._logger.info(f"Getting details for ticket [{ticket_id}]")

                    response = await self._bruin_repository.get_ticket_details(ticket_id)
                    response_status = response['status']
                    response_body = response['body']

                    ticket_notes = response_body.get('ticketNotes')

                    if response_status not in range(200, 300):
                        self._logger.error(f"Error: Dispatch [{dispatch_number}] "
                                           f"Get ticket details for ticket {ticket_id}: "
                                           f"{response_body}")
                        continue

                    if dispatch_number and ticket_notes:
                        self._logger.info(
                            f"Checking watermark for Dispatch [{dispatch_number}] in ticket_id: {ticket_id}")

                        self._logger.info(ticket_notes)
                        watermark_found = UtilsRepository.get_first_element_matching(
                            iterable=ticket_notes,
                            condition=lambda note: self.DISPATCH_REQUESTED_WATERMARK in note.get('noteValue'),
                            fallback=None
                        )
                        confirmed_note_found = UtilsRepository.get_first_element_matching(
                            iterable=ticket_notes,
                            condition=lambda note: self.DISPATCH_CONFIRMED_WATERMARK in note.get('noteValue'),
                            fallback=None
                        )

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"watermark_found: {watermark_found} "
                                          f"confirmed_note_found: {confirmed_note_found}")
                        if watermark_found is not None:
                            if confirmed_note_found is not None:
                                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                  f"- already has a confirmed note")
                                # TODO: notify slack
                            else:
                                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                  f"- Adding confirm note")
                                time_of_dispatch = dispatch.get('Local_Time_of_Dispatch')
                                am_pm_of_dispatch = ''
                                if time_of_dispatch is not None and time_of_dispatch != 'None':
                                    time_of_dispatch = time_of_dispatch[:-2]
                                    am_pm_of_dispatch = time_of_dispatch[-2:]

                                note_data = {
                                    'vendor': 'LIT',
                                    'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
                                    'time_of_dispatch': time_of_dispatch,
                                    'am_pm': am_pm_of_dispatch,
                                    'time_zone': dispatch.get('Time_Zone_Local'),
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
                                    return
                                self._logger.info(f"Note: `{note}` "
                                                  f"Dispatch: {dispatch_number} "
                                                  f"Ticket_id: {ticket_id} - Appended")
                                self._logger.info(
                                    f"Note appended. Response {append_note_response_body}")
                        else:
                            self._logger.warn(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- Watermark not found, ticket does not belong to us")
        except Exception as ex:
            self._logger.error(f"Error: {ex}")

        stop = perf_counter()
        self._logger.info(f"Monitor Confirmed Dispatches took: {(stop - start) / 60} minutes")

    async def _monitor_tech_on_site_dispatches(self, tech_on_site_dispatches):
        try:
            start = perf_counter()
            self._logger.info(f"Dispatches to process before filter {len(tech_on_site_dispatches)}")
            tech_on_site_dispatches = list(filter(self._is_tech_on_site, tech_on_site_dispatches))
            self._logger.info(f"Dispatches to process after filter {len(tech_on_site_dispatches)}")
            for dispatch in tech_on_site_dispatches:
                dispatch_number = dispatch.get('Dispatch_Number', None)
                ticket_id = dispatch.get('MetTel_Bruin_TicketID', None)

                self._logger.info(f"Dispatch: [{dispatch_number}] ticket id for {ticket_id}")
                if not self._is_valid_ticket_id(ticket_id):
                    self._logger.info(f"Dispatch: [{dispatch_number}] ticket id for {ticket_id} discarded.")
                    continue
                self._logger.info(f"Determined final ticket id for {ticket_id}")

                if ticket_id is not None:
                    self._logger.info(f"Getting details for ticket [{ticket_id}]")

                    response = await self._get_ticket_details(ticket_id)
                    response_status = response['status']
                    response_body = response['body']

                    ticket_notes = response_body.get('ticketNotes')

                    if response_status not in range(200, 300):
                        self._logger.error(f"Dispatch [{dispatch_number}] "
                                           f"get ticket details for ticket {ticket_id}")
                        # TODO: notify slack
                        continue

                    if dispatch_number and ticket_notes:
                        self._logger.info(
                            f"Checking watermark for Dispatch [{dispatch_number}] in ticket_id: {ticket_id}")

                        self._logger.info(ticket_notes)

                        watermark_found = UtilsRepository.get_first_element_matching(
                            iterable=ticket_notes,
                            condition=lambda note: self.DISPATCH_REQUESTED_WATERMARK in note.get('noteValue'),
                            fallback=None
                        )
                        confirmed_note_found = UtilsRepository.get_first_element_matching(
                            iterable=ticket_notes,
                            condition=lambda note: self.DISPATCH_CONFIRMED_WATERMARK in note.get('noteValue'),
                            fallback=None
                        )
                        tech_on_site_note_found = UtilsRepository.get_first_element_matching(
                            iterable=ticket_notes,
                            condition=lambda note: self.DISPATCH_FIELD_ENGINEER_ON_SITE_WATERMARK in note.get('noteValue'),
                            fallback=None
                        )

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"watermark_found: {watermark_found} "
                                          f"confirmed_note_found: {confirmed_note_found} "
                                          f"tech_on_site_note_found: {tech_on_site_note_found}")
                        if watermark_found is not None:
                            if confirmed_note_found is not None and tech_on_site_note_found is not None:
                                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                  f"- already has a tech on site note")
                                # TODO: notify slack
                            else:
                                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                  f"- Adding tech on site note")
                                note_data = {
                                    'vendor': 'LIT',
                                    'field_engineer_name': dispatch.get('Tech_First_Name')
                                }
                                note = lit_get_tech_on_site_note(note_data)
                                # if self._config.DISPATCH_MONITOR_CONFIG['environment'] == 'production':
                                append_note_response = await self._bruin_repository.append_note_to_ticket(ticket_id, note)
                                append_note_response_status = append_note_response['status']
                                append_note_response_body = append_note_response['body']
                                if append_note_response_status not in range(200, 300):
                                    self._logger.info(f"Note: `{note}` "
                                                      f"Dispatch: {dispatch_number} "
                                                      f"Ticket_id: {ticket_id} - Not appended")
                                    return
                                self._logger.info(f"Note: `{note}` "
                                                  f"Dispatch: {dispatch_number} "
                                                  f"Ticket_id: {ticket_id} - Appended")
                                self._logger.info(
                                    f"Note appended. Response {append_note_response_body}")
                        else:
                            self._logger.warn(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- Watermark not found, ticket does not belong to us")
        except Exception as ex:
            self._logger.error(f"Error: {ex}")

        stop = perf_counter()
        self._logger.info(f"Monitor Tech on Site Dispatches took: {(stop - start) / 60} minutes")

    async def _monitor_repair_completed(self, dispatches_completed):
        try:
            start = perf_counter()
            # Filter repair completed dispatches
            self._logger.info(f"Dispatches to process before filter {len(dispatches_completed)}")
            dispatches_completed = list(filter(self._is_repair_completed, dispatches_completed))
            self._logger.info(f"Dispatches to process after filter {len(dispatches_completed)}")
            for dispatch in dispatches_completed:
                dispatch_number = dispatch.get('Dispatch_Number', None)
                ticket_id = dispatch.get('MetTel_Bruin_TicketID', None)

                self._logger.info(f"Dispatch: [{dispatch_number}] ticket id for {ticket_id}")
                if not self._is_valid_ticket_id(ticket_id):
                    self._logger.info(f"Dispatch: [{dispatch_number}] ticket id for {ticket_id} discarded.")
                    continue

                if ticket_id is not None:
                    self._logger.info(f"Getting details for ticket [{ticket_id}]")

                    response = await self._get_ticket_details(ticket_id)
                    response_status = response['status']
                    response_body = response['body']

                    ticket_notes = response_body.get('ticketNotes')

                    if response_status not in range(200, 300):
                        self._logger.error(f"Dispatch [{dispatch_number}] get ticket details for ticket {ticket_id}")
                        # TODO: notify slack
                        continue

                    if dispatch_number and ticket_notes:
                        self._logger.info(
                            f"Checking watermark for Dispatch [{dispatch_number}] in ticket_id: {ticket_id}")

                        self._logger.info(ticket_notes)

                        watermark_found = UtilsRepository.get_first_element_matching(
                            iterable=ticket_notes,
                            condition=lambda note: self.DISPATCH_REQUESTED_WATERMARK in note.get('noteValue'),
                            fallback=None
                        )
                        confirmed_note_found = UtilsRepository.get_first_element_matching(
                            iterable=ticket_notes,
                            condition=lambda note: self.DISPATCH_CONFIRMED_WATERMARK in note.get('noteValue'),
                            fallback=None
                        )
                        tech_on_site_note_found = UtilsRepository.get_first_element_matching(
                            iterable=ticket_notes,
                            condition=lambda note: self.DISPATCH_FIELD_ENGINEER_ON_SITE_WATERMARK in note.get(
                                'noteValue'),
                            fallback=None
                        )
                        repair_completed_note_found = UtilsRepository.get_first_element_matching(
                            iterable=ticket_notes,
                            condition=lambda note: self.DISPATCH_REPAIR_COMPLETED_WATERMARK in note.get(
                                'noteValue'),
                            fallback=None
                        )
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"watermark_found: {watermark_found} "
                                          f"confirmed_note_found: {confirmed_note_found} "
                                          f"tech_on_site_note_found: {tech_on_site_note_found} "
                                          f"repair_completed_note_found: {repair_completed_note_found}")
                        if watermark_found is not None:
                            if confirmed_note_found is not None and tech_on_site_note_found is not None \
                                    and repair_completed_note_found is not None:
                                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                  f"- already has a repair completed note")
                                # TODO: notify slack
                            else:
                                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                  f"- Adding repair completed note")
                                time_of_dispatch = dispatch.get('Local_Time_of_Dispatch')
                                am_pm_of_dispatch = ''
                                if time_of_dispatch is not None and time_of_dispatch != 'None':
                                    time_of_dispatch = time_of_dispatch[:-2]
                                    am_pm_of_dispatch = time_of_dispatch[-2:]

                                note_data = {
                                    'vendor': 'LIT',
                                    'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
                                    'time_of_dispatch': time_of_dispatch,
                                    'am_pm': am_pm_of_dispatch,
                                    'time_zone': dispatch.get('Time_Zone_Local'),
                                    'ticket_id': ticket_id
                                }

                                note = lit_get_repair_completed_note(note_data)
                                # if self._config.DISPATCH_MONITOR_CONFIG['environment'] == 'production':
                                append_note_response = await self._bruin_repository.append_note_to_ticket(ticket_id, note)
                                append_note_response_status = append_note_response['status']
                                append_note_response_body = append_note_response['body']
                                if append_note_response_status not in range(200, 300):
                                    self._logger.info(f"Note: `{note}` "
                                                      f"Dispatch: {dispatch_number} "
                                                      f"Ticket_id: {ticket_id} - Not appended")
                                    return
                                self._logger.info(f"Note: `{note}` "
                                                  f"Dispatch: {dispatch_number} "
                                                  f"Ticket_id: {ticket_id} - Appended")
                                self._logger.info(
                                    f"Note appended. Response {append_note_response_body}")
                        else:
                            self._logger.warn(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- Watermark not found, ticket does not belong to us")
        except Exception as ex:
            self._logger.error(f"Error: {ex}")

        stop = perf_counter()
        self._logger.info(f"Monitor Tech on Site Dispatches took: {(stop - start) / 60} minutes")
