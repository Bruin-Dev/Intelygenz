import time
import json
from datetime import datetime
from time import perf_counter

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone
from shortuuid import uuid

from application.templates.lit_dispatch_confirmed import lit_get_dispatch_confirmed_note


class LitDispatchMonitor:
    def __init__(self, config, redis_client, event_bus, scheduler, logger):
        self._config = config
        self._redis_client = redis_client
        self._scheduler = scheduler
        self._event_bus = event_bus
        self._logger = logger
        self.MAIN_WATERMARK = '#*Automation Engine*#'

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

    def _exists_watermark_in_ticket(self, watermark, ticket_notes):
        watermark_found = False

        for ticket_note_data in ticket_notes:
            self._logger.info(ticket_note_data)
            ticket_note = ticket_note_data.get('noteValue')

            if self.MAIN_WATERMARK in ticket_note and watermark in ticket_note:
                watermark_found = True
                break

        return watermark_found

    async def _lit_dispatch_monitoring_process(self):
        start = perf_counter()
        self._logger.info(f"[dispatch_monitoring_process] Getting all dispatches...")

        payload = {"request_id": uuid(), "body": {}}
        response = await self._event_bus.rpc_request("lit.dispatch.get", payload, timeout=30)

        if 'body' not in response \
                or 'Status' not in response['body'] \
                or 'DispatchList' not in response['body'] \
                or response['body']['Status'] != "Success" \
                or response['body']['DispatchList'] is None:
            self._logger.error(f"Could not retrieve all dispatches, reason: {response['body']}")
            # TODO: notify slack
            return

        self._logger.info(f"[dispatch_monitoring_process] "
                          f"Retrieved {len(response['body']['DispatchList'])} dispatches.")
        lit_dispatches = response['body']['DispatchList']

        # Filter confirmed dispatches
        # A confirmed dispatch must have status: 'Request Confirmed'
        # and this two fields filled Tech_First_Name, Tech_Mobile_Number
        confirmed_dispatches = [
            dispatch
            for dispatch in lit_dispatches
            if dispatch.get('Dispatch_Status') == 'Request Confirmed'
            if dispatch.get("Tech_First_Name") is not None
            if len(dispatch.get("Tech_First_Name")) > 0
            if dispatch.get("Tech_Mobile_Number") is not None
            if len(dispatch.get("Tech_Mobile_Number")) > 0
        ]
        for dispatch in confirmed_dispatches:
            # TODO: post confirmed note
            ticket_id = dispatch.get('MetTel_Bruin_TicketID')
            # TODO: remove
            ticket_id = '4661755'
            if ticket_id:
                self._logger.info(f"[dispatch_monitoring_process] "
                                  f"Getting details for ticket [{ticket_id}]")
                response = await self._get_ticket_details(ticket_id)
                response_status = response['status']
                response_body = response['body']

                dispatch_number = dispatch.get('Dispatch_Number')
                ticket_notes = response_body.get('ticketNotes')

                if response_status not in range(200, 300):
                    self._logger.error(f"Dispatch [{dispatch_number}] "
                                       f"get ticket details for ticket {ticket_id}")
                    # TODO: notify slack
                    continue

                if dispatch_number and ticket_notes:
                    self._logger.info(f"Checking watermark for Dispatch [{dispatch_number}] in ticket_id: {ticket_id}")

                    self._logger.info(ticket_notes)

                    watermark_found = self._exists_watermark_in_ticket(
                        'Dispatch Management - Dispatch Requested', ticket_notes)
                    confirmed_note_found = self._exists_watermark_in_ticket(
                        'Dispatch Management - Dispatch Confirmed', ticket_notes)

                    if watermark_found is True:
                        if confirmed_note_found is True:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- already has a confirmed note")
                            # TODO: notify slack
                        else:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- Adding confirm note")
                            time_of_dispatch = dispatch.get('Local_Time_of_Dispatch')
                            ampm_of_dispatch = ''
                            if time_of_dispatch is not None and time_of_dispatch != 'None':
                                time_of_dispatch = time_of_dispatch[:-2]
                                ampm_of_dispatch = time_of_dispatch[-2:]

                            note_data = {
                                'vendor': 'LIT',
                                'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
                                'time_of_dispatch': time_of_dispatch,
                                'am_pm': ampm_of_dispatch,
                                'time_zone': dispatch.get('Time_Zone_Local'),
                                'tech_name': dispatch.get('tech_name'),
                                'tech_phone': dispatch.get('tech_phone')
                            }
                            note = lit_get_dispatch_confirmed_note(note_data)
                            append_note_response = await self._append_note_to_ticket(ticket_id, note)
                            append_note_response_status = append_note_response['status']
                            append_note_response_body = append_note_response['body']
                            if append_note_response_status not in range(200, 300):
                                self._logger.info(f"[process_note] Note: `{note}` Dispatch: {dispatch_number} "
                                                  f"Ticket_id: {ticket_id} - Not appended")
                                return
                            self._logger.info(f"[process_note] Note: `{note}` Dispatch: {dispatch_number} "
                                              f"Ticket_id: {ticket_id} - Appended")
                            self._logger.info(f"[process_note] Note appended. Response {append_note_response_body}")
                    else:
                        self._logger.warn(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- Watermark not found, ticket does not belong to us")

        stop = perf_counter()
        self._logger.info(f"[dispatch_monitoring_process] Elapsed time processing hosts with cache"
                          f": {(stop - start) / 60} minutes")

    async def _get_ticket_details(self, ticket_id):
        ticket_request_msg = {'request_id': uuid(),
                              'body': {'ticket_id': ticket_id}}
        ticket = await self._event_bus.rpc_request("bruin.ticket.details.request", ticket_request_msg, timeout=30)
        return ticket

    async def _append_note_to_ticket(self, ticket_id, ticket_note):
        append_note_to_ticket_request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'note': ticket_note,
            },
        }

        append_ticket_to_note = await self._event_bus.rpc_request(
            "bruin.ticket.note.append.request", append_note_to_ticket_request, timeout=15
        )
        return append_ticket_to_note
