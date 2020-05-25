import asyncio
import time

from datetime import datetime
from typing import List
from typing import Set

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone
from tenacity import retry, wait_exponential, stop_after_delay


class TNBAMonitor:
    def __init__(self, event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                 monitoring_map_repository, bruin_repository, velocloud_repository, prediction_repository,
                 notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._t7_repository = t7_repository
        self._ticket_repository = ticket_repository
        self._monitoring_map_repository = monitoring_map_repository
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository
        self._prediction_repository = prediction_repository
        self._notifications_repository = notifications_repository

        self._monitoring_mapping = {}
        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['semaphore'])

    def __refresh_monitoring_mapping(self):
        self._monitoring_mapping = self._monitoring_map_repository.get_monitoring_map_cache()

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
        self._logger.info('Starting TNBA process...')
        if not self._monitoring_mapping:
            self._logger.info('Creating map with all customers and all their devices...')
            await self._monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses()
            await self._monitoring_map_repository.start_create_monitoring_map_job(exec_on_start=False)
            self._logger.info('Map of devices by customer created')

        start_time = time.time()

        self.__refresh_monitoring_mapping()

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
        self._logger.info(f'TNBA process finished! Took {end_time - start_time} seconds.')

    async def _get_all_open_tickets_with_details_for_monitored_companies(self):
        open_tickets = []

        bruin_clients_ids: Set[int] = set(self._monitoring_mapping.keys())
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
        serials_under_monitoring: Set[str] = set(sum(
            (
                list(edge_status_by_serial_dict.keys())
                for edge_status_by_serial_dict in self._monitoring_mapping.values()
            ),
            []
        ))

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

            t7_prediction_response = await self._t7_repository.get_prediction(ticket_id)
            t7_prediction_response_body = t7_prediction_response['body']
            t7_prediction_response_status = t7_prediction_response['status']
            if t7_prediction_response_status not in range(200, 300):
                continue

            ticket_detail_id = ticket['ticket_details'][0]['detailID']  # TODO: Process ALL details
            serial_number = ticket['ticket_details'][0]['detailValue']  # TODO: Process ALL details

            self._logger.info(
                f'Seeking predictions for ticket {ticket_id} and serial {serial_number} in the response '
                f'received from T7 API...'
            )
            prediction_object_for_serial: dict = self._prediction_repository.find_prediction_object_by_serial(
                t7_prediction_response_body, serial_number
            )
            if not prediction_object_for_serial:
                self._logger.info(f"No predictions were found for serial {serial_number} and ticket {ticket_id}!")
                continue

            self._logger.info(
                f'Found predictions for ticket {ticket_id} and serial {serial_number}: {prediction_object_for_serial}'
            )

            next_results_response = await self._bruin_repository.get_next_results_for_ticket_detail(
                ticket_id, ticket_detail_id, serial_number
            )
            next_results_response_body = next_results_response['body']
            next_results_response_status = next_results_response['status']
            if next_results_response_status not in range(200, 300):
                continue

            self._logger.info(
                f'Filtering predictions available in next results for ticket {ticket_id} and serial {serial_number}...'
            )
            predictions: list = prediction_object_for_serial['predictions']
            next_results: list = next_results_response_body['nextResults']
            relevant_predictions = self._prediction_repository.filter_predictions_in_next_results(
                predictions, next_results
            )

            if not relevant_predictions:
                self._logger.info(
                    f"No predictions with name appearing in the next results were found for serial {serial_number} "
                    f"and ticket {ticket_id}!"
                )
                continue

            self._logger.info(
                f'Predictions available in next results found for ticket {ticket_id} and serial '
                f'{serial_number}: {relevant_predictions}'
            )

            self._logger.info(
                f"Building TNBA note from predictions found for serial {serial_number} and ticket {ticket_id}..."
            )
            best_prediction: dict = self._prediction_repository.get_best_prediction(relevant_predictions)
            tnba_note: str = self._ticket_repository.build_tnba_note_from_prediction(best_prediction)

            if self._config.ENVIRONMENT == 'production':
                self._logger.info(f'Appending TNBA note to ticket {ticket_id}...')
                await self._bruin_repository.append_note_to_ticket(ticket_id, tnba_note, is_private=True)
            elif self._config.ENVIRONMENT == 'dev':
                tnba_message = (
                    f'TNBA note would have been appended to ticket {ticket_id} (serial: {serial_number}). '
                    f'Note: {tnba_note}'
                )
                self._logger.info(tnba_message)
                await self._notifications_repository.send_slack_message(tnba_message)

            self._logger.info(f'Finished processing ticket without TNBA notes. ID: {ticket_id}')

        self._logger.info('Finished processing tickets without TNBA notes!')

    async def _process_tickets_with_tnba(self, tickets: List[dict]):
        self._logger.info('Processing tickets with TNBA notes...')

        for ticket in tickets:
            ticket_id = ticket["ticket_id"]
            self._logger.info(f'Processing ticket {ticket_id} with TNBA notes...')

            self._logger.info(f'Looking for the last TNBA note appended to ticket {ticket_id}...')
            ticket_notes = ticket['ticket_notes']
            newest_tnba_note = self._ticket_repository.find_newest_tnba_note(ticket_notes)

            if not self._ticket_repository.is_tnba_note_old_enough(newest_tnba_note):
                self._logger.info(f'TNBA note found for ticket {ticket_id} is too recent. Skipping ticket...')
                continue

            ticket_detail_id = ticket['ticket_details'][0]['detailID']  # TODO: Process ALL details
            serial_number = ticket['ticket_details'][0]['detailValue']  # TODO: Process ALL details

            t7_prediction_response = await self._t7_repository.get_prediction(ticket_id)
            t7_prediction_response_body = t7_prediction_response['body']
            t7_prediction_response_status = t7_prediction_response['status']
            if t7_prediction_response_status not in range(200, 300):
                continue

            self._logger.info(
                f'Seeking predictions for ticket {ticket_id} and serial {serial_number} in the response '
                f'received from T7 API...'
            )
            prediction_object_for_serial: dict = self._prediction_repository.find_prediction_object_by_serial(
                t7_prediction_response_body, serial_number
            )
            if not prediction_object_for_serial:
                self._logger.info(f"No predictions were found for serial {serial_number} and ticket {ticket_id}!")
                continue

            self._logger.info(
                f'Found predictions for ticket {ticket_id} and serial {serial_number}: {prediction_object_for_serial}'
            )

            next_results_response = await self._bruin_repository.get_next_results_for_ticket_detail(
                ticket_id, ticket_detail_id, serial_number
            )
            next_results_response_body = next_results_response['body']
            next_results_response_status = next_results_response['status']
            if next_results_response_status not in range(200, 300):
                continue

            self._logger.info(
                f'Filtering predictions available in next results for ticket {ticket_id} and serial {serial_number}...'
            )
            predictions: list = prediction_object_for_serial['predictions']
            next_results: list = next_results_response_body['nextResults']
            relevant_predictions = self._prediction_repository.filter_predictions_in_next_results(
                predictions, next_results
            )

            if not relevant_predictions:
                self._logger.info(
                    f"No predictions with name appearing in the next results were found for serial {serial_number} "
                    f"and ticket {ticket_id}!"
                )
                continue

            self._logger.info(
                f'Predictions available in next results found for ticket {ticket_id} and serial '
                f'{serial_number}: {relevant_predictions}'
            )

            best_prediction: dict = self._prediction_repository.get_best_prediction(relevant_predictions)
            if not self._prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note(
                    newest_tnba_note, best_prediction):
                self._logger.info(
                    f"Predictions for serial {serial_number} and ticket {ticket_id} didn't change since the last TNBA"
                    f"note was appended. Skipping ticket..."
                )
                continue

            self._logger.info(
                f"Building TNBA note from predictions found for serial {serial_number} and ticket {ticket_id}..."
            )
            tnba_note: str = self._ticket_repository.build_tnba_note_from_prediction(best_prediction)

            if self._config.ENVIRONMENT == 'production':
                self._logger.info(f'Appending TNBA note to ticket {ticket_id}...')
                await self._bruin_repository.append_note_to_ticket(ticket_id, tnba_note, is_private=True)
            elif self._config.ENVIRONMENT == 'dev':
                tnba_message = (
                    f'TNBA note would have been appended to ticket {ticket_id} (serial: {serial_number}). '
                    f'Note: {tnba_note}'
                )
                self._logger.info(tnba_message)
                await self._notifications_repository.send_slack_message(tnba_message)

            self._logger.info(f'Finished processing ticket with TNBA notes. ID: {ticket_id}')

        self._logger.info('Finished processing tickets with TNBA notes!')
