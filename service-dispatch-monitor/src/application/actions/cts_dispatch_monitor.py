import asyncio
from datetime import datetime
from time import perf_counter
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

        # Dispatch Notes watermarks
        self.MAIN_WATERMARK = '#*Automation Engine*#'
        self.DISPATCH_REQUESTED_WATERMARK = 'Dispatch Management - Dispatch Requested'
        self.DISPATCH_CONFIRMED_WATERMARK = 'Dispatch Management - Dispatch Confirmed'

    async def start_monitoring_job(self, exec_on_start):
        self._logger.info('Scheduling Service Dispatch Monitor job for CTS...')
        next_run_time = undefined
        if exec_on_start:
            tz = timezone(self._config.DISPATCH_MONITOR_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('Service Outage Monitor job is going to be executed immediately')

        self._scheduler.add_job(self._cts_dispatch_monitoring_process, 'interval',
                                minutes=self._config.DISPATCH_MONITOR_CONFIG['jobs_intervals']['lit_dispatch_monitor'],
                                next_run_time=next_run_time, replace_existing=False,
                                id='_service_dispatch_monitor_lit_process')

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
                    or 'Status' not in response_cts_dispatches_body \
                    or response_cts_dispatches_body['Status'] != "Success" \
                    or 'DispatchList' not in response_cts_dispatches_body \
                    or response_cts_dispatches_body['DispatchList'] is None:
                self._logger.error(f"[get_all_dispatches] Could not retrieve all dispatches, "
                                   f"reason: {response_cts_dispatches_body}")
                err_msg = f'An error occurred retrieving all dispatches from CTS.'
                await self._notifications_repository.send_slack_message(err_msg)
                return

            cts_dispatches = response_cts_dispatches_body.get('DispatchList', [])
            # TODO: split by status
            # dispatches_splitted_by_status = self._get_dispatches_splitted_by_status(cts_dispatches)
            dispatches_splitted_by_status = cts_dispatches

            self._logger.info(f"Splitted by status: {list(dispatches_splitted_by_status.keys())}")

            monitor_tasks = [
                self._monitor_confirmed_and_pending_dispatches(dispatches_splitted_by_status)
            ]

            start_monitor_tasks = perf_counter()
            await asyncio.gather(*monitor_tasks, return_exceptions=True)
            stop_monitor_tasks = perf_counter()
            self._logger.info(f"[CTS] All monitor tasks finished: "
                              f"{(stop_monitor_tasks - start_monitor_tasks) / 60} minutes")

            stop = perf_counter()
            self._logger.info(f"[CTS] Elapsed time processing all dispatches cache: {(stop - start) / 60} minutes")
        except Exception as ex:
            self._logger.error(f"Error: {ex}")

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

    async def _monitor_confirmed_and_pending_dispatches(self, confirmed_dispatches):
        try:
            start = perf_counter()
            self._logger.info(f"Dispatches to process before filter {len(confirmed_dispatches)}")
            confirmed_dispatches = list(filter(self._is_dispatch_confirmed, confirmed_dispatches))
            self._logger.info(f"Total confirmed dispatches after filter: {len(confirmed_dispatches)}")

            for dispatch in confirmed_dispatches:
                try:
                    dispatch_number = dispatch.get('Dispatch_Number', None)
                    ticket_id = dispatch.get('MetTel_Bruin_TicketID', None)

                    self._logger.info(f"Processing Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - {dispatch}")

                    if ticket_id is None or not self._is_valid_ticket_id(ticket_id) or dispatch_number is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} discarded.")
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

                    watermark_found = UtilsRepository.find_note(ticket_notes, self.MAIN_WATERMARK)
                    requested_watermark_found = UtilsRepository.find_note(ticket_notes,
                                                                          self.DISPATCH_REQUESTED_WATERMARK)
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"main_watermark_found: {watermark_found} "
                                      f"requested_watermark_found: {requested_watermark_found} ")

                except Exception as ex:
                    err_msg = f"Error: Dispatch [{dispatch_number}] in ticket_id: {ticket_id} - {dispatch}"
                    self._logger.error(f"Error: {ex}")
                    await self._notifications_repository.send_slack_message(err_msg)
                    continue
        except Exception as ex:
            err_msg = f"Error: _monitor_confirmed_and_pending_dispatches - {ex}"
            self._logger.error(f"Error: {ex}")
            await self._notifications_repository.send_slack_message(err_msg)
        stop = perf_counter()
        self._logger.info(f"Monitor Confirmed Dispatches took: {(stop - start) / 60} minutes")
