import asyncio
import time
import os

from datetime import datetime
from typing import List
from typing import Set

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone
from tenacity import retry, wait_exponential, stop_after_delay

TNBA_NOTE_APPENDED_SUCCESS_MSG = (
    'TNBA note appended to ticket {ticket_id} and detail {detail_id} (serial: {serial_number}) '
    'with prediction: {prediction}. Details at app.bruin.com/t/{ticket_id}'
)


class TNBAMonitor:
    def __init__(self, event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                 customer_cache_repository, bruin_repository, prediction_repository,
                 notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._t7_repository = t7_repository
        self._ticket_repository = ticket_repository
        self._customer_cache_repository = customer_cache_repository
        self._bruin_repository = bruin_repository
        self._prediction_repository = prediction_repository
        self._notifications_repository = notifications_repository

        self.__reset_customer_cache()
        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['semaphore'])

    def __reset_customer_cache(self):
        self._customer_cache = []

    async def start_tnba_automated_process(self, exec_on_start=False):
        self._logger.info('Scheduling TNBA automated process job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz)
            self._logger.info('TNBA automated process job is going to be executed immediately')

        try:
            self._scheduler.add_job(self._run_tickets_polling, 'interval',
                                    seconds=self._config.MONITORING_INTERVAL_SECONDS,
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_run_tickets_polling')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of TNBA automated process job. Reason: {conflict}')

    async def _run_tickets_polling(self):
        self.__reset_customer_cache()

        self._logger.info('Starting TNBA process...')

        customer_cache_response = await self._customer_cache_repository.get_cache_for_tnba_monitoring()
        if customer_cache_response['status'] not in range(200, 300) or customer_cache_response['status'] == 202:
            return

        self._customer_cache = customer_cache_response['body']

        start_time = time.time()

        self._logger.info('Getting all open tickets for all customers...')
        open_tickets = await self._get_all_open_tickets_with_details_for_monitored_companies()
        self._logger.info(
            f'Got {len(open_tickets)} open tickets for all customers. '
            f'Filtering them (and their details) to get only the ones under the device list')
        relevant_open_tickets = self._filter_tickets_and_details_related_to_edges_under_monitoring(open_tickets)
        self._logger.info(
            f'Got {len(relevant_open_tickets)} relevant tickets for all customers. '
            f'Cleaning them up to exclude all invalid notes...'
        )
        relevant_open_tickets = self._filter_invalid_notes_in_tickets(relevant_open_tickets)

        self._logger.info('Splitting tickets in tickets with and without TNBA notes...')
        tickets_with_tnba, tickets_without_tnba = self._distinguish_tickets_with_and_without_tnba(relevant_open_tickets)

        self._logger.info(f'Tickets split successfully. '
                          f'Tickets with TNBA: {len(tickets_with_tnba)}. '
                          f'Tickets without TNBA: {len(tickets_without_tnba)}. '
                          f'Processing both ticket sets...')
        await asyncio.gather(
            self._process_tickets_with_tnba(tickets_with_tnba),
            self._process_tickets_without_tnba(tickets_without_tnba),
        )

        end_time = time.time()
        self._logger.info(f'TNBA process finished! Took {(end_time - start_time) // 60} minutes.')

    async def _get_all_open_tickets_with_details_for_monitored_companies(self):
        open_tickets = []

        bruin_clients_ids: Set[int] = set(elem['bruin_client_info']['client_id'] for elem in self._customer_cache)
        tasks = [
            self._get_open_tickets_with_details_by_client_id(client_id, open_tickets)
            for client_id in bruin_clients_ids
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        return open_tickets

    async def _get_open_tickets_with_details_by_client_id(self, client_id, open_tickets):
        @retry(wait=wait_exponential(multiplier=self._config.NATS_CONFIG['multiplier'],
                                     min=self._config.NATS_CONFIG['min']),
               stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay']))
        async def get_open_tickets_with_details_by_client_id():
            async with self._semaphore:
                result = []

                open_outage_tickets_response = await self._bruin_repository.get_open_outage_tickets(client_id)
                open_outage_tickets_response_body = open_outage_tickets_response['body']
                open_outage_tickets_response_status = open_outage_tickets_response['status']
                if open_outage_tickets_response_status not in range(200, 300):
                    open_outage_tickets_response_body = []

                open_affecting_tickets_response = await self._bruin_repository.get_open_affecting_tickets(client_id)
                open_affecting_tickets_response_body = open_affecting_tickets_response['body']
                open_affecting_tickets_response_status = open_affecting_tickets_response['status']
                if open_affecting_tickets_response_status not in range(200, 300):
                    open_affecting_tickets_response_body = []

                all_open_tickets: list = open_outage_tickets_response_body + open_affecting_tickets_response_body
                open_tickets_ids = (ticket['ticketID'] for ticket in all_open_tickets)

                self._logger.info(f'Getting all opened tickets for Bruin customer {client_id}...')
                for ticket_id in open_tickets_ids:
                    ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
                    ticket_details_response_body = ticket_details_response['body']
                    ticket_details_response_status = ticket_details_response['status']

                    if ticket_details_response_status not in range(200, 300):
                        continue

                    ticket_details_list = ticket_details_response_body['ticketDetails']
                    if not ticket_details_list:
                        self._logger.info(f"Ticket {ticket_id} doesn't have any detail under ticketDetails key. "
                                          f"Skipping...")
                        continue

                    self._logger.info(f'Got details for ticket {ticket_id} of Bruin customer {client_id}!')

                    result.append({
                        'ticket_id': ticket_id,
                        'ticket_details': ticket_details_list,
                        'ticket_notes': ticket_details_response_body['ticketNotes'],
                    })

                self._logger.info(f'Finished getting all opened tickets for Bruin customer {client_id}!')
                for ticket_item in result:
                    open_tickets.append(ticket_item)

        try:
            await get_open_tickets_with_details_by_client_id()
        except Exception as e:
            self._logger.error(
                f"An error occurred while trying to get open tickets with details for Bruin client {client_id} -> {e}"
            )

    def _filter_tickets_and_details_related_to_edges_under_monitoring(self, tickets):
        serials_under_monitoring: Set[str] = set(elem['serial_number'] for elem in self._customer_cache)

        relevant_tickets = []
        for ticket in tickets:
            ticket_details = ticket['ticket_details']

            relevant_details = [
                detail
                for detail in ticket_details
                if detail['detailValue'] in serials_under_monitoring
            ]

            if not relevant_details:
                # Having no relevant details means the ticket is not relevant either
                continue

            relevant_tickets.append({
                'ticket_id': ticket['ticket_id'],
                'ticket_details': relevant_details,
                'ticket_notes': ticket['ticket_notes'],
            })

        return relevant_tickets

    def _filter_invalid_notes_in_tickets(self, tickets):
        sanitized_tickets = []

        for ticket in tickets:
            relevant_notes = [
                note
                for note in ticket['ticket_notes']
                if note['noteValue'] is not None
            ]

            sanitized_tickets.append({
                'ticket_id': ticket['ticket_id'],
                'ticket_details': ticket['ticket_details'],
                'ticket_notes': relevant_notes,
            })

        return sanitized_tickets

    def _distinguish_tickets_with_and_without_tnba(self, tickets) -> tuple:
        tickets_with_tnba = [
            ticket
            for ticket in tickets
            if self._ticket_repository.has_tnba_note(ticket['ticket_notes'])
        ]

        tickets_without_tnba = [
            ticket
            for ticket in tickets
            if ticket not in tickets_with_tnba
        ]

        return tickets_with_tnba, tickets_without_tnba

    async def _process_tickets_without_tnba(self, tickets: List[dict]):
        self._logger.info('Processing tickets without TNBA notes...')

        for ticket in tickets:
            ticket_id = ticket["ticket_id"]
            self._logger.info(f'Processing ticket {ticket_id} without TNBA notes...')

            task_history_response = await self._bruin_repository.get_ticket_task_history(ticket_id)
            task_history_response_body = task_history_response['body']
            task_history_response_status = task_history_response['status']
            if task_history_response_status not in range(200, 300):
                self._logger.error(
                    f'Error on _process_tickets_without_tnba getting ticket_task_history for ticket_id[{ticket_id}]'
                )
                continue

            ticket_rows_with_asset = [tr for tr in task_history_response_body if
                                      tr.get('Asset') and tr['Asset'] is not None]

            if len(ticket_rows_with_asset) == 0:
                self._logger.info(f'Skipped get_prediction for ticket_id[{ticket_id}] without assets...')
                continue

            t7_prediction_response = await self._t7_repository.get_prediction(ticket_id, task_history_response_body)
            t7_prediction_response_body = t7_prediction_response['body']
            t7_prediction_response_status = t7_prediction_response['status']
            if t7_prediction_response_status not in range(200, 300):
                continue

            tnba_notes: List[dict] = []
            slack_messages: List[str] = []
            available_options: List[dict] = []
            suggested_notes: List[dict] = []

            for ticket_detail in ticket['ticket_details']:
                ticket_detail_response = await self._process_ticket_detail_without_tnba(
                    ticket_id,
                    ticket_detail,
                    t7_prediction_response_body
                )

                if ticket_detail_response['tnba_note']:
                    tnba_notes.append(ticket_detail_response['tnba_note'])

                if ticket_detail_response['slack_message']:
                    slack_messages.append(ticket_detail_response['slack_message'])

                available_options.append(ticket_detail_response['available_options'])
                suggested_notes.append(ticket_detail_response['suggested_notes'])

            if not tnba_notes:
                self._logger.info(f'No TNBA notes were built for ticket {ticket_id}!')
            else:
                self._logger.info(f'Appending TNBA notes to ticket {ticket_id}...')
                append_notes_response = await self._bruin_repository.append_multiple_notes_to_ticket(
                    ticket_id, tnba_notes
                )
                append_notes_response_status = append_notes_response['status']
                if append_notes_response_status not in range(200, 300):
                    continue

                slack_message = os.linesep.join(slack_messages)
                await self._notifications_repository.send_slack_message(slack_message)

            await self._t7_repository.save_prediction(
                ticket_id,
                task_history_response_body,
                t7_prediction_response_body,
                available_options,
                suggested_notes
            )
            self._logger.info(f'Finished processing ticket without TNBA notes. ID: {ticket_id}')

        self._logger.info('Finished processing tickets without TNBA notes!')

    async def _process_ticket_detail_without_tnba(
            self,
            ticket_id,
            ticket_detail,
            t7_prediction_response_body
    ):

        ticket_detail_id = ticket_detail['detailID']
        self._logger.info(f'Processing detail {ticket_detail_id} of ticket {ticket_id}...')

        serial_number = ticket_detail['detailValue']

        response = {
            'tnba_note': None,
            'slack_message': None,
            'available_options': {
                'asset': serial_number,
                'available_options': None,
            },
            'suggested_notes': {
                'asset': serial_number,
                'suggested_note': None,
                'details': None,
            }
        }

        self._logger.info(
            f'Seeking predictions for ticket {ticket_id}, detail {ticket_detail_id} and serial {serial_number} '
            f'in the response received from T7 API...'
        )

        prediction_object_for_serial: dict = self._prediction_repository.find_prediction_object_by_serial(
            t7_prediction_response_body, serial_number
        )

        if not prediction_object_for_serial:
            msg = (
                f"No predictions were found for ticket {ticket_id}, detail {ticket_detail_id} and serial "
                f"{serial_number}!"
            )
            self._logger.info(msg)
            response['suggested_notes']['details'] = msg
            return response

        elif 'error' in prediction_object_for_serial.keys():
            msg = (
                f"Prediction for ticket {ticket_id}, detail {ticket_detail_id} and serial {serial_number} was "
                f"found but it contains an error from T7 API -> {prediction_object_for_serial['error']}"
            )
            self._logger.info(msg)
            await self._notifications_repository.send_slack_message(msg)
            response['suggested_notes']['details'] = msg
            return response

        self._logger.info(
            f'Found predictions for ticket {ticket_id}, detail {ticket_detail_id} and serial {serial_number}: '
            f'{prediction_object_for_serial}'
        )

        next_results_response = await self._bruin_repository.get_next_results_for_ticket_detail(
            ticket_id, ticket_detail_id, serial_number
        )
        next_results_response_body = next_results_response['body']
        next_results_response_status = next_results_response['status']
        if next_results_response_status not in range(200, 300):
            msg = f'Error getting next results ticket[{ticket_id}] detail[{ticket_detail_id}] serial [{serial_number}]'
            response['suggested_notes']['details'] = msg
            return response

        self._logger.info(
            f'Filtering predictions available in next results for ticket {ticket_id}, '
            f'detail {ticket_detail_id} and serial {serial_number}...'
        )
        predictions: list = prediction_object_for_serial['predictions']
        next_results: list = next_results_response_body['nextResults']
        response['available_options']['available_options'] = [result['resultName'].strip() for result in next_results]

        relevant_predictions = self._prediction_repository.filter_predictions_in_next_results(
            predictions, next_results
        )

        if not relevant_predictions:
            msg = (
                f"No predictions with name appearing in the next results were found for ticket {ticket_id}, "
                f"detail {ticket_detail_id} and serial {serial_number}!"
            )
            self._logger.info(msg)
            response['suggested_notes']['details'] = msg
            return response

        self._logger.info(
            f'Predictions available in next results found for ticket {ticket_id}, detail {ticket_detail_id} '
            f'and serial {serial_number}: {relevant_predictions}'
        )

        best_prediction: dict = self._prediction_repository.get_best_prediction(relevant_predictions)

        self._logger.info(
            f"Building TNBA note from predictions found for ticket {ticket_id}, detail {ticket_detail_id} "
            f"and serial {serial_number}..."
        )
        tnba_note: str = self._ticket_repository.build_tnba_note_from_prediction(best_prediction)

        if self._config.ENVIRONMENT == 'production':
            response['tnba_note'] = {
                'text': tnba_note,
                'detail_id': ticket_detail_id,
                'service_number': serial_number,
            }
            response['slack_message'] = TNBA_NOTE_APPENDED_SUCCESS_MSG.format(
                ticket_id=ticket_id, detail_id=ticket_detail_id,
                serial_number=serial_number, prediction=best_prediction['name'],
            )
            response['suggested_notes']['suggested_note'] = tnba_note
            return response
        elif self._config.ENVIRONMENT == 'dev':
            tnba_message = (
                f'TNBA note would have been appended to ticket {ticket_id} and detail {ticket_detail_id} '
                f'(serial: {serial_number}). Note: {tnba_note}. Details at app.bruin.com/t/{ticket_id}'
            )
            response['suggested_notes']['suggested_note'] = tnba_note
            self._logger.info(tnba_message)
            await self._notifications_repository.send_slack_message(tnba_message)

        self._logger.info(f'Finished processing detail {ticket_detail_id} of ticket {ticket_id}!')
        return response

    async def _process_tickets_with_tnba(self, tickets: List[dict]):
        self._logger.info('Processing tickets with TNBA notes...')

        for ticket in tickets:
            ticket_id = ticket["ticket_id"]
            self._logger.info(f'Processing ticket {ticket_id} with TNBA notes...')

            task_history_response = await self._bruin_repository.get_ticket_task_history(ticket_id)
            task_history_response_body = task_history_response['body']
            task_history_response_status = task_history_response['status']
            if task_history_response_status not in range(200, 300):
                self._logger.error(
                    f'Error on _process_tickets_with_tnba getting ticket_task_history for ticket_id[{ticket_id}]'
                )
                continue

            ticket_rows_with_asset = [tr for tr in task_history_response_body if
                                      tr.get('Asset') and tr['Asset'] is not None]

            if len(ticket_rows_with_asset) == 0:
                self._logger.info(f'Skipped get_prediction for ticket_id[{ticket_id}] without assets...')
                continue

            t7_prediction_response = await self._t7_repository.get_prediction(ticket_id, task_history_response_body)
            t7_prediction_response_body = t7_prediction_response['body']
            t7_prediction_response_status = t7_prediction_response['status']
            if t7_prediction_response_status not in range(200, 300):
                continue

            tnba_notes: List[dict] = []
            slack_messages: List[str] = []
            available_options: List[dict] = []
            suggested_notes: List[dict] = []
            ticket_notes = ticket['ticket_notes']

            for ticket_detail in ticket['ticket_details']:
                ticket_detail_response = await self._process_ticket_detail_with_tnba(
                    ticket_id,
                    ticket_detail,
                    t7_prediction_response_body,
                    ticket_notes
                )
                if ticket_detail_response['tnba_note']:
                    tnba_notes.append(ticket_detail_response['tnba_note'])

                if ticket_detail_response['slack_message']:
                    slack_messages.append(ticket_detail_response['slack_message'])

                available_options.append(ticket_detail_response['available_options'])
                suggested_notes.append(ticket_detail_response['suggested_notes'])

            if not tnba_notes:
                self._logger.info(f'No TNBA notes were built for ticket {ticket_id}!')
            else:
                self._logger.info(f'Appending TNBA notes to ticket {ticket_id}...')
                append_notes_response = await self._bruin_repository.append_multiple_notes_to_ticket(
                    ticket_id, tnba_notes
                )
                append_notes_response_status = append_notes_response['status']
                if append_notes_response_status not in range(200, 300):
                    continue

                slack_message = os.linesep.join(slack_messages)
                await self._notifications_repository.send_slack_message(slack_message)

            await self._t7_repository.save_prediction(
                ticket_id,
                task_history_response_body,
                t7_prediction_response_body,
                available_options,
                suggested_notes
            )
            self._logger.info(f'Finished processing ticket with TNBA notes. ID: {ticket_id}')

        self._logger.info('Finished processing tickets with TNBA notes!')

    async def _process_ticket_detail_with_tnba(
            self,
            ticket_id,
            ticket_detail,
            t7_prediction_response_body,
            ticket_notes,
    ):
        ticket_detail_id = ticket_detail['detailID']
        self._logger.info(f'Processing detail {ticket_detail_id} of ticket {ticket_id}...')

        serial_number = ticket_detail['detailValue']

        response = {
            'tnba_note': None,
            'slack_message': None,
            'available_options': {
                'asset': serial_number,
                'available_options': None,
            },
            'suggested_notes': {
                'asset': serial_number,
                'suggested_note': None,
                'details': None,
            }
        }

        self._logger.info(
            f'Looking for the last TNBA note appended to ticket {ticket_id} and detail {ticket_detail_id}...'
        )
        newest_tnba_note = self._ticket_repository.find_newest_tnba_note_by_service_number(
            ticket_notes, serial_number
        )

        if not self._ticket_repository.is_tnba_note_old_enough(newest_tnba_note):
            msg = (
                f'TNBA note found for ticket {ticket_id} and detail {ticket_detail_id} is too recent. '
                f'Skipping detail...'
            )
            self._logger.info(msg)
            response['suggested_notes']['details'] = msg
            return response

        self._logger.info(
            f'Seeking predictions for ticket {ticket_id}, detail {ticket_detail_id} and serial {serial_number} '
            f'in the response received from T7 API...'
        )

        prediction_object_for_serial: dict = self._prediction_repository.find_prediction_object_by_serial(
            t7_prediction_response_body, serial_number
        )

        if not prediction_object_for_serial:
            msg = (
                f"No predictions were found for ticket {ticket_id}, detail {ticket_detail_id} and serial "
                f"{serial_number}!"
            )
            self._logger.info(msg)
            response['suggested_notes']['details'] = msg
            return response

        elif 'error' in prediction_object_for_serial.keys():
            msg = (
                f"Prediction for ticket {ticket_id}, detail {ticket_detail_id} and serial {serial_number} was "
                f"found but it contains an error from T7 API -> {prediction_object_for_serial['error']}"
            )
            self._logger.info(msg)
            await self._notifications_repository.send_slack_message(msg)
            response['suggested_notes']['details'] = msg
            return response

        self._logger.info(
            f'Found predictions for ticket {ticket_id}, detail {ticket_detail_id} and serial {serial_number}: '
            f'{prediction_object_for_serial}'
        )

        next_results_response = await self._bruin_repository.get_next_results_for_ticket_detail(
            ticket_id, ticket_detail_id, serial_number
        )
        next_results_response_body = next_results_response['body']
        next_results_response_status = next_results_response['status']
        if next_results_response_status not in range(200, 300):
            msg = f'Error getting next results ticket[{ticket_id}] detail[{ticket_detail_id}] serial [{serial_number}]'
            response['suggested_notes']['details'] = msg
            return response

        self._logger.info(
            f'Filtering predictions available in next results for ticket {ticket_id}, '
            f'detail {ticket_detail_id} and serial {serial_number}...'
        )
        predictions: list = prediction_object_for_serial['predictions']
        next_results: list = next_results_response_body['nextResults']
        response['available_options']['available_options'] = [result['resultName'].strip() for result in next_results]

        relevant_predictions = self._prediction_repository.filter_predictions_in_next_results(
            predictions, next_results
        )

        if not relevant_predictions:
            msg = (
                f"No predictions with name appearing in the next results were found for ticket {ticket_id}, "
                f"detail {ticket_detail_id} and serial {serial_number}!"
            )
            self._logger.info(msg)
            response['suggested_notes']['details'] = msg
            return response

        self._logger.info(
            f'Predictions available in next results found for ticket {ticket_id}, detail {ticket_detail_id} '
            f'and serial {serial_number}: {relevant_predictions}'
        )

        best_prediction: dict = self._prediction_repository.get_best_prediction(relevant_predictions)

        if not self._prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note(
                newest_tnba_note, best_prediction):
            msg = (
                f"Best prediction for ticket {ticket_id}, detail {ticket_detail_id} and serial {serial_number} "
                f"didn't change since the last TNBA note was appended. Skipping detail..."
            )
            self._logger.info(msg)
            response['suggested_notes']['details'] = msg
            return response

        self._logger.info(
            f"Best prediction for ticket {ticket_id}, detail {ticket_detail_id} and serial {serial_number} "
            f"changed since the last TNBA note was appended. New best prediction: {best_prediction}"
        )

        self._logger.info(
            f"Building TNBA note from predictions found for ticket {ticket_id}, detail {ticket_detail_id} "
            f"and serial {serial_number}..."
        )
        tnba_note: str = self._ticket_repository.build_tnba_note_from_prediction(best_prediction)

        if self._config.ENVIRONMENT == 'production':
            response['tnba_note'] = {
                'text': tnba_note,
                'detail_id': ticket_detail_id,
                'service_number': serial_number,
            }
            response['slack_message'] = TNBA_NOTE_APPENDED_SUCCESS_MSG.format(
                ticket_id=ticket_id, detail_id=ticket_detail_id,
                serial_number=serial_number, prediction=best_prediction['name'],
            )
            response['suggested_notes']['suggested_note'] = tnba_note
            return response
        elif self._config.ENVIRONMENT == 'dev':
            tnba_message = (
                f'TNBA note would have been appended to ticket {ticket_id} and detail {ticket_detail_id} '
                f'(serial: {serial_number}). Note: {tnba_note}. Details at app.bruin.com/t/{ticket_id}'
            )
            response['suggested_notes']['suggested_note'] = tnba_note
            self._logger.info(tnba_message)
            await self._notifications_repository.send_slack_message(tnba_message)

        self._logger.info(f'Finished processing detail {ticket_detail_id} of ticket {ticket_id}!')
        return response
