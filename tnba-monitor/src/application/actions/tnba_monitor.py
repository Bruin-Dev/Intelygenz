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
    '{notes_count} TNBA note(s) were appended to ticket {ticket_id}: app.bruin.com/t/{ticket_id}'
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

        self.__reset_state()
        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['semaphore'])

    def __reset_state(self):
        self._customer_cache_by_serial = {}
        self._tnba_notes_to_append = []

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
        self.__reset_state()

        self._logger.info('Starting TNBA process...')

        customer_cache_response = await self._customer_cache_repository.get_cache_for_tnba_monitoring()
        if customer_cache_response['status'] not in range(200, 300) or customer_cache_response['status'] == 202:
            return

        customer_cache = customer_cache_response['body']
        self._customer_cache_by_serial = {
            cached_info['serial_number']: cached_info
            for cached_info in customer_cache
        }

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
        relevant_open_tickets = self._filter_irrelevant_notes_in_tickets(relevant_open_tickets)

        self._logger.info('Getting T7 predictions for all relevant open tickets...')
        predictions_by_ticket_id = await self._get_predictions_by_ticket_id(relevant_open_tickets)

        self._logger.info('Removing erroneous T7 predictions...')
        predictions_by_ticket_id = self._remove_erroneous_predictions(predictions_by_ticket_id)

        self._logger.info('Splitting ticket details in ticket details with and without TNBA notes...')
        ticket_details_with_tnba, ticket_details_without_tnba = self._distinguish_ticket_details_with_and_without_tnba(
            relevant_open_tickets
        )

        self._logger.info('Mapping all ticket details with their predictions...')
        ticket_details_with_tnba = self._map_ticket_details_with_predictions(
            ticket_details_with_tnba, predictions_by_ticket_id
        )
        ticket_details_without_tnba = self._map_ticket_details_with_predictions(
            ticket_details_without_tnba, predictions_by_ticket_id
        )

        self._logger.info(f'Ticket details split and mapped with predictions successfully. '
                          f'Ticket details with TNBA: {len(ticket_details_with_tnba)}. '
                          f'Ticket details without TNBA: {len(ticket_details_without_tnba)}. '
                          f'Processing both ticket details sets...')
        await asyncio.gather(
            self._process_ticket_details_with_tnba(ticket_details_with_tnba),
            self._process_ticket_details_without_tnba(ticket_details_without_tnba),
        )
        self._logger.info('All ticket details were processed.')

        if not self._tnba_notes_to_append:
            self._logger.info('No TNBA notes for append were built for any detail processed.')
        else:
            self._logger.info(f'{len(self._tnba_notes_to_append)} TNBA notes were built for append.')
            await self._append_tnba_notes()

        end_time = time.time()
        self._logger.info(f'TNBA process finished! Took {round((end_time - start_time) / 60, 2)} minutes.')

    async def _get_all_open_tickets_with_details_for_monitored_companies(self):
        open_tickets = []

        bruin_clients_ids: Set[int] = set(
            elem['bruin_client_info']['client_id']
            for elem in list(self._customer_cache_by_serial.values())
        )
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
        serials_under_monitoring: Set[str] = set(self._customer_cache_by_serial.keys())

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

    def _filter_irrelevant_notes_in_tickets(self, tickets):
        serials_under_monitoring: Set[str] = set(self._customer_cache_by_serial.keys())

        sanitized_tickets = []

        for ticket in tickets:
            relevant_notes = [
                note
                for note in ticket['ticket_notes']
                if note['noteValue'] is not None
            ]

            for index, note in enumerate(relevant_notes):
                service_numbers_in_note = set(note['serviceNumber'])
                relevant_service_numbers = serials_under_monitoring & service_numbers_in_note

                if not relevant_service_numbers:
                    del relevant_notes[index]
                else:
                    relevant_notes[index]['serviceNumber'] = list(relevant_service_numbers)

            sanitized_tickets.append({
                'ticket_id': ticket['ticket_id'],
                'ticket_details': ticket['ticket_details'],
                'ticket_notes': relevant_notes,
            })

        return sanitized_tickets

    async def _get_predictions_by_ticket_id(self, tickets: list) -> dict:
        result = {}

        for ticket in tickets:
            ticket_id = ticket["ticket_id"]
            self._logger.info(f'Claiming T7 predictions for ticket {ticket_id}...')

            task_history_response = await self._bruin_repository.get_ticket_task_history(ticket_id)
            if task_history_response['status'] not in range(200, 300):
                continue

            task_history: list = task_history_response['body']
            any_ticket_row_has_asset = any(row.get('Asset') for row in task_history)
            if not any_ticket_row_has_asset:
                self._logger.info(f"Task history of ticket {ticket_id} doesn't have any asset. Skipping...")
                continue

            t7_prediction_response = await self._t7_repository.get_prediction(ticket_id, task_history)
            if t7_prediction_response['status'] not in range(200, 300):
                continue

            ticket_predictions: list = t7_prediction_response['body']
            if not ticket_predictions:
                self._logger.info(f"There are no predictions for ticket {ticket_id}. Skipping...")
                continue

            result[ticket_id] = ticket_predictions
            self._logger.info(f'T7 predictions found for ticket {ticket_id}!')

        return result

    def _remove_erroneous_predictions(self, predictions_by_ticket_id: dict) -> dict:
        result = {}

        for ticket_id, prediction_objects in predictions_by_ticket_id.items():
            valid_predictions = []

            for prediction_obj in prediction_objects:
                serial_number = prediction_obj['assetId']

                if 'error' in prediction_obj.keys():
                    self._logger.info(
                        f"Prediction for serial {serial_number} in ticket {ticket_id} was found but it contains an "
                        f"error from T7 API -> {prediction_obj['error']}"
                    )
                    continue

                valid_predictions.append(prediction_obj)

            if not valid_predictions:
                self._logger.info(f"All predictions in ticket {ticket_id} were erroneous. Skipping ticket...")
                continue

            result[ticket_id] = valid_predictions

        return result

    def _distinguish_ticket_details_with_and_without_tnba(self, tickets: list) -> tuple:
        ticket_details_with_tnba = []
        ticket_details_without_tnba = []

        for ticket in tickets:
            ticket_id = ticket['ticket_id']
            ticket_details = ticket['ticket_details']
            ticket_notes = ticket['ticket_notes']

            for detail in ticket_details:
                serial_number = detail['detailValue']

                notes_related_to_serial = [
                    note
                    for note in ticket_notes
                    if serial_number in note['serviceNumber']
                ]

                detail_object = {
                    'ticket_id': ticket_id,
                    'ticket_detail': detail,
                    'ticket_notes': notes_related_to_serial,
                }

                if self._ticket_repository.has_tnba_note(notes_related_to_serial):
                    ticket_details_with_tnba.append(detail_object)
                else:
                    ticket_details_without_tnba.append(detail_object)

        return ticket_details_with_tnba, ticket_details_without_tnba

    def _map_ticket_details_with_predictions(self, ticket_details: list, predictions_by_ticket_id: dict) -> list:
        result = []

        for detail_object in ticket_details:
            ticket_id = detail_object['ticket_id']
            serial_number = detail_object['ticket_detail']['detailValue']
            predictions_for_ticket: list = predictions_by_ticket_id.get(ticket_id)

            if not predictions_for_ticket:
                self._logger.info(
                    f'Ticket {ticket_id} does not have any prediction associated. Skipping serial '
                    f'{serial_number}...'
                )
                continue

            prediction_object_related_to_serial = self._prediction_repository.find_prediction_object_by_serial(
                predictions=predictions_for_ticket,
                serial_number=serial_number,
            )
            if not prediction_object_related_to_serial:
                self._logger.info(
                    f'No predictions were found for ticket {ticket_id} and serial {serial_number}. Skipping...'
                )
                continue

            predictions: list = prediction_object_related_to_serial['predictions']

            result.append({
                **detail_object,
                'ticket_detail_predictions': predictions,
            })

        return result

    async def _process_ticket_details_without_tnba(self, ticket_details: List[dict]):
        self._logger.info('Processing ticket details without TNBA notes...')

        tasks = [
            self._process_ticket_detail_without_tnba(detail_object)
            for detail_object in ticket_details
        ]
        await asyncio.gather(*tasks)

        self._logger.info('Finished processing ticket details without TNBA notes!')

    async def _process_ticket_detail_without_tnba(self, detail_object: dict):
        ticket_id = detail_object['ticket_id']
        ticket_detail_id = detail_object['ticket_detail']['detailID']
        serial_number = detail_object['ticket_detail']['detailValue']
        predictions = detail_object['ticket_detail_predictions']

        self._logger.info(f'Processing detail {ticket_detail_id} (serial: {serial_number}) of ticket {ticket_id}...')

        next_results_response = await self._bruin_repository.get_next_results_for_ticket_detail(
            ticket_id, ticket_detail_id, serial_number
        )
        next_results_response_body = next_results_response['body']
        next_results_response_status = next_results_response['status']
        if next_results_response_status not in range(200, 300):
            return

        self._logger.info(
            f'Filtering predictions available in next results for ticket {ticket_id}, '
            f'detail {ticket_detail_id} and serial {serial_number}...'
        )
        next_results: list = next_results_response_body['nextResults']

        relevant_predictions = self._prediction_repository.filter_predictions_in_next_results(
            predictions, next_results
        )

        if not relevant_predictions:
            msg = (
                f"No predictions with name appearing in the next results were found for ticket {ticket_id}, "
                f"detail {ticket_detail_id} and serial {serial_number}!"
            )
            self._logger.info(msg)
            return

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
            self._tnba_notes_to_append.append({
                'ticket_id': ticket_id,
                'text': tnba_note,
                'detail_id': ticket_detail_id,
                'service_number': serial_number,
            })
        elif self._config.ENVIRONMENT == 'dev':
            tnba_message = (
                f'TNBA note would have been appended to ticket {ticket_id} and detail {ticket_detail_id} '
                f'(serial: {serial_number}). Note: {tnba_note}. Details at app.bruin.com/t/{ticket_id}'
            )
            self._logger.info(tnba_message)
            await self._notifications_repository.send_slack_message(tnba_message)

        self._logger.info(
            f'Finished processing detail {ticket_detail_id} (serial: {serial_number}) of ticket {ticket_id}!'
        )

    async def _process_ticket_details_with_tnba(self, ticket_details: List[dict]):
        self._logger.info('Processing ticket details with TNBA notes...')

        tasks = [
            self._process_ticket_detail_with_tnba(detail_object)
            for detail_object in ticket_details
        ]
        await asyncio.gather(*tasks)

        self._logger.info('Finished processing ticket details with TNBA notes!')

    async def _process_ticket_detail_with_tnba(self, detail_object: dict):
        ticket_id = detail_object['ticket_id']
        ticket_detail_id = detail_object['ticket_detail']['detailID']
        ticket_notes = detail_object['ticket_notes']
        serial_number = detail_object['ticket_detail']['detailValue']
        predictions = detail_object['ticket_detail_predictions']

        self._logger.info(f'Processing detail {ticket_detail_id} (serial: {serial_number}) of ticket {ticket_id}...')

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
            return

        next_results_response = await self._bruin_repository.get_next_results_for_ticket_detail(
            ticket_id, ticket_detail_id, serial_number
        )
        next_results_response_body = next_results_response['body']
        next_results_response_status = next_results_response['status']
        if next_results_response_status not in range(200, 300):
            return

        self._logger.info(
            f'Filtering predictions available in next results for ticket {ticket_id}, '
            f'detail {ticket_detail_id} and serial {serial_number}...'
        )
        next_results: list = next_results_response_body['nextResults']

        relevant_predictions = self._prediction_repository.filter_predictions_in_next_results(
            predictions, next_results
        )

        if not relevant_predictions:
            msg = (
                f"No predictions with name appearing in the next results were found for ticket {ticket_id}, "
                f"detail {ticket_detail_id} and serial {serial_number}!"
            )
            self._logger.info(msg)
            return

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
            return

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
            self._tnba_notes_to_append.append({
                'ticket_id': ticket_id,
                'text': tnba_note,
                'detail_id': ticket_detail_id,
                'service_number': serial_number,
            })
        elif self._config.ENVIRONMENT == 'dev':
            tnba_message = (
                f'TNBA note would have been appended to ticket {ticket_id} and detail {ticket_detail_id} '
                f'(serial: {serial_number}). Note: {tnba_note}. Details at app.bruin.com/t/{ticket_id}'
            )
            self._logger.info(tnba_message)
            await self._notifications_repository.send_slack_message(tnba_message)

        self._logger.info(
            f'Finished processing detail {ticket_detail_id} (serial: {serial_number}) of ticket {ticket_id}!'
        )

    async def _append_tnba_notes(self):
        notes_by_ticket_id = {}

        for note_object in self._tnba_notes_to_append:
            ticket_id = note_object['ticket_id']
            tnba_note = note_object['text']
            ticket_detail_id = note_object['detail_id']
            service_number = note_object['service_number']

            notes_by_ticket_id.setdefault(ticket_id, [])
            notes_by_ticket_id[ticket_id].append({
                'text': tnba_note,
                'detail_id': ticket_detail_id,
                'service_number': service_number,
            })

        for ticket_id, notes in notes_by_ticket_id.items():
            self._logger.info(f'Appending {len(notes)} TNBA notes to ticket {ticket_id}...')

            append_notes_response = await self._bruin_repository.append_multiple_notes_to_ticket(ticket_id, notes)
            append_notes_response_status = append_notes_response['status']
            if append_notes_response_status not in range(200, 300):
                continue

            slack_message = TNBA_NOTE_APPENDED_SUCCESS_MSG.format(notes_count=len(notes), ticket_id=ticket_id)
            await self._notifications_repository.send_slack_message(slack_message)
